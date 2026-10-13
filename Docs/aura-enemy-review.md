# Review: AuraProjectile + Enemy

Phạm vi: `Assets/_Game/Scripts/Weapon/` (`AuraProjectile`, `Projectile`, `GarlickWeapon`, `Weapon`),
`Assets/_Game/Scripts/Enemy/` (`EnemyController`, `EnemyView`, `IDamageable`, `DamagingContext`).
Ngày: 2026-08-10.

Thay thế `garlick-aura-review.md` (07/08) — bản đó viết cho `CircleProjectile.cs` đã bị xoá và đổi thành
`AuraProjectile`. Các mục #3, #4, #5, #7 của bản cũ đã được xử lý xong.

Tổng thể hướng đi đúng: stats là `readonly struct` immutable, `Weapon` là plain C# class không phải
MonoBehaviour, tick tập trung qua `EnemyController`/`WeaponController` thay vì N cái `Update`, pooling đi
qua interface `IPoolable`. Dưới đây là phần còn lại, xếp theo mức độ.

---

## Bảng tổng hợp

| # | Mức | Vấn đề | Vị trí |
|---|-----|--------|--------|
| 1 | 🔴 Nghiêm trọng | `RemoveAt` trong vòng lặp tiến → bỏ sót enemy | `EnemyController.cs:32-46` |
| 2 | 🔴 Nghiêm trọng | `for` ngược vẫn chưa an toàn với mutation từ trigger | `AuraProjectile.cs:31-39` |
| 3 | 🟠 Vừa | Despawn trước khi tắt `IsAlive` | `EnemyView.cs:98-102` |
| 4 | 🟠 Vừa | Knockback sai hướng và sai thời điểm | `EnemyView.cs:104-108` |
| 5 | 🟠 Vừa | Enemy vừa vào aura ăn 2 hit sát nhau | `AuraProjectile.cs:71-72` |
| 6 | 🟠 Vừa | `new Material` + `Shader.Find` mỗi enemy | `EnemyView.cs:39-45` |
| 7 | 🟠 Vừa | `LifeTimeLeft` / `PierceLeft` là dead state | `AuraProjectile.cs:52-53` |
| 8 | 🟡 Nhẹ | Aura bám player trong `Update` → jitter | `AuraProjectile.cs:58-61` |
| 9 | 🟡 Nhẹ | `CompareTag` mỗi va chạm thay vì lọc bằng Layer | `Projectile.cs:48`, `AuraProjectile.cs:66,78` |
| 10 | 🟡 Nhẹ | Coroutine flash không dừng khi despawn | `EnemyView.cs:19-35`, `:85-88` |
| 11 | ⚪ Kiến trúc | `AuraProjectile` kế thừa sai tầng | `AuraProjectile.cs:4` |
| 12 | ⚪ Kiến trúc | `Init` và `ApplyStats` duplicate | `AuraProjectile.cs:41-56` |
| 13 | ⚪ Kiến trúc | `_isInitialized` là cờ thừa | `GarlickWeapon.cs:7,21-35` |
| 14 | ⚪ Kiến trúc | `DamageTickInterval` bị buộc dính vào cooldown | `Weapon.cs:45` |
| 15 | ⚪ Kiến trúc | `IDamageable` và `DamagingContext` nằm lệch folder | `Enemy/`, `Weapon/` |
| 16 | ⚪ Style | Naming lệch giữa Player và Enemy module | `EnemyController`, `EnemyView` |
| 17 | ⚪ Style | Nit gộp (using thừa, `<` vs `<=`, cooldown drift, `Debug.Log`) | nhiều chỗ |

---

## 1. 🔴 `RemoveAt` trong vòng lặp tiến → bỏ sót enemy

**Vị trí:** `EnemyController.cs:32-46`

**Vấn đề:** sau `RemoveAt(i)` + `continue`, `i++` vẫn chạy → phần tử vừa dồn xuống index `i` bị bỏ qua.
Hệ quả kép: enemy đó không được `Tick()` frame này (nhỏ), và nếu nó **cũng** chết thì nó ở lại list thêm
một frame nữa. Nhiều enemy chết cùng lúc → list dồn rác dần.

Phụ: `Time.deltaTime` là property call, đang gọi lại mỗi vòng lặp.

