using UnityEngine;

public class HomingProjectile : MovingProjectile
{
    private Transform _target;
    private float minDistance;
    private float currentDistance;
    private Collider2D[] _hits = new Collider2D[64];
    private int _hitCount;
    [SerializeField] private LayerMask _enemyLayer;

    private void Start() //later refactor
    {
        minDistance = 10000f;
        currentDistance = -1;
        _hitCount = Physics2D.OverlapCircleNonAlloc(_center, radius ,_hits,_enemyLayer);
        if(_hitCount <=0 )
        {
            _isAlive = false;
            return;
        }
        for(int i =0;i<hitCount;i++)
        {
            currentDistance = GetDistanceTo(_hitCount[i]);
            if(_target!=null && currentDistance <= minDistance)
            {
                _target = _hitCount[i];
                minDistance = currentDistance;
            }
        }
        Direction = (_target.position - transform.position).normalized;
    }
    
    protected override void Move(float deltaTime)
    {
        if(!_isAlive) return;
        transform.position += (Vector3)(Direction * (Stats.Speed * deltaTime));
    }

    private void GetDistanceTo(Transform target)
    {
        return Math.Abs(target.position - this.trasform.position);
    }

}
