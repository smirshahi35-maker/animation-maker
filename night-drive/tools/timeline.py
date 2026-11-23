"""Shared edit timeline: maps output time -> source time with speed ramps."""
import os
import numpy as np

# raw phone clip (not committed): 2336x1080 HEVC, 30 fps, 13.97 s
SRC = os.environ.get("NIGHT_DRIVE_SRC", "night-drive/source.mp4")
FPS = 24
SRC_FPS = 30.0
SRC_FRAMES = 419

# Source events (seconds)
S_ON = 4.866    # headlights switch on (first lit frame 146)
S_OFF = 11.90   # headlights off, city lights revealed
S_END = 13.93   # last source frame

T0 = 0.6        # black lead-in before picture
SLOW_HIT = 0.32 # speed right after the reveal
TAIL = 0.9      # black tail after picture ends


def _smooth(x):
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3 - 2 * x)


def build(dt=1.0 / 2400):
    """Integrate the speed curve. Returns (t_grid, s_grid, events)."""
    ts, ss = [], []
    t, s = 0.0, 0.0
    t_on = t_off = t_end = None
    while True:
        if t < T0:
            v = 0.0
        elif s < S_ON:
            v = 1.0
        else:
            if t_on is None:
                t_on = t
            k = t - t_on
            if s < S_OFF - 0.18:
                # impact slow-mo, then ramp back to real time
                v = SLOW_HIT + (1 - SLOW_HIT) * _smooth((k - 0.85) / 0.75)
            else:
                # ease down to half speed into the lights-off moment
                if t_off is None and s >= S_OFF:
                    t_off = t
                v = 1.0 - 0.5 * _smooth((s - (S_OFF - 0.18)) / 0.3)
        ts.append(t)
        ss.append(s)
        if s >= S_END:
            t_end = t
            break
        s += v * dt
        t += dt
    return np.array(ts), np.array(ss), dict(t_on=t_on, t_off=t_off, t_end=t_end,
                                            total=t_end + TAIL)


T_GRID, S_GRID, EV = build()
T_ON, T_OFF, T_END, TOTAL = EV["t_on"], EV["t_off"], EV["t_end"], EV["total"]


def src_time(t):
    return float(np.interp(t, T_GRID, S_GRID))


if __name__ == "__main__":
    print({k: round(v, 3) for k, v in EV.items()})
