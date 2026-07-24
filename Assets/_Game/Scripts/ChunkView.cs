using UnityEngine;
using System.Collections.Generic;
public class ChunkView : MonoBehaviour
{
    [SerializeField] private List<GameObject> propSpawnPoints;
    [SerializeField] private List<GameObject> propPrefabs;
    private List<GameObject> _props;
    
    private void Awake()
    {
        _props = new List<GameObject>();
    }
    
    public void InitProps(int seed,GridPosition pos)
    {
        ClearProp();

        int rand;
        int salt;
        GameObject spawnPoint;
        for (int i = 0; i < propSpawnPoints.Count; i++)
        {
            spawnPoint = propSpawnPoints[i].gameObject;
            salt = (i + 1) * 48618773;
            rand = CalculatePropIndex(seed, salt,pos);
            GameObject props = ObjectPoolingManager.Instance.SpawnObject(propPrefabs[rand],spawnPoint.transform.position, Quaternion.identity,ObjectPoolingManager.PoolType.Prop);
            _props.Add(props);
            props.transform.SetParent(spawnPoint.transform);
        }
    }
    
    private int CalculatePropIndex(int worldSeed,int salt,GridPosition pos)
    {

        int res;
        if (propPrefabs == null || propPrefabs.Count == 0)
        {
            Debug.LogError("No chunk prefab found");
            return 0;
        }
        int hash = pos.X * 73856093 ^ pos.Y * 19349663 ^ worldSeed * 83492791 ^ salt;
        
        res = (hash & 0x7FFFFFFF) % propPrefabs.Count;

        return res;
    }
    
    public void ClearProp()
    {
        foreach (var obj in _props)
        {
            if (obj != null)
            {
                ObjectPoolingManager.Instance.DespawnObject(obj,ObjectPoolingManager.PoolType.Prop);
            }
        }
        _props.Clear();
    }
}
