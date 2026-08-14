using UnityEngine;

public abstract class Projectile : MonoBehaviour,IPoolable
{

    protected Vector2 Direction;
    protected ProjectileStats Stats;
    protected Vector3 LocalScale;
    
    
    public virtual void Init(ProjectileSpawnInfo info)
    {
        Direction = info.Direction.sqrMagnitude > 0.0001f ? info.Direction.normalized : Vector2.right ;
        Stats = info.Stats;
        LocalScale = transform.localScale;
    }
    
    public virtual void ApplyStats(ProjectileSpawnInfo info)
    {
        Direction = info.Direction.sqrMagnitude > 0.0001f ? info.Direction.normalized : Vector2.right ;
        Stats = info.Stats;
        transform.localScale = LocalScale * Stats.Size;
    }
    


    protected virtual void OnDespawn()
    {
        
    }

    protected virtual void OnSpawn()
    {
        
    }
    
}
