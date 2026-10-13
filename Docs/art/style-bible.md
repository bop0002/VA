# VaClone Style Bible (v2)

> Chốt ngày **2026-10-13**. Thay cho bản v1 (2026-10-10), bản cũ lưu ở `_archive/style-bible-v1-2026-10-10.md`.
> Asset mới phải theo tài liệu này. Muốn đổi hướng thì sửa tài liệu trước, rồi mới sửa asset.

## 0. Trạng thái asset

| Asset | Trạng thái | File dùng trong Unity | Nguồn hoặc cách làm lại |
|---|---|---|---|
| **Player** | ✅ Chốt | `Art/Characters/PlayerV3/` (idle + walk 0..3), `Art/Characters/Animation/` | User sửa tay. **File trong Unity là bản gốc** |
| **Aura (Garlick)** | ✅ Chốt | `Art/Projectiles/aura 2.png` (tĩnh), `Art/Projectiles/AuraRiptile/` (12 frame + `AuraRipple.anim`) | `build_aura_v2.py` (vẽ bằng code), bản `H_lam_dao_tim` |
| **Tilemap Graveyard** | ✅ Chốt | `Art/Tiles/Graveyard/` (sheet, 32 tile, 2 RuleTile, Palette), `Prefabs/Chunks/Graveyard Chunk 1..3` | `graveyard.py` (style **flat**) + `make_unity_graveyard.py` |
| Props Graveyard | Đang dùng (đi kèm tilemap) | `Art/Props/Graveyard/` (17 PNG), `Prefabs/Props/Graveyard/` | `graveyard_props.py` (bản 2: to, mềm, 2 tông) |
| Bóng chân | Đang dùng | `Art/FX/Shadows/` | `mock_scene.py` |
| Zombie, Shooter (ghost) | Đang dùng, **chưa chốt lại** | `Art/Enemies/enemy_zombie_idle2.png`, `enemy_ghost.png` | Zombie gốc từ `build_soft.py` (A_zombie_to), user sửa tay |
| Knife (iceshard), Magic Wand | ⏳ **Chưa confirm, chưa test** | `Art/Projectiles/proj_iceshard(_b).png`, `proj_wand.png` | `build_fx.py` từ ảnh Gemini |
| Đạn Shooter | Đang dùng tạm | `Art/Projectiles/proj_enemy.png` | `build_fx.py` |

Đường dẫn Unity tính từ `Assets/_Game/`. Script nằm ở `Tools/artpipe/v2/`.

## 1. Tham chiếu

| Ref | Lấy gì |
|---|---|
| `Tools/ArtRef/refmainchac.png` | **Phong cách nhân vật:** chibi mềm, khối tròn, ít chi tiết |
| `Tools/ArtRef/conceptref.jpg` | **Phong cách map:** nghĩa địa đêm, mảng màu phẳng, rêu tối, đất tím, mép tile không viền |
| `Tools/ArtRef/Screenshot ...png` (Skul) | Chỉ lấy độ "nhộn" và sự đa dạng của quái. Không sao chép |

## 2. Quy tắc chung

- **PPU 32** cho mọi sprite, 1 tile = 32×32px = 1 unit.
  - Import: Filter **Point**, Compression **None**.
  - Mọi sprite phải dùng cùng PPU thì pixel mới đều nhau.
- **Pivot:**
  - Nhân vật, quái, projectile, aura: **Center**.
  - Props: **Bottom** (alignment 7).
  - Bóng: **Center**.
- **Khung nhân vật và quái là 48×48.**
  - Player cao khoảng 40px (bbox 33×40).
  - Zombie được phóng lên khoảng 37px, đứng cùng đường chân với player.
- **Góc nhìn:**
  - Nhân vật nhìn 3/4 chính diện, quay phải. Hướng trái dùng `flipX`.
  - Map nhìn top-down, lưới vuông. Props vẽ 3/4 chính diện, không vẽ isometric.
- **Hòa nhập nhân vật vào map:**
  - Không đổi màu sprite nhân vật. Bản gốc được user chọn sau khi so với bản làm phẳng và tô lại bóng.
  - Thay vào đó dùng **bóng chân** cộng **ánh sáng URP Light 2D** (mục 7).

