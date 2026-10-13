# Enemy Projectile & Player Damage Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Cho hệ thống projectile dùng chung cho cả hai phe. Enemy bắn được đạn gây damage cho player, enemy chạm vào player cũng gây damage, player có i-frame, và máu player nằm trong model chứ không còn ở `PlayerView`.

**Architecture:** Thêm một lớp trừu tượng "mục tiêu":
- `ITargetable` (có `IsAlive`, `Position`, `Radius` và `TakeDamage`) được implement bởi `EnemyView` và `PlayerController`.
- `ITargetQuery` có hai bản cài đặt:
  - `EnemyTargetQuery` bọc `SpatialHashGrid`.
  - `PlayerTargetQuery` kiểm tra va chạm trực tiếp với player duy nhất, không cần grid.

Mỗi projectile mang `Team` (phe của **người bắn**) và `Owner`, rồi hỏi `context.TargetsFor(Team)` để lấy phe đối diện. Enemy bắn qua `EnemyRangedAttack`, dữ liệu lấy từ ScriptableObject riêng (không dính `PlayerStats` hay level). Nhịp bắn loạt được tách khỏi `Weapon` thành `Volley` để hai phía dùng chung.

**Tech Stack:** Unity 6, C#, `ObjectPoolingManager` hiện có, `SpatialHashGrid` hiện có.

## Global Constraints

- Thứ tự tick trong `GameBootstrap.Update` giữ nguyên: player → enemy → weapon → projectile.
- Chỉ `ProjectileController` được gọi `DespawnObject` cho projectile. Projectile chỉ được `Kill()`.
- Code trong `Projectile/` **không được** nhắc tới `EnemyView` hay `PlayerController` sau khi xong Task 3. Chỉ được dùng `ITargetable` và `ITargetQuery`.
- Không cấp phát bộ nhớ mỗi frame trong `Tick`: không lambda, không `new List` trong `Tick`; list và dictionary tạo sẵn làm field.
- Comment trong code viết không dấu, giống style hiện tại của project.
- **Không có unit test tự động** (project chưa có `.asmdef`). Mỗi task được verify bằng (1) Unity compile 0 lỗi trong Console và (2) checklist khi Play.
- Mỗi task kết thúc bằng một commit. Trước khi commit, revert mọi giá trị test đã chỉnh trong ScriptableObject hoặc prefab (trừ asset mới tạo có chủ đích).

## File Structure

| File | Trách nhiệm |
|---|---|
| `Scripts/Combat/Team.cs` (mới) | `enum Team { Player, Enemy }`: phe của người bắn |
| `Scripts/Combat/ITargetable.cs` (mới) | Thứ có thể bị đánh trúng: `IsAlive`, `Position`, `Radius`, kế thừa `IDamageable` |
| `Scripts/Combat/CollisionMath.cs` (mới) | Hàm tĩnh: hình tròn với hình tròn, hình tròn với hộp xoay |
| `Scripts/Combat/ITargetQuery.cs` (mới) | Interface truy vấn mục tiêu theo hình tròn hoặc hộp |
| `Scripts/Combat/EnemyTargetQuery.cs` (mới) | `ITargetQuery` bọc `ISpatialGridQuery` |
| `Scripts/Combat/PlayerTargetQuery.cs` (mới) | `ITargetQuery` cho player duy nhất |
| `Scripts/Combat/Volley.cs` (mới) | Đếm nhịp bắn loạt N viên cách nhau `interval` |
| `Scripts/Enemy/EnemyRangedAttackData.cs` (mới) | SO cấu hình đòn bắn của enemy |
| `Scripts/Enemy/EnemyRangedAttack.cs` (mới) | Runtime cho đòn bắn: cooldown, tầm, volley, spawn đạn `Team.Enemy` |
| `Scripts/Player/Player.cs` | Model: máu, armor, `ApplyDamage` |
| `Scripts/Player/PlayerController.cs` | Implement `ITargetable`, i-frame, gọi feedback trên view |
| `Scripts/Player/PlayerView.cs` | Bỏ `IDamageable`; thêm `PlayHitFeedback`, `PlayDeath` |
| `Scripts/Player/PlayerStats.cs` | Thêm `BodyRadius`, `HitInvulnerability` |
| `Scripts/Enemy/EnemyView.cs` | Implement `ITargetable`, `ContactDamage`, giữ `EnemyRangedAttack` |
| `Scripts/Enemy/EnemyData.cs` | Thêm field `RangedAttack` |
| `Scripts/Enemy/EnemyController.cs` | Contact damage, tick ranged attack, spawn test shooter |
| `Scripts/Map/SpatialHashGrid.cs` | Dùng `CollisionMath` thay cho phép toán viết tay |
| `Scripts/Projectile/*.cs` | Đổi `EnemyView` thành `ITargetable`; thêm `Team` và `Owner`; Aura bám theo `Owner` |
| `Scripts/Weapon/Weapon.cs` | Dùng `Volley` |
| `Scripts/Weapon/WeaponContext.cs`, `WeaponController.cs`, 3 weapon | Truyền `Owner`, spawn với `Team.Player` |
| `Scripts/Core/GameBootstrap.cs` | Wiring query, test shooter |

(Mọi đường dẫn `Scripts/...` đều nằm dưới `Assets/_Game/Scripts/`.)

---

### Task 1: Combat primitives + EnemyView là ITargetable

**Files:**
- Create: `Assets/_Game/Scripts/Combat/Team.cs`
- Create: `Assets/_Game/Scripts/Combat/ITargetable.cs`
- Create: `Assets/_Game/Scripts/Combat/CollisionMath.cs`
- Modify: `Assets/_Game/Scripts/Enemy/EnemyView.cs`
- Modify: `Assets/_Game/Scripts/Map/SpatialHashGrid.cs` (`GetEnemyInRadius`, `GetEnemiesInBox`)

**Interfaces:**
- Produces:
  - `enum Team { Player, Enemy }`
  - `interface ITargetable : IDamageable { bool IsAlive {get;} Vector2 Position {get;} float Radius {get;} }`
  - `static class CollisionMath`, với `CircleOverlapsCircle(Vector2 a, float ra, Vector2 b, float rb)` và `CircleOverlapsBox(Vector2 circle, float radius, Vector2 boxCenter, Vector2 halfSize, Vector2 right)`
  - `EnemyView.ContactDamage` (float)

