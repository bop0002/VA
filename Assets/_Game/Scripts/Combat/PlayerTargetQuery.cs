using System.Collections.Generic;
using UnityEngine;

//Ko dung check spatial grid
public class PlayerTargetQuery : ITargetQuery
{
    private readonly ITargetable _player;

    public PlayerTargetQuery(ITargetable player)
    {
        _player = player;
    }

    public void QueryCircle(Vector2 center, float radius, List<ITargetable> result)
    {
        result.Clear();
        if (!_player.IsAlive) return;
        if (CollisionMath.CircleOverlapsCircle(center, radius, _player.Position, _player.Radius)) result.Add(_player);
    }

    public void QueryBox(Vector2 center, Vector2 halfSize, Vector2 right, List<ITargetable> result)
    {
        result.Clear();
        if (!_player.IsAlive) return;
        if (CollisionMath.CircleOverlapsBox(_player.Position, _player.Radius, center, halfSize, right)) result.Add(_player);
    }
}