**Phương pháp:** duyệt ngược. Kèm swap-remove để xoá O(1) thay vì O(n) (thứ tự list không quan trọng ở đây):

```csharp
float deltaTime = Time.deltaTime;
for (int i = _enemies.Count - 1; i >= 0; i--)
{
    if (!_enemies[i].IsAlive)
    {
        _enemies[i] = _enemies[^1];
        _enemies.RemoveAt(_enemies.Count - 1);
        continue;
    }
    _enemies[i].Tick(deltaTime);
}
```

---

## 2. 🔴 `for` ngược vẫn chưa an toàn — trả lời câu hỏi ở `AuraProjectile.cs:36`

**Vị trí:** `AuraProjectile.cs:31-39` (vòng lặp), `:82` (`Remove` trong `OnTriggerExit2D`)

**Câu hỏi trong code:** *"for each thi 2 enemy tro len lai crash???"* — đúng, và đây là nguyên nhân:

```
DamageInRange()  →  đang duyệt _damageables
  → damageable.TakeDamage()
    → EnemyView.TakeDamage()  →  máu <= 0
      → ObjectPoolingManager.DespawnObject()  →  obj.SetActive(false)
        → Unity bắn OnTriggerExit2D lên aura
          → _damageables.Remove(damageable)   ⚠ list bị sửa GIỮA lúc duyệt
  → foreach ném InvalidOperationException
```

**Vấn đề còn lại:** đổi sang `for` ngược chỉ chặn được exception, **không** chặn được lỗi logic. `for` ngược
chỉ an toàn khi phần tử bị xoá nằm ở index `>= i`. Ở đây enemy bị xoá là do trigger bắn ra, index của nó
hoàn toàn có thể nhỏ hơn `i` → các phần tử phía sau dịch xuống → bạn skip một target hoặc gây damage lên
target đã duyệt.

Vẫn còn hai vấn đề nữa cùng gốc rễ, đều xuất phát từ việc "tự nuôi một list target":
- Stale reference: enemy về pool rồi được tái sử dụng thành con khác, aura vẫn cầm reference cũ.
- Trùng lặp khi một enemy có nhiều collider (đúng như comment ở `:72`) — `List.Remove` chỉ xoá bản đầu
  tiên nên bản sao kẹt lại vĩnh viễn.

**Phương pháp — bỏ hẳn trigger cho aura, chủ động quét khi cần:**

```csharp
private static readonly Collider2D[] _hits = new Collider2D[64];
[SerializeField] private LayerMask _enemyMask;
[SerializeField] private float _baseRadius = 1f;

private void DamageInRange()
{
    float radius = _baseRadius * Stats.Size;
    int count = Physics2D.OverlapCircleNonAlloc(transform.position, radius, _hits, _enemyMask);
    DamagingContext ctx = new DamagingContext(Stats.Damage, Stats.Knockback, transform.position);
    for (int i = 0; i < count; i++)
    {
        if (_hits[i].TryGetComponent(out IDamageable d)) d.TakeDamage(ctx);
    }
    DamageTick = Stats.DamageTickInterval;
}
```

Xử lý một lượt: hết collection-modified, hết stale reference, hết duplicate-collider, và bỏ được cả
`Collider2D` trên aura lẫn `_damageables`, `OnTriggerEnter2D`, `OnTriggerExit2D`, `OnDespawn().Clear()`.

Về hiệu năng cũng có lợi: hiện tại aura phải trả giá `OnTriggerEnter/Exit` cho **mọi** enemy ở **mọi**
frame vật lý, chỉ để gây damage mỗi ~0.5s. Overlap query chỉ chạy đúng lúc cần. Buffer khai báo `static`
để không alloc.

> Nếu muốn giữ hướng list-based: phải copy sang buffer tạm (tái dùng, không `new` mỗi tick) rồi duyệt
> buffer, cộng thêm check `IsAlive` trước mỗi `TakeDamage`, cộng `HashSet` chống trùng. Nhiều việc hơn mà
> vẫn không sạch bằng.

---

## 3. 🟠 Despawn trước khi tắt `IsAlive`

**Vị trí:** `EnemyView.cs:98-102`

**Vấn đề:** `DespawnObject()` gọi `OnDespawn()` và `SetActive(false)` trong khi `IsAlive` vẫn còn `true`.
Mọi thứ chạy trong cửa sổ đó — kể cả `OnTriggerExit2D` mà `SetActive(false)` kích hoạt — đều nhìn thấy
một enemy "còn sống" nhưng đã nằm trong pool.

