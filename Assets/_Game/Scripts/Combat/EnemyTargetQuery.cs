using System.Collections.Generic;
using UnityEngine;

// spatial grid
public class EnemyTargetQuery : ITargetQuery
{
    private readonly ISpatialGridQuery _grid;
    private readonly List<EnemyView> _cached = new List<EnemyView>();

    public EnemyTargetQuery(ISpatialGridQuery grid)
    {
        _grid = grid;
    }

    public void QueryCircle(Vector2 center, float radius, List<ITargetable> result)
    {
        _grid.GetEnemyInRadius(center, radius, _cached);
        Copy(result);
    }

    public void QueryBox(Vector2 center, Vector2 halfSize, Vector2 right, List<ITargetable> result)
    {
        _grid.GetEnemiesInBox(center, halfSize, right, _cached);
        Copy(result);
    }

    private void Copy(List<ITargetable> result)
    {
        result.Clear();
        foreach (var enemy in _cached) result.Add(enemy);
        _cached.Clear();
    }
}
