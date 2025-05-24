#!/bin/bash
read -r total used free shared buff cache available <<< $(free -m | awk 'NR==2{print $2" "$3" "$4" "$5" "$6" "$7" "$7}')
percent=$(( 100 * used / total ))
echo "{\"text\": \"󰍛 $percent%\"}"
