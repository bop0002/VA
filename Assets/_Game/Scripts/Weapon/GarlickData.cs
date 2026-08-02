using UnityEngine;

[CreateAssetMenu(fileName = "GarlickData", menuName = "Scriptable Objects/Weapon/GarlickData")]
public class GarlickData : WeaponData
{
    public override Weapon CreateRunTime()
    {
        return new GarlickWeapon(this);
    }
}
