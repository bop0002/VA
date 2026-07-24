using System;
using System.Collections.Generic;
using UnityEngine;
using Random = UnityEngine.Random;

public class MapController : MonoBehaviour
{
    [SerializeField] private List<GameObject> chunkPrefabs; ///Later refactor
    [SerializeField] private PlayerMovement playerMovement; ///Later refactor
    [SerializeField] private ObjectPoolingManager  objectPoolingManager;
    
    private Dictionary<GridPosition,ChunkView> _activeGridPositions;
    private List<GridPosition> _removeList;
    private readonly int viewDistance = 1;
    private readonly int despawnBuffer = 1;
    private GridPosition _playerLastPos =  new GridPosition(int.MinValue,int.MinValue);
    private int worldSeed;
    ///Later refactor

    private void Start()
    {
        Init();
    }

    private void Update()
    {
        GridPosition playerGridPos = GridPositionExtensions.WorldToGrid(playerMovement.transform.position);
        if(playerGridPos != _playerLastPos) ChunkChecker();
        _playerLastPos = playerGridPos;
    }
    
    private void Init()
    {
        _removeList = new List<GridPosition>();
        _activeGridPositions = new Dictionary<GridPosition, ChunkView>();
        worldSeed = Random.Range(int.MinValue, int.MaxValue);
    }

    private void ChunkChecker()
    {
        _removeList.Clear();
        GridPosition playerGridPos = GridPositionExtensions.WorldToGrid(playerMovement.transform.position);
        for (int i = -viewDistance; i <= viewDistance; i++)
        {
            for(int j = -viewDistance;j <=viewDistance ;j++)
            {
                GridPosition tempGridPos = playerGridPos + new GridPosition(j, i);
                if (!_activeGridPositions.ContainsKey(tempGridPos))
                {
                    SpawnChunk(tempGridPos);
                }
            }
        }

        foreach (var tmp in _activeGridPositions)
        {
            if(Mathf.Abs(tmp.Key.X - playerGridPos.X) > viewDistance + despawnBuffer || Mathf.Abs(tmp.Key.Y - playerGridPos.Y) > viewDistance + despawnBuffer)
            {
                DespawnChunk(tmp.Value);
                _removeList.Add(tmp.Key);
            }
        }
        
        foreach (var tmp in _removeList)
        {
            _activeGridPositions.Remove(tmp);
        }
    }
    
    private void SpawnChunk(GridPosition spawnPosition)
    {
        Vector3 worldSpawnPos = GridPositionExtensions.GridToWorld(spawnPosition);
        int prefabIndex = CalculatePrefabIndex(spawnPosition);
        ChunkView obj = objectPoolingManager.SpawnObject<ChunkView>(chunkPrefabs[prefabIndex], worldSpawnPos, Quaternion.identity,ObjectPoolingManager.PoolType.TileMap);
        obj.InitProps(worldSeed,spawnPosition);
        _activeGridPositions.Add(spawnPosition,obj);
    }

    private void DespawnChunk(ChunkView obj)
    {
        obj.ClearProp();
        objectPoolingManager.DespawnObject(obj.gameObject, ObjectPoolingManager.PoolType.TileMap);
    }
    
    
    private int CalculatePrefabIndex(GridPosition pos)
    {
        int hash = pos.X * 73856093 ^ pos.Y * 19349663 ^ worldSeed * 83492791;
        
        if (chunkPrefabs == null || chunkPrefabs.Count == 0)
        {
            Debug.LogError("No chunk prefab found");
            return 0;
        }
        int index = (hash & 0X7FFFFFFF) % chunkPrefabs.Count;
        
        return index;
    }
    
    

    
}
