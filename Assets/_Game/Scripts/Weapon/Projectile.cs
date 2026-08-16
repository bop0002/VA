using UnityEngine;

public abstract class Projectile : MonoBehaviour,IPoolable
{

    protected Vector2 Direction;
    protected ProjectileStats Stats;
    protected Vector3 LocalScale;

    private void Awake()
    {
        LocalScale = transform.localScale;
    }
    
    public virtual void Init(ProjectileSpawnInfo info)
    {
        Direction = info.Direction.sqrMagnitude > 0.0001f ? info.Direction.normalized : Vector2.right ;
        Stats = info.Stats;
        LocalScale = LocalScale * Stats.Size;
    }
    

    public virtual void OnDespawn()
    {
        
    }

    public virtual void OnSpawn()
    {
        
    }
    
}
