using System.Collections.Generic;
using UnityEngine;

public class AuraProjectile : Projectile  ///Co nen lam kieu projectile cho aura va orbit:???
{
    private List<EnemyView> _hits = new List<EnemyView>();
    [SerializeField] private LayerMask _enemyLayer;
    private Dictionary<IDamageable, float> _hitCooldown = new Dictionary<IDamageable, float>();
    private Vector2 _center;
    private float radius;
    private int hitCount;
    private float currentTime;
    private List<IDamageable> _toRemoveList = new List<IDamageable>();

    private readonly float collideRadius = 5f; // temp
    

    public override void Tick(float dt, ProjectileTickContext context)
    {
        currentTime = Time.time;
        UpdatePosition(context.Position);
        DamageInRange(context.Grid);
        CleanUp();
    }
    
    private void UpdatePosition(Vector3 playerPosition)
    {
        transform.position = playerPosition;
    }
    
    private void DamageInRange(ISpatialGridQuery query)
    {
        _center = (Vector2)transform.position;
        radius = collideRadius * Mathf.Max(transform.lossyScale.x, transform.lossyScale.y);
        query.GetEnemyInRadius(_center, radius, _hits);
        foreach (var enemy in _hits)
        {
            TryDamage(enemy);
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
    
    
    private void OnDrawGizmos()
    {
        Gizmos.color = Color.red;
        Gizmos.DrawWireSphere(_center, radius);
    }
    
    
    
    
    



}
