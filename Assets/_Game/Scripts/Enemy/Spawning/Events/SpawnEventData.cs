using UnityEngine;


public abstract class SpawnEventData : ScriptableObject
{
    public EnemyData Enemy;
    [Min(1)] public int Count = 10;
    
    public abstract void Execute(EnemyController enemies, SpawnArea area);
}
