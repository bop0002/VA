# ProjectileController Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Chuyển toàn bộ projectile sang cho `ProjectileController` tick. Projectile tìm enemy qua `SpatialHashGrid` thay vì Physics2D, để cả 3 vũ khí gây damage lại và Garlic đi theo player.

**Architecture:** `GameBootstrap` tạo `ProjectileController` (nhận pool + grid) và gọi `Tick` **sau** `EnemyController.Tick`, tức là sau khi grid đã được build lại. Weapon không gọi pool trực tiếp nữa mà spawn qua `ctx.Projectiles.Spawn<T>(...)`. Projectile không có `Update()` riêng, không tự despawn: khi hết đời thì chỉ gọi `Kill()`, còn controller mới là nơi trả nó về pool.

**Tech Stack:** Unity 6, C#, `ObjectPoolingManager` hiện có, `SpatialHashGrid` hiện có (`GetEnemyInRadius`, `GetEnemiesInBox`).

## Global Constraints

- Thứ tự tick trong `GameBootstrap.Update`: player → enemy → weapon → projectile. Không đổi thứ tự này.
- Chỉ `ProjectileController` được gọi `DespawnObject` cho projectile. Projectile chỉ được `Kill()`.
- Không dùng `Physics2D`, `OnTriggerEnter2D` hay `_enemyLayer` trong thư mục `Weapon/` sau khi xong plan.
- Không cấp phát bộ nhớ mỗi frame trong `Tick`: dùng list/dictionary tạo sẵn (field hoặc `static readonly`).
- Comment trong code viết không dấu, giống style hiện tại của project.
- **Không có unit test tự động:** project chưa có `.asmdef`, nên test EditMode không reference được `Assembly-CSharp`. Mỗi task được verify bằng (1) Unity compile 0 lỗi và (2) checklist khi Play. Muốn có test tự động thì cần một plan riêng để thêm asmdef cho `Scripts/`.
- Kiểm tra compile từ terminal (khi Unity Editor đang mở và đã focus lại để recompile):
  `grep -n "error CS" "$LOCALAPPDATA/Unity/Editor/Editor.log" | tail -5`
  Kết quả mong đợi: không có dòng nào mới hơn lần sửa cuối. Cách chắc nhất vẫn là xem Console trong Unity: 0 lỗi đỏ.

## File Structure

| File | Trách nhiệm |
|---|---|
| `Assets/_Game/Scripts/Weapon/ProjectileTickContext.cs` (mới) | Struct dữ liệu mỗi frame truyền cho projectile: vị trí player, grid, thời gian |
| `Assets/_Game/Scripts/Weapon/ProjectileController.cs` | Spawn qua pool, giữ danh sách, tick, despawn projectile đã chết |
| `Assets/_Game/Scripts/Weapon/Projectile.cs` | Base: `IsAlive`, `Kill()`, `Tick(...)`, scale theo `Stats.Size` (sửa bug nhân dồn) |
| `Assets/_Game/Scripts/Weapon/MovingProjectile.cs` | Bay thẳng, lifetime, pierce, trúng enemy bằng `GetEnemiesInBox` |
| `Assets/_Game/Scripts/Weapon/HomingProjectile.cs` | Tìm enemy gần nhất bằng `GetEnemyInRadius`, bẻ hướng |
| `Assets/_Game/Scripts/Weapon/AuraProjectile.cs` | Đi theo player, gây damage theo nhịp bằng `GetEnemyInRadius` |
| `Assets/_Game/Scripts/Weapon/WeaponContext.cs` | Thêm field `Projectiles` |
| `Assets/_Game/Scripts/Weapon/WeaponController.cs` | Nhận `ProjectileController`, truyền vào context |
| `Assets/_Game/Scripts/Weapon/KnifeWeapon.cs`, `MagicWandWeapon.cs`, `GarlickWeapon.cs` | Spawn qua `ctx.Projectiles` |
| `Assets/_Game/Scripts/Core/GameBootstrap.cs` | Tạo `ProjectileController`, tick sau enemy |

---

### Task 0: Chốt phần refactor hiện tại (commit trước khi bắt đầu)

Mục đích: có một điểm an toàn để quay lại nếu Task 1 làm hỏng game.

**Files:**
- Modify: `Assets/_Game/Scripts/Core/GameBootstrap.cs:2` và `:42-45`
- Inspector: GameObject `GameBoostrap` trong `GameScene`

- [ ] **Step 1: Xoá `using UnityEditor;`** ở dòng 2 của `GameBootstrap.cs` (dòng này làm lỗi khi build game).

- [ ] **Step 2: Sửa `OnDrawGizmos`** để không NullReference khi chưa Play (Unity gọi hàm này cả ở Edit mode, lúc đó `_enemyController` còn null):

```csharp
    private void OnDrawGizmos()
    {
        _enemyController?.DrawGizmos();
    }
```

