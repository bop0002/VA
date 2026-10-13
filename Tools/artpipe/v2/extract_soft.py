"""v2 - tach sprite phong cach chibi mem (khong ep palette vaclone, khong ve vien moi).

Khac artpipe.extract: palette lay tu chinh anh (median-cut ~N mau), giu vien goc cua anh,
mac dinh giu do phan giai native (khong ep ve 32px). --height de thu nho neu can.
Dung: python Tools/artpipe/v2/extract_soft.py inbox/newchar.png --name player_soft [--height 32] [--colors 20]
Ra: v2/out/soft/<name>.png, <name>_x8.png (xem), <name>_ongrass.png (dat len tile A/B)
"""
import argparse, os, sys
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import artpipe

OUT = os.path.join(HERE, "out", "soft")


def largest_component(mask):
    comps, labels = artpipe.components(mask, 50)
    lab, (x0, y0, x1, y1), _ = max(comps, key=lambda c: c[2])
    return labels == lab, (x0, y0, x1, y1)


def extract(path, name, height=None, colors=20):
    rgb = np.asarray(Image.open(path).convert("RGB"))
    fg = artpipe.chroma_mask(rgb)          # True = nhan vat (khong phai nen magenta)
    fg, (x0, y0, x1, y1) = largest_component(fg)
    _, s, ox, oy = artpipe.detect_grid(rgb)[0]
    # luoi native: bat dau tu offset luoi, phu het bbox
    gx0 = ox + np.floor((x0 - ox) / s) * s; gy0 = oy + np.floor((y0 - oy) / s) * s
    nw = int(np.ceil((x1 - gx0) / s)); nh = int(np.ceil((y1 - gy0) / s))
    # palette tu chinh anh
    q = Image.fromarray(rgb[y0:y1, x0:x1]).quantize(colors, method=Image.MEDIANCUT)
    pal = np.array(q.getpalette()[:colors * 3]).reshape(-1, 3)
    idx = np.full((nh, nw), -1, np.int32)
    for j in range(nh):
        for i in range(nw):
            ya, yb = int(gy0 + j * s), int(gy0 + (j + 1) * s)
            xa, xb = int(gx0 + i * s), int(gx0 + (i + 1) * s)
            # chi lay loi o (bo 25% vien) tranh nhoe jpeg/khu rang cua
            m = int(s * 0.25)
            cell_m = fg[ya + m:yb - m, xa + m:xb - m]
            if cell_m.mean() < 0.5:
                continue
            px = rgb[ya + m:yb - m, xa + m:xb - m][cell_m].astype(int)
            d = ((px[:, None, :] - pal[None]) ** 2).sum(-1).argmin(1)
            idx[j, i] = np.bincount(d, minlength=len(pal)).argmax()
    img = np.zeros((nh, nw, 4), np.uint8)
    img[idx >= 0, :3] = pal[idx[idx >= 0]]; img[idx >= 0, 3] = 255
    spr = Image.fromarray(img, "RGBA"); spr = spr.crop(spr.getbbox())
    native = spr.size
    if height and spr.height > height:   # thu nho: nearest theo tam o (giu mau, khong blend)
        r = height / spr.height
        spr = spr.resize((max(1, round(spr.width * r)), height), Image.NEAREST)
    os.makedirs(OUT, exist_ok=True)
    spr.save(os.path.join(OUT, f"{name}.png"))
    spr.resize((spr.width * 8, spr.height * 8), Image.NEAREST).save(os.path.join(OUT, f"{name}_x8.png"))
    print(f"ok {name}: grid {s:.2f}px, native {native[0]}x{native[1]} -> {spr.size[0]}x{spr.size[1]}")
    return spr


def on_grass(sprs, name):
    """Dat sprite len 2 map A/B (ti le that 32px = 1 o) de so kich thuoc."""
    def demo(t):                                  # B_moonlit da vao out/_archive (2026-10-13)
        p = os.path.join(HERE, "out", f"terrain_{t}_demo.png")
        return p if os.path.exists(p) else os.path.join(HERE, "out", "_archive", f"terrain_{t}_demo.png")
    tiles = [Image.open(demo(t)).convert("RGBA").crop((0, 0, 192, 96)) for t in ("A_meadow", "B_moonlit")]
    sheet = Image.new("RGBA", (192, 192))
    for k, t in enumerate(tiles):
        x = 16
        for s in sprs:
            t.alpha_composite(s, (x, 80 - s.height)); x += s.width + 12
        sheet.paste(t, (0, k * 96))
    sheet.resize((sheet.width * 4, sheet.height * 4), Image.NEAREST).save(os.path.join(OUT, f"{name}_ongrass.png"))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("image"); ap.add_argument("--name", required=True)
    ap.add_argument("--height", type=int); ap.add_argument("--colors", type=int, default=20)
    a = ap.parse_args()
    extract(a.image, a.name, a.height, a.colors)
