using System.Collections.Generic;
using UnityEngine;

[CreateAssetMenu(fileName = "StageData", menuName = "Scriptable Objects/StageData")]
public class StageData : ScriptableObject
{
    public float WaveDuration = 60f;
    public int MaxEnemies = 300;
    //Khoang cach ngoai mep camera de spawn"
    public float SpawnMargin = 1f;
    public float RecycleMargin = 3f;
    //Insatance tao san trong pool
    public int PrewarmPerType = 30;
    public List<WaveData> Waves = new List<WaveData>();
}
