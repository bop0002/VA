using UnityEngine;

public class FireBallWeapon : Weapon
{
    private FireBallData _fireBallData;
    public FireBallWeapon(FireBallData data) : base(data)
    {
        _fireBallData = data;
    }

    
    protected override int GetShotCount(PlayerStats playerStats) => GetProjectileCount(playerStats);

    protected override void FireShot(WeaponContext ctx, int shotIndex)
    {
        ProjectileSpawnInfo info = new ProjectileSpawnInfo(ctx.Direction, BuildProjectileStats(ctx.PlayerStats), Team.Player, ctx.Owner);
        Vector3 spawnPos = ctx.PlayerPosition + (Vector3)ctx.Direction.normalized * _fireBallData.SpawnForward;
        ctx.ProjectileService.Spawn<HomingProjectile>(_fireBallData.Prefab, spawnPos, RotationFromDirection(ctx.Direction), info);
    }

    private Quaternion RotationFromDirection(Vector2 direction)
    {
        float angle = Mathf.Atan2(direction.y, direction.x) * Mathf.Rad2Deg;
        return Quaternion.Euler(0f, 0f, angle); // sprite ve huong sang phai
    }

}
