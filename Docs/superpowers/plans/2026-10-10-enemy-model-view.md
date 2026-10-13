# Enemy Model/View Split Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Tách `EnemyView` (đang ôm cả logic lẫn hình ảnh) thành:
- **`Enemy`:** model C# thuần, giữ stats, máu, di chuyển, knockback và đòn bắn.
- **`EnemyView`:** chỉ còn lo hiển thị.

Ngoài ra, plan tách phần spawn ra `EnemySpawner`, thêm sự kiện enemy chết, và cho shooter dừng lại ở tầm bắn.

**Architecture:** Làm giống phía player (`Player`, `PlayerController`, `PlayerView`):
- **`Enemy : ITargetable`:** grid, projectile và contact damage đều làm việc với `Enemy`, không còn đụng tới MonoBehaviour.
- **`EnemyController`:** tạo enemy, tick, huỷ, và đồng bộ sang view mỗi frame.
  - Đồng bộ một chiều: Model → Controller → View, không dùng event.
  - Khi bị trúng đòn, model chỉ bật một flag. Controller thấy flag thì gọi `view.PlayHitFlash()`.
- **Vị trí:** `Transform` vẫn là nguồn sự thật, theo quyết định của bạn. `Enemy.Position` đọc/ghi thẳng `transform.position`. Sau này muốn chuyển vị trí vào model thì chỉ phải sửa property này.
- **`EnemySpawner`:** quyết định khi nào, ở đâu, loại nào; việc tạo thật thì gọi `EnemyController.Spawn`.

**Tech Stack:** Unity 6, C# 9, `ObjectPoolingManager` hiện có, `SpatialHashGrid` hiện có.

## Global Constraints

- Thứ tự tick trong `GameBootstrap.Update` giữ nguyên: player → enemy → weapon → projectile.
- **Phạm vi của `EnemyView`:** sau Task 1, chỉ `Enemy.cs`, `EnemyController.cs` và chính `EnemyView.cs` được nhắc tới `EnemyView`.
- **Phạm vi của `Enemy`:** code trong `Projectile/` không được nhắc tới `Enemy`, chỉ được dùng `ITargetable`.
- **Không cấp phát mỗi frame trong `Tick`:** list, stack và context đều tạo sẵn làm field, không lambda. Event chỉ được invoke, không subscribe trong `Tick`.
- Comment trong code viết không dấu, giống style hiện tại.
- **Không có unit test tự động** (chưa có `.asmdef`). Mỗi task được verify bằng (1) Unity compile 0 lỗi trong Console và (2) checklist khi Play.
- Mỗi task kết thúc bằng một commit. Trước khi commit, revert mọi giá trị test đã chỉnh trong asset.
- **Line ending:** file `.cs` dùng CRLF giống phần còn lại của project.

## File Structure

| File | Trách nhiệm |
|---|---|
| `Scripts/Enemy/Enemy.cs` (mới) | Model: stats, máu, di chuyển, knockback, `RangedAttack`, flag nháy trắng. Implement `ITargetable` |
| `Scripts/Enemy/EnemyView.cs` | Chỉ hiển thị: flip sprite, nháy trắng, gizmo |
| `Scripts/Enemy/EnemyController.cs` | Spawn/despawn (pool cho view và model), separation, tick, contact damage, đòn bắn, sync view, sự kiện chết |
| `Scripts/Enemy/EnemySpawner.cs` (mới) | Rải enemy quanh player (sau này: wave) |
| `Scripts/Enemy/EnemyDeathInfo.cs` (mới) | Dữ liệu sự kiện chết: `Data` và `Position` |
| `Scripts/Enemy/EnemyData.cs` | Thêm `KnockbackDecay`, `MaxKnockback`, `StopDistance` |
| `Scripts/Enemy/EnemySpawnContext.cs` | **Xoá** (không còn ai dùng) |
| `Scripts/Map/SpatialHashGrid.cs` | `EnemyView` → `Enemy` |
| `Scripts/Combat/EnemyTargetQuery.cs` | `List<EnemyView>` → `List<Enemy>` |
| `Scripts/Core/GameBootstrap.cs` | Tạo `EnemySpawner`, đăng ký `EnemyDied` |

