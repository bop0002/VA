"""v2 - tileset terrain 3x3 + 4 goc trong cho cac theme da chon. Thay bo autotile 47 o cua v1.

Sheet moi theme: 6 cot x 3 hang o 32px (v2/out/terrain_<theme>.png)
    c0..c2 : khoi 3x3 (NW N NE / W C E / SW S SE) - C = duong full
    c3..c4 : r0 = goc trong co o NW, NE | r1 = goc trong co o SW, SE | r2 = duong bien the 1, 2
    c5     : co bien the 0, 1, 2 (0 = tron, dung nhieu nhat)
Mep giua cac o khop vi: duong bien cach mep o b px + song w(t) co chu ky 32 va w(0)=w(32)=0;
nen co/duong la texture lap chu ky 32; trang tri (bui co, hoa, soi) chi dat cach mep >= 3px.
Duong toi thieu rong 2 o (bo 3x3 khong co o duong rong 1).
Dung: python Tools/artpipe/v2/terrain_v2.py
"""
import os
import numpy as np
from PIL import Image, ImageDraw

import tiles_v2 as tv

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = tv.OUT
T, B, R = 32, 9, 6                  # o, le co tu mep, ban kinh bo goc ngoai
PICK = ["A_meadow", "B_moonlit", "C_haunted", "E_cemetery", "F_swamp"]


def w(t):
    return np.round(1.6 * np.sin(2 * np.pi * t / T) + 0.9 * np.sin(6 * np.pi * t / T + 0)).astype(int)


def grass_mask(sides, inner, pad=4):
    """True = co. Toa do mo rong [-pad, T+pad) de tinh vien/bong o mep cho khop o ben canh."""
    r = np.arange(-pad, T + pad)
    y, x = np.meshgrid(r, r, indexing="ij")
    g = np.zeros_like(x, bool)
    if "N" in sides: g |= y < B + w(x)
    if "S" in sides: g |= (T - 1 - y) < B + w(x)
    if "W" in sides: g |= x < B + w(y)
    if "E" in sides: g |= (T - 1 - x) < B + w(y)
    for a, bb in (("N", "W"), ("N", "E"), ("S", "W"), ("S", "E")):   # bo tron goc ngoai
        if a in sides and bb in sides:
            cy = B + R if a == "N" else T - 1 - B - R
            cx = B + R if bb == "W" else T - 1 - B - R
            inq = ((y < cy) if a == "N" else (y > cy)) & ((x < cx) if bb == "W" else (x > cx))
            g |= inq & ((y - cy) ** 2 + (x - cx) ** 2 > R * R)
    for corner in inner:                                               # goc trong: 1/4 hinh tron ban kinh B
        cy = -0.5 if corner[0] == "N" else T - 0.5
        cx = -0.5 if corner[1] == "W" else T - 0.5
        g |= (y - cy) ** 2 + (x - cx) ** 2 < (B + 0.5) ** 2
    return g


def periodic_noise(rng, n=4):
    g = rng.random((n, n))
    big = np.tile(g, (3, 3))
    im = Image.fromarray((big * 255).astype(np.uint8)).resize((3 * T, 3 * T), Image.BICUBIC)
    return np.asarray(im)[T:2 * T, T:2 * T] / 255.0


def fills(th, rng):
    G, P = tv.ramp(th["grass"]), tv.ramp(th["path"])
    # nen phang + dom 1-2px (mang to se lo lap moi 32px)
    grass = np.empty((T, T, 3), np.uint8); grass[:] = G[1]
    for _ in range(10):
        y, x = rng.integers(0, T, 2); grass[y, x] = G[0]
        if rng.random() < .5: grass[y, (x + 1) % T] = G[0]
    path = np.empty((T, T, 3), np.uint8); path[:] = P[2]
    if th["style"] == "dirt":
        for _ in range(16):
            y, x = rng.integers(0, T, 2); path[y, x] = P[1] if rng.random() < .65 else P[3]
    else:                               # da cuoi tren xuyen chu ky 32 (khoang cach vong)
        pts = rng.random((9, 2)) * T
        yy, xx = np.mgrid[0:T, 0:T]
        ds = []
        for py, px in pts:
            dy = np.minimum(abs(yy - py), T - abs(yy - py)); dx = np.minimum(abs(xx - px), T - abs(xx - px))
            ds.append(dy ** 2 + (dx * 0.8) ** 2)
        ds = np.sort(np.sqrt(np.stack(ds)), 0)
        gap = ds[1] - ds[0] < 1.6
        top = ~gap & np.roll(gap, 1, 0)
        path[top] = P[3]; path[~gap & np.roll(gap, -1, 0) & ~top] = P[1]; path[gap] = P[1]
    return grass, path


