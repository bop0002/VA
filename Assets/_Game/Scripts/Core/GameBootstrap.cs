using System.Collections.Generic;
using UnityEngine;

public class GameBootstrap : MonoBehaviour
{
    [SerializeField] private PlayerView _playerView;
    [SerializeField] private InputReader _inputReader;

    //Temp before gameflow
    [SerializeField] private PlayerStats _playerStats;
    [SerializeField] private List<WeaponData>  startingWeapons;
    [SerializeField] private StageData _stage;
    [SerializeField] private Camera _camera;

    [SerializeField] private MapController _mapController;

    [SerializeField] private ObjectPoolingManager _objectPoolingManager;

    private EnemyController _enemyController;
    private EnemySpawner _enemySpawner;
    private PlayerController _playerController;
    private WeaponController _weaponController;
    private ProjectileController _projectileController;

    private SpatialHashGrid _spatialHashGrid;
    private int _killCount;

    private void Start() //Havent fixing poolingmanager
    {
        _spatialHashGrid = new SpatialHashGrid(1f);
        _playerController = new PlayerController(_playerView, _playerStats);
        _projectileController = new ProjectileController(
            new EnemyTargetQuery(_spatialHashGrid),
            new PlayerTargetQuery(_playerController));
        _weaponController = new WeaponController(_playerController, startingWeapons,_projectileController);
        _enemyController = new EnemyController(_playerController, _spatialHashGrid, _projectileController);
        _enemyController.EnemyDied += HandleEnemyDied;
        if (_camera == null) _camera = Camera.main;
        if (_stage != null) _enemySpawner = new EnemySpawner(_stage, _enemyController, _playerController, _camera);
        else Debug.LogError("GameBootstrap: chua gan StageData, spawner tat");
    }

    public void Update()
    {
        float dt = Time.deltaTime;
        _playerController.Tick(dt);
        _enemySpawner?.Tick(dt);
        _enemyController.Tick(dt);
        _weaponController.Tick(dt);
        _projectileController.Tick(dt);
    }

    private void OnDestroy()
    {
        if (_enemyController != null) _enemyController.EnemyDied -= HandleEnemyDied;
    }

    private void HandleEnemyDied(EnemyDeathInfo info)
    {
        _killCount++;
    }

    private void OnDrawGizmos() //temp
    {
        _enemyController?.DrawGizmos();
        _enemySpawner?.DrawGizmos();
    }

}
