"""Prop/decor ve tay bang code (Gemini ve sai goc nhin hoac qua vun o 16px).

- prop_fence: rao sat NGANG rong dung 32px, song cach deu 8px -> dat sat nhau thanh day lien (ray chay qua mep).
- prop_grave: huyet mo chinh dien (thay ban isometric cua Gemini), u dat phia sau.
- decor_bones / decor_leaves / decor_puddle: thay ban Gemini bi vun / toi / sai mau o 16px.
Mau lay tu ban Gemini (inbox/props*.jpg), chi dung palette vaclone.hex.
"""
import os, sys
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import artpipe

PAL = artpipe.load_palette()
HEX = [l.strip() for l in open(artpipe.PALETTE_FILE) if l.strip()]
C = {
    "O": "1a1424", "K": "0d0912", "D": "2a2138",
    "i": "3a324e", "I": "4c4468", "h": "605b7c",                 # sat
    "r": "5e3a2a", "R": "8a5a3a",                                # gi set / dat
    "m": "2e4a2a", "M": "4f7a3a",                                # reu
    "w": "3a2420", "d": "5e3a2a", "e": "8a5a3a",                 # dat
    "1": "887f70", "2": "b2a791", "3": "cfc6af", "4": "ece4c2",  # xuong
    "l": "6b3a2e", "L": "b0684a",                                # la kho
    "q": "1f2d33", "Q": "2f414d", "W": "3e5a5a", "s": "a8bbde",  # nuoc dem
}
IDX = {k: HEX.index(v) for k, v in C.items()}


def canvas(h, w):
    return np.full((h, w), -1, np.int32)


def px(g, y, x, k):
    if 0 <= y < g.shape[0] and 0 <= x < g.shape[1]:
        g[y, x] = IDX[k]


def ellipse(g, cy, cx, ry, rx, pick):
    for y in range(g.shape[0]):
        for x in range(g.shape[1]):
            v = ((y - cy) / ry) ** 2 + ((x - cx) / rx) ** 2
            if v <= 1:
                k = pick(y, x, v)
                if k: px(g, y, x, k)


def save(g, name, frame=None, outline=True):
    if outline:
        g = artpipe.enforce_outline(g, PAL)
    spr = artpipe.to_rgba(g, PAL)
    spr = spr.crop(spr.getbbox())
    if frame:
        fw = max(frame[0], spr.width); fh = max(frame[1], spr.height + 1)
        spr = artpipe.place_in_frame(spr, (fw, fh))
    spr.save(os.path.join(artpipe.OUT_DIR, name + ".png"))
    return spr


def fence():
    """32x26. Khong dung enforce_outline (se ve vien o 2 mep trai/phai, lam dut ray khi noi day)."""
    rng = np.random.default_rng(2)
    g = canvas(26, 32)
    for top in (7, 17):                                  # 2 thanh ray chay het chieu ngang
        for x in range(32):
            px(g, top, x, "O"); px(g, top + 1, x, "I"); px(g, top + 2, x, "i"); px(g, top + 3, x, "O")
    for x0 in (3, 11, 19, 27):                           # 4 song, cach 8px -> noi day van deu
        for y in range(4, 24):
            px(g, y, x0 - 1, "O"); px(g, y, x0, "I" if y < 12 else "i"); px(g, y, x0 + 1, "D"); px(g, y, x0 + 2, "O")
        for y, row in enumerate(("..OO..", ".OhIO.", "OhIiDO", ".OiDO.")):   # mui giao
            for j, k in enumerate(row):
                if k != ".": px(g, y, x0 - 2 + j, k)
        for y in range(24, 26):
            px(g, y, x0 - 1, "O"); px(g, y, x0, "O"); px(g, y, x0 + 1, "O"); px(g, y, x0 + 2, "O")
        for _ in range(3):                               # gi set
            y = int(rng.integers(6, 23)); px(g, y, x0 + int(rng.integers(0, 2)), "r" if rng.random() < .6 else "R")
        for dx in (-2, 3):                               # reu o chan song
            if rng.random() < 0.7:
                px(g, 23, x0 + dx, "M"); px(g, 24, x0 + dx, "m"); px(g, 22, x0 + dx, "m")
    return save(g, "prop_fence", (32, 32), outline=False)


