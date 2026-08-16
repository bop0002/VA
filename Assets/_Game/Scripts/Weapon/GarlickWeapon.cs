using UnityEngine;

public class GarlickWeapon : Weapon
{
    private GarlickData _garlickData;
    private AuraProjectile _cirleProjectile;
    private bool _isInitialized;
    public GarlickWeapon(GarlickData data) : base(data)
    {
        _garlickData = data;
        _isInitialized = false;
    }

    protected override void Fire(WeaponContext ctx)
    {
        if (_isInitialized) return;
        ProjectileStats stats = BuildProjectileStats(ctx.PlayerStats);
        ProjectileSpawnInfo info = new ProjectileSpawnInfo(ctx.Direction, ctx.Origin, stats);
        Quaternion rot = Quaternion.Euler(0f, 0f, 0f);
        
        if (!_isInitialized)
        {
            Vector3 spawnPos = ctx.Origin.position;
            
            AuraProjectile projectile = ObjectPoolingManager.Instance.SpawnObject<AuraProjectile>(Data.Prefab, spawnPos, rot,
                ObjectPoolingManager.PoolType.WeaponProjectile);
                        
            _cirleProjectile = projectile;
            _cirleProjectile.Init(info);
            _isInitialized = true;
        }
    }
}
