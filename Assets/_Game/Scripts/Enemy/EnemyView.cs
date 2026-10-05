using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class EnemyView : MonoBehaviour,IPoolable,IDamageable
{
    private EnemyData _data;
    private EnemyStats  _stats;
    private Vector2 _directionTowardPlayer;
    private Vector3 _playerPosition;
    private SpriteRenderer _renderer;
    
    public float BodyRadius => _stats.BodyRadius;
    
    //DEBUG NOT FINAL VFX GET HIT
    [SerializeField] private float flashDuration = 0.1f;

    [ContextMenu("TestKnockback")]
    private void TestKnockback() => ApplyKnockback(1f);
    
    private Material originalMaterial;
    private Material flashMaterial;
    private Coroutine flashCoroutine;

    private Vector2 _knockbackVelocity;
    private const float maxSeperationDeltaTime = 1 / 30f; //dt
    [SerializeField] private float _knockbackDecay = 5f; //Do tieu cua knock back (V)
    [SerializeField] private float _maxKnockback = 4f;
    [SerializeField] private  float overlapPushStr = 12f; //tmp
    [SerializeField] private  float overlapMaxPushStr = 15f; 
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
        _knockbackVelocity = Vector2.zero;
        _stats = data.Stats;
        _playerPosition = context.PlayerPosition; //hoi thua cho ca player nen chi truyen direction thoi ?
        IsAlive =  true;
    }
    
    public void Tick(float deltaTime,List<EnemyView> neighbors,Vector3 playerPosition)
    {
        if(!IsAlive) return;
        _playerPosition = playerPosition;
        _directionTowardPlayer = ( _playerPosition - transform.position).normalized;
        Move(deltaTime,ComputeSeparation(neighbors));
        FlipSprite();
    }

    private void Move(float deltaTime,Vector2 overlapPushForce)
    {
        float sepDt = Mathf.Min(deltaTime,maxSeperationDeltaTime);
        Vector2 displacement = ((_directionTowardPlayer * _stats.Speed + _knockbackVelocity )* deltaTime)  + overlapPushForce * sepDt;
        transform.position += (Vector3)displacement;
        _knockbackVelocity *= Mathf.Exp(-_knockbackDecay * deltaTime);
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
            onDead?.Invoke();
        }
    }

    private void OnDrawGizmos()
    {
        Gizmos.color = Color.red;
        Gizmos.DrawSphere(transform.position,_stats.BodyRadius);
    }

    private Vector2 ComputeSeparation(List<EnemyView> neighbors)
    {
        //later to ispatailgrid???
        Vector2 pushForce = Vector2.zero;
        foreach(var other in neighbors)
        {
            if(other == this) continue;
            Vector2 delta = transform.position - other.transform.position;
            float distance = delta.magnitude;
            float overlapRadius = other._stats.BodyRadius + _stats.BodyRadius;
            if(distance < overlapRadius)
            {
                Vector2 pushDir = Vector2.zero;
                if (distance < 0.001f)
                {
                    int myId = gameObject.GetInstanceID();
                    int otherId = other.gameObject.GetInstanceID();
                    pushDir = (myId > otherId) ? Vector2.right : Vector2.left;
                }
                else pushDir = delta/distance;
                float overlapDepth = overlapRadius - distance;
                pushForce += pushDir * (overlapDepth * overlapPushStr);
            }
        }
        return Vector2.ClampMagnitude(pushForce,overlapMaxPushStr);
    }
    
    
    private void ApplyKnockback(float knockback)
    {
        _knockbackVelocity -= _directionTowardPlayer * knockback * _knockbackDecay ;
        _knockbackVelocity = Vector2.ClampMagnitude(_knockbackVelocity,_maxKnockback*_knockbackDecay);
    }
}