## 3. Player (đã chốt)

- Phong cách chibi mềm theo `refmainchac.png`:
  - Mũ trùm tím (`#403459 / #4e4168 / #5e527a`), mặt da `#f7caa4`, tóc mái thẳng `#8a535a`, áo choàng đỏ sẫm `#833358`.
  - Viền gần đen.
- **Mặt:** mắt là chấm tròn 2×2, không lông mi, có miệng nhỏ. Hai tay khép sát thân.
- **Animation:**
  - Walk có 4 frame: nhấc chân trái, nhún, nhấc chân phải, nhún.
  - Chóp mũ đung đưa trễ nhịp 1px.
  - `PlayerWalk.anim` chạy 8 fps, có loop. `PlayerIdle.anim` có 1 frame.
- **File gốc là `Assets/_Game/Art/Characters/PlayerV3/`, vì user đã sửa tay cả 5 frame.**
  - `Tools/artpipe/v2/export_soft/player_v3/` là bản sao.
  - `player_v3.py` mặc định chỉ vẽ preview. Thêm `--regen-walk` mới sinh lại walk, và sẽ **ghi đè** walk đã sửa tay.

## 4. Aura Garlick (đã chốt)

- **Vẽ bằng code**, không lấy từ ảnh Gemini. Ảnh Gemini thu nhỏ xuống 64px thì vòng bị đứt, mỏng và nhòe màu.
- **Kích thước 64×64:** đường kính 2 unit ở PPU 32, khớp `_baseRadius = 1` của `AuraProjectile`.
- **Thiết kế:**
  - Vòng đồng tâm, xen kẽ hai kiểu:
    - **vòng đặc** dày 2px màu xanh dương: mép ngoài sáng, mép trong đậm;
    - **vòng đứt** mảnh 1px màu tím, có chấm lấp lánh.
  - Phía trong mỗi vòng có một vệt mờ.
  - Viền ngoài mảnh đứng yên, đánh dấu đúng bán kính gây sát thương.
- **Palette H_lam_dao_tim:**

| Vai trò | Màu |
|---|---|
| deep | `#123070` |
| mid | `#3282e8` |
| hi | `#64c8ff` |
| top | `#dcf5ff` |
| vòng đứt | `#af73ff` |
| lấp lánh | `#f5ebff` |

- **Lõi giữa rỗng** (bán kính < 5px), để không phủ màu lên nhân vật. Đây là yêu cầu của user.
- **Animation:** 12 frame, vòng lan ra từ lõi tới mép, lặp liền mạch.
  - `AuraRipple.anim` đang chạy 12 fps.
  - Sprite tĩnh là frame 4.
- Dựng lại: `python Tools/artpipe/v2/build_aura_v2.py blue`. Script tự đặt bản H làm file chính và cho các bản màu khác vào `_archive`.
- Đã thử rồi bỏ (trong `_archive`): tách từ ảnh Gemini, bản toon 6 frame có viền mực, các phối màu A–I khác.

## 5. Tilemap Graveyard (đã chốt)

- **Style flat** theo `conceptref.jpg`:
  - Mảng màu phẳng, mép đất không có viền.
  - Lá cỏ tối (G1) rìa sang đất, đất sát mép tối hơn một bậc.
  - Mảng chi tiết là khối liền, không rải hạt nhiễu.
  - Bài học: concept là mảng phẳng; tile càng chi tiết càng lệch khỏi chất toon.
- **Palette** (`graveyard.py`):

| Ramp | Màu (tối → sáng) |
|---|---|
| Cỏ G | `#243036 #33444a #3f5250 #4b6058 #5e7662 #768f6c` |
| Đất tím P | `#251c30 #33263f #3f2d49 #4a3450 #58405d #674f69` |
| Đá S | `#2a2834 #4a4a56 #6b6c74 #8c8d92` |
| Xương | `#5d5a58 #a9a294 #d8d0bc` |
| Nấm phát sáng | `#3d6e73 #6fb7b0 #b8f0dc` |
| Lá khô | `#4a3530 #6b4a35 #8a6a45` |
| Hoa | `#7a6a9a #b8a8d8 #e8e0f0` |