- [ ] **Step 3: Gán vũ khí trong Inspector.** Chọn GameObject `GameBoostrap` trong scene, ở `Starting Weapons` thêm 3 phần tử: `KnifeData`, `MagicWandData`, `GarlickData` (thư mục `Assets/_Game/SO/WeaponData/`). Lưu scene (Ctrl+S).

- [ ] **Step 4: Verify.** Unity Console không có lỗi đỏ. Nhấn Play:
  - 10 enemy spawn và đuổi theo player.
  - Knife bay ra theo hướng di chuyển.
  - Chưa gây damage là **đúng** ở bước này, vì enemy không có collider.

- [ ] **Step 5: Commit** (không add thư mục `Docs/` nếu bạn chưa muốn):

```bash
git add Assets/_Game/Scripts Assets/Scenes/GameScene.unity Assets/_Game/Prefabs/Player.prefab
git commit -m "refactor: add GameBootstrap and plain C# controllers"
```

---

### Task 1: Khung ProjectileController + Garlic đi theo player và gây damage

**Files:**
- Create: `Assets/_Game/Scripts/Weapon/ProjectileTickContext.cs`
- Modify (thay toàn bộ nội dung): `ProjectileController.cs`, `Projectile.cs`, `MovingProjectile.cs`, `HomingProjectile.cs`, `AuraProjectile.cs`, `WeaponContext.cs`, `WeaponController.cs`, `KnifeWeapon.cs`, `MagicWandWeapon.cs`, `GarlickWeapon.cs`, `Core/GameBootstrap.cs`

**Interfaces:**
- Produces:
  - `readonly struct ProjectileTickContext { Vector3 PlayerPosition; SpatialHashGrid Grid; float Time; }`
  - `ProjectileController(ObjectPoolingManager pool, SpatialHashGrid grid)`
  - `T ProjectileController.Spawn<T>(GameObject prefab, Vector3 position, Quaternion rotation, ProjectileSpawnInfo info) where T : Projectile` (trả `null` nếu pool lỗi)
  - `void ProjectileController.Tick(float deltaTime, Vector3 playerPosition)`
  - `Projectile`: `bool IsAlive { get; }`, `virtual void Tick(float deltaTime, in ProjectileTickContext ctx)`, `protected void Kill()`, `protected virtual void Awake()`
  - `MovingProjectile`: `protected virtual void Move(float deltaTime, in ProjectileTickContext ctx)`
  - `WeaponContext.Projectiles` (kiểu `ProjectileController`)

Lưu ý: tất cả projectile chuyển sang `Tick` **trong cùng task này**, vì base class đổi. Nếu tách ra, project sẽ không compile giữa chừng.

- [ ] **Step 1: Tạo `ProjectileTickContext.cs`**

```csharp
using UnityEngine;

public readonly struct ProjectileTickContext
{
    public readonly Vector3 PlayerPosition;
    public readonly SpatialHashGrid Grid;
    public readonly float Time;

    public ProjectileTickContext(Vector3 playerPosition, SpatialHashGrid grid, float time)
    {
        PlayerPosition = playerPosition;
        Grid = grid;
        Time = time;
    }
}
```

- [ ] **Step 2: Viết `ProjectileController.cs`**

```csharp
using System.Collections.Generic;
using UnityEngine;

public class ProjectileController
{
    private readonly ObjectPoolingManager _pool;
    private readonly SpatialHashGrid _grid;
    private readonly List<Projectile> _projectiles = new List<Projectile>();

    public ProjectileController(ObjectPoolingManager pool, SpatialHashGrid grid)
    {
        _pool = pool;
        _grid = grid;
    }

    public T Spawn<T>(GameObject prefab, Vector3 position, Quaternion rotation, ProjectileSpawnInfo info) where T : Projectile
    {
        T projectile = _pool.SpawnObject<T>(prefab, position, rotation, ObjectPoolingManager.PoolType.WeaponProjectile);
        if (projectile == null) return null;

        projectile.Init(info);
        _projectiles.Add(projectile);
        return projectile;
    }

    public void Tick(float deltaTime, Vector3 playerPosition)
    {
        ProjectileTickContext ctx = new ProjectileTickContext(playerPosition, _grid, Time.time);

        for (int i = 0; i < _projectiles.Count; i++)
        {
            _projectiles[i].Tick(deltaTime, in ctx);
        }

        // Duyet nguoc + swap-remove: xoa O(1), khong lam lech index
        for (int i = _projectiles.Count - 1; i >= 0; i--)
        {
            Projectile projectile = _projectiles[i];
            if (projectile.IsAlive) continue;

            _projectiles[i] = _projectiles[^1];
            _projectiles.RemoveAt(_projectiles.Count - 1);
            _pool.DespawnObject(projectile.gameObject, ObjectPoolingManager.PoolType.WeaponProjectile);
        }
    }
}
```

