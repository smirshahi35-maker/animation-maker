"""Cinematic grade + camera, picture only (no text).

Quality pipeline per output frame:
  1. motion-compensated temporal denoise (DIS optical flow, +-2 frames,
     per-pixel rejection so nothing ghosts)
  2. stabilisation of the handheld path (similarity fit on the cabin,
     Gaussian-smoothed trajectory)
  3. optical-flow frame interpolation for 30->24 fps and the slow-motion
  4. one resample into the 2.39:1 frame, then grade, bloom/halation,
     anamorphic streaks, grain.
Writes H.264 video without audio.
"""
import subprocess, sys, math
from collections import OrderedDict
import numpy as np
import cv2
from scipy.ndimage import gaussian_filter1d
from timeline import SRC, FPS, SRC_FPS, T0, T_ON, T_OFF, T_END, TOTAL, src_time, _smooth

OUT = sys.argv[1]
ONLY = [float(x) for x in sys.argv[2].split(",")] if len(sys.argv) > 2 else None

SW, SH = 2336, 1080
W, H = 1920, 1080
PW, PH = 1920, 804             # 2.39:1 picture
BAR = (H - PH) // 2
BASE = PW / SW
CUTS = (146, 357, 365)         # first frame of a new lighting state


def same_segment(a, b):
    lo, hi = min(a, b), max(a, b)
    return not any(lo < c <= hi for c in CUTS)


# ---------------------------------------------------------------- decode
print("decoding source...", flush=True)
cmd = ["ffmpeg", "-v", "error", "-i", SRC, "-vf",
       "hqdn3d=1.2:1.2:0:0,scale=in_color_matrix=bt709:in_range=tv:out_range=pc,format=rgb24",
       "-f", "rawvideo", "-"]
raw = subprocess.run(cmd, capture_output=True, check=True).stdout
SRCF = np.frombuffer(raw, np.uint8).reshape(-1, SH, SW, 3)
NF = len(SRCF)
print("frames:", NF, flush=True)

LIFT = (255 * (np.arange(256) / 255.0) ** 0.5).astype(np.uint8)   # see into the shadows


