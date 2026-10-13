"""v2 - dung bo sprite chibi mem de test trong game: tach anh Gemini -> frame idle + walk -> export_soft/.

Walk sinh bang code (Gemini ve walk khong dung duoc): chia chan trai/phai theo tam ban chan,
nhac 1 ben len 1px xen ke + than nhun 1px.
Dung: python Tools/artpipe/v2/build_soft.py  -> v2/export_soft/<phuong an>/ + v2/out/soft/preview_*.png/.gif
"""
import os, shutil
import numpy as np
from PIL import Image

import extract_soft as es

HERE = os.path.dirname(os.path.abspath(__file__))
INBOX = os.path.join(HERE, "..", "inbox")
EXPORT = os.path.join(HERE, "export_soft")
FRAME = 48                      # khung vuong chua sprite ~40px, pivot giua khung

# (anh nguon, ten, thu muc, so frame walk)
SOURCES = [
    ("V1/newchar.png", "player", "Characters", 4),
    ("V2/Chibi Pixel Zombie Reaching Forward.png", "enemy_zombie", "Enemies", 2),
]


def feet_split(a):
    """Cot chia 2 ban chan: khoang trong o hang day sprite, neu khong co thi lay tam."""
    solid = a[..., 3] > 0
    rows = np.nonzero(solid.any(1))[0]
    bottom = solid[rows[-1]]
    xs = np.nonzero(bottom)[0]
    gaps = [x for x in range(xs.min(), xs.max()) if not bottom[x]]
    return int(np.median(gaps)) if gaps else int(xs.mean()), rows[-1]


def lift(a, x_from, x_to, foot_h=4):
    """Nhac 1 ban chan len 1px (vung foot_h hang cuoi, cot [x_from, x_to))."""
    o = a.copy()
    solid = a[..., 3] > 0
    bottom = np.nonzero(solid.any(1))[0][-1]
    y0 = bottom - foot_h + 1
    reg = a[y0:bottom + 1, x_from:x_to].copy()
    o[y0:bottom + 1, x_from:x_to] = 0
    o[y0 - 1:bottom, x_from:x_to] = np.where(reg[..., 3:] > 0, reg, o[y0 - 1:bottom, x_from:x_to])
    return o


def bob(a, foot_h=4):
    """Than (tren vung chan) ha 1px - nhun khi 2 chan cham dat."""
    o = a.copy()
    solid = a[..., 3] > 0
    bottom = np.nonzero(solid.any(1))[0][-1]
    y0 = bottom - foot_h + 1
    body = a[:y0].copy()
    o[:y0] = 0
    o[1:y0 + 1] = np.where(body[..., 3:] > 0, body, o[1:y0 + 1])
    return o


def walk_frames(a, n):
    split, _ = feet_split(a)
    w = a.shape[1]
    L = lift(a, 0, split); R = lift(a, split, w)
    return [L, bob(a), R, bob(a)] if n == 4 else [L, R]


def frame(a):
    im = Image.fromarray(a, "RGBA")
    out = Image.new("RGBA", (FRAME, FRAME))
    out.alpha_composite(im, ((FRAME - im.width) // 2, FRAME - im.height - 4))   # chan cach day khung 4px
    return out


# phuong an test kich thuoc: ten -> {sprite: chieu cao muc tieu (None = native)}
# native: player 40px (luoi 16.75), zombie 31px (luoi 23) -> mat do pixel lech 1.37 lan
OPTIONS = {
    "A_zombie_to": {"player": None, "enemy_zombie": 37},     # zombie phong nearest x1.19 (pixel hoi khong deu)
    # "B_player_nho": {"player": 31, "enemy_zombie": None},  # bo 2026-10-11 (chot A); ban cu o export_soft/_archive/
}


def build(opt, sizes):
    root = os.path.join(EXPORT, opt)
    allf = {}
    for src, name, folder, nwalk in SOURCES:
        spr = es.extract(os.path.join(INBOX, src), name)
        h = sizes.get(name)
        if h and h != spr.height:
            spr = spr.resize((max(1, round(spr.width * h / spr.height)), h), Image.NEAREST)
        a = np.asarray(spr).copy()
        pad = np.zeros((a.shape[0] + 2, a.shape[1], 4), np.uint8); pad[1:-1] = a   # cho phep nhac/nhun 1px
        os.makedirs(os.path.join(root, folder), exist_ok=True)
        frames = [("idle", pad)] + [(f"walk_{i}", f) for i, f in enumerate(walk_frames(pad, nwalk))]
        allf[name] = []
        for tag, f in frames:
            im = frame(f); im.save(os.path.join(root, folder, f"{name}_{tag}.png")); allf[name].append(im)
        print(f"   {opt}: {name} {spr.width}x{spr.height}")
    return allf


if __name__ == "__main__":
    # CHI xoa thu muc cua chinh script nay (truoc day xoa MOI thu muc con -> mat player_v3 user sua tay, Projectiles...)
    for d in OPTIONS:
        if os.path.isdir(os.path.join(EXPORT, d)): shutil.rmtree(os.path.join(EXPORT, d))
    bgA = Image.open(os.path.join(HERE, "out", "terrain_A_meadow_demo.png")).convert("RGBA").crop((0, 0, 160, 64))
    rows = {}
    for opt, sizes in OPTIONS.items():
        allf = build(opt, sizes)
        rows[opt] = allf
        es.on_grass([fr[0].crop(fr[0].getbbox()) for fr in allf.values()], f"preview_idle_{opt}")
    # GIF: moi phuong an 1 hang
    gif = []
    for k in range(4):
        f = Image.new("RGBA", (160, 64 * len(rows)))
        for r, allf in enumerate(rows.values()):
            t = bgA.copy(); x = 20
            for fr in allf.values():
                walk = fr[1:]; t.alpha_composite(walk[k % len(walk)], (x, 8)); x += 56
            f.paste(t, (0, r * 64))
        gif.append(f.resize((f.width * 4, f.height * 4), Image.NEAREST))
    gif[0].save(os.path.join(HERE, "out", "soft", "preview_walk.gif"), save_all=True, append_images=gif[1:],
                duration=125, loop=0, disposal=2)
    print("ok ->", EXPORT, list(OPTIONS))
