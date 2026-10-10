using UnityEngine;

public class EnemyRangedAttack
{
    private readonly Volley _volley = new Volley();
    private EnemyRangedAttackData _data;
    private float _cooldownTimer;

    public void Init(EnemyRangedAttackData data)
    {
        _data = data;
        _volley.Stop();
        _cooldownTimer = data.Cooldown * Random.value; 
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
        Vector2 dir = target.Position - shooter.Position;
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
