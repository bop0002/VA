using System;
using System.Collections.Generic;
using UnityEngine;

public class MovingProjectile : Projectile
{
    
    private float LifeTimeLeft;
    private int PierceLeft;
    private List<EnemyView> _hits = new List<EnemyView>();
    private List<EnemyView> _alreadyHit = new List<EnemyView>();
    private Vector2 _worldHalfSize;
    [SerializeField] private Vector2 _halfSize = new Vector2(1f,1f); //half rect x,y 
    public override void Init(ProjectileSpawnInfo info)
    {
        base.Init(info);
        LifeTimeLeft = Stats.Duration;
        PierceLeft = Mathf.Max(1, Stats.Pierce);
        _worldHalfSize = _halfSize * transform.lossyScale;
        _alreadyHit.Clear();
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

        DamageInRange(context.Grid);
        Move(dt);
    }
    
    protected virtual void Move(float deltaTime)
    {
        transform.position += (Vector3)(Direction * (Stats.Speed * deltaTime));
    }

    private void DamageInRange(ISpatialGridQuery query)
    {
        query.GetEnemiesInBox(transform.position,_worldHalfSize,Direction,_hits);
        foreach (var enemy in _hits)
        {
            if(!enemy.IsAlive || _alreadyHit.Contains(enemy)) continue;
            enemy.TakeDamage(new DamagingContext(Stats.Damage, Stats.Knockback),null);
            _alreadyHit.Add(enemy);
            PierceLeft--;
            if (PierceLeft <= 0)
            {
                Kill();
                return;
            }
        }
    }
    
    private void OnDrawGizmos()
    {
        Vector2 half = Application.isPlaying ? _worldHalfSize : _halfSize * transform.lossyScale.x;
        Vector2 dir = Application.isPlaying ? Direction : Vector2.right;
        Gizmos.color = Color.red;
        Gizmos.matrix = Matrix4x4.TRS(transform.position, Quaternion.FromToRotation(Vector3.right, dir), Vector3.one);
        Gizmos.DrawWireCube(Vector3.zero, half * 2f);
        Gizmos.matrix = Matrix4x4.identity;
    }
    

}
