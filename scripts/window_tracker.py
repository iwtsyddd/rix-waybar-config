#!/usr/bin/env python3

import json
import subprocess
import os
import sys
import re
from typing import Optional, Dict, Any
from pathlib import Path
import time

class WindowTracker:
    def __init__(self):
        self.cache = {}
        self.cache_timeout = 1.0
        self.last_update = 0
        self.last_result = None

        self.app_icons = {
            'firefox': '󰈹',
            'chrome': '󰊯',
            'chromium': '󰊯',
            'brave': '󰊯',
            'edge': '󰇩',
            'safari': '󰀹',

            'code': '󰨞',
            'vscode': '󰨞',
            'vim': '',
            'nvim': '',
            'emacs': '',
            'atom': '',
            'sublime': '󰅳',

            'terminal': '󰆍',
            'alacritty': '󰆍',
            'kitty': '󰄛',
            'konsole': '󰆍',
            'gnome-terminal': '󰆍',
            'xterm': '󰆍',
            'wezterm': '󰆍',

            'nautilus': '󰉋',
            'files': '󰉋',
            'thunar': '󰉋',
            'dolphin': '󰉋',
            'ranger': '󰉋',
            'nemo': '󰉋',

            'discord': '󰙯',
            'telegram': '',
            'slack': '󰒱',
            'teams': '󰊻',
            'whatsapp': '󰖣',

            'vlc': '󰕼',
            'mpv': '󰐹',
            'spotify': '',
            'rhythmbox': '󰎆',

            'libreoffice': '󰈙',
            'writer': '󰈙',
            'calc': '󰘚',
            'impress': '󰐩',

            'settings': '',
            'control': '',
            'system': '',

            'default': '󰖲'
        }

        # Паттерны для извлечения названия приложения
        self.app_patterns = {
            # Visual Studio Code
            r'.*?-?\s*Visual Studio Code.*': 'Visual Studio Code',
            r'.*?-?\s*Code.*': 'Visual Studio Code',

            # Браузеры
            r'.*?-?\s*Mozilla Firefox.*': 'Firefox',
            r'.*?-?\s*Firefox.*': 'Firefox',
            r'.*?-?\s*Google Chrome.*': 'Chrome',
            r'.*?-?\s*Chrome.*': 'Chrome',
            r'.*?-?\s*Chromium.*': 'Chromium',
            r'.*?-?\s*Brave.*': 'Brave',
            r'.*?-?\s*Microsoft Edge.*': 'Edge',
            r'.*?-?\s*Safari.*': 'Safari',

            # Терминалы
            r'.*?-?\s*Alacritty.*': 'Alacritty',
            r'.*?-?\s*Kitty.*': 'Kitty',
            r'.*?-?\s*Konsole.*': 'Konsole',
            r'.*?-?\s*GNOME Terminal.*': 'Terminal',
            r'.*?-?\s*Terminal.*': 'Terminal',
            r'.*?-?\s*WezTerm.*': 'WezTerm',

            # Файловые менеджеры
            r'.*?-?\s*Nautilus.*': 'Files',
            r'.*?-?\s*Files.*': 'Files',
            r'.*?-?\s*Thunar.*': 'Thunar',
            r'.*?-?\s*Dolphin.*': 'Dolphin',

            # Мессенджеры
            r'.*?-?\s*Discord.*': 'Discord',
            r'.*?-?\s*Telegram.*': 'Telegram',
            r'.*?-?\s*Slack.*': 'Slack',
            r'.*?-?\s*Microsoft Teams.*': 'Teams',
            r'.*?-?\s*WhatsApp.*': 'WhatsApp',

            # Медиа
            r'.*?-?\s*VLC.*': 'VLC',
            r'.*?-?\s*mpv.*': 'mpv',
            r'.*?-?\s*Spotify.*': 'Spotify',

            # LibreOffice
            r'.*?-?\s*LibreOffice Writer.*': 'LibreOffice Writer',
            r'.*?-?\s*LibreOffice Calc.*': 'LibreOffice Calc',
            r'.*?-?\s*LibreOffice Impress.*': 'LibreOffice Impress',
            r'.*?-?\s*LibreOffice.*': 'LibreOffice',

            # Vim/Neovim
            r'.*?-?\s*Vim.*': 'Vim',
            r'.*?-?\s*Neovim.*': 'Neovim',
            r'.*?-?\s*nvim.*': 'Neovim',

            # Другие редакторы
            r'.*?-?\s*Sublime Text.*': 'Sublime Text',
            r'.*?-?\s*Atom.*': 'Atom',
            r'.*?-?\s*Emacs.*': 'Emacs',
        }

    def run_command(self, cmd: list, timeout: float = 2.0) -> Optional[str]:
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False
            )
            return result.stdout.strip() if result.returncode == 0 else None
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
            return None

    def get_hyprland_window(self) -> Optional[str]:
        try:
            output = self.run_command(['hyprctl', 'activewindow', '-j'])
            if output:
                data = json.loads(output)
                return data.get('title', '').strip()
        except json.JSONDecodeError:
            pass
        return None

    def get_sway_window(self) -> Optional[str]:
        try:
            output = self.run_command(['swaymsg', '-t', 'get_tree'])
            if output:
                data = json.loads(output)
                focused = self._find_focused_sway(data)
                return focused.get('name', '').strip() if focused else None
        except json.JSONDecodeError:
            pass
        return None

    def _find_focused_sway(self, node: dict) -> Optional[dict]:
        if node.get('focused'):
            return node

        for child in node.get('nodes', []) + node.get('floating_nodes', []):
            result = self._find_focused_sway(child)
            if result:
                return result
        return None

    def get_i3_window(self) -> Optional[str]:
        try:
            output = self.run_command(['i3-msg', '-t', 'get_tree'])
            if output:
                data = json.loads(output)
                focused = self._find_focused_i3(data)
                return focused.get('name', '').strip() if focused else None
        except json.JSONDecodeError:
            pass
        return None

    def _find_focused_i3(self, node: dict) -> Optional[dict]:
        if node.get('focused'):
            return node

        for child in node.get('nodes', []):
            result = self._find_focused_i3(child)
            if result:
                return result
        return None

    def get_x11_window(self) -> Optional[str]:
        methods = [
            ['xdotool', 'getactivewindow', 'getwindowname'],
            ['xwininfo', '-id', '$(xprop -root _NET_ACTIVE_WINDOW | cut -d\' \' -f5)', '2>/dev/null'],
            ['wmctrl', '-l']
        ]

        for method in methods:
            if method[0] == 'xdotool':
                title = self.run_command(method)
                if title:
                    return title
            elif method[0] == 'wmctrl':
                output = self.run_command(method)
                if output:
                    lines = output.split('\n')
                    for line in lines:
                        if '*' in line:  # Активное окно помечено звездочкой
                            parts = line.split(None, 3)
                            return parts[3] if len(parts) > 3 else None

        return None

    def get_kde_window(self) -> Optional[str]:
        title = self.run_command(['qdbus', 'org.kde.KWin', '/KWin', 'activeWindow'])
        if title and title != 'none':
            return title
        return None

    def get_gnome_window(self) -> Optional[str]:
        try:
            output = self.run_command([
                'gdbus', 'call', '--session',
                '--dest', 'org.gnome.Shell',
                '--object-path', '/org/gnome/Shell',
                '--method', 'org.gnome.Shell.Eval',
                'global.display.focus_window.get_wm_class()'
            ])
            if output and 'true' in output:
                return output.split(',')[1].strip().strip("'\"")
        except:
            pass
        return None

    def extract_app_name(self, title: str) -> str:
        """Извлекает название приложения из заголовка окна"""
        if not title:
            return ""

        # Проверяем паттерны для известных приложений
        for pattern, app_name in self.app_patterns.items():
            if re.match(pattern, title, re.IGNORECASE):
                return app_name

        # Если не найдено соответствие в паттернах, пытаемся извлечь из конца заголовка
        # Многие приложения имеют формат "Документ - Приложение"
        if ' - ' in title:
            parts = title.split(' - ')
            if len(parts) >= 2:
                # Берем последнюю часть как название приложения
                potential_app = parts[-1].strip()
                # Проверяем, что это не выглядит как путь к файлу
                if not ('/' in potential_app or '\\' in potential_app or '.' in potential_app[-4:]):
                    return potential_app

        # Если ничего не подошло, возвращаем оригинальный заголовок (обрезанный)
        return self.clean_title(title)

    def clean_title(self, title: str) -> str:
        if not title:
            return ""

        title = re.sub(r'[^\x20-\x7E\u00A0-\uFFFF]', '', title)

        if len(title) > 50:
            title = title[:47] + "..."

        return title.strip()

    def get_app_icon(self, app_name: str) -> str:
        app_name_lower = app_name.lower()

        for app_key, icon in self.app_icons.items():
            if app_key in app_name_lower:
                return icon

        return self.app_icons['default']

    def detect_environment(self) -> str:
        if os.environ.get('HYPRLAND_INSTANCE_SIGNATURE'):
            return 'hyprland'
        elif os.environ.get('SWAYSOCK'):
            return 'sway'
        elif os.environ.get('I3SOCK'):
            return 'i3'
        elif os.environ.get('KDE_FULL_SESSION'):
            return 'kde'
        elif os.environ.get('GNOME_DESKTOP_SESSION_ID'):
            return 'gnome'
        elif os.environ.get('DISPLAY'):
            return 'x11'
        elif os.environ.get('WAYLAND_DISPLAY'):
            return 'wayland'
        else:
            return 'unknown'

    def get_window_title(self) -> str:
        current_time = time.time()

        if (self.last_result and
            current_time - self.last_update < self.cache_timeout):
            return self.last_result

        env = self.detect_environment()
        title = None

        if env == 'hyprland':
            title = self.get_hyprland_window()
        elif env == 'sway':
            title = self.get_sway_window()
        elif env == 'i3':
            title = self.get_i3_window()
        elif env == 'kde':
            title = self.get_kde_window()
        elif env == 'gnome':
            title = self.get_gnome_window()

        if not title and os.environ.get('DISPLAY'):
            title = self.get_x11_window()

        if not title:
            title = "󰘳 Desktop"
        else:
            # Извлекаем название приложения вместо полного заголовка
            app_name = self.extract_app_name(title)
            if app_name:
                icon = self.get_app_icon(app_name)
                title = f"{icon} {app_name}"
            else:
                title = "󰘳 Desktop"

        self.last_result = title
        self.last_update = current_time

        return title

    def get_json_output(self) -> str:
        title = self.get_window_title()

        title_escaped = title.replace('"', '\\"').replace('\\', '\\\\')

        return json.dumps({
            "text": title_escaped,
            "tooltip": title_escaped,
            "class": "window-title"
        }, ensure_ascii=False)

def main():
    try:
        tracker = WindowTracker()

        if len(sys.argv) > 1 and sys.argv[1] == '--json':
            print(tracker.get_json_output())
        else:
            print(tracker.get_json_output())

    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        fallback = json.dumps({
            "text": "󰘳 Desktop",
            "tooltip": f"Error: {str(e)}",
            "class": "window-title-error"
        })
        print(fallback)
        sys.exit(1)

if __name__ == "__main__":
    main()