def small_gray(img):
    g = cv2.cvtColor(np.clip(img, 0, 255).astype(np.uint8), cv2.COLOR_RGB2GRAY)
    return LIFT[cv2.resize(g, (SW // 2, SH // 2), interpolation=cv2.INTER_AREA)]


G0 = [small_gray(SRCF[i]) for i in range(NF)]
DIS = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
GX, GY = np.meshgrid(np.arange(SW, dtype=np.float32), np.arange(SH, dtype=np.float32))


def flow_half(ga, gb):
    return DIS.calc(ga, gb, None)


def flow_full(ga, gb):
    return cv2.resize(flow_half(ga, gb), (SW, SH), interpolation=cv2.INTER_LINEAR) * 2.0


def sample(img, f, scale):
    """img sampled at x + scale * f(x)."""
    return cv2.remap(img, GX + scale * f[..., 0], GY + scale * f[..., 1],
                     cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)


# ---------------------------------------------------------------- stabilisation
print("tracking camera...", flush=True)
_gy, _gx = np.mgrid[0:SH // 2, 0:SW // 2]
# cabin only: dashboard/seats band + pillars + headliner (not the road outside)
CABIN = ((_gy > 290) | (_gy < 30) | (_gx < 70) | (_gx > SW // 2 - 70))


def pair_motion(i):
    if not same_segment(i, i + 1):
        return 0.0, 0.0, 0.0
    ga, gb = G0[i], G0[i + 1]
    f = flow_half(ga, gb)
    gm = cv2.magnitude(cv2.Sobel(ga, cv2.CV_32F, 1, 0), cv2.Sobel(ga, cv2.CV_32F, 0, 1))
    m = CABIN & (gm > np.percentile(gm[CABIN], 80))
    ys, xs = np.nonzero(m)
    if len(xs) < 80:
        return 0.0, 0.0, 0.0
    sel = np.random.default_rng(i).choice(len(xs), min(1500, len(xs)), replace=False)
    p = np.stack([xs[sel], ys[sel]], 1).astype(np.float32)
    q = p + f[ys[sel], xs[sel]]
    A, inl = cv2.estimateAffinePartial2D(p, q, method=cv2.RANSAC, ransacReprojThreshold=1.0)
    if A is None or inl.sum() < 60:
        return 0.0, 0.0, 0.0
    ang = math.atan2(A[1, 0], A[0, 0])
    c = np.array([SW / 4, SH / 4])
    R = A[:, :2]
    tc = A[:, 2] + R @ c - c          # translation about the frame centre
    return tc[0] * 2, tc[1] * 2, ang


mot = np.array([pair_motion(i) for i in range(NF - 1)])
traj = np.vstack([[0, 0, 0], np.cumsum(mot, axis=0)])
smooth = gaussian_filter1d(traj, sigma=14, axis=0, mode="nearest")
CORR = smooth - traj
CORR[:, 0:2] = np.clip(CORR[:, 0:2], -60, 60)
CORR[:, 2] = np.clip(CORR[:, 2], -math.radians(1.2), math.radians(1.2))
print("stab correction max px:", np.abs(CORR[:, :2]).max(0).round(1),
      "deg:", round(math.degrees(np.abs(CORR[:, 2]).max()), 2), flush=True)


def corr_at(fi):
    a = int(min(max(math.floor(fi), 0), NF - 1)); b = min(a + 1, NF - 1); w = fi - a
    if not same_segment(a, b):
        return CORR[a] if w < 0.5 else CORR[b]
    return CORR[a] * (1 - w) + CORR[b] * w


# ---------------------------------------------------------------- denoise + interpolation
class LRU(OrderedDict):
    def __init__(self, n):
        super().__init__(); self.n = n

    def get_or(self, k, fn):
        if k in self:
            self.move_to_end(k); return self[k]
        v = fn(); self[k] = v
        if len(self) > self.n:
            self.popitem(last=False)
        return v


_den = LRU(6)
_gden = LRU(6)
_flows = LRU(4)


DIL = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))


def _denoise(i):
    c = SRCF[i].astype(np.float32)
    acc = c.copy()
    wsum = np.ones((SH, SW), np.float32)
    for d, base in ((-2, 0.6), (-1, 1.0), (1, 1.0), (2, 0.6)):
        j = i + d
        if j < 0 or j >= NF or not same_segment(i, j):
            continue
        f = flow_full(G0[i], G0[j])
        wj = sample(SRCF[j].astype(np.float32), f, 1.0)
        diff = cv2.GaussianBlur(np.abs(wj - c).max(axis=2), (0, 0), 1.0)
        diff = cv2.dilate(diff, DIL)                 # conservative near motion edges
        w = base * np.exp(-(diff / 4.0) ** 2)
        acc += wj * w[..., None]
        wsum += w
    return acc / wsum[..., None]


def den(i):
    return _den.get_or(i, lambda: _denoise(i))


def gden(i):
    return _gden.get_or(i, lambda: small_gray(den(i)))


def fetch(s):
    fi = s * SRC_FPS
    a = int(math.floor(fi)); w = fi - a
    a = min(max(a, 0), NF - 1); b = min(a + 1, NF - 1)
    if a == b or w < 0.04:
        return den(a), fi
    if w > 0.96:
        return den(b), fi
    if not same_segment(a, b):
        return (den(b) if w >= 0.5 else den(a)), fi
    fab, fba = _flows.get_or(a, lambda: (flow_full(gden(a), gden(b)), flow_full(gden(b), gden(a))))
    A = sample(den(a), fab, -w)
    B = sample(den(b), fba, -(1 - w))
    mix = A * (1 - w) + B * w
    # where the two warps disagree (occlusions, fast hands) use the nearer frame
    d = cv2.dilate(cv2.GaussianBlur(np.abs(A - B).max(axis=2), (0, 0), 1.5), DIL)
    conf = np.exp(-(d / 10.0) ** 2)[..., None]
    near = den(a) if w < 0.5 else den(b)
    return mix * conf + near * (1 - conf), fi


# ---------------------------------------------------------------- camera
def camera(t):
    """zoom, source centre (cx, cy)."""
    cx, cy = SW / 2, SH / 2 - 12
    if t < T_ON:                                   # slow push-in on the dark cabin
        z = 1.07 + 0.05 * _smooth((t - T0) / (T_ON - T0))
    elif t < T_OFF:                                # punch on the reveal, then slow drift
        k = t - T_ON
        punch = 0.06 * math.exp(-k / 0.25) * (1 - math.exp(-k / 0.035))
        z = 1.09 + 0.05 * _smooth(k / (T_OFF - T_ON)) + punch
        cy = SH / 2 - 30
    else:                                          # creep toward the city lights
        k = (t - T_OFF) / (T_END - T_OFF)
        z = 1.10 + 0.12 * _smooth(k)
        cx = SW / 2 + (1130 - SW / 2) * _smooth(k) * 0.6
        cy = (SH / 2 - 30) + (300 - (SH / 2 - 30)) * _smooth(k)
    return z, cx, cy


CORNERS = np.array([[0, 0, 1], [PW, 0, 1], [0, PH, 1], [PW, PH, 1]], np.float64).T


def warp(img, t, corr):
    z, cx, cy = camera(t)
    k = BASE * z
    hw, hh = PW / 2 / k, PH / 2 / k
    cx = min(max(cx, hw + 2), SW - hw - 2)
    cy = min(max(cy, hh + 2), SH - hh - 2)
    Mc = np.array([[k, 0, PW / 2 - k * cx], [0, k, PH / 2 - k * cy], [0, 0, 1]])
    c0 = np.array([SW / 2, SH / 2])
    for f in (1.0, 0.85, 0.7, 0.55, 0.4, 0.25, 0.1, 0.0):
        tx, ty, ang = corr * f
        ca, sa = math.cos(ang), math.sin(ang)
        R = np.array([[ca, -sa], [sa, ca]])
        C = np.eye(3)
        C[:2, :2] = R
        C[:2, 2] = c0 - R @ c0 + np.array([tx, ty])
        M = Mc @ C
        src_c = np.linalg.inv(M) @ CORNERS
        if (src_c[0].min() >= 1 and src_c[0].max() <= SW - 1 and
                src_c[1].min() >= 1 and src_c[1].max() <= SH - 1):
            break
    return cv2.warpAffine(img, M[:2], (PW, PH), flags=cv2.INTER_LANCZOS4,
                          borderMode=cv2.BORDER_REFLECT)


# ---------------------------------------------------------------- grade
yy, xx = np.mgrid[0:PH, 0:PW].astype(np.float32)
rr = np.sqrt(((xx - PW / 2) / (PW / 2)) ** 2 + ((yy - PH / 2) / (PH / 2)) ** 2 * 0.75)
VIGNETTE = (1 - 0.55 * _smooth((rr - 0.42) / 0.78)).astype(np.float32)[..., None]


def _ca_map(s):
    mx = (xx - PW / 2) * s + PW / 2
    my = (yy - PH / 2) * s + PH / 2
    return mx.astype(np.float32), my.astype(np.float32)


CA_R = _ca_map(1 / 1.0014)
CA_B = _ca_map(1 / 0.9986)
LUMA = np.array([0.2126, 0.7152, 0.0722], np.float32)


def sharpen(x):
    blur = cv2.GaussianBlur(x, (0, 0), 1.3)
    return x + 0.4 * (x - blur)


def grade(x, t):
    """x: float32 RGB 0..255 picture. Returns float 0..1."""
    x = x / 255.0
    if t < T_ON:
        gain = 1.5
    elif t < T_OFF:
        gain = 1.18
    else:
        gain = 1.18 + 0.9 * _smooth((t - T_OFF) / 0.8)   # eyes adjusting to the dark
    x = x * gain
    if T_ON <= t < T_ON + 0.6:                             # flash on the reveal
        x = x * (1 + 1.4 * math.exp(-(t - T_ON) / 0.09))

    x = np.clip(x, 0, None)
    x = x / (1 + 0.35 * x)                      # soft highlight roll-off
    x = np.power(np.clip(x * 1.35, 0, 1), 0.86)  # renormalise + lift mids
    x = x + 0.30 * (x * x * (3 - 2 * x) - x)    # S-curve
    L = (x @ LUMA)[..., None]

    # film-like saturation: muted overall, reds kept, dense in the shadows
    red = np.clip((x[..., :1] - np.maximum(x[..., 1:2], x[..., 2:3])) * 5, 0, 1)
    sat = 0.70 + 0.55 * red
    x = L + (x - L) * sat
    x = x * (1 - 0.10 * red * (1 - L))         # deepen saturated reds a touch

    ws = 1 - _smooth(L / 0.5)
    wh = _smooth((L - 0.45) / 0.55)
    x = x + ws * np.array([-0.032, 0.010, 0.042], np.float32) \
          + wh * np.array([0.032, 0.010, -0.026], np.float32)
    x = 0.012 + x * 0.98                        # black floor
    return np.clip(x, 0, 1)


def bloom(x, t):
    L = x @ LUMA
    thr = 0.55 if t < T_OFF else 0.22
    m = np.clip((L - thr) / (1 - thr), 0, 1) ** 1.4
    small = cv2.resize(x * m[..., None], (PW // 4, PH // 4), interpolation=cv2.INTER_AREA)
    b1 = cv2.resize(cv2.GaussianBlur(small, (0, 0), 5), (PW, PH), interpolation=cv2.INTER_LINEAR)
    b2 = cv2.resize(cv2.GaussianBlur(small, (0, 0), 22), (PW, PH), interpolation=cv2.INTER_LINEAR)
    halo = np.array([1.0, 0.55, 0.38], np.float32)    # red-orange halation fringe
    amt = 1.0 if t < T_OFF else 2.2
    x = x + amt * (0.55 * b1 * halo + 0.45 * b2)
    # anamorphic lens streak: only the hottest points, stretched horizontally, cool blue
    sthr = 0.78 if t < T_OFF else 0.30
    sm = np.clip((L - sthr) / (1 - sthr), 0, 1) ** 2
    ss = cv2.resize(sm, (PW // 4, PH // 4), interpolation=cv2.INTER_AREA)
    streak = cv2.GaussianBlur(ss, (0, 0), sigmaX=55, sigmaY=0.7)
    streak += 0.6 * cv2.GaussianBlur(ss, (0, 0), sigmaX=14, sigmaY=0.5)
    streak = cv2.resize(streak, (PW, PH), interpolation=cv2.INTER_LINEAR)
    s_amt = 3.0 if t < T_OFF else 7.5
    return x + s_amt * streak[..., None] * np.array([0.35, 0.62, 1.0], np.float32)


rng = np.random.default_rng(7)


def finish(x, t):
    r = cv2.remap(x[..., 0], *CA_R, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    b = cv2.remap(x[..., 2], *CA_B, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    x = np.dstack([r, x[..., 1], b]) * VIGNETTE
    g = rng.normal(0, 1, (PH // 2, PW // 2)).astype(np.float32)
    g = cv2.resize(g, (PW, PH), interpolation=cv2.INTER_LINEAR)
    L = x @ LUMA
    x = x + (g * 0.020 * (0.35 + 2.2 * L * (1 - L)))[..., None]
    fade = _smooth((t - T0) / 1.2) * (1 - _smooth((t - (T_END - 1.1)) / 1.1))
    return np.clip(x * fade, 0, 1)


# ---------------------------------------------------------------- main loop
n_out = int(round(TOTAL * FPS))
times = [i / FPS for i in range(n_out)] if ONLY is None else ONLY
if ONLY is None:
    enc = subprocess.Popen([
        "ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb48le",
        "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-vf", "scale=out_color_matrix=bt709:out_range=tv:sws_dither=ed,format=yuv420p",
        "-c:v", "libx264", "-preset", "slow", "-crf", "15", "-profile:v", "high",
        "-tune", "grain", "-x264-params", "log-level=error",
        "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
        "-color_range", "tv", OUT], stdin=subprocess.PIPE)

for i, t in enumerate(times):
    out = np.zeros((H, W, 3), np.float32)
    if T0 <= t < T_END + 0.05:
        img, fi = fetch(src_time(t))
        pic = sharpen(warp(img, t, corr_at(fi)))
        x = finish(bloom(grade(pic, t), t), t)
        out[BAR:BAR + PH] = x
    if ONLY is not None:
        cv2.imwrite(f"{OUT}_{t:.2f}.png",
                    cv2.cvtColor((np.clip(out, 0, 1) * 255).astype(np.uint8), cv2.COLOR_RGB2BGR))
    else:
        enc.stdin.write((np.clip(out, 0, 1) * 65535).astype(np.uint16).tobytes())
        if i % 24 == 0:
            print(f"{t:5.2f}s / {TOTAL:.2f}s", flush=True)

if ONLY is not None:
    sys.exit(0)
enc.stdin.close()
enc.wait()
print("done", OUT)
