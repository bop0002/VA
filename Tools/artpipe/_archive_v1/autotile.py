"""autotile - sinh bo 47-tile blob (cho Unity RuleTile) tu 2 texture: nen (co) va lop phu (dat/duong).

Dung:
  python Tools/artpipe/autotile.py --base out/tile_grass_full.png --over out/tile_dirt_full.png --name auto_dirt

Moi o la "o dat". 8 hang xom (N,E,S,W,NE,SE,SW,NW) quyet dinh mep: canh nao khong phai dat thi dat lui vao,
goc cheo chi tinh khi 2 canh ke deu la dat (quy tac blob -> 47 cau hinh).
Mep: blur truong 3x3 o roi threshold -> goc bo tron tu nhien. Gon song o mep bang 0 tai goc o -> o canh nhau khop.
"""
import argparse, json, os
import numpy as np
from PIL import Image
import artpipe

T = 32
DIRS = {"N": (0, -1), "NE": (1, -1), "E": (1, 0), "SE": (1, 1), "S": (0, 1), "SW": (-1, 1), "W": (-1, 0), "NW": (-1, -1)}
CORNERS = {"NE": ("N", "E"), "SE": ("S", "E"), "SW": ("S", "W"), "NW": ("N", "W")}


def blob_configs():
    """47 cau hinh hop le: goc cheo chi co nghia khi 2 canh ke deu co."""
    out = []
    for m in range(256):
        n = {d: bool(m >> i & 1) for i, d in enumerate(DIRS)}
        if any(n[c] and not (n[a] and n[b]) for c, (a, b) in CORNERS.items()):
            continue
        out.append(n)
    assert len(out) == 47, len(out)
    return out


def box_blur(f, r, passes=3):
    for _ in range(passes):
        for axis in (0, 1):
            c = np.cumsum(np.pad(f, [(r + 1, r) if a == axis else (0, 0) for a in (0, 1)], mode="edge"), axis=axis)
            f = (np.take(c, range(2 * r + 1, c.shape[axis]), axis=axis) - np.take(c, range(0, c.shape[axis] - 2 * r - 1), axis=axis)) / (2 * r + 1)
    return f


def mask_for(n, inset=0.6, wobble=0.26):
    """Mask 32x32: True = dat."""
    field = np.zeros((3 * T, 3 * T))
    field[T:2 * T, T:2 * T] = 1
    for d, (dx, dy) in DIRS.items():
        if n[d]:
            field[(1 + dy) * T:(2 + dy) * T, (1 + dx) * T:(2 + dx) * T] = 1
    f = box_blur(field, 3)[T:2 * T, T:2 * T]
    x = np.arange(T)
    # gon song: sin(k*pi*x/(T-1)) = 0 tai x=0 va x=T-1 -> mep khop giua 2 o dat canh nhau
    wx = np.sin(3 * np.pi * x / (T - 1)) * 0.6 + np.sin(5 * np.pi * x / (T - 1)) * 0.4
    noise = wobble * (wx[None, :] + wx[:, None]) / 2
    return f > inset + noise


def shade(color, pal, k):
    return pal[artpipe.nearest(np.clip(np.array([color]) * k, 0, 255).astype(int), pal)[0]]


