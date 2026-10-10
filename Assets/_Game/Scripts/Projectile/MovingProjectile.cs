using System;
using System.Collections.Generic;
using UnityEngine;

public class MovingProjectile : Projectile
{
    
    private float LifeTimeLeft;
    private int PierceLeft;
    private readonly List<ITargetable> _hits = new List<ITargetable>();
    private readonly List<ITargetable> _alreadyHit = new List<ITargetable>();
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

        DamageInRange(context.TargetsFor(Team));
        Move(dt);
    }
    
    protected virtual void Move(float deltaTime)
    {
        transform.position += (Vector3)(Direction * (Stats.Speed * deltaTime));
    }

    private void DamageInRange(ITargetQuery targets)
    {
        targets.QueryBox(transform.position, _worldHalfSize, Direction, _hits);
        foreach (var target in _hits)
        {
            if (!target.IsAlive || _alreadyHit.Contains(target)) continue;
            target.TakeDamage(new DamagingContext(Stats.Damage, Stats.Knockback));
            _alreadyHit.Add(target);
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
