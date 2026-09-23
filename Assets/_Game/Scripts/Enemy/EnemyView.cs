using System;
using System.Collections;
using System.Collections.Generic;
using Unity.VisualScripting.Antlr3.Runtime.Misc;
using UnityEngine;

public class EnemyView : MonoBehaviour,IPoolable,IDamageable
{
    private EnemyData _data;
    private EnemyStats  _stats;
    private Vector2 _directionTowardPlayer;
    private Transform _player;
    private SpriteRenderer _renderer;
    
    //DEBUG NOT FINAL VFX GET HIT
    [SerializeField] private float flashDuration = 0.1f;

    private Material originalMaterial;
    private Material flashMaterial;
    private Coroutine flashCoroutine;
    
    public void Flash()
    {
        if (flashCoroutine != null)
            StopCoroutine(flashCoroutine);

        flashCoroutine = StartCoroutine(FlashRoutine());
    }

    private IEnumerator FlashRoutine()
    {
        _renderer.material = flashMaterial;

        yield return new WaitForSeconds(flashDuration);
        
        _renderer.material = originalMaterial;
        flashCoroutine = null;
    }
    
    public bool IsAlive { get; private set; }

    private void Awake()
    {
        _renderer = GetComponent<SpriteRenderer>();
        
        originalMaterial = _renderer.material;
        flashMaterial = new Material(Shader.Find("GUI/Text Shader"));
    }
    
    public void Init(EnemyData data,EnemySpawnContext context)
    {
        _data = data;
        _stats = data.Stats;
        _player = context.PlayerOrigin;
        IsAlive =  true;
    }
    
    public void Tick(float deltaTime,List<EnemyView> neighbors)
    {
        if(!IsAlive) return;
        _directionTowardPlayer = ( _player.position - transform.position).normalized;
        Move(deltaTime);
        FlipSprite();
    }

    private void Move(float deltaTime)
    {
        transform.position += (Vector3)(_directionTowardPlayer * (_stats.Speed * deltaTime));
    }

    private void FlipSprite()
    {
        if (!(_directionTowardPlayer.x > 0))
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
    
    public void TakeDamage(DamagingContext ctx,Action onDead)
    {
        if (!IsAlive) return;
        _stats.Health -= ctx.Damage;
        /*Debug.Log($"{gameObject.name} dealt {ctx.Damage} damage to {_stats.Health}");*/
        
        Flash();
        ApplyKnockback(ctx.Knockback);
        if(_stats.Health <= 0)
        {
            IsAlive = false;
            ObjectPoolingManager.Instance.DespawnObject(gameObject,ObjectPoolingManager.PoolType.Enemy);
            onDead?.Invoke();
        }
    }

    private void OnDrawGizmos()
    {
        Gizmos.color = Color.red;
        Gizmos.DrawSphere(transform.position,_stats.BodyRadius);
    }

    private void ApplyOverlapForce(List<EnemyView> neighbors)
    {
        
    }
    
    private void ApplyKnockback(float knockback)
    {
        //transform.position -= (Vector3)(_directionTowardPlayer) * knockback;
        /*Debug.Log((Vector3)(_directionTowardPlayer) * knockback);*/
    }
}
