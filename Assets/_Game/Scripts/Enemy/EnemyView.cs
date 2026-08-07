using UnityEngine;

public class EnemyView : MonoBehaviour,IPoolable,IDamageable
{
    private EnemyData _data;
    private EnemyStats  _stats;
    private Vector2 _direction;
    private Transform _player;
    private SpriteRenderer _renderer;
    public bool IsAlive { get; private set; }

    private void Awake()
    {
        _renderer = GetComponent<SpriteRenderer>();
    }
    
    public void Init(EnemyData data,EnemySpawnContext context)
    {
        _data = data;
        _stats = data.Stats;
        _player = context.PlayerOrigin;
        IsAlive =  true;
    }
    
    public void Tick(float deltaTime)
    {
        if(!IsAlive) return;
        Move(deltaTime);
        FlipSprite();
    }

    private void Move(float deltaTime)
    {
        _direction = ( _player.position - transform.position).normalized;
        transform.position += (Vector3)(_direction * (_stats.Speed * deltaTime));
    }

    private void FlipSprite()
    {
        if (!(_direction.x > 0))
        {
            _renderer.flipX = true;
        }
        else
        {
            _renderer.flipX = false;
        }
    }
    
    public void OnSpawn()
    {
        
    }

    public void OnDespawn()
    {
        Debug.Log($"{gameObject.name} despawned");
    }
    
    public void TakeDamage(float damage)
    {
        if (!IsAlive) return;
        _stats.Health -= damage;
        Debug.Log($"{gameObject.name} dealt {damage} damage to {_stats.Health}");
        if(_stats.Health <= 0)
        {
            ObjectPoolingManager.Instance.DespawnObject(gameObject,ObjectPoolingManager.PoolType.Enemy);
            IsAlive = false;
        }
    }
}
