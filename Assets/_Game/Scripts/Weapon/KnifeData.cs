using UnityEngine;

[CreateAssetMenu(fileName = "KnifeData", menuName = "Scriptable Objects/Weapon/KnifeData")]
public class KnifeData : WeaponData
{
    [Header("Knife")] public float SpawnSpacing = 1f;
    public override Weapon CreateRunTime()
    {
        return new KnifeWeapon(this);
    }
    
    
    
}