- [ ] **Step 3: Viết `Projectile.cs`**

Thay đổi so với bản cũ: thêm `IsAlive`/`Kill()`/`Tick`. Sửa bug `LocalScale` bị nhân dồn mỗi lần lấy từ pool và không bao giờ được gán vào transform. `Awake` thành `protected virtual` để class con không vô tình che mất.

```csharp
using UnityEngine;

public abstract class Projectile : MonoBehaviour, IPoolable
{
    protected Vector2 Direction;
    protected ProjectileStats Stats;
    private Vector3 _baseScale;

    public bool IsAlive { get; private set; }

    protected virtual void Awake()
    {
        _baseScale = transform.localScale;
    }

    public virtual void Init(ProjectileSpawnInfo info)
    {
        Direction = info.Direction.sqrMagnitude > 0.0001f ? info.Direction.normalized : Vector2.right;
        Stats = info.Stats;
        transform.localScale = _baseScale * Stats.Size;
        IsAlive = true;
    }

    // Goi boi ProjectileController moi frame. Khong tu despawn, chi Kill().
    public virtual void Tick(float deltaTime, in ProjectileTickContext ctx)
    {
    }

    protected void Kill()
    {
        IsAlive = false;
    }

    public virtual void OnSpawn()
    {
    }

    public virtual void OnDespawn()
    {
        IsAlive = false;
    }
}
```

- [ ] **Step 4: Viết `MovingProjectile.cs`** (bỏ `Update`, `OnTriggerEnter2D`, `Despawn()`; phần trúng enemy làm ở Task 2)

```csharp
using UnityEngine;

public class MovingProjectile : Projectile
{
    private float _lifeTimeLeft;
    protected int PierceLeft;

    public override void Init(ProjectileSpawnInfo info)
    {
        base.Init(info);
        _lifeTimeLeft = Stats.Duration;
        PierceLeft = Mathf.Max(1, Stats.Pierce);
    }

    public override void Tick(float deltaTime, in ProjectileTickContext ctx)
    {
        if (!IsAlive) return;

        _lifeTimeLeft -= deltaTime;
        if (_lifeTimeLeft <= 0f)
        {
            Kill();
            return;
        }

        Move(deltaTime, in ctx);
    }

    protected virtual void Move(float deltaTime, in ProjectileTickContext ctx)
    {
        transform.position += (Vector3)(Direction * (Stats.Speed * deltaTime));
    }
}
```

- [ ] **Step 5: Viết `HomingProjectile.cs`** (chỉ đổi chữ ký cho compile; tìm mục tiêu bằng grid làm ở Task 3)

```csharp
using UnityEngine;

public class HomingProjectile : MovingProjectile
{
    private Transform _target;
    private static readonly Collider2D[] _hits = new Collider2D[64];
    private Vector2 _center;
    [SerializeField] private float radius = 4f;
    [SerializeField] private float turnRate = 270f;
    [SerializeField] private LayerMask _enemyLayer;

    public override void Init(ProjectileSpawnInfo info)
    {
        base.Init(info);
        AcquireTarget();
    }

    private void AcquireTarget()
    {
        float minDistance = float.MaxValue;
        _target = null;
        _center = transform.position;
        int hitCount = Physics2D.OverlapCircleNonAlloc(_center, radius, _hits, _enemyLayer);
        for (int i = 0; i < hitCount; i++)
        {
            float currentDistance = Vector3.Distance(transform.position, _hits[i].transform.position);
            if (_target == null || currentDistance <= minDistance)
            {
                _target = _hits[i].transform;
                minDistance = currentDistance;
            }
        }
        if (_target != null) Direction = (_target.position - transform.position).normalized;
    }

    private void OnDrawGizmosSelected()
    {
        Gizmos.color = Color.red;
        Gizmos.DrawWireSphere(_center, radius);
    }

    protected override void Move(float deltaTime, in ProjectileTickContext ctx)
    {
        if (_target != null)
        {
            Vector2 desired = ((Vector2)_target.position - (Vector2)transform.position).normalized;
            Direction = (Vector2)Vector3.RotateTowards(Direction, desired, turnRate * Mathf.Deg2Rad * deltaTime, 0f);
        }
        base.Move(deltaTime, in ctx);
    }

    public override void OnDespawn()
    {
        base.OnDespawn();
        _target = null;
    }
}
```

- [ ] **Step 6: Viết `AuraProjectile.cs`** (bản cuối: đi theo player và dùng grid)

Đây chính là lời giải cho câu hỏi "truyền Vector3 thì Garlic theo player kiểu gì": vị trí player được đưa vào **mỗi frame** qua `ctx.PlayerPosition`, chứ không chỉ chụp lại một lần lúc spawn.