- [ ] **Step 1: Tạo `Team.cs`**

```csharp
// Phe cua NGUOI BAN. Projectile Team.Player danh enemy, Team.Enemy danh player.
public enum Team
{
    Player,
    Enemy
}
```

- [ ] **Step 2: Tạo `ITargetable.cs`**

```csharp
using UnityEngine;

// Bat cu thu gi projectile co the ban trung: enemy, player, sau nay la vat the pha duoc trong map
public interface ITargetable : IDamageable
{
    bool IsAlive { get; }
    Vector2 Position { get; }
    float Radius { get; }
}
```

- [ ] **Step 3: Tạo `CollisionMath.cs`.** Phép toán được chuyển nguyên từ `SpatialHashGrid.GetEnemiesInBox` sang.

```csharp
using UnityEngine;

public static class CollisionMath
{
    public static bool CircleOverlapsCircle(Vector2 a, float radiusA, Vector2 b, float radiusB)
    {
        float r = radiusA + radiusB;
        return (a - b).sqrMagnitude <= r * r;
    }

    // Box xoay: halfSize.x doc theo right, halfSize.y doc theo up. right phai normalize.
    public static bool CircleOverlapsBox(Vector2 circle, float radius, Vector2 boxCenter, Vector2 halfSize, Vector2 right)
    {
        Vector2 up = new Vector2(-right.y, right.x);
        Vector2 d = circle - boxCenter;
        Vector2 local = new Vector2(Vector2.Dot(d, right), Vector2.Dot(d, up)); // toa do tam tron trong he truc cua box
        Vector2 closest = new Vector2(
            Mathf.Clamp(local.x, -halfSize.x, halfSize.x),
            Mathf.Clamp(local.y, -halfSize.y, halfSize.y)); // diem tren box gan tam tron nhat
        return (local - closest).sqrMagnitude <= radius * radius;
    }
}
```

- [ ] **Step 4: Cho `SpatialHashGrid` dùng `CollisionMath`.** Trong `GetEnemyInRadius`, thay hai dòng tính `r` bằng:

```csharp
            if (CollisionMath.CircleOverlapsCircle(center, radius, enemy.transform.position, enemy.BodyRadius)) result.Add(enemy);
```

Trong `GetEnemiesInBox`, thay vòng `foreach` bằng đoạn dưới. Giữ nguyên `up`, `extent` và `CollectEnemyInBound` phía trên.

```csharp
        foreach (var enemy in _candidates)
        {
            if (!enemy.IsAlive) continue;
            if (CollisionMath.CircleOverlapsBox(enemy.transform.position, enemy.BodyRadius, center, halfSize, right)) result.Add(enemy);
        }
```

- [ ] **Step 5: `EnemyView` implement `ITargetable`.** Đổi khai báo class và thêm property cạnh `BodyRadius`:

```csharp
public class EnemyView : MonoBehaviour, IPoolable, ITargetable
```

```csharp
    public float BodyRadius => _stats.BodyRadius;
    public Vector2 Position => transform.position;
    public float Radius => _stats.BodyRadius;
    public float ContactDamage => _stats.Damage;
```

Sửa chữ ký `TakeDamage` cho khớp default của interface: `public void TakeDamage(DamagingContext ctx, Action onDead = null)`.

- [ ] **Step 6: Verify.** Unity compile 0 lỗi. Bấm Play: knife, wand và garlic vẫn giết enemy như trước, vì hit test chỉ đổi chỗ chứ không đổi công thức.

- [ ] **Step 7: Commit**

```bash
git add Assets/_Game/Scripts/Combat Assets/_Game/Scripts/Enemy/EnemyView.cs Assets/_Game/Scripts/Map/SpatialHashGrid.cs
git commit -m "add: combat primitives (Team, ITargetable, CollisionMath)"
```

(Nhớ add luôn các file `.meta` mà Unity sinh ra trong `Combat/`. Lệnh `git add` thư mục ở trên đã bao gồm chúng.)

---

### Task 2: Máu player vào model, i-frame, contact damage của enemy

**Files:**
- Modify: `Assets/_Game/Scripts/Player/Player.cs`
- Modify: `Assets/_Game/Scripts/Player/PlayerStats.cs`
- Modify: `Assets/_Game/Scripts/Player/PlayerController.cs`
- Modify: `Assets/_Game/Scripts/Player/PlayerView.cs`
- Modify: `Assets/_Game/Scripts/Enemy/EnemyController.cs` (`Tick`)
- Modify: `Assets/_Game/Scripts/Weapon/WeaponController.cs` (`Tick`)

**Interfaces:**
- Consumes: `ITargetable`, `CollisionMath.CircleOverlapsCircle`, `EnemyView.Position`, `EnemyView.Radius`, `EnemyView.ContactDamage` (Task 1)
- Produces:
  - `PlayerController : ITargetable`: `Position` (Vector2), `Radius`, `IsAlive`, `TakeDamage(DamagingContext, Action = null)`
  - `Player.ApplyDamage(float) : float`
  - `PlayerView.PlayHitFeedback()`, `PlayerView.PlayDeath()`

- [ ] **Step 1: `PlayerStats` thêm 2 field** (cuối class):

```csharp
    public float BodyRadius = 0.4f;          // ban kinh hit cua player
    public float HitInvulnerability = 0.5f;  // giay bat tu sau moi lan trung don
```

- [ ] **Step 2: Viết lại `Player.cs`**

```csharp
using UnityEngine;

public class Player
{
    public PlayerStats Stats { get; private set; }
    public float MaxHealth { get; private set; }
    public float CurrentHealth { get; private set; }
    public bool IsAlive => CurrentHealth > 0f;

    public Player(PlayerStats stats)
    {
        Stats = stats;
        MaxHealth = stats.Health;
        CurrentHealth = MaxHealth;
    }

    // Tru mau sau armor (tru phang nhu VS). Tra ve luong mau that su mat.
    public float ApplyDamage(float damage)
    {
        if (!IsAlive) return 0f;
        float taken = Mathf.Max(0f, damage - Stats.Armor);
        CurrentHealth = Mathf.Max(0f, CurrentHealth - taken);
        return taken;
    }
}
```

