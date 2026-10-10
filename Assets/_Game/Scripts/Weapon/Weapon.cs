using UnityEngine;

public abstract class Weapon
{
    protected readonly WeaponData Data;

    public string Id => Data.Id;
    public int Level { get; private set; } = 1;
    public bool IsMaxLevel => Level == Data.MaxLevel;

    protected WeaponLevelStats Stats => Data.Levels[Level - 1];

    private float _cooldownTimer;

    private readonly Volley _volley = new Volley();
    
    protected Weapon(WeaponData data)
    {
        Data = data;
        _cooldownTimer = 0f;
    }

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
    
    protected abstract void FireShot(WeaponContext ctx,int shotIndex);
    protected virtual int GetShotCount(PlayerStats playerStats) => 1;
    /// <summary>Chỉ số của level hiện tại sau khi áp modifier của player.</summary>
    protected virtual ProjectileStats BuildProjectileStats(PlayerStats playerStats)
    {
        WeaponLevelStats levelStats = Stats;
        return new ProjectileStats(
            speed: levelStats.Speed * playerStats.SpeedRate,
            damage: levelStats.Damage * playerStats.DamageRate,
            pierce: levelStats.Pierce + playerStats.Pierce,
            size: levelStats.Size * playerStats.ProjectileSize,
            duration: levelStats.Duration + playerStats.ProjectileDuration,
            knockback: levelStats.Knockback,
            damageTickInterval : GetCooldown(playerStats));
    }

    protected int GetProjectileCount(PlayerStats playerStats)
    {
        return Stats.ProjectileCount + playerStats.ProjectileCount;
    }

    protected virtual float GetCooldown(PlayerStats playerStats)
    {
        return Stats.Cooldown / Mathf.Max(0.01f, playerStats.CooldownRate);
    }

    public bool TryLevelUp()
    {
        if (IsMaxLevel) return false;
        Level++;
        return true;
    }

}
