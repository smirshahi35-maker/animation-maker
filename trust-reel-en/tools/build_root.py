#!/usr/bin/env python3
"""Write the audio block of index.html (English version): narration, two music beds and every SFX hit.

Same mix as the Persian film (../trust-reel/tools/build_root.py): same SFX files and levels, re-timed to the
English scenes. SFX times are scene-local in tools/sfx_en.json ({"<k>": {"scene": "s2", "t": 1.62}, ...}),
keyed by the SFX number k (the order of the list below, as in TIMING.md).

The beds' level against the voice comes from the carve's level-match lane (carve.mjs measures the raw file),
so each bed's own volume lane only shapes it: dips and fades (data-volume stays 1). Then:
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
END = 49.30
SCENES = {"s1": 0.0, "s2": 6.14, "s3": 19.28, "s4": 32.84}


def dur(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(ROOT / p)],
                                capture_output=True, text=True, check=True).stdout)


def auto(points):
    """A volume lane as an escaped, double-quoted attribute (the form carve.mjs reads and keeps)."""
    lane = {"version": 1, "lanes": [{"target": "volume", "points": [{"t": round(t, 3), "v": v} for t, v in points]}]}
    return 'data-automation="' + htmllib.escape(json.dumps(lane, separators=(",", ":")), quote=True) + '"'


SFX = [  # (file, volume[, max duration]) in the order of TIMING.md (k = index); levels as in the Persian mix
    ("paper-crumple-hot", 0.2), ("paper-crumple-hot", 0.14), ("whoosh-soft", 0.06),
    ("bin-drop", 0.45), ("bin-drop", 0.35), ("whoosh-deep", 0.35), ("whoosh-soft", 0.12),
    ("screen-on-hot", 0.1), ("counter-ticks", 0.15), ("swipe", 0.35), ("lonely-tick", 0.35),
    ("swipe", 0.3), ("whoosh-soft", 0.12), ("counter-ticks", 0.18), ("whoosh-soft", 0.06),
    ("lonely-tick", 0.3), ("whoosh-soft", 0.12), ("swipe", 0.25), ("lonely-tick", 0.22),
    ("whoosh-deep", 0.3), ("whoosh-soft", 0.12),
    ("impact-sub", 0.2), ("glitch", 0.07), ("glitch", 0.11), ("ding-clean", 0.1),
    ("whoosh-soft", 0.15), ("tile-pop-hot", 0.3), ("tile-pop-hot", 0.25),
    ("tile-pop-hot", 0.3), ("ding-clean", 0.09), ("whoosh-deep", 0.3), ("whoosh-soft", 0.12),
] + [("dm-ping", round(0.07 - i * 0.01, 2)) for i in range(6)] + [
    ("whoosh-deep", 0.25), ("whoosh-soft", 0.15), ("counter-ticks", 0.18, 1.1),
    ("whoosh-soft", 0.3), ("tap-hot", 0.5), ("whoosh-soft", 0.13),
    ("typing", 0.12, 0.56), ("send", 0.5), ("ding-clean", 0.35),
]

times = json.load(open(ROOT / "tools/sfx_en.json"))
assert len(times) == len(SFX), f"sfx_en.json has {len(times)} entries, expected {len(SFX)}"

html = INDEX.read_text()
lines = []
vo = dur("assets/audio/vo/narration.wav")
lines.append(f'<audio id="narration" src="assets/audio/vo/narration.wav" data-start="0.2" data-duration="{vo:.2f}" data-track-index="10" data-volume="1"></audio>')
# Story bed: +3 dB shape, a dip under the empty inbox ("DMs are empty?"), fade into the tip bed at the ring fly-through.
s2, s3 = SCENES["s2"], SCENES["s3"]
st = s3 + 0.25
lines.append(f'<audio id="music-story" src="assets/audio/music/story.mp3" data-start="0" data-duration="{st:.2f}" data-track-index="11" data-volume="1" '
             f'{auto([(0, 1.4), (s2 + 2.1, 1.4), (s2 + 2.3, 0.8), (s2 + 2.9, 0.8), (s2 + 3.3, 1.4), (s3 - 0.65, 1.4), (s3 + 0.25, 0)])}></audio>')
tip_start = s3 + 0.07
lines.append(f'<audio id="music-tip" src="assets/audio/music/tip.mp3" data-start="{tip_start:.2f}" data-duration="{END - tip_start:.2f}" data-track-index="12" data-volume="1" '
             f'{auto([(0, 0.6), (END - tip_start - 0.6, 0.6), (END - tip_start, 0)])}></audio>')
for k, (name, v, *mx) in enumerate(SFX):
    e = times[str(k)]
    t = SCENES[e["scene"]] + e["t"]
    d = min(dur(f"assets/audio/sfx/{name}.wav"), END - t, *mx)
    lines.append(f'<audio id="sfx-{k:02d}-{name}" src="assets/audio/sfx/{name}.wav" data-start="{t:.2f}" data-duration="{d:.2f}" data-track-index="{13 + k % 4}" data-volume="{v}"></audio>')

block = "      <!-- AUDIO (tools/build_root.py) -->\n      " + "\n      ".join(lines) + "\n      <!-- /AUDIO -->"
html = re.sub(r"      <!-- AUDIO.*?<!-- /AUDIO -->", lambda m: block, html, flags=re.S)
INDEX.write_text(html)
print(f"{len(SFX)} sfx, narration {vo:.2f}s; now run carve.mjs on music-story and music-tip")
