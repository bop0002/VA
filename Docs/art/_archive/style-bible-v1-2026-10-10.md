# VaClone Style Bible

> Chốt ngày 2026-10-10 dựa trên `Tools/ArtRef/`. Mọi asset mới phải theo tài liệu này. Muốn đổi thì sửa tài liệu trước, rồi mới sửa asset.

## 1. Tham chiếu

| Ref | Lấy gì |
|---|---|
| `Tools/ArtRef/3d30516b-...jpg` (graveyard, do Gemini gen) | **Style anchor chính.** Đính kèm vào MỌI prompt Gemini. Lấy màu, viền, tỉ lệ, góc nhìn, độ tương phản giữa nhân vật và nền |
| `Tools/ArtRef/Screenshot ...png` (Skul: The Hero Slayer) | Chỉ lấy độ "nhộn" chibi và sự đa dạng trong thiết kế quái. Không sao chép nhân vật (game thương mại) |

## 2. Kích thước & góc nhìn

- **Pixel art thật, PPU 32.** 1 tile = 32×32px = 1 unit.
- **Khung nhân vật và quái thường là 32×32.**
  - Nhân vật cao khoảng 26–30px, chân chạm hàng pixel thứ 2 từ dưới lên.
  - Pivot đặt ở giữa đáy (bottom-center).
- **Quái to hoặc elite dùng 48×48. Boss dùng 64×64.**
- **Icon và vật phẩm** (ngọc, rương, vũ khí trên UI) dùng 16×16.
- **Góc nhìn:**
  - Nhân vật và quái nhìn chính diện, hơi nghiêng 3/4 về phải. Hướng trái có được bằng cách lật `flipX`.
  - Map là top-down lưới vuông. Props (mộ, cây, đèn) vẽ kiểu 3/4 để có chiều sâu.

## 3. Tỉ lệ chibi

- Đầu chiếm khoảng **50%** chiều cao (đầu khoảng 14–16px, thân và chân khoảng 14px).
- Đầu tròn, mắt to đơn giản (2×2 hoặc 2×3 px), tay chân ngắn, bàn tay là một khối.
- Mỗi quái phải có **dáng (silhouette) dễ nhận ra** chỉ bằng màu đặc. Đây là điều bắt buộc vì màn hình sẽ có rất nhiều quái.

## 4. Nét & đổ bóng

- **Viền 1px bao ngoài** dùng `#1a1424` (tối ngả tím), không dùng đen tuyền.
  - Đường chi tiết bên trong dùng tông tối nhất của chính vật liệu đó.
- **Đổ bóng 3 tông cho mỗi vật liệu:** tối, gốc, sáng. Thêm điểm highlight nếu cần.
  - Ánh sáng chiếu từ trên, hơi lệch trái.
- **Không dither, không anti-alias, không gradient.**
- **Không vẽ glow hay quầng sáng vào sprite.** Glow làm trong Unity (Light2D hoặc sprite additive). Sprite chỉ vẽ lõi sáng.
- **Bóng đổ dưới chân không vẽ vào sprite.** Dùng chung một sprite bóng oval trong Unity.

## 5. Palette — `Tools/artpipe/palettes/vaclone.hex` (50 màu)

| Ramp | Màu (tối → sáng) | Dùng cho |
|---|---|---|
| Outline | `0d0912 1a1424 2a2138` | Viền, khe tối |
| Night bg | `2f2742 3a324e 4c4468 605b7c` | Nền đêm, đá, tường |
| Ground | `1f2d33 2f414d 3e5a5a 5a7a6a` | Đất, cỏ đêm |
| Skin | `6b3a2e b0684a e0a07a f6d2b0` | Da người, tóc nâu |
| Bone | `887f70 b2a791 cfc6af ece4c2 fffbea` | Xương, kim loại sáng (lấy mẫu từ ref) |
| Spirit | `8f9cbc a8bbde dae6f5` | Ghost, linh hồn, sương (lấy mẫu từ ghost Gemini) |
| Zombie | `49533b 707f5f 8b9f75 afbc8c` | Da zombie (lấy mẫu từ ref) |
| Poison | `2e4a2a 4f7a3a 86b04a c4dc78` | Độc, ngọc xanh lá, cây tươi |
| Red | `4a1428 8e1f30 dc3943 ff8a7a` | Máu, HP, ngọc đỏ |
| Fire | `7a2e14 d0601c f6a23a ffe08a` | Lửa, vàng kim, coin |
| Ice | `1c2e6e 2f6fd0 4fb4f0 a8f0ff` | Băng, sét, EXP |
| Magic | `3a1a5e 6a2fa0 a860e0 e0b0ff` | Phép, dơi, áo choàng |
| Wood | `3a2420 5e3a2a 8a5a3a` | Gỗ, rương, cán vũ khí |

