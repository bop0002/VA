"""artpipe - bien anh Gemini (nen magenta) thanh sprite pixel art sach theo Style Bible.

Dung:
  python Tools/artpipe/artpipe.py extract <anh> [--height 28] [--frame 32] [--name enemy_zombie]
  python Tools/artpipe/artpipe.py palette-test <anh>

Pipeline: tach nen chroma -> tach tung sprite (connected components) -> downsample ve chieu cao dich
(mode pooling) -> ep palette -> ve lai vien 1px -> dat vao khung (pivot bottom-center) -> xuat png + json + preview.
"""
import argparse, json, os, sys
from collections import Counter, deque
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(ROOT, "out")
PALETTE_FILE = os.path.join(ROOT, "palettes", "vaclone.hex")
OUTLINE = (0x1a, 0x14, 0x24)


def load_palette(path=PALETTE_FILE):
    hexes = [l.strip() for l in open(path) if l.strip() and not l.startswith("#")]
    return np.array([[int(h[i:i + 2], 16) for i in (0, 2, 4)] for h in hexes], dtype=np.int32)


# ---------- 1. tach nen ----------
def chroma_mask(rgb, thresh=70):
    """True = foreground. Nen magenta (ke ca bong do magenta toi): R va B cao hon G nhieu."""
    r, g, b = rgb[..., 0].astype(int), rgb[..., 1].astype(int), rgb[..., 2].astype(int)
    magenta = np.minimum(r, b) - g
    balanced = np.abs(r - b) < 90          # magenta that thi R ~ B
    return ~((magenta > thresh) & balanced)


def components(mask, min_area):
    """Connected components (4-neighbor). Tra ve list bbox (x0,y0,x1,y1) va label map."""
    h, w = mask.shape
    labels = np.zeros((h, w), np.int32)
    boxes, cur = [], 0
    for y0 in range(h):
        row = mask[y0]
        for x0 in np.nonzero(row & (labels[y0] == 0))[0]:
            if labels[y0, x0]:
                continue
            cur += 1
            q = deque([(y0, x0)]); labels[y0, x0] = cur
            xs, ys, n = [x0, x0], [y0, y0], 0
            while q:
                y, x = q.popleft(); n += 1
                xs[0] = min(xs[0], x); xs[1] = max(xs[1], x); ys[0] = min(ys[0], y); ys[1] = max(ys[1], y)
                for ny, nx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
                    if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not labels[ny, nx]:
                        labels[ny, nx] = cur; q.append((ny, nx))
            if n >= min_area:
                boxes.append((cur, (xs[0], ys[0], xs[1] + 1, ys[1] + 1), n))
    return boxes, labels


def watermark_mask(rgb):
    """Logo ✦ cua Gemini: trang ngai hong/xam, nam o goc phai duoi. Chi xet vung do de khong an mat
    mau sang that cua sprite."""
    H, W = rgb.shape[:2]
    m = np.zeros((H, W), bool)
    y0, x0 = int(H * 0.75), int(W * 0.8)
    r, g, b = (rgb[y0:, x0:, i].astype(int) for i in range(3))
    tint = (np.minimum(r, b) - g > 12) & (np.abs(r - b) < 40) & (g > 120)   # hong nhat / xam hong
    grey = (np.abs(r - g) < 18) & (np.abs(b - g) < 18) & (g > 120)          # logo xam tren anh khong magenta
    m[y0:, x0:] = tint | grey
    return m


def merge_boxes(boxes, gap):
    """Gom cac component co bbox cach nhau <= gap px thanh 1 nhom. Tra ve [(labels, bbox, area)]."""
    groups = [([lab], list(bb), n) for lab, bb, n in boxes]
    merged = True
    while merged:
        merged = False
        for i in range(len(groups)):
            for j in range(i + 1, len(groups)):
                a, b = groups[i][1], groups[j][1]
                if a[0] - gap <= b[2] and b[0] - gap <= a[2] and a[1] - gap <= b[3] and b[1] - gap <= a[3]:
                    labs = groups[i][0] + groups[j][0]
                    bb = [min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3])]
                    groups[i] = (labs, bb, groups[i][2] + groups[j][2])
                    del groups[j]; merged = True
                    break
            if merged:
                break
    return [(g[0], tuple(g[1]), g[2]) for g in groups]