(Mọi đường dẫn `Scripts/...` đều nằm dưới `Assets/_Game/Scripts/`.)

---

### Task 0: Commit phần enemy-projectile đang dở

Working tree đang chứa toàn bộ code của plan `2026-10-05-enemy-projectile`: một phần đã stage, một phần chưa (`EnemyController`, `EnemyData`, `EnemyView`, `PlayerStats`, `EnemyRangedAttack*`). Commit trước để refactor mới có điểm quay lại.

- [ ] **Step 1: Xác nhận Play mode đã chạy ổn.** Shooter bắn, player mất máu, weapon vẫn giết enemy.
- [ ] **Step 2: Stage và commit.** Không add `ProjectSettings.asset` nếu thay đổi đó không cố ý.

```bash
git add Assets/_Game Assets/Scenes/GameScene.unity Docs
git status   # ProjectSettings/ProjectSettings.asset phai con o "not staged"
git commit -m "add: shared projectile for enemy, player damage model, i-frame, contact damage"
```

---

### Task 1: Tách `Enemy` model khỏi `EnemyView`

Task này phải làm trọn trong một lần: đổi kiểu trong grid thì `EnemyController`, `EnemyTargetQuery` và `EnemyView` phải đổi cùng lúc mới compile được. Hãy làm hết các step rồi mới quay lại Unity.

**Files:**
- Create: `Assets/_Game/Scripts/Enemy/Enemy.cs`
- Modify: `Assets/_Game/Scripts/Enemy/EnemyView.cs` (viết lại)
- Modify: `Assets/_Game/Scripts/Enemy/EnemyController.cs` (viết lại)
- Modify: `Assets/_Game/Scripts/Enemy/EnemyData.cs`
- Modify: `Assets/_Game/Scripts/Map/SpatialHashGrid.cs`
- Modify: `Assets/_Game/Scripts/Combat/EnemyTargetQuery.cs`
- Delete: `Assets/_Game/Scripts/Enemy/EnemySpawnContext.cs` (+ `.meta`)

**Interfaces:**
- Consumes:
  - `ITargetable`, `CollisionMath`, `IProjectileService` (đã có)
  - `EnemyRangedAttack.Init/Tick` (đã có)
  - `PlayerController.Position`, `.Radius`, `.TakeDamage` (đã có)
- Produces:
  - `class Enemy : ITargetable`, gồm:
    - property: `Id`, `Data`, `View`, `RangedAttack`, `ContactDamage`, `FacingDirection`
    - `void Init(int id, EnemyData data, EnemyView view)`
    - `void Tick(float dt, Vector2 playerPosition, Vector2 separation)`
    - `bool ConsumeHitFlash()`
    - `void Release()`
  - `EnemyView`: `SetFacing(Vector2)`, `PlayHitFlash()`, `SetDebugRadius(float)`
  - `EnemyController.Spawn(EnemyData data, Vector2 position) : Enemy`
  - `SpatialHashGrid.GetNeighbours(Enemy, List<Enemy>)`, `AddToCell(Enemy)`
  - `ISpatialGridQuery`: hai hàm query nhận `List<Enemy>`

- [ ] **Step 1: `EnemyData` thêm thông số di chuyển.** Đây là các giá trị trước kia là `SerializeField` trên prefab; mặc định giữ đúng giá trị prefab đang dùng.

Thêm sau field `Stats`, trước `[Header("Attack")]`:

```csharp
    [Header("Movement")]
    [Tooltip("Do tieu knockback, cang lon thi dung cang nhanh")]
    public float KnockbackDecay = 5f;
    [Tooltip("Van toc knockback toi da (nhan voi KnockbackDecay)")]
    public float MaxKnockback = 4f;
```

