using System.Collections;
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

        ProjectileSpawnInfo info = new ProjectileSpawnInfo(ctx.Direction, ctx.PlayerPosition, stats);
        Quaternion rot = RotationFromDirection(ctx.Direction);

        for (int i = 0; i < count; i++)
        {
            Vector3 offset = (Vector3)(ctx.Direction.normalized * (i * _knifeData.SpawnSpacing));
            Vector3 spawnPos = ctx.PlayerPosition -  offset;

            Projectile projectile = ctx.ProjectileService.Spawn<MovingProjectile>(_knifeData.Prefab,spawnPos,rot,info);

            if (projectile == null) return;
        }
    }
    
    private IEnumerator FireBurstRoutine(WeaponContext ctx, int count, ProjectileStats stats)
    {
        Vector2 dir = ctx.Direction.normalized;
        Vector3 perp = new Vector3(-dir.y, dir.x, 0f);
        Quaternion rot = RotationFromDirection(dir);

        for (int i = 0; i < count; i++)
        {
            // Lệch nhẹ tay cầm sang trái/phải ngẫu nhiên để không bị đè hẳn lên nhau
            float slightOffset = Random.Range(-0.1f, 0.1f);
            Vector3 spawnPos = ctx.PlayerPosition + perp * slightOffset;

            ProjectileSpawnInfo info = new ProjectileSpawnInfo(dir, spawnPos, stats);
            ctx.ProjectileService.Spawn<MovingProjectile>(_knifeData.Prefab, spawnPos, rot, info);

            yield return new WaitForSeconds(0.06f);
        }
    }
    
    private Quaternion RotationFromDirection(Vector2 direction)
    {
        float angle = Mathf.Atan2(direction.y, direction.x) * Mathf.Rad2Deg;
        return Quaternion.Euler(0f, 0f, angle -45); ///!!!
    }


}
