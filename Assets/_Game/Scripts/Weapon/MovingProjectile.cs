using UnityEngine;

public class MovingProjectile : Projectile
{
    
    private float LifeTimeLeft;
    private int PierceLeft;

    protected bool _isAlive;
    
    
    public override void Init(ProjectileSpawnInfo info)
    {
        base.Init(info);
        LifeTimeLeft = Stats.Duration;
        PierceLeft = Mathf.Max(1, Stats.Pierce);
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

    protected void OnTriggerEnter2D(Collider2D other)
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

    public void Despawn()
    {
        if (!_isAlive) return;
        _isAlive = false;
        ObjectPoolingManager.Instance.DespawnObject(this.gameObject,ObjectPoolingManager.PoolType.WeaponProjectile);
    }

    public override void OnDespawn()
    {
        _isAlive = false;
    }

}
