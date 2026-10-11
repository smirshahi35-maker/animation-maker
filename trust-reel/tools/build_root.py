#!/usr/bin/env python3
"""Write the audio block of index.html: narration, two music beds and every SFX hit.

Times are global seconds. The beds' level against the voice comes from the carve's level-match lane
(carve.mjs measures the raw file), so each bed's own volume lane only shapes it: dips and fades
(data-volume stays 1; a lane's values are absolute). The carve (voice-over EQ dip) is added afterwards by carve.mjs, which
keeps that lane and appends its own:
  python3 tools/build_root.py
  node ~/.claude/skills/hyperframes-audio/scripts/carve.mjs --comp index.html --bed music-story --voice narration --strength 0.7
  node ~/.claude/skills/hyperframes-audio/scripts/carve.mjs --comp index.html --bed music-tip --voice narration --strength 0.7
"""
import html as htmllib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"
END = 50.04
S = 0.64  # the re-recorded hook is 0.64 s longer: s2, s3, s4 start that much later than in draft 1


def dur(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(ROOT / p)],
                                capture_output=True, text=True, check=True).stdout)


def auto(points):
    """A volume lane as an escaped, double-quoted attribute (the form carve.mjs reads and keeps)."""
    lane = {"version": 1, "lanes": [{"target": "volume", "points": [{"t": round(t, 3), "v": v} for t, v in points]}]}
    return 'data-automation="' + htmllib.escape(json.dumps(lane, separators=(",", ":")), quote=True) + '"'


SFX = [  # (file, global time, volume[, max duration]); "-hot" files are compressed copies of quiet one-shots
    ("paper-crumple-hot", 2.33, 0.25), ("paper-crumple-hot", 2.71, 0.2), ("whoosh-soft", 3.36, 0.12),
    ("bin-drop", 4.52, 0.8), ("bin-drop", 4.68, 0.6), ("whoosh-deep", 6.09, 0.35), ("whoosh-soft", 6.36, 0.4),
    ("screen-on-hot", 6.66, 0.2), ("counter-ticks", 6.35 + S, 0.25), ("swipe", 7.34 + S, 0.55), ("lonely-tick", 8.17 + S, 0.6),
    ("swipe", 9.10 + S, 0.4), ("whoosh-soft", 9.12 + S, 0.3), ("counter-ticks", 11.55 + S, 0.3), ("whoosh-soft", 13.55 + S, 0.12),
    ("lonely-tick", 14.45 + S, 0.6), ("whoosh-soft", 15.50 + S, 0.35), ("swipe", 17.12 + S, 0.5), ("lonely-tick", 18.50 + S, 0.5),
    ("whoosh-deep", 18.78 + S, 0.35), ("whoosh-soft", 18.85 + S, 0.4),
    ("impact-sub", 19.20 + S, 0.2), ("glitch", 20.90 + S, 0.2), ("glitch", 22.00 + S, 0.13), ("ding-clean", 23.40 + S, 0.35),
    ("whoosh-soft", 25.97 + S, 0.35), ("tile-pop-hot", 27.43 + S, 0.35), ("tile-pop-hot", 28.51 + S, 0.35),
    ("tile-pop-hot", 29.77 + S, 0.35), ("ding-clean", 30.20 + S, 0.3), ("whoosh-deep", 31.50 + S, 0.3), ("whoosh-soft", 31.58 + S, 0.4),
] + [("dm-ping", round(33.30 + S + i * 0.17, 2), round(0.14 - i * 0.01, 2)) for i in range(6)] + [
    ("whoosh-deep", 34.50 + S, 0.25), ("whoosh-soft", 34.50 + S, 0.3), ("counter-ticks", 38.20 + S, 0.3),
    ("whoosh-soft", 39.28 + S, 0.35), ("tap-hot", 41.13 + S, 0.6), ("whoosh-soft", 41.85 + S, 0.13),
    ("typing", 46.08, 0.3, 0.56), ("send", 47.74, 0.5), ("ding-clean", 48.29, 0.35),
]

html = INDEX.read_text()
lines = []
vo = dur("assets/audio/vo/narration.wav")
lines.append(f'<audio id="narration" src="assets/audio/vo/narration.wav" data-start="0.2" data-duration="{vo:.2f}" data-track-index="10" data-volume="1"></audio>')
# Shape only: the carve level-matches the raw beds 13-19 dB under the voice. tip.mp3 is ~4 dB hotter than story.mp3.
st = 19.5 + S
lines.append(f'<audio id="music-story" src="assets/audio/music/story.mp3" data-start="0" data-duration="{st:.2f}" data-track-index="11" data-volume="1" '
             f'{auto([(0, 1.0), (8.1 + S, 1.0), (8.3 + S, 0.57), (8.9 + S, 0.57), (9.3 + S, 1.0), (18.5 + S, 1.0), (19.4 + S, 0)])}></audio>')
tip_start = 19.22 + S
lines.append(f'<audio id="music-tip" src="assets/audio/music/tip.mp3" data-start="{tip_start:.2f}" data-duration="{END - tip_start:.2f}" data-track-index="12" data-volume="1" '
             f'{auto([(0, 0.6), (END - tip_start - 0.6, 0.6), (END - tip_start, 0)])}></audio>')
for k, (name, t, v, *mx) in enumerate(SFX):
    d = min(dur(f"assets/audio/sfx/{name}.wav"), END - t, *mx)
    lines.append(f'<audio id="sfx-{k:02d}-{name}" src="assets/audio/sfx/{name}.wav" data-start="{t:.2f}" data-duration="{d:.2f}" data-track-index="{13 + k % 4}" data-volume="{v}"></audio>')

block = "      <!-- AUDIO (tools/build_root.py) -->\n      " + "\n      ".join(lines) + "\n      <!-- /AUDIO -->"
if "<!-- AUDIO" in html:
    html = re.sub(r"      <!-- AUDIO.*?<!-- /AUDIO -->", lambda m: block, html, flags=re.S)
else:
    html = re.sub(r'      <audio id="narration"[^\n]*</audio>', lambda m: block, html)
INDEX.write_text(html)
print(f"{len(SFX)} sfx, narration {vo:.2f}s; now run carve.mjs on music-story and music-tip")
