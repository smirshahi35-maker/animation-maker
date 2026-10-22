"""Cut the IRAM CO. logo out of the earlier reel cover (deliverables/armenia-investment-cover.png).

The original logo file is not in git; the cover shows it at 360 px on a plain green gradient.
Gold lines and lettering are keyed by colour; the emerald shapes are the regions the gold
outlines enclose (everything a flood fill from the crop border cannot reach).

usage: python3 -I logo_from_cover.py <cover.png> <out.png>
"""
import sys
from collections import deque

import numpy as np
from PIL import Image, ImageFilter

src, out = sys.argv[1], sys.argv[2]
im = np.array(Image.open(src).convert("RGB").crop((340, 350, 740, 800))).astype(float)
r, g, b = im[..., 0], im[..., 1], im[..., 2]

# gold: warm and bright (bg is ~ (30, 75, 55), emerald ~ (20, 120, 80))
gold_soft = np.clip((r - b - 35) / 70, 0, 1) * np.clip((r - 60) / 60, 0, 1)
gold = gold_soft > 0.35

# seal hairline gaps in the outlines, then flood the outside from the border
sealed = np.array(Image.fromarray((gold * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(5))) > 0
h, w = sealed.shape
outside = np.zeros_like(sealed)
q = deque((y, x) for y in range(h) for x in (0, w - 1)) + deque((y, x) for x in range(w) for y in (0, h - 1))
while q:
    y, x = q.popleft()
    if outside[y, x] or sealed[y, x]:
        continue
    outside[y, x] = True
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        ny, nx = y + dy, x + dx
        if 0 <= ny < h and 0 <= nx < w and not outside[ny, nx] and not sealed[ny, nx]:
            q.append((ny, nx))

# everything the flood cannot reach is the icon (outlines, emerald faces, the window); erode by the
# 2 px the seal added so no background ring is kept. Only above the lettering (rows < ICON_BOTTOM),
# or the counters of R, A and O would be filled too.
ICON_BOTTOM = 312
solid = ~outside
solid[ICON_BOTTOM:] = False
solid = np.array(Image.fromarray((solid * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(5))) > 0
alpha = np.maximum(gold_soft, solid * 1.0)
alpha = np.array(Image.fromarray((alpha * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6))) / 255.0

rgba = np.dstack([im, alpha * 255]).astype(np.uint8)
img = Image.fromarray(rgba, "RGBA")
img = img.crop(img.getbbox())
img.save(out)
print(out, img.size)
