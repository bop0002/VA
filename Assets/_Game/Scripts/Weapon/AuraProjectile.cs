using System.Collections.Generic;
using UnityEngine;

public class AuraProjectile : Projectile  ///Co nen lam kieu projectile cho aura va orbit:???
{

    protected Transform _owner;
    protected List<IDamageable>  _damageables;

    protected float DamageTick;
    
    private void Awake()
    {
        _damageables = new List<IDamageable>();
    }
    
    protected override void Update()
    {
        if (!_isAlive) return;
        float deltaTime = Time.deltaTime;
        
        DamageTick -= deltaTime;
        if(DamageTick <= 0f)
        {
            DamageInRange();
        }
        
        Move(deltaTime);
    }

    private void DamageInRange()
    {
        for (int i = _damageables.Count - 1; i >= 0; i--)
        {
            _damageables[i].TakeDamage(new DamagingContext(Stats.Damage,Stats.Knockback));
            ///for each thi 2 enemy tro len lai crash???
        }
        DamageTick = Stats.DamageTickInterval;
    }

    public override void Init(ProjectileSpawnInfo info)
    {
        base.Init(info);
        DamageTick = 0f;
        _owner = info.Origin;
    }

    public void ApplyStats(ProjectileSpawnInfo info)
    {
        Direction = info.Direction.sqrMagnitude > 0.0001f ? info.Direction.normalized : Vector2.right ;
        Stats = info.Stats;
        LifeTimeLeft = Stats.Duration;
        PierceLeft = Mathf.Max(1, Stats.Pierce);
        transform.localScale = new Vector3(Stats.Size, Stats.Size, Stats.Size);
        _isAlive = true;
    }
    
    protected override void Move(float deltaTime)
    {
        transform.position = _owner.position;
    }

    protected override void OnTriggerEnter2D(Collider2D other)
    {
        if (!_isAlive) return;
        if(!other.gameObject.TryGetComponent(out IDamageable damageable) || other.CompareTag("Player"))
        {
            return;
        }

        damageable.TakeDamage(new DamagingContext(Stats.Damage,Stats.Knockback)); //spammble
        _damageables.Add(damageable); //cheking for mutiple collider per target?
    }

    private void OnTriggerExit2D(Collider2D other)
    {
        if (!_isAlive) return;
        if(!other.gameObject.TryGetComponent(out IDamageable damageable)||other.CompareTag("Player"))
        {
            return;
        }
        _damageables.Remove(damageable);
        
    }
    
    public override void OnDespawn()
    {
        base.OnDespawn();
        _damageables.Clear();
    }



}
