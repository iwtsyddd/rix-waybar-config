#!/bin/bash

# Путь к Python скрипту
SCRIPT_DIR="$HOME/.config/waybar/scripts"
PYTHON_SCRIPT="$SCRIPT_DIR/window_tracker.py"

# Проверяем существование Python скрипта
if [[ ! -f "$PYTHON_SCRIPT" ]]; then
    echo '{"text": "󰘳 Desktop", "tooltip": "Python script not found"}'
    exit 1
fi

# Запускаем Python скрипт с таймаутом
timeout 3s python3 "$PYTHON_SCRIPT" --json 2>/dev/null || echo '{"text": "󰘳 Desktop", "tooltip": "Script timeout or error"}'
