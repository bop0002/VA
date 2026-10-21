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
    private Vector2 _worldOffset;
    [SerializeField] private Vector2 _halfSize = new Vector2(1f,1f); //half rect x,y 
    [SerializeField] private Vector2 _offset; // tam hitbox
    [SerializeField] private GameObject _hitFxPrefab; //(co the de trong)
    public override void Init(ProjectileSpawnInfo info)
    {
        base.Init(info);
        LifeTimeLeft = Stats.Duration;
        PierceLeft = Mathf.Max(1, Stats.Pierce);
        _worldHalfSize = _halfSize * transform.lossyScale;
        _worldOffset = _offset * transform.lossyScale;
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
        targets.QueryBox(HitCenter(Direction, _worldOffset), _worldHalfSize, Direction, _hits);
        foreach (var target in _hits)
        {
            if (!target.IsAlive || _alreadyHit.Contains(target)) continue;
            target.TakeDamage(new DamagingContext(Stats.Damage, Stats.Knockback));
            _alreadyHit.Add(target);
            PierceLeft--;
            if (PierceLeft <= 0)
            {
                SpawnHitFx();
                Kill();
                return;
            }
        }
    }
    
    private Vector2 HitCenter(Vector2 dir, Vector2 offset)
    {
        Vector2 perp = new Vector2(-dir.y, dir.x);
        return (Vector2)transform.position + dir * offset.x + perp * offset.y;
    }

    private void SpawnHitFx()
    {
        if (_hitFxPrefab == null) return;
        GameObject fx = ObjectPoolingManager.Instance.SpawnObject(_hitFxPrefab, transform.position, transform.rotation, ObjectPoolingManager.PoolType.Fx);
        if (fx != null) fx.transform.localScale = transform.lossyScale;
    }

    private void OnDrawGizmos()
    {
        Vector2 half = Application.isPlaying ? _worldHalfSize : _halfSize * transform.lossyScale.x;
        Vector2 dir = Application.isPlaying ? Direction : Vector2.right;
        Vector2 offset = Application.isPlaying ? _worldOffset : _offset * transform.lossyScale.x;
        Gizmos.color = Color.red;
        Gizmos.matrix = Matrix4x4.TRS(HitCenter(dir, offset), Quaternion.FromToRotation(Vector3.right, dir), Vector3.one);
        Gizmos.DrawWireCube(Vector3.zero, half * 2f);
        Gizmos.matrix = Matrix4x4.identity;
    }
    

}
