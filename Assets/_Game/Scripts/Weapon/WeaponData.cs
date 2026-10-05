using UnityEngine;

public abstract class WeaponData : ScriptableObject
{
    [Header("Indentify")]
    public string Id;
    public string DisplayName;
    public Sprite Icon;
    
    [Header("Prefab")]
    
    public GameObject Prefab;

    [Header("Levels")] 
    public WeaponLevelStats[] Levels = new WeaponLevelStats[1];
    public int MaxLevel => Levels.Length;
    [Header("Fire")]
    public float ProjectileInterval = 0f;
    public abstract Weapon CreateRunTime();

    private void OnValidate()
    {
        if (string.IsNullOrEmpty(Id)) Id = DisplayName;
    }

}
