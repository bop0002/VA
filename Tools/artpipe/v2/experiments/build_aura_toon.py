"""v2 - aura ban toon (tu build_aura_v2): it frame hon + net toon hon.

Khac v2:
  - 3 vong thay vi 4 (vong to, thua -> doc ro hon)
  - vien muc toi 1px 2 ben moi vong (giong vien nhan vat), mau phang, bo vet mo nhieu bac
  - hien/mat theo BAC (mong -> day -> mong) thay vi alpha muot
  - vong B lien net, chi dut 2-3 khuc to
  - 6 frame / vong lap (8 frame de so sanh)
Dung: python Tools/artpipe/v2/experiments/build_aura_toon.py -> export_soft/Projectiles/aura_toon/<palette>/ + out/aura_toon_*.png/.gif
"""
import os
import numpy as np
from PIL import Image

import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
import build_aura_v2 as v2
from build_aura_v2 import D, ANG, N, R, put

HERE, OUT = v2.HERE, os.path.join(v2.OUT, "_archive")
EXPORT = os.path.join(HERE, "export_soft", "_archive", "aura_toon")
CORE, EDGE = 8.0, 27.5          # vong tat truoc vien hitbox (R-2) -> khong chong 3 net o mep
GAP = (EDGE - CORE) / 3


def ink(pal):
    return tuple(int(c * 0.38) for c in pal["deep"])


def stage_of(r):
    """Bac theo ban kinh: 0 an, 1 mong (moi sinh / sap tat), 2 day du."""
    if r < CORE + 1.5 or r > EDGE + 0.5: return 0
    if r < CORE + 4 or r > EDGE - 3: return 1
    return 2


def ring_A(img, r, pal, k):
    st = stage_of(r)
    if st == 0: return
    o = ink(pal)
    if st == 1:
        put(img, (D >= r - 2) & (D < r - 1), pal["mid"], 255); return
    put(img, (D >= r - 4) & (D < r - 3), o, 200)                     # vien muc trong
    put(img, (D >= r - 3) & (D < r - 2), pal["mid"], 255)
    put(img, (D >= r - 2) & (D < r - 1), pal["hi"], 255)
    put(img, (D >= r - 1) & (D < r), o, 220)                         # vien muc ngoai


def ring_B(img, r, pal, k):
    st = stage_of(r)
    if st == 0: return
    o = ink(pal)
    gap = ((ANG / (2 * np.pi) * 3 + k / 12) % 1) < 0.1               # 3 khuc dut to, troi cham
    if st == 1:
        put(img, (D >= r - 2) & (D < r - 1) & ~gap, pal["alt"], 200); return
    put(img, (D >= r - 3) & (D < r - 2) & ~gap, o, 180)
    put(img, (D >= r - 2) & (D < r - 1) & ~gap, pal["alt"], 255)
    put(img, (D >= r - 1) & (D < r) & ~gap, o, 180)
    for t in (0.9, 3.0, 5.0):                                         # 3 cham lap lanh 2x2 kieu toon
        x, y = int(R + np.cos(t) * (r - 1.5)), int(R + np.sin(t) * (r - 1.5))
        img[max(0, y - 1):y + 1, max(0, x - 1):x + 1] = pal["spark"] + (255,)


def render(pal, frame, frames):
    img = np.zeros((N, N, 4), np.uint8)
    put(img, D < R - 1, pal["deep"], 70)                              # nen phang 1 bac
    put(img, D < CORE, ink(pal), 200)                                 # loi: vien muc + 2 mau phang
    put(img, D < CORE - 1, pal["mid"], 200)
    put(img, D < CORE - 3.5, pal["hi"], 200)
    s = frame / (frames / 2) * GAP
    for k in range(-1, 5):
        (ring_A if k % 2 == 0 else ring_B)(img, CORE + k * GAP + s, pal, frame * 12 // frames)
    put(img, (D >= R - 1) & (D < R), ink(pal), 230)                   # vien hitbox: muc
    put(img, (D >= R - 2) & (D < R - 1), pal["mid"], 160)
    return img


def pick_static(nf):
    """Frame co vong A (day) nam giua (~CORE + 1.5 GAP) -> vong ro, khong bi player che, khong dinh vien."""
    want = CORE + 1.5 * GAP
    return int(np.argmin([min(abs(CORE + k * GAP + i / (nf / 2) * GAP - want) for k in (0, 2)) for i in range(nf)]))


if __name__ == "__main__":
    rows = []
    for name, pal in v2.PALETTES.items():
        d = os.path.join(EXPORT, name); os.makedirs(d, exist_ok=True)
        for nf, fps in ((6, 8), (8, 10)):
            fr = [render(pal, i, nf) for i in range(nf)]
            st = [v2.stage(f) for f in fr]
            st[0].save(os.path.join(OUT, f"aura_toon_{name}_{nf}f.gif"), save_all=True, append_images=st[1:],
                       duration=1000 // fps, loop=0)
            if nf == 6:
                for i, f in enumerate(fr): Image.fromarray(f, "RGBA").save(os.path.join(d, f"aura_ripple_{i}.png"))
                si = pick_static(nf)
                Image.fromarray(fr[si], "RGBA").save(os.path.join(d, "aura.png"))
                rows.append((v2.bare(fr[si]), v2.stage(fr[si]), fr))
    H1 = rows[0][1].height; W0, H0 = rows[0][0].width, rows[0][0].height
    cmp_ = Image.new("RGBA", (len(rows) * (H1 + 12), H0 + H1 + 12), (10, 10, 14, 255))
    for i, (a, b, _) in enumerate(rows):
        x = i * (H1 + 12); cmp_.paste(a, (x + (H1 - W0) // 2, 0)); cmp_.paste(b, (x, H0 + 12))
    cmp_.save(os.path.join(OUT, "aura_toon_preview.png"))
    # dai frame 6f moi palette
    strip = Image.new("RGBA", (6 * 68, len(rows) * 68), (24, 26, 30, 255))
    for j, (_, _, fr) in enumerate(rows):
        for i, f in enumerate(fr): strip.alpha_composite(Image.fromarray(f, "RGBA"), (i * 68 + 2, j * 68 + 2))
    strip.resize((strip.width * 3, strip.height * 3), Image.NEAREST).save(os.path.join(OUT, "aura_toon_frames.png"))
    print("ok ->", EXPORT)
