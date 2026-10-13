"""v2 - dua player/enemy (export_soft/A_zombie_to) ve phong cach phang 2 tong cua map C_graveyard + prop ban 2.

2 phuong an (ap cho moi frame idle/walk, dung nguyen bo frame cu):
  A_gom2tong : giu hinh khoi goc; moi chat lieu (nhom mau cung hue) gom con 2 tong (sang/toi) + 1 diem sang neu co;
               xoa pixel le; vien den -> mau vien chung OL cua prop.
  B_tolaikhoi: nhu A nhung to lai bong kieu prop: than = tong sang, bong 1px o mep duoi/phai cua tung mang chat lieu.
Dung: python Tools/artpipe/v2/experiments/chars_flat.py -> v2/export_soft/graveyard_chars/<pa>/... + v2/out/chars_flat_preview.png
"""
import os, colorsys, glob
import numpy as np
from PIL import Image

import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))   # = v2/
import graveyard_props as gp

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # = v2/ (script nam o v2/experiments/)
import sys; sys.path.insert(0, HERE)
SRC = os.path.join(HERE, "export_soft", "A_zombie_to")
DST = os.path.join(HERE, "export_soft", "_archive", "graveyard_chars")
OUT = os.path.join(HERE, "out", "_archive")
OL = gp.OL


def hls(c):
    return colorsys.rgb_to_hls(*[v / 255 for v in c])


def materials(colors):
    """Gom mau thanh chat lieu: cung hue (+-35 do) va do bao hoa gan nhau. Mau rat toi = vien."""
    groups, line = [], []
    for c in colors:
        h, l, s = hls(c)
        if l < 0.1: line.append(c); continue
        for g in groups:
            h2, _, s2 = hls(g[0])
            dh = min(abs(h - h2), 1 - abs(h - h2)) * 360
            if (dh < 35 or s < 0.08 and s2 < 0.08) and abs(s - s2) < 0.15:
                g.append(c); break
        else:
            groups.append([c])
    return groups, line


def tone_map(img_list):
    """Bang doi mau chung cho moi frame: mau -> (chat lieu id, mau dich, la_toi)."""
    cnt = {}
    for a in img_list:
        for c in map(tuple, a[a[..., 3] > 0][:, :3]): cnt[c] = cnt.get(c, 0) + 1
    groups, line = materials(sorted(cnt, key=lambda c: -cnt[c]))
    mp = {c: (-1, tuple(OL), True) for c in line}
    for gi, g in enumerate(groups):
        if len(g) == 1:
            mp[g[0]] = (gi, g[0], False); continue
        g = sorted(g, key=lambda c: hls(c)[1])
        ls = np.array([hls(c)[1] for c in g])
        cut = int(np.argmax(np.diff(ls))) + 1 if len(g) > 2 else 1          # tach o khoang sang lon nhat
        dark, light = g[:cut], g[cut:]
        hi = None
        if len(light) > 1 and ls[-1] - ls[-2] > 0.05 and cnt[g[-1]] < 0.25 * sum(cnt[c] for c in light):
            hi = g[-1]; light = light[:-1]                                    # diem sang rieng, it pixel
        dc = max(dark, key=lambda c: cnt[c]); lc = max(light, key=lambda c: cnt[c])
        for c in dark: mp[c] = (gi, dc, True)
        for c in light: mp[c] = (gi, lc, False)
        if hi: mp[hi] = (gi, hi, False)
    return mp, groups