Phụ: `IsAlive` không được reset ở `OnSpawn()`, hiện đang phụ thuộc hoàn toàn vào việc `Init()` được gọi.
Thêm một đường spawn nào quên `Init` là có enemy zombie.

**Phương pháp:** đảo thứ tự, và đưa trạng thái pool về đúng hook của `IPoolable`:

```csharp
if (_stats.Health <= 0f)
{
    IsAlive = false;
    ObjectPoolingManager.Instance.DespawnObject(gameObject, ObjectPoolingManager.PoolType.Enemy);
}
```

---

## 4. 🟠 Knockback sai hướng và sai thời điểm

**Vị trí:** `EnemyView.cs:104-108`

**Vấn đề hướng:** knockback phải đẩy theo hướng **từ nguồn sát thương**, nhưng đang dùng
`_directionTowardPlayer`. Aura nằm ở tâm player nên trùng nhau — che mất lỗi. Dao ném bay tới từ hướng
khác thì enemy sẽ bị đẩy sai hẳn.

**Vấn đề thời điểm:** `_directionTowardPlayer` chỉ được gán trong `Tick()`. Enemy trúng đòn trước `Tick()`
đầu tiên → vector `(0,0)` → knockback bằng 0.

**Vấn đề thứ ba:** `transform.position -=` dịch chuyển tức thời, dễ nhét enemy xuyên collider/tường. Project
đã có DOTween, nên tween ngắn (~0.1s) vừa an toàn vừa có cảm giác đấm hơn.

**Phương pháp:** đưa nguồn sát thương vào context, bên nhận tự tính hướng:

```csharp
public readonly struct DamagingContext
{
    public readonly float Damage;
    public readonly float Knockback;
    public readonly Vector2 SourcePosition;   // hoặc Direction đã normalize
}
```

Bên `EnemyView`: `Vector2 dir = ((Vector2)transform.position - ctx.SourcePosition).normalized;`

---

## 5. 🟠 Enemy vừa vào aura ăn 2 hit sát nhau

**Vị trí:** `AuraProjectile.cs:71-72`

**Vấn đề:** `OnTriggerEnter2D` gây damage ngay **rồi** mới add vào list. Con nào bước vào đúng lúc
`DamageTick` sắp về 0 sẽ ăn hit thứ hai chỉ vài ms sau. Nhịp damage phụ thuộc vào thời điểm ngẫu nhiên
enemy chạm vùng.

**Phương pháp:** đi theo #2 thì vấn đề tự biến mất (không còn `OnTriggerEnter2D`). Nếu giữ hướng cũ: bỏ
damage ở Enter, để `DamageInRange()` lo toàn bộ. Muốn "chạm là đau ngay" thì phải lưu thời điểm tick riêng
cho từng target (`Dictionary<IDamageable, float>`) — đắt hơn nhiều, cân nhắc có đáng không.

---

## 6. 🟠 `new Material` + `Shader.Find` mỗi enemy

**Vị trí:** `EnemyView.cs:39-45`

Ba vấn đề cộng dồn, đây là chi phí lớn nhất trong file khi số enemy lên vài trăm:

1. `_renderer.material` (không phải `sharedMaterial`) tạo một material instance riêng cho từng enemy →
   phá SRP batching / dynamic batching, mỗi enemy một draw call.
2. `new Material(...)` mỗi enemy là leak thật — material instance không được dọn theo GameObject khi bạn
   còn giữ reference, và enemy đi qua pool nên không bao giờ bị destroy.
3. `Shader.Find` lúc runtime trả `null` nếu shader không nằm trong **Always Included Shaders** — chạy ngon
   trong Editor, `NullReferenceException` trong build.

**Phương pháp:** tốt nhất là `MaterialPropertyBlock` — không tạo instance nào, giữ nguyên batching:

```csharp
private static MaterialPropertyBlock _mpb;
private static readonly int FlashId = Shader.PropertyToID("_FlashAmount"); // cần shader hỗ trợ

_renderer.GetPropertyBlock(_mpb);
_mpb.SetFloat(FlashId, 1f);
_renderer.SetPropertyBlock(_mpb);
```

