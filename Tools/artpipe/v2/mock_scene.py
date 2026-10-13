"""v2 - canh gia lap khung hinh game (480x270 = 15x8.4 unit o PPU 32) tren Graveyard Chunk 1: so sanh
  1_goc        : sprite dat thang len map
  2_bong       : + sprite bong chan (export_soft/Shadows/shadow_*.png - dung duoc luon trong Unity)
  3_bong_den   : + anh sang dem gia lap URP Light 2D (Global lanh ~0.58, Point cam o duoc/den long, quang am quanh player)
Dung: python Tools/artpipe/v2/mock_scene.py -> v2/out/mock_scene_<ban>.png (x3) + mock_scene_compare.png
"""
import os
import numpy as np
from PIL import Image

import graveyard as gy

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
SOFT = os.path.join(HERE, "export_soft")
SHADOWS = os.path.join(SOFT, "Shadows")
W, H = 480, 270


def load(p):
    im = Image.open(os.path.join(SOFT, p)).convert("RGBA")
    return im.crop(im.getbbox())


def shadow_sprite(w, h):
    """Elip pixel 2 bac: loi dam (alpha 170) + vanh nhat (alpha 95), mau dat toi nhat cua map."""
    c = Image.new("RGBA", (w, h))
    a = np.zeros((h, w, 4), np.uint8)
    yy, xx = np.mgrid[0:h, 0:w]
    d = ((xx + 0.5 - w / 2) / (w / 2)) ** 2 + ((yy + 0.5 - h / 2) / (h / 2)) ** 2
    a[d < 1, :3] = gy.P[0]; a[d < 1, 3] = 95
    a[d < 0.55, 3] = 170
    return Image.fromarray(a, "RGBA")


def lights(im, sources, ambient=0.58):
    a = np.asarray(im).astype(float)
    yy, xx = np.mgrid[0:H, 0:W]
    L = np.ones((H, W, 3)) * ambient * np.array([0.84, 0.9, 1.12])
    for cx, cy, r, col, k in sources:
        f = np.clip(1 - np.hypot(xx - cx, (yy - cy) * 1.15) / r, 0, 1) ** 1.5 * k
        L += f[..., None] * np.array(col)
    a[..., :3] = np.clip(a[..., :3] * L, 0, 255)
    return Image.fromarray(a.astype(np.uint8), "RGBA")


def build(step):
    bg = Image.open(os.path.join(OUT, "chunk_preview_graveyard_1.png")).convert("RGBA").crop((80, 170, 80 + W, 170 + H))
    # xoa dau + danh dau prop spawn trong anh preview chunk: phu bang co nen
    grass = Image.open(os.path.join(OUT, "tilesheet_C_graveyard.png")).convert("RGBA").crop((5 * 32, 0, 6 * 32, 32))
    a = np.asarray(bg)
    red = (a[..., 0] > 200) & (a[..., 1] < 90)
    for y, x in zip(*np.nonzero(red)):
        bg.putpixel((int(x), int(y)), grass.getpixel((int(x) % 32, int(y) % 32)))
    P = lambda k: load(f"Props_Graveyard/{k}.png")
    player = load("A_zombie_to/Characters/player_idle.png")
    zw = [load(f"A_zombie_to/Enemies/enemy_zombie_walk_{i}.png") for i in range(2)]
    zidle = load("A_zombie_to/Enemies/enemy_zombie_idle.png")
    flip = lambda im: im.transpose(Image.FLIP_LEFT_RIGHT)
    shard = load("Projectiles/proj_iceshard.png")
    # (ten, anh, x trai, y chan, co bong?)  - zombie ben phai player quay trai (flip)
    items = [
        ("tomb_round", P("tomb_round"), 30, 70, False), ("tomb_tall", P("tomb_tall"), 66, 64, False),
        ("cross_stone", P("cross_stone"), 100, 72, False), ("tomb_broken", P("tomb_broken"), 136, 70, False),
        ("tree_face", P("tree_face"), 400, 110, False), ("tree_dead", P("tree_dead"), -14, 262, False),
        ("torch", P("torch_0"), 170, 92, False), ("torch", P("torch_1"), 330, 210, False),
        ("lantern", P("lantern"), 60, 200, False), ("rock_big", P("rock_big"), 300, 70, False),
        ("skull_pile", P("skull_pile"), 420, 250, False), ("bush_dead", P("bush_dead"), 250, 262, False),
        ("cross_wood", P("cross_wood"), 440, 175, False),
        ("player", player, 222, 158, True),
        ("zombie", flip(zw[0]), 300, 140, True), ("zombie", flip(zidle), 336, 168, True),
        ("zombie", flip(zw[1]), 282, 196, True), ("zombie", flip(zw[0]), 372, 132, True),
        ("zombie", zw[1], 150, 150, True), ("zombie", zidle, 120, 186, True), ("zombie", zw[0], 176, 222, True),
        ("zombie", zidle, 214, 96, True), ("zombie", flip(zw[1]), 250, 246, True),
    ]
    for k in range(5): items.append(("fence", P("fence" if k < 4 else "fence_post"), 300 + k * 32 - 120, 30, False))
    sh_s, sh_b = shadow_sprite(22, 7), shadow_sprite(26, 8)
    for name, im, x, by, has_sh in sorted(items, key=lambda t: t[3]):
        if step >= 2 and has_sh:
            s = sh_b if name == "player" else sh_s
            bg.alpha_composite(s, (int(x + im.width / 2 - s.width / 2), by - s.height + 3))
        bg.alpha_composite(im, (int(x), by - im.height))
    for sx, sy in ((262, 130), (296, 152)):                                # bang bay ve phia zombie ben phai
        bg.alpha_composite(shard, (sx, sy))
    if step >= 3:
        bg = lights(bg, [
            (177, 62, 95, (1.0, 0.6, 0.28), 0.95),     # duoc tren
            (337, 178, 95, (1.0, 0.6, 0.28), 0.95),    # duoc duoi
            (73, 168, 70, (1.0, 0.75, 0.4), 0.75),     # den long
            (240, 140, 80, (0.6, 0.58, 0.55), 0.5),    # quang quanh player
            (275, 140, 22, (0.4, 0.7, 1.0), 0.6),      # bang phat sang nhe
        ])
    return bg


if __name__ == "__main__":
    os.makedirs(SHADOWS, exist_ok=True)
    gy.save(shadow_sprite(22, 7), os.path.join(SHADOWS, "shadow_small.png"))
    gy.save(shadow_sprite(26, 8), os.path.join(SHADOWS, "shadow_player.png"))
    gy.save(shadow_sprite(40, 10), os.path.join(SHADOWS, "shadow_big.png"))
    names = ["1_goc", "2_bong", "3_bong_den"]
    shots = []
    for i, n in enumerate(names):
        im = build(i + 1); shots.append(im)
        gy.save(im.resize((W * 3, H * 3), Image.NEAREST), os.path.join(OUT, f"mock_scene_{n}.png"))
    cmp_ = Image.new("RGBA", (W, H * 3 + 8), (10, 10, 14, 255))
    for i, im in enumerate(shots): cmp_.paste(im, (0, i * (H + 4)))
    gy.save(cmp_.resize((W * 2, cmp_.height * 2), Image.NEAREST), os.path.join(OUT, "mock_scene_compare.png"))
    print("ok")
