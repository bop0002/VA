"""v2 - prop cho map C_graveyard (theo conceptref.jpg): bia mo, thap tu, rao sat, duoc, den long, cay chet...

Ban 2 (user: "lam mem, to hon"): khoi to tron, to 2 tong (than + bong day phia duoi-phai) + 1 vet sang tren-trai,
bo chi tiet nho (reu, chu khac, van vo). Hinh ve tren toa do logic, phong K lan khi raster -> to hon ma pixel van deu.
Rao giu 32px (lap theo o). Vien toi 1px. Ban 1 luu o export_soft/Props_Graveyard_v1.
Dung: python Tools/artpipe/v2/graveyard_props.py -> v2/export_soft/Props_Graveyard/*.png + v2/out/graveyard_props_*.png
"""
import os
import numpy as np
from PIL import Image

import graveyard as gy

HERE = os.path.dirname(os.path.abspath(__file__))
EXPORT = os.path.join(HERE, "export_soft", "Props_Graveyard")
OUT = os.path.join(HERE, "out")
K = 1.35                                    # he so phong so voi ban 1
hx = gy.hx
OL = hx("#15111f")
STONE = [hx(c) for c in ("#454360", "#5c5a76", "#7a7892")]          # bong, than, sang
WOOD = [hx(c) for c in ("#3e2a2c", "#5e3e34", "#7a5440")]
IRON = [hx(c) for c in ("#2a2838", "#403e56", "#5c5a76")]
FIRE = [hx(c) for c in ("#e0582a", "#f8a838", "#ffe68a")]
BARK = [hx(c) for c in ("#2a2129", "#3d3138", "#544549")]
EYE = [hx(c) for c in ("#d0501e", "#ffc050")]
BONE = [hx(c) for c in ("#a9a294", "#d8d0bc", "#f0ead8")]


class Canvas:
    def __init__(self, w, h, k=K):
        self.k = k
        self.W, self.H = int(round(w * k)), int(round(h * k))
        self.a = np.zeros((self.H, self.W, 4), np.uint8)

    def grid(self):
        """Toa do logic (tam pixel / K) -> ve hinh theo kich thuoc ban 1 nhung raster to hon."""
        y, x = np.mgrid[0:self.H, 0:self.W]
        return (y + 0.5) / self.k, (x + 0.5) / self.k

    def put(self, mask, col):
        self.a[mask, :3] = col; self.a[mask, 3] = 255

    def outline(self):
        s = self.a[..., 3] > 0
        n = np.zeros_like(s)
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n |= np.roll(np.roll(s, dy, 0), dx, 1)
        self.put(n & ~s, OL)
        return self

    def shadow(self, y0, x0, x1):
        """Bong dat duoi chan (1px, mau dat toi) - ve sau outline."""
        y, x = self.grid()
        row = int(y0 * self.k)
        m = np.zeros(self.a.shape[:2], bool)
        m[row, :] = (x[row] >= x0) & (x[row] <= x1)
        self.put(m & (self.a[..., 3] == 0), gy.P[1])
        return self

    def img(self):
        im = Image.fromarray(self.a, "RGBA")
        return im.crop(im.getbbox())


def two_tone(c, mask, ramp, band=2):
    """Than ramp[1]; bong day `band` px o mep duoi-phai; 1px sang o mep tren-trai."""
    sh = lambda dy, dx: np.roll(np.roll(mask, dy, 0), dx, 1)
    c.put(mask, ramp[1])
    shadow = np.zeros_like(mask)
    for d in range(1, band + 1):
        shadow |= ~sh(-d, 0) | ~sh(-d, -d) | ~sh(0, -d)
    c.put(mask & shadow, ramp[0])
    c.put(mask & ~shadow & (~sh(1, 0) | ~sh(0, 1)), ramp[2])


