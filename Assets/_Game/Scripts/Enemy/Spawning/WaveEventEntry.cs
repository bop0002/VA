using System;
using UnityEngine;

[Serializable]
public class WaveEventEntry
{
    public SpawnEventData Event;
    //Giay tinh tu dau wave
    public float Delay = 10f;
    //Xac suat moi lan kich hoat (roll rieng tung lan)
    [Range(0f, 1f)] public float Chance = 1f;
    //So lan lap them sau lan dau
    [Min(0)] public int Repeat = 0;
    //Giay giua cac lan lap
    public float RepeatInterval = 20f;
}
