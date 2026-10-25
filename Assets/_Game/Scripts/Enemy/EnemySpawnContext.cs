using UnityEngine;

public struct EnemySpawnContext
{
    public Vector3 PlayerPosition;
    public Vector2 FixedDirection; // mac dinh duoi player/ dung cho swarm
    public float FixedSpeed;       // dung cho swarm

    public EnemySpawnContext(Vector3 playerPosition)
    {
        PlayerPosition = playerPosition;
        FixedDirection = Vector2.zero;
        FixedSpeed = 0f;
    }

    public EnemySpawnContext(Vector3 playerPosition, Vector2 fixedDirection, float fixedSpeed)
    {
        PlayerPosition = playerPosition;
        FixedDirection = fixedDirection.normalized;
        FixedSpeed = fixedSpeed;
    }
}
