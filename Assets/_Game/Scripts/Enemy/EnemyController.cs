using System;
using System.Collections.Generic;
using UnityEngine;

public class EnemyController 
{
    private readonly PlayerController _playerController;
    private readonly IProjectileService _projectileService;
    private readonly SpatialHashGrid _spatialHashGrid;
    private readonly List<EnemyView> _enemies;

    private List<EnemyView> _neighborCacheList; //Tam thoi work voi 1 cell size voi lon hon thi ko bic (khong readonly vi truyen ref)
    private float _deltaTime;

    public event Action<EnemyDeathInfo> EnemyDied; // sau nay: roi XP gem, UI kill

    // Gom ca enemy vua chet chua kip don 
    public int ActiveCount => _enemies.Count;

    public EnemyController(PlayerController playerController, SpatialHashGrid spatialHashGrid, IProjectileService projectileService)
    {
        _playerController = playerController;
        _spatialHashGrid = spatialHashGrid;
        _projectileService = projectileService;
        _neighborCacheList = new List<EnemyView>();
        _enemies = new List<EnemyView>();
    }

    public EnemyView Spawn(EnemyData data, Vector2 position)
    {
        return SpawnWithContext(data, position, new EnemySpawnContext(_playerController.PlayerPosition));
    }

    // Swarm
    public EnemyView SpawnStraight(EnemyData data, Vector2 position, Vector2 direction, float speed)
    {
        return SpawnWithContext(data, position, new EnemySpawnContext(_playerController.PlayerPosition, direction, speed));
    }

    private EnemyView SpawnWithContext(EnemyData data, Vector2 position, EnemySpawnContext context)
    {
        EnemyView enemyView = ObjectPoolingManager.Instance.SpawnObject<EnemyView>(data.Prefab, position, Quaternion.identity,
            ObjectPoolingManager.PoolType.Enemy);
        if (enemyView == null) return null;
        enemyView.Init(data, context);
        _enemies.Add(enemyView);
        return enemyView;
    }


    public void RecycleOutside(SpawnArea spawnArea, SpawnArea keepArea)
    {
        for (int i = _enemies.Count - 1; i >= 0; i--)
        {
            EnemyView enemy = _enemies[i];
            if (!enemy.IsAlive || keepArea.Contains(enemy.Position)) continue;

            if (!enemy.MovesStraight)
            {
                enemy.Teleport(spawnArea.OppositeEdgePoint(enemy.Position));
                continue;
            }
            Vector2 offset = enemy.Position - spawnArea.Center;
            bool passedPlayer = Vector2.Dot(offset, enemy.MoveDirection) > 0f;
            bool tooFar = offset.sqrMagnitude > (keepArea.HalfExtents * 2f).sqrMagnitude;
            if (passedPlayer || tooFar) DespawnStraight(i);
        }
    }

    public void DrawGizmos()
    {
        if(_spatialHashGrid == null) return;
        _spatialHashGrid.DrawGizmos();
    }
    
    public void Tick(float dt)
    {
        _spatialHashGrid.ClearBuckets();
        _deltaTime = dt;
        for (int i = _enemies.Count-1; i >=0;i--)
        {
            EnemyView enemy = _enemies[i];
            if (enemy.IsAlive) continue;
            EnemyDied?.Invoke(new EnemyDeathInfo(enemy.Model.Data, enemy.Position));
            RemoveAt(i);
        }

        foreach (var enemy in _enemies)
        {
            _spatialHashGrid.AddToCell(enemy);
        }
        //Nen tinh het overlapForce roi moi apply ?
        foreach(var enemy in _enemies)
        {
            _neighborCacheList.Clear();
            _spatialHashGrid.GetNeighbours(enemy,ref _neighborCacheList);
            enemy.Tick(_deltaTime,_neighborCacheList,_playerController.PlayerPosition);

            // I-frame cua player chan viec tru mau moi frame.
            if (enemy.IsAlive && CollisionMath.CircleOverlapsCircle(enemy.Position, enemy.Radius, _playerController.Position, _playerController.Radius))
            {
                _playerController.TakeDamage(new DamagingContext(enemy.ContactDamage, 0f));
            }

            if (enemy.IsAlive) enemy.RangedAttack?.Tick(_deltaTime, enemy, _playerController, _projectileService);
        }
        Debug.Log(ActiveCount);
    }
    
    private void DespawnStraight(int index)
    {
        _enemies[index].Model.MarkDespawned();
        RemoveAt(index);
    }
    
    private void RemoveAt(int index)
    {
        EnemyView enemy = _enemies[index];
        _enemies[index] = _enemies[^1];
        _enemies.RemoveAt(_enemies.Count - 1);
        ObjectPoolingManager.Instance.DespawnObject(enemy.gameObject, ObjectPoolingManager.PoolType.Enemy);
    }
}
