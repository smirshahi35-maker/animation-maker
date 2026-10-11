"""Per-SFX masking check: in 50 ms windows where the narration is actually voiced, speech-band (300-4000 Hz)
level of the voice minus that of the SFX stem (file x data-volume). Prints the worst windows per SFX under 8 dB."""
import json, re, subprocess, numpy as np
SR = 16000
def dec(p, flt=None):
    af = ["-af", flt] if flt else []
    return np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", p, *af, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                                        capture_output=True).stdout, dtype=np.float32)
BP = "highpass=f=300,lowpass=f=4000"
vo = dec('assets/audio/vo/narration.wav', BP)
voice = np.zeros(int(51 * SR), np.float32); voice[int(.2 * SR):int(.2 * SR) + len(vo)] = vo
html = open('index.html').read()
n = int(.05 * SR)
db = lambda x: 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-12)
for idn, src, a, d, v in re.findall(r'<audio id="(sfx-[^"]*)" src="([^"]+)" data-start="([0-9.]+)" data-duration="([0-9.]+)"[^>]*data-volume="([0-9.]+)"', html):
    a, d, v = float(a), float(d), float(v)
    s = dec(src, BP)[:int(d * SR)] * v
    worst = None
    for i in range(0, len(s) - n, n // 2):
        g = int(a * SR) + i
        vl, sl = db(voice[g:g + n]), db(s[i:i + n])
        if vl < -38 or sl < -60:
            continue
        m = vl - sl
        if worst is None or m < worst[0]:
            worst = (m, round(a + i / SR, 2), round(vl, 1), round(sl, 1))
    if worst and worst[0] < 8:
        print(f"{idn:26s} vol {v:<5} worst margin {worst[0]:5.1f} dB at {worst[1]} (voice {worst[2]}, sfx {worst[3]})")
