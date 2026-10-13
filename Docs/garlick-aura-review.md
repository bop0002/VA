# Review: Garlick / CircleProjectile (aura damage tick)

Phạm vi: `Assets/_Game/Scripts/Weapon/CircleProjectile.cs`, `GarlickWeapon.cs`, `Weapon.cs`.
Ngày: 2026-08-07.

Hướng làm tổng thể đúng — list target + `OnTriggerEnter2D`/`OnTriggerExit2D` là cách chuẩn cho vùng damage
liên tục, và tách `DamageInRange()` ra hàm riêng đọc rất rõ. Dưới đây là các vấn đề còn lại, xếp theo mức độ.

---

## Bảng tổng hợp

| # | Mức | Vấn đề | Vị trí |
|---|-----|--------|--------|
| 1 | 🔴 Nghiêm trọng | Aura tích luỹ vô hạn | `GarlickWeapon.cs:20-31` |
| 2 | 🔴 Nghiêm trọng | `foreach` + `Remove` → InvalidOperationException | `CircleProjectile.cs:34-37` + `:71` |
| 3 | 🟠 Vừa | `return` thừa làm skip `Move()` một frame | `CircleProjectile.cs:26` |
| 4 | 🟠 Vừa (tiềm ẩn) | `_damageables` không được dọn khi despawn | `CircleProjectile.cs:66`, `:75-80` |
| 5 | 🟡 Nhẹ | `DamageTick` không reset khi lấy lại từ pool | `CircleProjectile.cs:10`, `:12-15` |
| 6 | 🟡 Nhẹ | `Add` không chống trùng | `CircleProjectile.cs:61` |
| 7 | 🟡 Nhẹ | `DamageTickInterval` = 0 → damage mỗi frame | `Weapon.cs:44` |
| 8 | ⚪ Design | Damage đến từ 2 nguồn (enter + tick) | `CircleProjectile.cs:60` |
| 9 | ⚪ Style | Quy ước đặt tên lệch | `CircleProjectile.cs:8`, `:10` |

---

## 1. 🔴 Aura tích luỹ vô hạn

**Vị trí:** `GarlickWeapon.cs:20-31`

**Vấn đề:** `CircleProjectile.Update()` đã bỏ phần đếm `LifeTimeLeft` → aura không bao giờ despawn
(đúng ý đồ). Nhưng `Weapon.Tick()` vẫn gọi `Fire()` lặp lại theo cooldown, và `Fire()` thì spawn thêm
`count` aura mới mỗi lần.

Hệ quả: cooldown 1s → sau 10 giây có 10 aura chồng đúng một chỗ → damage nhân 10, và pool phình mãi
vì không object nào được trả về.

**Phương pháp — chọn 1 trong 3:**

**(a) Weapon giữ reference, `Fire()` idempotent.** Ít thay đổi kiến trúc nhất.
`GarlickWeapon` giữ `List<CircleProjectile> _auras`. `Fire()` chỉ spawn phần còn thiếu so với
`GetProjectileCount()`, rồi đẩy chỉ số mới xuống các aura đang sống. Lợi thế: level up / buff player
tự động ăn vào aura đang chạy, vì `Fire()` vẫn nổ đều theo cooldown.

Cần thêm một hàm public trên `CircleProjectile` kiểu `ApplyStats(ProjectileStats)` — cập nhật `Stats`
và `localScale` mà **không** reset `DamageTick`, để nhịp damage không bị giật mỗi lần weapon fire.

```csharp
// GarlickWeapon.Fire — ý tưởng
while (_auras.Count < count) { spawn + Init + _auras.Add(...); }
for (int i = 0; i < _auras.Count; i++) _auras[i].ApplyStats(stats);
```

**(b) Tách khỏi cơ chế cooldown-fire.** Thêm cờ vào `Weapon` kiểu `protected virtual bool IsContinuous => false;`
và `Tick()` chỉ gọi `Fire()` một lần nếu weapon là continuous. Sạch về mặt khái niệm (aura ≠ đạn bắn ra),
nhưng đụng vào base class nên ảnh hưởng mọi weapon sau này.

**(c) Aura không phải projectile.** Cho Garlick spawn một GameObject con gắn thẳng vào player lúc
`Acquire`, không đi qua `ObjectPoolingManager` chút nào. Đúng bản chất nhất (nó là aura vĩnh viễn, không
phải viên đạn), nhưng phải viết class riêng, không tái dùng `Projectile`.

