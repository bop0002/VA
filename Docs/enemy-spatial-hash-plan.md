# Kế hoạch: Spatial Hash cho Enemy + Projectile (thay hoàn toàn PhysX2D)

Phạm vi: `Assets/_Game/Scripts/Enemy/`, `Assets/_Game/Scripts/Map/SpatialHashGrid.cs`,
`Assets/_Game/Scripts/Weapon/` (`MovingProjectile`, `HomingProjectile`, `AuraProjectile`),
prefab weapon (`Garlick`, `Knife`, `MagicWandProjectile`).

Ngày viết: 2026-09-23. Doc này thay thế bản 2026-08-17 — bản cũ giả định enemy vẫn giữ
Kinematic Rigidbody2D + Collider2D và khuyên "đo trước khi đổi kiến trúc". Bạn đã đi xa hơn
thế: xoá hẳn Rigidbody2D/Collider2D khỏi enemy, tự viết `SpatialHashGrid`, và quyết định đưa
luôn cả projectile-enemy collision vào hệ tự viết này (không còn dùng PhysX2D cho enemy dưới
bất kỳ hình thức nào). Doc này bám theo hướng đó.

Đây là **lộ trình để tự làm**, không phải code hoàn chỉnh — nêu mục tiêu, cạm bẫy, tiêu chí
nghiệm thu; phần code chỉ là khung `TODO` khi cần minh hoạ ý tưởng thuật toán.

---

## Trạng thái hiện tại (đã xong, không cần làm lại)

- `SpatialHashGrid.cs`: Dictionary<EnemyCell, List<EnemyView>>, `EnemyCell` là readonly struct có
  `IEquatable<EnemyCell>` + `GetHashCode()` riêng (đã fix bug boxing/reflection). `AddToCell`,
  `ClearBuckets`, `GetNeighbours` (quét 3×3 quanh 1 enemy, nhận buffer tái sử dụng — không alloc
  mới mỗi lần gọi), `DrawGizmos` để debug bằng mắt.
- `EnemyController.cs`: sở hữu 1 instance `SpatialHashGrid`, tách riêng pass dọn enemy chết
  (swap-remove) trước khi build grid, có buffer `_neighborCacheList` tái sử dụng.
- `EnemyView.cs`: không còn `Rigidbody2D`, di chuyển thuần bằng `transform.position +=`.
  `Tick()` đã nhận thêm tham số `neighbors`. Có `OnDrawGizmos` vẽ `BodyRadius` để kiểm tra bằng
  mắt lúc tune.
- `EnemyStats.cs`: đã có field `BodyRadius` (Zombie đang để `0.5`).
- `Zombie.prefab`: không còn `Rigidbody2D`/`CircleCollider2D` — enemy giờ là entity thuần data,
  không phụ thuộc PhysX2D nữa.

## Còn thiếu / đang là stub — chưa làm

- `EnemyView.ApplyOverlapForce(neighbors)` — thân hàm rỗng, **chưa được gọi trong `Tick()`**.
- `EnemyView.ApplyKnockback(float)` — vẫn là code cũ bị comment, chưa hoạt động.
- `MovingProjectile`, `HomingProjectile`, `AuraProjectile` — vẫn 100% dùng
  `Physics2D.OverlapCircleNonAlloc` / `OnTriggerEnter2D` / `Collider2D`, chưa đụng tới.
- `Garlick.prefab`, `Knife.prefab`, `MagicWandProjectile.prefab` — vẫn còn Rigidbody2D (Kinematic)
  + Collider2D (trigger) — chưa dọn vì script phía trên còn phụ thuộc chúng.
- **Một bug thứ tự xử lý trong `EnemyController.Update()`** — xem Giai đoạn A1, cần sửa trước
  tiên vì nó làm sai lệch mọi phép tính separation sau này.

---

## ⚠️ Giai đoạn A1 — Sửa thứ tự build grid (làm trước mọi thứ khác)

