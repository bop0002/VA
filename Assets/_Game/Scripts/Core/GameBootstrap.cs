using System.Collections.Generic;
using UnityEngine;

public class GameBootstrap : MonoBehaviour
{
    [SerializeField] private PlayerView _playerView;
    [SerializeField] private InputReader _inputReader;
    
    //Temp before gameflow
    [SerializeField] private PlayerStats _playerStats;
    [SerializeField] private List<WeaponData>  startingWeapons;
    [SerializeField] private EnemyData _data; 
    [SerializeField] private EnemyData _shooterData;
    [SerializeField] private int _testShooterSpawn;
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
        _projectileController = new ProjectileController(
            new EnemyTargetQuery(_spatialHashGrid),
            new PlayerTargetQuery(_playerController));
        _weaponController = new WeaponController(_playerController, startingWeapons,_projectileController);
        _enemyController = new EnemyController(_playerController, _data, _shooterData, _spatialHashGrid, _projectileController, _testEnemySpawn, _testShooterSpawn);
    }
    
    public void Update()
    {
        float dt = Time.deltaTime;
        _playerController.Tick(dt);
        _enemyController.Tick(dt);
        _weaponController.Tick(dt);
        _projectileController.Tick(dt);
    }

    private void OnDrawGizmos() //temp
    {
        _enemyController?.DrawGizmos();
    }
    
}
