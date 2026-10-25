using System;
using System.Collections.Generic;
using UnityEngine;

[Serializable]
public class WaveData
{
    //Tat ca enemy tren screen tinh den round nay minimum
    public int Minimum = 10;
    //Enemy per 
    public float SpawnInterval = 1f;
    public List<EnemyData> Enemies = new List<EnemyData>();
    
    //Per wave
    public List<EnemyData> Bosses = new List<EnemyData>();
    public List<WaveEventEntry> Events = new List<WaveEventEntry>();
}
