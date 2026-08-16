using UnityEngine;

public class KnifeWeapon : Weapon
{
    private KnifeData _knifeData;

    public KnifeWeapon(KnifeData data) : base(data)
    {
        _knifeData = data;
    }

    protected override void Fire(WeaponContext ctx)
    {
        ProjectileStats stats = BuildProjectileStats(ctx.PlayerStats);
        int count = GetProjectileCount(ctx.PlayerStats);

        ProjectileSpawnInfo info = new ProjectileSpawnInfo(ctx.Direction, ctx.Origin, stats);
        Quaternion rot = RotationFromDirection(ctx.Direction);

        for (int i = 0; i < count; i++)
        {
            Vector3 offset = (Vector3)(ctx.Direction.normalized * (i * _knifeData.SpawnSpacing));
            Vector3 spawnPos = ctx.Origin.position -  offset;

            MovingProjectile projectile = ObjectPoolingManager.Instance.SpawnObject<MovingProjectile>(Data.Prefab, spawnPos, rot,
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
