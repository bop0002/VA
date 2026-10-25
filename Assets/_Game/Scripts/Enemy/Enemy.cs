using UnityEngine;

public class Enemy
{
    private readonly EnemyRangedAttack _rangedAttack = new EnemyRangedAttack();
    private EnemyStats _stats;

    public EnemyData Data { get; private set; }
    public EnemyRangedAttack RangedAttack { get; private set; }
    public float CurrentHealth { get; private set; }
    public bool IsAlive { get; private set; }

    public float MaxHealth => _stats.MaxHealth;
    public float Speed => _stats.Speed;
    public float ContactDamage => _stats.Damage;
    public float BodyRadius => _stats.BodyRadius;

    public void Init(EnemyData data)
    {
        Data = data;
        _stats = data.Stats;
        CurrentHealth = _stats.MaxHealth;
        RangedAttack = data.RangedAttack != null ? _rangedAttack : null;
        RangedAttack?.Init(data.RangedAttack);
        IsAlive = true;
    }

    public bool ApplyDamage(float damage)
    {
        if (!IsAlive) return false;
        CurrentHealth = Mathf.Max(0f, CurrentHealth - damage);
        if (CurrentHealth > 0f) return false;
        IsAlive = false;
        return true;
    }

    public void MarkDespawned()
    {
        IsAlive = false;
    }
}
