using System.Collections.Generic;
using TMPro;
using UnityEngine;

public class EnemyController 
{
    private PlayerController _playerController;
    private EnemyData _enemyData; // temp;
    private int _testEnemySpawn;
    SpatialHashGrid _spatialHashGrid;
    private List<EnemyView> _enemies;

    private List<EnemyView> _neighborCacheList; //Tam thoi work voi 1 cell size voi lon hon thi ko bic
    private float _deltaTime;

    public EnemyController(PlayerController playerController,EnemyData enemyData,SpatialHashGrid spatialHashGrid,int testEnemySpawn)
    {
        _playerController = playerController;
        _enemyData = enemyData;
        _spatialHashGrid = spatialHashGrid;
        _neighborCacheList = new List<EnemyView>();
        _enemies = new List<EnemyView>();
        _testEnemySpawn = testEnemySpawn;
        for (int i = 0; i < _testEnemySpawn; i++)
        {
            TestSpawn();
        }
    }
    
    private void TestSpawn()
    {
        Vector3 pos = new Vector3(Random.Range(-10.0f, 10.0f), Random.Range(-10.0f, 10.0f));
        Quaternion rot = Quaternion.identity;
        EnemyView enemyView = ObjectPoolingManager.Instance.SpawnObject<EnemyView>(_enemyData.Prefab, pos, rot,
            ObjectPoolingManager.PoolType.Enemy);
        EnemySpawnContext context = new EnemySpawnContext(_playerController.PlayerPosition);
        enemyView.Init(_enemyData, context);
        _enemies.Add(enemyView);
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
            if (!enemy.IsAlive)
            {
                _enemies[i] =  _enemies[^1];
                _enemies.RemoveAt( _enemies.Count-1); //hoac la ban event ;
                ObjectPoolingManager.Instance.DespawnObject(enemy.gameObject,ObjectPoolingManager.PoolType.Enemy);
            }
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
        }
    }
}
