"""Ghep moi sprite trong out/ thanh 1 anh xem nhanh (phong to 6x tren nen Ground)."""
import glob, os, sys
from PIL import Image
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
fs = sorted(f for f in glob.glob(os.path.join(OUT, "*.png")) if "preview" not in f)
ims = [Image.open(f) for f in fs]
sheet = Image.new("RGBA", (sum(i.width + 4 for i in ims), max(i.height for i in ims)), (0x2f, 0x41, 0x4d, 255))
x = 0
for i in ims:
    sheet.alpha_composite(i, (x, sheet.height - i.height)); x += i.width + 4
dst = sys.argv[1] if len(sys.argv) > 1 else os.path.join(OUT, "..", "contact.png")
sheet.resize((sheet.width * 6, sheet.height * 6), Image.NEAREST).save(dst)
print([os.path.basename(f) for f in fs])