> Gợi ý: (a) nếu muốn đi tiếp nhanh, (c) nếu sau này còn nhiều vũ khí dạng aura/orbit.

---

## 2. 🔴 `foreach` + `Remove` trong lúc lặp → InvalidOperationException

**Vị trí:** `CircleProjectile.cs:34-37` (vòng lặp) và `:71` (`Remove`)

**Vấn đề:** Chuỗi sự kiện khi một enemy chết trong vùng:

```
DamageInRange()  →  foreach đang duyệt _damageables
  → damageable.TakeDamage()
    → EnemyView.TakeDamage()  →  máu <= 0
      → ObjectPoolingManager.DespawnObject()
        → obj.SetActive(false)
          → Unity bắn OnTriggerExit2D lên aura
            → _damageables.Remove(damageable)   ⚠ list bị sửa GIỮA foreach
  → vòng lặp kế tiếp ném InvalidOperationException
```

Nghĩa là: từ 2 enemy trở lên trong vùng, chỉ cần một con chết là có khả năng vỡ giữa combat.

**Phương pháp:** duyệt ngược bằng `for` thay vì `foreach` — chỉ số lớn về nhỏ nên phần tử bị xoá
không làm lệch các phần tử chưa duyệt.

```csharp
for (int i = _damageables.Count - 1; i >= 0; i--)
    _damageables[i].TakeDamage(Stats.Damage);
```

Nếu muốn chắc chắn tuyệt đối (phòng trường hợp `TakeDamage` gây ra thay đổi phức tạp hơn), copy list ra
buffer tạm rồi duyệt buffer — nhưng nhớ tái dùng buffer chứ đừng `new List<>()` mỗi tick.

---

## 3. 🟠 `return` thừa làm skip `Move()`

**Vị trí:** `CircleProjectile.cs:26`

```csharp
DamageTick -= deltaTime;
if(DamageTick <= 0f)
{
    DamageInRange();
    return;          // ← Move(deltaTime) bị bỏ qua
}
Move(deltaTime);
```

**Vấn đề:** đúng frame gây damage thì aura không cập nhật vị trí theo player → giật một frame.
`DamageInRange()` và `Move()` hoàn toàn độc lập, không có lý do gì để loại trừ nhau.

**Phương pháp:** bỏ `return`, hoặc gọi `Move(deltaTime)` lên trước khối `if`.

---

## 4. 🟠 `_damageables` không được dọn khi despawn (tiềm ẩn)

**Vị trí:** `CircleProjectile.cs:66` (guard) và `:75-80` (`Despawn`)

**Vấn đề:** `Despawn()` set `_isAlive = false` **trước** khi gọi `DespawnObject()`. Ngay sau đó Unity bắn
`OnTriggerExit2D` cho từng enemy còn trong vùng, nhưng dòng 66 `if (!_isAlive) return;` chặn hết →
list giữ nguyên toàn bộ target cũ.

Hiện chưa cắn vì aura không despawn. Nhưng sẽ cắn ngay khi:
- bạn cho aura có thời hạn, hoặc
- dùng lại `CircleProjectile` cho một vũ khí khác có `Duration`.

Lúc đó object lấy lại từ pool mang theo danh sách target từ kiếp trước → đánh trúng enemy ở tận đầu bản đồ,
hoặc `TakeDamage` lên enemy đã được pool tái sử dụng thành con khác.

**Phương pháp:** clear list ở `OnDespawn()` — đây là hook của `IPoolable`, được `ObjectPoolingManager`
gọi đúng thời điểm trả object về pool, và không bị guard `_isAlive` chi phối.

```csharp
public override void OnDespawn()
{
    base.OnDespawn();
    _damageables.Clear();
}
```

---

## 5. 🟡 `DamageTick` không reset khi lấy lại từ pool

**Vị trí:** `CircleProjectile.cs:10` (`protected float DamageTick = 0;`), `:12-15` (`Awake`)

**Vấn đề:** field initializer và `Awake()` chỉ chạy đúng một lần lúc `Instantiate`. Object lấy lại từ pool
không chạy lại chúng, nên `DamageTick` giữ giá trị dở dang từ kiếp trước.

`Awake()` đang dùng đúng mục đích (khởi tạo `new List<>()` — thứ chỉ cần làm một lần). Nhưng
**mọi giá trị cần trạng thái sạch theo từng lần spawn** thì phải nằm ở `Init()` hoặc `OnSpawn()`.

