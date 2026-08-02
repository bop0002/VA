using UnityEngine;

public class Projectile : MonoBehaviour,IPoolable
{
    
    protected Vector2 Direction;
    protected float Speed;
    protected float Damage;
    protected int PierceLeft;
    protected float Size;
    protected float LifeTime;

    protected bool _isAlive;
    
    public virtual void Init(ProjectileSpawnInfo info)
    {
        Direction = info.Direction.sqrMagnitude > 0.0001f ? info.Direction.normalized : Vector2.right ;
        Speed = info.Speed;
        Damage = info.Damage;
        PierceLeft = Mathf.Max(1, info.Pierce);
        this.transform.localScale = new Vector3(info.Size, info.Size, info.Size);
        Size =  info.Size;
        LifeTime = info.Duration;
        _isAlive = true;

    }

    private void Update()
    {
        if (!_isAlive) return;
        float deltaTime = Time.deltaTime;
        LifeTime -= deltaTime;
        if(LifeTime < 0f)
        {
            Despawn();
            return;
        }

        Move(deltaTime);
    }

    protected virtual void Move(float deltaTime)
    {
        transform.position += (Vector3)(Direction * (Speed * deltaTime));
    }

    protected virtual void OnCollisionEnter2D(Collision2D other)
    {
        if (!_isAlive) return;
        
        if(!other.gameObject.TryGetComponent(out IDamageable damageable))
        {
            return;
        }
        
        damageable.TakeDamage(Damage);
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
