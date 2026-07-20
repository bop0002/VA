using System.Collections.Generic;
using UnityEngine;

public class PropsRandomizer : MonoBehaviour
{
    [SerializeField] private List<GameObject> propSpawnPoints;
    [SerializeField] private List<GameObject> propPrefabs;

    private void Start()
    {
        RandomizeProps();
    }
    
    private void RandomizeProps()
    {
        foreach (var pos in propSpawnPoints)
        {
            int rand = Random.Range(0, propPrefabs.Count);
            GameObject props = Instantiate(propPrefabs[rand], pos.transform.position, Quaternion.identity);
            props.transform.SetParent(pos.transform);
        }
    }
    
}
