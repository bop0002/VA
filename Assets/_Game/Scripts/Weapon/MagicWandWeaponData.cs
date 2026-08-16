using UnityEngine;
[CreateAssetMenu(fileName = "MagicWandData", menuName = "Scriptable Objects/Weapon/MagicWandData")]
public class MagicWandWeaponData : WeaponData
{
    public override Weapon CreateRunTime()
    {
        return new MagicWandWeapon(this);
    }
}
