using UnityEngine;

public class RockWeapon : Weapon
{
    private RockData _rockData;

    public RockWeapon(RockData data) : base(data)
    {
        _rockData = data;
    }
    protected override int GetShotCount(PlayerStats playerStats) => GetProjectileCount(playerStats);
    protected override void FireShot(WeaponContext ctx,int shotIndex)
    {
        Vector2 dir = ctx.Direction.normalized;
        Vector3 perp = new Vector3(-dir.y, dir.x, 0f);
        Vector3 spawnPos = ctx.PlayerPosition + (Vector3)dir * _rockData.SpawnForward
                           + perp * Random.Range(-_rockData.SideJitter, _rockData.SideJitter);

        ProjectileSpawnInfo info = new ProjectileSpawnInfo(dir, BuildProjectileStats(ctx.PlayerStats), Team.Player, ctx.Owner);
        ctx.ProjectileService.Spawn<MovingProjectile>(_rockData.Prefab, spawnPos, RotationFromDirection(dir), info);
    }
    
    private Quaternion RotationFromDirection(Vector2 direction)
    {
        float angle = Mathf.Atan2(direction.y, direction.x) * Mathf.Rad2Deg;
        return Quaternion.Euler(0f, 0f, angle); // sprite ve huong sang phai
    }


}
