# Remove the dark-green disc and grey surround from the client logo; keep the gold line art, the
# emerald facets and both text lines.
#  - Enclosed areas of the mark (gems, house front, window) keep their original colours; letter counters
#    (R, A, O ...) are disc and become transparent.
#  - Gold edges are un-mixed against the disc using the local gold colour, so thin letters keep no dark fringe.
import sys, numpy as np
from PIL import Image
from scipy import ndimage

src, out = sys.argv[1], sys.argv[2]
im = Image.open(src).convert("RGB")
rgb = np.asarray(im).astype(float) / 255
hsv = np.asarray(im.convert("HSV")).astype(float) / 255
h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
bg = np.array([2, 36, 21]) / 255.0                                   # disc colour

gold_core = (v > 0.55) & (s > 0.25) & (h > 0.07) & (h < 0.2)
gold_any = (v > 0.3) & (h > 0.06) & (h < 0.22) & (s > 0.2)

# interiors of the mark: holes in the gold outline above the text
outline = ndimage.binary_closing(gold_any, iterations=2)
holes = ndimage.binary_fill_holes(outline) & ~outline
lab, n = ndimage.label(holes)
gems = np.zeros_like(holes)
for i in range(1, n + 1):
    region = lab == i
    if region.sum() > 20 and np.where(region)[0].max() < 545:   # buildings and house (above the text); letter counters stay clear
        gems |= region
top = np.zeros_like(holes); top[:545] = True                  # the mark sits above the text
gems = ndimage.binary_fill_holes((gems | outline) & top) & ~outline   # also the thin gaps inside the window
gems = ndimage.binary_dilation(gems, iterations=1)

# local gold colour from confident gold pixels (normalized blur)
w = ndimage.gaussian_filter(gold_core.astype(float), 5) + 1e-6
gold_col = np.dstack([ndimage.gaussian_filter(rgb[..., c] * gold_core, 5) / w for c in range(3)])
fallback = np.array([0.86, 0.66, 0.26])
gold_col = np.where((w > 0.02)[..., None], gold_col, fallback)

# alpha for gold: projection of the pixel onto the disc→gold segment
d = gold_col - bg
a_gold = np.clip(((rgb - bg) * d).sum(-1) / np.maximum((d * d).sum(-1), 1e-4), 0, 1)
a_gold[(s < 0.3) & (v < 0.4)] = 0                                   # grey surround outside the disc
near_gold = ndimage.binary_dilation(gold_any, iterations=2)
a_gold = a_gold * near_gold

# the whole mark silhouette (gems, house, window, inner gold lines) is opaque; only its outer rim is un-mixed
mark = ndimage.binary_fill_holes((gems | outline) & top)
gems = gems | ndimage.binary_erosion(mark, iterations=2)
alpha = np.where(gems, 1.0, a_gold)
alpha[alpha < 0.06] = 0
color = np.where(gems[..., None], rgb, np.where((a_gold > 0.85)[..., None], rgb, gold_col))

rgba = np.dstack([np.clip(color, 0, 1), alpha])
img = Image.fromarray((rgba * 255).astype(np.uint8), "RGBA")
img = img.crop(img.getbbox())
img.save(out)
print(out, img.size)