def tombstone(kind):
    c = Canvas(26, 31); y, x = c.grid()
    if kind == "round":
        m = ((x >= 5) & (x <= 21) & (y >= 10) & (y <= 28)) | ((((x - 13) ** 2) + (y - 11) ** 2) < 8.2 ** 2)
    elif kind == "tall":
        m = ((x >= 7) & (x <= 19) & (y >= 7) & (y <= 28)) | ((((x - 13) / 6.2) ** 2 + ((y - 7.5) / 3.5) ** 2) < 1)
    else:   # broken: dinh vo cheo, goc bo tron
        m = (x >= 5) & (x <= 21) & (y >= 12) & (y <= 28) & (y > 21 - (x - 5) * 0.6)
    m &= y <= 28
    two_tone(c, m, STONE, band=2)
    if kind == "round":   # 1 mang khac lom to thay cho chu
        inset = ((x >= 9.5) & (x <= 16.5) & (y >= 13) & (y <= 22)) | (((x - 13) ** 2 + (y - 13) ** 2) < 3.5 ** 2)
        c.put(inset & m, STONE[0])
    return c.outline().shadow(29.3, 3, 23).img()


def stone_cross():
    c = Canvas(22, 32); y, x = c.grid()
    m = ((x >= 8.5) & (x <= 13.5) & (y >= 2) & (y <= 29)) | ((y >= 8) & (y <= 12.5) & (x >= 3) & (x <= 19))
    m |= (y >= 25.5) & (y <= 29) & (x >= 5.5) & (x <= 16.5)
    two_tone(c, m, STONE, band=2)
    return c.outline().shadow(30.3, 4, 18).img()


def wood_cross():
    c = Canvas(18, 28); y, x = c.grid()
    m = ((x >= 7.5) & (x <= 10.5) & (y >= 2) & (y <= 25)) | ((y >= 7) & (y <= 9.8) & (x >= 2.5) & (x <= 15.5))
    two_tone(c, m, WOOD, band=1)
    return c.outline().shadow(26.3, 5, 13).img()


def fence(post_only=False):
    """Rao 32px lap ngang (khong phong K de khop o): 3 song 2px + cot to dau doan, mui giao to."""
    w = 7 if post_only else 32
    c = Canvas(w + 2, 32, k=1); y, x = c.grid(); x = x - 1.5; y = y - 0.5
    bars = [(2.5, 2)] if post_only else [(2.5, 2), (11, 1), (19, 1), (27, 1)]
    for bx, hw in bars:
        bm = (np.abs(x - bx) <= hw) & (y >= 8) & (y <= 29)
        tip = (np.abs(x - bx) <= (y - 1.5) * 0.55) & (y >= 2) & (y <= 7.5)
        two_tone(c, bm | tip, IRON, band=1)
    if not post_only:
        for ry in (12, 24):
            rm = (y >= ry) & (y <= ry + 1.5) & (x >= -1.5) & (x <= 30.5)
            c.put(rm, IRON[1]); c.put(rm & (y >= ry + 1), IRON[0])
    return c.outline().img()


def torch(frame):
    c = Canvas(14, 34); y, x = c.grid()
    stick = (x >= 5.5) & (x <= 8.5) & (y >= 13) & (y <= 31)
    two_tone(c, stick, WOOD, band=1)
    cup = (x >= 4) & (x <= 10) & (y >= 10.5) & (y <= 14)
    two_tone(c, cup, IRON, band=1)
    sway = [0, 0.8, -0.8][frame]; top = [1.5, 2.5, 1][frame]
    t = np.clip((y - top) / (11 - top), 0, 1)                      # 0 dinh -> 1 day ngon lua
    cx = 7 + sway * (1 - t)
    fl = (np.abs(x - cx) <= 0.4 + 3.6 * np.sqrt(t)) & (y >= top) & (y <= 11)
    c.put(fl, FIRE[0])
    inner = (np.abs(x - cx) <= 2.2 * np.sqrt(np.clip((y - top - 3) / (11 - top - 3), 0, 1))) & (y <= 11) & fl
    c.put(inner, FIRE[1])
    core = inner & (np.abs(x - 7) <= 1) & (y >= 7.5)
    c.put(core, FIRE[2])
    return c.outline().shadow(32.3, 4, 10).img()


