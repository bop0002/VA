"""v2 - map C_graveyard theo Tools/ArtRef/conceptref.jpg: co xanh reu toi, duong dat tim, mep rang cua KHONG vien.

Sheet nen 8x4 o 32px, cung thu tu o voi tilesheet_A_meadow (RuleTile/chunk dung lai duoc):
    0 NW 1 N 2 NE | 8 W 9 C 10 E | 16 SW 17 S 18 SE   duong 3x3
    3/4/11/12 goc trong NW NE SW SE, 19/20 duong bien the
    5 co tron, 13/21 co bien the nhe, 6 7 14 15 22 23 24..31 co trang tri
Mep co: song w(t) cua terrain_v2 + rang co nho (chu ky trong 32 -> khop seam), bong toi tren dat sat mep.
Dung: python Tools/artpipe/v2/graveyard.py -> v2/out/tilesheet_C_graveyard{,_labeled,_demo}.png
"""
import os
import numpy as np
from PIL import Image

import terrain_v2 as tr
import tilesheet_full as tf

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
T = 32
NAME = "C_graveyard"
# detail = ban dau (nhieu hat), flat = mang phang + la co toi o mep (giong concept), flat_soft = flat + mang sang/toi lon o o bien the
STYLES = ["detail", "flat", "flat_soft"]
STYLE = "detail"

hx = lambda s: np.array([int(s[i:i + 2], 16) for i in (1, 3, 5)], np.uint8)
# mau lay tu conceptref.jpg (vung co trai, vung duong giua)
G = [hx(c) for c in ("#243036", "#33444a", "#3f5250", "#4b6058", "#5e7662", "#768f6c")]   # co: toi -> sang
P = [hx(c) for c in ("#251c30", "#33263f", "#3f2d49", "#4a3450", "#58405d", "#674f69")]   # dat tim
S = [hx(c) for c in ("#2a2834", "#4a4a56", "#6b6c74", "#8c8d92")]                         # soi/da xam
BONE = [hx(c) for c in ("#5d5a58", "#a9a294", "#d8d0bc")]
MUSH = [hx(c) for c in ("#3d6e73", "#6fb7b0", "#b8f0dc")]                                 # nam phat sang xanh
LEAF = [hx(c) for c in ("#4a3530", "#6b4a35", "#8a6a45")]
FLOW = [hx(c) for c in ("#7a6a9a", "#b8a8d8", "#e8e0f0")]


def hash2(y, x, k=0):
    """Gia ngau nhien theo toa do (mod 32) -> nhu nhau o moi o, khong lo seam."""
    y = np.asarray(y) % T; x = np.asarray(x) % T
    v = (x * 374761393 + y * 668265263 + k * 2147483647) & 0xFFFFFFFF
    v = ((v ^ (v >> 13)) * 1274126177) & 0xFFFFFFFF
    return (v & 0xFFFF) / 65535.0


def strokes(img, rng, n, shape, col_a, col_b):
    """Rai n net nho (toa do vong 32 -> lap khong seam). shape: list (dy, dx, 0|1) 1 = mau b."""
    for _ in range(n):
        y, x = rng.integers(0, T, 2)
        for dy, dx, k in shape:
            img[(y + dy) % T, (x + dx) % T] = col_b if k else col_a


V = [(0, 0, 0), (-1, -1, 1), (-1, 1, 1)]          # la co chu V: goc toi, 2 dau sang
DASH = [(0, 0, 0), (0, 1, 0)]
BLOT = [(0, 0, 0), (0, 1, 0), (1, 0, 0), (1, 1, 0), (0, 2, 1)]


def grass_fill():
    """Nen co mem: mau giua + dom 2px toi va net la chu V sang, mat do thap (khong nhieu hat)."""
    rng = np.random.default_rng(7)
    img = np.empty((T, T, 3), np.uint8); img[:] = G[2]
    if STYLE != "detail":                                  # phang: chi vai la co toi
        strokes(img, rng, 4, V, G[1], G[1])
        return img
    strokes(img, rng, 10, BLOT, G[1], G[1])
    strokes(img, rng, 14, DASH, G[1], G[1])
    strokes(img, rng, 12, V, G[2], G[3])
    strokes(img, rng, 4, V, G[3], G[4])
    return img


