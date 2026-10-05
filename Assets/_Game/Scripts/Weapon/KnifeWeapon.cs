using System.Collections;
using UnityEngine;

public class KnifeWeapon : Weapon
{
    private KnifeData _knifeData;

    public KnifeWeapon(KnifeData data) : base(data)
    {
        _knifeData = data;
    }
    protected override int GetShotCount(PlayerStats playerStats) => GetProjectileCount(playerStats);
    protected override void FireShot(WeaponContext ctx,int shotIndex)
    {
        Vector2 dir = ctx.Direction.normalized;
        Vector3 perp = new Vector3(-dir.y, dir.x, 0f);
        Vector3 spawnPos = ctx.PlayerPosition + perp * Random.Range(-_knifeData.SideJitter, _knifeData.SideJitter);

        ProjectileSpawnInfo info = new ProjectileSpawnInfo(dir, spawnPos, BuildProjectileStats(ctx.PlayerStats));
        ctx.ProjectileService.Spawn<MovingProjectile>(_knifeData.Prefab, spawnPos, RotationFromDirection(dir), info);
    }
    
    private Quaternion RotationFromDirection(Vector2 direction)
    {
        float angle = Mathf.Atan2(direction.y, direction.x) * Mathf.Rad2Deg;
        return Quaternion.Euler(0f, 0f, angle -45); ///!!!
    }


}
