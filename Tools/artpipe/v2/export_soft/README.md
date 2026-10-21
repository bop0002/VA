# export_soft: asset thành phẩm (nguồn để chép vào Unity)

**Import chung:**
- Sprite (2D and UI), PPU **32**, Filter **Point**, Compression **None**.
- Pivot **Center**, trừ props dùng **Bottom**.

| Thư mục | Trạng thái | Nguồn | Trong Unity (`Assets/_Game/Art/`) |
|---|---|---|---|
| `player_v3/` | ✅ Chốt | Bản sao của `Characters/PlayerV3` (user sửa tay, **Unity là bản gốc**) | `Characters/PlayerV3/` |
| `Projectiles/aura.png`, `aura_ripple/` | ✅ Chốt | `build_aura_v2.py` (bản H) | `Projectiles/aura 2.png`, `Projectiles/AuraRiptile/` |
| `Projectiles/aura_alpha.png` | User sửa tay (khoét lõi rộng khoảng 9px) | Không ghi đè | `Projectiles/aura_alpha 1.png` |
| `Projectiles/aura_v2/H_lam_dao_tim/` | ✅ Chốt | Bản đầy đủ của aura chính | |
| `Projectiles/proj_*.png` | Chỉ `proj_enemy` còn dùng (Knife/Wand đã thay bằng FireBall/Rock tải về) | `build_fx.py` | `Projectiles/` |
| `Props_Graveyard/` | Đang dùng | `graveyard_props.py` | `Props/Graveyard/` |
| `Shadows/` | Đang dùng | `mock_scene.py` | `FX/Shadows/` |
| `A_zombie_to/` | Nguồn gốc player và zombie (bị `build_soft.py` tạo lại) | `build_soft.py` | Zombie đang dùng là `Enemies/enemy_zombie_idle2.png` (user sửa) |
| `_archive/` | Không dùng | Các phương án đã bỏ: `B_player_nho`, `Props_Graveyard_v1`, `graveyard_chars` (làm phẳng nhân vật), `aura_extract` / `aura_toon` / `aura_v2` (màu khác) | |

`Projectiles/aura_user_edit.png` và `aura_alpha_user_edit.png` là bản sao lưu của hai file user sửa tay (2026-10-13).

## Ghi chú dùng

- **Aura:**
  - 64×64, tức đường kính 2 unit, khớp `_baseRadius 1`.
  - Animation: 12 frame, `AuraRipple.anim` đang chạy 12 fps, có loop.
  - Nếu animate scale thì gắn sprite vào GameObject con. Bán kính sát thương tính theo `lossyScale` của object gốc.
- **Projectile:**
  - Tất cả quay sang PHẢI (`transform.right` là hướng bay).
  - Collider gợi ý: iceshard dùng Capsule ngang khoảng 0.5×0.3; wand và enemy dùng Circle r khoảng 0.18, đặt ở đầu đạn.
- **Player:**
  - Khung 48×48, `PlayerWalk` 8 fps.
  - Collider gợi ý: Capsule 0.6×1.0, offset y −0.15.
- **Bóng:** gắn làm con của nhân vật, cùng sorting layer, order −1.
