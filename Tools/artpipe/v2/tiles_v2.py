"""v2 - mau tile toon de chon (phan 1). Moi theme render 1 map mau 12x8 o (co + duong dat/da).

Khac ban v1: mau ruc hon, vien duong toi ro (toon), mep co co gờ sang + bong do xuong duong,
bui co hinh chu V co highlight, hoa diem mau. Chua cat tileset - chot theme roi moi cat.
Dung: python Tools/artpipe/v2/tiles_v2.py  -> v2/out/tiles_options.png
"""
import os
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
T, W, H = 32, 12, 8


def c(h):
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.uint8)


# grass: dk, mid, lt, hi | path: line, dk, mid, lt | accent: hoa
THEMES = {
    "A_meadow":   dict(grass="1f5a3a 2f7d43 4fa84a 9be05a", path="2a1a1a 7a4e30 a06a3c d39a5a", accent="ff6b8a ffe066 ffffff", style="dirt"),
    "B_moonlit":  dict(grass="173c48 22605f 33877a 72c4a0", path="1a1424 463a68 63559a 9284cc", accent="e0b0ff ffe08a a8f0ff", style="dirt"),
    "C_haunted":  dict(grass="234a32 336b3e 4f9446 a2d45e", path="1a1028 4a2a5e 6a3f80 9a6ac0", accent="ff8a7a f6a23a e0b0ff", style="dirt"),
    "D_autumn":   dict(grass="4e5a24 6e7f2c 9aa33a d8cf68", path="2a1414 6b3a2a 94583a c48a5a", accent="dc3943 f6a23a ffe08a", style="dirt"),
    "E_cemetery": dict(grass="1f4a3c 2f6b4f 4a9463 98d08a", path="1a1424 4c4468 6e6a90 a8b2d0", accent="ece4c2 a8bbde ff8a7a", style="cobble"),
    "F_swamp":    dict(grass="2a4426 3f6630 6a9a3c b8d86a", path="0d1418 1f3a40 2f5a5e 4f8a84", accent="c4dc78 a860e0 ffe08a", style="dirt"),
}


def ramp(s):
    return [c(h) for h in s.split()]


def path_mask():
    m = np.zeros((H, W), bool)
    m[5, 0:8] = True; m[2:6, 7] = True; m[2, 7:12] = True     # duong cong
    m[5:7, 9:11] = True                                       # khoang dat 2x2
    m[1, 2] = True                                            # o le -> mang tron
    return m


def smooth_mask(cells, rng, r=9):
    big = np.kron(cells.astype(float), np.ones((T, T)))
    k = np.ones(2 * r + 1) / (2 * r + 1)
    for ax in (0, 1):
        big = np.apply_along_axis(lambda v: np.convolve(np.pad(v, r, mode="edge"), k, "valid"), ax, big)
    n = low_noise(big.shape, rng, 12) * 0.22
    return big + n - 0.11 > 0.5