```csharp
using System.Collections.Generic;
using UnityEngine;

public class AuraProjectile : Projectile
{
    private static readonly List<EnemyView> s_hits = new List<EnemyView>(128);

    [SerializeField] private float _baseRadius = 5f;

    private readonly Dictionary<EnemyView, float> _nextHitTime = new Dictionary<EnemyView, float>();
    private readonly List<EnemyView> _toRemove = new List<EnemyView>();
    private float _radius;

    public override void Init(ProjectileSpawnInfo info)
    {
        base.Init(info);
        _nextHitTime.Clear();
    }

    public override void Tick(float deltaTime, in ProjectileTickContext ctx)
    {
        if (!IsAlive) return;

        transform.position = ctx.PlayerPosition;
        _radius = _baseRadius * Mathf.Max(transform.lossyScale.x, transform.lossyScale.y);

        ctx.Grid.GetEnemyInRadius(transform.position, _radius, s_hits);
        for (int i = 0; i < s_hits.Count; i++)
        {
            TryDamage(s_hits[i], ctx.Time);
        }

        PruneHitTimes(ctx.Time);
    }

    private void TryDamage(EnemyView enemy, float time)
    {
        if (_nextHitTime.TryGetValue(enemy, out float nextHit) && time < nextHit) return;

        _nextHitTime[enemy] = time + Stats.DamageTickInterval;
        enemy.TakeDamage(new DamagingContext(Stats.Damage, Stats.Knockback), null);
    }

    // Xoa enemy da chet hoac het cooldown de dictionary khong phinh to
    private void PruneHitTimes(float time)
    {
        foreach (KeyValuePair<EnemyView, float> pair in _nextHitTime)
        {
            if (!pair.Key.IsAlive || pair.Value <= time) _toRemove.Add(pair.Key);
        }

        for (int i = 0; i < _toRemove.Count; i++)
        {
            _nextHitTime.Remove(_toRemove[i]);
        }
        _toRemove.Clear();
    }

    private void OnDrawGizmosSelected()
    {
        Gizmos.color = Color.red;
        Gizmos.DrawWireSphere(transform.position, _radius);
    }
}
```

- [ ] **Step 7: Viết `WeaponContext.cs`**

```csharp
using UnityEngine;

public readonly struct WeaponContext
{
    public readonly Vector3 PlayerPosition;
    public readonly Vector2 Direction;
    public readonly PlayerStats PlayerStats;
    public readonly ProjectileController Projectiles;

    public WeaponContext(Vector3 playerPosition, Vector2 direction, PlayerStats stats, ProjectileController projectiles)
    {
        PlayerPosition = playerPosition;
        Direction = direction;
        PlayerStats = stats;
        Projectiles = projectiles;
    }
}
```

- [ ] **Step 8: Viết `WeaponController.cs`** (thêm tham số `ProjectileController`, bỏ cờ `_initialized` vì constructor đã luôn Init)

```csharp
using System.Collections.Generic;
using UnityEngine;

public class WeaponController
{
    private readonly PlayerController _playerController;
    private readonly ProjectileController _projectileController;
    private readonly List<WeaponData> _startingWeapons;
    private readonly List<Weapon> _weapons = new List<Weapon>();

    private Player _player;

    public IReadOnlyList<Weapon> Weapons => _weapons;

    public WeaponController(PlayerController playerController, List<WeaponData> startingWeapons, ProjectileController projectileController)
    {
        _playerController = playerController;
        _startingWeapons = startingWeapons;
        _projectileController = projectileController;
        Init(_playerController.GetPlayer());
    }

    public void Init(Player owner)
    {
        _player = owner;
        _weapons.Clear();
        foreach (WeaponData data in _startingWeapons)
        {
            if (data != null) Acquire(data);
        }
    }

    private void Acquire(WeaponData data)
    {
        Weapon existing = _weapons.Find(w => w.Id == data.Id);
        if (existing != null)
        {
            existing.TryLevelUp();
            return;
        }
        _weapons.Add(data.CreateRunTime());
    }

    public void Tick(float deltaTime)
    {
        WeaponContext ctx = new WeaponContext(_playerController.PlayerPosition, _playerController.LastMoveDirection, _player.Stats, _projectileController);
        for (int i = 0; i < _weapons.Count; i++)
        {
            _weapons[i].Tick(deltaTime, ctx);
        }
    }
}
```

- [ ] **Step 9: Viết `KnifeWeapon.cs`**