`EnemyController.cs`, vòng lặp thứ hai trong `Update()`:

```csharp
foreach (var enemy in _enemies)
{
    _neighborCacheList.Clear();
    _grid.AddToCell(enemy);                          // (1) thêm enemy này vào grid
    _grid.GetNeighbours(enemy, ref _neighborCacheList); // (2) query ngay lập tức
    enemy.Tick(Time.deltaTime, _neighborCacheList);
}
```

Vấn đề: bạn add-rồi-query **cho từng enemy trong cùng 1 lượt lặp**, thay vì add hết toàn bộ rồi
mới query. Enemy đứng đầu `foreach` sẽ query một grid gần như trống (các enemy phía sau chưa kịp
`AddToCell`); enemy cuối cùng mới thấy gần đủ toàn bộ. Kết quả: separation không nhất quán, phụ
thuộc thứ tự trong `_enemies` — enemy giống hệt nhau về vị trí nhưng ở vị trí index khác nhau
trong list sẽ nhận neighbor list khác nhau.

Việc cần làm: tách thành 2 pass riêng biệt.

```csharp
// Pass 1: build đầy đủ grid trước
foreach (var enemy in _enemies) _grid.AddToCell(enemy);

// Pass 2: mới cho Tick (bên trong mới query neighbours)
foreach (var enemy in _enemies)
{
    _neighborCacheList.Clear();
    _grid.GetNeighbours(enemy, ref _neighborCacheList);
    enemy.Tick(Time.deltaTime, _neighborCacheList);
}
```

**Nghiệm thu:** không có cách nào "nhìn thấy" bug này bằng mắt ở mật độ thấp — nó chỉ lộ ra khi
so sánh số liệu hoặc khi separation (A2) đã chạy và bạn thấy enemy ở đầu/cuối list cư xử khác
nhau bất thường ở cùng điều kiện. Sửa trước, đừng để dành debug sau.

---

## Giai đoạn A2 — Implement `ApplyOverlapForce` (separation)

Hướng đã chốt: **mỗi enemy tự tính lực đẩy của riêng nó** dựa trên `neighbors` nhận được từ
`Tick()`, cộng dồn theo độ sâu chồng lấn (không phải lực cố định, không phải 1/khoảng cách).

```csharp
private Vector2 ComputeSeparation(List<EnemyView> neighbors)
{
    Vector2 push = Vector2.zero;
    foreach (var other in neighbors)
    {
        if (other == this) continue;                 // grid trả về cả chính mình, phải loại

        Vector2 delta = (Vector2)transform.position - (Vector2)other.transform.position;
        float distance = delta.magnitude;
        float combinedRadius = _stats.BodyRadius + other.BodyRadius; // cần public getter

        if (distance >= combinedRadius) continue;     // không chồng lấn

        Vector2 pushDir = distance < 0.0001f
            ? MộtHướngCốĐịnhDựaTrênInstanceID(this, other)   // tránh chia 0 / NaN khi trùng vị trí
            : delta / distance;

        float overlapDepth = combinedRadius - distance;
        push += pushDir * overlapDepth;
    }
    return Vector2.ClampMagnitude(push, maxSeparationPush) * separationStrength;
}
```

Điểm cần tự quyết khi điền TODO:
- **`other.BodyRadius` cần expose ra ngoài** — hiện `_stats` là private trong `EnemyView`, cần
  1 public getter (`public float BodyRadius => _stats.BodyRadius;`) để enemy khác đọc được.
- **Trường hợp trùng vị trí (`distance ≈ 0`)**: dùng `GetInstanceID()` của 2 enemy để chọn 1
  hướng cố định, xác định, không đổi mỗi frame — tránh NaN và tránh enemy giật liên tục vì hướng
  ngẫu nhiên đổi mỗi lần.