# ---------- 2. do luoi pixel gia ----------
def detect_grid(rgb, smin=5, smax=24):
    """Tim kich thuoc khoi pixel gia s va offset. Tra ve list ung vien (score, s, ox, oy) giam dan."""
    a = rgb.astype(np.int32)
    # canh doc (doi mau giua 2 cot) -> profile theo x; canh ngang -> profile theo y
    px = (np.abs(np.diff(a, axis=1)).sum(-1) > 60).sum(axis=0).astype(float)
    py = (np.abs(np.diff(a, axis=0)).sum(-1) > 60).sum(axis=1).astype(float)
    cands = []
    for s in np.arange(smin, smax, 0.25):
        def best(prof):
            n = len(prof)
            return max((prof[np.round(np.arange(o, n - 1, s)).astype(int)].sum() / (n / s), o)
                       for o in np.arange(0, s, 0.5))
        sx, ox = best(px); sy, oy = best(py)
        cands.append((sx + sy, float(s), float(ox), float(oy)))
    cands.sort(reverse=True)
    return cands


def pick_grid(cands, bbox_h, height):
    """Trong cac ung vien manh (>=85% best) - thuong la luoi that va boi/uoc cua no (8, 16, 10.25, 20.5) -
    chon cai cho chieu cao native >= height va gan height nhat. Khong co -> None (Gemini ve pixel khong deu,
    caller thu nho thang tu anh nguon)."""
    top = cands[0][0]
    ok = [c for c in cands if c[0] >= top * 0.85 and bbox_h / c[1] >= height * 0.97]
    return min(ok, key=lambda c: bbox_h / c[1]) if ok else None


# ---------- 3. downsample ----------
def mode_downsample(rgb, mask, out_w, out_h, pal, dark_bias=0.45):
    """Moi o lay mau xuat hien nhieu nhat (sau khi ep palette) -> giu vien va mang mau sac net."""
    h, w = mask.shape
    lum = pal @ np.array([299, 587, 114]) // 1000
    idx = nearest(rgb.reshape(-1, 3), pal).reshape(h, w)
    out_idx = np.full((out_h, out_w), -1, np.int32)
    for oy in range(out_h):
        y0, y1 = int(oy * h / out_h), max(int((oy + 1) * h / out_h), int(oy * h / out_h) + 1)
        for ox in range(out_w):
            x0, x1 = int(ox * w / out_w), max(int((ox + 1) * w / out_w), int(ox * w / out_w) + 1)
            m = mask[y0:y1, x0:x1]
            if m.mean() < 0.5:
                continue
            common = Counter(idx[y0:y1, x0:x1][m].tolist()).most_common(2)
            c = common[0][0]
            # chi tiet manh (xuong, mat) hay bi vien toi lan at -> uu tien mau sang neu no du nhieu
            if len(common) > 1 and lum[c] < 60 and lum[common[1][0]] > lum[c] + 60 \
                    and common[1][1] >= common[0][1] * dark_bias:
                c = common[1][0]
            out_idx[oy, ox] = c
    return out_idx


def nearest(colors, pal):
    """Mau gan nhat trong palette theo khoang cach 'redmean' (gan voi cam nhan mat)."""
    c = colors[:, None, :].astype(np.int32)
    p = pal[None, :, :]
    rmean = (c[..., 0] + p[..., 0]) // 2
    d = c - p
    dist = ((512 + rmean) * d[..., 0] ** 2 >> 8) + 4 * d[..., 1] ** 2 + ((767 - rmean) * d[..., 2] ** 2 >> 8)
    return dist.argmin(1)


# ---------- 3. vien ----------
def enforce_outline(idx, pal):
    """Pixel foreground nam sat nen -> mau vien. Dam bao vien ngoai dung 1px, dong nhat."""
    fg = idx >= 0
    pad = np.pad(fg, 1)
    edge = fg & ~(pad[:-2, 1:-1] & pad[2:, 1:-1] & pad[1:-1, :-2] & pad[1:-1, 2:])
    out_i = int(nearest(np.array([OUTLINE]), pal)[0])
    idx = idx.copy(); idx[edge] = out_i
    return idx


def to_rgba(idx, pal):
    h, w = idx.shape
    out = np.zeros((h, w, 4), np.uint8)
    fg = idx >= 0
    out[fg, :3] = pal[idx[fg]]; out[fg, 3] = 255
    return Image.fromarray(out, "RGBA")


def place_in_frame(sprite, frame):
    """Pivot bottom-center: chan cham hang pixel thu 2 tu duoi len."""
    fw, fh = frame
    canvas = Image.new("RGBA", (fw, fh), (0, 0, 0, 0))
    x = (fw - sprite.width) // 2
    y = fh - 1 - sprite.height
    canvas.alpha_composite(sprite, (max(x, 0), max(y, 0)))
    return canvas


def preview(img, scale=8, bg=(0x2f, 0x41, 0x4d)):
    p = Image.new("RGBA", img.size, bg + (255,)); p.alpha_composite(img)
    return p.resize((img.width * scale, img.height * scale), Image.NEAREST)


