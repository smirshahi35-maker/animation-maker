"""Cinematic grade + camera + titles. Writes graded 24fps video (no audio)."""
import subprocess, sys, math
import numpy as np
import cv2
from timeline import (SRC, FPS, SRC_FPS, SRC_FRAMES, T0, T_ON, T_OFF, T_END, TOTAL,
                      S_OFF, src_time, _smooth)

TEXT_DIR = sys.argv[1]
OUT = sys.argv[2]
ONLY = [float(x) for x in sys.argv[3].split(",")] if len(sys.argv) > 3 else None

SW, SH = 2336, 1080
W, H = 1920, 1080
PW, PH = 1920, 804             # 2.39:1 picture
BAR = (H - PH) // 2
BASE = PW / SW                 # fit width
EVENT_FRAMES = {146, 357}      # never blend across these (light switches)

# ---------------------------------------------------------------- decode
print("decoding source...", flush=True)
cmd = ["ffmpeg", "-v", "error", "-i", SRC, "-vf",
       "hqdn3d=1.2:1.2:5:5,scale=in_color_matrix=bt709:in_range=tv:out_range=pc,format=rgb24",
       "-f", "rawvideo", "-"]
raw = subprocess.run(cmd, capture_output=True, check=True).stdout
frames = np.frombuffer(raw, np.uint8).reshape(-1, SH, SW, 3)
NF = len(frames)
print("frames:", NF, flush=True)


def fetch(s):
    fi = s * SRC_FPS
    a = int(math.floor(fi)); b = a + 1; w = fi - a
    a = min(max(a, 0), NF - 1); b = min(max(b, 0), NF - 1)
    if a == b or w < 0.08:
        return frames[a].astype(np.float32)
    if w > 0.92:
        return frames[b].astype(np.float32)
    if any(a < e <= b for e in EVENT_FRAMES):   # hard light change: no ghosting
        return frames[b if w >= 0.5 else a].astype(np.float32)
    return frames[a].astype(np.float32) * (1 - w) + frames[b].astype(np.float32) * w


# ---------------------------------------------------------------- camera
rng = np.random.default_rng(7)
_noise_t = np.linspace(0, 40, 4000)
_nx = np.interp(np.linspace(0, 40, 4000), np.linspace(0, 40, 400), rng.normal(size=400))
_ny = np.interp(np.linspace(0, 40, 4000), np.linspace(0, 40, 400), rng.normal(size=400))
_nr = np.interp(np.linspace(0, 40, 4000), np.linspace(0, 40, 400), rng.normal(size=400))


def shake(t):
    """Decaying impact shake (output px, degrees)."""
    dx = dy = rot = 0.0
    for t_hit, amp, tau in ((T_ON, 16.0, 0.30), (T_OFF, 7.0, 0.35)):
        k = t - t_hit
        if 0 <= k < 2.0:
            e = amp * math.exp(-k / tau)
            ph = (t * 10.0) % 40
            dx += e * np.interp(ph, _noise_t, _nx)
            dy += e * np.interp(ph, _noise_t, _ny)
            rot += e * 0.022 * np.interp(ph, _noise_t, _nr)
    return dx, dy, rot


def camera(t):
    """zoom, source centre (cx, cy)."""
    cx, cy = SW / 2, SH / 2 - 12
    if t < T_ON:                                   # slow push-in on the dark cabin
        z = 1.035 + 0.06 * _smooth((t - T0) / (T_ON - T0))
    elif t < T_OFF:                                # punch on the reveal, then slow drift
        k = t - T_ON
        punch = 0.07 * math.exp(-k / 0.22) * (1 - math.exp(-k / 0.03))
        z = 1.06 + 0.05 * _smooth(k / (T_OFF - T_ON)) + punch
        cy = SH / 2 - 30
    else:                                          # creep toward the city lights
        k = (t - T_OFF) / (T_END - T_OFF)
        z = 1.08 + 0.12 * _smooth(k)
        cx = SW / 2 + (1130 - SW / 2) * _smooth(k) * 0.6
        cy = (SH / 2 - 30) + (300 - (SH / 2 - 30)) * _smooth(k)
    return z, cx, cy


def warp(img, t):
    z, cx, cy = camera(t)
    dx, dy, rot = shake(t)
    k = BASE * z
    hw, hh = PW / 2 / k, PH / 2 / k               # half-size in source px
    m = 6 / k                                     # margin for rotation
    cx = min(max(cx - dx / k, hw + m), SW - hw - m)
    cy = min(max(cy - dy / k, hh + m), SH - hh - m)
    M = cv2.getRotationMatrix2D((cx, cy), rot, k)
    M[0, 2] += PW / 2 - cx
    M[1, 2] += PH / 2 - cy
    return cv2.warpAffine(img, M, (PW, PH), flags=cv2.INTER_LINEAR,
                          borderMode=cv2.BORDER_REFLECT)


