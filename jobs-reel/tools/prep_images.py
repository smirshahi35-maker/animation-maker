"""Prepare GPT Image sketches for the paper look.

For every assets/ai/src/sNN-*.png:
  assets/ai/sNN.webp        graphite on transparent ("colour to alpha" against the paper), so it sits on the
                            shared paper like a multiply without needing a blend mode
  assets/ai/sNN-lines.webp  pencil contour pass, same treatment, for the "sketch first, shade second" reveal
For portraits listed in CUTOUT, also:
  assets/ai/sNN-cut.webp   background removed, tinted to the panel paper so it can sit in front of type
Placeholders: storyboard panels stand in for images that are not generated yet (assets/ai/sNN.webp + .placeholder).
"""
import glob, os, subprocess, sys
import numpy as np
from PIL import Image, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AI = os.path.join(ROOT, 'assets/ai')
CUTOUT = {'s03', 's07'}
PANEL = np.array([0xe9, 0xe1, 0xd3], dtype=np.float32) / 255.0  # frame panel paper

def paper_color(a):
    h = a.shape[0]
    top = a[int(h * 0.02):int(h * 0.14), int(a.shape[1] * 0.1):int(a.shape[1] * 0.9)].reshape(-1, 3)
    return np.percentile(top, 60, axis=0)

def normalise(a):
    p = paper_color(a)
    out = np.clip(a / p, 0, 1)
    # soften residual paper tone so it disappears under multiply
    lum = out.mean(axis=2, keepdims=True)
    lift = np.clip((lum - 0.90) / 0.08, 0, 1)
    return out * (1 - lift) + lift, p

def to_alpha(n):
    """Colour-to-alpha against white: exact for grey graphite, i.e. equal to a multiply on any paper."""
    a = np.clip((1 - n).max(axis=2, keepdims=True), 0, 1)
    c = 1 - (1 - n) / np.maximum(a, 1e-4)
    out = np.dstack([np.clip(c, 0, 1), a])
    return Image.fromarray((out * 255).round().astype(np.uint8), 'RGBA')

def save_webp(img, path, q):
    img.save(path, 'WEBP', quality=q, alpha_quality=90, method=6)

def lines(a):
    g = Image.fromarray((a.mean(axis=2) * 255).astype(np.uint8))
    small = np.asarray(g.filter(ImageFilter.GaussianBlur(1.2)), dtype=np.float32)
    big = np.asarray(g.filter(ImageFilter.GaussianBlur(7)), dtype=np.float32)
    dog = np.clip((big - small) / 40.0, 0, 1) ** 0.8          # dark strokes
    tone = np.clip(1 - np.asarray(g, dtype=np.float32) / 255.0, 0, 1)
    ink = np.clip(dog * 0.9 + np.clip(tone - 0.12, 0, 1) * 0.25, 0, 1)
    ink[ink < 0.06] = 0  # keep the empty paper empty
    v = (1 - ink) * 255
    rgb = np.stack([v * 1.0, v * 0.985, v * 0.96], axis=2)
    return Image.fromarray(np.clip(rgb + (255 - rgb) * 0.0, 0, 255).astype(np.uint8))

def main():
    for src in sorted(p for p in glob.glob(os.path.join(AI, 'src', 's??-*.png')) if not p.endswith('-cut-raw.png')):
        sid = os.path.basename(src)[:3]
        a = np.asarray(Image.open(src).convert('RGB'), dtype=np.float32) / 255.0
        n, p = normalise(a)
        save_webp(to_alpha(n), os.path.join(AI, f'{sid}.webp'), 88)
        save_webp(to_alpha(np.asarray(lines(n), dtype=np.float32) / 255.0), os.path.join(AI, f'{sid}-lines.webp'), 80)
        ph = os.path.join(AI, f'{sid}.placeholder')
        if os.path.exists(ph): os.remove(ph)
        if sid in CUTOUT:
            cut = os.path.join(AI, 'src', f'{sid}-cut-raw.png')
            if not os.path.exists(cut):
                subprocess.run(['npx', 'hyperframes', 'remove-background', src, '-o', cut], check=True, cwd=ROOT,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            c = np.asarray(Image.open(cut).convert('RGBA'), dtype=np.float32) / 255.0
            rgb = np.clip(c[..., :3] / p, 0, 1) * PANEL
            out = np.dstack([rgb, c[..., 3:4]])
            save_webp(Image.fromarray((out * 255).astype(np.uint8), 'RGBA'), os.path.join(AI, f'{sid}-cut.webp'), 90)
        print('prepared', sid, 'paper', (p * 255).round().astype(int).tolist())
    # placeholders from the storyboard for anything not generated yet
    for i in range(1, 16):
        sid = f's{i:02d}'
        if glob.glob(os.path.join(AI, 'src', f'{sid}-*.png')):
            continue
        panel = Image.open(os.path.join(ROOT, 'references/panels', f'{i:02d}.jpg')).convert('RGB')
        w, h = panel.size
        tw = int(h * 9 / 16)
        if tw <= w:
            panel = panel.crop(((w - tw) // 2, 0, (w - tw) // 2 + tw, h))
        im = panel.resize((1152, 2048), Image.LANCZOS)
        a = np.asarray(im, dtype=np.float32) / 255.0
        n, _ = normalise(a)
        n[: int(2048 * 0.45)] = 1.0  # hide the storyboard's own caption
        save_webp(to_alpha(n), os.path.join(AI, f'{sid}.webp'), 80)
        save_webp(to_alpha(np.asarray(lines(n), dtype=np.float32) / 255.0), os.path.join(AI, f'{sid}-lines.webp'), 70)
        open(os.path.join(AI, f'{sid}.placeholder'), 'w').write('storyboard panel stand-in\n')
        if sid in CUTOUT:  # stand-in "cutout": graphite only, so the frame/type stay visible
            save_webp(to_alpha(n), os.path.join(AI, f'{sid}-cut.webp'), 80)
        print('placeholder', sid)

if __name__ == '__main__':
    main()
