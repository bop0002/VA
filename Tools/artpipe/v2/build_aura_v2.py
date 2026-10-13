"""v2 - aura ve lai bang code (thay cach thu nho anh Gemini o build_aura.py: vong bi dut, mong, nhoe mau).

Giu thiet ke anh Gemini (vong dong tam quanh loi sang) nhung ve pixel sach:
  - vong lien net (vanh khuyen tinh theo tam pixel, day >= 1px -> khong ho)
  - 2 kieu vong xen ke de tung vong khac nhau ro: A = vong day 2px (mep ngoai sang, mep trong dam),
    B = vong mong 1px dut khuc + cham lap lanh
  - vet sang mo phia trong moi vong (vong dang lan ra) -> day dan, co chieu sau
  - vien ngoai tinh = ban kinh sat thuong (de doc hitbox)
Animation: vong lan ra tu loi (CORE) toi mep (EDGE), mo dan o 2 dau; loop qua 2 khoang cach vong
(12 frame) de 2 kieu A/B xen ke van lien mach. Sprite tinh = frame STATIC.
Dung: python Tools/artpipe/v2/build_aura_v2.py [blue] -> export_soft/Projectiles/aura_v2/<palette>/ + out/aura_v2_*.png/.gif
"""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
EXPORT = os.path.join(HERE, "export_soft", "Projectiles", "aura_v2")
ARCH_EXPORT = os.path.join(HERE, "export_soft", "_archive", "aura_v2")   # cac ban mau khong chon
ARCH_OUT = os.path.join(OUT, "_archive")
N = 64                      # 64px = duong kinh 2 unit o PPU 32 = _baseRadius 1
R = N / 2
CORE, EDGE = 7.0, 29.5      # vong sinh ra / bien mat (px)
GAP = (EDGE - CORE) / 4     # 4 vong cung luc
FRAMES = 12                 # 2 khoang GAP
STATIC = 4                  # frame dung lam sprite tinh (2 vong A sang deu, vong B xen giua)

# palette: (dam, vua, sang, rat sang, trang) - kieu B dung 'alt' cho khac mau vong A
PALETTES = {
    "A_ngoc": dict(deep=(14, 92, 76), mid=(30, 168, 120), hi=(70, 240, 165), top=(190, 255, 225),
                   alt=(60, 220, 170), spark=(235, 255, 245)),
    "B_ngoc_lam": dict(deep=(14, 80, 96), mid=(30, 168, 130), hi=(80, 245, 170), top=(200, 255, 230),
                       alt=(70, 210, 255), spark=(230, 250, 255)),
    "C_doc_xanh": dict(deep=(40, 96, 30), mid=(100, 190, 40), hi=(170, 250, 70), top=(235, 255, 180),
                       alt=(90, 235, 140), spark=(250, 255, 220)),
}

yy, xx = np.mgrid[0:N, 0:N]
D = np.hypot(xx + 0.5 - R, yy + 0.5 - R)
ANG = np.arctan2(yy + 0.5 - R, xx + 0.5 - R)


def fade(r):
    """Do dam theo ban kinh: hien dan sau loi, sang nhat ~2/3, mo dan khi toi mep."""
    return float(np.clip((r - CORE) / 4, 0, 1) * np.clip((EDGE + 1 - r) / 5, 0, 1))


def put(img, mask, col, a):
    """Ve de len (chi khi alpha moi >= alpha cu -> vong sang khong bi vet mo de mat)."""
    m = mask & (a >= img[..., 3])
    img[m, :3] = col; img[m, 3] = a


def ring_A(img, r, pal, k):
    """Vong day 2px: mep ngoai sang, mep trong 'vua' + vet mo 3px phia trong."""
    f = fade(r)
    if f <= 0: return
    for w, a in ((3, 70), (2, 110)):                                    # vet (trail) phia trong
        put(img, (D >= r - 2 - w) & (D < r - 2), pal["deep"], int(a * f))
    put(img, (D >= r - 2) & (D < r - 1), pal["mid"], int(255 * min(1, f * 1.3)))
    put(img, (D >= r - 1) & (D < r), pal["hi"] if f < 0.85 else pal["top"], int(255 * min(1, f * 1.3)))


