# artpipe

Pipeline art cho VaClone. Cần Python 3.10, Pillow và numpy.
Hướng art đã chốt nằm ở `Docs/art/style-bible.md`. Đọc file đó trước.

## Cấu trúc

```
artpipe/
  artpipe.py        thư viện lõi: tách nền magenta, dò lưới pixel giả, các component (v2 dùng lại)
  palettes/         palette v1 (vaclone.hex)
  inbox/            ảnh Gemini tải về: V1/ (lô đầu), V2/ (lô chibi mềm và projectile)
  v2/               PIPELINE HIỆN TẠI. Xem v2/README.md
    *.py              script đang dùng
    prompts/          prompt Gemini (prompts_v2.txt là bản hiện hành)
    work/             ảnh anchor đính kèm khi gen Gemini (mainref_x8, player_anchor, zombie_anchor)
    export_soft/      asset thành phẩm (nguồn để chép vào Unity)
    out/              ảnh preview và sheet trung gian
    experiments/      script thử nghiệm đã bỏ (chỉ ghi vào _archive/)
    */_archive/       kết quả các phương án không chọn
  _archive_v1/      pipeline v1 (2026-10-10): handmade/, export/, out/, test/. Chỉ để tham khảo
```

## Lệnh hay dùng (chạy từ gốc repo)

| Lệnh | Việc |
|---|---|
| `python Tools/artpipe/v2/graveyard.py` | Vẽ lại tilesheet Graveyard (style flat) vào `v2/out/tilesheet_C_graveyard.png` |
| `python Tools/artpipe/v2/graveyard_props.py` | Vẽ lại 17 prop Graveyard vào `export_soft/Props_Graveyard/` |
| `python Tools/artpipe/v2/build_aura_v2.py blue` | Vẽ lại aura. Bản H làm file chính: `export_soft/Projectiles/aura.png` và `aura_ripple/` |
| `python Tools/artpipe/v2/player_v3.py` | Preview player (đọc frame hiện có). `--regen-walk` sẽ ghi đè walk |
| `python Tools/artpipe/v2/build_fx.py` | Tách projectile Gemini (`inbox/V2`) vào `export_soft/Projectiles/` |
| `python Tools/artpipe/v2/mock_scene.py` | Cảnh giả lập (bóng và đèn), xuất sprite bóng vào `export_soft/Shadows/` |
| `python Tools/artpipe/v2/build_soft.py` | Tách player và zombie gốc từ inbox vào `export_soft/A_zombie_to/` |

**Ghi vào Unity (chỉ chạy khi user đồng ý, và nên đóng Unity trước):**
- `make_unity_graveyard.py`: sheet `.meta`, 32 tile, RuleTile, chunk.
- `unity_organize.py`: sắp xếp thư mục `Assets/_Game/Art`. Script này chỉ chạy một lần, đã chạy ngày 2026-10-13.

## Quy tắc an toàn

- File user sửa tay là bản gốc. Script phải đọc lại file đó, **không được ghi đè**.
  - Hiện có: `Assets/_Game/Art/Characters/PlayerV3/*` và `export_soft/Projectiles/aura_alpha.png`.
- Script chỉ được xóa thư mục do chính nó tạo ra. `build_soft.py` đã được sửa ngày 2026-10-13: trước đó nó xóa mọi thư mục con của `export_soft`.
- Kết quả thử nghiệm luôn ghi vào `out/_archive/` và `export_soft/_archive/`, không bao giờ ghi lên file chính.
