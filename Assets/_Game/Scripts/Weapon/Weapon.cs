using Unity.VisualScripting;
using UnityEditor.Build;
using UnityEngine;

public abstract class Weapon
{
    protected readonly WeaponData Data;

    public string Id => Data.Id;
    public int Level { get; private set; } = 1;
    public bool IsMaxLevel => Level == Data.MaxLevel;

    protected WeaponLevelStats Stats => Data.Levels[Level - 1];

    private float _cooldownTimer;
    
    protected Weapon(WeaponData data)
    {
        Data = data;
        _cooldownTimer = 0f;
    }

    public void Tick(float deltaTime,in WeaponContext ctx)
    {
        _cooldownTimer -= deltaTime;
        if (_cooldownTimer > 0f)
        {
            return;
        }
        Fire(ctx);
        _cooldownTimer = GetCooldown(ctx);
    }

    protected abstract void Fire(WeaponContext ctx);

    protected virtual float GetCooldown(WeaponContext ctx)
    {
        return Stats.Cooldown / Mathf.Max(0.01f, ctx.PlayerStats.CooldownRate);
    }

    public bool TryLevelUp()
    {
        if (IsMaxLevel) return false;
        Level++;
        return true;
    }
    
}