- [ ] **Step 2: Tạo `Enemy.cs`**

```csharp
using System;
using UnityEngine;

// Model cua 1 enemy: stats, mau, di chuyen, knockback, don ban. Khong ve gi.
// Vi tri doc/ghi thang tren Transform cua view (Transform la nguon su that).
public class Enemy : ITargetable
{
    private const float MaxSeparationDeltaTime = 1f / 30f; // chan luc day tach khi frame dai

    private readonly EnemyRangedAttack _rangedAttack = new EnemyRangedAttack();
    private Transform _transform;
    private Vector2 _lastPosition;      // vi tri luc Release, cho ai con giu reference cu
    private EnemyStats _stats;          // ban sao tu data, Health bi tru truc tiep
    private Vector2 _knockbackVelocity;
    private Vector2 _moveDirection;     // huong toi player (da normalize)
    private bool _hitFlashPending;

    public int Id { get; private set; }  // pha the hoa khi 2 enemy trung vi tri
    public EnemyData Data { get; private set; }
    public EnemyView View { get; private set; }
    public EnemyRangedAttack RangedAttack { get; private set; } // null = khong ban
    public float ContactDamage => _stats.Damage;
    public Vector2 FacingDirection => _moveDirection;

    // ITargetable
    public bool IsAlive { get; private set; }
    public float Radius => _stats.BodyRadius;
    public Vector2 Position
    {
        get => _transform != null ? (Vector2)_transform.position : _lastPosition;
        private set => _transform.position = value;
    }

    public void Init(int id, EnemyData data, EnemyView view)
    {
        Id = id;
        Data = data;
        View = view;
        _transform = view.transform;
        _stats = data.Stats;
        _knockbackVelocity = Vector2.zero;
        _moveDirection = Vector2.zero;
        _hitFlashPending = false;
        RangedAttack = data.RangedAttack != null ? _rangedAttack : null;
        RangedAttack?.Init(data.RangedAttack);
        IsAlive = true;
    }

    // separation: luc day tach khoi enemy khac, do EnemyController tinh
    public void Tick(float dt, Vector2 playerPosition, Vector2 separation)
    {
        if (!IsAlive) return;
        _moveDirection = (playerPosition - Position).normalized;

        float sepDt = Mathf.Min(dt, MaxSeparationDeltaTime);
        Vector2 chase = _moveDirection * _stats.Speed;
        Vector2 displacement = (chase + _knockbackVelocity) * dt + separation * sepDt;
        Position += displacement;
        _knockbackVelocity *= Mathf.Exp(-Data.KnockbackDecay * dt);
    }

    public void TakeDamage(DamagingContext ctx, Action onDead = null)
    {
        if (!IsAlive) return;
        _stats.Health -= ctx.Damage;
        _hitFlashPending = true; // controller doc va bao view nhay trang
        ApplyKnockback(ctx.Knockback);
        if (_stats.Health <= 0f)
        {
            IsAlive = false;
            onDead?.Invoke();
        }
    }

    // Tra ve true dung 1 lan sau moi lan trung don
    public bool ConsumeHitFlash()
    {
        bool pending = _hitFlashPending;
        _hitFlashPending = false;
        return pending;
    }

    // Goi khi tra ve pool: bo reference toi view/data de khong giu object da tat
    public void Release()
    {
        _lastPosition = Position;
        IsAlive = false;
        View = null;
        _transform = null;
        Data = null;
        RangedAttack = null;
    }

    private void ApplyKnockback(float knockback)
    {
        _knockbackVelocity -= _moveDirection * knockback * Data.KnockbackDecay; // day nguoc huong toi player
        _knockbackVelocity = Vector2.ClampMagnitude(_knockbackVelocity, Data.MaxKnockback * Data.KnockbackDecay);
    }
}
```

- [ ] **Step 3: Viết lại `EnemyView.cs`**

