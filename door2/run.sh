#!/bin/bash
# What the recorded terminal shows: the command typed, then the real run of doors/door2_megaworld.py
MODE=$1
CMD="python -m doors.door2_megaworld"
[ "$MODE" = headful ] && CMD="$CMD --headful"
sleep 1.2
printf '\033[1;36m~/navigating-the-grey\033[0m $ '
for ((i=0; i<${#CMD}; i++)); do printf '%s' "${CMD:$i:1}"; sleep 0.04; done
sleep 0.5; echo
$CMD 2>&1
printf '\033[1;36m~/navigating-the-grey\033[0m $ '
sleep 30