- [ ] **Step 3: Viết lại `PlayerController.cs`.** Constructor cũ quên gán `_playerStats`, bản dưới đã gán.

```csharp
using System;
using UnityEngine;

public class PlayerController : ITargetable
{
    private PlayerView _playerView;
    private PlayerStats _playerStats;
    private Player _player;
    private float _invulnerableTimer;

    public Vector3 PlayerPosition { get; private set; }
    public Vector3 LastMoveDirection { get; private set; }

    // ITargetable
    public Vector2 Position => PlayerPosition;
    public float Radius => _playerStats.BodyRadius;
    public bool IsAlive => _player.IsAlive;

    public PlayerController(PlayerView playerView, PlayerStats playerStats)
    {
        _playerStats = playerStats;
        _player = new Player(playerStats);
        _playerView = playerView;
        playerView.InitStat(_player);
    }

    public void Tick(float dt)
    {
        PlayerPosition = _playerView.Position;
        LastMoveDirection = _playerView.LastMoveDirection;
        if (_invulnerableTimer > 0f) _invulnerableTimer -= dt;
    }

    public void TakeDamage(DamagingContext ctx, Action onDead = null)
    {
        if (!IsAlive || _invulnerableTimer > 0f) return; // dang i-frame thi bo qua moi don
        float taken = _player.ApplyDamage(ctx.Damage);
        _invulnerableTimer = _playerStats.HitInvulnerability;
        _playerView.PlayHitFeedback();
        Debug.Log($"Player -{taken} hp, con {_player.CurrentHealth}"); // tmp, xoa khi co UI mau

        if (!IsAlive)
        {
            _playerView.PlayDeath();
            onDead?.Invoke();
        }
    }

    public Player GetPlayer() => _player;
}
```

- [ ] **Step 4: Sửa `PlayerView.cs`**
  - Đổi khai báo thành `public class PlayerView : MonoBehaviour` (bỏ `IDamageable`).
  - Xoá property `IsAlive`, dòng `IsAlive = true;` trong `InitStat`, và cả method `TakeDamage`.
  - Thêm `using System.Collections;`.
  - Thêm các field và method sau:

```csharp
    [SerializeField] private float _hitFlashDuration = 0.1f;
    private SpriteRenderer _renderer;
    private Coroutine _hitFlash;
```

Trong `Awake`, thêm `_renderer = GetComponent<SpriteRenderer>();`. Sau đó thêm vào class:

```csharp
    public void PlayHitFeedback()
    {
        if (_hitFlash != null) StopCoroutine(_hitFlash);
        _hitFlash = StartCoroutine(HitFlashRoutine());
    }

    private IEnumerator HitFlashRoutine()
    {
        _renderer.color = Color.red;
        yield return new WaitForSeconds(_hitFlashDuration);
        _renderer.color = Color.white;
        _hitFlash = null;
    }

    public void PlayDeath()
    {
        _inputReader.OnMovePerformed -= HandleMove; // chet thi het nhan input
        MoveDirection = Vector2.zero;
        currentVelocity = Vector2.zero;
        Debug.Log("Player is dead");
    }
```

- [ ] **Step 5: Contact damage trong `EnemyController.Tick`.** Thay vòng `foreach` cuối cùng bằng:

```csharp
        foreach (var enemy in _enemies)
        {
            _neighborCacheList.Clear();
            _spatialHashGrid.GetNeighbours(enemy, ref _neighborCacheList);
            enemy.Tick(_deltaTime, _neighborCacheList, _playerController.PlayerPosition);

            // Cham player thi gay damage. I-frame cua player chan viec tru mau moi frame.
            if (enemy.IsAlive && CollisionMath.CircleOverlapsCircle(enemy.Position, enemy.Radius, _playerController.Position, _playerController.Radius))
            {
                _playerController.TakeDamage(new DamagingContext(enemy.ContactDamage, 0f));
            }
        }
```

Đồng thời xoá dòng `using TMPro;` thừa ở đầu file.

- [ ] **Step 6: Player chết thì ngừng bắn.** Trong `WeaponController.Tick`, đổi guard đầu hàm thành:

```csharp
        if (!_initialized || !_playerController.IsAlive)
        {
            return;
        }
```

- [ ] **Step 7: Verify khi Play**
  - Inspector của `SO/PlayerStats.asset` hiện `BodyRadius 0.4` và `HitInvulnerability 0.5`. Nếu thấy 0 thì nhập tay.
  - Đứng yên cho zombie chạm vào: player nháy đỏ. Console in `Player -9 hp ...` (damage 10 trừ armor 1), **tối đa khoảng 2 lần/giây** dù bị nhiều zombie vây.
  - Weapon vẫn bắn và giết enemy bình thường.
  - Muốn test chết: tạm đặt `Health` = 30 trong `PlayerStats.asset`. Khi chết, player đứng yên, weapon ngừng bắn, Console in `Player is dead`. **Sau đó revert về 1000.**

- [ ] **Step 8: Commit**

```bash
git add Assets/_Game/Scripts/Player Assets/_Game/Scripts/Enemy/EnemyController.cs Assets/_Game/Scripts/Weapon/WeaponController.cs Assets/_Game/SO/PlayerStats.asset
git commit -m "refactor: player health in model, i-frame, enemy contact damage"
```

---

### Task 3: Target query + projectile theo Team/Owner

Task lớn nhưng không chia nhỏ được: đổi kiểu trong `ProjectileTickContext` thì mọi projectile và weapon phải đổi cùng lúc mới compile. Hãy làm hết các step rồi mới quay lại Unity.

**Files:**
- Create: `Assets/_Game/Scripts/Combat/ITargetQuery.cs`
- Create: `Assets/_Game/Scripts/Combat/EnemyTargetQuery.cs`
- Create: `Assets/_Game/Scripts/Combat/PlayerTargetQuery.cs`
- Modify: `Assets/_Game/Scripts/Projectile/ProjectileTickContext.cs`
- Modify: `Assets/_Game/Scripts/Projectile/ProjectileSpawnInfo.cs`
- Modify: `Assets/_Game/Scripts/Projectile/ProjectileController.cs`
- Modify: `Assets/_Game/Scripts/Projectile/Projectile.cs`
- Modify: `Assets/_Game/Scripts/Projectile/MovingProjectile.cs`
- Modify: `Assets/_Game/Scripts/Projectile/HomingProjectile.cs`
- Modify: `Assets/_Game/Scripts/Projectile/AuraProjectile.cs` (viết lại)
- Modify: `Assets/_Game/Scripts/Weapon/WeaponContext.cs`
- Modify: `Assets/_Game/Scripts/Weapon/WeaponController.cs`
- Modify: `Assets/_Game/Scripts/Weapon/KnifeWeapon.cs`, `MagicWandWeapon.cs`, `GarlickWeapon.cs`
- Modify: `Assets/_Game/Scripts/Core/GameBootstrap.cs`