- **`separationStrength` là hệ số điều chỉnh một phần, không nên để lực giải quyết 100% chồng
  lấn ngay trong 1 frame** — nếu 3+ enemy chồng nhau cùng lúc, giải hết cặp A-B trong 1 frame có
  thể tạo chồng lấn mới với C. Để hệ số <1 (thử 0.3–0.6) cho hệ hội tụ mượt qua vài frame thay vì
  giật hình.
- **`maxSeparationPush`**: chặn trần để tránh enemy bị "nổ" văng xa khi vừa spawn dồn cục hoặc
  nhiều enemy chết cùng lúc để lại 1 enemy kẹt giữa đám đông.

Sau khi có `ComputeSeparation`, gọi nó trong `Tick()` và cộng vào chuyển động:

```csharp
public void Tick(float deltaTime, List<EnemyView> neighbors)
{
    if (!IsAlive) return;
    _directionTowardPlayer = (_player.position - transform.position).normalized;
    Vector2 separation = ComputeSeparation(neighbors);
    transform.position += (Vector3)(_directionTowardPlayer * _stats.Speed + separation) * deltaTime;
    FlipSprite();
}
```

(Cộng thẳng vector separation vào vector đuổi player — không cần override/tạm dừng chuyển động,
enemy sẽ tự "lách" quanh nhau trong lúc vẫn tiến về player.)

**Nghiệm thu:** spawn 50-100 enemy dồn cục quanh 1 điểm, enemy tự giãn ra không chồng lên nhau,
không rung giật, không có enemy văng ra xa bất thường. Bật Gizmo (`OnDrawGizmos` đã vẽ sẵn
`BodyRadius`) để nhìn bằng mắt các vòng tròn có chồng lên nhau hay không.

---

## Giai đoạn A3 — Thêm hướng vào `DamagingContext` (cần cho knockback)

`DamagingContext` hiện chỉ có `Damage` và `Knockback` (độ lớn, không có hướng). Quyết định đã
bàn: **đẩy ra xa player** là đủ cho scope hiện tại (mọi vũ khí đều gắn trên player, không cần
đẩy theo hướng đạn bay tới) — nghĩa là **không bắt buộc phải sửa `DamagingContext`**, chỉ cần
enemy tự dùng `-_directionTowardPlayer` làm hướng knockback trong `ApplyKnockback`.

Nếu sau này muốn chính xác hơn (đẩy theo hướng đạn bay tới, không phải hướng player), lúc đó mới
cần mở rộng `DamagingContext` thêm 1 `Vector2` hướng/vị trí nguồn, và sửa cả 3 nơi tạo
`DamagingContext` (`MovingProjectile`, `HomingProjectile`, `AuraProjectile`). Không cần làm ngay.

---

## Giai đoạn A4 — Implement `ApplyKnockback` thật

Hướng đã chọn: **vận tốc đẩy giảm dần theo thời gian**, cộng chung vào cùng buffer với
separation thay vì dịch chuyển tức thời (`transform.position -=`).

```csharp
private Vector2 _knockbackVelocity;

private void ApplyKnockback(float knockback)
{
    _knockbackVelocity += -_directionTowardPlayer * knockback; // hướng: xem Giai đoạn A3
}
```

Trong `Tick()`, cộng `_knockbackVelocity` vào chuyển động (cùng chỗ đã cộng `separation` ở A2),
rồi giảm dần nó mỗi frame:

```csharp
transform.position += (Vector3)(_directionTowardPlayer * _stats.Speed + separation + _knockbackVelocity) * deltaTime;
_knockbackVelocity = Vector2.MoveTowards(_knockbackVelocity, Vector2.zero, knockbackDecay * deltaTime);
// hoặc: _knockbackVelocity *= Mathf.Exp(-knockbackDecay * deltaTime);  // tắt mượt hơn, không về 0 tuyệt đối
```

Cả 2 cách decay đều độc lập framerate (nhân `deltaTime`, không phải hằng số cố định như `*= 0.9f`
— cách đó phụ thuộc framerate, máy khoẻ knockback tắt nhanh hơn máy yếu). Chọn theo cảm giác:
`MoveTowards` dứt khoát/cứng, `Exp` mượt hơn/"đuối dần".

