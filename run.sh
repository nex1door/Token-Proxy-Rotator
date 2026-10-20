#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

if [ ! -f api-keys.txt ]; then
    if [ -f api-keys.example.txt ]; then
        echo "[INFO] api-keys.txt not found. Copying template from api-keys.example.txt..."
        cp api-keys.example.txt api-keys.txt
        echo "[!] Created api-keys.txt. Please edit it and insert your actual API keys!"
    fi
fi

if [ -f .venv/bin/activate ]; then
    . .venv/bin/activate
fi

exec python3 proxy.py