def decorate(img, grass, th, rng, n_tuft, n_flower, n_peb, margin=3):
    G, P, A = tv.ramp(th["grass"]), tv.ramp(th["path"]), tv.ramp(th["accent"])
    lo, hi = margin + 2, T - margin - 2

    def free(m, y, x, r):
        return m[y - r:y + r + 1, x - r:x + r + 1].all()
    for _ in range(n_tuft * 4):
        if n_tuft <= 0: break
        y, x = int(rng.integers(lo + 2, hi)), int(rng.integers(lo, hi))
        if not free(grass, y - 1, x, 3): continue
        dark = rng.random() < 0.35
        top, mid = (G[2], G[1]) if dark else (G[3], G[2])
        for dx, ht in ((-1, 2), (0, 3), (1, 2)):
            for k in range(ht): img[y - k, x + dx] = top if k == ht - 1 else mid
        img[y + 1, x - 1:x + 2] = G[0]; n_tuft -= 1
    for _ in range(n_flower * 6):
        if n_flower <= 0: break
        y, x = int(rng.integers(lo, hi)), int(rng.integers(lo, hi))
        if not free(grass, y, x, 3): continue
        col = A[int(rng.integers(0, len(A)))]
        img[y - 1, x] = img[y + 1, x] = img[y, x - 1] = img[y, x + 1] = col
        img[y, x] = A[1] if not (col == A[1]).all() else A[2]; img[y + 2, x] = G[0]; n_flower -= 1
    if th["style"] == "dirt":
        for _ in range(n_peb * 6):
            if n_peb <= 0: break
            y, x = int(rng.integers(lo, hi - 2)), int(rng.integers(lo, hi - 1))
            if not free(~grass, y + 1, x, 3): continue
            img[y, x:x + 2] = P[3]; img[y + 1, x:x + 2] = P[2]; img[y + 2, x:x + 2] = P[0]; n_peb -= 1


def make_tile(th, gfill, pfill, sides="", inner="", seed=0, deco=(3, 1, 2)):
    G, P = tv.ramp(th["grass"]), tv.ramp(th["path"])
    pad = 4
    gm = grass_mask(sides, [inner[i:i + 2] for i in range(0, len(inner), 2)], pad)
    pm = ~gm
    sh = lambda m, dy, dx: np.roll(np.roll(m, dy, 0), dx, 1)
    edge = pm & (sh(gm, 1, 0) | sh(gm, -1, 0) | sh(gm, 0, 1) | sh(gm, 0, -1))
    under = pm & ~edge & (sh(gm, 2, 0) | sh(gm, 3, 0))
    lip = gm & (sh(pm, 1, 0) | sh(pm, -1, 0) | sh(pm, 0, 1) | sh(pm, 0, -1))
    lip_top = lip & sh(pm, -1, 0)
    c = slice(pad, pad + T)
    gm, edge, under, lip, lip_top = gm[c, c], edge[c, c], under[c, c], lip[c, c], lip_top[c, c]
    img = np.where(gm[..., None], gfill, pfill).copy()
    img[under] = P[1]; img[edge] = P[0]; img[lip] = G[2]; img[lip_top] = G[3]
    decorate(img, gm & ~lip, th, np.random.default_rng(seed), *deco)
    return img


LAYOUT = {   # (cot, hang): (sides co, goc trong co, seed, (bui, hoa, soi))
    (0, 0): ("NW", "", 1, (2, 1, 0)), (1, 0): ("N", "", 2, (2, 0, 1)), (2, 0): ("NE", "", 3, (2, 1, 0)),
    (0, 1): ("W", "", 4, (1, 0, 1)), (1, 1): ("", "", 5, (0, 0, 2)), (2, 1): ("E", "", 6, (1, 0, 1)),
    (0, 2): ("SW", "", 7, (2, 0, 0)), (1, 2): ("S", "", 8, (2, 1, 1)), (2, 2): ("SE", "", 9, (2, 0, 0)),
    (3, 0): ("", "NW", 10, (0, 0, 1)), (4, 0): ("", "NE", 11, (0, 0, 1)),
    (3, 1): ("", "SW", 12, (0, 0, 1)), (4, 1): ("", "SE", 13, (0, 0, 1)),
    (3, 2): ("", "", 14, (0, 0, 0)), (4, 2): ("", "", 15, (0, 0, 4)),
    (5, 0): ("NSWE", "", 16, (1, 0, 0)), (5, 1): ("NSWE", "", 17, (5, 1, 0)), (5, 2): ("NSWE", "", 18, (7, 3, 0)),
}


