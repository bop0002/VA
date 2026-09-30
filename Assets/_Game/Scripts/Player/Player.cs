using UnityEngine;

public class Player
{
    public PlayerStats Stats { get; private set; }
    public float CurrentHealth;
    public Player(PlayerStats stats)
    {
        CurrentHealth =  stats.Health;
        Stats = stats;    
    }
    
}