def build(base, over, name):
    pal = artpipe.load_palette()
    b = np.asarray(Image.open(base).convert("RGB"))[:T, :T].astype(int)
    o = np.asarray(Image.open(over).convert("RGB"))[:T, :T].astype(int)
    vals, cnt = np.unique(b.reshape(-1, 3), axis=0, return_counts=True)
    base_col = vals[cnt.argmax()]                     # mau co chu dao
    cfgs = blob_configs()
    cols = 8
    sheet = Image.new("RGBA", (cols * T, -(-len(cfgs) // cols) * T))
    meta = []
    for i, n in enumerate(cfgs):
        m = mask_for(n)
        img = np.where(m[..., None], o, b).copy()
        pad = np.pad(m, 1, mode="edge")
        near_grass = m & ~(pad[:-2, 1:-1] & pad[2:, 1:-1] & pad[1:-1, :-2] & pad[1:-1, 2:])
        near_dirt = ~m & (pad[:-2, 1:-1] | pad[2:, 1:-1] | pad[1:-1, :-2] | pad[1:-1, 2:])
        # rang cua co: ngon co nho 1-2px chia vao dat (hash theo toa do -> moi o cung pattern, ko lech)
        teeth = np.zeros_like(m)
        for y, x in zip(*np.nonzero(near_dirt)):
            hsh = (x * 73856093 ^ y * 19349663) % 7
            if hsh < 3:
                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    yy, xx = y + dy, x + dx
                    if 0 <= yy < T and 0 <= xx < T and m[yy, xx]:
                        teeth[yy, xx] = True
                        if hsh == 0 and 0 <= yy + dy < T and 0 <= xx + dx < T and m[yy + dy, xx + dx]:
                            teeth[yy + dy, xx + dx] = True
        img[teeth] = shade(base_col, pal, 1.25)
        m = m & ~teeth
        pad = np.pad(m, 1, mode="edge")
        near_grass = m & ~(pad[:-2, 1:-1] & pad[2:, 1:-1] & pad[1:-1, :-2] & pad[1:-1, 2:])
        for y, x in zip(*np.nonzero(near_grass)):
            img[y, x] = shade(img[y, x], pal, 0.7)     # mep dat toi -> cam giac lom
        for y, x in zip(*np.nonzero(near_dirt)):
            img[y, x] = shade(img[y, x], pal, 1.25)    # vien co sang
        tile = Image.fromarray(img.astype(np.uint8)).convert("RGBA")
        sheet.paste(tile, ((i % cols) * T, (i // cols) * T))
        meta.append({"index": i, "neighbors": {d: n[d] for d in DIRS}})
    os.makedirs(artpipe.OUT_DIR, exist_ok=True)
    sheet.save(os.path.join(artpipe.OUT_DIR, f"{name}.png"))
    json.dump({"tileSize": T, "columns": cols, "tiles": meta}, open(os.path.join(artpipe.OUT_DIR, f"{name}.json"), "w"), indent=1)
    preview_map(sheet, cfgs, b, name)
    print(f"ok {name}: {len(cfgs)} tile -> out/{name}.png + .json")


def preview_map(sheet, cfgs, base, name, w=14, h=10, seed=4):
    """Ve thu 1 map ngau nhien (duong dat + vung dat) dung bo tile vua sinh de soi mep."""
    rng = np.random.default_rng(seed)
    grid = np.zeros((h, w), bool)
    grid[4:6, :] = True; grid[:, 6:8] = True               # nga tu duong
    for _ in range(3):
        y, x = rng.integers(1, h - 3), rng.integers(1, w - 3); grid[y:y + 3, x:x + 3] = True
    grid[2, 11] = True                                     # 1 o le
    lut = {tuple(sorted(d for d in DIRS if c[d])): i for i, c in enumerate(cfgs)}
    img = Image.new("RGBA", (w * T, h * T))
    btile = Image.fromarray(base.astype(np.uint8)).convert("RGBA")
    for y in range(h):
        for x in range(w):
            if not grid[y, x]:
                img.paste(btile, (x * T, y * T)); continue
            nb = {d: (0 <= y + dy < h and 0 <= x + dx < w and grid[y + dy, x + dx]) for d, (dx, dy) in DIRS.items()}
            for c, (a, b) in CORNERS.items():
                nb[c] = nb[c] and nb[a] and nb[b]
            i = lut[tuple(sorted(d for d in DIRS if nb[d]))]
            img.paste(sheet.crop(((i % 8) * T, (i // 8) * T, (i % 8 + 1) * T, (i // 8 + 1) * T)), (x * T, y * T))
    img.resize((img.width * 2, img.height * 2), Image.NEAREST).save(os.path.join(artpipe.OUT_DIR, f"{name}_map_preview.png"))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True); ap.add_argument("--over", required=True); ap.add_argument("--name", default="autotile")
    a = ap.parse_args()
    build(a.base, a.over, a.name)