def lantern():
    c = Canvas(19, 40); y, x = c.grid()
    post = (x >= 7.5) & (x <= 10) & (y >= 5) & (y <= 37)
    arm = (y >= 4.5) & (y <= 6.5) & (x >= 7.5) & (x <= 16)
    base = (y >= 35.5) & (y <= 37.5) & (x >= 5.5) & (x <= 12)
    two_tone(c, post | arm | base, IRON, band=1)
    box = (x >= 10.5) & (x <= 17.5) & (y >= 8.5) & (y <= 18.5)
    roof = (np.abs(x - 14) <= (y - 6) * 1.6) & (y >= 6.5) & (y <= 9)
    c.put(box | roof, IRON[1])
    glass = (x >= 12) & (x <= 16) & (y >= 10.5) & (y <= 17)
    c.put(glass, FIRE[1]); c.put(glass & (x <= 13.3) & (y <= 13.5), FIRE[2])
    return c.outline().shadow(38.3, 4, 14).img()


def limb(c, x0, y0, ang, ln, th, depth, rng, body):
    y, x = c.grid()
    for k in np.arange(0, ln, 0.5):
        px = x0 + np.cos(ang) * k; py = y0 - np.sin(ang) * k
        r = max(0.9, th * (1 - k / ln * 0.55))
        body |= (x - px) ** 2 + (y - py) ** 2 <= r * r
    ex, ey = x0 + np.cos(ang) * ln, y0 - np.sin(ang) * ln
    if depth > 0:
        for da in (-0.5, 0.45):
            limb(c, ex, ey, ang + da + rng.normal(0, .08), ln * 0.6, th * 0.55, depth - 1, rng, body)
    return body


def dead_tree(face):
    c = Canvas(54, 62); y, x = c.grid(); rng = np.random.default_rng(4 if face else 8)
    trunk = (np.abs(x - 27) <= 4.6 + np.maximum(0, y - 50) * 0.7) & (y >= 24) & (y <= 58)
    body = trunk.copy()
    limb(c, 26, 28, np.pi * 0.74, 15, 3.2, 1, rng, body)
    limb(c, 28, 27, np.pi * 0.26, 15, 3.2, 1, rng, body)
    limb(c, 27, 26, np.pi * 0.52, 10, 2.6, 0, rng, body)
    two_tone(c, body, BARK, band=2)
    if face:
        for ex in (23, 29):
            eye = ((x - ex - 1) ** 2 + (y - 39) ** 2) < 1.9 ** 2
            c.put(eye, EYE[0]); c.put(eye & (x < ex + 1) & (y < 39), EYE[1])
        mouth = (((x - 27) / 3.6) ** 2 + ((y - 46) / 2.4) ** 2) < 1
        c.put(mouth, OL)
    return c.outline().shadow(59.3, 17, 37).img()


def dead_bush():
    c = Canvas(24, 18); rng = np.random.default_rng(5)
    body = np.zeros(c.a.shape[:2], bool)
    for a in (0.5, 0.9, 1.35, 1.75, 2.2, 2.6):
        limb(c, 12, 15.5, a, 7.5, 1.2, 0, rng, body)
    two_tone(c, body, BARK, band=1)
    return c.outline().shadow(17, 6, 18).img()


def rock(big):
    w, h = (21, 15) if big else (13, 10)
    c = Canvas(w + 2, h + 3); y, x = c.grid()
    m = ((x - (w + 2) / 2) / (w / 2)) ** 2 + ((y - h / 2 - 1.2) / (h / 2)) ** 2 < 1
    m &= y <= h + 1
    two_tone(c, m, STONE, band=2)
    return c.outline().shadow(h + 2.3, 2, w).img()


