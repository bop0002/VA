using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Pool;

public class ObjectPoolingManager : MonoBehaviour
{
    private Dictionary<GameObject, ObjectPool<GameObject>> _prefabs2Pool;
    private Dictionary<GameObject,GameObject> _instance2Prefabs;
    private GameObject _emptyHolder;
    private GameObject _tileMapHolder;
    private GameObject _propHolder;
    public static ObjectPoolingManager Instance { get; private set; }
    
    private void Awake()
    {

        if (Instance != null && Instance != this)
        {
            Destroy(gameObject);
            return;
        }

        Instance = this;
        
        _prefabs2Pool = new Dictionary<GameObject, ObjectPool<GameObject>>();
        _instance2Prefabs = new Dictionary<GameObject, GameObject>();
        SetUpEmpties();
        DontDestroyOnLoad(this);
    }
    
    public enum PoolType
    {
        TileMap,
        Prop
    }
    
    private void SetUpEmpties()
    {
        _emptyHolder = new GameObject("ObjectPool");
        
        _tileMapHolder = new GameObject("TileMap");
        _tileMapHolder.transform.SetParent(_emptyHolder.transform);
        
        _propHolder = new GameObject("Prop");
        _propHolder.transform.SetParent(_emptyHolder.transform);
        
        DontDestroyOnLoad(_tileMapHolder.transform.parent);
        
    }
    
    private void CreatePool(GameObject prefab,PoolType poolType)
    {
        ObjectPool<GameObject> pool = new ObjectPool<GameObject>(
            createFunc: () => CreateObject(prefab,poolType),
            actionOnGet : OnGetObject,
            actionOnRelease : OnReleaseObject,
            actionOnDestroy : OnDestroyObject);
        _prefabs2Pool.Add(prefab, pool);
    }

    private GameObject CreateObject(GameObject prefab,PoolType poolType)
    {
        GameObject obj = Instantiate(prefab, Vector3.zero, Quaternion.identity);
        obj.SetActive(false);
        obj.transform.SetParent(GetParentTransform(poolType).transform);
        return obj;
    }

    private void OnGetObject(GameObject obj)
    {
        
    }

    private void OnReleaseObject(GameObject obj)
    {
        obj.SetActive(false);
    }

    private void OnDestroyObject(GameObject obj)
    {
        if (_instance2Prefabs.ContainsKey(obj))
        {
            _instance2Prefabs.Remove(obj);
        }
    }

    private GameObject GetParentTransform(PoolType poolType) ///Refactor
    {
        switch(poolType)
        {
            case PoolType.TileMap:
                return _tileMapHolder;
                break;
            case PoolType.Prop:
                return _propHolder;
                break;
            default:
                return null;
                break;
        }
    }
    
    
    public T SpawnObject<T>(GameObject prefab, Vector3 pos, Quaternion rot,PoolType poolType) where T : Object
    {
        if (!_prefabs2Pool.ContainsKey(prefab))
        {
            CreatePool(prefab,poolType);
        }

        GameObject obj = _prefabs2Pool[prefab].Get();
        if (obj != null)
        {

            if (!_instance2Prefabs.ContainsKey(obj))
            {
                _instance2Prefabs.Add(obj, prefab);
            }
            
            obj.transform.position = pos;
            obj.transform.rotation = rot;
            obj.SetActive(true);

            if (typeof(T) == typeof(GameObject))
            {
                return obj as T;
            }
            
            T component = obj.GetComponent<T>();
            if (component == null)
            {
                Debug.LogError($"{obj.name} not have component of type {typeof(T)}");
                return null;
            }
            
            return component;
        }
        else return null;

    }
    
    public GameObject SpawnObject(GameObject prefab, Vector3 pos, Quaternion rot,PoolType poolType)
    {
        return SpawnObject<GameObject>(prefab, pos, rot, poolType);
    }

    public void DespawnObject(GameObject obj,PoolType poolType)
    {
        if (_instance2Prefabs.TryGetValue(obj, out GameObject prefab))
        {
            if (obj.transform.parent != GetParentTransform(poolType).transform)
            {
                obj.transform.SetParent(GetParentTransform(poolType).transform);
            }

            if (_prefabs2Pool.TryGetValue(prefab, out ObjectPool<GameObject> pool))
            {
                pool.Release(obj);
            }
            
        }
        else
        {
            Debug.LogError($"{obj.name} not have key in dict instance");
        }
    }
    
}
