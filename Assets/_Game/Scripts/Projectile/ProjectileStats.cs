/// Chỉ số cuối cùng của một viên đạn = WeaponLevelStats (authoring) + PlayerStats (modifier).
/// Immutable
public readonly struct ProjectileStats
{
    public readonly float Speed;
    public readonly float Damage;
    public readonly int Pierce;
    public readonly float Size;
    public readonly float Duration;
    public readonly float Knockback;
    public readonly float DamageTickInterval;

    public ProjectileStats(float speed, float damage, int pierce, float size, float duration, float knockback,float damageTickInterval)
    {
        Speed = speed;
        Damage = damage;
        Pierce = pierce;
        Size = size;
        Duration = duration;
        Knockback = knockback;
        DamageTickInterval = damageTickInterval;
    }
}