**Phương pháp:** gán `DamageTick = 0f;` trong `Init()` (nếu muốn tick ngay khi spawn) hoặc
`= Stats.DamageTickInterval` (nếu muốn chờ đủ một nhịp). Riêng list có thể khai báo thẳng
`= new List<IDamageable>()` tại chỗ khai báo rồi bỏ `Awake()` cho gọn.

---

## 6. 🟡 `Add` không chống trùng

**Vị trí:** `CircleProjectile.cs:61`

**Vấn đề:** add thẳng không kiểm tra. Nếu prefab enemy có nhiều hơn một collider (body + hitbox chẳng hạn),
`OnTriggerEnter2D` bắn nhiều lần cho cùng một `IDamageable` → vào list 2 lần → ăn damage gấp đôi mỗi tick.
Tệ hơn: `List.Remove()` chỉ xoá phần tử **đầu tiên** khớp, nên bản sao còn kẹt lại vĩnh viễn kể cả khi
enemy đã ra khỏi vùng.

**Phương pháp:** check `if (_damageables.Contains(damageable)) return;` trước khi add. Với số lượng nhỏ
(vài chục target) thì `List.Contains` là O(n) nhưng vẫn rẻ hơn `HashSet` về mặt cache và không sinh rác.

**Liên quan:** `other.gameObject.TryGetComponent` chỉ tìm trên đúng GameObject mang collider. Nếu collider
đặt ở child còn `EnemyView` ở root thì không tìm thấy `IDamageable`. Nếu prefab enemy có cấu trúc như vậy
thì cần `GetComponentInParent`.

---

## 7. 🟡 `DamageTickInterval` = 0 → damage mỗi frame

**Vị trí:** `Weapon.cs:44`

**Vấn đề:** `damageTickInterval` được map từ `GetCooldown()`, tức `Stats.Cooldown / CooldownRate`.
Nếu `Cooldown` trong `WeaponLevelStats` của Garlick để 0 (giá trị mặc định của một field float trong SO
chưa điền) thì `DamageTick` luôn `<= 0` → gây damage mỗi frame, enemy bốc hơi tức thì.

**Phương pháp:** kẹp sàn ở chỗ gán — `Mathf.Max(0.05f, ...)` — hoặc validate trong `WeaponData.OnValidate()`
để phát hiện ngay trong Editor thay vì lúc chạy.

---

## 8. ⚪ Damage đến từ 2 nguồn (design, không phải lỗi)

**Vị trí:** `CircleProjectile.cs:60`

Enemy ăn damage ngay lúc `OnTriggerEnter2D`, rồi lại ăn ở nhịp tick. Con bước vào vùng ngay sau một tick sẽ
ăn 2 phát rất sát nhau; con bước vào ngay trước tick thì cũng vậy. Nhịp damage không đều theo thời điểm vào vùng.

- Nếu muốn "chạm là đau ngay" → giữ nguyên, đây là chủ ý hợp lý.
- Nếu muốn nhịp đều tuyệt đối → `OnTriggerEnter2D` chỉ add vào list, để `DamageInRange()` lo toàn bộ damage.

---

## 9. ⚪ Quy ước đặt tên lệch

**Vị trí:** `CircleProjectile.cs:8` (`_damageables`), `:10` (`DamageTick`)

Cả hai đều `protected` nhưng một cái underscore + camelCase, một cái PascalCase. Trong `Projectile` bạn
đang dùng PascalCase cho protected (`Direction`, `Stats`, `LifeTimeLeft`, `PierceLeft`) và underscore cho
private (`_isAlive`). Theo đó thì `_damageables` nên là `Damageables`, hoặc đổi thành `private` nếu subclass
không cần đụng tới.

---

## Thứ tự đề nghị

1. **#2** — sửa nhanh nhất (đổi `foreach` → `for` ngược), chặn crash ngay.
2. **#3** — bỏ một chữ `return`.
3. **#1** — cần quyết định kiến trúc, làm sau khi đã chốt hướng (a)/(b)/(c).
4. **#4, #5, #6, #7** — dọn một lượt, đều là sửa vài dòng.
5. **#8, #9** — tuỳ ý.

## Ghi chú ngoài phạm vi

`Weapon.cs:39` vẫn dùng `playerStats.SpeedRate` cho tốc độ đạn. `SpeedRate` đang là tốc độ di chuyển player
(`PlayerView.cs:30`, asset đang set = 2), còn `ProjectileSpeedRate` (= 1) không ai đọc. Gần như chắc chắn
dòng đó phải là `ProjectileSpeedRate` — nhưng nó đổi feel game nên để bạn quyết.
