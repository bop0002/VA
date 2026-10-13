# experiments: script thử nghiệm đã bỏ

Các script này vẫn chạy được (`python Tools/artpipe/v2/experiments/<script>.py`). Chúng chỉ ghi vào `v2/out/_archive/` và `v2/export_soft/_archive/`, không đụng tới file chính.

| Script | Thử gì | Kết luận |
|---|---|---|
| `build_aura.py` | Tách aura từ ảnh Gemini nền tối, thu nhỏ xuống 64px | Bỏ: vòng đứt, mỏng, nhòe màu |
| `build_aura_anim.py` | Animate aura bằng scale/xoay, gợn sóng theo frame, hoặc kết hợp | Chọn gợn sóng theo frame, dựng lại bằng `build_aura_v2.py` |
| `build_aura_toon.py` | Aura toon 6/8 frame, có viền mực | Bỏ, user chọn nét mỏng của v2 |
| `blend_test.py` | Phân tích vì sao nhân vật lệch tông với map | Kết luận: thiếu bóng chân và ánh sáng (xem `mock_scene.py`) |
| `chars_flat.py` | Làm phẳng hoặc tô lại bóng nhân vật theo style map | Bỏ, giữ sprite gốc |
| `chars_v2.py` | 5 kiểu xử lý toon cho nhân vật v1 (T0–T4) | Bỏ (thời v1) |
| `variants_v2.py` | Biến thể màu cho nhân vật v1 | Bỏ (thời v1) |
