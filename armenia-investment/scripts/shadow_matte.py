# Turn a real "leaf shadow on a white wall" frame into a transparent shadow layer.
import sys, numpy as np
from PIL import Image, ImageFilter
src, out = sys.argv[1], sys.argv[2]
L = np.asarray(Image.open(src).convert("L")).astype(float)
hi, lo = np.percentile(L, 97), np.percentile(L, 3)
a = np.clip((hi - L) / max(1.0, hi - lo), 0, 1) ** 0.85
alpha = Image.fromarray((a * 235).astype(np.uint8)).filter(ImageFilter.GaussianBlur(10))
rgba = Image.new("RGBA", alpha.size, (48, 44, 40, 0)); rgba.putalpha(alpha)
rgba.save(out)
print(out, rgba.size)
