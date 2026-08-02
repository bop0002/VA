using UnityEngine;

public readonly struct WeaponContext
{
    public readonly Transform Origin;
    public readonly Vector2 Direction;
    public readonly PlayerStats PlayerStats;
    
    public WeaponContext(Transform origin, Vector2 direction, PlayerStats stats)
    {
        Origin = origin;
        Direction = direction;
        PlayerStats = stats;
    }
    
}
