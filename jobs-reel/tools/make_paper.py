"""Seeded paper backdrop + film-grain tile for the reel (deterministic)."""
import os
import numpy as np
from PIL import Image, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'assets/paper')
rng = np.random.default_rng(1985)
W, H = 1080, 1920

def noise(scale):
    small = rng.random((H // scale + 2, W // scale + 2)).astype(np.float32)
    im = Image.fromarray((small * 255).astype(np.uint8)).resize((W + 2 * scale, H + 2 * scale), Image.BICUBIC)
    return np.asarray(im, dtype=np.float32)[scale:scale + H, scale:scale + W] / 255.0 - 0.5

yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
d = np.sqrt(((xx - W * 0.5) / (W * 0.62)) ** 2 + ((yy - H * 0.46) / (H * 0.58)) ** 2)
t = np.clip(d, 0, 1.35) / 1.35
center = np.array([0xdb, 0xd1, 0xc0], np.float32)
edge = np.array([0xa8, 0x9c, 0x89], np.float32)
img = center * (1 - t[..., None] ** 1.6) + edge * (t[..., None] ** 1.6)
tex = noise(220) * 0.05 + noise(60) * 0.03 + noise(12) * 0.025 + noise(3) * 0.03
fib = np.asarray(Image.fromarray(((rng.random((H, W)) > 0.9965) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6)), np.float32) / 255.0
img = img * (1 + tex[..., None]) - fib[..., None] * 18
Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).save(os.path.join(OUT, 'paper.jpg'), quality=92)

G = 512
g = rng.random((G, G)).astype(np.float32)
dark = (g < 0.035).astype(np.float32) * rng.uniform(0.18, 0.45, (G, G)).astype(np.float32)
light = (g > 0.975).astype(np.float32) * rng.uniform(0.15, 0.35, (G, G)).astype(np.float32)
rgba = np.zeros((G, G, 4), np.float32)
rgba[..., :3] = np.where(dark[..., None] > 0, [40, 30, 20], [255, 248, 235])
rgba[..., 3] = (dark + light) * 255
Image.fromarray(rgba.astype(np.uint8), 'RGBA').save(os.path.join(OUT, 'grain.png'), optimize=True)
print('paper + grain written')
