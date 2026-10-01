using System.Collections.Generic;
using UnityEngine;


public interface IProjectileService
{
    public T Spawn<T>(GameObject prefab, Vector3 position, Quaternion rotation, ProjectileSpawnInfo spawnInfo) where T : Projectile;
}

public class ProjectileController : IProjectileService
{
    ISpatialGridQuery _spatialHashGrid;
    private List<Projectile> _projectiles;
    public ProjectileController(ISpatialGridQuery spatialGridQuery)
    {
        _spatialHashGrid = spatialGridQuery;
        _projectiles = new List<Projectile>();
    }

    public T Spawn<T>(GameObject prefab, Vector3 position, Quaternion rotation, ProjectileSpawnInfo spawnInfo) where T : Projectile
    {
        T projectile = ObjectPoolingManager.Instance.SpawnObject<T>(prefab, position, rotation, ObjectPoolingManager.PoolType.WeaponProjectile);
        if(projectile==null) return null;
        
        projectile.Init(spawnInfo);
        _projectiles.Add(projectile);
        return projectile;
    }

    public void Tick(float dt,Vector3 position)
    {
        ProjectileTickContext tickContext = new ProjectileTickContext(position, _spatialHashGrid);
        foreach (Projectile projectile in _projectiles)
        {
            projectile.Tick(dt,tickContext);
        }

        for (int i = _projectiles.Count - 1; i >= 0; i--)
        {
            Projectile dead = _projectiles[i];
            if (!dead.IsAlive)
            {
                _projectiles[i] = _projectiles[^1];
                _projectiles.RemoveAt(_projectiles.Count-1);
                ObjectPoolingManager.Instance.DespawnObject(dead.gameObject,ObjectPoolingManager.PoolType.WeaponProjectile);
            }
        }
    }
    
}
