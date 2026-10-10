using System.Collections.Generic;
using UnityEngine;

public class AuraProjectile : Projectile
{
    [SerializeField] private float _baseRadius = 5f; // ban kinh khi scale = 1

    private readonly List<ITargetable> _hits = new List<ITargetable>();
    private readonly Dictionary<ITargetable, float> _nextHitTime = new Dictionary<ITargetable, float>(); // target -> luc duoc danh lai
    private readonly List<ITargetable> _expired = new List<ITargetable>();
    private Vector2 _center;
    private float _radius;
    private float _time; // dong ho rieng cua aura, cong dt moi tick

    public override void Init(ProjectileSpawnInfo info)
    {
        base.Init(info);
        _nextHitTime.Clear();
        _time = 0f;
    }

    public override void Tick(float dt, ProjectileTickContext context)
    {
        if (!IsAlive) return;
        if (Owner == null || !Owner.IsAlive)
        {
            Kill(); // chu chet -> aura bien mat
            return;
        }

        _time += dt;
        transform.position = Owner.Position;
        DamageInRange(context.TargetsFor(Team));
        CleanUp();
    }

    private void DamageInRange(ITargetQuery targets)
    {
        _center = transform.position;
        _radius = _baseRadius * Mathf.Max(transform.lossyScale.x, transform.lossyScale.y);
        targets.QueryCircle(_center, _radius, _hits);
        foreach (var target in _hits)
        {
            if (_nextHitTime.TryGetValue(target, out float next) && _time < next) continue;
            _nextHitTime[target] = _time + Stats.DamageTickInterval;
            target.TakeDamage(new DamagingContext(Stats.Damage, Stats.Knockback));
        }
    }

    // Xoa target da het cooldown de dictionary khong phinh ra theo so enemy tung cham
    private void CleanUp()
    {
        foreach (var pair in _nextHitTime)
        {
            if (pair.Value <= _time) _expired.Add(pair.Key);
        }
        foreach (var target in _expired) _nextHitTime.Remove(target);
        _expired.Clear();
    }

    private void OnDrawGizmos()
    {
        Gizmos.color = Color.red;
        Gizmos.DrawWireSphere(_center, _radius);
    }
}
