using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class EnemyView : MonoBehaviour, IPoolable, ITargetable
{
    private readonly Enemy _model = new Enemy();
    private Vector2 _moveDirection;
    private Vector2 _fixedDirection; // khac zero = bay thang (swarm)
    private float _fixedSpeed;
    private Vector3 _playerPosition;
    private SpriteRenderer _renderer;

    public bool MovesStraight => _fixedDirection != Vector2.zero;
    public Vector2 MoveDirection => MovesStraight ? _fixedDirection : _moveDirection;

    public Enemy Model => _model;
    public float BodyRadius => _model.BodyRadius;
    public Vector2 Position => transform.position;
    public float Radius => _model.BodyRadius;
    public float ContactDamage => _model.ContactDamage;
    public float MaxHealth => _model.MaxHealth;
    public float CurrentHealth => _model.CurrentHealth;
    public EnemyRangedAttack RangedAttack => _model.RangedAttack; // null = khong ban
    
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
    
    public bool IsAlive => _model.IsAlive;

    private void Awake()
    {
        _renderer = GetComponent<SpriteRenderer>();

        originalMaterial = _renderer.material;
        flashMaterial = new Material(Shader.Find("GUI/Text Shader"));
    }
    
    public void Init(EnemyData data,EnemySpawnContext context)
    {
        _model.Init(data);
        _knockbackVelocity = Vector2.zero;
        _playerPosition = context.PlayerPosition; //hoi thua cho ca player nen chi truyen direction thoi ?
        _fixedDirection = context.FixedDirection;
        _fixedSpeed = context.FixedSpeed;
    }

    // Recycle: dich sang cho moi, bo knockback dang con
    public void Teleport(Vector2 position)
    {
        transform.position = position;
        _knockbackVelocity = Vector2.zero;
    }
    
    public void Tick(float deltaTime,List<EnemyView> neighbors,Vector3 playerPosition)
    {
        if(!IsAlive) return;
        _playerPosition = playerPosition;
        _moveDirection = MovesStraight ? _fixedDirection : (Vector2)(_playerPosition - transform.position).normalized;
        Move(deltaTime,ComputeSeparation(neighbors));
        FlipSprite();
    }

    private void Move(float deltaTime,Vector2 overlapPushForce)
    {
        float sepDt = Mathf.Min(deltaTime,maxSeperationDeltaTime);
        float speed = MovesStraight ? _fixedSpeed : _model.Speed;
        Vector2 displacement = ((_moveDirection * speed + _knockbackVelocity )* deltaTime)  + overlapPushForce * sepDt;
        transform.position += (Vector3)displacement;
        _knockbackVelocity *= Mathf.Exp(-_knockbackDecay * deltaTime);
    }

    private void FlipSprite()
    {
        if (!(_moveDirection.x > 0))
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
        if (flashCoroutine != null)
        {
            StopCoroutine(flashCoroutine);
            flashCoroutine = null;
        }
        _renderer.material = originalMaterial;
    }
    
    public void TakeDamage(DamagingContext ctx, Action onDead = null)
    {
        if (!IsAlive) return;
        bool died = _model.ApplyDamage(ctx.Damage);

        Flash();
        ApplyKnockback(ctx.Knockback);
        if (died) onDead?.Invoke();
    }

    private void OnDrawGizmos()
    {
        Gizmos.color = Color.red;
        Gizmos.DrawSphere(transform.position,_model.BodyRadius);
    }

    private Vector2 ComputeSeparation(List<EnemyView> neighbors)
    {
        Vector2 pushForce = Vector2.zero;
        foreach(var other in neighbors)
        {
            if(other == this) continue;
            Vector2 delta = transform.position - other.transform.position;
            float distance = delta.magnitude;
            float overlapRadius = other.BodyRadius + BodyRadius;
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
        _knockbackVelocity -= _moveDirection * knockback * _knockbackDecay ;
        _knockbackVelocity = Vector2.ClampMagnitude(_knockbackVelocity,_maxKnockback*_knockbackDecay);
    }
}
