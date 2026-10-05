using UnityEngine;

[CreateAssetMenu(fileName = "KnifeData", menuName = "Scriptable Objects/Weapon/KnifeData")]
public class KnifeData : WeaponData
{
    [Header("Knife")] public float SideJitter = 0.3f;
    public override Weapon CreateRunTime()
    {
        return new KnifeWeapon(this);
    }
    
    
    
}
