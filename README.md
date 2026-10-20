# 🔄 TokenRotator

> Универсальный локальный OpenAI-совместимый прокси с автоматической Round-Robin ротацией API-ключей и умным Failover (отказоустойчивостью).

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)]()

---

## 📌 О проекте

При активной работе с LLM через любые API-провайдеры разработчики регулярно сталкиваются с лимитами запросов в минуту (Rate Limits, HTTP 429), исчерпанием дневного баланса (HTTP 402/403) или временными сбоями серверов (HTTP 500/502/503/таймауты).

**TokenRotator** решает эту проблему:
- Вы указываете пул ваших API-ключей в простом текстовом файле.
- Прокси распределяет запросы между ключами по алгоритму **Round-Robin**.
- Если на каком-то ключе исчерпан лимит или провайдер вернул ошибку (`401`, `402`, `403`, `429`, `500`, `502`, `503`, Timeout) — прокси **не роняет сессию**, а прозрачно переключается на следующий рабочий ключ и повторяет запрос.
- Для клиента (OpenCode, Cursor, Continue, Roo Code, Claude Code или скриптов) прокси выглядит как стандартный OpenAI-сервер.

---

## ✨ Возможности

- 🚀 **Полная OpenAI-совместимость**:
  - `POST /v1/chat/completions` — генерация ответов.
  - `POST /v1/responses` — поддержка эндпоинта responses.
  - `GET /v1/models` — список поддерживаемых моделей.
  - `GET /` — healthcheck статус сервера.
- 🔁 **Round-Robin ротация**: равномерная нагрузка на все ключи в пуле.
- 🛡️ **Интеллектуальный Failover**: автоматический повтор запроса на следующем ключе при ошибках `401, 402, 403, 429, 500, 502, 503` или сетевых обрывах.
- 🌊 **Потоковая передача (SSE Streaming)**: полноценная поддержка `stream: true` без задержек.
- 🔒 **Безопасность**:
  - Маскирование ключей в терминале и логах (`...abc123`).
  - Файлы ключей и локальные конфиги изолированы и занесены в `.gitignore`.
- 🤖 **Интеграция с OpenCode**: готовые скрипты запуска со своими изолированными XDG-папками.
- 💻 **Кроссплатформенность**: готовые скрипты запуска под Windows (`.bat`) и Linux/macOS (`.sh`).

---

## 📁 Структура проекта

```text
TokenRotator/
├── proxy.py               # Основной прокси-сервер (FastAPI + HTTPX)
├── requirements.txt       # Зависимости Python
├── package.json           # Зависимости Node.js (для OpenCode)
├── api-keys.example.txt   # Шаблон для добавления API-ключей
├── opencode.json          # Конфигурация для OpenCode CLI
├── opencode.example.json  # Резервный шаблон конфигурации OpenCode
├── run.bat                # Запуск прокси на Windows
├── run.sh                 # Запуск прокси на Linux / macOS
├── run-opencode.bat       # Запуск OpenCode на Windows
├── run-opencode.sh        # Запуск OpenCode на Linux / macOS
├── .gitignore             # Исключение ключей, кэшей и временных данных
├── AGENTS.md              # Документация для AI-ассистентов
└── README.md              # Документация проекта
```

---

## 🚀 Быстрый старт

### 1. Клонирование репозитория

```bash
git clone https://github.com/nex1door/Token-Proxy-Rotator.git
cd Token-Proxy-Rotator
```

### 2. Установка зависимостей

Рекомендуется использовать виртуальное окружение:

**Windows (PowerShell / CMD):**
```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

**Linux / macOS (Bash):**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Настройка целевого API (Upstream URL)

В файле [proxy.py](proxy.py) или через переменную окружения `BASE_URL` укажите адрес вашего целевого провайдера:

```python
# proxy.py
BASE_URL = os.getenv("BASE_URL", "https://api.your-provider.com/v1").rstrip("/")
```

> [!TIP]
> Вы можете указать URL любого OpenAI-совместимого сервиса, например:
> - Официальный OpenAI: `https://api.openai.com/v1`
> - OpenRouter: `https://openrouter.ai/api/v1`
> - DeepSeek: `https://api.deepseek.com/v1`
> - Любой другой шлюз или локальный сервер (vLLM, Ollama, LiteLLM).

### 4. Настройка API-ключей

Создайте файл `api-keys.txt` на основе шаблона `api-keys.example.txt`:

