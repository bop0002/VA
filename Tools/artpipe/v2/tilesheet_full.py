"""v2 - sheet tile day du cho map A_meadow va B_moonlit: terrain 6x3 cu + 14 bien the co (tong 17 o co).

Bo cuc 8 cot x 4 hang o 32px (256x128):
    c0..c5 r0..r2 : giu nguyen terrain_<theme>.png (khoi 3x3 duong, 4 goc trong, 2 duong bien the, 3 co)
    c6..c7 r0..r2 : co bien the 3..8
    c0..c7 r3     : co bien the 9..16
Moi o co dung chung nen phang lap chu ky 32 + trang tri cach mep >= 3px -> ghep voi bat ky o nao cung khong seam.
Dung: python Tools/artpipe/v2/tilesheet_full.py -> v2/out/tilesheet_<theme>.png, _labeled.png, _demo.png
"""
import os
import numpy as np
from PIL import Image, ImageDraw

import tiles_v2 as tv
import terrain_v2 as tr

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = tv.OUT
T = 32
THEMES = ["A_meadow", "B_moonlit"]

# (ten, ham ve, seed) - ten in len sheet chu thich
GRASS_EXTRA = [
    ("bui thua", "tufts", 3), ("bui day", "tufts_dense", 4), ("hoa le", "flowers", 5), ("cum hoa", "flower_patch", 6),
    ("mang toi", "dark_patch", 7), ("mang sang", "light_patch", 8), ("soi nho", "pebbles", 9), ("da to", "rock", 10),
    ("nam", "mushrooms", 11), ("co+hoa", "mixed", 12), ("mang toi+bui", "dark_tufts", 13), ("co trui", "bare", 14),
    ("hoa+soi", "flower_pebble", 15), ("mang sang+hoa", "light_flowers", 16),
]


def blob(rng, cx, cy, rx, ry, margin=4):
    yy, xx = np.mgrid[0:T, 0:T]
    ang = np.arctan2(yy - cy, xx - cx)
    wob = 1 + 0.18 * np.sin(3 * ang + rng.random() * 6) + 0.1 * np.sin(5 * ang + rng.random() * 6)
    m = ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2 < wob ** 2
    m[:margin] = m[-margin:] = False; m[:, :margin] = m[:, -margin:] = False
    return m


def stones(img, rng, P, G, n, big=False):
    placed = 0
    for _ in range(n * 10):
        if placed >= n: break
        w, h = (4, 3) if big else (2, 2)
        y, x = int(rng.integers(5, T - 5 - h)), int(rng.integers(5, T - 5 - w))
        if (img[y - 1:y + h + 2, x - 1:x + w + 1] != img[0, 0]).any() and not big:
            continue
        if big:   # da to co vien
            img[y - 1, x:x + w] = P[0]; img[y + h, x:x + w] = P[0]; img[y:y + h, x - 1] = P[0]; img[y:y + h, x + w] = P[0]
            img[y:y + h, x:x + w] = P[2]; img[y, x:x + w - 1] = P[3]; img[y + h - 1, x + 1:x + w] = P[1]
            img[y + h + 1, x:x + w] = G[0]
        else:
            img[y, x:x + w] = P[3]; img[y + 1, x:x + w] = P[2]; img[y + 2, x:x + w] = G[0]
        placed += 1


def mushrooms(img, rng, A, G, n):
    cap = A[0]
    for _ in range(n):
        y, x = int(rng.integers(8, T - 7)), int(rng.integers(6, T - 7))
        img[y, x - 1:x + 2] = cap; img[y - 1, x] = cap; img[y, x] = A[2]       # mu + cham sang
        img[y + 1, x] = A[2]; img[y + 2, x - 1:x + 2] = G[0]                    # chan + bong


def grass_variant(th, gfill, kind, seed):
    G, P, A = tv.ramp(th["grass"]), tv.ramp(th["path"]), tv.ramp(th["accent"])
    rng = np.random.default_rng(seed)
    img = gfill.copy()
    full = np.ones((T, T), bool)
    deco = lambda t, f, p: tr.decorate(img, full, th, rng, t, f, p)
    if kind == "tufts": deco(3, 0, 0)
    elif kind == "tufts_dense": deco(9, 0, 0)
    elif kind == "flowers": deco(1, 3, 0)
    elif kind == "flower_patch":
        for dy, dx in ((0, 0), (3, 4), (-2, 5), (4, -1)):
            y, x = 15 + dy, 14 + dx
            c = A[int(rng.integers(0, len(A)))]
            img[y - 1, x] = img[y + 1, x] = img[y, x - 1] = img[y, x + 1] = c; img[y, x] = A[1]; img[y + 2, x] = G[0]
        deco(2, 0, 0)
    elif kind in ("dark_patch", "dark_tufts"):
        m = blob(rng, 16, 16, 9, 6); img[m] = G[0]
        if kind == "dark_tufts": deco(4, 0, 0)
    elif kind in ("light_patch", "light_flowers"):
        m = blob(rng, 15, 17, 10, 7); img[m] = G[2]
        if kind == "light_flowers": deco(1, 2, 0)
    elif kind == "pebbles": stones(img, rng, P, G, 4)
    elif kind == "rock": stones(img, rng, P, G, 1, big=True); deco(2, 0, 0)
    elif kind == "mushrooms": mushrooms(img, rng, A, G, 2); deco(2, 0, 0)
    elif kind == "mixed": deco(5, 2, 0)
    elif kind == "bare":
        m = blob(rng, 16, 15, 7, 5); img[m] = P[1]
        edge = m & ~(np.roll(m, 1, 0) & np.roll(m, -1, 0) & np.roll(m, 1, 1) & np.roll(m, -1, 1))
        img[edge] = P[0]; img[m & np.roll(~m, 1, 0) & ~edge] = P[1]
        img[np.roll(edge, -1, 0) & ~m] = G[3]                                     # go co sang phia tren
    elif kind == "flower_pebble": deco(1, 2, 0); stones(img, rng, P, G, 2)
    return img