def path_fill():
    """Dat tim: dom 2px toi/sang thua, khong soi (soi chi o bien the 20 de khoi lap luoi)."""
    rng = np.random.default_rng(9)
    img = np.empty((T, T, 3), np.uint8); img[:] = P[3]
    if STYLE != "detail":
        strokes(img, rng, 4, DASH, P[2], P[2])
        return img
    strokes(img, rng, 10, BLOT, P[2], P[2])
    strokes(img, rng, 12, DASH, P[2], P[2])
    strokes(img, rng, 8, DASH, P[4], P[4])
    return img


def make_tile(gfill, pfill, sides="", inner=""):
    pad = 4
    gm = tr.grass_mask(sides, [inner[i:i + 2] for i in range(0, len(inner), 2)], pad)
    r = np.arange(-pad, T + pad)
    yy, xx = np.meshgrid(r, r, indexing="ij")
    sh = lambda m, dy, dx: np.roll(np.roll(m, dy, 0), dx, 1)
    pm = ~gm
    # rang co: diem dat sat mep co -> thanh co (la thong xuong/ngang), mot so dai 2px
    near = pm & (sh(gm, 1, 0) | sh(gm, -1, 0) | sh(gm, 0, 1) | sh(gm, 0, -1))
    tooth = near & (hash2(yy, xx, 11) < 0.45)
    long_ = sh(tooth & sh(gm, 1, 0), 1, 0) & pm & (hash2(yy, xx, 12) < 0.5)   # rang dai keo xuong duoi
    gm2 = gm | tooth | long_
    pm2 = ~gm2
    tip = gm2 & ~gm                                          # dau rang: sang hon
    edge = gm2 & (sh(pm2, 1, 0) | sh(pm2, -1, 0) | sh(pm2, 0, 1) | sh(pm2, 0, -1))
    shadow1 = pm2 & (sh(gm2, 1, 0) | sh(gm2, 0, 1) | sh(gm2, 0, -1) | sh(gm2, -1, 0))
    shadow2 = pm2 & ~shadow1 & (sh(gm2, 2, 0) | sh(gm2, 3, 0))   # bong dai hon phia duoi co
    if STYLE != "detail":
        return flat_edge(gm, pm, yy, xx, sh, pad, gfill, pfill)
    c = slice(pad, pad + T)
    gm2, tip, edge, shadow1, shadow2 = gm2[c, c], tip[c, c], edge[c, c], shadow1[c, c], shadow2[c, c]
    img = np.where(gm2[..., None], gfill, pfill).copy()
    img[shadow2] = P[2]; img[shadow1] = P[1]
    img[edge] = G[3]; img[tip] = G[4]
    return img, gm2


def flat_edge(gm, pm, yy, xx, sh, pad, gfill, pfill):
    """Mep kieu concept: la co TOI (G1) thua thot thong ra dat 1-3px, dat sat mep toi nhe 1 bac, khong vien sang."""
    near = pm & (sh(gm, 1, 0) | sh(gm, -1, 0) | sh(gm, 0, 1) | sh(gm, 0, -1))
    blade = near & (hash2(yy, xx, 11) < 0.32)
    down = sh(blade & sh(gm, 1, 0), 1, 0) & pm & (hash2(yy, xx, 12) < 0.55)     # la dai ve phia duoi (co o tren)
    down2 = sh(down, 1, 0) & pm & (hash2(yy, xx, 13) < 0.35)
    fringe = blade | down | down2
    rim = gm & (sh(pm, 1, 0) | sh(pm, -1, 0) | sh(pm, 0, 1) | sh(pm, 0, -1)) & (hash2(yy, xx, 14) < 0.5)
    shade = pm & ~fringe & (sh(gm | fringe, 1, 0) | sh(gm | fringe, 0, 1) | sh(gm | fringe, 0, -1) | sh(gm | fringe, -1, 0))
    c = slice(pad, pad + T)
    gm, fringe, rim, shade = gm[c, c], fringe[c, c], rim[c, c], shade[c, c]
    img = np.where(gm[..., None], gfill, pfill).copy()
    img[shade] = P[2]; img[rim] = G[1]; img[fringe] = G[1]
    return img, gm | fringe


