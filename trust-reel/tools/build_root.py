#!/usr/bin/env python3
"""Write the audio block of index.html: narration, two music beds and every SFX hit.

Times are global seconds. Music fades live in data-automation; the carve (voice-over EQ dip) is
added afterwards by carve.mjs and preserved here: existing data-fx-* attributes are kept.
Run: python3 tools/build_root.py
"""
import json, re, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"
END = 49.4

def dur(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(ROOT / p)],
                                capture_output=True, text=True, check=True).stdout)

def auto(points):
    return json.dumps({"version": 1, "lanes": [{"target": "volume", "points": [{"t": t, "v": v} for t, v in points]}]}, separators=(",", ":"))

SFX = [  # (file, global time, volume)
    ("paper-crumple", 2.26, 0.7), ("paper-crumple", 2.70, 0.6), ("whoosh-soft", 3.40, 0.35),
    ("bin-drop", 4.36, 0.8), ("bin-drop", 4.50, 0.6), ("whoosh-deep", 5.42, 0.7),
    ("screen-on", 6.08, 0.5), ("counter-ticks", 6.35, 0.25), ("swipe", 7.34, 0.55), ("lonely-tick", 8.17, 0.6),
    ("swipe", 9.10, 0.4), ("whoosh-soft", 9.12, 0.3), ("counter-ticks", 11.55, 0.3), ("whoosh-soft", 13.55, 0.35),
    ("lonely-tick", 14.45, 0.6), ("whoosh-soft", 15.50, 0.3), ("swipe", 17.45, 0.5), ("lonely-tick", 18.50, 0.5),
    ("whoosh-deep", 18.78, 0.7),
    ("impact-sub", 19.20, 0.55), ("glitch", 20.90, 0.35), ("glitch", 22.00, 0.35), ("ding-clean", 23.40, 0.35),
    ("whoosh-soft", 25.97, 0.35), ("tile-pop", 27.43, 0.5), ("tile-pop", 28.51, 0.5), ("tile-pop", 29.77, 0.5),
    ("ding-clean", 30.20, 0.3), ("whoosh-deep", 31.50, 0.55),
] + [("dm-ping", round(33.30 + i * 0.17, 2), round(0.34 - i * 0.02, 2)) for i in range(8)] + [
    ("whoosh-deep", 34.85, 0.55), ("counter-ticks", 38.20, 0.3), ("tap", 41.13, 0.7), ("whoosh-soft", 41.85, 0.3),
    ("typing", 45.65, 0.6), ("send", 47.45, 0.5), ("ding-clean", 48.00, 0.35),
]

html = INDEX.read_text()
keep = {}
for m in re.finditer(r'<audio id="(music-[a-z]+)"([^>]*)>', html):
    fx = re.findall(r'(data-fx-[a-z]+="[^"]*")', m.group(2))
    keep[m.group(1)] = " ".join(fx)

lines = []
vo = dur("assets/audio/vo/narration.wav")
lines.append(f'<audio id="narration" src="assets/audio/vo/narration.wav" data-start="0.2" data-duration="{vo:.2f}" data-track-index="10" data-volume="1"></audio>')
st = 19.5
lines.append(f'<audio id="music-story" src="assets/audio/music/story.mp3" data-start="0" data-duration="{st}" data-track-index="11" data-volume="0.42" '
             f"data-automation='{auto([(0, 1), (8.1, 1), (8.3, 0.55), (8.9, 0.55), (9.3, 1), (18.5, 1), (19.4, 0)])}' {keep.get('music-story', '')}></audio>")
tip_start = 19.22
lines.append(f'<audio id="music-tip" src="assets/audio/music/tip.mp3" data-start="{tip_start}" data-duration="{END - tip_start:.2f}" data-track-index="12" data-volume="0.40" '
             f"data-automation='{auto([(0, 1), (END - tip_start - 0.6, 1), (END - tip_start, 0)])}' {keep.get('music-tip', '')}></audio>")
for k, (name, t, v) in enumerate(SFX):
    d = dur(f"assets/audio/sfx/{name}.wav")
    d = min(d, END - t)
    lines.append(f'<audio id="sfx-{k:02d}-{name}" src="assets/audio/sfx/{name}.wav" data-start="{t:.2f}" data-duration="{d:.2f}" data-track-index="{13 + k % 4}" data-volume="{v}"></audio>')

block = "      <!-- AUDIO (tools/build_root.py) -->\n      " + "\n      ".join(lines) + "\n      <!-- /AUDIO -->"
if "<!-- AUDIO" in html:
    html = re.sub(r"      <!-- AUDIO.*?<!-- /AUDIO -->", lambda m: block, html, flags=re.S)
else:
    html = re.sub(r'      <audio id="narration"[^\n]*</audio>', lambda m: block, html)
INDEX.write_text(html)
print(f"{len(SFX)} sfx, narration {vo:.2f}s")