```csharp
using UnityEngine;

public class KnifeWeapon : Weapon
{
    private KnifeData _knifeData;

    public KnifeWeapon(KnifeData data) : base(data)
    {
        _knifeData = data;
    }

    protected override void Fire(WeaponContext ctx)
    {
        ProjectileStats stats = BuildProjectileStats(ctx.PlayerStats);
        int count = GetProjectileCount(ctx.PlayerStats);

        ProjectileSpawnInfo info = new ProjectileSpawnInfo(ctx.Direction, ctx.PlayerPosition, stats);
        Quaternion rot = RotationFromDirection(ctx.Direction);

        for (int i = 0; i < count; i++)
        {
            Vector3 offset = (Vector3)(ctx.Direction.normalized * (i * _knifeData.SpawnSpacing));
            Vector3 spawnPos = ctx.PlayerPosition - offset;

            if (ctx.Projectiles.Spawn<MovingProjectile>(Data.Prefab, spawnPos, rot, info) == null) return;
        }
    }

    private Quaternion RotationFromDirection(Vector2 direction)
    {
        float angle = Mathf.Atan2(direction.y, direction.x) * Mathf.Rad2Deg;
        return Quaternion.Euler(0f, 0f, angle - 45); // sprite knife ve cheo 45 do
    }
}
```

- [ ] **Step 10: Viết `MagicWandWeapon.cs`**

```csharp
using UnityEngine;

public class MagicWandWeapon : Weapon
{
    private MagicWandWeaponData _magicWandData;

    public MagicWandWeapon(MagicWandWeaponData data) : base(data)
    {
        _magicWandData = data;
    }

    protected override void Fire(WeaponContext ctx)
    {
        ProjectileStats stats = BuildProjectileStats(ctx.PlayerStats);
        int count = GetProjectileCount(ctx.PlayerStats);

        ProjectileSpawnInfo info = new ProjectileSpawnInfo(ctx.Direction, ctx.PlayerPosition, stats);
        Quaternion rot = RotationFromDirection(ctx.Direction);

        for (int i = 0; i < count; i++)
        {
            if (ctx.Projectiles.Spawn<HomingProjectile>(Data.Prefab, ctx.PlayerPosition, rot, info) == null) return;
        }
    }

    private Quaternion RotationFromDirection(Vector2 direction)
    {
        float angle = Mathf.Atan2(direction.y, direction.x) * Mathf.Rad2Deg;
        return Quaternion.Euler(0f, 0f, angle - 45);
    }
}
```

- [ ] **Step 11: Viết `GarlickWeapon.cs`** (bỏ cờ `_isInitialized` bị check hai lần; chỉ cần kiểm tra đã có aura hay chưa)

```csharp
using UnityEngine;

public class GarlickWeapon : Weapon
{
    private AuraProjectile _auraProjectile;

    public GarlickWeapon(GarlickData data) : base(data)
    {
    }

    protected override void Fire(WeaponContext ctx)
    {
        if (_auraProjectile != null) return;

        ProjectileStats stats = BuildProjectileStats(ctx.PlayerStats);
        ProjectileSpawnInfo info = new ProjectileSpawnInfo(ctx.Direction, ctx.PlayerPosition, stats);
        _auraProjectile = ctx.Projectiles.Spawn<AuraProjectile>(Data.Prefab, ctx.PlayerPosition, Quaternion.identity, info);
    }
}
```

- [ ] **Step 12: Viết `GameBootstrap.cs`**

```csharp
using System.Collections.Generic;
using UnityEngine;

public class GameBootstrap : MonoBehaviour
{
    [SerializeField] private PlayerView _playerView;
    [SerializeField] private InputReader _inputReader;

    //Temp final before gameflow
    [SerializeField] private PlayerStats _playerStats;
    [SerializeField] private List<WeaponData> startingWeapons;
    [SerializeField] private EnemyData _data;
    [SerializeField] private int _testEnemySpawn;

    [SerializeField] private MapController _mapController;
    [SerializeField] private ObjectPoolingManager _objectPoolingManager;

    private EnemyController _enemyController;
    private PlayerController _playerController;
    private WeaponController _weaponController;
    private ProjectileController _projectileController;

    private SpatialHashGrid _spatialHashGrid;

    private void Start() //Havent fixing poolingmanager
    {
        _spatialHashGrid = new SpatialHashGrid(1f);
        _playerController = new PlayerController(_playerView, _playerStats);
        _enemyController = new EnemyController(_playerView, _data, _spatialHashGrid, _testEnemySpawn);
        _projectileController = new ProjectileController(_objectPoolingManager, _spatialHashGrid);
        _weaponController = new WeaponController(_playerController, startingWeapons, _projectileController);
    }

    private void Update()
    {
        float deltaTime = Time.deltaTime;
        _playerController.Tick(deltaTime);
        _enemyController.Tick(deltaTime);      // build lai grid
        _weaponController.Tick(deltaTime);     // spawn projectile
        _projectileController.Tick(deltaTime, _playerController.PlayerPosition); // query grid
    }

    private void OnDrawGizmos()
    {
        _enemyController?.DrawGizmos();
    }
}
```