Nếu chưa muốn đụng shader: ít nhất cho `flashMaterial` thành `static` để cả class dùng chung một
instance duy nhất, và gán shader qua `[SerializeField] Shader` thay vì `Shader.Find`.

---

## 7. 🟠 `LifeTimeLeft` / `PierceLeft` là dead state

**Vị trí:** `AuraProjectile.cs:52-53`, `:17-29`

**Vấn đề:** `ApplyStats` set `LifeTimeLeft` và `PierceLeft`, nhưng `Update()` override đã bỏ phần trừ
lifetime của base, và `OnTriggerEnter2D` override cũng không trừ pierce. Hai field được ghi nhưng không ai
đọc — người đọc code sau này (kể cả bạn sau 2 tuần) sẽ tưởng aura có thời hạn.

Hệ quả thật: aura **không bao giờ** despawn. Player chết, đổi scene, weapon bị gỡ — aura vẫn nằm đó.

**Phương pháp:** chốt thiết kế trước:
- Aura vĩnh viễn → bỏ hai dòng gán đó, và cần một đường despawn tường minh do `GarlickWeapon` gọi.
- Aura có thời hạn → đừng override bỏ phần lifetime, gọi `base.Update()` hoặc tự trừ.

---

## 8. 🟡 Aura bám player trong `Update` → jitter

**Vị trí:** `AuraProjectile.cs:58-61`

**Vấn đề:** player di chuyển bằng `Rigidbody2D.linearVelocity` trong `FixedUpdate`, aura copy vị trí trong
`Update` → luôn trễ một bước và rung nhẹ khi player đổi hướng.

**Phương pháp:** `transform.SetParent(info.Origin)` lúc `Init`, rồi bỏ hẳn `Move()`. Transform con bám cứng
theo cha, không tốn gì mỗi frame. `ObjectPoolingManager.DespawnObject` đã reparent về holder nên không vỡ pool.

⚠ Lưu ý: khi làm con của player thì `localScale` bị nhân với scale của player — nếu player scale khác 1
thì kích thước aura sẽ sai.

---

## 9. 🟡 `CompareTag` mỗi va chạm thay vì lọc bằng Layer

**Vị trí:** `Projectile.cs:48`, `AuraProjectile.cs:66`, `:78`

**Vấn đề:** đang để va chạm xảy ra rồi mới lọc bằng code. Ở mật độ bullet-hell (hàng trăm đạn × hàng trăm
enemy) thì mỗi callback bị gọi đều tốn interop C++→C#, kể cả khi kết quả là `return` ngay.

**Phương pháp:** tách Layer (Player / Enemy / PlayerProjectile) và tắt các ô tương ứng trong
**Project Settings → Physics 2D → Layer Collision Matrix**. Callback sẽ không bao giờ được gọi cho cặp
không quan tâm → bỏ được cả `CompareTag` lẫn `TryGetComponent` thất bại.

---

## 10. 🟡 Coroutine flash không dừng khi despawn

**Vị trí:** `EnemyView.cs:19-35`, `:85-88`

**Vấn đề:** enemy chết giữa lúc đang flash → `SetActive(false)` giết coroutine trước khi nó kịp trả
`originalMaterial` về. Lần lấy lại từ pool, enemy đó trắng vĩnh viễn.

**Phương pháp:** dọn trong `OnDespawn()` — đây là hook `IPoolable`, chạy đúng thời điểm:

```csharp
public void OnDespawn()
{
    if (flashCoroutine != null) { StopCoroutine(flashCoroutine); flashCoroutine = null; }
    _renderer.material = originalMaterial;
}
```

---

## 11. ⚪ `AuraProjectile` kế thừa sai tầng — trả lời câu hỏi ở `AuraProjectile.cs:4`

**Câu hỏi trong code:** *"Co nen lam kieu projectile cho aura va orbit:???"* — theo cách hiện tại thì không.

**Vấn đề:** `AuraProjectile` override `Update`, `Move`, `OnTriggerEnter2D`, và **không dùng** `Direction`,
`Speed`, `Pierce`, `LifeTimeLeft`. Nó thừa kế gần như 100% thứ nó vứt đi — dấu hiệu kinh điển của base class
đặt sai tầng. Làm tiếp `OrbitProjectile` sẽ phải override lại đúng những thứ vừa override lần này.

