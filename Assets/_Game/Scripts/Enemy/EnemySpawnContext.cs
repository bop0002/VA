using UnityEngine;

public struct EnemySpawnContext
{
    public Transform PlayerOrigin;

    public EnemySpawnContext(Transform origin)
    {
        PlayerOrigin = origin;
    }
}
