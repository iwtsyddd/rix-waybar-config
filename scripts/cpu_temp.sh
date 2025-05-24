#!/bin/bash
zone=$(grep -l "x86_pkg_temp" /sys/class/thermal/thermal_zone*/type 2>/dev/null | head -n1 | sed 's:/type::')
[ -z "$zone" ] && zone="/sys/class/thermal/thermal_zone0"
raw=$(cat "${zone}/temp")
temp=$(( raw / 1000 ))
echo "{\"text\": \" ${temp}°C\"}"