**Nghiệm thu:** đánh trúng enemy, nó bị đẩy lùi mượt rồi tự quay lại đuổi player, không giật,
không kẹt đứng yên bất thường lâu.

---

## Giai đoạn B — Mở rộng `SpatialHashGrid` cho truy vấn bán kính lớn (AOE)

`GetNeighbours` hiện chỉ quét cố định 3×3 ô quanh 1 enemy — đủ cho separation (bán kính nhỏ,
cỡ enemy) nhưng **không đủ cho Garlic/aura** khi bán kính AOE lớn hơn `_cellSize`. Cần thêm 1 hàm
mới, tổng quát hơn:

```csharp
public void GetInRadius(Vector2 center, float radius, List<EnemyView> results)
{
    results.Clear();
    EnemyCell min = WorldToCell(center - new Vector2(radius, radius));
    EnemyCell max = WorldToCell(center + new Vector2(radius, radius));

    for (int x = min.X; x <= max.X; x++)
    for (int y = min.Y; y <= max.Y; y++)
    {
        if (_buckets.TryGetValue(new EnemyCell(x, y), out var list))
            foreach (var enemy in list) results.Add(enemy); // TODO: lọc bằng khoảng cách thật ở nơi gọi (narrow-phase)
    }
}
```

Lưu ý: `WorldToCell` hiện nhận `Transform`, hàm này cần nhận thẳng `Vector2` (đã bàn ở phần
trước — aura cần query tại `player.position + offset`, không phải tại transform gốc). Cân nhắc
thêm overload `WorldToCell(Vector2 worldPos)` dùng chung cho cả `GetNeighbours` lẫn
`GetInRadius`.

**Nghiệm thu:** gọi `GetInRadius` với bán kính lớn hơn nhiều lần `_cellSize`, kết quả chứa đúng
mọi enemy trong bán kính đó (kiểm bằng cách so với brute-force tạm thời trong lúc test).

---

## Giai đoạn C — Migrate Projectile sang Spatial Hash (bỏ hẳn PhysX2D)

Thứ tự gợi ý: đơn giản → phức tạp.

### C1 — `MovingProjectile` (Knife)

Bỏ `OnTriggerEnter2D`. Sau mỗi `Move()`, query `GetInRadius(transform.position, radius, buffer)`
(radius = bán kính đạn + bán kính enemy lớn nhất, hoặc so từng enemy với đúng bán kính của nó),
lọc bằng khoảng cách thật, gọi `TakeDamage`, giảm `PierceLeft`.

⚠️ **Rủi ro tunneling**: đạn nhanh có thể "nhảy qua" enemy nếu `Speed * deltaTime` lớn hơn tổng
bán kính trong 1 frame — PhysX2D che giấu vấn đề này cho bạn từ trước, giờ tự lo. Nếu tốc độ đạn
không quá cao so với `cellSize`/bán kính enemy thì không cần xử lý gì thêm; nếu có đạn tốc độ cao,
cân nhắc check theo đoạn thẳng từ vị trí cũ→mới thay vì chỉ check tại điểm hiện tại.

### C2 — `HomingProjectile`

Thay `Physics2D.OverlapCircleNonAlloc` trong `AcquireTarget()` bằng `GetInRadius`. Bỏ
`[SerializeField] LayerMask _enemyLayer` và buffer `Collider2D[64]`. `GetDistanceTo` đổi từ nhận
`Collider2D` sang nhận `EnemyView`.

### C3 — `AuraProjectile` (Garlic)

Bỏ `CircleCollider2D` — cần tự thêm field `radius`/`offset` riêng (trước đây đọc từ
`_collider.radius`/`_collider.offset`, giờ không còn collider để đọc). Thay
`Physics2D.OverlapCircleNonAlloc` trong `DamageInRange()` bằng `GetInRadius`. Xoá
`OnTriggerEnter2D`/`OnTriggerExit2D` (đã dead code — `OnTriggerExit2D` vốn đã rỗng từ đầu).