# ---------- lenh ----------
def extract(path, height, frame, name, min_area_ratio=0.01, gap=0):
    pal = load_palette()
    rgb = np.asarray(Image.open(path).convert("RGB"))
    mask = chroma_mask(rgb)
    H, W = mask.shape
    total = H * W
    mask &= ~watermark_mask(rgb)
    if gap > 0:   # prop nhieu manh (xuong rai, da + soi): lay ca manh nho roi gom theo khoang cach
        boxes, labels = components(mask, 30)
        boxes = merge_boxes(boxes, gap)
        boxes = [b for b in boxes if b[2] >= total * min_area_ratio * 0.2]
    else:
        boxes, labels = components(mask, int(total * min_area_ratio))
        boxes = [([lab], bb, n) for lab, bb, n in boxes]
    # bo logo Gemini o goc phai duoi (nho, sat goc)
    boxes = [b for b in boxes if not (b[1][0] > W * 0.85 and b[1][1] > H * 0.75 and b[2] < total * 0.01)]
    # thu tu doc: theo hang (y) roi cot (x) -> anh luoi 4x3 ra dung thu tu
    row_h = max(1, min(b[1][3] - b[1][1] for b in boxes))
    boxes.sort(key=lambda b: (round(((b[1][1] + b[1][3]) / 2) / (row_h * 1.5)), b[1][0]))
    os.makedirs(OUT_DIR, exist_ok=True)
    results = []
    max_h = max(b[1][3] - b[1][1] for b in boxes)
    grid = pick_grid(detect_grid(rgb), max_h, height)
    if grid:
        _, s, ox, oy = grid
    else:   # luoi khong ro -> o = bbox/height, thu nho thang
        s, ox, oy = max_h / height, 0.0, 0.0
        print(f"(i) khong do duoc luoi pixel ro rang -> thu nho thang, o {s:.2f}px")
    # luot 1: chup tung sprite theo luoi native (khong mat chi tiet)
    natives = []
    for labs, (x0, y0, x1, y1), _ in boxes:
        gx0 = int(ox + np.floor((x0 - ox) / s) * s); gy0 = int(oy + np.floor((y0 - oy) / s) * s)
        nw = int(np.ceil((x1 - gx0) / s)); nh = int(np.ceil((y1 - gy0) / s))
        gx1 = min(W, int(round(gx0 + nw * s))); gy1 = min(H, int(round(gy0 + nh * s)))
        gx0, gy0 = max(gx0, 0), max(gy0, 0)
        sub_mask = np.isin(labels[gy0:gy1, gx0:gx1], labs)
        idx = mode_downsample(rgb[gy0:gy1, gx0:gx1], sub_mask, nw, nh, pal)
        rows = np.nonzero((idx >= 0).any(1))[0]; cols = np.nonzero((idx >= 0).any(0))[0]
        natives.append(idx[rows[0]:rows[-1] + 1, cols[0]:cols[-1] + 1])
    # luot 2: 1 ti le chung cho ca anh -> sprite to cao nhat = --height, giu ti le giua cac con
    ratio = min(1.0, height / max(n.shape[0] for n in natives))
    for i, idx in enumerate(natives):
        nh, nw = idx.shape
        native_h = nh
        if ratio < 1.0:
            nrgb = np.zeros((nh, nw, 3), np.uint8); nm = idx >= 0
            nrgb[nm] = pal[idx[nm]]
            idx = mode_downsample(nrgb, nm, max(1, round(nw * ratio)), max(1, round(nh * ratio)), pal)
        idx = enforce_outline(idx, pal)
        spr = to_rgba(idx, pal)
        spr = spr.crop(spr.getbbox())
        fw = max(frame, spr.width + 2); fh = max(frame, spr.height + 1)
        framed = place_in_frame(spr, (fw, fh))
        stem = f"{name}_{i:02d}" if len(boxes) > 1 else name
        png = os.path.join(OUT_DIR, stem + ".png")
        framed.save(png)
        preview(framed).save(os.path.join(OUT_DIR, stem + "_preview.png"))
        meta = {"name": stem, "frame": [fw, fh], "pivot": [0.5, 1 / fh], "ppu": 32,
                "source": os.path.basename(path), "spriteSize": [spr.width, spr.height],
                "grid": s, "nativeHeight": native_h}
        json.dump(meta, open(os.path.join(OUT_DIR, stem + ".json"), "w"), indent=2)
        results.append((stem, spr.size, s, native_h))
    for r in results:
        print(f"ok {r[0]} sprite {r[1]} grid {r[2]}px native_h {r[3]}")
    if ratio < 1.0:
        print(f"(!) native cao hon --height {height} -> thu nho x{ratio:.2f}, co the mat chi tiet manh")
    return results


