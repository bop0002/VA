"""v2 - cac kieu xu ly toon cho player + enemy de chon (phan 1). Lay sprite tu export/ (ban v1 da duyet).

T0 goc | T1 ruc mau | T2 ruc + vien den + highlight vien tren | T3 sel-out (vien mau toi theo khoi) | T4 ruc + vien day 2px
Dung: python Tools/artpipe/v2/experiments/chars_v2.py  -> v2/out/chars_options.png
"""
import colorsys, glob, os
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # = v2/ (script nam o v2/experiments/)
import sys; sys.path.insert(0, HERE)
EXPORT = os.path.join(HERE, "..", "_archive_v1", "export")
OUT = os.path.join(HERE, "out", "_archive")
OUTLINE = np.array([0x1a, 0x14, 0x24])
INK = np.array([0x0d, 0x09, 0x12])

SPRITES = ["Characters/player_idle"] + [f"Enemies/enemy_{n}" for n in (
    "zombie_a", "zombie_b", "skeleton", "skeleton_helmet", "ghost", "hound", "bat_0")]


def load(n):
    return np.asarray(Image.open(os.path.join(EXPORT, n + ".png")).convert("RGBA")).copy()


def is_outline(a):
    return (a[..., 3] > 0) & (np.abs(a[..., :3].astype(int) - OUTLINE).sum(-1) < 30)


def hsv_map(a, s_mul=1.4, v_mul=1.08, v_add=0.0):
    out = a.copy()
    m = (a[..., 3] > 0) & ~is_outline(a)
    for y, x in zip(*np.nonzero(m)):
        r, g, b = a[y, x, :3] / 255.0
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        s = min(1, s * s_mul); v = min(1, v * v_mul + v_add)
        out[y, x, :3] = np.array(colorsys.hsv_to_rgb(h, s, v)) * 255
    return out


def nb(m, dy, dx):
    p = np.pad(m, 1)
    return p[1 + dy:1 + dy + m.shape[0], 1 + dx:1 + dx + m.shape[1]]


def t1(a):
    return hsv_map(a)


def t2(a):
    o = hsv_map(a)
    ol = is_outline(a)
    o[ol, :3] = INK
    fill = (a[..., 3] > 0) & ~ol
    rim = fill & nb(ol, -1, 0) & ~nb(ol, 1, 0)           # o fill ngay duoi vien tren -> sang len
    for y, x in zip(*np.nonzero(rim)):
        o[y, x, :3] = np.minimum(255, o[y, x, :3].astype(int) * 1.25 + 25)
    return o


def t3(a):
    o = hsv_map(a, 1.3, 1.05)
    ol = is_outline(a)
    fill = (a[..., 3] > 0) & ~ol
    for y, x in zip(*np.nonzero(ol)):
        cols = [o[y + dy, x + dx, :3] for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1))
                if 0 <= y + dy < a.shape[0] and 0 <= x + dx < a.shape[1] and fill[y + dy, x + dx]]
        if cols:   # vien ngoai giu toi; vien trong (giua 2 khoi) lay mau khoi toi di
            base = np.mean(cols, 0)
            outer = not (nb(a[..., 3] > 0, -1, 0)[y, x] and nb(a[..., 3] > 0, 1, 0)[y, x]
                         and nb(a[..., 3] > 0, 0, -1)[y, x] and nb(a[..., 3] > 0, 0, 1)[y, x])
            o[y, x, :3] = base * (0.35 if outer else 0.5)
    return o


def t4(a):
    o = t2(a)
    solid = o[..., 3] > 0
    ring = ~solid & (nb(solid, -1, 0) | nb(solid, 1, 0) | nb(solid, 0, -1) | nb(solid, 0, 1))
    o[ring] = [*INK, 255]
    return o


TREAT = [("T0 goc", lambda a: a), ("T1 ruc", t1), ("T2 ruc+vien den+rim", t2), ("T3 sel-out", t3), ("T4 vien day 2px", t4)]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    S, cell, lab = 4, 36, 150
    bg_map = Image.open(os.path.join(OUT, "map_A_meadow.png")).convert("RGBA")
    bg2 = Image.open(os.path.join(OUT, "map_C_haunted.png")).convert("RGBA")
    Wd = lab + len(SPRITES) * cell * S
    sheet = Image.new("RGBA", (Wd, len(TREAT) * cell * S * 2 + 20), (18, 14, 24, 255))
    dr = ImageDraw.Draw(sheet)
    raw = {n: load(n) for n in SPRITES}
    for r, (tn, fn) in enumerate(TREAT):
        for half, bg in enumerate((bg_map, bg2)):
            y0 = (r * 2 + half) * cell * S + 10
            if half == 0: dr.text((8, y0 + 8), tn, fill=(240, 230, 210))
            for i, n in enumerate(SPRITES):
                yy = (60, 150)[half]; tile = bg.crop((20 + i * 40, yy, 20 + i * 40 + cell, yy + cell))
                spr = Image.fromarray(fn(raw[n]).astype(np.uint8), "RGBA")
                tile.alpha_composite(spr, ((cell - spr.width) // 2, (cell - spr.height) // 2))
                sheet.paste(tile.resize((cell * S, cell * S), Image.NEAREST), (lab + i * cell * S, y0))
            if r == 0 and half == 0:
                for nm, fn2 in TREAT[1:]:
                    pass
        for nm, f in [(tn, fn)]:
            spr = Image.fromarray(f(raw["Characters/player_idle"]).astype(np.uint8), "RGBA")
            spr.save(os.path.join(OUT, f"player_{tn.split()[0]}.png"))
    sheet.save(os.path.join(OUT, "chars_options.png"))
    print("ok", os.path.join(OUT, "chars_options.png"))
