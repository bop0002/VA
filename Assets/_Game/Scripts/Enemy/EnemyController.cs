using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Analytics;

public class EnemyController : MonoBehaviour
{
    [SerializeField] private  PlayerView _playerView;
    [SerializeField] private EnemyData _data; // temp;
    [SerializeField] private int testEnemySpawn;
    SpatialHashGrid _grid;
    private List<EnemyView> _enemies;

    private List<EnemyView> _neighborCacheList;
    private float _deltaTime;
    private void Start()
    {
        _grid = new SpatialHashGrid(1f);
        _neighborCacheList = new List<EnemyView>();
        _enemies = new List<EnemyView>();
        for (int i = 0; i < testEnemySpawn; i++)
        {
            TestInit();
        }
    }
    
    private void TestInit()
    {
        Vector3 pos = new Vector3(Random.Range(-10.0f, 10.0f), Random.Range(-10.0f, 10.0f));
        Quaternion rot = Quaternion.identity;
        EnemyView enemyView = ObjectPoolingManager.Instance.SpawnObject<EnemyView>(_data.Prefab, pos, rot,
            ObjectPoolingManager.PoolType.Enemy);
        EnemySpawnContext context = new EnemySpawnContext(_playerView.transform);
        enemyView.Init(_data, context);
        _enemies.Add(enemyView);
    }

    private void OnDrawGizmos()
    {
        if(_grid == null) return;
        _grid.DrawGizmos();
    }
    
    private void Update()
    {
        _grid.ClearBuckets();
        _deltaTime  = Time.deltaTime;
        for (int i = _enemies.Count-1; i >=0;i--)
        {
            if (!_enemies[i].IsAlive)
            {
                _enemies[i] =  _enemies[^1];
                _enemies.RemoveAt( _enemies.Count-1); //hoac la ban event ;
            }
        }

        foreach (var enemy in _enemies)
        {
            _neighborCacheList.Clear();
            _grid.AddToCell(enemy);
            _grid.GetNeighbours(enemy, ref _neighborCacheList);
            enemy.Tick(Time.deltaTime,_neighborCacheList);
        }
    }
}
