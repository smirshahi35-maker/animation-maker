# Extract the footage used in each scene as 30 fps JPEG sequences sized for the sticker,
# build the animated palm-shadow matte and a paper-grain texture.
import json, os, subprocess, sys
import numpy as np
from PIL import Image, ImageFilter

ROOT = sys.argv[1]
W, H, FPS = 600, 760, 30
F = lambda n: f"{ROOT}/footage/{n}/{n.split('_')[0]}.mp4" if os.path.exists(f"{ROOT}/footage/{n}/{n.split('_')[0]}.mp4") else f"{ROOT}/footage/{n}/{n}.mp4"

# id, source folder, source start (s), length (s), horizontal crop anchor (0 left .. 1 right)
SHOTS = [
    ("s1_cascade",   "cascade_16209388",   16.0, 6.2, 0.5),
    ("s2_grapes",    "grapes_5527337",      2.0, 3.6, 0.5),
    ("s2_signing",   "signing_7735908",     1.0, 5.0, 0.5),
    ("s3_atm",       "atm_5700357",         0.3, 5.6, 0.55),
    ("s4_passport",  "passport2_9207809",   6.5, 6.6, 0.68),
    ("s5_city",      "cascadewide_16209386", 24.0, 3.6, 0.5),
    ("s5_living",    "livingroom2_5824189", 3.0, 4.2, 0.45),
    ("s6_orchard",   "orchard_11992124",    5.0, 2.8, 0.5),
    ("s6_apricot",   "apricothand_8447051", 3.0, 3.0, 0.5),
    ("s7_fruit",     "fruitline_10576687",  1.0, 4.0, 0.5),
    ("s7_pack",      "packline_6444196",   20.0, 4.4, 0.4),
    ("s8_city",      "citywalk_19022311",  10.0, 4.4, 0.5),
    ("s9_city",      "cascadewide_16209386", 36.0, 6.8, 0.5),
]

def src_path(folder):
    d = f"{ROOT}/footage/{folder}"
    return os.path.join(d, [f for f in os.listdir(d) if f.endswith(".mp4")][0])

for name, folder, ss, dur, ax in SHOTS:
    out = f"{ROOT}/build/frames/{name}"
    if os.path.isdir(out) and len(os.listdir(out)) >= int(dur * FPS) - 1:
        continue
    os.makedirs(out, exist_ok=True)
    vf = (f"fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase,"
          f"crop={W}:{H}:(iw-{W})*{ax}:(ih-{H})/2,eq=saturation=1.05")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(ss), "-i", src_path(folder), "-t", str(dur),
                    "-vf", vf, "-q:v", "3", f"{out}/%04d.jpg"], check=True)
    print(name, len(os.listdir(out)))

# palm shadow matte sequence (15 fps, half resolution; the layer is blurred anyway)
pdir = f"{ROOT}/build/palm"
if not os.path.isdir(pdir) or not os.listdir(pdir):
    os.makedirs(pdir + "/raw", exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src_path("palmshadow_8516672"), "-vf", "fps=15,scale=540:960",
                    f"{pdir}/raw/%04d.png"], check=True)
    for fn in sorted(os.listdir(pdir + "/raw")):
        L = np.asarray(Image.open(f"{pdir}/raw/{fn}").convert("L")).astype(float)
        bg = np.asarray(Image.fromarray(L.astype(np.uint8)).filter(ImageFilter.GaussianBlur(60))).astype(float)
        bg = np.maximum(bg, np.percentile(L, 90))   # paper level; shadows sit below it
        a = np.clip((bg - L) / 55.0, 0, 1) ** 0.9
        alpha = Image.fromarray((a * 230).astype(np.uint8)).filter(ImageFilter.GaussianBlur(5))
        rgba = Image.new("RGBA", alpha.size, (46, 42, 38, 0)); rgba.putalpha(alpha)
        rgba.save(f"{pdir}/{fn}")
    print("palm", len(os.listdir(pdir)) - 1)

# paper grain (tiled, offset per frame in the page)
g = f"{ROOT}/build/grain.png"
if not os.path.exists(g):
    rng = np.random.default_rng(7)
    n = rng.normal(0, 1, (1024, 1024))
    n = (n - n.min()) / (n.max() - n.min())
    a = (np.abs(n - 0.5) * 2) ** 2.2 * 60
    img = Image.new("RGBA", (1024, 1024), (90, 75, 60, 0)); img.putalpha(Image.fromarray(a.astype(np.uint8)))
    img.save(g)
print("done")