**Phương pháp:** tách hai tầng, đẩy phần "bay theo hướng" xuống một lớp trung gian:

```
ProjectileBase (abstract)   : Stats, _isAlive, IPoolable, Init/Despawn     ← mọi loại đều cần
├── MovingProjectile        : Direction, Speed, Pierce, LifeTime, Move()   ← Knife
├── AuraProjectile          : bám owner, damage theo tick
└── OrbitProjectile         : quay quanh owner theo góc + bán kính
```

Orbit về bản chất giống Aura hơn giống Knife (cũng bám owner, cũng damage lặp, cũng không có pierce). Nếu
sau này thấy Aura và Orbit chia sẻ nhiều code thì chèn thêm một tầng `OwnerBoundProjectile` giữa chúng.

---

## 12. ⚪ `Init` và `ApplyStats` duplicate

**Vị trí:** `AuraProjectile.cs:41-56` so với `Projectile.cs:14-23`

**Vấn đề:** `ApplyStats` chép lại gần như nguyên văn thân `Projectile.Init` (direction, stats, lifetime,
pierce, scale, isAlive). Sửa công thức ở một chỗ mà quên chỗ kia là loại bug rất khó thấy.

**Phương pháp:** đảo chiều phụ thuộc — `ApplyStats` là phần dùng lại được, `Init` gọi nó rồi làm thêm phần
chỉ chạy một lần lúc spawn:

```csharp
public override void Init(ProjectileSpawnInfo info)
{
    ApplyStats(info);
    _owner = info.Origin;
    DamageTick = 0f;
}
```

---

## 13. ⚪ `_isInitialized` là cờ thừa

**Vị trí:** `GarlickWeapon.cs:7`, `:21-35`