def tufts(img, mask, rng, n, cols=None):
    if cols is None:
        cols = (G[3], G[4], G[5]) if STYLE == "detail" else (G[1], G[1], G[1])   # phang: bui toi nhu concept
    lo, hi = 6, T - 6
    for _ in range(n * 6):
        if n <= 0: break
        y, x = int(rng.integers(lo + 2, hi)), int(rng.integers(lo, hi))
        if not mask[y - 3:y + 2, x - 2:x + 3].all(): continue
        for dx, ht in ((-1, 2), (0, 3), (1, 2), (2, 1) if rng.random() < .4 else (0, 0)):
            for k in range(ht): img[y - k, x + dx] = cols[1] if k == ht - 1 else cols[0]
        if rng.random() < .3: img[y - 3, x] = cols[2]
        img[y + 1, x - 1:x + 2] = G[1]; n -= 1


def pebbles(img, mask, rng, n, big=False):
    for _ in range(n * 10):
        if n <= 0: break
        w, h = (5, 4) if big else (2, 2)
        y, x = int(rng.integers(6, T - 6 - h)), int(rng.integers(6, T - 6 - w))
        if not mask[y - 1:y + h + 2, x - 1:x + w + 1].all(): continue
        img[y:y + h, x:x + w] = S[1]; img[y, x:x + w] = S[2]
        if big:
            img[y + 1, x + 1:x + w - 1] = S[2]; img[y, x + 1] = S[3]
            img[y + h - 1, x + 1:x + w] = S[0]; img[y:y + h, x + w - 1] = S[0]
        img[y + h, x:x + w] = G[0]; n -= 1


def mushrooms(img, rng, n):
    for _ in range(n):
        y, x = int(rng.integers(9, T - 8)), int(rng.integers(7, T - 7))
        img[y, x - 1:x + 2] = MUSH[1]; img[y - 1, x] = MUSH[2]; img[y, x] = MUSH[2]
        img[y + 1, x] = BONE[1]; img[y + 2, x - 1:x + 2] = G[0]
        img[y - 2, x] = MUSH[0]


def bones(img, rng, n):
    for _ in range(n):
        y, x = int(rng.integers(10, T - 10)), int(rng.integers(8, T - 12))
        if rng.random() < .5:      # xuong ngang
            img[y, x + 1:x + 5] = BONE[2]; img[y - 1, x] = img[y + 1, x] = BONE[1]
            img[y - 1, x + 5] = img[y + 1, x + 5] = BONE[1]; img[y + 1, x + 1:x + 5] = BONE[0]
        else:                      # xuong cheo
            for k in range(4): img[y + k, x + k] = BONE[2]; img[y + k + 1, x + k] = BONE[0]
            img[y - 1, x] = img[y, x - 1] = BONE[1]; img[y + 4, x + 4] = img[y + 3, x + 5] = BONE[1]


def skull(img, y, x):
    m = ["..###..", ".#####.", "#######", "#.#.#.#", "#######", ".#.#.#.", "..___.."]
    for j, row in enumerate(m):
        for i, ch in enumerate(row):
            if ch == "#": img[y + j, x + i] = BONE[2] if j < 3 else BONE[1]
            if ch == "_": img[y + j, x + i] = G[0]
    img[y + 3, x + 1] = img[y + 3, x + 5] = G[0]; img[y + 3, x + 3] = BONE[0]   # hoc mat + mui
    img[y, x + 2:x + 5] = BONE[1]


