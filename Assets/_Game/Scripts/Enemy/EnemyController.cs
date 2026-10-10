using System.Collections.Generic;
using UnityEngine;

public class EnemyController 
{
    private PlayerController _playerController;
    private EnemyData _enemyData; // temp;
    private readonly EnemyData _shooterData; // temp
    private readonly IProjectileService _projectileService;
    private int _testEnemySpawn;
    SpatialHashGrid _spatialHashGrid;
    private List<EnemyView> _enemies;

    private List<EnemyView> _neighborCacheList; //Tam thoi work voi 1 cell size voi lon hon thi ko bic
    private float _deltaTime;

    public EnemyController(PlayerController playerController, EnemyData enemyData, EnemyData shooterData,
        SpatialHashGrid spatialHashGrid, IProjectileService projectileService, int testEnemySpawn, int testShooterSpawn)
    {
        _playerController = playerController;
        _enemyData = enemyData;
        _shooterData = shooterData;
        _spatialHashGrid = spatialHashGrid;
        _projectileService = projectileService;
        _neighborCacheList = new List<EnemyView>();
        _enemies = new List<EnemyView>();
        _testEnemySpawn = testEnemySpawn;
        for (int i = 0; i < _testEnemySpawn; i++) TestSpawn(_enemyData);
        if (_shooterData != null)
        {
            for (int i = 0; i < testShooterSpawn; i++) TestSpawn(_shooterData);
        }
    }
    
    private void TestSpawn(EnemyData data)
    {
        Vector3 pos = new Vector3(Random.Range(-10.0f, 10.0f), Random.Range(-10.0f, 10.0f));
        EnemyView enemyView = ObjectPoolingManager.Instance.SpawnObject<EnemyView>(data.Prefab, pos, Quaternion.identity,
            ObjectPoolingManager.PoolType.Enemy);
        enemyView.Init(data, new EnemySpawnContext(_playerController.PlayerPosition));
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

            // I-frame cua player chan viec tru mau moi frame.
            if (enemy.IsAlive && CollisionMath.CircleOverlapsCircle(enemy.Position, enemy.Radius, _playerController.Position, _playerController.Radius))
            {
                _playerController.TakeDamage(new DamagingContext(enemy.ContactDamage, 0f));
            }

            if (enemy.IsAlive) enemy.RangedAttack?.Tick(_deltaTime, enemy, _playerController, _projectileService);
        }
    }
}
