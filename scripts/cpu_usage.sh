#!/bin/bash
set -eu

# читаем первую строку /proc/stat
read -r cpu user nice system idle iowait irq softirq steal _ < /proc/stat
prev_idle=$((idle + iowait))
prev_total=$((user + nice + system + idle + iowait + irq + softirq + steal))
sleep 1
read -r cpu user nice system idle iowait irq softirq steal _ < /proc/stat
idle2=$((idle + iowait))
total2=$((user + nice + system + idle + iowait + irq + softirq + steal))
diff_idle=$((idle2 - prev_idle))
diff_total=$((total2 - prev_total))
usage=$((100 * (diff_total - diff_idle) / diff_total))

echo "{\"text\":\" $usage%\"}"