```csharp
using System.Collections;
using UnityEngine;

// Chi hien thi: flip sprite, nhay trang khi trung don. Logic nam o Enemy.
public class EnemyView : MonoBehaviour, IPoolable
{
    [SerializeField] private float flashDuration = 0.1f;

    private SpriteRenderer _renderer;
    private Material _originalMaterial;
    private Material _flashMaterial;
    private Coroutine _flashCoroutine;
    private float _debugRadius;

    private void Awake()
    {
        _renderer = GetComponent<SpriteRenderer>();
        _originalMaterial = _renderer.material;
        _flashMaterial = new Material(Shader.Find("GUI/Text Shader"));
    }

    public void SetDebugRadius(float radius) => _debugRadius = radius;

    public void SetFacing(Vector2 direction)
    {
        _renderer.flipX = !(direction.x > 0f);
    }

    public void PlayHitFlash()
    {
        if (_flashCoroutine != null) StopCoroutine(_flashCoroutine);
        _flashCoroutine = StartCoroutine(FlashRoutine());
    }

    private IEnumerator FlashRoutine()
    {
        _renderer.material = _flashMaterial;
        yield return new WaitForSeconds(flashDuration);
        _renderer.material = _originalMaterial;
        _flashCoroutine = null;
    }

    public void OnSpawn()
    {
    }

    public void OnDespawn()
    {
        // tra ve pool giua luc dang nhay -> reset ve material goc
        if (_flashCoroutine != null)
        {
            StopCoroutine(_flashCoroutine);
            _flashCoroutine = null;
        }
        _renderer.material = _originalMaterial;
    }

    private void OnDrawGizmos()
    {
        Gizmos.color = Color.red;
        Gizmos.DrawWireSphere(transform.position, _debugRadius);
    }
}
```

- [ ] **Step 4: `SpatialHashGrid` đổi sang `Enemy`**
  1. Trong file, thay mọi `EnemyView` bằng `Enemy` (interface, `_buckets`, `_candidates`, tham số các hàm).
  2. Xoá hai hàm dùng `Transform` vì không còn ai gọi:

```csharp
    private EnemyCell WorldToCell(Transform transform) => WorldToCell((Vector2)transform.position);
    public List<EnemyView> GetEnemyInCell(Transform transform) { ... }
```

  3. Trong `GetEnemyInRadius` và `GetEnemiesInBox`, dùng `enemy.Position` và `enemy.Radius`:

```csharp
            if (CollisionMath.CircleOverlapsCircle(center, radius, enemy.Position, enemy.Radius)) result.Add(enemy);
```

```csharp
            if (CollisionMath.CircleOverlapsBox(enemy.Position, enemy.Radius, center, halfSize, right)) result.Add(enemy);
```

  4. Thay `GetNeighbours` và `AddToCell`:

```csharp
    public void GetNeighbours(Enemy enemy, List<Enemy> neighbours)
    {
        neighbours.Clear();
        EnemyCell centerCell = WorldToCell(enemy.Position);
        for (int i = -1; i <= 1; i++)
        {
            for (int j = -1; j <= 1; j++)
            {
                if (_buckets.TryGetValue(new EnemyCell(centerCell.X + i, centerCell.Y + j), out var list))
                {
                    neighbours.AddRange(list);
                }
            }
        }
    }

    public void AddToCell(Enemy enemy)
    {
        EnemyCell cell = WorldToCell(enemy.Position);
        if (!_buckets.TryGetValue(cell, out var list))
        {
            list = new List<Enemy>();
            _buckets[cell] = list;
        }
        list.Add(enemy);
    }
```

- [ ] **Step 5: `EnemyTargetQuery` đổi kiểu cache**

```csharp
    private readonly List<Enemy> _cached = new List<Enemy>();
```

- [ ] **Step 6: Viết lại `EnemyController.cs`.** Constructor giữ nguyên chữ ký, để Task 1 không phải sửa `GameBootstrap`.