# ---------------------------------------------------------------- grade
yy, xx = np.mgrid[0:PH, 0:PW].astype(np.float32)
rr = np.sqrt(((xx - PW / 2) / (PW / 2)) ** 2 + ((yy - PH / 2) / (PH / 2)) ** 2 * 0.75)
VIGNETTE = (1 - 0.5 * _smooth((rr - 0.45) / 0.75)).astype(np.float32)[..., None]

# chromatic aberration maps (R slightly larger, B slightly smaller, toward edges)
def _ca_map(s):
    mx = (xx - PW / 2) * s + PW / 2
    my = (yy - PH / 2) * s + PH / 2
    return mx.astype(np.float32), my.astype(np.float32)
CA_R = _ca_map(1 / 1.0016)
CA_B = _ca_map(1 / 0.9984)

LUMA = np.array([0.2126, 0.7152, 0.0722], np.float32)


def grade(x, t):
    """x: float32 RGB 0..255 picture. Returns float 0..1."""
    x = x / 255.0
    # act-dependent exposure
    if t < T_ON:
        gain = 1.45
    elif t < T_OFF:
        gain = 1.18
    else:
        k = (t - T_OFF)
        gain = 1.18 + 0.9 * _smooth(k / 0.8)     # eyes adjusting to the dark
    x = x * gain

    # flash on the reveal
    if T_ON <= t < T_ON + 0.6:
        f = math.exp(-(t - T_ON) / 0.09)
        x = x * (1 + 1.4 * f)

    # tone: lift mids, gentle S, matte blacks, soft shoulder
    x = np.clip(x, 0, None)
    x = x / (1 + 0.35 * x)                      # soft highlight roll-off
    x = np.power(x / (1 / 1.35), 0.86)          # renormalise + lift mids
    x = np.clip(x, 0, 1)
    x = x + 0.22 * (x * x * (3 - 2 * x) - x)    # S-curve
    L = (x @ LUMA)[..., None]

    # saturation: pull everything back, keep reds alive
    mx = x.max(axis=2, keepdims=True)
    red = np.clip((x[..., :1] - np.maximum(x[..., 1:2], x[..., 2:3])) * 5, 0, 1)
    sat = 0.72 + 0.55 * red
    x = L + (x - L) * sat

    # split tone: teal shadows, faintly warm highlights
    ws = 1 - _smooth(L / 0.5)
    wh = _smooth((L - 0.45) / 0.55)
    x = x + ws * np.array([-0.030, 0.010, 0.040], np.float32) \
          + wh * np.array([0.030, 0.008, -0.025], np.float32)
    x = 0.018 + x * 0.975                        # matte black floor
    return np.clip(x, 0, 1)