**Interfaces:**
- Consumes: `Team`, `ITargetable`, `CollisionMath` (Task 1); `PlayerController : ITargetable` (Task 2)
- Produces:
  - `interface ITargetQuery { void QueryCircle(Vector2 center, float radius, List<ITargetable> result); void QueryBox(Vector2 center, Vector2 halfSize, Vector2 right, List<ITargetable> result); }`
  - `ProjectileTickContext.TargetsFor(Team) : ITargetQuery`
  - `ProjectileSpawnInfo(Vector2 direction, ProjectileStats stats, Team team, ITargetable owner)`
  - `ProjectileController(ITargetQuery enemyTargets, ITargetQuery playerTargets)` và `ProjectileController.Tick(float dt)`
  - `WeaponContext.Owner` (ITargetable)

- [ ] **Step 1: Tạo `ITargetQuery.cs`**

```csharp
using System.Collections.Generic;
using UnityEngine;

// Hoi "ai dang nam trong vung nay". Ket qua luon Clear truoc khi ghi.
public interface ITargetQuery
{
    void QueryCircle(Vector2 center, float radius, List<ITargetable> result);
    void QueryBox(Vector2 center, Vector2 halfSize, Vector2 right, List<ITargetable> result);
}
```

- [ ] **Step 2: Tạo `EnemyTargetQuery.cs`**

```csharp
using System.Collections.Generic;
using UnityEngine;

// Enemy dong -> dung spatial grid
public class EnemyTargetQuery : ITargetQuery
{
    private readonly ISpatialGridQuery _grid;
    private readonly List<EnemyView> _scratch = new List<EnemyView>();

    public EnemyTargetQuery(ISpatialGridQuery grid)
    {
        _grid = grid;
    }

    public void QueryCircle(Vector2 center, float radius, List<ITargetable> result)
    {
        _grid.GetEnemyInRadius(center, radius, _scratch);
        Copy(result);
    }

    public void QueryBox(Vector2 center, Vector2 halfSize, Vector2 right, List<ITargetable> result)
    {
        _grid.GetEnemiesInBox(center, halfSize, right, _scratch);
        Copy(result);
    }

    private void Copy(List<ITargetable> result)
    {
        result.Clear();
        foreach (var enemy in _scratch) result.Add(enemy);
        _scratch.Clear();
    }
}
```

- [ ] **Step 3: Tạo `PlayerTargetQuery.cs`**

```csharp
using System.Collections.Generic;
using UnityEngine;

// Chi co 1 player -> khong can grid, check truc tiep
public class PlayerTargetQuery : ITargetQuery
{
    private readonly ITargetable _player;

    public PlayerTargetQuery(ITargetable player)
    {
        _player = player;
    }

    public void QueryCircle(Vector2 center, float radius, List<ITargetable> result)
    {
        result.Clear();
        if (!_player.IsAlive) return;
        if (CollisionMath.CircleOverlapsCircle(center, radius, _player.Position, _player.Radius)) result.Add(_player);
    }

    public void QueryBox(Vector2 center, Vector2 halfSize, Vector2 right, List<ITargetable> result)
    {
        result.Clear();
        if (!_player.IsAlive) return;
        if (CollisionMath.CircleOverlapsBox(_player.Position, _player.Radius, center, halfSize, right)) result.Add(_player);
    }
}
```

- [ ] **Step 4: Viết lại `ProjectileTickContext.cs`.** Bỏ `Position`, vì Aura giờ bám theo `Owner`.

```csharp
public readonly struct ProjectileTickContext
{
    public readonly ITargetQuery EnemyTargets;
    public readonly ITargetQuery PlayerTargets;

    public ProjectileTickContext(ITargetQuery enemyTargets, ITargetQuery playerTargets)
    {
        EnemyTargets = enemyTargets;
        PlayerTargets = playerTargets;
    }

    // team = phe nguoi ban -> tra ve query cua phe DOI DIEN
    public ITargetQuery TargetsFor(Team team) => team == Team.Player ? EnemyTargets : PlayerTargets;
}
```

- [ ] **Step 5: Viết lại `ProjectileSpawnInfo.cs`.** Bỏ `PlayerPosition` (không ai đọc).

```csharp
using UnityEngine;

public struct ProjectileSpawnInfo
{
    public Vector2 Direction;
    public ProjectileStats Stats;
    public Team Team;           // phe nguoi ban
    public ITargetable Owner;   // nguoi ban, Aura bam theo. Co the null voi dan khong can owner

    public ProjectileSpawnInfo(Vector2 direction, ProjectileStats stats, Team team, ITargetable owner)
    {
        Direction = direction;
        Stats = stats;
        Team = team;
        Owner = owner;
    }
}
```

- [ ] **Step 6: Sửa `Projectile.cs`**
  - Thêm 2 field: `protected Team Team;` và `protected ITargetable Owner;`.
  - Trong `Init`, sau `Stats = info.Stats;` thêm `Team = info.Team;` và `Owner = info.Owner;`.
  - Trong `OnDespawn`, thêm `Owner = null;` để không giữ reference của enemy đã chết trong pool.
  - Đổi `Tick` thành abstract: `public abstract void Tick(float dt, ProjectileTickContext context);`

- [ ] **Step 7: Sửa `ProjectileController.cs`.** Constructor và `Tick` mới; `Spawn` và `IProjectileService` giữ nguyên.

```csharp
    private readonly List<Projectile> _projectiles = new List<Projectile>();
    private readonly ProjectileTickContext _tickContext;

    public ProjectileController(ITargetQuery enemyTargets, ITargetQuery playerTargets)
    {
        _tickContext = new ProjectileTickContext(enemyTargets, playerTargets);
    }

    public void Tick(float dt)
    {
        foreach (Projectile projectile in _projectiles)
        {
            projectile.Tick(dt, _tickContext);
        }
        // ... vong swap-remove despawn giu nguyen
    }
```

