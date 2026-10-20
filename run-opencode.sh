#!/usr/bin/env bash
cd "$(dirname "$0")"

export XDG_CONFIG_HOME="$(pwd)/.config"
export XDG_DATA_HOME="$(pwd)/.local-share"
export XDG_STATE_HOME="$(pwd)/.local-state"
export XDG_CACHE_HOME="$(pwd)/.cache"

DEFAULT_MODEL="rotator/default-model"

if [ $# -gt 0 ]; then
    ARGS=("$@")
else
    ARGS=("-m" "$DEFAULT_MODEL")
fi

if command -v opencode >/dev/null 2>&1; then
    exec opencode "${ARGS[@]}"
elif command -v npx >/dev/null 2>&1; then
    exec npx opencode "${ARGS[@]}"
else
    echo "[ERROR] opencode or npx was not found. Please install Node.js."
    exit 1
fi
