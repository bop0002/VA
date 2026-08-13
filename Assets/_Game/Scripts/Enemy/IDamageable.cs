using System;
using UnityEngine;

public interface IDamageable
{
    public void TakeDamage(DamagingContext ctx,Action onDead = null);
}
