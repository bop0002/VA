using System;
using Unity.VisualScripting;
using UnityEngine;

[Serializable] 
public struct WeaponLevelStats
{
    public float Speed;
    public float Damage;
    public int Pierce;
    public float Size;
    public float Duration;
    public float Cooldown;
    public int ProjectileCount;

    [TextArea] public string UpgradeDescription;

}
