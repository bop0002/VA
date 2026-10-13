"""Player: lam sach ban idle (tu Gemini qua artpipe) va dung walk cycle bang code tu chinh ban idle.

Gemini walk 4 frame: mat moi frame mot kieu, chan gan nhu dung yen -> khong dung.
Walk o day: nang luan phien 1 ban chan 1px + nhun than 1px -> mat/trang phuc giong het idle.
Input: out/player_idle.png (python artpipe.py extract inbox/maincharacter.jpg --name player_idle --height 30)
"""
import os, sys
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import artpipe

OUT = artpipe.OUT_DIR
HEX = [l.strip() for l in open(artpipe.PALETTE_FILE) if l.strip()]


def c(h):
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)] + [255], np.uint8)


DARK, WHITE, BROW, SKIN, SKIN_SH = c("0d0912"), c("fffbea"), c("4a1428"), c("f6d2b0"), c("e0a07a")
LEGS_TOP = 27               # hang bat dau cua chan (duoi vat ao choang)
LEFT_LEG = (9, 16)          # cot [x0, x1) cua chan trai
RIGHT_LEG = (16, 22)


def clean_face(a):
    a = a.copy()
    # mat chibi 2x2, highlight goc tren-phai
    for x0 in (13, 19):
        a[13:15, x0:x0 + 2] = DARK
        a[13, x0 + 1] = WHITE
    a[13, 15] = SKIN_SH; a[14, 15] = SKIN; a[14, 21] = SKIN_SH; a[13, 21] = SKIN_SH
    # may cau: dau trong thap hon dau ngoai
    a[12, 13] = a[12, 14] = a[12, 15] = BROW
    a[12, 18] = a[12, 19] = a[12, 20] = BROW
    a[11, 13] = SKIN_SH; a[11, 20] = SKIN_SH
    # mieng nho
    a[16, 16] = a[16, 17] = SKIN_SH
    return a


def shift_region(a, rows, cols, dy, dx=0):
    """Dich 1 vung (chan) di dy, giu nguyen phan con lai. Phan bi ho ra phia duoi -> trong suot."""
    out = a.copy()
    r0, r1 = rows; c0, c1 = cols
    region = a[r0:r1, c0:c1].copy()
    out[r0:r1, c0:c1] = 0
    out[r0:r1, c0:c1][region[..., 3] == 0] = a[r0:r1, c0:c1][region[..., 3] == 0] * 0
    tgt = out[r0 + dy:r1 + dy, c0 + dx:c1 + dx]
    m = region[..., 3] > 0
    tgt[m] = region[m]
    return out


def walk_frames(idle):
    h = idle.shape[0]
    body_up = np.zeros_like(idle)                     # than nhun len 1px, chan giu nguyen
    body_up[:LEGS_TOP - 1] = idle[1:LEGS_TOP]
    body_up[LEGS_TOP - 1:] = idle[LEGS_TOP - 1:]
    body_up[LEGS_TOP - 1][idle[LEGS_TOP - 1][..., 3] == 0] = 0
    left_up = shift_region(idle, (LEGS_TOP, h), LEFT_LEG, -1)
    right_up = shift_region(idle, (LEGS_TOP, h), RIGHT_LEG, -1)
    return [left_up, body_up, right_up, body_up]


def save(a, name):
    img = Image.fromarray(a, "RGBA")
    img.save(os.path.join(OUT, name + ".png"))
    return img


if __name__ == "__main__":
    idle = np.asarray(Image.open(os.path.join(OUT, "player_idle.png")).convert("RGBA"))
    clean = clean_face(idle)
    frames = [save(clean, "player_idle_clean")]
    for i, f in enumerate(walk_frames(clean)):
        frames.append(save(f, f"player_walk_code_{i}"))
    # preview: idle cu | idle sach | 4 frame walk, + gif walk
    seq = [Image.fromarray(idle, "RGBA")] + frames
    sheet = Image.new("RGBA", (len(seq) * 36, 32), (0x2f, 0x41, 0x4d, 255))
    for i, im in enumerate(seq):
        sheet.alpha_composite(im, (i * 36, 0))
    sheet.resize((sheet.width * 8, sheet.height * 8), Image.NEAREST).save(os.path.join(OUT, "..", "player_contact.png"))
    gif = []
    for im in frames[1:]:
        bg = Image.new("RGBA", (32, 32), (0x2f, 0x41, 0x4d, 255)); bg.alpha_composite(im)
        gif.append(bg.resize((256, 256), Image.NEAREST).convert("P"))
    gif[0].save(os.path.join(OUT, "..", "player_walk.gif"), save_all=True, append_images=gif[1:], duration=140, loop=0)
    print("ok player_idle_clean + player_walk_code_0..3 + player_walk.gif")