def low_noise(shape, rng, cell):
    g = rng.random((shape[0] // cell + 2, shape[1] // cell + 2))
    im = Image.fromarray((g * 255).astype(np.uint8)).resize(
        ((g.shape[1]) * cell, (g.shape[0]) * cell), Image.BICUBIC)
    return np.asarray(im)[:shape[0], :shape[1]] / 255.0


def shift(m, dy, dx):
    return np.roll(np.roll(m, dy, 0), dx, 1)


def render(th, seed=3):
    rng = np.random.default_rng(seed)
    G, P, A = ramp(th["grass"]), ramp(th["path"]), ramp(th["accent"])
    hp, wp = H * T, W * T
    path = smooth_mask(path_mask(), rng)
    img = np.zeros((hp, wp, 3), np.uint8)

    # --- co: nen mid, mang cel toi/sang to (khong dither) ---
    n = low_noise((hp, wp), rng, 56)
    img[:] = G[1]; img[n < 0.2] = G[0]; img[n > 0.8] = G[2]

    # --- duong ---
    if th["style"] == "dirt":
        n2 = low_noise((hp, wp), rng, 18)
        pv = np.where(n2[..., None] < 0.22, P[1], np.where(n2[..., None] > 0.8, P[3], P[2]))
        img[path] = pv[path]
    else:   # da cuoi: o voronoi, vien toi, highlight goc tren-trai
        pts = rng.random((260, 2)) * [hp, wp]
        yy, xx = np.mgrid[0:hp, 0:wp]
        d = np.full((hp, wp), 1e9); d2 = d.copy(); lab = np.zeros((hp, wp), int)
        for i, (py, px) in enumerate(pts):
            dd = (yy - py) ** 2 + ((xx - px) * 0.8) ** 2
            closer = dd < d
            d2 = np.where(closer, d, np.minimum(d2, dd)); lab = np.where(closer, i, lab); d = np.where(closer, dd, d)
        gap = np.sqrt(d2) - np.sqrt(d) < 1.6
        stone = np.empty((hp, wp, 3), np.uint8); stone[:] = P[2]
        top = ~gap & shift(gap, 1, 0)                          # canh tren cua vien -> sang
        stone[top] = P[3]; stone[gap] = P[1]
        bot = ~gap & shift(gap, -1, 0); stone[bot & ~top] = P[1]
        img[path] = stone[path]

    # --- vien toon: duong vien toi + bong do tu co xuong + go sang tren co ---
    grass = ~path
    edge = path & (shift(grass, 1, 0) | shift(grass, -1, 0) | shift(grass, 0, 1) | shift(grass, 0, -1))
    under = path & ~edge & (shift(grass, 2, 0) | shift(grass, 3, 0)) & ~(shift(grass, -2, 0))
    img[under] = P[1]
    img[edge] = P[0]
    lip = grass & (shift(path, 1, 0) | shift(path, -1, 0) | shift(path, 0, 1) | shift(path, 0, -1))
    img[lip & shift(path, -1, 0)] = G[3]                      # mep co nam tren duong -> sang
    img[lip & ~shift(path, -1, 0)] = G[2]

    # soi tren duong dat
    if th["style"] == "dirt":
        for _ in range(26):
            y, x = int(rng.integers(2, hp - 3)), int(rng.integers(2, wp - 3))
            if path[y - 1:y + 3, x - 1:x + 3].all():
                img[y, x] = img[y, x + 1] = P[3]; img[y + 1, x] = img[y + 1, x + 1] = P[2]
                img[y + 2, x:x + 2] = P[0]

    # --- bui co chu V (3 la), hoa ---
    for _ in range(int(wp * hp / 260)):
        y, x = int(rng.integers(3, hp - 2)), int(rng.integers(2, wp - 3))
        if not grass[y - 3:y + 2, x - 2:x + 3].all():
            continue
        dark = rng.random() < 0.35
        hi, mid = (G[2], G[1]) if dark else (G[3], G[2])
        for dx, ht in ((-1, 2), (0, 3), (1, 2)):
            for k in range(ht):
                img[y - k, x + dx] = hi if k == ht - 1 else mid
        img[y + 1, x - 1:x + 2] = G[0]                         # bong chan
    for _ in range(int(wp * hp / 1400)):
        y, x = int(rng.integers(2, hp - 3)), int(rng.integers(2, wp - 3))
        if not grass[y - 2:y + 3, x - 2:x + 3].all():
            continue
        col = A[int(rng.integers(0, len(A)))]
        img[y - 1, x] = img[y + 1, x] = img[y, x - 1] = img[y, x + 1] = col
        img[y, x] = A[1] if not (col == A[1]).all() else A[2]
        img[y + 2, x] = G[0]
    return Image.fromarray(img)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    S, pad, lab = 2, 12, 22
    names = list(THEMES)
    cols = 2
    rows = (len(names) + 1) // cols
    sheet = Image.new("RGB", (cols * (W * T * S + pad) + pad, rows * (H * T * S + pad + lab) + pad), (18, 14, 24))
    dr = ImageDraw.Draw(sheet)
    for i, nm in enumerate(names):
        im = render(THEMES[nm])
        im.save(os.path.join(OUT, f"map_{nm}.png"))
        x = pad + (i % cols) * (W * T * S + pad); y = pad + (i // cols) * (H * T * S + pad + lab)
        dr.text((x, y + 4), nm, fill=(240, 230, 210))
        sheet.paste(im.resize((W * T * S, H * T * S), Image.NEAREST), (x, y + lab))
    sheet.save(os.path.join(OUT, "tiles_options.png"))
    print("ok", len(names), "theme ->", os.path.join(OUT, "tiles_options.png"))
