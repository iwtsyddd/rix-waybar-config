#!/bin/bash

# Функция для получения названия окна через Wayland
get_wayland_window() {
    if command -v hyprctl >/dev/null 2>&1; then
        # Hyprland
        hyprctl activewindow -j 2>/dev/null | jq -r '.title // empty' 2>/dev/null
    elif command -v swaymsg >/dev/null 2>&1; then
        # Sway
        swaymsg -t get_tree 2>/dev/null | jq -r '.. | select(.focused? == true) | .name // empty' 2>/dev/null
    else
        echo ""
    fi
}

# Функция для получения названия окна через X11
get_x11_window() {
    if command -v xdotool >/dev/null 2>&1; then
        xdotool getactivewindow getwindowname 2>/dev/null || echo ""
    elif command -v xprop >/dev/null 2>&1; then
        xprop -id "$(xprop -root _NET_ACTIVE_WINDOW | cut -d' ' -f5)" WM_NAME 2>/dev/null | cut -d'"' -f2 || echo ""
    else
        echo ""
    fi
}

# Основная логика
main() {
    local title=""

    # Проверяем, какая система используется
    if [[ -n "${WAYLAND_DISPLAY}" ]]; then
        title=$(get_wayland_window)
    elif [[ -n "${DISPLAY}" ]]; then
        title=$(get_x11_window)
    fi

    # Обработка результата
    if [[ -z "$title" || "$title" == "null" ]]; then
        title="󰘳 Desktop"
    else
        # Ограничиваем длину и убираем лишние символы
        title=$(echo "$title" | sed 's/[[:cntrl:]]//g' | cut -c1-40)

        # Добавляем иконку в зависимости от типа окна
        case "$title" in
            *"Firefox"*|*"Chrome"*|*"Chromium"*) title="󰈹 $title" ;;
            *"Code"*|*"VSCode"*|*"vim"*|*"nvim"*) title="󰨞 $title" ;;
            *"Terminal"*|*"Alacritty"*|*"Kitty"*) title="󰆍 $title" ;;
            *"Files"*|*"Nautilus"*|*"Thunar"*) title="󰉋 $title" ;;
            *"Discord"*|*"Telegram"*) title="󰭹 $title" ;;
            *) title="󰖲 $title" ;;
        esac
    fi

    # Экранирование кавычек для JSON
    title=$(echo "$title" | sed 's/"/\\"/g')

    # Вывод в формате JSON
    printf '{"text": "%s", "tooltip": "%s"}\n' "$title" "$title"
}

main "$@"
