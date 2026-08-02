using UnityEngine;

public class GarlickWeapon : Weapon
{
    private GarlickData _garlickData;

    public GarlickWeapon(GarlickData data) : base(data)
    {
        _garlickData = data;
    }

    protected override void Fire(WeaponContext ctx)
    {
        WeaponLevelStats weaponStats = Stats;
        PlayerStats playerStats = ctx.PlayerStats;
        
        ProjectileSpawnInfo info = new ProjectileSpawnInfo(ctx.Direction, Stats.Speed * playerStats.SpeedRate,
            Stats.Damage * playerStats.DamageRate,Stats.Pierce * playerStats.Pierce,Stats.Size * playerStats.ProjectileSize,Stats.Duration + playerStats.ProjectileDuration,ctx.Origin);
        int count = Stats.ProjectileCount + playerStats.ProjectileCount;
        Quaternion rot = Quaternion.Euler(0f, 0f, 0f);
        
        for (int i = 0; i < count; i++)
        {
            //Vector3 offset = (Vector3)(ctx.Direction.normalized * (i * _garlickData.SpawnSpacing));
            Vector3 spawnPos = ctx.Origin.position;
            
            CircleProjectile projectile = ObjectPoolingManager.Instance.SpawnObject<CircleProjectile>(Data.Prefab, spawnPos, rot,
                ObjectPoolingManager.PoolType.WeaponProjectile);

            if (projectile == null) return;
            
            projectile.Init(info);
        }
        
    }
}
