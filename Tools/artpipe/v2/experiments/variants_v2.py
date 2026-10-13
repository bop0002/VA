"""v2 - bien the mau tu thiet ke cu (da ap T2: ruc + vien den + rim). Giu nguyen dang, chi doi mau theo dai hue.

Moi bien the = danh sach (hue_lo, hue_hi, hue_moi | None, s_mul, v_mul): pixel co hue trong dai [lo, hi) (do)
va do bao hoa > 0.12 duoc doi sang hue_moi (giu chenh lech hue tuong doi), nhan s/v.
Dung: python Tools/artpipe/v2/experiments/variants_v2.py  -> v2/out/variants_options.png + v2/out/variants/<sprite>_v<k>.png
"""
import colorsys, os
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # = v2/ (script nam o v2/experiments/)
import sys; sys.path.insert(0, HERE)
SRC = os.path.join(HERE, "out", "_archive", "sprites_T2")
OUT = os.path.join(HERE, "out", "_archive")

HOOD, SCARF = (200, 310), (335, 375)          # 335..375 = vong qua 0 (do), tranh da (hue ~20-30)
VARIANTS = {
    "player_idle": [
        ("goc", []),
        ("ngoc+vang", [(*HOOD, 178, 1.0, 1.05), (*SCARF, 45, 1.0, 1.15)]),
        ("do+vang", [(*HOOD, 352, 0.9, 1.0), (*SCARF, 48, 1.0, 1.15)]),
        ("rung+do", [(*HOOD, 135, 0.8, 1.0), ]),
        ("nau+lam", [(*HOOD, 28, 0.7, 1.0), (*SCARF, 205, 1.0, 1.05)]),
    ],
    "enemy_zombie_a": [
        ("goc", []),
        ("xam lam", [(40, 120, 195, 0.6, 1.0)]),
        ("tim", [(40, 120, 285, 0.7, 1.0)]),
        ("xanh doc", [(40, 120, 95, 1.4, 1.1), (140, 200, 290, 1.0, 1.0)]),
    ],
    "enemy_zombie_b": [
        ("goc", []),
        ("xam lam", [(40, 120, 195, 0.6, 1.0)]),
        ("tim", [(40, 120, 285, 0.7, 1.0)]),
        ("xanh doc", [(40, 120, 95, 1.4, 1.1)]),
    ],
    "enemy_skeleton": [
        ("goc", []),
        ("xuong cu", [(15, 70, 32, 1.8, 0.85)]),
        ("bang", [(15, 70, 200, 1.6, 1.0)]),
        ("nguyen rua", [(15, 70, 110, 2.0, 0.95)]),
    ],
    "enemy_skeleton_helmet": [
        ("goc", []),
        ("mu sat", [(340, 28, 220, 0.25, 1.25)]),
        ("mu vang", [(340, 28, 45, 1.3, 1.25)]),
        ("bang", [(15, 70, 200, 1.6, 1.0)]),
    ],
    "enemy_ghost": [
        ("goc", []),
        ("xanh la", [(180, 280, 135, 1.6, 1.0)]),
        ("hong", [(180, 280, 320, 1.4, 1.0)]),
        ("tim", [(180, 280, 272, 1.8, 1.0)]),
    ],
    "enemy_hound": [
        ("goc", []),
        ("nau", [(200, 300, 25, 1.0, 1.15)]),
        ("xam", [(200, 300, 220, 0.25, 1.15)]),
        ("do sam", [(200, 300, 350, 1.2, 1.1)]),
    ],
    "enemy_bat_0": [
        ("goc", []),
        ("do mau", [(220, 300, 352, 1.0, 1.05)]),
        ("xanh doc", [(220, 300, 120, 0.9, 1.05)]),
        ("nau", [(220, 300, 25, 0.8, 1.1)]),
    ],
}


def in_band(h, lo, hi):
    return lo <= h < hi or lo <= h + 360 < hi or (lo > hi and (h >= lo or h < hi))


def recolor(a, rules):
    o = a.copy()
    for y, x in zip(*np.nonzero(a[..., 3] > 0)):
        r, g, b = a[y, x, :3] / 255.0
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        hd = h * 360
        if s < 0.12 or v < 0.12:
            continue
        for lo, hi, nh, sm, vm in rules:
            if in_band(hd, lo, hi):
                hi_ = hi + 360 if hi < lo else hi
                rel = (hd if hd >= lo else hd + 360) - (lo + hi_) / 2
                h2 = ((nh + rel * 0.5) % 360) / 360
                o[y, x, :3] = np.array(colorsys.hsv_to_rgb(h2, min(1, s * sm), min(1, v * vm))) * 255
                break
    return o


if __name__ == "__main__":
    os.makedirs(os.path.join(OUT, "variants"), exist_ok=True)
    bg = Image.open(os.path.join(HERE, "out", "terrain_A_meadow_demo.png")).convert("RGBA")
    S, cell, lab = 4, 34, 170
    ncol = max(len(v) for v in VARIANTS.values())
    sheet = Image.new("RGBA", (lab + ncol * cell * S, len(VARIANTS) * (cell * S + 18) + 8), (18, 14, 24, 255))
    dr = ImageDraw.Draw(sheet)
    for r, (name, vs) in enumerate(VARIANTS.items()):
        a = np.asarray(Image.open(os.path.join(SRC, name + ".png")).convert("RGBA")).copy()
        y0 = 8 + r * (cell * S + 18)
        dr.text((8, y0 + cell * S // 2), name, fill=(240, 230, 210))
        for k, (vn, rules) in enumerate(vs):
            spr = Image.fromarray(recolor(a, rules).astype(np.uint8), "RGBA")
            spr.save(os.path.join(OUT, "variants", f"{name}_v{k}.png"))
            t = bg.crop((4, 4 + 32 * (r % 2), 4 + cell, 4 + 32 * (r % 2) + cell))
            t.alpha_composite(spr, ((cell - spr.width) // 2, (cell - spr.height) // 2))
            x0 = lab + k * cell * S
            sheet.paste(t.resize((cell * S, cell * S), Image.NEAREST), (x0, y0 + 14))
            dr.text((x0 + 4, y0), f"v{k} {vn}", fill=(200, 190, 230))
    sheet.save(os.path.join(OUT, "variants_options.png"))
    print("ok", os.path.join(OUT, "variants_options.png"))