### C4 — Dọn prefab

`Garlick.prefab`, `Knife.prefab`, `MagicWandProjectile.prefab`: bỏ `Rigidbody2D` + `Collider2D`.
Chỉ làm **sau khi** C1-C3 xong và test chạy đúng — bỏ component trước khi script hết phụ thuộc
vào chúng sẽ làm projectile mất tác dụng ngay lập tức, khó debug hơn nếu làm ngược thứ tự.

### C5 — Vấn đề kiến trúc cần quyết định: ai giữ instance `SpatialHashGrid`?

Hiện `_grid` là field private trong `EnemyController`. Một khi `MovingProjectile`/
`HomingProjectile`/`AuraProjectile` (là component trên GameObject hoàn toàn khác, do
`ObjectPoolingManager` spawn ra) cũng cần query grid này, chúng cần cách lấy **cùng 1 instance**
đó — không phải tạo grid riêng (tạo riêng thì mỗi projectile chỉ thấy được đúng enemy nào tự nó
add vào, vô nghĩa).

Vài lựa chọn (tự cân nhắc, không có đáp án đúng/sai tuyệt đối):
- **Static/singleton** — giống pattern `ObjectPoolingManager.Instance` project đã dùng sẵn. Nhất
  quán với codebase hiện tại, dễ làm nhất.
- **Truyền reference qua `ProjectileSpawnInfo`/`WeaponContext`** lúc spawn — tường minh hơn
  (dependency injection), nhưng phải sửa thêm cả `Weapon.cs`/các lớp `*Weapon` để truyền xuyên
  qua toàn bộ chuỗi spawn.

Nghiêng về singleton vì khớp convention đã có, trừ khi bạn có lý do cụ thể muốn tránh singleton
cho class này.

---

## Giai đoạn D — Dọn dẹp & kiểm thử

- [ ] Xoá `using UnityEngine.UIElements;` thừa trong `SpatialHashGrid.cs` (không dùng tới).
- [ ] Xoá `using Unity.VisualScripting.Antlr3.Runtime.Misc;` thừa trong `EnemyView.cs`.
- [ ] Cân nhắc bỏ từ khoá `ref` trên `GetNeighbours(EnemyView, ref List<EnemyView>)` — không cần
      thiết vì `List<T>` là reference type, chỉ mutate nội dung chứ không gán lại cả list (không
      phải bug, chỉ là thừa).
- [ ] Test với `testEnemySpawn` lớn (vài trăm~vài nghìn), quan sát Gizmo cả grid
      (`SpatialHashGrid.DrawGizmos`) lẫn `BodyRadius` từng enemy.
- [ ] Tune `_cellSize` (hiện `1f` trong `EnemyController.Start()`) sau khi có đủ 3 loại truy vấn
      dùng chung 1 grid (separation, projectile, aura) — quan sát mật độ enemy/cell ở khu vực
      đông nhất, không tune theo lý thuyết suông.

## Checklist nghiệm thu toàn bộ

- [ ] Enemy không chồng lên nhau ở mật độ cao, không rung giật, không văng vô cực.
- [ ] Knockback rõ ràng, tắt mượt, enemy tự quay lại đuổi player sau đó.
- [ ] Đạn thường (Knife), homing (MagicWand), aura (Garlic) đều gây damage đúng, đúng pierce/tick
      interval, không phụ thuộc `Physics2D`/`Collider2D`/`LayerMask` nào nữa.
- [ ] Không còn `Rigidbody2D`/`Collider2D` nào trên enemy hoặc projectile.
- [ ] Không có GC spike mới trong Profiler do rebuild grid mỗi frame (buffer tái sử dụng, không
      `new List<>()` trong vòng lặp nóng).
