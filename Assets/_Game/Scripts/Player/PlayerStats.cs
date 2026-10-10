using UnityEngine;

[CreateAssetMenu(fileName = "PlayerStats", menuName = "Scriptable Objects/PlayerStats")]
public class PlayerStats : ScriptableObject
{
    public float SpeedRate;
    public float DamageRate;
    public int Pierce;
    public int ProjectileCount;
    public float Health;
    public float ProjectileSpeedRate;
    public float Armor;
    public float ProjectileSize;
    public float ProjectileDuration;
    public float CooldownRate;
    public float HealthRegenRate;
    public float ExperienceGainRate;
    public float BodyRadius = 0.4f;          
    public float HitInvulnerability = 0.5f;  
}