def make_seamless(idx, band=0.3, seed=0):
    """Lam lien mep ma KHONG tron mau (tron se sinh mau ngoai palette).
    roll(T, N/2) lien mep o bien nhung co seam o giua; T lien o giua nhung seam o bien.
    Lay T o vung giua, roll o vung bien, vung chuyen tiep chon pixel ngau nhien theo trong so."""
    h, w = idx.shape
    rolled = np.roll(idx, (h // 2, w // 2), axis=(0, 1))
    yy, xx = np.mgrid[0:h, 0:w]
    # khoang cach toi bien gan nhat, chuan hoa 0 (bien) .. 1 (tam)
    d = np.minimum(np.minimum(yy, h - 1 - yy) / (h / 2), np.minimum(xx, w - 1 - xx) / (w / 2))
    weight = np.clip((d - (0.5 - band)) / (2 * band), 0, 1)   # 0 o bien -> 1 o tam
    rng = np.random.default_rng(seed)
    return np.where(rng.random((h, w)) < weight, idx, rolled)


def tile(path, name, tiles, tile_size=32, seamless=True):
    pal = load_palette()
    img = Image.open(path).convert("RGB")
    side = min(img.size)                                       # cat vuong o giua
    img = img.crop(((img.width - side) // 2, (img.height - side) // 2,
                    (img.width + side) // 2, (img.height + side) // 2))
    rgb = np.asarray(img)
    grid = pick_grid(detect_grid(rgb), side, tiles * tile_size)
    _, s, ox, oy = grid if grid else (0, side / (tiles * tile_size), 0.0, 0.0)
    n = int(round(side / s))
    # offset le (0.5px) khong duoc lam hut 1 o; neu vuot anh thi dich vao trong
    x0 = min(int(round(ox)) % int(round(s)), max(0, side - int(n * s)))
    y0 = min(int(round(oy)) % int(round(s)), max(0, side - int(n * s)))
    if int(n * s) > side:
        n -= 1
    full = np.ones((int(n * s), int(n * s)), bool)
    idx = mode_downsample(rgb[y0:y0 + int(n * s), x0:x0 + int(n * s)], full, n, n, pal)
    native = n
    target = tiles * tile_size
    if n != target:   # dua ve dung N = tiles*32 (thu nho dung mode; phong to dung nearest)
        if n > target:
            nrgb = pal[idx].astype(np.uint8)
            idx = mode_downsample(nrgb, np.ones((n, n), bool), target, target, pal)
        else:
            idx = np.asarray(Image.fromarray(idx.astype(np.uint8)).resize((target, target), Image.NEAREST)).astype(np.int32)
    if seamless:
        idx = make_seamless(idx)
    os.makedirs(OUT_DIR, exist_ok=True)
    tex = to_rgba(idx, pal)
    tex.save(os.path.join(OUT_DIR, f"{name}_full.png"))
    k = 0
    for ty in range(tiles):
        for tx in range(tiles):
            tex.crop((tx * tile_size, ty * tile_size, (tx + 1) * tile_size, (ty + 1) * tile_size)) \
               .save(os.path.join(OUT_DIR, f"{name}_{k:02d}.png")); k += 1
    # preview: lap 3x3 de soi seam
    rep = Image.new("RGBA", (target * 3, target * 3))
    for i in range(3):
        for j in range(3):
            rep.paste(tex, (i * target, j * target))
    rep.resize((rep.width * 4, rep.height * 4), Image.NEAREST).save(os.path.join(OUT_DIR, f"{name}_tiled_preview.png"))
    print(f"ok {name}: grid {s}px native {native}x{native} -> {target}x{target}, {k} tile {tile_size}px"
          + ("" if native >= target else "  (!) native nho hon -> phong to nearest"))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("extract")
    e.add_argument("image"); e.add_argument("--height", type=int, default=28)
    e.add_argument("--frame", type=int, default=32); e.add_argument("--name", default=None)
    e.add_argument("--gap", type=int, default=0, help="gom manh roi cach nhau <= gap px (prop nhieu manh)")
    t = sub.add_parser("tile")
    t.add_argument("image"); t.add_argument("--name", default=None)
    t.add_argument("--tiles", type=int, default=2, help="so o moi chieu (2 -> texture 64x64 = 4 tile)")
    t.add_argument("--no-seamless", action="store_true")
    a = ap.parse_args()
    name = a.name or os.path.splitext(os.path.basename(a.image))[0]
    if a.cmd == "extract":
        extract(a.image, a.height, a.frame, name, gap=a.gap)
    elif a.cmd == "tile":
        tile(a.image, name, a.tiles, seamless=not a.no_seamless)


if __name__ == "__main__":
    main()
