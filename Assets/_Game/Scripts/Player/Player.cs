using UnityEngine;

public class Player
{
    public PlayerStats Stats { get; private set; }

    public Player(PlayerStats stats)
    {
        Stats = stats;    
    }
    
}
