using UnityEngine;

[CreateAssetMenu(fileName = "RockData", menuName = "Scriptable Objects/Weapon/RockData")]
public class RockData : WeaponData
{
    [Header("Rock")] public float SideJitter = 0.3f;
    public float SpawnForward = 0f; // khoang cach tu tam player toi diem spawn, theo huong ban
    public override Weapon CreateRunTime()
    {
        return new RockWeapon(this);
    }
    
    
    
}