Xoá field `_spatialHashGrid` và cả constructor cũ.

- [ ] **Step 8: Sửa `MovingProjectile.cs`**
  - Đổi hai list sang `ITargetable`:

```csharp
    private readonly List<ITargetable> _hits = new List<ITargetable>();
    private readonly List<ITargetable> _alreadyHit = new List<ITargetable>();
```

  - Trong `Tick`, đổi `DamageInRange(context.Grid);` thành `DamageInRange(context.TargetsFor(Team));`.
  - Thay `DamageInRange` bằng:

```csharp
    private void DamageInRange(ITargetQuery targets)
    {
        targets.QueryBox(transform.position, _worldHalfSize, Direction, _hits);
        foreach (var target in _hits)
        {
            if (!target.IsAlive || _alreadyHit.Contains(target)) continue;
            target.TakeDamage(new DamagingContext(Stats.Damage, Stats.Knockback));
            _alreadyHit.Add(target);
            PierceLeft--;
            if (PierceLeft <= 0)
            {
                Kill();
                return;
            }
        }
    }
```

- [ ] **Step 9: Sửa `HomingProjectile.cs`**
  - Đổi field: `private readonly List<ITargetable> _candidates = new List<ITargetable>();` và `private ITargetable _target;`.
  - Trong `Tick`: `if (_target == null || !_target.IsAlive) _target = AcquireTarget(context.TargetsFor(Team));`
  - Thay `AcquireTarget`:

```csharp
    private ITargetable AcquireTarget(ITargetQuery targets)
    {
        ITargetable closest = null;
        targets.QueryCircle(_center, radius, _candidates);
        float minDistance = float.MaxValue;
        foreach (var candidate in _candidates)
        {
            float distance = (_center - candidate.Position).sqrMagnitude;
            if (distance < 0.0001f) continue;
            if (distance < minDistance)
            {
                closest = candidate;
                minDistance = distance;
            }
        }
        return closest;
    }
```

  - Trong `Move`, đổi dòng `toTarget` thành `Vector2 toTarget = _target.Position - (Vector2)transform.position;`.

- [ ] **Step 10: Viết lại `AuraProjectile.cs`.** Sửa bốn chỗ: bám theo `Owner`, bỏ lambda, bỏ field thừa, và chạy theo thời gian nội bộ `_time` (cộng `dt`) thay cho `Time.time`.

```csharp
using System.Collections.Generic;
using UnityEngine;

public class AuraProjectile : Projectile
{
    [SerializeField] private float _baseRadius = 5f; // ban kinh khi scale = 1

    private readonly List<ITargetable> _hits = new List<ITargetable>();
    private readonly Dictionary<ITargetable, float> _nextHitTime = new Dictionary<ITargetable, float>(); // target -> luc duoc danh lai
    private readonly List<ITargetable> _expired = new List<ITargetable>();
    private Vector2 _center;
    private float _radius;
    private float _time; // dong ho rieng cua aura, cong dt moi tick

    public override void Init(ProjectileSpawnInfo info)
    {
        base.Init(info);
        _nextHitTime.Clear();
        _time = 0f;
    }

    public override void Tick(float dt, ProjectileTickContext context)
    {
        if (!IsAlive) return;
        if (Owner == null || !Owner.IsAlive)
        {
            Kill(); // chu chet -> aura bien mat
            return;
        }

        _time += dt;
        transform.position = Owner.Position;
        DamageInRange(context.TargetsFor(Team));
        CleanUp();
    }

    private void DamageInRange(ITargetQuery targets)
    {
        _center = transform.position;
        _radius = _baseRadius * Mathf.Max(transform.lossyScale.x, transform.lossyScale.y);
        targets.QueryCircle(_center, _radius, _hits);
        foreach (var target in _hits)
        {
            if (_nextHitTime.TryGetValue(target, out float next) && _time < next) continue;
            _nextHitTime[target] = _time + Stats.DamageTickInterval;
            target.TakeDamage(new DamagingContext(Stats.Damage, Stats.Knockback));
        }
    }

    // Xoa target da het cooldown de dictionary khong phinh ra theo so enemy tung cham
    private void CleanUp()
    {
        foreach (var pair in _nextHitTime)
        {
            if (pair.Value <= _time) _expired.Add(pair.Key);
        }
        foreach (var target in _expired) _nextHitTime.Remove(target);
        _expired.Clear();
    }

    private void OnDrawGizmos()
    {
        Gizmos.color = Color.red;
        Gizmos.DrawWireSphere(_center, _radius);
    }
}
```

- [ ] **Step 11: Sửa `WeaponContext.cs`**

```csharp
using UnityEngine;

public readonly struct WeaponContext
{
    public readonly Vector3 PlayerPosition;
    public readonly Vector2 Direction;
    public readonly PlayerStats PlayerStats;
    public readonly IProjectileService ProjectileService;
    public readonly ITargetable Owner; // nguoi cam vu khi

    public WeaponContext(Vector3 playerPosition, Vector2 direction, PlayerStats stats, IProjectileService projectileService, ITargetable owner)
    {
        PlayerPosition = playerPosition;
        Direction = direction;
        PlayerStats = stats;
        ProjectileService = projectileService;
        Owner = owner;
    }
}
```

- [ ] **Step 12: `WeaponController.Tick` truyền owner.** Đổi dòng tạo context thành:

```csharp
        WeaponContext ctx = new WeaponContext(_playerController.PlayerPosition, _playerController.LastMoveDirection, _player.Stats, _projectileService, _playerController);
```

- [ ] **Step 13: Ba weapon tạo `ProjectileSpawnInfo` mới**
  - `KnifeWeapon.FireShot`:

```csharp
        ProjectileSpawnInfo info = new ProjectileSpawnInfo(dir, BuildProjectileStats(ctx.PlayerStats), Team.Player, ctx.Owner);
```

  Đồng thời xoá dòng `using System.Collections;` thừa.

  - `MagicWandWeapon.FireShot`:

```csharp
        ProjectileSpawnInfo info = new ProjectileSpawnInfo(ctx.Direction, BuildProjectileStats(ctx.PlayerStats), Team.Player, ctx.Owner);
```

  - `GarlickWeapon.FireShot`: viết lại cho gọn, bỏ phần check `_isInitialized` bị lặp.

