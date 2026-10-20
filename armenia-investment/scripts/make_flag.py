# Waving Armenian flag (red / blue / apricot) as a transparent PNG, drawn procedurally:
# sine-wave displacement plus light and shadow along the folds.
import sys, numpy as np
from PIL import Image, ImageFilter
out = sys.argv[1]
W, H = 900, 450                      # flag cloth 2:1
red, blue, orange = np.array([217, 0, 18]), np.array([0, 51, 160]), np.array([242, 168, 0])
PAD = 60
CW, CH = W + 2 * PAD, H + 2 * PAD
yy, xx = np.mgrid[0:CH, 0:CW].astype(float)
u = (xx - PAD) / W                                  # cloth coords before warping
amp = 22 * (0.35 + 0.65 * np.clip(u, 0, 1))          # waves grow away from the hoist
phase = 2 * np.pi * (u * 1.55) + 0.6
v = (yy - PAD - amp * np.sin(phase)) / H             # inverse vertical displacement
u2 = u + 0.012 * np.sin(2 * np.pi * v * 1.2)         # slight horizontal ripple
inside = (u2 >= 0) & (u2 <= 1) & (v >= 0) & (v <= 1)
col = np.where((v < 1 / 3)[..., None], red, np.where((v < 2 / 3)[..., None], blue, orange)).astype(float)
shade = 1 + 0.28 * np.cos(phase + 0.35) * (0.4 + 0.6 * np.clip(u, 0, 1))
fine = 1 + 0.05 * np.sin(2 * np.pi * (u * 6 + v * 0.8))
rgb = np.clip(col * (shade * fine)[..., None], 0, 255)
hl = np.clip(np.cos(phase + 0.35), 0, 1) ** 6 * 70 * np.clip(u, 0, 1)   # glossy highlight on the crests
rgb = np.clip(rgb + hl[..., None], 0, 255)
alpha = inside.astype(float)
a = Image.fromarray((alpha * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8))
img = Image.fromarray(rgb.astype(np.uint8), "RGB").convert("RGBA"); img.putalpha(a)
img.crop(img.getbbox()).save(out)
print(out)
