"""v2 - aura (Garlick) tu anh Gemini nen TOI (vong sang xanh tren nen den, khong phai nen magenta nhu build_fx).

Anh phat sang -> tach bang "unblend": anh = nen + anh_sang*alpha. Lay phan sang hon nen lam alpha + mau,
ep elip ve hinh tron (hitbox la circle), thu nho ve N x N (vong ~8px nguon -> 1px), roi luong tu alpha
thanh vai bac + palette xanh vai mau cho dung chat pixel. Lap lanh (sparkle) dat lai thanh cham sang 1px.
Mac dinh N=64 -> o PPU 32 = duong kinh 2 unit = dung _baseRadius 1 cua Garlick (truoc: 60px, lech 0.06u).
Dung: python Tools/artpipe/v2/experiments/build_aura.py -> export_soft/Projectiles/aura(_alpha).png + aura_variants/ + out/aura_preview.png
"""
import os
import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # = v2/ (script nam o v2/experiments/)
import sys; sys.path.insert(0, HERE)
SRC = os.path.join(HERE, "..", "inbox", "V2", "aura.png")
EXPORT = os.path.join(HERE, "export_soft", "_archive", "aura_extract")   # KHONG ghi de aura chinh
OUT = os.path.join(HERE, "out", "_archive")
ALPHA_LV = np.array([0, 50, 90, 140, 200, 255])        # bac alpha cho phep


def load():
    a = np.asarray(Image.open(SRC).convert("RGB")).astype(float)
    bg = np.median(np.concatenate([a[:20].reshape(-1, 3), a[-20:, :800].reshape(-1, 3)]), 0)
    return a, bg


def ellipse_box(a):
    """Bien elip = vung xanh ro (G>R) sau khi lam mo, bo cac manh nho (sparkle roi rac)."""
    b = np.asarray(Image.fromarray(a.astype(np.uint8)).filter(ImageFilter.BoxBlur(8))).astype(int)
    m = (b[..., 1] - b[..., 0]) > 18
    rows, cols = np.nonzero(m.sum(1) > 25)[0], np.nonzero(m.sum(0) > 25)[0]
    return cols.min(), rows.min(), cols.max() + 1, rows.max() + 1


def unblend(a, bg, ref):
    """alpha = do sang vuot nen / ref; mau = nen + phan sang / alpha (mau 'that' cua vong)."""
    e = np.clip(a - bg, 0, None)
    al = np.clip(e.max(-1) / ref, 0, 1)
    col = np.clip(bg + e / np.maximum(al, 1e-3)[..., None], 0, 255)
    return col, al


