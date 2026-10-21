# artpipe v2: pipeline hiện tại

Hướng art đã chốt nằm ở `Docs/art/style-bible.md`. Lệnh chạy từ gốc repo: `python Tools/artpipe/v2/<script>.py`.

## Script đang dùng

| Script | Asset | Ra file |
|---|---|---|
| `player_v3.py` | Player (✅ chốt) | Preview `out/player_v3_*`. Frame gốc là `Assets/_Game/Art/Characters/PlayerV3` (user sửa tay, có bản sao ở `export_soft/player_v3/`). `--regen-walk` / `--regen-idle` sẽ ghi đè |
| `build_aura_v2.py` | Aura Garlick (✅ chốt) | `export_soft/Projectiles/aura.png` + `aura_ripple/0..11` (bản H). Chạy với tham số `blue` để dựng lại bộ màu xanh, các bản màu khác vào `_archive` |
| `graveyard.py` | Tilemap Graveyard (✅ chốt, style flat) | `out/tilesheet_C_graveyard{,_labeled,_demo}.png`. Style `detail` và `flat_soft` vào `out/_archive` |
| `graveyard_props.py` | 17 prop Graveyard | `export_soft/Props_Graveyard/`, `out/graveyard_props_*.png`, `graveyard_torch.gif` |
| `mock_scene.py` | Bóng chân + cảnh giả lập đèn | `export_soft/Shadows/`, `out/mock_scene_*.png` |
| `build_fx.py` | Projectile từ Gemini (giờ chỉ còn dùng `proj_enemy`; FireBall/Rock là asset tải về) | `export_soft/Projectiles/proj_*.png` |
| `build_soft.py` | Player và zombie gốc tách từ Gemini | `export_soft/A_zombie_to/` (chỉ xóa và tạo lại đúng thư mục này) |
| `extract_soft.py` | Thư viện tách sprite chibi mềm (dùng `../artpipe.py`) | `out/soft/` |
| `tiles_v2.py`, `terrain_v2.py`, `tilesheet_full.py` | Thư viện vẽ tile (graveyard dùng lại). `tilesheet_full` dựng sheet Meadow | `out/tilesheet_A_meadow*.png` |
| `make_unity_chunks.py` | Ghi chunk và RuleTile vào Unity (Meadow, và làm thư viện cho Graveyard) | `Assets/...` (cần user đồng ý) |
| `make_unity_graveyard.py` | Ghi sheet `.meta`, 32 tile, RuleTile, Graveyard Chunk 1..3 vào Unity | `Assets/...` (cần user đồng ý) |
| `unity_organize.py` | Sắp xếp `Assets/_Game/Art` và Prefabs (chạy một lần, ngày 2026-10-13) | `Assets/...` |

## Thư mục

| Thư mục | Nội dung |
|---|---|
| `prompts/prompts_v2.txt` | Prompt Gemini hiện hành. `prompts_v2_backup.txt` là bản sao chỉ đọc |
| `work/` | Ảnh anchor đính kèm khi gen Gemini: `mainref_x8.png`, `player_anchor.png`, `zombie_anchor.png` |
| `export_soft/` | Asset thành phẩm để chép vào Unity. Xem `export_soft/README.md` |
| `out/` | Sheet, preview và GIF của bản đang dùng. `out/soft/` là ảnh debug của `extract_soft` |
| `experiments/` | Script thử nghiệm đã bỏ. Xem `experiments/README.md` |
| `*/_archive/` | Kết quả các phương án không chọn (chỉ để tham khảo) |

## Lịch sử quyết định

| Ngày | Quyết định |
|---|---|
| 2026-10-10 | Tile v2 toon thay autotile 47 ô của v1. Chọn A_meadow và B_moonlit. Nhân vật v1 giữ nguyên |
| 2026-10-11 | Đổi sang nhân vật chibi mềm theo `refmainchac.png`. Chọn cỡ A (player 36×40, zombie phóng lên khoảng 37px) |
| 2026-10-13 | Map C_graveyard theo `conceptref.jpg`, style flat. Props bản 2 |
| 2026-10-13 | Giữ sprite nhân vật gốc, không làm phẳng. Hòa nhập bằng bóng chân + Light 2D |
| 2026-10-13 | Player v3: mắt chấm, tay khép, mũ đung đưa. User sửa tay bản cuối |
| 2026-10-13 | Aura vẽ bằng code (v2, nét mỏng, 12 frame), màu H_lam_dao_tim, lõi rỗng |
