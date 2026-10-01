using UnityEngine;

public class MovingProjectile : Projectile
{
    
    private float LifeTimeLeft;
    private int PierceLeft;
    
    
    public override void Init(ProjectileSpawnInfo info)
    {
        base.Init(info);
        LifeTimeLeft = Stats.Duration;
        PierceLeft = Mathf.Max(1, Stats.Pierce);
    }
    
    public override void Tick(float dt,ProjectileTickContext context)
    {
        if (!IsAlive) return;
        LifeTimeLeft -= dt;
        if(LifeTimeLeft < 0f)
        {
            Kill();
            return;
        }
        
        Move(dt);
    }
    
    protected virtual void Move(float deltaTime)
    {
        transform.position += (Vector3)(Direction * (Stats.Speed * deltaTime));
    }

    protected void OnTriggerEnter2D(Collider2D other)
    {
        if (!IsAlive) return;

        if(!other.gameObject.TryGetComponent(out IDamageable damageable))
        {
            return;
        }

        damageable.TakeDamage(new DamagingContext(Stats.Damage, Stats.Knockback));
        PierceLeft--;
        if (PierceLeft <= 0) Kill();
    }



}
