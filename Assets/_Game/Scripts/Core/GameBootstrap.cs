using System.Collections.Generic;
using UnityEditor;
using UnityEngine;

public class GameBootstrap : MonoBehaviour
{
    [SerializeField] private PlayerView _playerView;
    [SerializeField] private InputReader _inputReader;
    
    //Temp final before gameflow
    [SerializeField] private PlayerStats _playerStats;
    [SerializeField] private List<WeaponData>  startingWeapons;
    [SerializeField] private EnemyData _data; 
    [SerializeField] private int _testEnemySpawn;
    
    [SerializeField] private MapController _mapController;

    [SerializeField] private ObjectPoolingManager _objectPoolingManager;
    
    private EnemyController _enemyController;
    private PlayerController _playerController;
    private WeaponController _weaponController;
    private ProjectileController _projectileController;
    
    private SpatialHashGrid _spatialHashGrid;
    
    private void Start() //Havent fixing poolingmanager
    {
        _spatialHashGrid = new SpatialHashGrid(1f);
        _playerController = new PlayerController(_playerView, _playerStats);
        _weaponController = new WeaponController(_playerController, startingWeapons);
        _enemyController = new EnemyController(_playerController, _data, _spatialHashGrid,_testEnemySpawn);
    }
    
    public void Update()
    {
        _playerController.Tick(Time.deltaTime);
        _weaponController.Tick(Time.deltaTime);
        _enemyController.Tick(Time.deltaTime);
    }

    private void OnDrawGizmos() //temp
    {
        _enemyController?.DrawGizmos();
    }
    
}
