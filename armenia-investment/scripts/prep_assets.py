import sys, numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

root = sys.argv[1]
A = f"{root}/styleframes/assets"

def cutout(src, box, out, pad=16):
    im = Image.open(src).convert("RGB").crop(box)
    hsv = np.asarray(im.convert("HSV")).astype(float) / 255
    rgb = np.asarray(im).astype(float) / 255
    s, v = hsv[..., 1], hsv[..., 2]
    mask = (s > 0.6) & (v > 0.55)            # bright orange flesh; shadows are darker, the pit is filled as a hole
    mask = ndimage.binary_opening(mask, iterations=3)
    lab, n = ndimage.label(mask)
    if n > 1:
        sizes = ndimage.sum(mask, lab, range(1, n + 1))
        mask = lab == (np.argmax(sizes) + 1)
    mask = ndimage.binary_fill_holes(ndimage.binary_closing(mask, iterations=6))
    soft = Image.fromarray((mask * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))
    # white sticker border
    border = ndimage.binary_dilation(mask, iterations=pad)
    bsoft = Image.fromarray((border * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.5))
    W, H = im.size
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    white = Image.new("RGBA", (W, H), (255, 253, 248, 255))
    canvas.paste(white, (0, 0), bsoft)
    fruit = im.convert("RGBA"); fruit.putalpha(soft)
    canvas = Image.alpha_composite(canvas, fruit)
    bb = canvas.getbbox(); canvas.crop(bb).save(out)
    print(out, canvas.crop(bb).size)

src = f"{root}/footage/apricot_27025430/apricot.jpg"
cutout(src, (330, 828, 960, 1420), f"{A}/apricot_pit.png")
cutout(src, (330, 260, 940, 845), f"{A}/apricot_half.png")

def pixelate(src, out, block=34):
    im = Image.open(src).convert("RGB")
    w, h = im.size
    im.resize((max(1, w // block), max(1, h // block)), Image.NEAREST).resize((w, h), Image.NEAREST).save(out, quality=92)
    print(out)

for n in ["cascade_front", "cascade_top", "grapes"]:
    pixelate(f"{A}/{n}.jpg", f"{A}/{n}_px.jpg")
