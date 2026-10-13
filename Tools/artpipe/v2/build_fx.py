"""v2 - tach projectile / aura tu anh Gemini (phong cach chibi mem) -> export_soft/Projectiles/.

Khac extract_soft.extract: giu MOI manh roi gan vat chinh (vet duoi, manh bang vun), khong chi manh lon nhat.
Moi projectile huong sang PHAI (Unity xoay theo huong bay). Aura (nguon nen toi) -> build_aura.py.
Dung: python Tools/artpipe/v2/build_fx.py -> v2/export_soft/Projectiles/*.png + v2/out/soft/fx_*.png
"""
import os
import numpy as np
from PIL import Image

import extract_soft as es
from extract_soft import artpipe

HERE = os.path.dirname(os.path.abspath(__file__))
INBOX = os.path.join(HERE, "..", "inbox", "V2")
EXPORT = os.path.join(HERE, "export_soft", "Projectiles")
OUT = es.OUT
OUTLINE = (30, 12, 30)

# (anh nguon, ten xuat, so mau palette)
SOURCES = [
    ("iceshardv2(replace knife).png", "proj_iceshard", 16),
    ("iceshard(replace knife).png", "proj_iceshard_b", 16),
    ("magicwandprojectile.png", "proj_wand", 14),
    ("enemyprojectile.png", "proj_enemy", 14),
]


def object_mask(rgb):
    """Nen magenta -> mask; giu manh lon nhat + cac manh nho nam gan no (<= 1/3 kich thuoc vat)."""
    fg = artpipe.chroma_mask(rgb)
    comps, labels = artpipe.components(fg, 30)
    main = max(comps, key=lambda c: c[2])
    x0, y0, x1, y1 = main[1]
    reach = max(x1 - x0, y1 - y0) // 3
    keep = np.zeros_like(fg)
    for lab, (a, b, c, d), n in comps:
        if a < x1 + reach and c > x0 - reach and b < y1 + reach and d > y0 - reach:
            keep |= labels == lab
    ys, xs = np.nonzero(keep)
    return keep, (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)


def extract(path, name, colors):
    rgb = np.asarray(Image.open(path).convert("RGB"))
    fg, (x0, y0, x1, y1) = object_mask(rgb)
    s = es_grid(rgb[max(0, y0 - 20):y1 + 20, max(0, x0 - 20):x1 + 20])
    _, _, ox, oy = s
    ox += max(0, x0 - 20); oy += max(0, y0 - 20); s = s[1]
    gx0 = ox + np.floor((x0 - ox) / s) * s; gy0 = oy + np.floor((y0 - oy) / s) * s
    nw = int(np.ceil((x1 - gx0) / s)); nh = int(np.ceil((y1 - gy0) / s))
    q = Image.fromarray(rgb[y0:y1, x0:x1]).quantize(colors, method=Image.MEDIANCUT)
    pal = np.array(q.getpalette()[:colors * 3]).reshape(-1, 3)
    img = np.zeros((nh, nw, 4), np.uint8)
    m = int(s * 0.25)
    for j in range(nh):
        for i in range(nw):
            ya, xa = int(gy0 + j * s), int(gx0 + i * s)
            yb, xb = int(gy0 + (j + 1) * s), int(gx0 + (i + 1) * s)
            cm = fg[ya + m:yb - m, xa + m:xb - m]
            if cm.size == 0 or cm.mean() < 0.5:
                continue
            px = rgb[ya + m:yb - m, xa + m:xb - m][cm].astype(int)
            d = ((px[:, None, :] - pal[None]) ** 2).sum(-1).argmin(1)
            img[j, i, :3] = pal[np.bincount(d, minlength=len(pal)).argmax()]; img[j, i, 3] = 255
    # vien toi bi nhiem mau nen magenta (vd 133,10,135) -> ve lai mau vien chung voi zombie/tile
    c = img[..., :3].astype(int)
    tinted = (img[..., 3] > 0) & (c.sum(-1) < 300) & (np.minimum(c[..., 0], c[..., 2]) - c[..., 1] > 25)
    img[tinted, :3] = OUTLINE
    spr = Image.fromarray(img, "RGBA")
    spr = spr.crop(spr.getbbox())
    print(f"ok {name}: grid {s:.2f}px -> {spr.width}x{spr.height}")
    return spr


def es_grid(rgb):
    """Luoi pixel gia: uoc luong tu do dai cac doan mau lien (mode = 1 o), roi detect_grid trong khoang hep
    quanh uoc luong de lay offset (vung nho -> detect_grid tu do hay bat nham boi so 3x, 4x)."""
    a = rgb.astype(int)
    runs = []
    for arr in (a, a.transpose(1, 0, 2)):
        for row in arr[::3]:
            runs += list(np.diff(np.nonzero(np.abs(np.diff(row, axis=0)).sum(-1) > 60)[0]))
    runs = np.array([r for r in runs if r >= 5])
    h = np.bincount(runs).astype(float)
    h[:-1] += h[1:] * 0.5                       # gop lan can (13 + 14 cung la 1 o ~13.5)
    est = int(h.argmax())
    return artpipe.detect_grid(rgb, smin=est - 1.5, smax=est + 2)[0]


def translucent(spr, fill_alpha=150):
    """Aura: vien toi giu dac, phan ruot ban trong suot de nhin thay dat ben duoi."""
    a = np.asarray(spr).copy()
    lum = a[..., :3].astype(int).sum(-1)
    inner = (a[..., 3] > 0) & (lum > 200)
    a[inner, 3] = fill_alpha
    return Image.fromarray(a, "RGBA")


def preview(sprs):
    """Dat len map A_meadow cung player/zombie (ti le that 32px = 1 o), x4."""
    bg = Image.open(os.path.join(HERE, "out", "tilesheet_A_meadow_demo.png")).convert("RGBA")
    bg = bg.resize((bg.width // 2, bg.height // 2), Image.NEAREST).crop((0, 0, 320, 128))
    ref = os.path.join(HERE, "export_soft", "A_zombie_to")
    player = Image.open(os.path.join(ref, "Characters", "player_idle.png"))
    zombie = Image.open(os.path.join(ref, "Enemies", "enemy_zombie_idle.png"))
    au = Image.open(os.path.join(EXPORT, "aura_alpha.png")).convert("RGBA")
    bg.alpha_composite(au, (60 - au.width // 2, 64 - au.height // 2))
    bg.alpha_composite(player, (60 - 24, 64 - 30))
    bg.alpha_composite(zombie, (250, 40))
    x = 130
    for k in ("proj_iceshard", "proj_iceshard_b", "proj_wand", "proj_enemy"):
        p = sprs[k]; bg.alpha_composite(p, (x, 30 - p.height // 2)); x += p.width + 10
    bg.resize((bg.width * 4, bg.height * 4), Image.NEAREST).save(os.path.join(OUT, "fx_preview.png"))


if __name__ == "__main__":
    os.makedirs(EXPORT, exist_ok=True)
    sprs = {}
    for src, name, colors in SOURCES:
        spr = extract(os.path.join(INBOX, src), name, colors)
        sprs[name] = spr
        spr.save(os.path.join(EXPORT, f"{name}.png"))
        spr.resize((spr.width * 8, spr.height * 8), Image.NEAREST).save(os.path.join(OUT, f"fx_{name}_x8.png"))
    preview(sprs)
    print("ok ->", EXPORT)
