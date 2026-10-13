"""v2 - thu animation aura (ban B_ro) -> GIF so sanh 3 cach:
  1_transform : 1 sprite, Unity Animation clip chinh Scale (1 -> 1.06) + alpha (0.85 -> 1) + quay cham (chop lap lanh di vong)
  2_ripple    : N frame vong lan ra ngoai (vong ngoai mo dan, vong moi hien o loi) - sprite frame-by-frame
  3_ca_hai    : ripple + nhip alpha (khong scale de hinh khop hitbox)
Ripple: warp anh goc theo ban kinh chuan hoa rn (elip -> tron): lay mau o rn - s, phan tran duoi loi
cong them 1 chu ky vong P -> lap vo han. Palette + thang alpha co dinh tu frame 0 -> khong nhap nhay mau.
Dung: python Tools/artpipe/v2/experiments/build_aura_anim.py -> export_soft/Projectiles/aura_ripple/*.png + out/aura_anim_*.gif
"""
import os
import numpy as np
from PIL import Image

import build_aura as ba

HERE = ba.HERE
OUT = ba.OUT
RIP = os.path.join(ba.EXPORT, "aura_ripple")
PARAMS = dict(lo=0.18, hi=0.75, glow=1.15)        # = ban B_ro
P = 0.185                                         # chu ky vong (do tren profile ban kinh: dinh o 0.44/0.61/0.80/0.99)
CORE = 0.26                                       # trong loi: quang sang dung yen
SCALE = 5


def ripple_warp(s):
    """s: do lech ban kinh (0..P). Tra ve ham warp cho ba.build."""
    def f(col, al):
        h, w = al.shape
        yy, xx = np.mgrid[0:h, 0:w]
        ux, uy = (xx + 0.5 - w / 2) / (w / 2), (yy + 0.5 - h / 2) / (h / 2)
        rn = np.hypot(ux, uy)
        src = rn - s
        src = np.where(src < CORE, src + P, src)
        src = np.where(rn < CORE, rn, src)
        k = src / np.maximum(rn, 1e-6)
        sx = np.clip(((ux * k + 1) * w / 2).astype(int), 0, w - 1)
        sy = np.clip(((uy * k + 1) * h / 2).astype(int), 0, h - 1)
        c2, a2 = col[sy, sx], al[sy, sx].copy()
        a2 *= np.clip((1.03 - rn) / (0.6 * P), 0, 1)            # mep ngoai: vong mo dan khi ra toi bien
        band = (rn >= CORE)
        a2[band] *= np.clip((rn[band] - CORE) / (0.5 * P) + 0.2, 0, 1)  # vong moi hien dan tu loi
        return c2, a2
    return f


def ripple_frames(n_frames):
    ba.build.norm = None
    base, pal = ba.build(64, ret_pal=True, **PARAMS)
    ba.build.norm = ba.build.last_norm                              # thang alpha chung voi frame tinh
    try:
        return [ba.build(64, warp=ripple_warp(P * i / n_frames), pal=pal, **PARAMS) for i in range(n_frames)], base
    finally:
        ba.build.norm = None


def ground(n=96):
    g = Image.open(os.path.join(HERE, "out", "tilesheet_C_graveyard.png")).convert("RGBA").crop((5 * 32, 0, 6 * 32, 32))
    im = Image.new("RGBA", (n, n))
    for y in range(0, n, 32):
        for x in range(0, n, 32): im.paste(g, (x, y))
    return im


PLAYER = Image.open(os.path.join(HERE, "export_soft", "player_v3", "player_idle.png")).convert("RGBA")


def frame(aura, scale=1.0, alpha=1.0, rot=0.0, n=96):
    """Gia lap Unity: sprite aura duoc scale/quay/nhan alpha (nearest, nhu Point filter) roi ve player len tren."""
    im = Image.fromarray(aura, "RGBA")
    if rot: im = im.rotate(rot, Image.NEAREST)
    if scale != 1.0:
        s = int(round(64 * scale)); im = im.resize((s, s), Image.NEAREST)
    if alpha != 1.0:
        a = np.asarray(im).copy(); a[..., 3] = (a[..., 3] * alpha).astype(np.uint8); im = Image.fromarray(a, "RGBA")
    bg = ground(n)
    bg.alpha_composite(im, (n // 2 - im.width // 2, n // 2 - im.height // 2))
    bg.alpha_composite(PLAYER, (n // 2 - 24, n // 2 - 30))
    return bg.resize((n * SCALE, n * SCALE), Image.NEAREST)


def save_gif(frames, name, fps):
    frames[0].save(os.path.join(OUT, name), save_all=True, append_images=frames[1:], duration=int(1000 / fps), loop=0)


if __name__ == "__main__":
    os.makedirs(RIP, exist_ok=True)
    FPS = 12
    rip, base = ripple_frames(6)
    for i, f in enumerate(rip): Image.fromarray(f, "RGBA").save(os.path.join(RIP, f"aura_ripple_{i}.png"))
    T = 72                                                           # 6 giay @12fps (quay 1 vong / 6s)
    pulse = lambda t: 0.5 - 0.5 * np.cos(2 * np.pi * t / FPS)       # 0..1, chu ky 1s
    g1 = [frame(base, scale=1 + 0.06 * pulse(t), alpha=0.85 + 0.15 * pulse(t), rot=-360 * t / T) for t in range(T)]
    # ripple 6 frame @ 8fps (~0.75s / vong) va 12fps (nhanh)
    g2 = [frame(rip[t % 6]) for t in range(24)]
    g3 = [frame(rip[(t // 1) % 6], alpha=0.85 + 0.15 * pulse(t)) for t in range(T)]
    save_gif(g1, "aura_anim_1_transform.gif", FPS)
    save_gif(g2, "aura_anim_2_ripple_8fps.gif", 8)
    save_gif(g2, "aura_anim_2_ripple_12fps.gif", 12)
    save_gif(g3, "aura_anim_3_ca_hai.gif", 8)
    # sheet tinh cac frame ripple
    sh = Image.new("RGBA", (64 * 6 + 5 * 4, 64), (45, 52, 50, 255))
    for i, f in enumerate(rip): sh.alpha_composite(Image.fromarray(f, "RGBA"), (i * 68, 0))
    sh.resize((sh.width * 4, sh.height * 4), Image.NEAREST).save(os.path.join(OUT, "aura_ripple_frames.png"))
    print("ok ->", RIP)
