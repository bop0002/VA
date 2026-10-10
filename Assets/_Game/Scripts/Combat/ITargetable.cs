using UnityEngine;

public interface ITargetable : IDamageable
{
    bool IsAlive { get; }
    Vector2 Position { get; }
    float Radius { get; }
}