**Nguyên tắc dễ đọc:**
- Nền chỉ dùng Night bg, Ground và Outline, đều tối và ít bão hòa.
- Nhân vật, quái, FX và vật phẩm phải có ít nhất một mảng màu sáng hoặc bão hòa để nổi trên nền.

## 6. Animation (hybrid)

| Entity | Frame vẽ | Phần làm bằng code |
|---|---|---|
| Player | idle 2–4 frame, walk 4–6 frame | flipX, hit flash |
| Quái thường | 1–2 frame (bước chân) | squash/bob DOTween, flipX, hit flash |
| Boss | idle 2–4 frame, attack 3–4 frame | tween |
| Projectile/FX | 1–4 frame | rotate, scale, glow |

## 7. Prompt template cho Gemini

Quy tắc chung:
- Luôn **đính kèm ảnh style anchor** (ref graveyard).
- Khi đã có sprite được duyệt, đính kèm thêm sprite đó.
- Đặt toàn bộ ảnh tải về vào `Tools/artpipe/inbox/`, đặt tên theo dạng `<loai>_<ten>_<so>.png`, ví dụ `enemy_zombie_01.png`.

**Bài học từ lô đầu tiên (2026-10-10):**
- Ảnh có **một nhân vật** thì Gemini vẽ khối pixel khoảng 16px, tương đương sprite cao khoảng 32px. Đây là kích thước lý tưởng.
- Ảnh **lô 5 con** thì khối pixel chỉ khoảng 8px, sprite cao khoảng 40px, nên khi thu nhỏ sẽ mất chi tiết mảnh.
- **Do đó:**
  - Quái quan trọng nên gen từng con một.
  - Gen lô chỉ để chốt concept, mỗi ảnh tối đa 3 con.
  - Luôn kèm câu *"the whole image is a 64x36 pixel grid upscaled 16x"*. Câu này ép Gemini vẽ khối pixel to.

Mọi prompt bên dưới đều dùng chung **khối STYLE** này. Copy nguyên văn và dán vào chỗ `[STYLE]`:

```
STYLE RULES (match the attached reference image exactly):
- dark-fantasy night graveyard survivor game, crisp pixel art
- low resolution: the whole image is a 64x36 pixel grid upscaled 16x, every pixel is a big clean square block
- 1-pixel dark purple outline (#1a1424) around every object, 3-tone flat shading, light from top-left
- no dithering, no anti-aliasing, no gradients, NO glow, NO drop shadow, NO text, NO watermark, NO border
- background: perfectly flat solid magenta #FF00FF everywhere (no shading, no floor)
```

### 7.1 Một quái (concept → sprite) — `enemy_<ten>_NN`

```
[STYLE]
Draw ONE chibi enemy: [MÔ TẢ, ví dụ: "rotting zombie with torn brown shirt, arms reaching forward"].
- chibi proportions: big round head about half of total height, short body and limbs
- front-facing, slightly turned to the right (3/4 view), full body
- menacing but cute: angry eyebrows / glowing eyes, readable silhouette
- the character is about 30 pixels tall, centered
```

> Muốn quái "dữ" như ref thì thêm: *"angry slanted eyebrows, glowing red eyes, sharp teeth, aggressive pose"*. Gemini mặc định thường vẽ quá hiền.

### 7.2 Lô concept (chốt ý tưởng, tối đa 3 con) — `concept_<chude>_NN`

```
[STYLE]
Draw a lineup of 3 different chibi enemies, evenly spaced in one row, not overlapping, same scale:
1. [..]  2. [..]  3. [..]
- big round heads (~50% height), 3/4 front view facing right, menacing but cute
```

### 7.3 Nhân vật chính — `player_<ten>_NN`

Bước 1, gen nhân vật đứng yên (idle):

```
[STYLE]
Draw ONE chibi hero, the player character: [MÔ TẢ, ví dụ: "young hooded rogue in a dark purple
cloak with a red scarf, holding a short glowing sword in the right hand"].
- chibi proportions: big round head about half of total height, short body
- front-facing, slightly turned to the right (3/4 view), standing idle pose, full body
- brave and determined expression, must stand out from dark backgrounds (bright accent colors)
- the character is about 30 pixels tall, centered
```

Bước 2, dùng chức năng **edit ảnh** của Gemini, đính kèm ảnh idle vừa duyệt:

```
This is my approved pixel-art hero sprite. Create a 4-frame WALK cycle of EXACTLY this character:
- 4 frames side by side in one horizontal row, evenly spaced, identical size, scale and vertical position
- keep head, face, colors, outline, weapon and proportions identical; only legs, arms and cloak move
- same pixel size as the original, 3/4 view facing right
- background: perfectly flat solid magenta #FF00FF, no shadow, no glow, no text
```

Làm tương tự cho `IDLE` (2 frame thở: đầu nhún xuống 1px) và `HURT` (1 frame).

### 7.4 Boss (64×64) — `boss_<ten>_NN`

