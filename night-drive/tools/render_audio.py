"""Sound design: car-stereo music (muffled -> open -> muffled), drone in F,
riser, impacts, reverb tail. Writes a float WAV."""
import subprocess, sys, wave
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve
from timeline import SRC, T0, T_ON, T_OFF, T_END, TOTAL, _smooth

OUT = sys.argv[1]
SR = 48000
N = int(TOTAL * SR)
t = np.arange(N) / SR
rng = np.random.default_rng(11)


def lp(x, f, order=4):
    return sosfilt(butter(order, f, "low", fs=SR, output="sos"), x, axis=0)


def hp(x, f, order=4):
    return sosfilt(butter(order, f, "high", fs=SR, output="sos"), x, axis=0)


def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], "band", fs=SR, output="sos"), x, axis=0)


def st(x):
    return np.stack([x, x], axis=1) if x.ndim == 1 else x


def env_seg(t0, t1, ramp_in=0.0, ramp_out=0.0):
    e = np.ones(N)
    if ramp_in > 0:
        e *= _smooth((t - t0) / ramp_in)
    else:
        e *= (t >= t0)
    if ramp_out > 0:
        e *= 1 - _smooth((t - (t1 - ramp_out)) / ramp_out)
    else:
        e *= (t < t1)
    return e


# ------------------------------------------------------------------ music
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", SRC, "-ac", "2", "-ar", str(SR),
                      "-f", "f32le", "-"], capture_output=True, check=True).stdout
src = np.frombuffer(raw, np.float32).reshape(-1, 2).astype(np.float64)
music = np.zeros((N, 2))
i0 = int(T0 * SR)
n = min(len(src), N - i0)
music[i0:i0 + n] = src[:n]

muff = lp(music, 380, 4) * 0.55         # "through the wall" version
muff = muff + 0.10 * lp(music, 1500, 2)
# open amount: closed before the reveal, slams open on the hit, closes on lights-off
open_amt = _smooth((t - T_ON) / 0.04) * (1 - _smooth((t - T_OFF) / 0.35))
open_amt = open_amt[:, None]
mus = muff * (1 - open_amt) + music * open_amt
# level: fade in, short "suck" before the hit, fade out after lights-off
mlev = _smooth((t - T0) / 1.2) * 0.8 + 0.2 * _smooth((t - T_ON) / 0.05)
suck = 1 - (_smooth((t - (T_ON - 0.16)) / 0.06) * (1 - _smooth((t - T_ON) / 0.01)))
mlev = mlev * suck * (1 - _smooth((t - (T_OFF + 0.05)) / 0.85))
mus = mus * mlev[:, None]

# ------------------------------------------------------------------ reverb
def make_ir(rt=2.8, seconds=3.5):
    m = int(seconds * SR)
    tt = np.arange(m) / SR
    decay = np.exp(-6.9 * tt / rt)
    ir = rng.normal(size=(m, 2)) * decay[:, None]
    ir = lp(ir, 5200, 2)
    ir[: int(0.018 * SR)] = 0                         # pre-delay
    return ir / np.sqrt((ir ** 2).sum(axis=0))

IR = make_ir()


def reverb(x):
    return np.stack([fftconvolve(x[:, c], IR[:, c])[:N] for c in range(2)], axis=1)


# ------------------------------------------------------------------ drone in F
def tone(freq, amp, detune=0.12):
    l = np.sin(2 * np.pi * (freq + detune) * t)
    r = np.sin(2 * np.pi * (freq - detune) * t + 0.7)
    return np.stack([l, r], axis=1) * amp

drone = tone(43.65, 0.45) + tone(65.41, 0.28) + tone(87.31, 0.22) + tone(130.81, 0.06)
drone *= (0.85 + 0.15 * np.sin(2 * np.pi * 0.13 * t))[:, None]
rumble = lp(rng.normal(size=(N, 2)), 160, 4) * 0.9    # tyre / road rumble
d_env = (_smooth(t / 1.4) * 0.20
         * (1 - 0.70 * _smooth((t - T_ON) / 0.3))
         * (1 + 1.6 * _smooth((t - T_OFF) / 0.8))
         * (1 - _smooth((t - (TOTAL - 2.2)) / 2.0)))
