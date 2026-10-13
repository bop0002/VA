"""v2 - player ban 3: mat cham tron chibi (bo long mi), 2 tay khep vao than, chop mu trum dung dua khi di.

Sua tren frame idle 48x48 (export_soft/A_zombie_to/Characters/player_idle.png):
  - mat: xoa hang tren + net mi, giu cham 2x2 (hang 21-22)
  - tay: bien dang (warp nearest) keo ban tay vao than ~2px, cot sat than giu nguyen -> khong lo lo hong
  - walk 4 frame = build_soft.walk_frames (nhac chan + nhun) + chop mu tre nhip (lech 1px)
Dung: python Tools/artpipe/v2/player_v3.py  (chi ve preview tu frame hien co; --regen-walk sinh lai walk tu idle;
     --regen-idle sinh lai ca idle tu dau). BAN GOC = Assets/_Game/Art/Characters/PlayerV3 (user sua tay 2026-10-13). -> v2/export_soft/player_v3/*.png + v2/out/player_v3_*.png/.gif
"""
import os
import numpy as np
from PIL import Image

import build_soft as bs

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "export_soft", "A_zombie_to", "Characters", "player_idle.png")
DST = os.path.join(HERE, "export_soft", "player_v3")
OUT = os.path.join(HERE, "out")
SKIN = (0xf7, 0xca, 0xa4)
HAIR = (0x8a, 0x53, 0x5a)


def eyes(a):
    """Mat goc: cot 24-25 va 31-32, hang 19-22 (hang 19 la net mi noi vao toc). Con cham 2x2 o hang 21-22."""
    a = a.copy()
    for x in (24, 25, 31, 32):
        a[20, x, :3] = SKIN
    a[19, 24, :3] = SKIN; a[19, 25, :3] = HAIR; a[19, 31, :3] = HAIR
    return a


def warp(a, field):
    """out[y, x] = a[y - dy, x - dx] (lam tron). field(yy, xx) -> (dy, dx) mang float."""
    h, w = a.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    dy, dx = field(yy, xx)
    sy = np.clip(np.round(yy - dy).astype(int), 0, h - 1)
    sx = np.clip(np.round(xx - dx).astype(int), 0, w - 1)
    return a[sy, sx]


def ramp(v, a, b):
    """0 khi v<=a, 1 khi v>=b (tuyen tinh)."""
    return np.clip((v - a) / (b - a), 0, 1)


def close_arms(a, d=2.0):
    def field(yy, xx):
        dx = np.zeros(yy.shape)
        r_rows = (yy >= 25) & (yy <= 31)
        dx -= d * ramp(xx, 35, 40) * r_rows                                   # tay phai: keo sang trai
        # tay trai + ao choang phia sau: keo sang phai, giam dan theo chieu doc (24->29 len, 34->40 xuong)
        # de mep ao co deu, khong gay bac
        l_rows = ramp(yy, 24, 29) * (1 - ramp(yy, 34, 40))
        dx += d * (1 - ramp(xx, 14, 19)) * l_rows
        return np.zeros(yy.shape), dx
    return warp(a, field)


def clean(a):
    """Xoa pixel vien toi le loi ra (chi <= 1 lang gieng 4 huong dac) - sinh ra khi warp nen silhouette."""
    a = a.copy()
    for _ in range(2):
        op = a[..., 3] > 0
        n = sum(np.roll(np.roll(op, dy, 0), dx, 1).astype(int) for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        dark = a[..., :3].astype(int).sum(-1) < 60
        a[op & dark & (n <= 1), 3] = 0
    return a


def hood_sway(a, dy, dx):
    """Chop mu (goc tren-trai) lech (dy, dx) px, giam dan ve 0 o phan mu chinh."""
    if dy == 0 and dx == 0: return a
    def field(yy, xx):
        wgt = (1 - ramp(yy, 7, 12)) * (1 - ramp(xx, 16, 22))
        return dy * wgt, dx * wgt
    return warp(a, field)


SWAY = [(0, -1), (-1, -1), (0, 0), (-1, 0)]   # theo walk [L, nhun, R, nhun]: chop mu tre nhip sau than


def walk_from(idle):
    """4 frame walk tu 1 idle. Chi don pixel le trong vung mu (y<12) - khong dong vao net user ve tay o cho khac."""
    out = []
    for f, s in zip(bs.walk_frames(idle, 4), SWAY):
        w = hood_sway(f, *s)
        c = clean(w); c[12:] = w[12:]
        out.append(c)
    return out


def build():
    a = np.asarray(Image.open(SRC).convert("RGBA")).copy()
    idle = clean(close_arms(eyes(a)))
    return idle, walk_from(idle)


def sheet(frames, scale=6, bg=(63, 82, 80, 255)):
    W = 48 * len(frames)
    im = Image.new("RGBA", (W, 48), bg)
    for i, f in enumerate(frames): im.alpha_composite(Image.fromarray(f, "RGBA"), (i * 48, 0))
    return im.resize((W * scale, 48 * scale), Image.NEAREST)


USER_IDLE = os.path.join(DST, "player_idle.png")      # user da sua tay file nay (2026-10-13) -> lam goc, KHONG ghi de


if __name__ == "__main__":
    import sys
    os.makedirs(DST, exist_ok=True)
    # 2026-10-13: ca idle + 4 walk da duoc user sua tay trong Unity (Assets/_Game/Art/Characters/PlayerV3 = ban goc,
    # da chep nguoc ve DST). Mac dinh CHI doc + ve preview; --regen-walk de sinh lai walk tu idle (ghi de walk sua tay!)
    if "--regen-idle" in sys.argv or not os.path.exists(USER_IDLE):
        idle, walk = build()
        Image.fromarray(idle, "RGBA").save(USER_IDLE)
    else:
        idle = np.asarray(Image.open(USER_IDLE).convert("RGBA")).copy()
        walk = walk_from(idle) if "--regen-walk" in sys.argv else             [np.asarray(Image.open(os.path.join(DST, f"player_walk_{i}.png")).convert("RGBA")) for i in range(4)]
    if "--regen-walk" in sys.argv or "--regen-idle" in sys.argv:
        for i, f in enumerate(walk): Image.fromarray(f, "RGBA").save(os.path.join(DST, f"player_walk_{i}.png"))
    old = np.asarray(Image.open(SRC).convert("RGBA"))
    cmp_ = Image.new("RGBA", (48 * 6 * 2 + 12, 48 * 6), (10, 10, 14, 255))
    cmp_.paste(sheet([old]), (0, 0)); cmp_.paste(sheet([idle]), (48 * 6 + 12, 0))
    cmp_.save(os.path.join(OUT, "player_v3_compare.png"))
    sheet([idle] + walk).save(os.path.join(OUT, "player_v3_frames.png"))
    g = [sheet([f], 6) for f in walk]
    g[0].save(os.path.join(OUT, "player_v3_walk.gif"), save_all=True, append_images=g[1:], duration=125, loop=0)
    print("ok ->", DST)
