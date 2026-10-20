@echo off
setlocal
cd /d "%~dp0"

set XDG_CONFIG_HOME=%~dp0.config
set XDG_DATA_HOME=%~dp0.local-share
set XDG_STATE_HOME=%~dp0.local-state
set XDG_CACHE_HOME=%~dp0.cache

set DEFAULT_MODEL=rotator/default-model

if not "%~1"=="" (
    set ARGS=%*
) else (
    set ARGS=-m %DEFAULT_MODEL%
)

if exist ".\node_modules\opencode-windows-x64\bin\opencode.exe" (
    ".\node_modules\opencode-windows-x64\bin\opencode.exe" %ARGS%
) else (
    where opencode >nul 2>nul
    if %errorlevel% equ 0 (
        opencode %ARGS%
    ) else (
        echo [INFO] Local opencode binary not found. Running via npx opencode...
        npx opencode %ARGS%
    )
)
