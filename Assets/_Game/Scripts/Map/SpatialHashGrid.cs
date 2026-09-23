using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UIElements;

public class SpatialHashGrid
{
    private readonly float _cellSize;
    private Dictionary<EnemyCell, List<EnemyView>> _buckets;
    
    
    public SpatialHashGrid(float cellSize)
    {
        _cellSize = cellSize;
        _buckets = new Dictionary<EnemyCell, List<EnemyView>> ();
    }

    private Vector3 CellToWorld(EnemyCell cell)
    {
        return new  Vector3(cell.X * _cellSize, cell.Y * _cellSize, 0.0f);
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

    public void GetNeighbours(EnemyView enemyView,ref List<EnemyView> neighbours)
    {
        if (enemyView == null) return;
        neighbours.Clear();
        EnemyCell centerCell =  WorldToCell(enemyView.transform);
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

    public void DrawGizmos()
    {
        Vector3 size = new Vector3(_cellSize, _cellSize, 0.05f);
        foreach (var cell in _buckets)
        {
            int enemyCount = cell.Value.Count;
            Vector3 center = CellToWorld(cell.Key);
            if(enemyCount >0)
            {
                Gizmos.color = new Color(0f, 1f, 0f, 0.25f);
                Gizmos.DrawCube(center, size);
                
                Gizmos.color = Color.red;
                Gizmos.DrawWireCube(center, size);
            }
            else
            {
                Gizmos.color = new Color(1f, 1f, 1f, 0.2f);
                Gizmos.DrawWireCube(center, size);
            }
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