drone = (drone + rumble * 0.35) * d_env[:, None]

# high shimmer pad for the city-lights ending
sh = tone(698.46, 0.05, 0.6) + tone(1046.5, 0.035, 0.9) + tone(1396.9, 0.02, 1.3)
sh *= (0.6 + 0.4 * np.sin(2 * np.pi * 0.4 * t))[:, None]
sh *= (_smooth((t - (T_OFF + 0.3)) / 1.8) * (1 - _smooth((t - (TOTAL - 2.0)) / 1.8)))[:, None]

# ------------------------------------------------------------------ riser
r0, r1 = T_ON - 2.6, T_ON - 0.16
k = np.clip((t - r0) / (r1 - r0), 0, 1)
active = ((t >= r0) & (t < r1)).astype(float)
noise = rng.normal(size=(N, 2))
riser_noise = bp(noise, 2500, 11000) * (k ** 3)[:, None] * 0.22
f_sweep = 90 * (8 ** k)                                   # 90 Hz -> 720 Hz
ph = 2 * np.pi * np.cumsum(f_sweep) / SR
riser_tone = np.tanh(2.2 * np.sin(ph)) * (k ** 2.2) * 0.16
riser = (riser_noise + st(riser_tone)) * active[:, None]

# ------------------------------------------------------------------ impacts
def boom(t_hit, f0, f1, decay, amp, crack=0.5):
    tau = t - t_hit
    on = tau >= 0
    tau_c = np.clip(tau, 0, None)
    f = f1 + (f0 - f1) * np.exp(-tau_c / 0.09)
    ph = 2 * np.pi * np.cumsum(f * on) / SR
    sub = np.sin(ph) * np.exp(-tau_c / decay) * (1 - np.exp(-tau_c / 0.004)) * on
    burst = lp(rng.normal(size=N), 2600, 2) * np.exp(-tau_c / 0.05) * on
    click = hp(rng.normal(size=N), 4000, 2) * np.exp(-tau_c / 0.006) * on
    x = amp * np.tanh(1.6 * sub) + crack * (0.6 * burst + 0.25 * click)
    return st(x)

hit_on = boom(T_ON, 85, 36, 1.1, 0.75, crack=0.45)
hit_off = boom(T_OFF, 70, 32, 0.8, 0.50, crack=0.20)

# soft bell as the city lights settle (F5 + octave), lives in the reverb
b0 = T_OFF + 1.0
btau = np.clip(t - b0, 0, None)
bell = (np.sin(2 * np.pi * 698.46 * btau) + 0.35 * np.sin(2 * np.pi * 1396.9 * btau)
        + 0.15 * np.sin(2 * np.pi * 2095.4 * btau)) * np.exp(-btau / 1.4) * (t >= b0)
bell = st(bell * (1 - np.exp(-btau / 0.01)) * 0.07)

# ------------------------------------------------------------------ mix
send_music = (0.05 + 0.5 * _smooth((t - T_OFF) / 0.3))[:, None]
wet = reverb(mus * send_music + hit_on * 0.22 + hit_off * 0.35
             + bell * 1.5 + sh * 0.8 + riser * 0.3)
mix = (mus + drone + sh + riser + hit_on + hit_off + bell + 0.45 * wet)
mix *= (1 - _smooth((t - (TOTAL - 0.6)) / 0.6))[:, None]
# gentle glue + soft clip
peak = np.abs(mix).max()
mix = mix / peak
mix = np.tanh(mix * 1.4) / np.tanh(1.4)       # soft glue on the hits
mix = (mix * 0.89).astype(np.float32)

import scipy.io.wavfile as wf
wf.write(OUT, SR, mix)
print("audio written", OUT, f"{TOTAL:.2f}s peak {peak:.2f}")