def leaves(img, rng, n):
    for _ in range(n):
        y, x = int(rng.integers(6, T - 7)), int(rng.integers(6, T - 7))
        c = LEAF[int(rng.integers(0, 3))]
        img[y, x:x + 2] = c; img[y + 1, x + 1] = c; img[y + 1, x] = LEAF[0]


def flowers(img, rng, n):
    for _ in range(n):
        y, x = int(rng.integers(7, T - 7)), int(rng.integers(7, T - 7))
        c = FLOW[int(rng.integers(0, 2))]
        img[y - 1, x] = img[y + 1, x] = img[y, x - 1] = img[y, x + 1] = c; img[y, x] = FLOW[2]
        img[y + 2, x] = G[1]


def patch(img, rng, col, rx, ry, cx=16, cy=16):
    m = tf.blob(rng, cx, cy, rx, ry, margin=4)
    img[m & ((hash2(*np.mgrid[0:T, 0:T], 21) < 0.85) | (STYLE != "detail"))] = col
    return m


def grass_variant(gfill, kind, seed):
    rng = np.random.default_rng(seed)
    img = gfill.copy(); full = np.ones((T, T), bool)
    if STYLE == "flat_soft" and kind in ("plain2", "plain3"):     # mang sang / toi lon, mem -> co bot phang deu
        m = tf.blob(rng, 16, 16, 12, 9, margin=2)
        img[m] = G[3] if kind == "plain2" else G[1]
        return img
    if kind == "plain2" and STYLE != "detail": strokes(img, rng, 3, V, G[1], G[1])
    elif kind == "plain2": img[hash2(*np.mgrid[0:T, 0:T], 31) < 0.06] = G[1]
    elif kind == "plain3": tufts(img, full, rng, 1)
    elif kind == "tufts": tufts(img, full, rng, 3)
    elif kind == "tufts_dense": tufts(img, full, rng, 8)
    elif kind == "dark_patch": patch(img, rng, G[1], 9, 6); tufts(img, full, rng, 1, (G[2], G[3], G[4]))
    elif kind == "moss_patch": patch(img, rng, G[3], 8, 6); tufts(img, full, rng, 2, (G[4], G[5], G[5]))
    elif kind == "pebbles": pebbles(img, full, rng, 4)
    elif kind == "rock": pebbles(img, full, rng, 1, big=True); tufts(img, full, rng, 2)
    elif kind == "mushrooms": mushrooms(img, rng, 2); tufts(img, full, rng, 1)
    elif kind == "bones": bones(img, rng, 2)
    elif kind == "skull": skull(img, 12, 12); tufts(img, full, rng, 2)
    elif kind == "leaves": leaves(img, rng, 7)
    elif kind == "flowers": flowers(img, rng, 2); tufts(img, full, rng, 2)
    elif kind == "bare":
        m = patch(img, rng, P[3], 7, 5)
        e = m & ~(np.roll(m, 1, 0) & np.roll(m, -1, 0) & np.roll(m, 1, 1) & np.roll(m, -1, 1))
        img[e] = P[1]; img[m & ~np.roll(m, 1, 0)] = P[1]; img[np.roll(e, -1, 0) & ~m] = G[3]
    elif kind == "roots":
        for y0, x0, d in ((12, 7, 1), (19, 9, 1)):
            for k in range(14): img[y0 + (k // 5) * d, x0 + k] = LEAF[0]; img[y0 + (k // 5) * d - 1, x0 + k] = LEAF[1] if k % 3 else LEAF[0]
    elif kind == "leaves_tufts": leaves(img, rng, 3); tufts(img, full, rng, 3)
    return img


# (ten nhan, kieu, seed) -> 2 o bien the nhe (13, 21) + 14 o trang tri
LIGHT = [("co 1", "plain2", 2), ("co 2", "plain3", 3)]
EXTRA = [("bui", "tufts", 3), ("bui day", "tufts_dense", 4), ("mang toi", "dark_patch", 7), ("reu", "moss_patch", 8),
         ("soi", "pebbles", 9), ("da", "rock", 10), ("nam sang", "mushrooms", 11), ("xuong", "bones", 12),
         ("so", "skull", 13), ("la kho", "leaves", 14), ("hoa tim", "flowers", 15), ("dat trui", "bare", 16),
         ("re cay", "roots", 17), ("la+bui", "leaves_tufts", 18)]
# vi tri (cot, hang) giong tilesheet_full: 6 7 14 15 22 23 + 24..31
SLOTS = [(6, 0), (7, 0), (6, 1), (7, 1), (6, 2), (7, 2)] + [(c, 3) for c in range(8)]


def build():
    gfill, pfill = grass_fill(), path_fill()
    sheet = np.zeros((4 * T, 8 * T, 3), np.uint8)
    tiles, labels = {}, {}
    for (cx, cy), (sides, inner, seed, _) in tr.LAYOUT.items():
        if sides == "NSWE": continue
        t, gm = make_tile(gfill, pfill, sides, inner)
        if (cx, cy) == (4, 2): pebbles(t, ~gm, np.random.default_rng(seed), 3)     # duong bien the: them soi
        if (cx, cy) == (3, 2): leaves(t, np.random.default_rng(seed), 3)
        tiles[(cx, cy)] = t
    tiles[(5, 0)] = gfill.copy(); labels[(5, 0)] = "co 0"
    for (lab, kind, seed), key in zip(LIGHT, [(5, 1), (5, 2)]):
        tiles[key] = grass_variant(gfill, kind, seed); labels[key] = lab
    for (lab, kind, seed), key in zip(EXTRA, SLOTS):
        tiles[key] = grass_variant(gfill, kind, seed); labels[key] = lab
    for (cx, cy), t in tiles.items():
        sheet[cy * T:(cy + 1) * T, cx * T:(cx + 1) * T] = t
    gk = [(5, 0), (5, 1), (5, 2)] + SLOTS
    return sheet, tiles, gk, labels


def save(im, path, tries=20):
    """Luu anh, thu lai neu file dang bi trinh xem anh/antivirus giu (Windows Errno 22/13)."""
    import time
    for k in range(tries):
        try: return im.save(path)
        except OSError:
            if k == tries - 1: raise
            time.sleep(0.25)


if __name__ == "__main__":
    import sys
    pick = sys.argv[1] if len(sys.argv) > 1 else "flat"    # style chot 2026-10-13 = flat -> file chinh tilesheet_C_graveyard.png
    demos = []
    for STYLE in STYLES:
        sheet, tiles, gk, labels = build()
        sfx = "" if STYLE == pick else f"_{STYLE}"
        o = OUT if STYLE == pick else os.path.join(OUT, "_archive")      # style khong chon -> out/_archive
        os.makedirs(o, exist_ok=True)
        save(Image.fromarray(sheet), os.path.join(o, f"tilesheet_{NAME}{sfx}.png"))
        save(tf.labeled(sheet, labels), os.path.join(o, f"tilesheet_{NAME}{sfx}_labeled.png"))
        d = tf.demo(tiles, gk, np.random.default_rng(3))
        save(Image.fromarray(d).resize((d.shape[1] * 2, d.shape[0] * 2), Image.NEAREST), os.path.join(o, f"tilesheet_{NAME}{sfx}_demo.png"))
        demos.append(Image.fromarray(d).crop((0, 0, 320, 224)))
    cmp_ = Image.new("RGB", (len(demos) * 328, 224), (10, 10, 14))
    for i, d in enumerate(demos): cmp_.paste(d, (i * 328, 0))
    save(cmp_.resize((cmp_.width * 2, cmp_.height * 2), Image.NEAREST), os.path.join(OUT, "_archive", f"tilesheet_{NAME}_compare.png"))
    print("ok", NAME, STYLES, "->", pick or "(chua chon)")
