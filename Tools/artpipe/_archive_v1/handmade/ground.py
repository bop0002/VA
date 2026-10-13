"""Nen nghia dia: co nen (4 bien the) + dat tim (autotile 47 o). Mau lay tu inbox/tilemap.jpg (Gemini).

Texture Gemini (inbox/tilemap.jpg) lien mep nhung lap moi 64px rat lo va mat chi tiet nho khi thu ve 32px,
nen o day ve lai bang code: co gan nhu tron + chi tiet thua, mang dat tim lam bang autotile (1 o le = mang tron,
nhieu o = duong / vung) -> dat duoc o bat ky dau, het lap pattern.
"""
import os, sys
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import artpipe, autotile

T = 32
OUT = artpipe.OUT_DIR


def rgb(h):
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.uint8)


GRASS, GRASS_DK, GRASS_LT, GRASS_HI = rgb("2f414d"), rgb("1f2d33"), rgb("3e5a5a"), rgb("5a7a6a")
DIRT, DIRT_DK, DIRT_LT, MOSS = rgb("2f2742"), rgb("2a2138"), rgb("3a324e"), rgb("2e4a2a")
PEBBLE, PEBBLE_SH = rgb("4c4468"), rgb("1a1424")


def put(img, y, x, col):
    img[y % img.shape[0], x % img.shape[1]] = col   # modulo -> chi tiet vat qua mep tu quan lai -> lien mep


def grass_tile(seed, blades, specks, pebbles):
    rng = np.random.default_rng(seed)
    img = np.empty((T, T, 3), np.uint8); img[:] = GRASS
    for _ in range(specks):                          # dom toi lam nen bot phang
        y, x = rng.integers(0, T, 2); put(img, y, x, GRASS_DK)
        if rng.random() < 0.4: put(img, y, x + 1, GRASS_DK)
    for _ in range(blades):                          # ngon co: 2px sang + bong toi duoi chan
        y, x = rng.integers(0, T, 2)
        put(img, y, x, GRASS_HI if rng.random() < 0.25 else GRASS_LT); put(img, y + 1, x, GRASS_LT)
        put(img, y + 2, x, GRASS_DK)
        if rng.random() < 0.5: put(img, y + 1, x + 1, GRASS_LT); put(img, y + 2, x + 1, GRASS_DK)
    for _ in range(pebbles):                         # soi tim nho
        y, x = rng.integers(0, T, 2); put(img, y, x, PEBBLE); put(img, y + 1, x, PEBBLE_SH)
    return img


def dirt_texture(seed=11, size=64):
    rng = np.random.default_rng(seed)
    img = np.empty((size, size, 3), np.uint8); img[:] = DIRT
    for _ in range(size * 6):
        y, x = rng.integers(0, size, 2); put(img, y, x, DIRT_DK if rng.random() < 0.6 else DIRT_LT)
    for _ in range(5):                               # cum reu
        y, x = rng.integers(0, size, 2)
        for dy, dx in ((0, 0), (0, 1), (1, 0), (1, 1), (0, 2), (-1, 1)):
            if rng.random() < 0.8: put(img, y + dy, x + dx, MOSS)
    for _ in range(4):
        y, x = rng.integers(0, size, 2); put(img, y, x, PEBBLE); put(img, y + 1, x, PEBBLE_SH)
    return img


VARIANTS = [  # (seed, blades, specks, pebbles) - 0 tron nhat, dung nhieu nhat
    (1, 6, 14, 0), (2, 10, 18, 1), (3, 14, 22, 1), (4, 8, 16, 2),
]


