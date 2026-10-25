using UnityEngine;

[CreateAssetMenu(fileName = "SwarmEvent", menuName = "Scriptable Objects/Spawn Events/Swarm")]
public class SwarmEvent : SpawnEventData
{
    public float Speed = 4f;
    public float Width = 3f;
    public float Depth = 2f;

    public override void Execute(EnemyController enemies, SpawnArea area)
    {
        if (Enemy == null) return;
        Vector2 start = area.RandomPointOnEdge();
        Vector2 dir = (area.Center - start).normalized;
        Vector2 side = new Vector2(-dir.y, dir.x);
        for (int i = 0; i < Count; i++)
        {
            Vector2 pos = start
                          + side * Random.Range(-Width * 0.5f, Width * 0.5f)
                          - dir * Random.Range(0f, Depth);
            enemies.SpawnStraight(Enemy, pos, dir, Speed);
        }
    }
}
