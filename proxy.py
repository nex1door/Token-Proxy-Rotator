import itertools
import os
import sys
import time

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse

# ==============================================================================
# НАСТРОЙКИ СЕРВЕРА И ВЫШЕСТОЯЩЕГО ПРОВАЙДЕРА
# ==============================================================================
# Укажите базовый URL вашего OpenAI-совместимого провайдера (через переменную окружения или прямо здесь)
BASE_URL = os.getenv("BASE_URL", "https://api.your-provider.com/v1").rstrip("/")

# Таймаут запроса к апстриму в секундах
TIMEOUT = float(os.getenv("TIMEOUT", "60"))

# Хост и порт для локального запуска прокси
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))

# Путь к файлу со списком API-ключей
API_KEYS_FILE = os.getenv("API_KEYS_FILE", "api-keys.txt")

# Список моделей для эндпоинта /v1/models (через запятую)
AVAILABLE_MODELS = os.getenv("AVAILABLE_MODELS", "default-model,gpt-4o,claude-3-5-sonnet")

# Статусы ответов, при которых выполняется переключение на следующий ключ
RETRY_STATUSES = {401, 402, 403, 429, 500, 502, 503}
# ==============================================================================


def load_api_keys():
    """Загрузка ключей из файла (пропускает пустые строки и комментарии с #)."""
    if not os.path.exists(API_KEYS_FILE):
        print(f"[{time.strftime('%H:%M:%S')}] ВНИМАНИЕ: Файл '{API_KEYS_FILE}' не найден!", file=sys.stderr)
        print(f"[{time.strftime('%H:%M:%S')}] Создайте '{API_KEYS_FILE}' на основе 'api-keys.example.txt' и добавьте ключи.", file=sys.stderr)
        return []

    with open(API_KEYS_FILE, encoding="utf-8") as f:
        keys = [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]

    if not keys:
        print(f"[{time.strftime('%H:%M:%S')}] ВНИМАНИЕ: В файле '{API_KEYS_FILE}' нет активных ключей!", file=sys.stderr)
    else:
        print(f"[{time.strftime('%H:%M:%S')}] Загружено API-ключей: {len(keys)} (источник: {API_KEYS_FILE})", flush=True)

    return keys


API_KEYS = load_api_keys()
key_cycle = itertools.cycle(API_KEYS) if API_KEYS else None
client = httpx.AsyncClient(timeout=TIMEOUT)

app = FastAPI(title="TokenRotator API Proxy", version="1.0.0")


@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "TokenRotator API Proxy",
        "keys_loaded": len(API_KEYS),
        "upstream_base_url": BASE_URL,
    }


@app.get("/v1/models")
async def models():
    model_list = [m.strip() for m in AVAILABLE_MODELS.split(",") if m.strip()]
    return {
        "object": "list",
        "data": [{"id": model_id, "object": "model", "owned_by": "rotator-proxy"} for model_id in model_list],
    }


@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    return await proxy(request, "/chat/completions")


@app.post("/v1/responses")
async def responses(request: Request):
    return await proxy(request, "/responses")


async def proxy(request: Request, path: str):
    global API_KEYS, key_cycle

    # Пробуем динамически подгрузить ключи, если файл был создан после запуска сервера
    if not API_KEYS:
        API_KEYS = load_api_keys()
        if API_KEYS:
            key_cycle = itertools.cycle(API_KEYS)
        else:
            return JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "message": f"API keys are missing. Please add your keys to '{API_KEYS_FILE}'.",
                        "type": "configuration_error",
                    }
                },
            )

    body = await request.json()
    is_stream = bool(body.get("stream"))
    last_error = None

    for _ in range(len(API_KEYS)):
        key = next(key_cycle)
        masked_key = f"...{key[-6:]}" if len(key) >= 6 else "***"
        headers = {"Authorization": f"Bearer {key}"}

        try:
            upstream = await client.post(
                f"{BASE_URL}{path}",
                headers=headers,
                json=body,
            )

            if upstream.status_code in RETRY_STATUSES:
                print(f"[{time.strftime('%H:%M:%S')}] Ключ {masked_key} вернул HTTP {upstream.status_code}. Переключаем...", flush=True)
                last_error = upstream.text
                continue

            if upstream.status_code >= 400:
                return JSONResponse(status_code=upstream.status_code, content={"error": upstream.text})

            if is_stream:
                async def stream():
                    async for chunk in upstream.aiter_bytes():
                        yield chunk

                return StreamingResponse(stream(), media_type="text/event-stream")

            return JSONResponse(upstream.json())

        except (httpx.TimeoutException, httpx.TransportError) as error:
            print(f"[{time.strftime('%H:%M:%S')}] Ключ {masked_key} вызвал ошибку сети/таймаута: {error.__class__.__name__}. Переключаем...", flush=True)
            last_error = str(error)

    return JSONResponse(
        status_code=httpx.codes.BAD_GATEWAY,
        content={"error": {"message": f"All API keys failed: {last_error}", "type": "upstream_error"}},
    )


@app.on_event("shutdown")
async def shutdown():
    await client.aclose()


if __name__ == "__main__":
    import uvicorn

    if "your-provider.com" in BASE_URL:
        print(f"[{time.strftime('%H:%M:%S')}] [ВНИМАНИЕ] BASE_URL настроен на пример ('{BASE_URL}').", file=sys.stderr)
        print(f"[{time.strftime('%H:%M:%S')}] [ВНИМАНИЕ] Укажите ваш настоящий URL провайдера через BASE_URL='https://...' или в коде proxy.py.", file=sys.stderr)

    print(f"[{time.strftime('%H:%M:%S')}] Запуск TokenRotator: http://{HOST}:{PORT} -> Upstream: {BASE_URL}")
    uvicorn.run(app, host=HOST, port=PORT)
