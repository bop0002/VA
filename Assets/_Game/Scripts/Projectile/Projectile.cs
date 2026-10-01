using UnityEngine;

public abstract class Projectile : MonoBehaviour,IPoolable
{

    protected Vector2 Direction;
    protected ProjectileStats Stats;
    private Vector3 _baseScale;

    public bool IsAlive { get;private set; }
    
    protected virtual void Awake()
    {
        _baseScale = transform.localScale;
    }
    
    public virtual void Init(ProjectileSpawnInfo info)
    {
        Direction = info.Direction.sqrMagnitude > 0.0001f ? info.Direction.normalized : Vector2.right ;
        Stats = info.Stats;
        transform.localScale = _baseScale * Stats.Size;
        IsAlive = true;
    }

    public virtual void Tick(float dt,ProjectileTickContext context)
    {
        
    }

    public virtual void Kill()
    {
        if (!IsAlive) return;
        IsAlive = false;
    }
    
    public virtual void OnDespawn()
    {
        IsAlive = false;
    }

    public virtual void OnSpawn()
    {
        
    }
    
}
