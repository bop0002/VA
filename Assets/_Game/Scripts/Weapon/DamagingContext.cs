using UnityEngine;

public readonly struct DamagingContext
{
    public readonly float Damage;
    public readonly float Knockback;

    public DamagingContext(float damage, float knockback)
    {
        Damage = damage;
        Knockback = knockback;
    }
}
