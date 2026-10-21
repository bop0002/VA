using UnityEngine;
[CreateAssetMenu(fileName = "FireBallData", menuName = "Scriptable Objects/Weapon/FireBallData")]
public class FireBallData : WeaponData
{
    [Header("FireBall")] public float SpawnForward = 0f; // khoang cach tu tam player toi diem spawn, theo huong ban
    public override Weapon CreateRunTime()
    {
        return new FireBallWeapon(this);
    }
}
