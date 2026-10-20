@echo off
setlocal
cd /d "%~dp0"

if not exist api-keys.txt (
    if exist api-keys.example.txt (
        echo [INFO] api-keys.txt not found. Copying template from api-keys.example.txt...
        copy api-keys.example.txt api-keys.txt >nul
        echo [!] Created api-keys.txt. Please edit it and insert your actual API keys!
    )
)

if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
)

python proxy.py
pause
