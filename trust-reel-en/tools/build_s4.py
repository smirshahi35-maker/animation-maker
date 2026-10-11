#!/usr/bin/env python3
"""Build compositions/s4.html from tools/s4.src.html: insert the 500-project wall tiles.

The centre of the wall is the phone itself (scaled 0.165 in .slot), so tiles skip (0, 0).
Tile sources cycle deterministically through the GPT Image 2.5 stills (no identical neighbours).
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
srcs = [f"assets/ai/web/tile-{k}.jpg" for k in range(1, 10)] + [
    "assets/ai/web/bts.jpg", "assets/ai/web/latte.jpg", "assets/ai/web/customer.jpg",
    "assets/ai/web/cafe-trend.jpg", "assets/ai/web/desk.jpg"]
TW, TH, G = 86, 186, 14
CX, CY = 540, 1163
tiles = []
for i in range(-6, 7):
    for j in range(-8, 9):
        if i == 0 and j == 0:
            continue
        x = CX + j * (TW + G) - TW / 2
        y = CY + i * (TH + G) - TH / 2
        # 5 and 3 (and 5±3 = 8, 2) are all non-zero mod 14, so no tile repeats an image of any of its
        # 8 neighbours (incl. diagonals). +102 puts tile-5 (srcs[4], the phone's own screen image) at
        # the phone's (0, 0) cell, so the phone never sits next to a tile-5 either.
        src = srcs[(i * 5 + j * 3 + 102) % len(srcs)]
        d = (i * i * 0.6 + j * j) ** 0.5
        tiles.append(f'<img class="tl" data-d="{d:.2f}" src="{src}" alt="" style="left:{x:.0f}px; top:{y:.0f}px" />')
src = (ROOT / "tools/s4.src.html").read_text()
(ROOT / "compositions/s4.html").write_text(src.replace("<!--WALL-->", "\n            ".join(tiles)))
print(f"compositions/s4.html: {len(tiles)} tiles")