def bloom(x, t):
    """Halation + bloom on highlights (headlights, dash, city lights)."""
    L = x @ LUMA
    thr = 0.55 if t < T_OFF else 0.22
    m = np.clip((L - thr) / (1 - thr), 0, 1) ** 1.4
    src = x * m[..., None]
    small = cv2.resize(src, (PW // 4, PH // 4), interpolation=cv2.INTER_AREA)
    b1 = cv2.GaussianBlur(small, (0, 0), 5)
    b2 = cv2.GaussianBlur(small, (0, 0), 22)
    b1 = cv2.resize(b1, (PW, PH), interpolation=cv2.INTER_LINEAR)
    b2 = cv2.resize(b2, (PW, PH), interpolation=cv2.INTER_LINEAR)
    halo = np.array([1.0, 0.55, 0.38], np.float32)    # red-orange halation fringe
    amt = 1.0 if t < T_OFF else 2.2
    x = x + amt * (0.55 * b1 * halo + 0.45 * b2)
    return x


def finish(x, t):
    # chromatic aberration
    r = cv2.remap(x[..., 0], *CA_R, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    b = cv2.remap(x[..., 2], *CA_B, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    x = np.dstack([r, x[..., 1], b])
    x = x * VIGNETTE
    # film grain (soft, luma-weighted)
    g = rng.normal(0, 1, (PH // 2, PW // 2)).astype(np.float32)
    g = cv2.resize(g, (PW, PH), interpolation=cv2.INTER_LINEAR)
    L = x @ LUMA
    gw = 0.028 * (0.35 + 2.2 * L * (1 - L))
    x = x + (g * gw)[..., None]
    # fades
    fade = _smooth((t - T0) / 1.7) * (1 - _smooth((t - (T_END - 1.1)) / 1.1))
    return np.clip(x * fade, 0, 1)


# ---------------------------------------------------------------- titles
def load_card(name):
    im = cv2.imread(f"{TEXT_DIR}/{name}.png", cv2.IMREAD_UNCHANGED).astype(np.float32) / 255.0
    rgb = cv2.cvtColor(im[..., :3], cv2.COLOR_BGR2RGB)
    a = im[..., 3:4]
    ys, xs = np.where(a[..., 0] > 0.004)
    pad = 60
    y0, y1 = max(ys.min() - pad, 0), min(ys.max() + pad, H)
    x0, x1 = max(xs.min() - pad, 0), min(xs.max() + pad, W)
    return dict(rgb=rgb[y0:y1, x0:x1] * a[y0:y1, x0:x1], a=a[y0:y1, x0:x1], box=(y0, y1, x0, x1))

CARDS = {n: load_card(n) for n in ("opening", "title_fa", "title_en", "end")}

# soft dark scrim behind the title block so thin type reads over the lit road
_b1, _b2 = CARDS["title_fa"]["box"], CARDS["title_en"]["box"]
_cy = (min(_b1[0], _b2[0]) + max(_b1[1], _b2[1])) / 2
_cx = (min(_b1[2], _b2[2]) + max(_b1[3], _b2[3])) / 2
_ry = (max(_b1[1], _b2[1]) - min(_b1[0], _b2[0])) * 0.62
_rx = (max(_b1[3], _b2[3]) - min(_b1[2], _b2[2])) * 0.80
_Y, _X = np.mgrid[0:H, 0:W].astype(np.float32)
_d = np.sqrt(((_X - _cx) / _rx) ** 2 + ((_Y - _cy) / _ry) ** 2)
SCRIM = (1 - _smooth((_d - 0.25) / 0.95)).astype(np.float32)[..., None]


def scrim(frame, t):
    a, _, _ = card_state(t, T_ON + 0.15, T_ON + 3.4, 0.6, 0.8)
    if a > 0.002:
        frame *= 1 - 0.55 * a * SCRIM
    return frame


def card_state(t, t_in, t_out, fin=0.7, fout=0.6):
    """opacity, blur sigma, scale"""
    if t < t_in or t > t_out + fout:
        return 0, 0, 1
    a_in = _smooth((t - t_in) / fin)
    a_out = 1 - _smooth((t - t_out) / fout)
    a = min(a_in, a_out)
    blur = 10 * (1 - a_in) + 8 * (1 - a_out)
    scale = 1.035 - 0.035 * a_in + 0.012 * _smooth((t - t_in) / (t_out + fout - t_in))
    return a, blur, scale


def overlay(frame, name, t, t_in, t_out, fin=0.7, fout=0.6):
    a, blur, scale = card_state(t, t_in, t_out, fin, fout)
    if a <= 0.002:
        return frame
    c = CARDS[name]
    y0, y1, x0, x1 = c["box"]
    rgb, al = c["rgb"], c["a"]
    h, w = al.shape[:2]
    if abs(scale - 1) > 1e-3:
        M = cv2.getRotationMatrix2D((w / 2, h / 2), 0, scale)
        rgb = cv2.warpAffine(rgb, M, (w, h), flags=cv2.INTER_LINEAR)
        al = cv2.warpAffine(al, M, (w, h), flags=cv2.INTER_LINEAR)[..., None]
    if blur > 0.3:
        rgb = cv2.GaussianBlur(rgb, (0, 0), blur)
        al = cv2.GaussianBlur(al, (0, 0), blur)[..., None]
    roi = frame[y0:y1, x0:x1]
    frame[y0:y1, x0:x1] = roi * (1 - al * a) + rgb * a
    return frame


# ---------------------------------------------------------------- main loop
n_out = int(round(TOTAL * FPS))
times = [i / FPS for i in range(n_out)] if ONLY is None else ONLY
if ONLY is None:
    enc = subprocess.Popen([
        "ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb48le",
        "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-vf", "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p10le",
        "-c:v", "libx265", "-preset", "medium", "-crf", "14", "-tag:v", "hvc1",
        "-x265-params", "log-level=error",
        "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
        "-color_range", "tv", OUT], stdin=subprocess.PIPE)

for i, t in enumerate(times):
    out = np.zeros((H, W, 3), np.float32)
    if T0 <= t < T_END + 0.05:
        s = src_time(t)
        img = warp(fetch(s), t)
        x = grade(img, t)
        x = bloom(x, t)
        x = finish(x, t)
        out[BAR:BAR + PH] = x
    # titles
    out = scrim(out, t)
    out = overlay(out, "opening", t, 0.25, 2.05, fin=0.8, fout=0.6)
    out = overlay(out, "title_fa", t, T_ON + 0.30, T_ON + 3.4, fin=0.75, fout=0.7)
    out = overlay(out, "title_en", t, T_ON + 0.75, T_ON + 3.4, fin=0.75, fout=0.7)
    out = overlay(out, "end", t, T_OFF + 1.0, T_END - 0.9, fin=1.0, fout=0.8)
    out[:BAR] = 0
    out[BAR + PH:] = 0
    if ONLY is not None:
        cv2.imwrite(f"{OUT}_{t:.2f}.jpg",
                    cv2.cvtColor((np.clip(out, 0, 1) * 255).astype(np.uint8), cv2.COLOR_RGB2BGR),
                    [cv2.IMWRITE_JPEG_QUALITY, 92])
    else:
        # dither into 16 bit to avoid banding in the dark gradients
        enc.stdin.write((np.clip(out, 0, 1) * 65535).astype(np.uint16).tobytes())
        if i % 24 == 0:
            print(f"{t:5.2f}s / {TOTAL:.2f}s", flush=True)

if ONLY is None:
    enc.stdin.close()
    enc.wait()
    print("done", OUT)