def sheet_for(name):
    th = tv.THEMES[name]
    gfill, pfill = fills(th, np.random.default_rng(42))
    sheet = np.zeros((3 * T, 6 * T, 3), np.uint8)
    tiles = {}
    for (cx, cy), (sides, inner, seed, deco) in LAYOUT.items():
        t = make_tile(th, gfill, pfill, sides, inner, seed, deco)
        if sides == "NSWE":                 # o co full: khong co vien
            t = np.where(np.ones((T, T, 1), bool), gfill, gfill).copy()
            decorate(t, np.ones((T, T), bool), th, np.random.default_rng(seed), *deco)
        tiles[(cx, cy)] = t
        sheet[cy * T:(cy + 1) * T, cx * T:(cx + 1) * T] = t
    return sheet, tiles


def demo_map(tiles, rng):
    """Ghep map 14x9 tu dung cac o trong sheet -> soi seam."""
    Wm, Hm = 14, 9
    p = np.zeros((Hm, Wm), bool)
    p[2:4, 1:9] = True; p[2:8, 7:9] = True; p[6:8, 7:13] = True; p[5:8, 2:5] = True
    at = lambda y, x: p[y, x] if 0 <= y < Hm and 0 <= x < Wm else False
    out = np.zeros((Hm * T, Wm * T, 3), np.uint8)
    for y in range(Hm):
        for x in range(Wm):
            if not p[y, x]:
                key = (5, int(rng.choice(3, p=[.6, .25, .15])))
            else:
                n, s, w_, e = at(y - 1, x), at(y + 1, x), at(y, x - 1), at(y, x + 1)
                cx = 0 if not w_ else (2 if not e else 1)
                cy = 0 if not n else (2 if not s else 1)
                key = (cx, cy)
                if (cx, cy) == (1, 1):
                    if not at(y - 1, x - 1): key = (3, 0)
                    elif not at(y - 1, x + 1): key = (4, 0)
                    elif not at(y + 1, x - 1): key = (3, 1)
                    elif not at(y + 1, x + 1): key = (4, 1)
                    else: key = [(1, 1), (3, 2), (4, 2)][int(rng.integers(0, 3))]
            out[y * T:(y + 1) * T, x * T:(x + 1) * T] = tiles[key]
    return out


if __name__ == "__main__":
    S, pad, lab = 2, 12, 20
    rows = []
    for nm in PICK:
        sheet, tiles = sheet_for(nm)
        Image.fromarray(sheet).save(os.path.join(OUT, f"terrain_{nm}.png"))
        demo = demo_map(tiles, np.random.default_rng(1))
        Image.fromarray(demo).save(os.path.join(OUT, f"terrain_{nm}_demo.png"))
        rows.append((nm, sheet, demo))
    dw = rows[0][2].shape[1]; sw = rows[0][1].shape[1]
    W_ = pad + sw * S + pad + dw * S + pad
    H_ = pad + len(rows) * (rows[0][2].shape[0] * S + lab + pad)
    big = Image.new("RGB", (W_, H_), (18, 14, 24)); dr = ImageDraw.Draw(big)
    for i, (nm, sheet, demo) in enumerate(rows):
        y = pad + i * (demo.shape[0] * S + lab + pad)
        dr.text((pad, y + 4), f"{nm}  (sheet 6x3 | map ghep tu sheet)", fill=(240, 230, 210))
        big.paste(Image.fromarray(sheet).resize((sw * S, sheet.shape[0] * S), Image.NEAREST), (pad, y + lab))
        big.paste(Image.fromarray(demo).resize((dw * S, demo.shape[0] * S), Image.NEAREST), (pad * 2 + sw * S, y + lab))
    big.save(os.path.join(OUT, "terrain_options.png"))
    print("ok", PICK)
