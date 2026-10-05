using UnityEngine;

public class MagicWandWeapon : Weapon
{
    private MagicWandWeaponData _magicWandData;
    public MagicWandWeapon(MagicWandWeaponData data) : base(data)
    {
        _magicWandData = data;
    }

    
    protected override int GetShotCount(PlayerStats playerStats) => GetProjectileCount(playerStats);

    protected override void FireShot(WeaponContext ctx, int shotIndex)
    {
        ProjectileSpawnInfo info = new ProjectileSpawnInfo(ctx.Direction, ctx.PlayerPosition, BuildProjectileStats(ctx.PlayerStats));
        ctx.ProjectileService.Spawn<HomingProjectile>(_magicWandData.Prefab, ctx.PlayerPosition, RotationFromDirection(ctx.Direction), info);
    }

    private Quaternion RotationFromDirection(Vector2 direction)
    {
        float angle = Mathf.Atan2(direction.y, direction.x) * Mathf.Rad2Deg;
        return Quaternion.Euler(0f, 0f, angle -45); ///!!!
    }

}
