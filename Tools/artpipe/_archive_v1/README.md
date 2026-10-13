> **LƯU TRỮ (pipeline v1, 2026-10-10).** Pipeline hiện tại là `Tools/artpipe/v2/`. Các script ở đây chỉ để tham khảo; đường dẫn đã thay đổi nên không đảm bảo chạy được.

# artpipe

Biến ảnh Gemini thành asset pixel art sạch, đúng `Docs/art/style-bible.md`. Cần Python 3.10, Pillow và numpy.

| Thư mục | Nội dung |
|---|---|
| `inbox/` | Ảnh Gemini tải về (nền magenta `#FF00FF`) |
| `out/` | Sprite và tile đã xử lý, kèm `.json` và `_preview.png` |
| `export/` | Bộ asset đã duyệt, gọn theo thư mục, để kéo vào Unity. Tạo lại bằng `python Tools/artpipe/export.py` |
| `palettes/vaclone.hex` | Palette 50 màu, toàn bộ asset bị ép về đây |
| `handmade/` | Asset Claude vẽ trực tiếp bằng code (ví dụ `bat.py`) |
| `test/` | Ảnh test của toolchain |

## Lệnh

```bash
# Nhan vat / quai / prop tren nen magenta. --height = chieu cao toi da (px).
# Anh nhieu con: tach tung con, giu ti le giua cac con.
python Tools/artpipe/artpipe.py extract Tools/artpipe/inbox/enemy_zombie_01.png --name enemy_zombie --height 30

# Texture mat dat vuong -> lien mep -> cat o 32px (--tiles 2 => 64x64 = 4 o)
python Tools/artpipe/artpipe.py tile Tools/artpipe/inbox/tile_grass_01.png --name tile_grass

# Bo 47 o autotile (RuleTile) tu 2 texture da qua lenh tile
cd Tools/artpipe && python autotile.py --base out/tile_grass_full.png --over out/tile_dirt_full.png --name auto_dirt

# Xem nhanh moi sprite trong out/ -> contact.png
python Tools/artpipe/contact.py
```

## Chiều cao gợi ý cho `--height`

| Loại | Chiều cao |
|---|---|
| Player, quái người | 30 |
| Quái nhỏ (dơi, slime) | 20–24 |
| Quái to, elite | 44 (khung 48) |
| Boss | 60 (khung 64) |
| Prop nhỏ | 28 |
| Cây | 60 |

## Đọc log

`grid 16.0px native_h 33` nghĩa là Gemini vẽ mỗi pixel thành một khối 16px, và sprite gốc cao 33 pixel thật. Nếu log in `(!) thu nho xN` thì sprite gốc cao hơn `--height`, nên đã bị thu nhỏ và có thể mất chi tiết mảnh. Khi đó nên gen lại theo hướng ít nhân vật hơn trong mỗi ảnh để khối pixel to hơn.

## Asset vẽ bằng code (`handmade/`)

| Script | Sinh ra |
|---|---|
| `bat.py` | `enemy_bat_0/1`: dơi 2 frame vỗ cánh, vẽ lại theo ref (bản Gemini quá hiền) |
| `player.py` | `player_idle_clean` (dọn mặt) và `player_walk_code_0..3` (walk dựng từ idle), kèm `player_walk.gif` |
| `ground.py` | `tile_grass_0..3`, `tile_dirt_full`, `auto_dirt` (47 ô), `decor_patch_*` (mảng đất tách từ Gemini), `ground_preview.png` |
| `props.py` | `prop_fence` (rào ngang 32px, nối được thành dãy), `prop_grave` (huyệt mộ chính diện), `decor_bones`, `decor_leaves`, `decor_puddle` |

## Bài học từ Gemini (2026-10-10)

- **Walk cycle do Gemini vẽ không dùng được:** mặt mỗi frame một kiểu, chân gần như đứng yên. Chỉ nên lấy bản idle đẹp nhất từ Gemini, còn walk thì dựng bằng code (`player.py`).
- **Texture mặt đất:** Gemini tự lặp một ô 512×512 liền mép thành ảnh 1024. Đo chu kỳ lặp rồi cắt đúng một ô, vừa không dính logo, vừa không cần làm liền mép lại. Ô này lặp mỗi 64px rất lộ, nên chỉ lấy màu và các mảng đất (decal). Còn cỏ nền và đường đất thì sinh bằng code.
- **Dò lưới pixel:** lưới thật và lưới gấp đôi hoặc một nửa đều được điểm cao. `artpipe` chọn lưới cho ra chiều cao gốc ≥ `--height` và gần nhất với nó. Nếu không có lưới nào đạt, nó thu nhỏ thẳng từ ảnh nguồn.
- **Props góc chéo:** Gemini hay vẽ hàng rào và mộ theo góc isometric, lệch với map lưới vuông. Prompt 7.7 đã chặn lỗi này, còn hàng rào và huyệt mộ thì vẽ bằng code.
- **Decor 16px gồm nhiều mảnh vụn** (như xương rải rác) sẽ thành nhiễu. Nên chọn món liền khối, hoặc vẽ bằng code.
