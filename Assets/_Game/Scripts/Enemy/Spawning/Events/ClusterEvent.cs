using UnityEngine;

[CreateAssetMenu(fileName = "ClusterEvent", menuName = "Scriptable Objects/Spawn Events/Cluster")]
public class ClusterEvent : SpawnEventData
{
    //Ban kinh cum. Spread * 2 nen nho hon RecycleMargin
    public float Spread = 1f;

    // Ca cum o 1 diem ngoai mep man hinh, do vao tu 1 huong
    public override void Execute(EnemyController enemies, SpawnArea area)
    {
        if (Enemy == null) return;
        Vector2 edge = area.RandomPointOnEdge();
        Vector2 outward = (edge - area.Center).normalized;
        Vector2 center = edge + outward * Spread;
        for (int i = 0; i < Count; i++)
        {
            enemies.Spawn(Enemy, center + Random.insideUnitCircle * Spread);
        }
    }
}