```csharp
using System.Collections.Generic;
using UnityEngine;

public class EnemyController
{
    private const float OverlapPushStrength = 12f; // luc day khi 2 enemy chong nhau (truoc o prefab)
    private const float OverlapMaxPush = 15f;

    private readonly PlayerController _playerController;
    private readonly SpatialHashGrid _spatialHashGrid;
    private readonly IProjectileService _projectileService;
    private readonly List<Enemy> _enemies = new List<Enemy>();
    private readonly Stack<Enemy> _modelPool = new Stack<Enemy>(); // tai su dung model, khong new moi lan spawn
    private readonly List<Enemy> _neighbours = new List<Enemy>();
    private int _nextId;

    public EnemyController(PlayerController playerController, EnemyData enemyData, EnemyData shooterData,
        SpatialHashGrid spatialHashGrid, IProjectileService projectileService, int testEnemySpawn, int testShooterSpawn)
    {
        _playerController = playerController;
        _spatialHashGrid = spatialHashGrid;
        _projectileService = projectileService;

        // tmp: Task 2 chuyen phan nay sang EnemySpawner
        for (int i = 0; i < testEnemySpawn; i++) Spawn(enemyData, RandomTestPosition());
        if (shooterData != null)
        {
            for (int i = 0; i < testShooterSpawn; i++) Spawn(shooterData, RandomTestPosition());
        }
    }

    private static Vector2 RandomTestPosition() => new Vector2(Random.Range(-10f, 10f), Random.Range(-10f, 10f));

    public Enemy Spawn(EnemyData data, Vector2 position)
    {
        EnemyView view = ObjectPoolingManager.Instance.SpawnObject<EnemyView>(data.Prefab, position, Quaternion.identity,
            ObjectPoolingManager.PoolType.Enemy);
        if (view == null) return null;

        Enemy enemy = _modelPool.Count > 0 ? _modelPool.Pop() : new Enemy();
        enemy.Init(_nextId++, data, view);
        view.SetDebugRadius(enemy.Radius);
        _enemies.Add(enemy);
        return enemy;
    }

    public void DrawGizmos()
    {
        _spatialHashGrid?.DrawGizmos();
    }

    public void Tick(float dt)
    {
        RemoveDead();

        _spatialHashGrid.ClearBuckets();
        foreach (var enemy in _enemies) _spatialHashGrid.AddToCell(enemy);

        Vector2 playerPosition = _playerController.Position;
        foreach (var enemy in _enemies)
        {
            _spatialHashGrid.GetNeighbours(enemy, _neighbours);
            enemy.Tick(dt, playerPosition, ComputeSeparation(enemy, _neighbours));

            // I-frame cua player chan viec tru mau moi frame
            if (enemy.IsAlive && CollisionMath.CircleOverlapsCircle(enemy.Position, enemy.Radius, playerPosition, _playerController.Radius))
            {
                _playerController.TakeDamage(new DamagingContext(enemy.ContactDamage, 0f));
            }

            if (enemy.IsAlive) enemy.RangedAttack?.Tick(dt, enemy, _playerController, _projectileService);

            SyncView(enemy);
        }
    }

    private void RemoveDead()
    {
        for (int i = _enemies.Count - 1; i >= 0; i--)
        {
            Enemy enemy = _enemies[i];
            if (enemy.IsAlive) continue;
            _enemies[i] = _enemies[^1];
            _enemies.RemoveAt(_enemies.Count - 1);
            Despawn(enemy);
        }
    }

    private void Despawn(Enemy enemy)
    {
        ObjectPoolingManager.Instance.DespawnObject(enemy.View.gameObject, ObjectPoolingManager.PoolType.Enemy);
        enemy.Release();
        _modelPool.Push(enemy);
    }

    // Model -> View, 1 chieu
    private static void SyncView(Enemy enemy)
    {
        enemy.View.SetFacing(enemy.FacingDirection);
        if (enemy.ConsumeHitFlash()) enemy.View.PlayHitFlash();
    }

    private static Vector2 ComputeSeparation(Enemy self, List<Enemy> neighbours)
    {
        Vector2 pushForce = Vector2.zero;
        Vector2 selfPosition = self.Position;
        foreach (var other in neighbours)
        {
            if (other == self) continue;
            Vector2 delta = selfPosition - other.Position;
            float distance = delta.magnitude;
            float overlapRadius = other.Radius + self.Radius;
            if (distance >= overlapRadius) continue;

            Vector2 pushDir;
            if (distance < 0.001f) pushDir = self.Id > other.Id ? Vector2.right : Vector2.left; // trung vi tri -> tach theo id
            else pushDir = delta / distance;
            pushForce += pushDir * ((overlapRadius - distance) * OverlapPushStrength);
        }
        return Vector2.ClampMagnitude(pushForce, OverlapMaxPush);
    }
}
```

