#!/usr/bin/env bash
# Usage: pexels_get.sh <video_id> <name>  -> downloads the best HD file into footage/<name>_<id>/
id="$1"; name="$2"; dir="footage/${name}_${id}"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
for d in hd_1080_1920 hd_1920_1080 uhd_1440_2560 uhd_2560_1440 hd_1080_2048 hd_720_1280 hd_1280_720 hd_1366_720; do
  for f in 30 25 24 60 50; do
    u="https://videos.pexels.com/video-files/$id/$id-${d}_${f}fps.mp4"
    if [ "$(curl -s -o /dev/null -m 15 -A "$UA" -I -w '%{http_code}' "$u")" = "200" ]; then
      mkdir -p "$dir"; curl -sS -L -m 300 -A "$UA" -o "$dir/$name.mp4" "$u" && echo "$name $id <- ${d}_${f}fps" && exit 0
    fi
  done
done
echo "$name $id: no file found"
