using UnityEngine;

public class Player
{
    public PlayerStats Stats { get; private set; }
    public float MaxHealth { get; private set; }
    public float CurrentHealth { get; private set; }
    public bool IsAlive => CurrentHealth > 0f;

    public Player(PlayerStats stats)
    {
        Stats = stats;
        MaxHealth = stats.Health;
        CurrentHealth = MaxHealth;
    }
    
    public float ApplyDamage(float damage)
    {
        if (!IsAlive) return 0f;
        float taken = Mathf.Max(0f, damage - Stats.Armor);
        CurrentHealth = Mathf.Max(0f, CurrentHealth - taken);
        return taken;
    }
}