def ring_B(img, r, pal, k):
    """Vong mong 1px dut khuc (dash quay nguoc chieu theo frame) + cham lap lanh."""
    f = fade(r)
    if f <= 0: return
    put(img, (D >= r - 3) & (D < r - 1), pal["deep"], int(80 * f))
    seg = max(6, int(r * 0.7))
    ph = (ANG / (2 * np.pi) * seg + k * 0.25) % 1
    put(img, (D >= r - 1) & (D < r) & (ph < 0.8), pal["alt"], int(255 * min(1, f * 1.3)))
    # cham lap lanh: 3 diem co dinh goc tren vong
    for t in (0.6, 2.4, 4.3):
        x, y = int(R + np.cos(t) * (r - 0.5)), int(R + np.sin(t) * (r - 0.5))
        if 0 <= x < N and 0 <= y < N and f > 0.4: img[y, x] = pal["spark"] + (255,)


def render(pal, frame=0, outline=True):
    img = np.zeros((N, N, 4), np.uint8)
    # quang nen: lop ban trong rat nhe toan vung + loi sang
    put(img, D < R - 1, pal["deep"], 40)
    put(img, D < CORE + 1, pal["deep"], 90)
    s = frame / (FRAMES / 2) * GAP                                      # do lan ra
    for k in range(-1, 6):
        r = CORE + k * GAP + s
        idx = k                                                          # kieu theo danh tinh vong -> xen ke A/B
        if r < CORE or r > EDGE + 1: continue
        (ring_A if idx % 2 == 0 else ring_B)(img, r, pal, frame)
    img[D < CORE - 2] = 0                                                # khoet loi (ca vet vong moi sinh): khong phu mau len nhan vat (user, 2026-10-13)
    if outline:                                                          # vien hitbox tinh, 1px
        put(img, (D >= R - 1.6) & (D < R - 0.6), pal["mid"], 150)
    return img


