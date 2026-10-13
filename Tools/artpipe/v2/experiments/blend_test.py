"""v2 - thu nghiem vi sao nhan vat 'khong an nhap' voi map graveyard: moi hang them 1 cach sua.

  1 goc                       : sprite dat thang len map
  2 + bong chan               : elip toi ban trong suot duoi chan (concept co, sprite minh khong co)
  3 + bong + am mau dem       : nhan vat giam bao hoa ~25% + nghieng lanh (cung 'khi quyen' voi map)
  4 + bong + anh sang dem     : ca canh toi lai, quang sang am quanh duoc va quanh player (gia lap Light 2D cua URP)
Khong sua sprite goc. Dung: python Tools/artpipe/v2/experiments/blend_test.py -> v2/out/blend_test.png
"""
import os
import numpy as np
from PIL import Image

import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))   # = v2/
import graveyard as gy

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # = v2/ (script nam o v2/experiments/)
import sys; sys.path.insert(0, HERE)
OUT = os.path.join(HERE, "out", "_archive")
SOFT = os.path.join(HERE, "export_soft")
W, H = 300, 110


def load(p):
    im = Image.open(os.path.join(SOFT, p)).convert("RGBA")
    return im.crop(im.getbbox())


def foot_shadow(bg, cx, by, w, alpha=170):
    yy, xx = np.mgrid[0:H, 0:W]
    m = ((xx - cx) / (w / 2)) ** 2 + ((yy - by) / 3.2) ** 2 < 1
    a = np.asarray(bg).copy()
    a[m, :3] = (a[m, :3] * (1 - alpha / 255) + np.array(gy.P[0]) * alpha / 255).astype(np.uint8)
    return Image.fromarray(a, "RGBA")


def night_tint(im, sat=0.75, tint=(0.88, 0.92, 1.06)):
    a = np.asarray(im).astype(float)
    rgb = a[..., :3]; g = rgb.mean(-1, keepdims=True)
    rgb = (g + (rgb - g) * sat) * np.array(tint)
    a[..., :3] = np.clip(rgb, 0, 255)
    return Image.fromarray(a.astype(np.uint8), "RGBA")


def lights(im, sources, ambient=0.62):
    """Nhan ca canh voi anh sang: ambient lanh + quang tron am (cx, cy, r, mau, cuong do)."""
    a = np.asarray(im).astype(float)
    yy, xx = np.mgrid[0:H, 0:W]
    L = np.ones((H, W, 3)) * ambient * np.array([0.85, 0.9, 1.1])
    for cx, cy, r, col, k in sources:
        f = np.clip(1 - np.hypot(xx - cx, yy - cy) / r, 0, 1) ** 1.6 * k
        L += f[..., None] * np.array(col)
    a[..., :3] = np.clip(a[..., :3] * L, 0, 255)
    return Image.fromarray(a.astype(np.uint8), "RGBA")


def scene(step):
    bg = Image.open(os.path.join(HERE, "out", "tilesheet_C_graveyard_demo.png")).convert("RGBA")
    bg = bg.resize((bg.width // 2, bg.height // 2), Image.NEAREST).crop((60, 120, 60 + W, 120 + H))
    pr = {k: load(f"Props_Graveyard/{k}.png") for k in ("tomb_round", "tomb_tall", "torch_0", "tree_face", "cross_stone")}
    player = load("A_zombie_to/Characters/player_idle.png")
    zombie = load("A_zombie_to/Enemies/enemy_zombie_idle.png")
    if step == 3:                                                   # buoc 4: Light 2D tu am mau ca canh
        player, zombie = night_tint(player), night_tint(zombie)
    items = [("tomb_round", pr["tomb_round"], 18, 52), ("tomb_tall", pr["tomb_tall"], 52, 48),
             ("tree", pr["tree_face"], 236, 76), ("torch", pr["torch_0"], 150, 70),
             ("cross", pr["cross_stone"], 200, 104),
             ("player", player, 100, 92), ("zombie", zombie, 180, 98), ("zombie", zombie, 60, 104)]
    for kind, im, x, by in sorted(items, key=lambda t: t[3]):        # ve theo y (sau -> truoc)
        if step >= 2 and kind in ("player", "zombie"):
            bg = foot_shadow(bg, x + im.width / 2, by - 1, im.width * 0.8)
        bg.alpha_composite(im, (int(x), by - im.height))
    if step >= 4:
        bg = lights(bg, [(157, 40, 70, (1.0, 0.62, 0.3), 0.9),          # duoc
                         (118, 76, 55, (0.55, 0.5, 0.45), 0.45)])       # quang quanh player
    return bg


if __name__ == "__main__":
    labels = ["1 goc", "2 + bong chan", "3 + bong + am mau dem", "4 + bong + anh sang dem (Light 2D)"]
    out = Image.new("RGBA", (W, (H + 4) * 4), (10, 10, 14, 255))
    for i in range(4):
        out.paste(scene(i + 1), (0, i * (H + 4)))
    out = out.resize((out.width * 3, out.height * 3), Image.NEAREST)
    from PIL import ImageDraw
    d = ImageDraw.Draw(out)
    for i, t in enumerate(labels):
        y = i * (H + 4) * 3 + 4
        d.rectangle((4, y, 8 + len(t) * 6, y + 12), fill=(0, 0, 0)); d.text((6, y + 1), t, fill=(255, 235, 170))
    gy.save(out, os.path.join(OUT, "blend_test.png"))
    print("ok")
