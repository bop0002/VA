using UnityEngine;

// enemy view recycle pool
public readonly struct EnemyDeathInfo
{
    public readonly EnemyData Data;
    public readonly Vector2 Position;

    public EnemyDeathInfo(EnemyData data, Vector2 position)
    {
        Data = data;
        Position = position;
    }
}