def stage(img, scale=5, n=96):
    g = Image.open(os.path.join(OUT, "tilesheet_C_graveyard.png")).convert("RGBA").crop((5 * 32, 0, 6 * 32, 32))
    bg = Image.new("RGBA", (n, n))
    for y in range(0, n, 32):
        for x in range(0, n, 32): bg.paste(g, (x, y))
    bg.alpha_composite(Image.fromarray(img, "RGBA"), (n // 2 - N // 2, n // 2 - N // 2))
    p = Image.open(os.path.join(HERE, "export_soft", "player_v3", "player_idle.png")).convert("RGBA")
    bg.alpha_composite(p, (n // 2 - 24, n // 2 - 30))
    return bg.resize((n * scale, n * scale), Image.NEAREST)


def bare(img, scale=5, bgc=(24, 26, 30)):
    b = Image.new("RGBA", (N + 8, N + 8), bgc + (255,))
    b.alpha_composite(Image.fromarray(img, "RGBA"), (4, 4))
    return b.resize((b.width * scale, b.height * scale), Image.NEAREST)


# bo thu mau "B_ngoc_lam" (user chon 2026-10-13): vong B giu xanh lam, doi mau vong A (+ 2 ban dao)
BLUE_SET = {
    "B_ngoc_lam": PALETTES["B_ngoc_lam"],
    "D_tim_lam": dict(deep=(44, 30, 100), mid=(120, 80, 225), hi=(180, 135, 255), top=(235, 215, 255),
                      alt=(70, 210, 255), spark=(235, 245, 255)),
    "E_bang_lam": dict(deep=(20, 60, 112), mid=(60, 140, 232), hi=(145, 212, 255), top=(235, 250, 255),
                       alt=(80, 225, 255), spark=(255, 255, 255)),
    "F_hong_lam": dict(deep=(88, 28, 88), mid=(220, 80, 180), hi=(255, 135, 220), top=(255, 220, 245),
                       alt=(70, 210, 255), spark=(255, 240, 250)),
    "G_vang_lam": dict(deep=(84, 66, 22), mid=(220, 168, 50), hi=(255, 222, 95), top=(255, 246, 205),
                       alt=(70, 200, 255), spark=(255, 255, 230)),
    "H_lam_dao_tim": dict(deep=(18, 48, 112), mid=(50, 130, 232), hi=(100, 200, 255), top=(220, 245, 255),
                          alt=(175, 115, 255), spark=(245, 235, 255)),
    "I_lam_dao_ngoc": dict(deep=(18, 48, 112), mid=(50, 130, 232), hi=(100, 200, 255), top=(220, 245, 255),
                           alt=(80, 245, 175), spark=(235, 255, 245)),
}


def run(palettes, tag):
    rows = []
    for name, pal in palettes.items():
        main = name == MAIN                                              # ban khong chon -> _archive
        d = os.path.join(EXPORT if main else ARCH_EXPORT, name); os.makedirs(d, exist_ok=True)
        o = OUT if main else ARCH_OUT; os.makedirs(o, exist_ok=True)
        frames = [render(pal, i) for i in range(FRAMES)]
        Image.fromarray(frames[STATIC], "RGBA").save(os.path.join(d, "aura.png"))
        for i, f in enumerate(frames): Image.fromarray(f, "RGBA").save(os.path.join(d, f"aura_ripple_{i}.png"))
        st = [stage(f) for f in frames]
        st[0].save(os.path.join(o, f"aura_v2_{name}.gif"), save_all=True, append_images=st[1:], duration=100, loop=0)
        rows.append((bare(frames[STATIC]), stage(frames[STATIC])))
    # preview: moi palette 1 cot - tren: aura tran tren nen toi, duoi: tren graveyard + player (toi da 4 cot / hang)
    W = rows[0][0].width; H0, H1 = rows[0][0].height, rows[0][1].height
    cols = min(4, len(rows)); nr = (len(rows) + cols - 1) // cols
    ch = H0 + H1 + 12
    cmp_ = Image.new("RGBA", (cols * (H1 + 12), nr * (ch + 24)), (10, 10, 14, 255))
    for i, (a, b) in enumerate(rows):
        x, y = (i % cols) * (H1 + 12), (i // cols) * (ch + 24)
        cmp_.paste(a, (x + (H1 - W) // 2, y)); cmp_.paste(b, (x, y + H0 + 12))
    cmp_.save(os.path.join(ARCH_OUT, f"aura_v2_{tag}preview.png"))


MAIN = "H_lam_dao_tim"      # user chon 2026-10-13 -> ban chinh export_soft/Projectiles/aura(_alpha).png + aura_ripple/


def promote(name=MAIN):
    """Chep ban da chon ra ten chinh (giu ten cu -> thay PNG trong Unity giu nguyen .meta/reference)."""
    import shutil, glob
    src = os.path.join(EXPORT, name)
    proj = os.path.dirname(EXPORT)
    shutil.copyfile(os.path.join(src, "aura.png"), os.path.join(proj, "aura.png"))
    # aura_alpha.png: user da tu khoet rong hon (2026-10-13) -> khong ghi de
    rip = os.path.join(proj, "aura_ripple"); os.makedirs(rip, exist_ok=True)
    for f in glob.glob(os.path.join(rip, "aura_ripple_*.png")): os.remove(f)
    for i in range(FRAMES):
        shutil.copyfile(os.path.join(src, f"aura_ripple_{i}.png"), os.path.join(rip, f"aura_ripple_{i}.png"))


if __name__ == "__main__":
    import sys
    if "blue" in sys.argv: run(BLUE_SET, "blue_")
    else: run(PALETTES, "")
    promote()
    print("ok ->", EXPORT)