**Windows:**
```powershell
copy api-keys.example.txt api-keys.txt
```

**Linux / macOS:**
```bash
cp api-keys.example.txt api-keys.txt
```

Откройте `api-keys.txt` и вставьте ваши рабочие API-ключи (по одному на строке, без кавычек и запятых):

```text
sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
sk-yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy
sk-zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz
```

> [!NOTE]
> Файл `api-keys.txt` добавлен в `.gitignore` и **никогда** не попадет в репозиторий Git.

### 5. Запуск прокси

Вы можете запустить сервер одной командой:

- **Windows:** дважды кликните `run.bat` или выполните:
  ```powershell
  .\run.bat
  ```
- **Linux / macOS:**
  ```bash
  chmod +x run.sh run-opencode.sh
  ./run.sh
  ```
- Либо напрямую через Python:
  ```bash
  python proxy.py
  ```

Сервер поднимется на: `http://127.0.0.1:8000`.

Проверить работоспособность можно в браузере или через curl:
```bash
curl http://127.0.0.1:8000/
```
Пример ответа:
```json
{
  "status": "online",
  "service": "TokenRotator API Proxy",
  "keys_loaded": 3,
  "upstream_base_url": "https://api.your-provider.com/v1"
}
```

---

## 🛠️ Настройка и переменные окружения

Поведение прокси можно конфигурировать без изменения кода через переменные окружения:

| Переменная | По умолчанию | Описание |
|---|---|---|
| `BASE_URL` | `https://api.your-provider.com/v1` | **URL целевого провайдера** (OpenAI-compatible) |
| `PORT` | `8000` | Порт локального прокси |
| `HOST` | `127.0.0.1` | Хост для биндинга (по умолчанию локально) |
| `TIMEOUT` | `60` | Таймаут ожидания ответа от апстрима (в секундах) |
| `API_KEYS_FILE` | `api-keys.txt` | Имя файла со списком ключей |
| `AVAILABLE_MODELS` | `default-model,gpt-4o,claude-3-5-sonnet` | Список моделей для `/v1/models` |

Пример запуска с переопределением параметров:
```bash
BASE_URL="https://api.openai.com/v1" PORT=8080 python proxy.py
```

---

## 💻 Использование с OpenCode

[OpenCode](https://opencode.ai/) — открытый терминальный AI-ассистент программирования. Репозиторий содержит готовую конфигурацию `opencode.json` и изолированные скрипты запуска.

1. Установите зависимости:
   ```bash
   npm install
   ```
2. Убедитесь, что прокси запущен (`run.bat` или `run.sh`).
3. Запустите OpenCode:
   - **Windows:** `.\run-opencode.bat`
   - **Linux / macOS:** `./run-opencode.sh`

Конфигурация в `opencode.json` направляет запросы к модели `rotator/default-model` напрямую в наш локальный ротатор `http://127.0.0.1:8000/v1`.

---

## 🔌 Подключение к другим клиентам

Вы можете использовать **TokenRotator** с любым приложением или инструментом, поддерживающим OpenAI API:

- **Base URL:** `http://127.0.0.1:8000/v1`
- **API Key:** любое значение (например, `unused`, так как прокси автоматически подставляет реальные ключи из пула).
- **Model Name:** модель, поддерживаемая вашим апстрим-провайдером (например `gpt-4o` или `default-model`).

### Пример: cURL

```bash
curl http://127.0.0.1:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer unused" \
  -d '{
    "model": "gpt-4o",
    "messages": [{"role": "user", "content": "Привет! Как дела?"}],
    "stream": false
  }'
```

### Пример: Python (библиотека `openai`)

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://127.0.0.1:8000/v1",
    api_key="unused"
)

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Напиши пример кода на Python."}],
    stream=True
)

for chunk in response:
    content = chunk.choices[0].delta.content or ""
    print(content, end="", flush=True)
```

### Пример: VS Code (Continue / Cline / Roo Code / Cursor)

В настройках провайдера выберите `OpenAI-Compatible`:
- **API Base URL / Endpoint:** `http://127.0.0.1:8000/v1`
- **API Key:** `unused`
- **Model Name:** имя вашей модели

---

## 🛡️ Безопасность

- Никогда не коммитьте ваш файл `api-keys.txt` в репозиторий.
- Перед отправкой коммита всегда проверяйте:
  ```bash
  git status
  ```

---

## 📄 Лицензия

Проект распространяется под открытой лицензией [MIT](LICENSE).
