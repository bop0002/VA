using UnityEngine;

[CreateAssetMenu(fileName = "RingEvent", menuName = "Scriptable Objects/Spawn Events/Ring")]
public class RingEvent : SpawnEventData
{
    //Ban kinh vong quanh player ,nho hon vung giu (spawn + RecycleMargin), neu khong se bi recycle 
    public float Radius = 5f;

    public override void Execute(EnemyController enemies, SpawnArea area)
    {
        if (Enemy == null) return;
        float step = Mathf.PI * 2f / Count;
        float startAngle = Random.value * step; // xoay ngau nhien moi lan
        for (int i = 0; i < Count; i++)
        {
            float angle = startAngle + step * i;
            Vector2 offset = new Vector2(Mathf.Cos(angle), Mathf.Sin(angle)) * Radius;
            enemies.Spawn(Enemy, area.Center + offset);
        }
    }
}