def build(name):
    th = tv.THEMES[name]
    base, tiles = tr.sheet_for(name)
    gfill, _ = tr.fills(th, np.random.default_rng(42))
    sheet = np.zeros((4 * T, 8 * T, 3), np.uint8)
    sheet[:3 * T, :6 * T] = base
    slots = [(6, 0), (7, 0), (6, 1), (7, 1), (6, 2), (7, 2)] + [(c, 3) for c in range(8)]
    labels = {(5, 0): "co 0", (5, 1): "co 1", (5, 2): "co 2"}
    grass_keys = [(5, 0), (5, 1), (5, 2)]
    for k, ((lab, kind, seed), (cx, cy)) in enumerate(zip(GRASS_EXTRA, slots)):
        t = grass_variant(th, gfill, kind, seed)
        sheet[cy * T:(cy + 1) * T, cx * T:(cx + 1) * T] = t
        tiles[(cx, cy)] = t; labels[(cx, cy)] = f"co {k + 3}"; grass_keys.append((cx, cy))
    return sheet, tiles, grass_keys, labels


def demo(tiles, grass_keys, rng):
    """Map 16x10: co ngau nhien (co 0 chiem ~45%) + duong ghep tu sheet."""
    Wm, Hm = 16, 10
    p = np.zeros((Hm, Wm), bool)
    p[2:4, 1:10] = True; p[2:8, 8:10] = True; p[6:8, 8:15] = True; p[6:9, 2:5] = True
    w = np.array([9, 3, 3] + [1] * (len(grass_keys) - 3), float); w /= w.sum()
    at = lambda y, x: p[y, x] if 0 <= y < Hm and 0 <= x < Wm else False
    out = np.zeros((Hm * T, Wm * T, 3), np.uint8)
    for y in range(Hm):
        for x in range(Wm):
            if not p[y, x]:
                key = grass_keys[int(rng.choice(len(grass_keys), p=w))]
            else:
                n, s, w_, e = at(y - 1, x), at(y + 1, x), at(y, x - 1), at(y, x + 1)
                key = (0 if not w_ else (2 if not e else 1), 0 if not n else (2 if not s else 1))
                if key == (1, 1):
                    if not at(y - 1, x - 1): key = (3, 0)
                    elif not at(y - 1, x + 1): key = (4, 0)
                    elif not at(y + 1, x - 1): key = (3, 1)
                    elif not at(y + 1, x + 1): key = (4, 1)
                    else: key = [(1, 1), (3, 2), (4, 2)][int(rng.integers(0, 3))]
            out[y * T:(y + 1) * T, x * T:(x + 1) * T] = tiles[key]
    return out


def labeled(sheet, labels, S=4):
    path_names = {(0, 0): "NW", (1, 0): "N", (2, 0): "NE", (0, 1): "W", (1, 1): "C", (2, 1): "E",
                  (0, 2): "SW", (1, 2): "S", (2, 2): "SE", (3, 0): "goc NW", (4, 0): "goc NE",
                  (3, 1): "goc SW", (4, 1): "goc SE", (3, 2): "duong 1", (4, 2): "duong 2"}
    im = Image.fromarray(sheet).resize((sheet.shape[1] * S, sheet.shape[0] * S), Image.NEAREST)
    dr = ImageDraw.Draw(im)
    for (cx, cy), txt in {**path_names, **labels}.items():
        x, y = cx * T * S, cy * T * S
        idx = cy * 8 + cx
        dr.rectangle((x, y, x + T * S - 1, y + T * S - 1), outline=(255, 255, 255))
        dr.rectangle((x + 1, y + 1, x + 62, y + 13), fill=(0, 0, 0))
        dr.text((x + 3, y + 2), f"{idx}: {txt}", fill=(255, 240, 160))
    return im


if __name__ == "__main__":
    for nm in THEMES:
        sheet, tiles, gk, labels = build(nm)
        Image.fromarray(sheet).save(os.path.join(OUT, f"tilesheet_{nm}.png"))
        labeled(sheet, labels).save(os.path.join(OUT, f"tilesheet_{nm}_labeled.png"))
        d = demo(tiles, gk, np.random.default_rng(3))
        Image.fromarray(d).resize((d.shape[1] * 2, d.shape[0] * 2), Image.NEAREST).save(os.path.join(OUT, f"tilesheet_{nm}_demo.png"))
        print("ok", nm, sheet.shape[1], "x", sheet.shape[0])