**Vấn đề:** cờ nằm trên `GarlickWeapon` (plain C# object) nhưng mô tả trạng thái của một GameObject trong
pool — hai vòng đời khác nhau. Nếu aura bị despawn vì bất kỳ lý do gì, cờ vẫn `true` → không bao giờ spawn
lại, weapon im lặng chết.

**Phương pháp:** dùng thẳng Unity null-check, nó đã đúng cho cả object bị destroy:

```csharp
if (_aura == null)
{
    _aura = ObjectPoolingManager.Instance.SpawnObject<AuraProjectile>(...);
    _aura.Init(info);
}
else _aura.ApplyStats(info);
```

Phụ: `_cirleProjectile` sai chính tả (`circle`) và tên không còn khớp class `AuraProjectile`.

---

## 14. ⚪ `DamageTickInterval` bị buộc dính vào cooldown

**Vị trí:** `Weapon.cs:45` (`damageTickInterval: GetCooldown(playerStats)`)

**Vấn đề:** "bao lâu weapon `Fire()` một lần" và "bao lâu aura gây damage một lần" là hai khái niệm khác
nhau đang chung một giá trị. Với Garlick, `Fire()` mỗi cooldown thực chất chỉ để refresh stats chứ không
bắn gì. Designer muốn chỉnh nhịp damage của aura sẽ vô tình đổi cả tần suất refresh, và ngược lại.

Ngoài ra `CooldownRate` của player (giảm cooldown) đang gián tiếp làm aura đánh nhanh hơn — có thể đúng ý
đồ, nhưng đang là tác dụng phụ chứ không phải quyết định.

**Phương pháp:** thêm field `DamageTickInterval` riêng vào `WeaponLevelStats` để chỉnh độc lập trong SO.

---

## 15. ⚪ `IDamageable` và `DamagingContext` nằm lệch folder

**Vị trí:** `Scripts/Enemy/IDamageable.cs`, `Scripts/Weapon/DamagingContext.cs`

**Vấn đề:** hai nửa của cùng một hợp đồng nằm ở hai module không liên quan, mà `PlayerView` cũng implement
`IDamageable` — tức cả ba module đều phụ thuộc vào nó. Để trong `Enemy/` khiến người đọc tưởng nó chỉ
dành cho enemy.

**Phương pháp:** gom về `Scripts/Core/Combat/` (hoặc `Scripts/Combat/`) cùng nhau.

Đi kèm: project hiện chưa có **namespace** nào. Ở quy mô này vẫn ổn, nhưng thêm dần `Game.Combat`,
`Game.Enemy`, `Game.Weapon` + asmdef sẽ cắt đáng kể thời gian compile khi số file tăng, và tránh va tên
với package sau này.

---

## 16. ⚪ Naming lệch giữa Player và Enemy module

**Vấn đề:** hai module đang chia trách nhiệm theo hai cách khác nhau:

| Player | Enemy | Thực tế |
|--------|-------|---------|
| `Player` (POCO) | — | không có tương đương |
| `PlayerController` | `EnemyController` | nhưng `EnemyController` thực chất là **spawner + manager** |
| `PlayerView` | `EnemyView` | nhưng `EnemyView` chứa cả movement, stats, damage, VFX → là **entity**, không phải view |
| `PlayerStats` | `EnemyStats` | ✅ khớp |

Người mới vào đọc `EnemyController` sẽ đi tìm logic điều khiển enemy và không thấy gì.

**Phương pháp:** chọn một trong hai hướng — tách `EnemyView` cho khớp pattern của Player, hoặc đổi tên cho
đúng việc đang làm (`EnemySpawner` / `EnemyManager` + `Enemy`). Hướng sau ít việc hơn và thành thật hơn.

Phụ: quy ước field cũng lệch trong cùng một file. `EnemyView` có `_data`, `_stats`, `_renderer` (underscore)
đứng cạnh `originalMaterial`, `flashMaterial`, `flashCoroutine`, `flashDuration` (không underscore).
`AuraProjectile` có `_damageables` cạnh `DamageTick` — cả hai đều `protected`.

---

## 17. ⚪ Nit gộp

- `Projectile.cs:30` — `LifeTimeLeft < 0f` nên là `<= 0f`.
- `Weapon.cs:29` — `_cooldownTimer = GetCooldown(...)` vứt mất phần âm dư của frame → nhịp bắn drift chậm
  dần theo framerate. Dùng `_cooldownTimer += GetCooldown(...)`.
- `EnemyView.cs:68-78` — `if (!(_directionTowardPlayer.x > 0))` phủ định lồng, viết thẳng:
  `_renderer.flipX = _directionTowardPlayer.x <= 0f;`
- `using` thừa: `UnityEngine.Analytics` (`EnemyController.cs:3`), `Unity.VisualScripting`
  (`WeaponLevelStats.cs:2`), `UnityEngine` (`IDamageable.cs:1`, `DamagingContext.cs:1`,
  `ProjectileSpawnInfo` thì cần).
- `PlayerView.cs:2,5` — `using System.Numerics` + alias `Vector2 = UnityEngine.Vector2`. Xoá hẳn cái using
  này; giữ lại là bẫy, chỉ cần một chỗ quên alias là compile error khó hiểu hoặc dùng nhầm type.
- `Debug.Log` trong `EnemyView.TakeDamage`, `ApplyKnockback`, `OnDespawn` chạy mỗi hit. String
  interpolation là alloc thật — bọc `#if UNITY_EDITOR` hoặc xoá trước khi đo hiệu năng.
- `ObjectPoolingManager.GetParentTransform` — có `break` sau `return` (unreachable) ở 3 nhánh, và comment
  `///Refactor` của bạn vẫn còn đó.

---

## Thứ tự đề nghị

1. **#1** — bug thật, sửa 5 dòng.
2. **#2** — chuyển aura sang `OverlapCircleNonAlloc`, xoá luôn gốc rễ của #5 và phần lớn #9.
3. **#3, #4** — vòng đời và knockback, cần đụng `DamagingContext` nên làm cùng lượt.
4. **#6, #10** — material/coroutine, cắn nặng nhất khi scale số lượng enemy.
5. **#11, #12** — tách base class **trước khi** bắt đầu viết `OrbitProjectile`, làm sau sẽ tốn gấp đôi.
6. **#7, #13, #14** — dọn state và cờ thừa.
7. **#15, #16, #17** — dọn khi thuận tay.

## Ghi chú ngoài phạm vi

Vẫn còn từ bản review trước, chưa xử lý: `Weapon.cs:39` dùng `playerStats.SpeedRate` cho tốc độ đạn.
`SpeedRate` là tốc độ di chuyển của player (`PlayerView.cs:30`), còn `ProjectileSpeedRate` không ai đọc.
Gần như chắc chắn dòng đó phải là `ProjectileSpeedRate`, nhưng nó đổi feel game nên để bạn quyết.
