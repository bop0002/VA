# Export — kéo cả thư mục vào `Assets/_Game/Art/Generated/`

Import chung: Sprite (2D and UI), **PPU 32**, **Filter Point**, **Compression None**, tắt Mip Maps.

| Thư mục | Pivot | Số file |
|---|---|---|
| `Characters/` | Center | 5 |
| `Enemies/` | Center | 8 |
| `Props/` | Bottom | 4 |
| `Decor/` | Center | 15 |
| `Tiles/` | Center | 4 |

- `Characters/player_walk_0..3`: Animation `Player_Walk`, Samples 8. `player_idle`: Animation `Player_Idle`.
- `Enemies/enemy_bat_0/1`: Animation `Bat_Fly`, Samples 6.
- `Tiles/tilesheet_*.png`: Sprite Mode Multiple → Slice Grid By Cell Size 32×32 → kéo vào Tile Palette. File `_labeled` chỉ để xem số ô, không import.
  Sheet 8×4 ô (256×128), đánh số trái→phải, trên→dưới (0..31); thứ tự này trùng với hậu tố `_N` Unity gán khi Slice.
  Đường: 0 NW, 1 N, 2 NE, 8 W, 9 C, 10 E, 16 SW, 17 S, 18 SE (hướng = phía có cỏ); 3/4/11/12 = góc trong cỏ ở NW/NE/SW/SE; 19, 20 = đường biến thể.
  Cỏ: 5 = cỏ trơn (dùng nhiều nhất); 13, 21, 6, 7, 14, 15, 22, 23, 24..31 = biến thể (bụi, hoa, mảng tối/sáng, sỏi, đá, nấm, mảng đất).
  Cỏ nền: Random Brush trộn cỏ 5 khoảng 50%, 13 và 21 mỗi ô ~10%, các ô còn lại chia đều. Đường rộng tối thiểu 2 ô.
- `Decor/decor_patch_*`: Sorting Layer Background (nằm dưới props).
