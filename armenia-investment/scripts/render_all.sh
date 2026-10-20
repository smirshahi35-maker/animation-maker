#!/usr/bin/env bash
# Render the full reel in 3 parallel parts and join them with the audio mix.
cd "$(dirname "$0")/.." || exit 1
export NODE_PATH=/opt/node-tools/node_modules
mkdir -p build/seg renders
for r in "0 500" "500 1000" "1000 1500"; do
  set -- $r
  node scripts/render.js video build/seg/seg_$1.mp4 $1 $2 > build/seg/log_$1.txt 2>&1 &
done
wait
printf "file '%s'\n" "$PWD/build/seg/seg_0.mp4" "$PWD/build/seg/seg_500.mp4" "$PWD/build/seg/seg_1000.mp4" > build/seg/list.txt
ffmpeg -v error -y -f concat -safe 0 -i build/seg/list.txt -i audio/mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart renders/armenia-investment-reel.mp4
echo "DONE $(ffprobe -v error -show_entries format=duration -of csv=p=0 renders/armenia-investment-reel.mp4)"