- [ ] **Step 7: Xoá `EnemySpawnContext`**

```bash
git rm Assets/_Game/Scripts/Enemy/EnemySpawnContext.cs Assets/_Game/Scripts/Enemy/EnemySpawnContext.cs.meta
```

- [ ] **Step 8: Kiểm tra ràng buộc.** Hai lệnh dưới phải ra đúng như mong đợi:

```bash
grep -rln "EnemyView" Assets/_Game/Scripts --include=*.cs
# mong doi: chi Enemy.cs, EnemyController.cs, EnemyView.cs
grep -n "Enemy\b" Assets/_Game/Scripts/Projectile/*.cs
# mong doi: khong in gi
```

- [ ] **Step 9: Verify khi Play**
  - Zombie và shooter đuổi player, đẩy nhau ra khi chồng lên nhau (giống trước).
  - Knife, wand và garlic trúng enemy: enemy nháy trắng, bị đẩy lùi và chết sau đủ damage. Nháy trắng có thể trễ 1 frame so với trước, không nhận ra được bằng mắt.
  - Sprite enemy quay mặt theo hướng player.
  - Zombie chạm vào thì player mất máu; shooter vẫn bắn.
  - Không còn log `... despawned` mỗi khi enemy chết.
  - Chọn `SO/EnemyData/Zombie.asset`: thấy `KnockbackDecay 5`, `MaxKnockback 4`. Nếu thấy 0 thì nhập tay, rồi làm tương tự với `Shooter.asset`.

- [ ] **Step 10: Commit**

```bash
git add -A Assets/_Game/Scripts Assets/_Game/SO/EnemyData
git commit -m "refactor: split Enemy model from EnemyView"
```

---

### Task 2: Tách `EnemySpawner`

**Files:**
- Create: `Assets/_Game/Scripts/Enemy/EnemySpawner.cs`
- Modify: `Assets/_Game/Scripts/Enemy/EnemyController.cs` (constructor, xoá `RandomTestPosition`)
- Modify: `Assets/_Game/Scripts/Core/GameBootstrap.cs` (`Start`)

**Interfaces:**
- Consumes: `EnemyController.Spawn(EnemyData, Vector2)` (Task 1), `PlayerController.Position`
- Produces:
  - `EnemySpawner(EnemyController enemies, PlayerController player)`
  - `EnemySpawner.SpawnAround(EnemyData data, int count, float halfExtent)`
  - `EnemyController(PlayerController, SpatialHashGrid, IProjectileService)`

- [ ] **Step 1: Tạo `EnemySpawner.cs`**

```csharp
using UnityEngine;

// Quyet dinh KHI NAO / O DAU / LOAI NAO spawn. Tao that su thi nho EnemyController.Spawn.
// Sau nay: wave theo thoi gian, spawn ngoai camera.
public class EnemySpawner
{
    private readonly EnemyController _enemies;
    private readonly PlayerController _player;

    public EnemySpawner(EnemyController enemies, PlayerController player)
    {
        _enemies = enemies;
        _player = player;
    }

    // Rai count enemy ngau nhien trong hinh vuong canh 2*halfExtent quanh player
    public void SpawnAround(EnemyData data, int count, float halfExtent)
    {
        if (data == null) return;
        for (int i = 0; i < count; i++)
        {
            Vector2 offset = new Vector2(Random.Range(-halfExtent, halfExtent), Random.Range(-halfExtent, halfExtent));
            _enemies.Spawn(data, _player.Position + offset);
        }
    }
}
```