def skull_pile():
    c = Canvas(24, 17); y, x = c.grid()
    for cx, cy in ((12, 6), (7, 11), (17, 11)):
        m = ((x - cx) ** 2 + (y - cy) ** 2) < 4.8 ** 2
        two_tone(c, m, BONE, band=1)
        for ex in (cx - 2.2, cx + 2.2):
            c.put(m & (((x - ex) ** 2 + (y - cy - 0.6) ** 2) < 1.3 ** 2), OL)
    return c.outline().shadow(16.3, 3, 21).img()


PROPS = {
    "tomb_round": lambda: tombstone("round"), "tomb_tall": lambda: tombstone("tall"),
    "tomb_broken": lambda: tombstone("broken"), "cross_stone": stone_cross, "cross_wood": wood_cross,
    "fence": fence, "fence_post": lambda: fence(True), "torch_0": lambda: torch(0), "torch_1": lambda: torch(1),
    "torch_2": lambda: torch(2), "lantern": lantern, "tree_dead": lambda: dead_tree(False),
    "tree_face": lambda: dead_tree(True), "bush_dead": dead_bush, "rock_big": lambda: rock(True),
    "rock_small": lambda: rock(False), "skull_pile": skull_pile,
}


def scene(imgs):
    """Dat prop len map demo graveyard (ban tile da chon) de xem tong the."""
    bg = Image.open(os.path.join(OUT, "tilesheet_C_graveyard_demo.png")).convert("RGBA")
    bg = bg.resize((bg.width // 2, bg.height // 2), Image.NEAREST)
    place = [("tree_face", 400, 120), ("tree_dead", 20, 300), ("tomb_round", 120, 44), ("tomb_tall", 160, 48),
             ("cross_stone", 200, 42), ("tomb_broken", 240, 48), ("cross_wood", 470, 260), ("torch_0", 330, 60),
             ("lantern", 90, 250), ("bush_dead", 220, 310), ("rock_big", 380, 300), ("rock_small", 420, 210),
             ("skull_pile", 300, 230), ("tomb_round", 30, 110), ("tomb_tall", 350, 180)]
    for k in range(6): place.append(("fence" if k < 5 else "fence_post", 120 + k * 32, 290))
    for name, x, yb in place:
        im = imgs[name]; bg.alpha_composite(im, (x, yb - im.height))
    return bg.resize((bg.width * 2, bg.height * 2), Image.NEAREST)


if __name__ == "__main__":
    os.makedirs(EXPORT, exist_ok=True)
    imgs = {k: f() for k, f in PROPS.items()}
    for k, im in imgs.items(): gy.save(im, os.path.join(EXPORT, f"{k}.png"))
    W = sum(im.width for im in imgs.values()) + 4 * len(imgs) + 4; H = max(im.height for im in imgs.values()) + 8
    sh = Image.new("RGBA", (W, H), tuple(gy.G[2]) + (255,)); x = 4
    for im in imgs.values(): sh.alpha_composite(im, (x, H - 4 - im.height)); x += im.width + 4
    gy.save(sh.resize((W * 4, H * 4), Image.NEAREST), os.path.join(OUT, "graveyard_props_sheet.png"))
    gy.save(scene(imgs), os.path.join(OUT, "graveyard_props_scene.png"))
    fr = [imgs[f"torch_{i}"].resize((imgs[f"torch_{i}"].width * 6, imgs[f"torch_{i}"].height * 6), Image.NEAREST) for i in range(3)]
    Wg, Hg = max(f.width for f in fr), max(f.height for f in fr)
    g = []
    for f in fr:
        b = Image.new("RGBA", (Wg, Hg), tuple(gy.G[1]) + (255,)); b.alpha_composite(f, ((Wg - f.width) // 2, Hg - f.height)); g.append(b)
    g[0].save(os.path.join(OUT, "graveyard_torch.gif"), save_all=True, append_images=g[1:], duration=140, loop=0)
    print("ok", len(imgs), "props ->", EXPORT, {k: im.size for k, im in imgs.items()})
