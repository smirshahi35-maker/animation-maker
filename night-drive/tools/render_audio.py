"""Audio: the clip's own song, nothing added.

The original track plays from t=0 in sync with the picture. It fades out over
the last stretch once the headlights go off, with a little of its own reverb
so it dissolves into the city shot instead of cutting. Loudness is set at mux
time."""
import subprocess, sys
import numpy as np
import scipy.io.wavfile as wf
from scipy.signal import butter, sosfilt, fftconvolve
from timeline import SRC, T0, T_OFF, TOTAL, S_AUDIO_END, _smooth

OUT = sys.argv[1]
SR = 48000
N = int(TOTAL * SR)
t = np.arange(N) / SR
rng = np.random.default_rng(11)

raw = subprocess.run(["ffmpeg", "-v", "error", "-i", SRC, "-ac", "2", "-ar", str(SR),
                      "-f", "f32le", "-"], capture_output=True, check=True).stdout
src = np.frombuffer(raw, np.float32).reshape(-1, 2).astype(np.float64)
music = np.zeros((N, 2))
i0 = int(T0 * SR)
n = min(len(src), N - i0)
music[i0:i0 + n] = src[:n]

end = T0 + S_AUDIO_END
fade_in = _smooth((t - T0) / 0.08)
fade_out = 1 - _smooth((t - T_OFF) / (end - 0.03 - T_OFF))
music *= (fade_in * fade_out)[:, None]


def make_ir(rt=2.4, seconds=3.0):
    m = int(seconds * SR)
    tt = np.arange(m) / SR
    ir = rng.normal(size=(m, 2)) * np.exp(-6.9 * tt / rt)[:, None]
    ir = sosfilt(butter(2, 4500, "low", fs=SR, output="sos"), ir, axis=0)
    ir[: int(0.02 * SR)] = 0
    return ir / np.sqrt((ir ** 2).sum(axis=0))


IR = make_ir()
send = (0.03 + 0.5 * _smooth((t - T_OFF) / 0.8))[:, None]
wet = np.stack([fftconvolve(music[:, c] * send[:, 0], IR[:, c])[:N] for c in range(2)], axis=1)
mix = music + 0.5 * wet
mix *= (1 - _smooth((t - (TOTAL - 0.3)) / 0.3))[:, None]
wf.write(OUT, SR, mix.astype(np.float32))
print("audio written", OUT, f"{TOTAL:.2f}s")
