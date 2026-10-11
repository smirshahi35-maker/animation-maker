"""Music-vs-voice check on a render: mix level in speech windows vs. music-only gaps (no speech, no SFX),
plus the estimated bed level under speech (mix minus the narration stem, aligned at the render's gain).
usage: python3 mixcheck.py <render.mp4> <project dir>"""
import json, re, subprocess, sys
import numpy as np

src, proj = sys.argv[1], sys.argv[2]
SR = 16000


def dec(p, ss=None):
    return np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                                        capture_output=True).stdout, dtype=np.float32)


mix = dec(src)
vo = dec(f"{proj}/assets/audio/vo/narration.wav")
voice = np.zeros_like(mix)
o = int(0.2 * SR)
voice[o:o + len(vo)] = vo[:len(mix) - o]
# render gain on the narration: least squares on speech samples
words = json.load(open(f"{proj}/assets/audio/vo/narration.words.json"))["words"]
html = open(f"{proj}/index.html").read()
sfx = [(float(a), float(a) + float(b)) for a, b in re.findall(r'<audio id="sfx-[^"]*"[^>]*data-start="([0-9.]+)" data-duration="([0-9.]+)"', html)]
speech = np.zeros(len(mix), bool)
for w in words:
    speech[int((w["start"] + 0.2) * SR):int((w["end"] + 0.2) * SR)] = True
busy = speech.copy()
for a, b in sfx:
    busy[int(a * SR):int(b * SR)] = True
g = float(np.dot(mix[speech], voice[speech]) / np.dot(voice[speech], voice[speech]))
bed = mix - g * voice
db = lambda x: 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-12)
print(f"render gain on narration {20*np.log10(g):+.1f} dB")
for name, a, b in [("hook s1", 0.2, 6.1), ("s2", 6.2, 19.2), ("s3", 19.3, 32.1), ("s4", 32.3, 46.6), ("end", 46.7, 48.6)]:
    sl = slice(int(a * SR), int(b * SR))
    sp, mx, bd = speech[sl], mix[sl], bed[sl]
    gap = ~busy[sl]
    line = f"{name:8s} voice {db(g*voice[sl][sp]):6.1f}  bed-under-speech {db(bd[sp]):6.1f}"
    line += f"  (Δ {db(g*voice[sl][sp]) - db(bd[sp]):4.1f} dB)"
    line += f"  music-only gaps {db(mx[gap]) if gap.sum() > SR * 0.2 else float('nan'):6.1f} dBFS ({gap.sum()/SR:.1f}s)"
    print(line)