```
[STYLE]
Draw ONE chibi BOSS: [MÔ TẢ, ví dụ: "giant grim reaper with a huge scythe and tattered black robe,
glowing purple eyes"].
- still chibi (big head ~40% height) but bulky and imposing, about 60 pixels tall, centered
- front-facing 3/4 view facing right
```

### 7.5 Tile mặt đất — `tile_<loai>_NN`

Ảnh AI khó liền mép, nên chỉ xin **texture vuông**. Phần cắt ô và làm liền mép do artpipe lo.

```
Using the attached image as the style reference (look at its ground):
Draw ONE seamless tileable square texture of [LOẠI: "dark mossy graveyard grass" / "packed dirt path" /
"cracked stone floor"], seen from directly above (top-down), pixel art.
- the image is a 64x64 pixel grid upscaled 16x, square image, fills the ENTIRE image edge to edge
- low contrast and dark (it is a background): use only muted dark teal / purple / brown tones
- small scattered details only (tiny grass blades, pebbles), no big objects, no paths, no light spots
- must tile seamlessly when repeated, no visible border, no text
```

Gen 3 loại: **cỏ** (nền chính), **đất** (đường đi), **đá lát** (khu vực đặc biệt). Phần viền chuyển tiếp giữa cỏ và đất do Claude vẽ bằng code (autotile).

### 7.6 Decor rải trên nền (16×16) — `decor_<chude>_NN`

```
[STYLE]
Draw a sheet of 12 tiny ground decorations for a top-down graveyard, arranged in a 4x3 grid, evenly
spaced, each about 12 pixels wide, not overlapping:
grass tufts (3 variants), small pebbles (2), scattered bones, a skull, dead leaves, a small mushroom,
purple flowers, a puddle, a crack in the ground
- seen from top-down with slight 3/4 tilt, dark muted colors so they stay in the background
```

### 7.7 Props (vật cản, đồ trang trí lớn) — `prop_<ten>_NN`

```
[STYLE]
Draw a lineup of 4 graveyard props, evenly spaced in one row, not overlapping, same pixel scale:
[CHỌN 4: rounded tombstone with cross carving / broken tombstone / stone cross / open grave with dirt
mound / dead twisted tree / iron fence segment / wooden coffin / standing torch with flame / hanging
lantern on a post / angel statue / pile of skulls / wooden signpost]
- top-down game view with 3/4 front tilt (we see the front face and a bit of the top)
- NOT isometric, NOT diagonal: every prop faces the camera straight-on; fences run perfectly
  horizontal left-to-right (so segments can be placed side by side), graves are axis-aligned rectangles
- each prop sized for a 32px tile grid: small props about 28 pixels tall, trees about 60 pixels tall
- slightly brighter than the ground so they read as obstacles, dark-fantasy mood
```

Cây chết và tượng nên gen riêng từng cái theo prompt 7.1 (thay chữ "enemy" bằng "prop"), vì chúng lớn.

### 7.8 Pickup & vật phẩm (16×16) — `item_<ten>_NN`

```
[STYLE]
Draw a sheet of 8 small collectible game items in a 4x2 grid, evenly spaced, each about 14 pixels big:
blue experience gem, green experience gem, red experience gem, gold coin, small treasure chest,
roast meat (health), magnet, bomb
- very bright saturated colors with a white highlight pixel so they pop on a dark background
```

### 7.9 Icon vũ khí và kỹ năng (16×16 hoặc 24×24) — `icon_<ten>_NN`

```
[STYLE]
Draw a sheet of 8 weapon icons for a survivor game, 4x2 grid, evenly spaced, each about 20 pixels big:
[ví dụ: throwing knife, magic wand, garlic bulb, holy water flask, axe, bible, lightning ring, fire wand]
- single object per icon, 45-degree angle, bold readable silhouette, bright accent color per weapon
```

### 7.10 Projectile và hiệu ứng (FX)

Mặc định **Claude vẽ bằng code** (đạn, vòng aura, tia sét, vụt chém), vì đây là hình khối đơn giản cần đúng palette và đúng số frame. Chỉ dùng Gemini khi muốn lấy concept:

```
[STYLE]
Draw a sheet of 6 magic projectiles in one row, evenly spaced: [ví dụ: blue magic bolt, fireball,
spinning knife, purple orb, ice shard, green poison blob]
- each about 12 pixels, flying to the right, bright core with 1px outline, NO glow halo
```

## 8. Lỗi thường gặp của Gemini → artpipe xử lý

| Lỗi | Xử lý |
|---|---|
| Nền không thật sự là `#FF00FF` hoặc bị lem hồng ở viền | Tách nền theo chroma có dung sai, khử viền ám màu |
| Pixel giả không đều | Tự dò kích thước khối pixel rồi downsample về lưới thật |
| Màu ngoài palette | Ép về `vaclone.hex` |
| Viền dày hoặc mất viền | Xóa viền rồi vẽ lại viền 1px `#1a1424` |
| Các frame lệch nhau | Căn theo đáy và tâm khối |
