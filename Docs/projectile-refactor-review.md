# Review: Projectile refactor + HomingProjectile

Phạm vi: `Assets/_Game/Scripts/Weapon/` (`Projectile`, `MovingProjectile`, `HomingProjectile`,
`AuraProjectile`, `GarlickWeapon`, `KnifeWeapon`, `MagicWandWeapon`).
Ngày: 2026-08-17. Nhánh `dev/enemy`, sau commit `4156219`.

Tiếp nối `aura-enemy-review.md` (10/08). Doc này viết theo hướng **gợi ý để tự làm** — nêu triệu chứng,
giải thích cơ chế, chỉ hướng đi và từ khoá tra cứu, không đưa lời giải hoàn chỉnh.

---

## Đã xử lý xong ✅

Ghi lại để khỏi lặp lại ở các vòng review sau:

- `IPoolable.OnSpawn/OnDespawn` từ `protected` → `public`. Trước đó chúng **không** implement được
  interface (C# không cho member `protected` implement interface), nên pool gọi phải bản default rỗng
  còn override trong `MovingProjectile` là dead code. Giờ đã nối đúng.
- `AcquireTarget` chuyển từ `Start()` sang `Init()`. `Start()` chỉ chạy một lần trong đời instance nên
  với object pooling, viên đạn tái sử dụng lần 2 trở đi không bao giờ tìm target lại.
- Điều kiện chọn target đã đúng: `_target == null || currentDistance <= minDistance`.
- `ApplyStats` bị xoá → chỉ còn một entry point là `Init`. Bớt được một cặp hàm gần trùng nhau.
- `_hits` → `static readonly` ở cả `HomingProjectile` và `AuraProjectile`.
- `HomingProjectile.OnDespawn` đã gọi `base.OnDespawn()` và reset `_target`.
- Steering bằng `Vector3.RotateTowards` đã có.
- `_owner` (dead field) trong `AuraProjectile` đã xoá.

Phần khó nhất — **vòng đời object pooling** — coi như đã qua.

---

## Bảng tổng hợp

| # | Mức | Vấn đề | Vị trí |
|---|-----|--------|--------|
| 1 | 🔴 Nghiêm trọng | `Awake` bị shadow → `AuraProjectile` không bao giờ cache `LocalScale` | `Projectile.cs:10`, `AuraProjectile.cs:15` |
| 2 | 🔴 Nghiêm trọng | `Stats.Size` vẫn chết, và `LocalScale` tự nhân dồn mỗi lần spawn | `Projectile.cs:19` |
| 3 | 🟠 Vừa | Homing không kiểm tra target còn sống → đuổi theo enemy đã despawn | `HomingProjectile.cs:47-56` |
| 4 | 🟠 Vừa | Aura của Garlic đứng yên stats sau khi level up | `GarlickWeapon.cs:14-32` |
| 5 | 🟡 Nhẹ | `_center` chỉ có giá trị trong Play mode → gizmo vô dụng lúc setup | `HomingProjectile.cs:8,23,44` |
| 6 | 🟡 Nhẹ | `Vector3.Distance` (có `sqrt`) khi chỉ cần so sánh | `HomingProjectile.cs:66` |
| 7 | 🟡 Nhẹ | `if(!_isAlive) return;` thừa | `HomingProjectile.cs:49` |
| 8 | 🟡 Nhẹ | `using System;` không còn dùng | `HomingProjectile.cs:1` |
| 9 | 🟡 Nhẹ | Nhánh `if (!_isInitialized)` là dead branch | `GarlickWeapon.cs:15,21` |
| 10 | ⚪ Kiến trúc | `MagicWandWeapon`: ép kiểu cụ thể + N viên cùng chỗ cùng target | `MagicWandWeapon.cs:24` |
| 11 | ⚪ Kiến trúc | `_enemyLayer` lặp lại trên từng prefab | `HomingProjectile.cs:11`, `AuraProjectile.cs:7` |
| 12 | ⚪ Kiến trúc | Aura vẫn có 2 đường damage song song + `OnTriggerExit2D` rỗng | `AuraProjectile.cs:85-93` |
| 13 | ⚪ API | `OverlapCircleNonAlloc` deprecated ở Unity 6000.3 | Homing + Aura |
| 14 | ⚪ Style | Naming lệch: `radius`, `turnRate`, `LifeTimeLeft`, `PierceLeft` | nhiều chỗ |

---

## 1. 🔴 `Awake` bị shadow → `AuraProjectile` mất `LocalScale`

`Projectile.cs:10` khai báo:

```csharp
private void Awake()
{
    LocalScale = transform.localScale;
}
```

Nhưng `AuraProjectile.cs:15` **cũng** khai báo `private void Awake()` của riêng nó.

Đây là cái bẫy Unity kinh điển. `Awake` không phải virtual method — Unity gọi nó qua hệ thống
messaging, tìm method theo **tên** trên type. Khi lớp con khai báo lại `Awake`, Unity chỉ gọi bản của
lớp con; bản ở lớp cha **không chạy**. Đây không phải override (không có `virtual`/`override`), mà là
*method hiding* — compiler thậm chí không cảnh báo vì cả hai đều `private`.

Hệ quả: mọi `AuraProjectile` có `LocalScale == Vector3.zero`. Ngay khi bạn sửa mục #2 để thực sự ghi
scale ra transform, aura sẽ co về kích thước 0 và biến mất khỏi màn hình.

`MovingProjectile` và `HomingProjectile` không khai báo `Awake` nên hiện đang may mắn thoát.

**Hướng sửa:** đây là lý do tồn tại của mẫu `protected virtual` + `override` + gọi `base`. Cho lớp cha
một `Awake` có thể override được, lớp con override và gọi `base.Awake()` ở dòng đầu.

Cùng một cái bẫy áp dụng cho `Start`, `Update`, `OnEnable`, `OnDestroy`, `OnTriggerEnter2D`... Lưu ý
`MovingProjectile.Update` đang là `protected virtual` — đúng chuẩn rồi, làm theo mẫu đó.

> Tra cứu: "Unity Awake inheritance base class not called", "C# method hiding vs overriding",
> warning `CS0108` (bạn sẽ thấy warning này nếu đổi một trong hai thành non-private).

---

## 2. 🔴 `Stats.Size` vẫn chết, và giờ còn nhân dồn

`Projectile.cs:19`:

```csharp
LocalScale = LocalScale * Stats.Size;
```

Hai vấn đề chồng lên nhau.

**Thứ nhất — vẫn không có ai ghi ra transform.** Dòng này gán vào *field*. Sau khi `ApplyStats` bị xoá,
`transform.localScale` không còn được ghi ở bất kỳ đâu trong codebase. Kiểm chứng nhanh: grep
`LocalScale` toàn project chỉ ra 3 dòng — khai báo (`:8`), gán trong `Awake` (`:12`), gán trong `Init`
(`:19`). Không dòng nào đọc nó. Field write-only ⇒ `WeaponLevelStats.Size` và `PlayerStats.ProjectileSize`
đang là stat chết trên toàn bộ vũ khí.

**Thứ hai — nó tự nhân dồn.** `Awake` chạy 1 lần, nhưng `Init` chạy **mỗi lần spawn**, và mỗi lần lại
nhân `LocalScale` với `Size` lần nữa. Với `Size = 1.5`, sau 10 lần tái sử dụng từ pool thì
`LocalScale = base × 1.5¹⁰ ≈ base × 57`. Hiện chưa nổ vì không ai đọc — nhưng đó chính là quả mìn: ngay
khi bạn thêm dòng ghi ra transform, viên đạn sẽ phình to dần theo số lần được pool tái sử dụng.

**Hướng sửa:** phân biệt rõ hai vai trò.

- `LocalScale` là **dữ liệu gốc bất biến** — scale của prefab. Ghi đúng một lần trong `Awake`, sau đó
  chỉ đọc, **không bao giờ ghi lại**.
- `transform.localScale` là **kết quả dẫn xuất** — tính lại mỗi lần spawn từ `LocalScale` và `Stats.Size`.

Quy tắc chung đáng nhớ: khi bạn có một giá trị gốc và một giá trị đã áp modifier, đừng ghi kết quả ngược
vào biến gốc. Mất giá trị gốc là mất khả năng tính lại — và trong môi trường pooling thì "tính lại" xảy
ra liên tục.

**Lưu ý dây chuyền:** `AuraProjectile.cs:33` tính `radius` từ `_collider.radius * lossyScale`. Sửa xong
mục này thì bán kính aura sẽ bắt đầu phản ứng theo `Size` — cần chỉnh lại số trong SO cho khớp. Và phải
sửa mục #1 **trước**, nếu không aura sẽ scale về 0.

---

## 3. 🟠 Homing không kiểm tra target còn sống

`HomingProjectile.cs:50` chỉ check `_target != null`.

Vấn đề: enemy chết → `DespawnObject` → `SetActive(false)` → về pool. GameObject **không bị Destroy**,
Transform vẫn tồn tại, nên `_target != null` vẫn đúng vĩnh viễn.

Kịch bản dựng lại được: bắn một viên đạn → target trúng đạn khác và chết → wave sau enemy đó được pool
tái sử dụng, spawn ở toạ độ khác → viên đạn đang bay lập tức bẻ lái đuổi theo qua nửa map. Với
`turnRate = 270°/s` thì nhìn rất rõ: đạn quay ngoắt giữa không trung.

Ở vòng review trước bug này chưa lộ vì đạn bay thẳng. Giờ đã có steering nên nó sống dậy.

**Hướng sửa:** cần một tiêu chí "target còn dùng được". Với pooling, `!= null` là không đủ —
`activeInHierarchy` mới phản ánh việc object có đang trong pool hay không. Khi target không còn hợp lệ,
quyết định xem nên tìm lại target mới hay để đạn bay thẳng tiếp (gợi ý: tìm lại cho cảm giác tốt hơn,
và bạn đã có sẵn `AcquireTarget()` để gọi).

> Chú ý cái bẫy phụ: `UnityEngine.Object` overload toán tử `==` để trả `true` cho object đã bị Destroy.
> Cái đó khác với "đang nằm trong pool" — object trong pool vẫn sống, chỉ bị tắt. Nên hai phép kiểm tra
> này bổ sung cho nhau chứ không thay thế nhau.

Cân nhắc thêm: bán kính tìm lại target khi đang bay **không nên** dùng chung số với `radius` tầm bắn.
Viên đạn đã bay xa 10 unit mà vẫn quét bán kính đầy đủ từ vị trí hiện tại của nó ⇒ tầm với thực tế rộng
gần gấp đôi tầm bắn danh nghĩa.

---

## 4. 🟠 Aura Garlic không cập nhật stats khi level up

Bỏ `ApplyStats` giải quyết được chuyện trùng lặp, nhưng cắt luôn đường cập nhật duy nhất của aura.
`GarlickWeapon` giờ spawn một lần rồi `return` mãi mãi (`:15`), nên `AuraProjectile.Stats` chốt cứng ở
level tại thời điểm spawn. Người chơi nâng cấp Garlic → damage/size/tick interval không đổi.

Đây là đánh đổi có chủ ý hay sót? Nếu là sót:

**Hướng sửa:** gọi mỗi frame là sai (đó là lý do bản cũ có comment `//later refactor ???`). Stats chỉ
đổi tại đúng một thời điểm — khi lên level. Vậy nên đường cập nhật nên bắt nguồn từ `Weapon.TryLevelUp()`
chứ không phải từ `Fire()`. Nghĩ theo hướng: `TryLevelUp` thành công → thông báo cho vũ khí biết để nó
tự làm mới thứ gì đang tồn tại dai (aura, orbit...). Vũ khí bắn-rồi-quên thì không cần làm gì.

Mẫu này sẽ dùng lại được cho orbit weapon sau này, nên đáng đầu tư làm cho tử tế.

---

## 5–9. Nhóm nhẹ

**5. `_center` (`:8,23,44`)** — chỉ được gán trong `AcquireTarget`, tức chỉ có giá trị sau lần spawn đầu
trong Play mode. Ngoài Play mode nó là `(0,0)` nên `OnDrawGizmosSelected` vẽ vòng tròn ở gốc toạ độ —
đúng lúc bạn cần gizmo nhất (khi đang chỉnh `radius` trên prefab) thì nó lại vô dụng. Gizmo nên vẽ từ
`transform.position`. Làm vậy thì field `_center` không còn lý do tồn tại → thành local.

**6. `GetDistanceTo` (`:66`)** — `Vector3.Distance` có một phép `sqrt`. Bạn chỉ dùng kết quả để *so sánh*
xem cái nào gần hơn, mà `sqrt` là hàm đơn điệu tăng ⇒ so sánh bình phương cho thứ tự y hệt với chi phí
rẻ hơn. Đây là tối ưu tiêu chuẩn trong gamedev, đáng thành phản xạ. Nếu đổi thì đổi tên hàm luôn
(`GetSqrDistanceTo`) — trả về bình phương mà tên nói "Distance" là bẫy cho chính mình sau này, đặc biệt
nếu có lúc bạn muốn so nó với một ngưỡng đọc từ SO.

**7. `if(!_isAlive) return;` (`:49`)** — `MovingProjectile.Update:31` đã chặn trước khi gọi `Move`.
Check thừa gây hiểu nhầm rằng `Move` có thể được gọi khi đã chết.

**8. `using System;` (`:1`)** — còn sót từ hồi dùng `Math.Abs`.

**9. `GarlickWeapon.cs:15,21`** — `if (_isInitialized) return;` rồi ngay sau đó `if (!_isInitialized)`.
Nhánh sau luôn đúng ⇒ dead branch.

---

## 10. ⚪ `MagicWandWeapon` — hai vấn đề chưa đụng tới

**Ép kiểu cụ thể** (`:24`): `SpawnObject<HomingProjectile>` trong khi `KnifeWeapon` đã đổi sang
`MovingProjectile`. Vũ khí không cần biết đạn của nó có homing hay không — nó chỉ cần một thứ `Init`
được. Thống nhất về `MovingProjectile` cho cả hai.

**N viên trùng nhau hoàn toàn** (`:20-30`): cả `count` viên spawn tại cùng `ctx.Origin.position`, cùng
`radius`, cùng luật "chọn gần nhất" ⇒ ra cùng một `_target`, chồng khít lên nhau, nhìn như một viên.
Nâng `ProjectileCount` sẽ không thấy khác biệt gì ngoài damage.

Lưu ý bản chất: cái này **không** liên quan tới việc `_hits` là `static`. Buffer chung hoàn toàn an toàn
vì mỗi lần gọi đều ghi đè rồi đọc xong ngay trong cùng một lời gọi hàm đồng bộ. Nguyên nhân là *điểm
xuất phát và luật chọn giống nhau*.

**Hướng sửa:** viên thứ `i` nên khoá target gần thứ `i`. Với `hitCount` chỉ vài chục thì selection thô
(lặp `i+1` lần, mỗi lần loại target đã chọn) là đủ — chưa cần sort. Xử lý cả trường hợp
`hitCount < count`: cho phần dư quay lại target gần nhất, hoặc bay thẳng.

Việc này ăn khớp với thay đổi ở mục *"Khoảng hở cooldown"* bên dưới — làm chung một lượt thì gọn hơn.

---

## 11. ⚪ `_enemyLayer` lặp trên từng prefab

Layer enemy là **hằng số của game**, không phải tham số tinh chỉnh per-prefab. Để nó thành `[SerializeField]`
nghĩa là mỗi prefab projectile mới bạn tạo ra đều phải nhớ set tay, quên thì `LayerMask` = 0 → không tìm
thấy gì → fail hoàn toàn im lặng, không exception, không log. Đúng kiểu bug ngốn nửa buổi.

**Hướng sửa:** một chỗ duy nhất giữ định nghĩa layer, đọc bằng `LayerMask.GetMask("Enemy")`. Project đã
có sẵn layer đặt tên tử tế (`Enemy` = 6, `Player` = 7, `PlayerProjectile` = 8) nên tra theo tên sẽ không
vỡ khi index đổi. Cache lại kết quả — `GetMask` phải tra chuỗi nên đừng gọi mỗi frame.

Đây cũng là chỗ tự nhiên để đặt `ContactFilter2D` dùng chung khi bạn chuyển sang API mới ở mục #13.

---

## 12. ⚪ Aura: 2 đường damage + `OnTriggerExit2D` rỗng

`AuraProjectile` vừa quét `OverlapCircleNonAlloc` mỗi frame (`:34`) vừa có `OnTriggerEnter2D` (`:85`),
cả hai cùng gọi `TryDamage`. Dictionary cooldown che được double-damage nên kết quả không sai, nhưng đây
là hai nguồn sự thật cho cùng một việc — sửa luật ở một chỗ mà quên chỗ kia là ra bug.

Chọn một. Quét chủ động (`OverlapCircle`) linh hoạt hơn vì kiểm soát được thời điểm và không phụ thuộc
collider, còn trigger thì rẻ hơn nhưng bị động. Với aura damage-over-time, quét chủ động hợp hơn.

`OnTriggerExit2D` chỉ có `return;` (`:90-93`) — xoá.

---

## 13. ⚪ `OverlapCircleNonAlloc` đã deprecated

Project đang ở Unity `6000.3.7f1`. `Physics2D.OverlapCircleNonAlloc` bị đánh dấu obsolete, sẽ sinh
warning. Bản thay thế nhận `ContactFilter2D` + `List<Collider2D>`, và list tự grow.

Cái này giải quyết luôn một hạn chế âm thầm của bản hiện tại: mảng 64 phần tử ⇒ enemy thứ 65 trở đi bị bỏ
qua **không một lời cảnh báo**. Với homing tìm gần nhất thì thường vô hại, nhưng aura giữa bầy đông sẽ
mất damage mà không ai biết.

> Tra cứu: `Physics2D.OverlapCircle(Vector2, float, ContactFilter2D, List<Collider2D>)`,
> `ContactFilter2D.SetLayerMask`, `useTriggers`.

Vẫn giữ nguyên nguyên tắc `static readonly` cho buffer — chỉ đổi kiểu chứa từ mảng sang `List`.

---

## 14. ⚪ Style

- `radius`, `turnRate` (`HomingProjectile.cs:9,10`) thiếu prefix `_`, trong khi `_target`, `_enemyLayer`
  ở ngay cạnh thì có.
- `LifeTimeLeft`, `PierceLeft` (`MovingProjectile.cs:6,7`) — PascalCase cho private field.
- `_cirleProjectile` (`GarlickWeapon.cs:6`) — typo "circle".
- `//what` (`HomingProjectile.cs:53`) — xem ghi chú về `RotateTowards` bên dưới.
- `Mathf. Deg2Rad` (`:53`) có khoảng trắng thừa sau dấu chấm. Hợp lệ về cú pháp nhưng IDE sẽ không
  auto-format lại giúp.

⚠️ **Cảnh báo trước khi đổi tên `radius` / `turnRate`:** Unity map dữ liệu serialize theo **tên field**.
Đổi tên là mất giá trị đã set trên prefab (`radius: 4`, `turnRate: 270` đang nằm trong
`MagicWandProjectile.prefab`) và nó sẽ âm thầm về giá trị mặc định trong code. Hoặc set lại tay sau khi
đổi, hoặc dùng `[FormerlySerializedAs("radius")]` (namespace `UnityEngine.Serialization`).

---

## Ghi chú: `Vector3.RotateTowards` làm gì (giải đáp `//what`)

```csharp
Vector3.RotateTowards(current, target, maxRadiansDelta, maxMagnitudeDelta)
```

Xoay vector `current` **về phía** `target`, nhưng không xoay quá `maxRadiansDelta` radian trong lần gọi
này. Tham số cuối giới hạn thay đổi **độ dài** vector — truyền `0f` nghĩa là giữ nguyên độ dài, đúng
điều bạn muốn vì `Direction` là vector đơn vị.

Vì sao nhân với `deltaTime`: `turnRate` là tốc độ quay tính bằng **độ mỗi giây**. Nhân `Deg2Rad` để đổi
sang radian (hàm nhận radian), nhân `deltaTime` để ra "được phép quay bao nhiêu trong frame này". Nhờ
vậy tốc độ bẻ lái không đổi theo framerate — 30fps và 144fps cho quỹ đạo giống nhau.

Trực giác về giá trị: `turnRate = 270` nghĩa là đạn quay được 3/4 vòng mỗi giây. Càng cao càng bám dai
(nhưng dễ thành "không thể né"); càng thấp thì đạn vọt qua mục tiêu rồi vòng lại — thường cho cảm giác
hay hơn. Đây là tham số nên tune bằng tay trong game chứ không phải suy ra bằng lý thuyết.

---

## Việc còn treo từ các buổi trao đổi trước

Chưa động tới, ghi lại để khỏi quên:

**A. Khoảng hở cooldown của Magic Wand.** Hiện `Weapon.Tick` tiêu cooldown vô điều kiện, nên nếu muốn
"chỉ bắn khi có enemy trong tầm" thì việc despawn viên đạn không lấy lại được cooldown đã mất → enemy vào
tầm ngay sau đó vẫn phải chờ hết chu kỳ. Hướng đã bàn: cho `Fire` trả về `bool` (có bắn thật không), chỉ
reset `_cooldownTimer` khi trả `true`, và chuyển việc dò target lên tầng `Weapon` để quyết định trước khi
spawn. Khi đó `_cooldownTimer` chạm 0 rồi nằm im ⇒ enemy vào tầm là bắn ngay frame đó.

Làm việc này cũng gỡ luôn mục #10 (weapon nắm cả danh sách hit nên phân phối target khác nhau được) và
đưa `SearchRadius` về `WeaponLevelStats` để nâng cấp theo level.

**B. Enemy dynamic body → kinematic + separation.** Xem `enemy-spatial-hash-plan.md`.

---

## Thứ tự đề xuất

1. **#1 rồi #2** — phải theo đúng thứ tự này. Sửa #2 trước khi sửa #1 thì aura co về scale 0.
2. **#3** — bug nhìn thấy được trong gameplay, sửa nhanh.
3. **#4** — quyết định xem có phải sót không, rồi làm đường cập nhật khi level up.
4. Nhóm 5–9 — dọn dẹp, làm một lượt.
5. **#10 + việc treo A** — làm chung, vì cùng đụng `MagicWandWeapon` và `Weapon.Tick`.
6. #11–14 — khi có thời gian rảnh.

Nhận xét chung: chất lượng đang lên rõ qua từng vòng. Bug lần này (#1, #2) không còn là lỗi logic mà là
**đặc thù của Unity** — cách messaging gọi `Awake` và cách serialize theo tên field. Đó là loại kiến thức
chỉ tích luỹ được qua va vấp, không suy ra được từ C# thuần. Đáng ghi lại.
