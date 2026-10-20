#!/usr/bin/env bash
# Usage: pexels_probe.sh <video_id>  -> prints the first working file URLs (largest first)
id="$1"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
cands=()
for q in uhd hd sd; do
  for d in 2160_3840 1440_2560 1080_1920 720_1280 540_960 3840_2160 2560_1440 1920_1080 1280_720 960_540 4096_2160 2048_1080 1366_720; do
    for f in 30 25 24 60 50; do
      cands+=("https://videos.pexels.com/video-files/$id/$id-${q}_${d}_${f}fps.mp4")
    done
  done
done
printf "%s\n" "${cands[@]}" | xargs -P 24 -I{} sh -c 'c=$(curl -s -o /dev/null -m 15 -A "'"$UA"'" -I -w "%{http_code}" "{}"); [ "$c" = "200" ] && echo "{}"'