```csharp
    protected override void FireShot(WeaponContext ctx, int shotIndex)
    {
        if (_isInitialized) return; // aura chi spawn 1 lan, sau do tu bam theo owner
        ProjectileSpawnInfo info = new ProjectileSpawnInfo(ctx.Direction, BuildProjectileStats(ctx.PlayerStats), Team.Player, ctx.Owner);
        AuraProjectile projectile = ctx.ProjectileService.Spawn<AuraProjectile>(Data.Prefab, ctx.PlayerPosition, Quaternion.identity, info);
        if (projectile == null) return;
        _cirleProjectile = projectile;
        _isInitialized = true;
    }
```

- [ ] **Step 14: Sửa `GameBootstrap`.** Phần `Start` và `Update`:

```csharp
    private void Start()
    {
        _spatialHashGrid = new SpatialHashGrid(1f);
        _playerController = new PlayerController(_playerView, _playerStats);
        _projectileController = new ProjectileController(
            new EnemyTargetQuery(_spatialHashGrid),
            new PlayerTargetQuery(_playerController));
        _weaponController = new WeaponController(_playerController, startingWeapons, _projectileController);
        _enemyController = new EnemyController(_playerController, _data, _spatialHashGrid, _testEnemySpawn);
    }

    public void Update()
    {
        float dt = Time.deltaTime;
        _playerController.Tick(dt);
        _enemyController.Tick(dt);
        _weaponController.Tick(dt);
        _projectileController.Tick(dt);
    }
```

- [ ] **Step 15: Kiểm tra ràng buộc.** Lệnh dưới phải **không in ra dòng nào**:

```bash
grep -n "EnemyView\|PlayerController\|context.Grid\|context.Position" Assets/_Game/Scripts/Projectile/*.cs
```

- [ ] **Step 16: Verify khi Play** (regression, hành vi phải y như trước):
  - Knife bay thẳng theo burst, pierce đúng số, không trúng một enemy hai lần.
  - Wand đuổi enemy gần nhất.
  - Garlic bám theo player, gây damage theo nhịp. Prefab `Garlick` hiện `_baseRadius = 5`.
  - Đạn của player **không** gây damage cho player. Đứng trong vùng garlic, không có log `Player -... hp` nào từ garlic.

- [ ] **Step 17: Commit**

```bash
git add Assets/_Game/Scripts
git commit -m "refactor: projectiles target via ITargetQuery by Team, aura follows Owner"
```

---

### Task 4: Tách `Volley` khỏi `Weapon`

**Files:**
- Create: `Assets/_Game/Scripts/Combat/Volley.cs`
- Modify: `Assets/_Game/Scripts/Weapon/Weapon.cs` (`Tick`, `TickVolley`, 3 field volley)

**Interfaces:**
- Produces:
  - `class Volley`, với các thành viên `bool IsFiring`, `void Start(int shotCount, float interval)`, `void Stop()`, `void Advance(float dt)` và `bool TryConsumeShot(out int shotIndex)`

- [ ] **Step 1: Tạo `Volley.cs`.** Logic chuyển nguyên từ `Weapon.TickVolley`.

```csharp
using UnityEngine;

// Dem nhip 1 loat N vien cach nhau interval. Khong biet gi ve dan, chi bao "toi luot vien thu i".
// Cach dung moi frame: Advance(dt) roi while (TryConsumeShot(out i)) Fire(i);
public class Volley
{
    private int _shotsRemaining;
    private int _shotIndex;
    private float _timer;
    private float _interval;

    public bool IsFiring => _shotsRemaining > 0;

    public void Start(int shotCount, float interval)
    {
        _shotsRemaining = Mathf.Max(1, shotCount);
        _shotIndex = 0;
        _timer = 0f; // vien dau ban ngay
        _interval = interval;
    }

    public void Stop()
    {
        _shotsRemaining = 0;
    }

    public void Advance(float dt)
    {
        _timer -= dt;
    }

    // timer += interval (khong gan =) de giu nhip va bu kip khi frame dai
    public bool TryConsumeShot(out int shotIndex)
    {
        if (_shotsRemaining <= 0 || _timer > 0f)
        {
            shotIndex = -1;
            return false;
        }
        shotIndex = _shotIndex++;
        _shotsRemaining--;
        _timer += _interval;
        return true;
    }
}
```

- [ ] **Step 2: Sửa `Weapon.cs`.** Xoá 3 field `_shotsRemaining`, `_shotIndex`, `_shotTimer` và hàm `TickVolley`, rồi thêm:

```csharp
    private readonly Volley _volley = new Volley();

    public void Tick(float deltaTime, in WeaponContext ctx)
    {
        if (_volley.IsFiring)
        {
            FireVolley(deltaTime, ctx);
            return;
        }
        _cooldownTimer -= deltaTime;
        if (_cooldownTimer > 0f) return;

        // loat moi
        _volley.Start(GetShotCount(ctx.PlayerStats), Data.ProjectileInterval);
        FireVolley(0f, ctx);
        _cooldownTimer = GetCooldown(ctx.PlayerStats);
    }

    private void FireVolley(float deltaTime, in WeaponContext ctx)
    {
        _volley.Advance(deltaTime);
        while (_volley.TryConsumeShot(out int shotIndex))
        {
            FireShot(ctx, shotIndex);
        }
    }
```

- [ ] **Step 3: Verify khi Play.** Tạm đặt `ProjectileCount = 3` trong `KnifeData.asset`. Knife phải bắn 3 viên nối nhau cách khoảng 0.06s, giống hệt trước khi refactor. Wand cũng bắn burst. Garlic vẫn spawn một lần. **Revert `ProjectileCount` về 1.**

- [ ] **Step 4: Commit**

```bash
git add Assets/_Game/Scripts/Combat/Volley.cs Assets/_Game/Scripts/Combat/Volley.cs.meta Assets/_Game/Scripts/Weapon/Weapon.cs
git commit -m "refactor: extract Volley from Weapon"
```

---

### Task 5: Enemy bắn đạn (EnemyRangedAttack)

