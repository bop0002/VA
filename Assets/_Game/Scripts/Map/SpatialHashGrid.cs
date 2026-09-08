using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UIElements;

public class SpatialHashGrid
{
    private readonly float _cellSize = 1f;
    private Dictionary<EnemyCell, List<EnemyView>> _buckets;
    
    
    public SpatialHashGrid()
    {
        _buckets = new Dictionary<EnemyCell, List<EnemyView>> ();
    }

    private EnemyCell WorldToCell(Transform transform)
    {
        return new EnemyCell(Mathf.RoundToInt(transform.position.x/_cellSize),Mathf.RoundToInt(transform.position.y/_cellSize));    
    }

    public List<EnemyView> GetEnemyInCell(Transform transform)
    {
        EnemyCell cell = WorldToCell(transform);
        if (!_buckets.TryGetValue(cell, out var list)) return null;
        return list;
    }

    public void GetNeighbours(Transform transform,List<EnemyView> neighbours)
    {
        neighbours.Clear();
        EnemyCell centerCell =  WorldToCell(transform);
        for (int i = -1; i <= 1; i++)
        {
            for (int j = -1; j <= 1; j++)
            {
                EnemyCell tmpCell = new EnemyCell(centerCell.X + i, centerCell.Y + j);
                if (_buckets.TryGetValue(tmpCell, out var list))
                {
                    foreach(var enemy in list) neighbours.Add(enemy);
                }
            }
        }
    }
    
    public void AddToCell(EnemyView enemy)
    {
        EnemyCell cell =  WorldToCell(enemy.transform);
        if (!_buckets.TryGetValue(cell, out var list))
        {
            list = new List<EnemyView>();
            list.Add(enemy);
            _buckets[cell] = list;
        }
        else list.Add(enemy);
    }
    
    
    
    public void ClearBuckets()
    {
        foreach (var list in _buckets.Values)
        {
            list.Clear();
        }
    }

    public readonly struct EnemyCell : IEquatable<EnemyCell> //Dung trong dict nen can viet equal va gethashcode rieng toi uu hieu nang
    {
        public readonly int X;
        public readonly int Y;

        public EnemyCell(int x, int y)
        {
            X = x;
            Y = y;
        }

        public bool Equals(EnemyCell other) 
        {
            return X==other.X && Y==other.Y;
        }
        
        public override int GetHashCode() => HashCode.Combine(X, Y);

    }
    
}
