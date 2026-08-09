using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Analytics;

public class EnemyController : MonoBehaviour
{
    [SerializeField] private  PlayerView _playerView;
    [SerializeField] private EnemyData _data; // temp;
    [SerializeField] private int testEnemySpawn;
    private List<EnemyView> _enemies;

    private void Start()
    {
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
    
    private void Update()
    {
        for (int i = 0; i < _enemies.Count; i++)
        {
            if (!_enemies[i].IsAlive)
            {
                _enemies.RemoveAt(i);
                continue;
            }
            else
            {
                _enemies[i].Tick(Time.deltaTime);
            }
        }
    }
}
