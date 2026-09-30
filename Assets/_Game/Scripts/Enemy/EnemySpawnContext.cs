using UnityEngine;

public struct EnemySpawnContext
{
    public Vector3 PlayerPosition;

    public EnemySpawnContext(Vector3 playerPosition)
    {
        PlayerPosition = playerPosition;
    }
}
