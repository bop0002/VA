using UnityEngine;

[CreateAssetMenu(fileName = "EnemyData", menuName = "Scriptable Objects/EnemyData")]
public class EnemyData : ScriptableObject
{
    [Header("Indentify")]
    public string Id;
    public string DisplayName;
    public Sprite Icon;
    
    [Header("Prefab")]
    public GameObject Prefab;

    public EnemyStats Stats;

    [Header("Attack")]
    public EnemyRangedAttackData RangedAttack; // null cx dc
}
