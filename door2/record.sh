#!/bin/bash
# Records door 2 on a 1280x720 virtual screen: a terminal along the bottom, the browser window above it.
#   door2/record.sh headful 21 headful.mp4      (from a clone of main, with Playwright installed)
#   door2/record.sh headless 21 headless.mp4
# Needs Xvfb, xterm, xdotool, xsetroot (x11-xserver-utils) and ffmpeg. Then, for a GIF:
#   ffmpeg -i headful.mp4 -vf "fps=10,scale=960:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=128:stats_mode=diff[p];[b][p]paletteuse=dither=bayer:bayer_scale=4:diff_mode=rectangle" door2_headful.gif
# Each slide GIF starts with a 20 ms still of the finished state (a poster frame), so a thumbnail or a PDF
# export shows the browser or the output rather than an empty screen:
#   ffmpeg -ss 12.5 -i headful.mp4 -frames:v 1 poster.png   (the headless one uses its last frame)
#   gifsicle --loopcount=forever -d2 poster.gif -d10 door2_headful.gif -o out.gif
MODE=$1; SECS=$2; OUT=$3; R=$(cd "$(dirname "$0")" && pwd)
export DISPLAY=:99
Xvfb :99 -screen 0 1280x720x24 -dpi 96 -noreset -nolisten tcp >/dev/null 2>&1 & XV=$!
for i in $(seq 50); do xsetroot -solid '#3A4A57' 2>/dev/null && break; sleep 0.1; done
sleep 0.3
( while true; do
    for w in $(xdotool search --onlyvisible --class '[Cc]hromium' 2>/dev/null); do
      xdotool windowmove "$w" 0 0 windowsize "$w" 1280 508 2>/dev/null
    done
    sleep 0.05
  done ) & PL=$!
ffmpeg -loglevel error -y -f x11grab -draw_mouse 0 -framerate 12 -video_size 1280x720 -i :99.0 -t "$SECS" -pix_fmt yuv420p "$OUT" & FF=$!
xterm -fa 'DejaVu Sans Mono' -fs 13 -bg '#172231' -fg '#EEF2F6' -b 8 -geometry 124x10+0+508 -e "$R/run.sh" "$MODE" & XT=$!
wait $FF
kill $PL $XT $XV 2>/dev/null
wait 2>/dev/null
echo "recorded $OUT"
