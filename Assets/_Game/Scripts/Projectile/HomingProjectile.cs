using System;
using UnityEngine;

public class HomingProjectile : MovingProjectile
{
    private Transform _target;
    private static readonly Collider2D[] _hits = new Collider2D[64];
    private Vector2 _center;
    [SerializeField] private float radius = 4f;
    [SerializeField] private float turnRate = 270f;
    [SerializeField] private LayerMask _enemyLayer;

    public override void Init(ProjectileSpawnInfo info)
    {
        base.Init(info);
        AcquireTarget();
    }
    
    private void AcquireTarget() //later refactor
    {
        float minDistance = float.MaxValue;
        _target = null;
        _center = transform.position;
        int hitCount = Physics2D.OverlapCircleNonAlloc(_center, radius ,_hits,_enemyLayer);
        if(hitCount <=0 )
        {
            return;
        }
        for(int i =0;i<hitCount;i++)
        {
            float currentDistance = GetDistanceTo(_hits[i]);
            if(_target ==null || currentDistance <= minDistance)
            {
                _target = _hits[i].transform;
                minDistance = currentDistance;
            }
        }
        Direction = (_target.position - transform.position).normalized;
    }
    
    private void OnDrawGizmosSelected()
    {
        Gizmos.color = Color.red;
        Gizmos.DrawWireSphere(_center, radius);
    }
    
    protected override void Move(float deltaTime)
    {
        if(!IsAlive) return;
        if (_target != null)
        {
            Vector2 desired = ((Vector2)_target.position - (Vector2)transform.position).normalized;
            Direction = (Vector2) Vector3.RotateTowards(Direction, desired, turnRate * Mathf. Deg2Rad * deltaTime, 0f); //what
        }
        base.Move(deltaTime);
    }

    public override void OnDespawn()
    {
        base.OnDespawn();
        _target = null;
    }
    
    private float GetDistanceTo(Collider2D target)
    {
        return Vector3.Distance(transform.position, target.transform.position);
    }

}
