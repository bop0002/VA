using UnityEngine;

public class MagicWandWeapon : Weapon
{
    private MagicWandWeaponData _magicWandData;
    public MagicWandWeapon(MagicWandWeaponData data) : base(data)
    {
        _magicWandData = data;
    }

    
    protected override void Fire(WeaponContext ctx)
    {
        ProjectileStats stats = BuildProjectileStats(ctx.PlayerStats);
        int count = GetProjectileCount(ctx.PlayerStats);

        ProjectileSpawnInfo info = new ProjectileSpawnInfo(ctx.Direction, ctx.PlayerPosition, stats);
        Quaternion rot = RotationFromDirection(ctx.Direction);

        for (int i = 0; i < count; i++)
        {
            Vector3 spawnPos = ctx.PlayerPosition;//de tam :3

            HomingProjectile projectile = ObjectPoolingManager.Instance.SpawnObject<HomingProjectile>(Data.Prefab, spawnPos, rot,
                ObjectPoolingManager.PoolType.WeaponProjectile);

            if (projectile == null) return;

            projectile.Init(info);
        }
    }

    private Quaternion RotationFromDirection(Vector2 direction)
    {
        float angle = Mathf.Atan2(direction.y, direction.x) * Mathf.Rad2Deg;
        return Quaternion.Euler(0f, 0f, angle -45); ///!!!
    }

}
