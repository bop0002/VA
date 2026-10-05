using System;
using System.Collections.Generic;
using UnityEngine;

public class HomingProjectile : MovingProjectile
{
    private List<EnemyView> _candidates = new List<EnemyView>();
    private Vector2 _center;     
    private EnemyView _target; 
    private bool _hasAimed;       // false = chua ngam lan nao -> lan dau co muc tieu se quay thang vao no

    //ban kinh tim dich
    [SerializeField] private float radius = 4f;

    //max turn rate to enemy
    [SerializeField] private float turnRate = 270f;


    public override void Init(ProjectileSpawnInfo info)
    {
        base.Init(info);
        _target = null;
        _hasAimed = false;
    }

    public override void Tick(float dt,ProjectileTickContext context)
    {
        if (!IsAlive) return;
        _center = transform.position;
        if(_target == null || !_target.IsAlive) _target = AcquireTarget(context.Grid);
        base.Tick(dt,context); 
    }

    private EnemyView AcquireTarget(ISpatialGridQuery query)
    {
        EnemyView closest = null;
        query.GetEnemyInRadius(_center,radius,_candidates); 
        float minDistance = float.MaxValue;
        foreach (var enemy in _candidates)
        {
            float distance = (_center - (Vector2)enemy.transform.position).sqrMagnitude;
            if(distance<0.0001f) continue;
            if (distance < minDistance)
            {
                closest = enemy;
                minDistance = distance;
            }
        }

        return closest;
    }
    
    private void OnDrawGizmosSelected()
    {
        Gizmos.color = Color.red;
        Gizmos.DrawWireSphere(_center, radius);
    }

    protected override void Move(float deltaTime)
    {
        if (_target != null)
        {
            Vector2 toTarget = (Vector2)(_target.transform.position - transform.position);
            if (toTarget.sqrMagnitude > 0.0001f)
            {
                Vector2 directionToTarget = toTarget.normalized;

                Direction = _hasAimed ? (Vector2)Vector3.RotateTowards(Direction, directionToTarget,
                    turnRate * Mathf.Deg2Rad * deltaTime, 0f) : directionToTarget;
                
                //Di thang den muc tieu neu da co khong co thi queo trong mat
                
                _hasAimed = true;
            }
        }
        base.Move(deltaTime); 
    }

    public override void OnDespawn()
    {
        base.OnDespawn();
        _target = null;
    }

}