**Files:**
- Create: `Assets/_Game/Scripts/Enemy/EnemyRangedAttackData.cs`
- Create: `Assets/_Game/Scripts/Enemy/EnemyRangedAttack.cs`
- Modify: `Assets/_Game/Scripts/Enemy/EnemyData.cs`
- Modify: `Assets/_Game/Scripts/Enemy/EnemyView.cs` (`Init`, thêm property `RangedAttack`)
- Modify: `Assets/_Game/Scripts/Enemy/EnemyController.cs` (constructor, `TestSpawn`, `Tick`)
- Modify: `Assets/_Game/Scripts/Core/GameBootstrap.cs`
- Create (Unity Editor): `Assets/_Game/Prefabs/Enemy/EnemyBullet.prefab`, `Assets/_Game/Prefabs/Enemy/ZombieShooter.prefab` (prefab variant của `Zombie`), `Assets/_Game/SO/EnemyData/ShooterRangedAttack.asset`, `Assets/_Game/SO/EnemyData/ZombieShooter.asset`

**Interfaces:**
- Consumes:
  - `Volley` (Task 4)
  - `Team`, `ITargetable` (Task 1)
  - `ProjectileSpawnInfo(dir, stats, team, owner)`, `IProjectileService.Spawn<T>` (Task 3)
  - `PlayerController : ITargetable` (Task 2)
- Produces:
  - `EnemyRangedAttack.Init(EnemyRangedAttackData)`
  - `EnemyRangedAttack.Tick(float dt, ITargetable shooter, ITargetable target, IProjectileService projectiles)`
  - `EnemyView.RangedAttack` (null nếu enemy không bắn)
  - `EnemyController(PlayerController, EnemyData, EnemyData shooterData, SpatialHashGrid, IProjectileService, int testEnemySpawn, int testShooterSpawn)`

- [ ] **Step 1: Tạo `EnemyRangedAttackData.cs`**

```csharp
using UnityEngine;

[CreateAssetMenu(fileName = "EnemyRangedAttack", menuName = "Scriptable Objects/EnemyRangedAttack")]
public class EnemyRangedAttackData : ScriptableObject
{
    [Header("Projectile")]
    public GameObject ProjectilePrefab; // prefab co MovingProjectile
    public float Speed = 6f;
    public float Damage = 5f;
    public float Size = 1f;
    public float Duration = 4f;
    public int Pierce = 1;

    [Header("Fire")]
    [Tooltip("Chi ban khi player trong tam nay")]
    public float Range = 8f;
    public float Cooldown = 2f;
    [Tooltip("So vien moi loat")]
    public int ShotCount = 1;
    [Tooltip("Giay giua 2 vien trong 1 loat")]
    public float ShotInterval = 0.15f;
    [Tooltip("Lech ngau nhien +-do cho moi vien")]
    public float SpreadAngle = 0f;

    public ProjectileStats BuildStats() => new ProjectileStats(Speed, Damage, Pierce, Size, Duration, 0f, 0f);
}
```

- [ ] **Step 2: `EnemyData` thêm field** (sau `Stats`):

```csharp
    [Header("Attack")]
    public EnemyRangedAttackData RangedAttack; // null = enemy chi can (contact damage)
```

- [ ] **Step 3: Tạo `EnemyRangedAttack.cs`**

```csharp
using UnityEngine;

// Runtime state cua don ban cho 1 enemy. Nhip giong Weapon: cooldown -> 1 loat (Volley) -> cooldown.
public class EnemyRangedAttack
{
    private readonly Volley _volley = new Volley();
    private EnemyRangedAttackData _data;
    private float _cooldownTimer;

    public void Init(EnemyRangedAttackData data)
    {
        _data = data;
        _volley.Stop();
        _cooldownTimer = data.Cooldown * Random.value; // lech nhip de cac enemy khong ban cung luc
    }

    public void Tick(float dt, ITargetable shooter, ITargetable target, IProjectileService projectiles)
    {
        if (!shooter.IsAlive || !target.IsAlive)
        {
            _volley.Stop();
            return;
        }

        if (_volley.IsFiring)
        {
            FireVolley(dt, shooter, target, projectiles);
            return;
        }

        _cooldownTimer -= dt;
        if (_cooldownTimer > 0f) return;
        // ngoai tam: giu trang thai san sang, vao tam la ban ngay
        if ((target.Position - shooter.Position).sqrMagnitude > _data.Range * _data.Range) return;

        _volley.Start(_data.ShotCount, _data.ShotInterval);
        FireVolley(0f, shooter, target, projectiles);
        _cooldownTimer = _data.Cooldown;
    }

    private void FireVolley(float dt, ITargetable shooter, ITargetable target, IProjectileService projectiles)
    {
        _volley.Advance(dt);
        while (_volley.TryConsumeShot(out _))
        {
            FireShot(shooter, target, projectiles);
        }
    }

    private void FireShot(ITargetable shooter, ITargetable target, IProjectileService projectiles)
    {
        Vector2 dir = target.Position - shooter.Position; // ngam lai moi vien
        if (dir.sqrMagnitude < 0.0001f) dir = Vector2.right;
        dir.Normalize();
        if (_data.SpreadAngle > 0f)
        {
            float spread = Random.Range(-_data.SpreadAngle, _data.SpreadAngle);
            dir = Quaternion.Euler(0f, 0f, spread) * dir;
        }

        float angle = Mathf.Atan2(dir.y, dir.x) * Mathf.Rad2Deg;
        ProjectileSpawnInfo info = new ProjectileSpawnInfo(dir, _data.BuildStats(), Team.Enemy, shooter);
        projectiles.Spawn<MovingProjectile>(_data.ProjectilePrefab, shooter.Position, Quaternion.Euler(0f, 0f, angle), info);
    }
}
```

- [ ] **Step 4: `EnemyView` giữ attack.** Thêm field và property:

```csharp
    // tmp: state cua enemy dang nam trong View, sau nay tach Enemy model thi chuyen sang do
    private readonly EnemyRangedAttack _rangedAttack = new EnemyRangedAttack();
    public EnemyRangedAttack RangedAttack { get; private set; } // null = khong ban
```

Trong `Init`, trước `IsAlive = true;` thêm:

```csharp
        RangedAttack = data.RangedAttack != null ? _rangedAttack : null;
        RangedAttack?.Init(data.RangedAttack);
```

