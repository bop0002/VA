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

    protected override void FireShot(WeaponContext ctx, int shotIndex)
    {
        if (_isInitialized) return; // aura chi spawn 1 lan, sau do tu bam theo owner
        ProjectileSpawnInfo info = new ProjectileSpawnInfo(ctx.Direction, BuildProjectileStats(ctx.PlayerStats), Team.Player, ctx.Owner);
        AuraProjectile projectile = ctx.ProjectileService.Spawn<AuraProjectile>(Data.Prefab, ctx.PlayerPosition, Quaternion.identity, info);
        if (projectile == null) return;
        _cirleProjectile = projectile;
        _isInitialized = true;
    }
}