def sparkles(a, box, n):
    """Cham lap lanh: rat sang + it bao hoa (trang xanh), nam trong/sat elip -> toa do pixel dich."""
    x0, y0, x1, y1 = box
    lum = a.mean(-1); sat = a.max(-1) - a.min(-1)
    m = (lum > 150) & (sat < 90)
    cx, cy, rx, ry = (x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2, (y1 - y0) / 2
    pts = set()
    for y, x in zip(*np.nonzero(m)):
        if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 < 1.1:
            pts.add((int((y - y0) / (y1 - y0) * n), int((x - x0) / (x1 - x0) * n)))
    return pts


def build(n=64, colors=6, soft=1.0, lo=0.0, hi=1.0, glow=1.0, warp=None, pal=None, sparks=True, ret_pal=False):
    """lo/hi: keo alpha (A-lo)/(hi-lo) -> vong ro hon, quang mo bi day xuong; glow: nhan do sang mau.
    warp(col, al) -> (col, al): bien doi anh do phan giai goc truoc khi thu nho (build_aura_anim: gon song).
    pal: palette co dinh (giu mau giong nhau giua cac frame animation)."""
    a, bg = load()
    box = x0, y0, x1, y1 = ellipse_box(a)
    ref = np.percentile((a - bg).max(-1)[y0:y1, x0:x1], 99)
    col, al = unblend(a[y0:y1, x0:x1], bg, ref)
    if warp is not None: col, al = warp(col, al)
    # thu nho tren gia tri premultiplied (BOX = trung binh dung dien tich) -> vong mong khong bi mat
    pm = np.dstack([col * al[..., None], al * 255]).astype(np.float32)
    small = np.dstack([np.asarray(Image.fromarray(pm[..., c], "F").resize((n, n), Image.BOX)) for c in range(4)])
    A = small[..., 3] / 255
    C = small[..., :3] / np.maximum(A, 1e-3)[..., None]
    # tang tuong phan alpha: vong (dinh cuc bo) len cao, quang nen giu thap
    build.last_norm = np.percentile(A, 99.5) if build.norm is None else build.norm
    A = np.clip(A / build.last_norm, 0, 1)
    A = np.clip((A - lo) / (hi - lo), 0, 1) ** 0.8 * soft
    C = C * glow
    yy, xx = np.mgrid[0:n, 0:n]
    r = np.hypot(xx + 0.5 - n / 2, yy + 0.5 - n / 2) / (n / 2)
    A[r > 1] = 0                                                    # cat tron dung ban kinh
    Aq = ALPHA_LV[np.abs(A[..., None] * 255 - ALPHA_LV).argmin(-1)]
    # palette: luong tu mau tren cac pixel con lai
    on = Aq > 0
    if pal is None:
        q = Image.fromarray(np.clip(C[on], 0, 255).astype(np.uint8)[None]).quantize(colors, method=Image.MEDIANCUT)
        pal = np.array(q.getpalette()[:colors * 3]).reshape(-1, 3)
    img = np.zeros((n, n, 4), np.uint8)
    img[on, :3] = pal[((C[on][:, None, :] - pal[None]) ** 2).sum(-1).argmin(1)]
    img[..., 3] = Aq
    # vong sang nhat (alpha toi da) dung mau sang nhat cua palette cho net vong noi bat
    hi = pal[pal.sum(1).argmax()]
    img[Aq == 255, :3] = hi
    for j, i in (sparkles(a, box, n) if sparks else ()):
        if 0 <= j < n and 0 <= i < n and r[j, i] <= 1:
            img[j, i] = (225, 255, 240, 255)
    return (img, pal) if ret_pal else img


build.norm = None         # None = tu chuan hoa; build_aura_anim dat = last_norm cua frame tinh -> moi frame chung 1 thang alpha


def stage(img, scale=6, bg=(45, 52, 50)):
    """Xem tren nen dat toi + player o giua."""
    n = img.shape[0]
    base = Image.new("RGBA", (n + 16, n + 16), bg + (255,))
    base.alpha_composite(Image.fromarray(img, "RGBA"), (8, 8))
    p = Image.open(os.path.join(HERE, "export_soft", "player_v3", "player_idle.png")).convert("RGBA")
    base.alpha_composite(p, (8 + n // 2 - 24, 8 + n // 2 - 30))
    return base.resize((base.width * scale, base.height * scale), Image.NEAREST)


if __name__ == "__main__":
    os.makedirs(EXPORT, exist_ok=True)
    variants = {"A_mem": build(64, soft=0.8), "B_ro": build(64, lo=0.18, hi=0.75, glow=1.15),
                "C_sang": build(64, lo=0.25, hi=0.7, glow=1.35)}
    vdir = os.path.join(EXPORT, "aura_variants")
    os.makedirs(vdir, exist_ok=True)
    for k, v in variants.items():
        Image.fromarray(v, "RGBA").save(os.path.join(vdir, f"aura_{k}.png"))
    # ban chinh (ten cu -> thay PNG trong Unity giu nguyen .meta/reference): aura_alpha = B (prefab Garlick dung), aura = C
    Image.fromarray(variants["B_ro"], "RGBA").save(os.path.join(EXPORT, "aura_alpha.png"))
    Image.fromarray(variants["C_sang"], "RGBA").save(os.path.join(EXPORT, "aura.png"))
    sheets = [stage(v) for v in variants.values()]
    tile = os.path.join(HERE, "out", "tilesheet_C_graveyard.png")
    if os.path.exists(tile):                                       # them 1 o tren nen graveyard
        g = Image.open(tile).convert("RGBA").crop((5 * 32, 0, 6 * 32, 32)).resize((32, 32))
        ground = Image.new("RGBA", (80, 80))
        for y in range(0, 80, 32):
            for x in range(0, 80, 32): ground.paste(g, (x, y))
        p = Image.open(os.path.join(HERE, "export_soft", "player_v3", "player_idle.png")).convert("RGBA")
        for v in variants.values():
            gd = ground.copy()
            gd.alpha_composite(Image.fromarray(v, "RGBA"), (8, 8)); gd.alpha_composite(p, (16, 10))
            sheets.append(gd.resize((480, 480), Image.NEAREST))
    k = len(variants)                                              # hang 1: nen toi, hang 2: nen graveyard
    W = sum(s.width for s in sheets[:k]) + 12 * (k - 1)
    cmp_ = Image.new("RGBA", (W, 480 * 2 + 12), (10, 10, 14, 255))
    for i, s in enumerate(sheets): cmp_.paste(s, ((i % k) * 492, (i // k) * 492))
    cmp_.save(os.path.join(OUT, "aura_preview.png"))
    print("ok ->", EXPORT)
