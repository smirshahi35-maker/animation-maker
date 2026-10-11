#!/usr/bin/env python3
"""Prepare the GPT Image 2.5 picks for the composition.

- crumpled cutout (birefnet) -> two separate balls (left = invoice, right = video file)
- bin cutout -> cropped to the object, opening geometry printed for s1's dive
- photos -> resized JPEGs at the size they are shown
- contact sheet -> nine tiles for the 500-project wall
Run: python3 tools/prep_images.py
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
AI = ROOT / "assets/ai"
SRC = AI / "src"
OUT = AI / "web"
OUT.mkdir(exist_ok=True)
geo = {}
COOL = {"bts", "latte", "customer"}


def bbox(alpha, thr=24):
    ys, xs = np.nonzero(alpha > thr)
    return xs.min(), ys.min(), xs.max() + 1, ys.max() + 1


def save_cut(img, name, max_side):
    img = img.copy()
    img.thumbnail((max_side, max_side), Image.LANCZOS)
    img.save(OUT / f"{name}.png", optimize=True)
    return img.size


def balls():
    im = Image.open(SRC / "crumpled-cut.png").convert("RGBA")
    a = np.array(im)[:, :, 3]
    w = im.width
    for name, (x0, x1) in {"ball-invoice": (0, w // 2), "ball-video": (w // 2, w)}.items():
        half = np.zeros_like(a)
        half[:, x0:x1] = a[:, x0:x1]
        l, t, r, b = bbox(half)
        pad = 12
        crop = im.crop((max(0, l - pad), max(0, t - pad), min(w, r + pad), min(im.height, b + pad)))
        geo[name] = {"size": save_cut(crop, name, 560)}


def bin_():
    im = Image.open(SRC / "bin-cut.png").convert("RGBA")
    arr = np.array(im)
    l, t, r, b = bbox(arr[:, :, 3])
    crop = im.crop((l, t, r, b))
    carr = np.array(crop).astype(np.float32)
    luma = 0.299 * carr[:, :, 0] + 0.587 * carr[:, :, 1] + 0.114 * carr[:, :, 2]
    h = crop.height
    # The open top: dark interior pixels in the upper part of the object.
    top = (luma < 70) & (carr[:, :, 3] > 200)
    top[int(h * 0.45):, :] = False
    ys, xs = np.nonzero(top)
    cx, cy = xs.mean(), ys.mean()
    ow, oh = np.percentile(xs, 98) - np.percentile(xs, 2), np.percentile(ys, 98) - np.percentile(ys, 2)
    size = save_cut(crop, "bin", 1000)
    s = size[0] / crop.width
    geo["bin"] = {"size": size, "opening_center": [round(cx * s, 1), round(cy * s, 1)],
                  "opening_size": [round(ow * s, 1), round(oh * s, 1)]}


def photo(name, w, h=None):
    p = next(AI.glob(f"{name}.*"))
    im = Image.open(p).convert("RGB")
    if h:
        # cover-crop to w x h
        r = max(w / im.width, h / im.height)
        im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
        x = (im.width - w) // 2
        y = (im.height - h) // 2
        im = im.crop((x, y, x + w, y + h))
    else:
        im.thumbnail((w, w * 4), Image.LANCZOS)
    if name in COOL:
        # one slightly cooler grade for the café set so the white cups read white
        r, g, b = im.split()
        r = r.point(lambda v: int(v * 0.955))
        b = b.point(lambda v: min(255, int(v * 1.035 + 2)))
        im = Image.merge("RGB", (r, g, b))
    im.save(OUT / f"{name}.jpg", quality=88, optimize=True, progressive=True)
    geo[name] = {"size": im.size}


def contact_sheet():
    p = next(AI.glob("contact-sheet.*"))
    im = Image.open(p).convert("RGB")
    a = np.array(im).astype(np.float32).mean(axis=2)
    # gutters are near-white full rows/columns
    cols = np.nonzero(a.mean(axis=0) > 238)[0]
    rows = np.nonzero(a.mean(axis=1) > 238)[0]

    def cuts(idx, n):
        # group gutter indices into runs; return cell spans between runs
        runs, start = [], None
        for i, v in enumerate(idx):
            if start is None:
                start = v
            if i == len(idx) - 1 or idx[i + 1] != v + 1:
                runs.append((start, v))
                start = None
        edges = [0]
        for s, e in runs:
            edges += [s, e + 1]
        edges.append(n)
        spans = [(edges[i], edges[i + 1]) for i in range(0, len(edges), 2) if edges[i + 1] - edges[i] > n * 0.15]
        return spans

    xs, ys = cuts(cols, im.width), cuts(rows, im.height)
    geo["contact-sheet"] = {"cols": xs, "rows": ys}
    k = 0
    for (y0, y1) in ys:
        for (x0, x1) in xs:
            k += 1
            tile = im.crop((x0 + 4, y0 + 4, x1 - 4, y1 - 4))
            tile.thumbnail((360, 640), Image.LANCZOS)
            tile.save(OUT / f"tile-{k}.jpg", quality=86, optimize=True)


if __name__ == "__main__":
    import sys
    which = sys.argv[1:] or ["balls", "bin", "photos", "sheet"]
    if "balls" in which:
        balls()
    if "bin" in which:
        bin_()
    if "photos" in which:
        for n, w, h in [("cafe-trend", 600, 1300), ("bts", 1280, 720), ("latte", 720, 900),
                        ("customer", 720, 900), ("desk", 1280, 720)]:
            if list(AI.glob(f"{n}.*")):
                photo(n, w, h)
    if "sheet" in which and list(AI.glob("contact-sheet.*")):
        contact_sheet()
    old = json.load(open(OUT / "geometry.json")) if (OUT / "geometry.json").exists() else {}
    old.update(geo)
    json.dump(old, open(OUT / "geometry.json", "w"), indent=1, default=int)
    print(json.dumps(geo, indent=1, default=int))