def apply(a, mp, reshade):
    h, w = a.shape[:2]
    op = a[..., 3] > 0
    mat = np.full((h, w), -2, int); out = a.copy()
    for y, x in zip(*np.nonzero(op)):
        gi, col, _ = mp[tuple(a[y, x, :3])]
        mat[y, x] = gi; out[y, x, :3] = col
    # xoa pixel le: 4 lang gieng cung chat lieu deu cung 1 mau khac -> theo lang gieng
    o2 = out.copy()
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            if mat[y, x] < 0: continue
            nb = [(y + dy, x + dx) for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1))]
            same = [tuple(out[p][:3]) for p in nb if mat[p] == mat[y, x]]
            if len(same) >= 3 and len(set(same)) == 1 and same[0] != tuple(out[y, x, :3]):
                o2[y, x, :3] = same[0]
    out = o2
    if reshade:
        tones = {}
        for c, (gi, col, dk) in mp.items():
            if gi >= 0: tones.setdefault(gi, {})["d" if dk else "l"] = col
        for gi, t in tones.items():
            if "d" not in t or "l" not in t: continue
            m = mat == gi
            sh = lambda dy, dx: np.roll(np.roll(m, dy, 0), dx, 1)
            edge = m & (~sh(-1, 0) | ~sh(0, -1))                         # mep duoi / phai cua mang
            fill = m & ~edge
            keep_hi = np.array([[tuple(out[y, x, :3]) not in (t["d"], t["l"]) for x in range(w)] for y in range(h)])
            out[fill & ~keep_hi, :3] = t["l"]; out[edge & ~keep_hi, :3] = t["d"]
    return out


def preview(sets):
    """Moi phuong an 1 hang: player + zombie dung tren map graveyard canh bia mo/duoc."""
    bg0 = Image.open(os.path.join(HERE, "out", "tilesheet_C_graveyard_demo.png")).convert("RGBA")
    bg0 = bg0.resize((bg0.width // 2, bg0.height // 2), Image.NEAREST).crop((0, 140, 260, 220))
    props = {k: Image.open(os.path.join(gp.EXPORT, f"{k}.png")) for k in ("tomb_round", "torch_0", "cross_stone")}
    rows = []
    for name, imgs in sets:
        bg = bg0.copy()
        bg.alpha_composite(props["tomb_round"], (10, 64 - props["tomb_round"].height))
        bg.alpha_composite(props["torch_0"], (210, 66 - props["torch_0"].height))
        bg.alpha_composite(props["cross_stone"], (230, 70 - props["cross_stone"].height))
        x = 50
        for im in imgs:
            bg.alpha_composite(im, (x, 70 - im.height)); x += 52
        rows.append(bg)
    big = Image.new("RGBA", (260, 80 * len(rows)))
    for i, r in enumerate(rows): big.paste(r, (0, i * 80))
    gp.gy.save(big.resize((big.width * 4, big.height * 4), Image.NEAREST), os.path.join(OUT, "chars_flat_preview.png"))


if __name__ == "__main__":
    files = sorted(glob.glob(os.path.join(SRC, "*", "*.png")))
    by_char = {}
    for f in files:
        key = os.path.basename(f).rsplit("_", 1)[0].replace("_walk", "")
        by_char.setdefault(key, []).append(f)
    sets = [("goc", [])]
    res = {"A_gom2tong": [], "B_tolaikhoi": []}
    for key, fs in by_char.items():
        arrs = [np.asarray(Image.open(f).convert("RGBA")) for f in fs]
        mp, groups = tone_map(arrs)
        print(key, "chat lieu:", ["/".join("%02x%02x%02x" % c for c in g) for g in groups])
        idle = [i for i, f in enumerate(fs) if f.endswith("_idle.png")][0]
        sets[0][1].append(Image.fromarray(arrs[idle]).crop(Image.fromarray(arrs[idle]).getbbox()))
        for pa, rs in (("A_gom2tong", False), ("B_tolaikhoi", True)):
            for f, a in zip(fs, arrs):
                o = apply(a, mp, rs)
                d = os.path.join(DST, pa, os.path.basename(os.path.dirname(f)))
                os.makedirs(d, exist_ok=True)
                gp.gy.save(Image.fromarray(o, "RGBA"), os.path.join(d, os.path.basename(f)))
                if f == fs[idle]:
                    im = Image.fromarray(o, "RGBA"); res[pa].append(im.crop(im.getbbox()))
    preview(sets + list(res.items()))
    print("ok ->", DST)
