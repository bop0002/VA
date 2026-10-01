using UnityEngine;

public struct ProjectileSpawnInfo
{
    public Vector2 Direction;
    public Vector3 PlayerPosition;
    public ProjectileStats Stats;

    public ProjectileSpawnInfo(Vector2 direction, Vector3 position, ProjectileStats stats)
    {
        Direction = direction;
        PlayerPosition = position;
        Stats = stats;
    }

}
