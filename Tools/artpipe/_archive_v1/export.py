"""Gom asset da duyet tu out/ vao export/ theo thu muc, de keo thang vao Assets/_Game/Art/Generated/.

Dung: python Tools/artpipe/export.py
export/ bi xoa va tao lai moi lan chay -> luon khop voi danh sach ben duoi.
"""
import json, os, shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "out")
EXPORT = os.path.join(ROOT, "export")

# thu muc -> [(file trong out/, ten khi export)]
LAYOUT = {
    "Characters": [("player_idle_clean.png", "player_idle.png")]
                  + [(f"player_walk_code_{i}.png", f"player_walk_{i}.png") for i in range(4)],
    "Enemies": [(f"{n}.png", f"{n}.png") for n in (
        "enemy_zombie_a", "enemy_zombie_b", "enemy_skeleton", "enemy_skeleton_helmet",
        "enemy_ghost", "enemy_hound", "enemy_bat_0", "enemy_bat_1")],
    "Props": [(f"{n}.png", f"{n}.png") for n in ("prop_tree_dead", "prop_tombstone", "prop_fence", "prop_grave")],
    "Decor": [(f"decor_{n}.png", f"decor_{n}.png") for n in (
        "grass_dry", "grass_dark", "bush", "rocks", "stone", "skull", "bones", "leaves",
        "mushroom", "flowers", "puddle", "crack", "patch_0", "patch_1", "patch_2")],
    # v2: tileset terrain 6x3 (xem v2/README.md), 2 theme user chon 2026-10-10
    "Tiles": [(f"../v2/out/tilesheet_{t}{x}.png", f"tilesheet_{t}{x}.png") for t in ("A_meadow", "B_moonlit") for x in ("", "_labeled")],
}

# goi y import cho tung thu muc (ghi vao README cua export)
PIVOT = {"Characters": "Center", "Enemies": "Center", "Props": "Bottom", "Decor": "Center", "Tiles": "Center"}

if __name__ == "__main__":
    if os.path.isdir(EXPORT):
        shutil.rmtree(EXPORT)
    missing, count = [], 0
    for folder, files in LAYOUT.items():
        os.makedirs(os.path.join(EXPORT, folder))
        for src, dst in files:
            p = os.path.join(OUT, src)
            if not os.path.exists(p):
                missing.append(src); continue
            shutil.copy2(p, os.path.join(EXPORT, folder, dst)); count += 1
    lines = ["# Export — kéo cả thư mục vào `Assets/_Game/Art/Generated/`", "",
             "Import chung: Sprite (2D and UI), **PPU 32**, **Filter Point**, **Compression None**, tắt Mip Maps.", "",
             "| Thư mục | Pivot | Số file |", "|---|---|---|"]
    for folder, files in LAYOUT.items():
        lines.append(f"| `{folder}/` | {PIVOT[folder]} | {len(os.listdir(os.path.join(EXPORT, folder)))} |")
    lines += ["", "- `Characters/player_walk_0..3`: Animation `Player_Walk`, Samples 8. `player_idle`: Animation `Player_Idle`.",
              "- `Enemies/enemy_bat_0/1`: Animation `Bat_Fly`, Samples 6.",
              "- `Tiles/tilesheet_*.png`: Sprite Mode Multiple → Slice Grid By Cell Size 32×32 → kéo vào Tile Palette. File `_labeled` chỉ để xem số ô, không import.",
              "  Sheet 8×4 ô (256×128), đánh số trái→phải, trên→dưới (0..31); thứ tự này trùng với hậu tố `_N` Unity gán khi Slice.",
              "  Đường: 0 NW, 1 N, 2 NE, 8 W, 9 C, 10 E, 16 SW, 17 S, 18 SE (hướng = phía có cỏ); 3/4/11/12 = góc trong cỏ ở NW/NE/SW/SE; 19, 20 = đường biến thể.",
              "  Cỏ: 5 = cỏ trơn (dùng nhiều nhất); 13, 21, 6, 7, 14, 15, 22, 23, 24..31 = biến thể (bụi, hoa, mảng tối/sáng, sỏi, đá, nấm, mảng đất).",
              "  Cỏ nền: Random Brush trộn cỏ 5 khoảng 50%, 13 và 21 mỗi ô ~10%, các ô còn lại chia đều. Đường rộng tối thiểu 2 ô.",
              "- `Decor/decor_patch_*`: Sorting Layer Background (nằm dưới props).", ""]
    open(os.path.join(EXPORT, "README.md"), "w", encoding="utf-8").write("\n".join(lines))
    print(f"ok {count} file -> {EXPORT}")
    if missing:
        print("(!) thieu:", missing)
