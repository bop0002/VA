using UnityEngine;

public struct ProjectileSpawnInfo
{
    public Vector2 Direction;
    public ProjectileStats Stats;
    public Team Team;           // phe nguoi ban
    public ITargetable Owner;   // nguoi ban, Aura bam theo. Co the null voi dan khong can owner

    public ProjectileSpawnInfo(Vector2 direction, ProjectileStats stats, Team team, ITargetable owner)
    {
        Direction = direction;
        Stats = stats;
        Team = team;
        Owner = owner;
    }
}