def extract_decals(native_path, min_px=20):
    """Tach cac mang dat tim tu texture Gemini (da qua artpipe tile, lien mep) thanh sprite trong suot.
    Lat 3x3 de mang vat qua mep van nguyen ven; chi lay mang co tam nam o ban giua."""
    tex = np.asarray(Image.open(native_path).convert("RGB"))
    n = tex.shape[0]
    big = np.tile(tex, (3, 3, 1))
    grass_cols = {tuple(c) for c in (GRASS, GRASS_DK, GRASS_LT, GRASS_HI)}
    fg = np.array([[tuple(p) not in grass_cols for p in row] for row in big])
    comps, labels = artpipe.components(fg, min_px)
    decals = []
    for lab, (x0, y0, x1, y1), _ in comps:
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        if not (n <= cx < 2 * n and n <= cy < 2 * n):
            continue
        m = labels[y0:y1, x0:x1] == lab
        rgba = np.zeros((y1 - y0, x1 - x0, 4), np.uint8)
        rgba[m, :3] = big[y0:y1, x0:x1][m]; rgba[m, 3] = 255
        decals.append(Image.fromarray(rgba, "RGBA"))
    return decals

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    grass = []
    for i, v in enumerate(VARIANTS):
        g = grass_tile(*v); grass.append(g)
        Image.fromarray(g).save(os.path.join(OUT, f"tile_grass_{i}.png"))
    Image.fromarray(dirt_texture()).save(os.path.join(OUT, "tile_dirt_full.png"))
    Image.fromarray(grass[0]).save(os.path.join(OUT, "tile_grass_full.png"))
    autotile.build(os.path.join(OUT, "tile_grass_full.png"), os.path.join(OUT, "tile_dirt_full.png"), "auto_dirt")

    # preview map 20x12: co ngau nhien (bien the 0 chiem 55%) + vai mang dat + 1 duong
    W, H = 20, 12
    rng = np.random.default_rng(5)
    sheet = Image.open(os.path.join(OUT, "auto_dirt.png"))
    cfgs = autotile.blob_configs()
    lut = {tuple(sorted(d for d in autotile.DIRS if c[d])): i for i, c in enumerate(cfgs)}
    dirt = np.zeros((H, W), bool)
    dirt[7, 2:15] = True; dirt[3:8, 14] = True                              # duong dat
    dirt[9:11, 16:18] = True                                                 # vung 2x2
    m = Image.new("RGB", (W * T, H * T))
    for y in range(H):
        for x in range(W):
            if dirt[y, x]:
                nb = {d: (0 <= y + dy < H and 0 <= x + dx < W and dirt[y + dy, x + dx]) for d, (dx, dy) in autotile.DIRS.items()}
                for c, (a, b) in autotile.CORNERS.items(): nb[c] = nb[c] and nb[a] and nb[b]
                i = lut[tuple(sorted(d for d in autotile.DIRS if nb[d]))]
                m.paste(sheet.crop(((i % 8) * T, (i // 8) * T, (i % 8 + 1) * T, (i // 8 + 1) * T)), (x * T, y * T))
            else:
                v = rng.choice(4, p=[.55, .2, .1, .15])
                m.paste(Image.fromarray(grass[v]), (x * T, y * T))
    # decal mang dat tu Gemini, rai ngau nhien (khong theo luoi) tranh duong dat
    decals = extract_decals(os.path.join(OUT, "tile_ground_full.png"))
    for i, d in enumerate(decals):
        d.save(os.path.join(OUT, f"decor_patch_{i}.png"))
    m = m.convert("RGBA")
    for _ in range(9):
        d = decals[rng.integers(len(decals))]
        if rng.random() < 0.5: d = d.transpose(Image.FLIP_LEFT_RIGHT)
        x, y = rng.integers(0, W * T - d.width), rng.integers(0, H * T - d.height)
        if dirt[y // T: (y + d.height) // T + 1, x // T: (x + d.width) // T + 1].any():
            continue
        m.alpha_composite(d, (int(x), int(y)))
    m.resize((m.width * 2, m.height * 2), Image.NEAREST).save(os.path.join(OUT, "..", "ground_preview.png"))
    print(f"ok tile_grass_0..3, tile_dirt_full, auto_dirt (47), decor_patch_0..{len(decals) - 1}, ground_preview.png")
