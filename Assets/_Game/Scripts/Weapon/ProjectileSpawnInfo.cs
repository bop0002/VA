using UnityEngine;

public struct ProjectileSpawnInfo //Final stats
{
    public Vector2 Direction;
    public Transform Origin;
    public float Speed;
    public float Damage;
    public int Pierce;
    public float Size;
    public float Duration;

    public ProjectileSpawnInfo(Vector2 direction, float speed, float damage, int pierce, float size, float duration,Transform origin)
    {
        Direction = direction;
        Speed = speed;
        Damage = damage;
        Pierce = pierce;
        Size = size;
        Duration = duration;
        Origin = origin;
    }
    
}
