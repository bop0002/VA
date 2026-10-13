"""Doi (enemy_bat) ve tay bang code, 2 frame vo canh. Concept: inbox lineup (Gemini), style: ref1 graveyard.
Ve nua trai (cot 0..15, cot 15 la truc giua) roi lat doi xung. Vien ngoai tu dong = Outline.
"""
import os, sys
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import artpipe

C = {  # ky tu -> mau trong vaclone.hex
    "O": "1a1424", "D": "2a2138",
    "B": "3a324e", "b": "4c4468", "h": "605b7c",      # than: Night bg ramp
    "W": "3a1a5e", "w": "6a2fa0", "v": "a860e0",      # mang canh: Magic ramp
    "R": "dc3943", "r": "ff8a7a", "M": "4a1428", "F": "fffbea",
}
HALF, H = 16, 22


def draw(top, bot):
    """top/bot: mep tren (xuong canh) va mep duoi (mang canh rang cua) cho cot 0..9."""
    g = np.full((H, HALF), ".", dtype="<U1")
    for c, (t, b) in enumerate(zip(top, bot)):
        g[t, c] = "h"                                   # xuong canh sang
        for y in range(t + 1, b + 1):
            g[y, c] = "v" if y == t + 1 and c >= 3 else ("w" if y < t + 4 else "W")
    # than: ellipse tam (15, 11)
    for y in range(H):
        for x in range(9, HALF):
            if ((x - 15) / 6.0) ** 2 + ((y - 11) / 6.2) ** 2 <= 1:
                g[y, x] = "h" if (y < 8 and x < 13) else ("B" if y > 13 or x < 11 else "b")
    for y, x in ((2, 11), (3, 11), (3, 12), (4, 11), (4, 12), (5, 11), (5, 12), (5, 13)):   # tai nhon
        g[y, x] = "b"
    g[4, 12] = g[5, 12] = "W"                            # trong tai
    g[8, 12] = g[9, 13] = g[9, 14] = "O"                 # long may cau (nghieng vao giua)
    g[10, 13], g[10, 14], g[11, 13], g[11, 14] = "R", "r", "R", "R"   # mat do phat sang
    g[13, 13], g[13, 14], g[13, 15] = "O", "M", "M"      # mieng ha
    g[14, 14], g[14, 15] = "F", "M"                      # nanh
    g[15, 15] = "O"
    return g


def render(g):
    full = np.concatenate([g, g[:, :-1][:, ::-1]], axis=1)  # lat doi xung, khong lap cot giua
    pal = artpipe.load_palette()
    hexes = [l.strip() for l in open(artpipe.PALETTE_FILE) if l.strip()]
    idx = np.full(full.shape, -1, np.int32)
    for k, hx in C.items():
        idx[full == k] = hexes.index(hx)
    idx = artpipe.enforce_outline(idx, pal)
    return artpipe.to_rgba(idx, pal)


FRAMES = {
    # canh gio len (chu V)
    "up":   ([1, 1, 2, 3, 4, 4, 5, 6, 7, 8], [4, 8, 10, 12, 10, 12, 14, 12, 13, 15]),
    # canh cup xuong
    "down": ([11, 10, 9, 9, 8, 8, 8, 8, 8, 8], [14, 17, 18, 16, 18, 19, 16, 17, 15, 14]),
}

if __name__ == "__main__":
    os.makedirs(artpipe.OUT_DIR, exist_ok=True)
    for i, (k, (t, b)) in enumerate(FRAMES.items()):
        spr = render(draw(t, b))
        spr = spr.crop(spr.getbbox())
        canvas = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
        canvas.alpha_composite(spr, ((32 - spr.width) // 2, 32 - 5 - spr.height))   # bay lo lung, chua cho bong do
        canvas.save(os.path.join(artpipe.OUT_DIR, f"enemy_bat_{i}.png"))
        print("ok", f"enemy_bat_{i}", k, spr.size)
