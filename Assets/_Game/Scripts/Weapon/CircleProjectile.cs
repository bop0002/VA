using System;
using DG.Tweening;
using UnityEngine;
public class CircleProjectile : Projectile
{
    
    protected Transform _owner;
    protected float FadeSpeed = 0.35f;
    protected SpriteRenderer SpriteRenderer;

    private void Awake()
    {
        SpriteRenderer = GetComponent<SpriteRenderer>();
    }
    
    public override void Init(ProjectileSpawnInfo info)
    {
        base.Init(info);
        _owner = info.Origin;
    }
    
    protected override void Move(float deltaTime)
    {
        transform.position = _owner.position;
    }
    
    protected override void OnTriggerEnter2D(Collider2D other)
    {
        if (!_isAlive) return;
        if(!other.gameObject.TryGetComponent(out IDamageable damageable))
        {
            return;
        }
        
        damageable.TakeDamage(Damage);
    }
    
    protected override async void Despawn()
    {                
        if (!_isAlive) return;
        _isAlive = false;
        try
        {
            await DespawnSequence();
            ObjectPoolingManager.Instance.DespawnObject(this.gameObject,ObjectPoolingManager.PoolType.WeaponProjectile);   
        }
        catch (Exception e)
        {
            Console.WriteLine("Circle Projectile Exception: " + e);
            throw;
        }
    }

    public override void OnSpawn()
    {
        base.OnSpawn();
        SpriteRenderer.DOKill(); 
        
        Color color = SpriteRenderer.color;
        color.a = 1f;
        SpriteRenderer.color = color;
    }
    
    protected async Awaitable  DespawnSequence()
    {
        SpriteRenderer.DOFade(0f, FadeSpeed);
        await Awaitable.WaitForSecondsAsync(FadeSpeed);
    }
    
}
