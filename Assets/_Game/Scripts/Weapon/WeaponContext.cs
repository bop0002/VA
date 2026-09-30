using UnityEngine;

public readonly struct WeaponContext
{
    public readonly Vector3 PlayerPosition;
    public readonly Vector2 Direction;
    public readonly PlayerStats PlayerStats;
    
    public WeaponContext(Vector3 playerPosition, Vector2 direction, PlayerStats stats)
    {
        PlayerPosition = playerPosition;
        Direction = direction;
        PlayerStats = stats;
    }
    
}