- [ ] **Step 2: Rút gọn constructor của `EnemyController`.** Đồng thời xoá luôn hàm `RandomTestPosition`.

```csharp
    public EnemyController(PlayerController playerController, SpatialHashGrid spatialHashGrid, IProjectileService projectileService)
    {
        _playerController = playerController;
        _spatialHashGrid = spatialHashGrid;
        _projectileService = projectileService;
    }
```

- [ ] **Step 3: `GameBootstrap`**
  - Thêm field `private EnemySpawner _enemySpawner;`.
  - Trong `Start`, thay dòng tạo `EnemyController` bằng:

```csharp
        _enemyController = new EnemyController(_playerController, _spatialHashGrid, _projectileController);
        _enemySpawner = new EnemySpawner(_enemyController, _playerController);
        _enemySpawner.SpawnAround(_data, _testEnemySpawn, 10f);
        _enemySpawner.SpawnAround(_shooterData, _testShooterSpawn, 10f);
```

- [ ] **Step 4: Verify khi Play.** Số zombie và shooter giống Task 1, rải trong khoảng ±10 quanh player, mọi thứ chạy như cũ.

- [ ] **Step 5: Commit**

```bash
git add Assets/_Game/Scripts
git commit -m "refactor: extract EnemySpawner from EnemyController"
```

---

### Task 3: Sự kiện enemy chết

**Files:**
- Create: `Assets/_Game/Scripts/Enemy/EnemyDeathInfo.cs`
- Modify: `Assets/_Game/Scripts/Enemy/EnemyController.cs` (`RemoveDead`, thêm event)
- Modify: `Assets/_Game/Scripts/Core/GameBootstrap.cs`

**Interfaces:**
- Consumes: `EnemyController.RemoveDead` (Task 1)
- Produces:
  - `readonly struct EnemyDeathInfo { EnemyData Data; Vector2 Position; }`
  - `EnemyController.EnemyDied` (`event Action<EnemyDeathInfo>`)

Event truyền **struct copy** chứ không truyền `Enemy`, vì model sẽ được trả về pool ngay sau đó. Người nghe giữ lại reference `Enemy` sẽ thấy nó "sống lại" thành một enemy khác.

- [ ] **Step 1: Tạo `EnemyDeathInfo.cs`**

```csharp
using UnityEngine;

// Snapshot luc enemy chet. Khong truyen Enemy vi model se vao pool ngay sau do.
public readonly struct EnemyDeathInfo
{
    public readonly EnemyData Data;
    public readonly Vector2 Position;

    public EnemyDeathInfo(EnemyData data, Vector2 position)
    {
        Data = data;
        Position = position;
    }
}
```

- [ ] **Step 2: `EnemyController` bắn event**
  - Thêm `using System;` ở đầu file.
  - Thêm field:

```csharp
    public event Action<EnemyDeathInfo> EnemyDied; // sau nay: roi XP gem, dem kill
```

  - Trong `RemoveDead`, ngay trước `Despawn(enemy);` (phải trước, vì `Release` xoá `Data`):

```csharp
            EnemyDied?.Invoke(new EnemyDeathInfo(enemy.Data, enemy.Position));
```

- [ ] **Step 3: `GameBootstrap` lắng nghe**
  - Thêm field `private int _killCount;`.
  - Cuối `Start`, thêm `_enemyController.EnemyDied += HandleEnemyDied;`.
  - Thêm vào class:

```csharp
    private void OnDestroy()
    {
        if (_enemyController != null) _enemyController.EnemyDied -= HandleEnemyDied;
    }

    private void HandleEnemyDied(EnemyDeathInfo info)
    {
        _killCount++;
        Debug.Log($"Kill #{_killCount}: {info.Data.DisplayName} tai {info.Position}"); // tmp, thay bang XP/UI sau
    }
```

