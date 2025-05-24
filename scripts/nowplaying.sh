#!/bin/bash
set -eu

np=$(playerctl metadata --format '{{artist}} - {{title}}' 2>/dev/null || true)

win_id=$(xdotool getwindowfocus 2>/dev/null || echo "")
if [[ -n "$win_id" ]]; then
    win=$(xdotool getwindowname "$win_id" 2>/dev/null || echo "")
else
    win=""
fi

[[ -z "$win" ]] && win="󰘳 Desktop"

if [[ -n "$np" ]]; then
    echo "{\"text\":\"🎵 $np\"}"
else
    short_win="${win%% - *}"
    echo "{\"text\":\"$short_win\"}"
fi