def grave():
    """Nhin tu tren xuong 3/4: ho det (rong > cao), thay vach sau; u dat lech phai phia sau nhu ban Gemini."""
    g = canvas(20, 32)
    ellipse(g, 7, 23, 5, 8, lambda y, x, v: "e" if (y < 5 and v < .7) else ("d" if y < 9 else "w"))
    for y, x in ((3, 21), (5, 26), (8, 29), (4, 24)):
        px(g, y, x, "R")
    for y in range(7, 19):
        for x in range(2, 23):
            if y == 7: k = "e"                           # mieng ho phia sau (sang)
            elif y == 18 or x in (2, 22): k = "d"        # mieng ho truoc / 2 ben
            elif y <= 10: k = "d" if y == 8 else "w"     # vach sau thay duoc
            else: k = "K" if y > 12 else "D"             # long ho toi
            px(g, y, x, k)
    return save(g, "prop_grave", (32, 32))


def bones():
    g = canvas(16, 16)

    def stamp(y, x):
        px(g, y - 1, x, "4"); px(g, y, x, "3"); px(g, y, x - 1, "3"); px(g, y, x + 1, "3"); px(g, y + 1, x, "1")

    def bone(p0, p1):
        n = int(max(abs(p1[0] - p0[0]), abs(p1[1] - p0[1])))
        for t in np.linspace(0, 1, n + 1):
            stamp(round(p0[0] + (p1[0] - p0[0]) * t), round(p0[1] + (p1[1] - p0[1]) * t))
        for ey, ex in (p0, p1):                          # nut xuong 2 bau
            for dy in (-1, 1):
                stamp(ey + dy, ex - 1); stamp(ey + dy, ex + 1)
    bone((4, 3), (12, 12))
    bone((12, 3), (4, 12))
    return save(g, "decor_bones", (16, 16))


def leaves():
    rng = np.random.default_rng(5)
    g = canvas(14, 18)

    def pick(y, x, v):
        if y < 6 and rng.random() < .25: return "e"     # dinh hoi sang, khong cam ruc
        return ["l", "d", "d", "w", "l"][int(rng.integers(0, 5))] if v < .8 else ("w" if y > 8 else "l")
    ellipse(g, 9, 9, 4.5, 7.5, pick)
    for y, x, k in ((4, 7, "e"), (4, 8, "l"), (5, 12, "e"), (3, 10, "L")):   # la noi tren dinh
        px(g, y, x, k)
    return save(g, "decor_leaves", (16, 16))


def puddle():
    g = canvas(11, 22)
    ellipse(g, 5, 10, 4, 9.5, lambda y, x, v: "W" if (v > .7 and y < 5) else ("Q" if v > .45 else "q"))
    ellipse(g, 8, 19, 1.5, 2.2, lambda y, x, v: "Q")    # giot nho
    for y, x in ((4, 6), (4, 7), (6, 13)):
        px(g, y, x, "s")                                 # anh phan chieu
    return save(g, "decor_puddle", (16, 16))


if __name__ == "__main__":
    os.makedirs(artpipe.OUT_DIR, exist_ok=True)
    items = [fence(), grave(), bones(), leaves(), puddle()]
    # preview: 3 doan rao noi nhau + cac mon khac tren nen co
    bg = Image.open(os.path.join(artpipe.OUT_DIR, "tile_grass_0.png")).convert("RGBA")
    W = 32 * 3 + 32 + 16 * 3 + 40
    sheet = Image.new("RGBA", (W, 40))
    for x in range(0, W, 32):
        for y in range(0, 40, 32): sheet.paste(bg, (x, y))
    for i in range(3): sheet.alpha_composite(items[0], (i * 32, 4))
    x = 32 * 3 + 4
    for it in items[1:]:
        sheet.alpha_composite(it, (x, 40 - it.height - 2)); x += it.width + 4
    sheet.resize((W * 6, 240), Image.NEAREST).save(os.path.join(artpipe.OUT_DIR, "..", "props_handmade.png"))
    print("ok prop_fence, prop_grave, decor_bones, decor_leaves, decor_puddle")
