using UnityEngine;

public struct ProjectileSpawnInfo
{
    public Vector2 Direction;
    public Transform Origin;
    public ProjectileStats Stats;

    public ProjectileSpawnInfo(Vector2 direction, Transform origin, ProjectileStats stats)
    {
        Direction = direction;
        Origin = origin;
        Stats = stats;
    }

}