- [ ] **Step 13: Verify compile.** Quay lại Unity, đợi compile xong. Console: 0 lỗi đỏ. Nếu có lỗi `does not contain a definition for 'Despawn'` thì còn chỗ nào đó gọi `MovingProjectile.Despawn()` cũ; tìm bằng lệnh sau và bỏ lời gọi đó:

```bash
grep -rn "\.Despawn()\|ObjectPoolingManager.Instance" Assets/_Game/Scripts/Weapon
```

Kết quả mong đợi: không còn dòng nào.

- [ ] **Step 14: Verify khi Play**
  - Vòng Garlic **đi theo player** khi di chuyển.
  - Enemy đứng trong vòng Garlic **nhấp nháy trắng và bị đẩy lùi** khoảng mỗi giây một lần.
  - Knife bay ra rồi biến mất sau khoảng 2 giây (chưa gây damage, sẽ làm ở Task 2).
  - Trong Hierarchy, `ObjectPool/WeaponProjectile`: knife bị tắt (inactive) khi hết đời, và được dùng lại chứ không tạo mới liên tục.
  - Knife to bằng prefab, không phình to dần sau nhiều lần bắn (đây là bug scale cũ đã được sửa).
  - Muốn thấy enemy chết: tạm đặt `Health` của `SO/EnemyData/Zombie.asset` về 30. **Nhớ trả lại 1000 trước khi commit**, vì chỉnh ScriptableObject trong lúc Play vẫn được lưu lại.

- [ ] **Step 15: Commit**

```bash
git status --short    # dam bao Zombie.asset khong nam trong danh sach thay doi
git add Assets/_Game/Scripts
git commit -m "feat: add ProjectileController, aura follows player and hits via spatial grid"
```

---

### Task 2: Knife trúng enemy qua grid (hitbox xoay theo hướng bay)

**Files:**
- Modify: `Assets/_Game/Scripts/Weapon/MovingProjectile.cs` (thay toàn bộ)
- Modify: `Assets/_Game/Scripts/Weapon/HomingProjectile.cs` (chỉ đổi hàm gizmo)
- Inspector: prefab `Assets/_Game/Prefabs/Weapon/Knife.prefab`

**Interfaces:**
- Consumes: `SpatialHashGrid.GetEnemiesInBox(Vector2 center, Vector2 halfSize, Vector2 right, List<EnemyView> result)` (đã có sẵn; tự `Clear()` `result`; `right` phải là vector đơn vị).
- Produces: `protected virtual void OnDrawGizmosSelected()` trong `MovingProjectile`.

Điểm khác biệt quan trọng so với `OnTriggerEnter2D`: trigger chỉ báo **một lần** khi mới chạm, còn grid query trả về enemy đang chồng lên **mỗi frame**. Vì vậy cần `_alreadyHit` để một enemy không bị trừ pierce nhiều lần.

- [ ] **Step 1: Viết `MovingProjectile.cs`**

```csharp
using System.Collections.Generic;
using UnityEngine;

public class MovingProjectile : Projectile
{
    private static readonly List<EnemyView> s_hits = new List<EnemyView>(64);

    // Nua kich thuoc hitbox theo don vi local, truc x = huong bay. Chinh trong Inspector (xem gizmo vang).
    [SerializeField] private Vector2 _hitHalfSize = new Vector2(0.5f, 0.5f);

    private readonly HashSet<EnemyView> _alreadyHit = new HashSet<EnemyView>();
    private float _lifeTimeLeft;
    protected int PierceLeft;

    public override void Init(ProjectileSpawnInfo info)
    {
        base.Init(info);
        _lifeTimeLeft = Stats.Duration;
        PierceLeft = Mathf.Max(1, Stats.Pierce);
        _alreadyHit.Clear();
    }

    public override void Tick(float deltaTime, in ProjectileTickContext ctx)
    {
        if (!IsAlive) return;

        _lifeTimeLeft -= deltaTime;
        if (_lifeTimeLeft <= 0f)
        {
            Kill();
            return;
        }

        Move(deltaTime, in ctx);
        HitEnemies(ctx.Grid);
    }

    protected virtual void Move(float deltaTime, in ProjectileTickContext ctx)
    {
        transform.position += (Vector3)(Direction * (Stats.Speed * deltaTime));
    }

    private void HitEnemies(SpatialHashGrid grid)
    {
        Vector2 halfSize = _hitHalfSize * transform.lossyScale.x;
        grid.GetEnemiesInBox(transform.position, halfSize, Direction, s_hits);

        for (int i = 0; i < s_hits.Count; i++)
        {
            EnemyView enemy = s_hits[i];
            if (!_alreadyHit.Add(enemy)) continue; // da trung enemy nay roi

            enemy.TakeDamage(new DamagingContext(Stats.Damage, Stats.Knockback), null);
            PierceLeft--;
            if (PierceLeft <= 0)
            {
                Kill();
                return;
            }
        }
    }

    public override void OnDespawn()
    {
        base.OnDespawn();
        _alreadyHit.Clear();
    }

    protected virtual void OnDrawGizmosSelected()
    {
        Vector2 halfSize = _hitHalfSize * transform.lossyScale.x;
        Vector2 direction = Application.isPlaying ? Direction : Vector2.right;

        Gizmos.color = Color.yellow;
        Gizmos.matrix = Matrix4x4.TRS(transform.position, Quaternion.FromToRotation(Vector3.right, direction), Vector3.one);
        Gizmos.DrawWireCube(Vector3.zero, halfSize * 2f);
        Gizmos.matrix = Matrix4x4.identity;
    }
}
```

