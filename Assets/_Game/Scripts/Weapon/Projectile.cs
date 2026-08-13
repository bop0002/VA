using UnityEngine;

public class Projectile : MonoBehaviour,IPoolable
{

    protected Vector2 Direction;
    protected ProjectileStats Stats;
    protected Vector3 LocalScale;
    
    protected float LifeTimeLeft;
    protected int PierceLeft;

    protected bool _isAlive;
    
    
    public virtual void Init(ProjectileSpawnInfo info)
    {
        Direction = info.Direction.sqrMagnitude > 0.0001f ? info.Direction.normalized : Vector2.right ;
        Stats = info.Stats;
        LifeTimeLeft = Stats.Duration;
        PierceLeft = Mathf.Max(1, Stats.Pierce);
        LocalScale = transform.localScale;
        _isAlive = true;

    }
    
    public virtual void ApplyStats(ProjectileSpawnInfo info)
    {
        Direction = info.Direction.sqrMagnitude > 0.0001f ? info.Direction.normalized : Vector2.right ;
        Stats = info.Stats;
        LifeTimeLeft = Stats.Duration;
        PierceLeft = Mathf.Max(1, Stats.Pierce);
        transform.localScale = LocalScale * Stats.Size;
        _isAlive = true;
    }
    
    protected virtual void Update()
    {
        if (!_isAlive) return;
        float deltaTime = Time.deltaTime;
        LifeTimeLeft -= deltaTime;
        if(LifeTimeLeft < 0f)
        {
            Despawn();
            return;
        }

        Move(deltaTime);
    }

    protected virtual void Move(float deltaTime)
    {
        transform.position += (Vector3)(Direction * (Stats.Speed * deltaTime));
    }

    protected virtual void OnTriggerEnter2D(Collider2D other)
    {
        if (!_isAlive) return;

        if(!other.gameObject.TryGetComponent(out IDamageable damageable))
        {
            return;
        }

        damageable.TakeDamage(new DamagingContext(Stats.Damage, Stats.Knockback));
        PierceLeft--;
        if (PierceLeft <= 0) Despawn();
    }

    protected virtual void Despawn()
    {
        if (!_isAlive) return;
        _isAlive = false;
        ObjectPoolingManager.Instance.DespawnObject(this.gameObject,ObjectPoolingManager.PoolType.WeaponProjectile);
    }

    public virtual void OnSpawn()
    {

    }

    public virtual void OnDespawn()
    {
        _isAlive = false;
    }

}