- [ ] **Step 5: Sửa `EnemyController`**
  - Thêm 2 field: `private readonly IProjectileService _projectileService;` và `private readonly EnemyData _shooterData;`.
  - Viết lại constructor và `TestSpawn`:

```csharp
    public EnemyController(PlayerController playerController, EnemyData enemyData, EnemyData shooterData,
        SpatialHashGrid spatialHashGrid, IProjectileService projectileService, int testEnemySpawn, int testShooterSpawn)
    {
        _playerController = playerController;
        _enemyData = enemyData;
        _shooterData = shooterData;
        _spatialHashGrid = spatialHashGrid;
        _projectileService = projectileService;
        _neighborCacheList = new List<EnemyView>();
        _enemies = new List<EnemyView>();
        _testEnemySpawn = testEnemySpawn;
        for (int i = 0; i < testEnemySpawn; i++) TestSpawn(_enemyData);
        if (_shooterData != null)
        {
            for (int i = 0; i < testShooterSpawn; i++) TestSpawn(_shooterData);
        }
    }

    private void TestSpawn(EnemyData data)
    {
        Vector3 pos = new Vector3(Random.Range(-10.0f, 10.0f), Random.Range(-10.0f, 10.0f));
        EnemyView enemyView = ObjectPoolingManager.Instance.SpawnObject<EnemyView>(data.Prefab, pos, Quaternion.identity,
            ObjectPoolingManager.PoolType.Enemy);
        enemyView.Init(data, new EnemySpawnContext(_playerController.PlayerPosition));
        _enemies.Add(enemyView);
    }
```

  - Trong `Tick`, ngay sau khối contact damage (Task 2, Step 5) và vẫn trong vòng `foreach`, thêm:

```csharp
            if (enemy.IsAlive) enemy.RangedAttack?.Tick(_deltaTime, enemy, _playerController, _projectileService);
```

- [ ] **Step 6: `GameBootstrap` wiring**
  - Thêm 2 field cạnh `_data`:

```csharp
    [SerializeField] private EnemyData _shooterData;
    [SerializeField] private int _testShooterSpawn;
```

  - Đổi dòng tạo `EnemyController`:

```csharp
        _enemyController = new EnemyController(_playerController, _data, _shooterData, _spatialHashGrid, _projectileController, _testEnemySpawn, _testShooterSpawn);
```

- [ ] **Step 7: Tạo asset trong Unity Editor**
  1. **EnemyBullet prefab:**
     - Duplicate `Prefabs/Weapon/Knife.prefab`, đổi tên thành `EnemyBullet` và chuyển vào `Prefabs/Enemy/`.
     - Đổi sprite sang hình tròn (vd `Knob` có sẵn của Unity) và tô màu đỏ hoặc tím cho dễ phân biệt với đạn player.
     - Scale 0.3. Đặt `_halfSize` của `MovingProjectile` khoảng `(0.5, 0.5)`; bật Gizmos để chỉnh cho khớp sprite.
     - Lưu ý: `EnemyRangedAttack` xoay đạn theo góc **không** trừ 45° như knife. Nếu dùng sprite knife sẽ bị lệch hướng, nên dùng sprite tròn.
  2. **`SO/EnemyData/ShooterRangedAttack.asset`:** Create, chọn `Scriptable Objects/EnemyRangedAttack`, gán `ProjectilePrefab = EnemyBullet`, giữ các giá trị mặc định.
  3. **`Prefabs/Enemy/ZombieShooter.prefab`:** chuột phải `Zombie.prefab`, chọn Create > Prefab Variant, rồi đổi màu SpriteRenderer (vd xanh) để nhận ra.
  4. **`SO/EnemyData/ZombieShooter.asset`:** duplicate `Zombie.asset`, gán `Prefab = ZombieShooter` và `RangedAttack = ShooterRangedAttack`.
  5. **GameBootstrap trong scene:** gán `_shooterData = ZombieShooter` và `_testShooterSpawn = 5`.

- [ ] **Step 8: Verify khi Play**
  - Shooter (màu khác) bắn đạn về phía player khi player trong khoảng 8 unit, mỗi khoảng 2s; các shooter không bắn đồng loạt.
  - Đạn trúng player: player nháy đỏ, Console in `Player -4 hp ...` (5 trừ armor 1), có i-frame.
  - Đạn enemy **xuyên qua** enemy khác, không gây damage cho enemy.
  - Knife và wand của player **không** va vào đạn enemy, không bắn trúng player.
  - Tạm đặt `ShotCount = 3` trong `ShooterRangedAttack.asset` để thấy burst, sau đó trả về 1. Tạm đặt `SpreadAngle = 15` để thấy đạn toả ra, sau đó trả về 0. (Hoặc giữ giá trị mới nếu muốn, vì đây là asset mới.)
  - Đạn hết `Duration` thì biến mất. Pool `WeaponProjectile` trong Hierarchy không tăng mãi.
  - Shooter chết khi giữa loạt bắn thì không còn đạn mới bắn ra.

- [ ] **Step 9: Commit**

```bash
git add Assets/_Game/Scripts Assets/_Game/Prefabs/Enemy Assets/_Game/SO/EnemyData Assets/_Game/Scenes
git commit -m "add: enemy ranged attack using shared projectile system"
```

(Đường dẫn scene có thể khác; xem `git status` và add file `.unity` chứa GameBootstrap.)

---

## Ngoài phạm vi (ghi lại để làm sau)

- **Enemy model tách khỏi `EnemyView`:** stats, máu và `EnemyRangedAttack` đang nằm trong View.
- **Shooter dừng ở khoảng cách bắn** thay vì lao vào player. Cần thêm `StopDistance` cho movement.
- **Knockback cho player** (`DamagingContext.Knockback` hiện bị bỏ qua cho player).
- **UI thanh máu** sẽ thay `Debug.Log` trong `PlayerController.TakeDamage`.
- **Pool inject** thay cho `ObjectPoolingManager.Instance`.
- **`Weapon.BuildProjectileStats`** vẫn dùng `SpeedRate` thay vì `ProjectileSpeedRate`.
- **`HomingProjectile._target`:** nếu enemy chết rồi được pool spawn lại thì reference cũ thành "sống lại" ở chỗ khác. Hiếm gặp nhưng có thể làm wand bẻ hướng sai. Sửa bằng cách lưu một spawn id cùng với target.