- [ ] **Step 2: Sửa gizmo trong `HomingProjectile.cs`.** Base giờ có `protected virtual OnDrawGizmosSelected`, nên hàm `private` cùng tên ở class con sẽ che mất nó (Unity báo warning CS0114). Thay hàm cũ:

```csharp
    private void OnDrawGizmosSelected()
    {
        Gizmos.color = Color.red;
        Gizmos.DrawWireSphere(_center, radius);
    }
```

bằng:

```csharp
    protected override void OnDrawGizmosSelected()
    {
        base.OnDrawGizmosSelected();
        Gizmos.color = Color.red;
        Gizmos.DrawWireSphere(_center, radius);
    }
```

- [ ] **Step 3: Verify compile.** Console: 0 lỗi, không có warning CS0114.

- [ ] **Step 4: Chỉnh hitbox Knife.** Mở `Knife.prefab`, chọn root. Gizmo vàng hiện ở Scene view, trục x của hộp là hướng bay. Chỉnh `Hit Half Size` cho vừa lưỡi dao; điểm bắt đầu gợi ý là `(0.4, 0.1)`. Lưu prefab.

- [ ] **Step 5: Verify khi Play**
  - Knife trúng enemy: enemy nhấp nháy và bị đẩy lùi, knife biến mất ngay (`Pierce` level 1 = 1).
  - Knife **không** xuyên qua mà gây damage liên tục trên cùng một enemy.
  - Pause game rồi chọn một knife đang bay trong Hierarchy: hộp vàng xoay đúng theo hướng bay.
  - Nếu knife bay xuyên qua enemy mà không trúng: tăng `x` của `Hit Half Size`. Knife level 2 có speed 20, tức bay khoảng 0.33 đơn vị mỗi frame ở 60 FPS, nên hộp phải dài hơn khoảng đó.

- [ ] **Step 6: Commit**

```bash
git add Assets/_Game/Scripts/Weapon Assets/_Game/Prefabs/Weapon/Knife.prefab
git commit -m "feat: moving projectile hits enemies via oriented box query"
```

---

### Task 3: Magic Wand tìm mục tiêu bằng grid + dọn Physics2D

**Files:**
- Modify: `Assets/_Game/Scripts/Weapon/HomingProjectile.cs` (thay toàn bộ)
- Modify: `Assets/_Game/Scripts/Weapon/Projectile.cs` (`Tick` thành `abstract`)
- Inspector: prefab `Assets/_Game/Prefabs/Weapon/MagicWandProjectile.prefab`

**Interfaces:**
- Consumes: `SpatialHashGrid.GetEnemyInRadius(Vector2 center, float radius, List<EnemyView> result)` (tự `Clear()` `result`, đã lọc `IsAlive`); `MovingProjectile.Move(float, in ProjectileTickContext)`; `MovingProjectile.OnDrawGizmosSelected()`.

Thay đổi hành vi: bản cũ chỉ tìm mục tiêu **một lần** lúc spawn. Bản mới tìm lại khi chưa có mục tiêu hoặc mục tiêu đã chết. Viên đầu tiên vẫn ngắm thẳng vào mục tiêu ngay frame đầu (`_hasAimed`), giống bản cũ.

- [ ] **Step 1: Viết `HomingProjectile.cs`**

`FormerlySerializedAs` giữ lại giá trị đã lưu trong prefab khi đổi tên field `radius` và `turnRate`.

