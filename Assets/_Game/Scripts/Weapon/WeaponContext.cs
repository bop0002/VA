using UnityEngine;

public readonly struct WeaponContext
{
    public readonly Vector3 PlayerPosition;
    public readonly Vector2 Direction;
    public readonly PlayerStats PlayerStats;
    public readonly IProjectileService ProjectileService;
    
    public WeaponContext(Vector3 playerPosition, Vector2 direction, PlayerStats stats, IProjectileService projectileService)
    {
        PlayerPosition = playerPosition;
        Direction = direction;
        PlayerStats = stats;
        ProjectileService = projectileService;
    }
    
}