- [ ] **Step 4: Verify khi Play.** Mỗi enemy chết in đúng **một** dòng `Kill #n`, `n` tăng dần, vị trí in ra khớp chỗ enemy biến mất. Enemy chết do aura hay knife đều được đếm.

- [ ] **Step 5: Commit**

```bash
git add Assets/_Game/Scripts
git commit -m "add: EnemyDied event with death snapshot"
```

---

### Task 4: Shooter giữ khoảng cách

**Files:**
- Modify: `Assets/_Game/Scripts/Enemy/EnemyData.cs`
- Modify: `Assets/_Game/Scripts/Enemy/Enemy.cs` (`Tick`)
- Modify (Unity Editor): `Assets/_Game/SO/EnemyData/Shooter.asset`

**Interfaces:**
- Consumes: `Enemy.Tick` (Task 1)
- Produces: `EnemyData.StopDistance` (float, 0 = lao thẳng vào)

- [ ] **Step 1: `EnemyData` thêm field** (trong header `Movement`, sau `MaxKnockback`):

```csharp
    [Tooltip("Dung lai khi cach player <= khoang nay. 0 = lao thang vao player")]
    public float StopDistance = 0f;
```

- [ ] **Step 2: `Enemy.Tick` dừng khi đủ gần.** Thay hai dòng `_moveDirection = ...` và `Vector2 chase = ...` bằng:

```csharp
        Vector2 toPlayer = playerPosition - Position;
        _moveDirection = toPlayer.normalized;

        // trong tam dung thi khong tien them, nhung van bi knockback/day tach
        float stop = Data.StopDistance;
        bool holdPosition = stop > 0f && toPlayer.sqrMagnitude <= stop * stop;
        Vector2 chase = holdPosition ? Vector2.zero : _moveDirection * _stats.Speed;
```

(Biến `sepDt` và phần tính `displacement` phía dưới giữ nguyên.)

- [ ] **Step 3: Unity.** Mở `SO/EnemyData/Shooter.asset`, đặt `StopDistance = 6`. Giá trị này phải nhỏ hơn `Range` 8 của `EnemyRangedAttack`, để shooter dừng ở chỗ còn bắn tới player. `Zombie.asset` giữ 0.

- [ ] **Step 4: Verify khi Play**
  - Shooter tiến tới cách player khoảng 6 unit thì đứng lại và bắn; player lùi ra thì shooter đi theo.
  - Zombie vẫn lao thẳng vào player.
  - Shooter vẫn bị knockback khi trúng đòn và vẫn bị đẩy tách khỏi enemy khác.

- [ ] **Step 5: Commit**

```bash
git add Assets/_Game/Scripts Assets/_Game/SO/EnemyData/Shooter.asset
git commit -m "add: StopDistance so ranged enemies hold range"
```

---

## Ngoài phạm vi (ghi lại để làm sau)

- **Position nằm trong model** thay vì `Transform`, nếu sau này cần chạy simulation không cần GameObject. Khi đó chỉ phải sửa property `Enemy.Position` và thêm `view.transform.position = enemy.Position` vào `SyncView`.
- **Reference cũ tới enemy đã chết:** `HomingProjectile._target` và `MovingProjectile._alreadyHit` giữ reference tới `Enemy`. Khi model bị pool tái dùng, reference cũ "sống lại" thành một enemy khác. Lỗi này đã có từ khi `EnemyView` được pool. Cách sửa: lưu `Id` cùng với reference, hoặc thêm một số "generation" cho mỗi lần spawn.
- **Wave spawn theo thời gian / ngoài camera** trong `EnemySpawner.Tick`.
- **Pool inject** thay cho `ObjectPoolingManager.Instance`.
- **XP gem / UI kill count** lắng nghe `EnemyDied`.