```csharp
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Serialization;

public class HomingProjectile : MovingProjectile
{
    private static readonly List<EnemyView> s_candidates = new List<EnemyView>(64);

    [FormerlySerializedAs("radius")] [SerializeField] private float _searchRadius = 4f;
    [FormerlySerializedAs("turnRate")] [SerializeField] private float _turnRate = 270f;

    private EnemyView _target;
    private bool _hasAimed;

    public override void Init(ProjectileSpawnInfo info)
    {
        base.Init(info);
        _target = null;
        _hasAimed = false;
    }

    protected override void Move(float deltaTime, in ProjectileTickContext ctx)
    {
        if (_target == null || !_target.IsAlive)
        {
            _target = FindClosestEnemy(ctx.Grid);
        }

        if (_target != null)
        {
            Vector2 toTarget = (Vector2)_target.transform.position - (Vector2)transform.position;
            if (toTarget.sqrMagnitude > 0.000001f)
            {
                Vector2 desired = toTarget.normalized;
                Direction = _hasAimed
                    ? (Vector2)Vector3.RotateTowards(Direction, desired, _turnRate * Mathf.Deg2Rad * deltaTime, 0f)
                    : desired;
            }
        }

        _hasAimed = true;
        base.Move(deltaTime, in ctx);
    }

    private EnemyView FindClosestEnemy(SpatialHashGrid grid)
    {
        Vector2 position = transform.position;
        grid.GetEnemyInRadius(position, _searchRadius, s_candidates);

        EnemyView closest = null;
        float minSqrDistance = float.MaxValue;
        for (int i = 0; i < s_candidates.Count; i++)
        {
            float sqrDistance = ((Vector2)s_candidates[i].transform.position - position).sqrMagnitude;
            if (sqrDistance < minSqrDistance)
            {
                minSqrDistance = sqrDistance;
                closest = s_candidates[i];
            }
        }
        return closest;
    }

    public override void OnDespawn()
    {
        base.OnDespawn();
        _target = null;
    }

    protected override void OnDrawGizmosSelected()
    {
        base.OnDrawGizmosSelected();
        Gizmos.color = Color.red;
        Gizmos.DrawWireSphere(transform.position, _searchRadius);
    }
}
```

- [ ] **Step 2: Đổi `Tick` trong `Projectile.cs` thành `abstract`.** Lúc này cả 3 loại projectile đều đã override, nên sau này thêm loại mới mà quên `Tick` sẽ bị báo lỗi ngay lúc compile. Thay:

```csharp
    // Goi boi ProjectileController moi frame. Khong tu despawn, chi Kill().
    public virtual void Tick(float deltaTime, in ProjectileTickContext ctx)
    {
    }
```

bằng:

```csharp
    // Goi boi ProjectileController moi frame. Khong tu despawn, chi Kill().
    public abstract void Tick(float deltaTime, in ProjectileTickContext ctx);
```

- [ ] **Step 3: Verify compile + không còn physics trong `Weapon/`**

```bash
grep -rn "Physics2D\|OnTriggerEnter2D\|_enemyLayer\|ObjectPoolingManager.Instance" Assets/_Game/Scripts/Weapon
```

Kết quả mong đợi: không có dòng nào. Console Unity: 0 lỗi.

- [ ] **Step 4: Chỉnh hitbox Wand.** Mở `MagicWandProjectile.prefab`: `Search Radius` = 4 và `Turn Rate` = 270 phải còn nguyên (nhờ `FormerlySerializedAs`). Chỉnh `Hit Half Size` theo gizmo vàng cho vừa sprite. Prefab có scale 0.3, nên `(0.5, 0.5)` local tương ứng hộp khoảng 0.3×0.3 ngoài thế giới. Lưu prefab.

- [ ] **Step 5: Verify khi Play**
  - Đạn wand bẻ cong về phía enemy gần nhất trong bán kính 4 và gây damage khi trúng.
  - Không có enemy trong tầm: đạn bay thẳng theo hướng player, hết 2 giây thì biến mất.
  - Enemy mục tiêu chết giữa chừng (tạm hạ `Health` để thử, nhớ trả lại): đạn chuyển sang enemy gần nhất khác thay vì bay theo xác.
  - Chạy liên tục khoảng 1 phút: Knife, Wand và Garlic cùng hoạt động, Console không có lỗi hay exception.

- [ ] **Step 6: Commit**

```bash
git status --short    # Zombie.asset khong duoc nam trong danh sach
git add Assets/_Game/Scripts/Weapon Assets/_Game/Prefabs/Weapon/MagicWandProjectile.prefab
git commit -m "feat: homing projectile targets via spatial grid, remove physics from projectiles"
```

---

## Ngoài phạm vi plan này (ghi lại để làm sau)

- `Weapon.BuildProjectileStats` (`Weapon.cs:39`) nhân tốc độ đạn với `SpeedRate` thay vì `ProjectileSpeedRate`. `SpeedRate` hiện là 2, nên đạn đang bay nhanh gấp đôi. Sửa riêng một dòng, sau khi đã test xong cảm giác bắn.
- `EnemyView.TakeDamage` vẫn tự despawn qua `ObjectPoolingManager.Instance`, và `EnemyController` vẫn truyền `Transform` của player. Việc này thuộc Mốc 2 (gom vòng đời enemy về `EnemyController`).
- Grid vẫn gắn cứng với `EnemyView`. Làm generic `<T>` sau khi có thêm loại object thứ hai cần query (pickup, prop).
