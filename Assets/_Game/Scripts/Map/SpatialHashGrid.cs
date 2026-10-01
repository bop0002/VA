using System;
using System.Collections.Generic;
using UnityEngine;

public interface ISpatialGridQuery
{
    public void GetEnemyInRadius(Vector2 center, float radius, List<EnemyView> result);
    public void GetEnemiesInBox(Vector2 center, Vector2 halfSize, Vector2 right, List<EnemyView> result);
}

public class SpatialHashGrid : ISpatialGridQuery
{
    private readonly float _cellSize;
    private Dictionary<EnemyCell, List<EnemyView>> _buckets;
    private readonly float maxEnemyRadius = 0.5f; //tmp

    private List<EnemyView> _candidates;
    
    public SpatialHashGrid(float cellSize)
    {
        _cellSize = cellSize;
        _candidates = new List<EnemyView>();
        _buckets = new Dictionary<EnemyCell, List<EnemyView>> ();
    }

    private Vector3 CellToWorld(EnemyCell cell)
    {
        return new  Vector3(cell.X * _cellSize, cell.Y * _cellSize, 0.0f);
    }
    
    private EnemyCell WorldToCell(Vector2 position)
    {
        return new EnemyCell(Mathf.RoundToInt(position.x/_cellSize),Mathf.RoundToInt(position.y/_cellSize));    
    }
    private EnemyCell WorldToCell(Transform transform) => WorldToCell((Vector2)transform.position);
    public List<EnemyView> GetEnemyInCell(Transform transform)
    {
        EnemyCell cell = WorldToCell(transform);
        if (!_buckets.TryGetValue(cell, out var list)) return null;
        return list;
    }
    
    private void CollectEnemyInBound(Vector2 min,Vector2 max,List<EnemyView> result)
    {
        EnemyCell cMin = WorldToCell(min - maxEnemyRadius * Vector2.one);
        EnemyCell cMax = WorldToCell(max + maxEnemyRadius * Vector2.one);

        for (int x = cMin.X; x <= cMax.X; x++)
        {
            for (int y = cMin.Y; y <= cMax.Y; y++)
            {
                if (_buckets.TryGetValue(new EnemyCell(x,y), out var enemies))
                {
                    result.AddRange(enemies);
                }
            }
        }
    }
    
    public void GetEnemyInRadius(Vector2 center, float radius, List<EnemyView> result)
    {
        result.Clear();
        CollectEnemyInBound(center - Vector2.one * radius,center + Vector2.one * radius,_candidates);
        foreach(var enemy in _candidates)
        {
            if(!enemy.IsAlive) continue;

            float r = enemy.BodyRadius + radius;
            if(r * r >= (center- (Vector2)enemy.transform.position).sqrMagnitude) result.Add(enemy);
        }

        _candidates.Clear();
    }

    public void GetEnemiesInBox(Vector2 center, Vector2 halfSize, Vector2 right, List<EnemyView> result)
    {
        result.Clear();
        Vector2 up = new Vector2(-right.y, right.x);
        Vector2 extent = new Vector2(Mathf.Abs(right.x)*halfSize.x + Mathf.Abs(up.x)*halfSize.y, Mathf.Abs(right.y)*halfSize.x+Mathf.Abs(up.y)* halfSize.y); // extent(extentx,extenty) hinh chu nhat cheo...
        CollectEnemyInBound(center-extent,center+extent,_candidates); //tinh aabb bound... mai quay lai

        foreach (var enemy in _candidates)
        {
            if(!enemy.IsAlive) continue;
            Vector2 d = (Vector2)enemy.transform.position - center;
            Vector2 local = new Vector2(Vector2.Dot(d, right), Vector2.Dot(d, up));
            Vector2 closestPoint = new Vector2(Mathf.Clamp(local.x,-halfSize.x,halfSize.x),Mathf.Clamp(local.y,-halfSize.y,halfSize.y)); //kiem tra xem closet point tren he moi nam ow nua nao cua box halftRadius vector chieu dai xy tuongung...
            float r = enemy.BodyRadius;
            if((local-closestPoint).sqrMagnitude<=r*r) result.Add(enemy);
        }
        _candidates.Clear();
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
