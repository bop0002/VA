using System.Collections.Generic;
using UnityEngine;

public class AuraProjectile : Projectile  ///Co nen lam kieu projectile cho aura va orbit:???
{
    private static readonly Collider2D[] _hits = new Collider2D[64];
    [SerializeField] private LayerMask _enemyLayer;
    private Dictionary<IDamageable, float> _hitCooldown;
    private CircleCollider2D  _collider;
    private Vector2 _center;
    private float radius;
    private int hitCount;
    private float currentTime;
    private List<IDamageable> _toRemoveList;
    private void Awake()
    {
        _collider = GetComponent<CircleCollider2D>();
        _hitCooldown = new Dictionary<IDamageable, float>();
        _toRemoveList = new List<IDamageable>();
    }
    
    protected void Update()
    {
        currentTime = Time.time;
        
        DamageInRange();
        CleanUp();
    }

    private void DamageInRange()
    {
        _center = (Vector2)transform.position + _collider.offset;
        radius = _collider.radius * Mathf.Max(transform.lossyScale.x, transform.lossyScale.y);
        hitCount = Physics2D.OverlapCircleNonAlloc(_center, radius ,_hits,_enemyLayer);
        for (int i = 0; i<hitCount; i++)
        {
            if(_hits[i].TryGetComponent(out IDamageable target)) TryDamage(target);
        }
    }

    private void TryDamage(IDamageable target)
    {
        if(_hitCooldown.TryGetValue(target,out float nextHit) && currentTime < nextHit) return;
        
        _hitCooldown[target] = currentTime+Stats.DamageTickInterval;
        target.TakeDamage(new DamagingContext(Stats.Damage, Stats.Knockback),()=>{_toRemoveList.Add(target);});
        
    }
    
    private void CleanUp()
    {
        foreach(var damageable in _hitCooldown)
        {
            if (damageable.Value <= currentTime)
            {
                _toRemoveList.Add(damageable.Key);
            }
        }
        
        foreach (IDamageable damageable in _toRemoveList)
        {
            _hitCooldown.Remove(damageable);
        }
        
        _toRemoveList.Clear();
        
    }
    
    
    private void OnDrawGizmosSelected()
    {
        Gizmos.color = Color.red;
        Gizmos.DrawWireSphere(_center, radius);
    }
    
    public override void Init(ProjectileSpawnInfo info)
    {
        base.Init(info); 
        transform.SetParent(info.Origin);
    }
    
    

    protected void OnTriggerEnter2D(Collider2D other)
    {
        if(other.TryGetComponent(out IDamageable target))TryDamage(target);
    }

    private void OnTriggerExit2D(Collider2D other)
    {
        return;
    }
    



}
