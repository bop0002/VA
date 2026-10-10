using UnityEngine;

[CreateAssetMenu(fileName = "EnemyRangedAttack", menuName = "Scriptable Objects/EnemyRangedAttack")]
public class EnemyRangedAttackData : ScriptableObject
{
    [Header("Projectile")]
    public GameObject ProjectilePrefab;
    public float Speed = 6f;
    public float Damage = 5f;
    public float Size = 1f;
    public float Duration = 4f;
    public int Pierce = 1;

    [Header("Fire")]
    public float Range = 8f;
    public float Cooldown = 2f;
    public int ShotCount = 1;
    public float ShotInterval = 0.15f;
    public float SpreadAngle = 0f;

    public ProjectileStats BuildStats() => new ProjectileStats(Speed, Damage, Pierce, Size, Duration, 0f, 0f);
}