- **Sheet 8×4 ô** (256×128), cùng thứ tự với Meadow. Ô đánh số trái → phải, trên → dưới, từ 0 đến 31.
  - Đường: 0 NW, 1 N, 2 NE, 8 W, 9 C, 10 E, 16 SW, 17 S, 18 SE. Hướng ghi là phía có cỏ.
  - Góc trong: 3, 4, 11, 12. Biến thể đường: 19, 20.
  - Cỏ trơn: 5. Biến thể cỏ: 13, 21, 6, 7, 14, 15, 22, 23, 24..31.
  - Đường rộng tối thiểu 2 ô.
- **Trong Unity:**
  - RuleTile `Graveyard Path` và `Graveyard Grass`.
  - `Graveyard Palette.prefab`.
  - Chunk `Graveyard Chunk 1/2/3` (seed 51, 67, 83) đang được `MapController.chunkPrefabs` dùng.
- **Props bản 2:** 17 cái, khối to (x1.35), 2 tông, viền `#15111f`.
  - Gồm: mộ tròn, mộ cao, mộ vỡ, thập giá đá, thập giá gỗ, rào (32px nối được), cột rào, đuốc 3 frame, đèn lồng, cây chết, cây mặt quỷ, bụi khô, đá to, đá nhỏ, đống sọ.
  - Prefab: tag `Prop`, sorting layer `Props`, `SpriteSortPoint` Pivot, `BoxCollider2D` ở chân. Bụi và đống sọ không có collider.
- Meadow (bản cũ) vẫn còn ở `Art/Tiles/Meadow`, chunk của nó ở `Prefabs/_Archive`.

## 6. Projectile (chưa chốt, trừ aura)

- Tất cả quay sang **PHẢI**. Unity dùng `transform.right` làm hướng bay.

| Projectile | Kích thước | Ghi chú |
|---|---|---|
| `proj_iceshard` | 22×13 | Thay Knife |
| `proj_iceshard_b` | 24×13 | Bản thay thế |
| `proj_wand` | 21×14 | Đạn Magic Wand |
| `proj_enemy` | 18×12 | Đạn Shooter |

- Lấy từ ảnh Gemini bằng `build_fx.py`.
- **Knife và Magic Wand: user chưa test và chưa confirm.** Khi chốt thì cập nhật mục 0.

## 7. Ánh sáng và bóng (khuyến nghị)

- **Bóng chân:** sprite elip 2 bậc, màu P0, alpha 95/170.
  - Ba cỡ: `shadow_small` 22×7, `shadow_player` 26×8, `shadow_big` 40×10.
  - Gắn làm con của Player, Zombie, Shooter, cùng sorting layer, order −1.
- **URP Light 2D:**

| Đèn | Loại | Màu | Cường độ | Bán kính |
|---|---|---|---|---|
| Global | Global Light 2D | `#D6E6FF` | 0.6 | |
| Đuốc | Spot Light 2D 360°, đặt ở y ≈ 1.1 | `#FF9A48` | 1 | 3 |
| Đèn lồng | Spot Light 2D 360° | `#FFC070` | | 2.2 |
| Quanh player | Spot Light 2D 360° | `#FFF0DC` | 0.5 | 2.5 |

  - Lửa và mắt dùng `Sprite-Unlit-Default` để không bị tối đi.
- **Đuốc:** `torch_0..2` chạy 8 fps, có loop. Có thể thêm hiệu ứng cường độ đèn chập chờn.
- Ảnh minh họa: `Tools/artpipe/v2/out/mock_scene_compare.png` (gốc / có bóng / có bóng + đèn).

## 8. Quy trình

1. Nhân vật và quái mới: gen bằng Gemini theo `Tools/artpipe/v2/prompts/prompts_v2.txt`. Claude tách ảnh bằng `extract_soft.py` / `build_soft.py`. Walk dựng bằng code, không gen.
2. Tile, props, FX hình học (aura, vòng, bóng): Claude vẽ bằng code.
3. Claude đưa ra nhiều bản để user chọn, rồi chỉnh dần theo bản được chọn.
4. Chỉ ghi vào `Assets/` khi user yêu cầu. Còn lại user tự đưa vào Unity.
5. Khi user sửa tay một file, **file đó trở thành bản gốc**. Script phải đọc lại file đó, không được ghi đè.
