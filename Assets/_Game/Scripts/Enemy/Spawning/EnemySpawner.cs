using System.Collections.Generic;
using UnityEngine;


public class EnemySpawner
{
    private const float MinSpawnInterval = 0.05f; 

    private readonly StageData _stage;
    private readonly EnemyController _enemies;
    private readonly PlayerController _player;
    private readonly Camera _camera;

    private float _elapsed;
    private int _waveIndex = -1;
    private float _spawnTimer;
    private int _typeCursor;     
    private SpawnArea _lastArea;

    private struct EventTimer
    {
        public WaveEventEntry Entry;
        public float NextTime; 
        public int Remaining; 
    }

    private readonly List<EventTimer> _eventTimers = new List<EventTimer>();
    private float _waveStartTime;

    public int WaveIndex => _waveIndex;

    public EnemySpawner(StageData stage, EnemyController enemies, PlayerController player, Camera camera)
    {
        _stage = stage;
        _enemies = enemies;
        _player = player;
        _camera = camera;
        Prewarm();
    }

    private void Prewarm()
    {
        HashSet<GameObject> prefabs = new HashSet<GameObject>();
        foreach (var wave in _stage.Waves)
        {
            foreach (var data in wave.Enemies) if (data != null && data.Prefab != null) prefabs.Add(data.Prefab);
            foreach (var data in wave.Bosses) if (data != null && data.Prefab != null) prefabs.Add(data.Prefab);
            foreach (var entry in wave.Events)
            {
                if (entry.Event != null && entry.Event.Enemy != null && entry.Event.Enemy.Prefab != null)
                    prefabs.Add(entry.Event.Enemy.Prefab);
            }
        }

        foreach (var prefab in prefabs)
        {
            ObjectPoolingManager.Instance.Prewarm(prefab, _stage.PrewarmPerType, ObjectPoolingManager.PoolType.Enemy);
        }
    }

    public void Tick(float dt)
    {
        if (_stage.Waves.Count == 0 || !_player.IsAlive) return;
        _elapsed += dt;
        bool waveChanged = UpdateWave();

        WaveData wave = _stage.Waves[_waveIndex];
        SpawnArea area = CurrentSpawnArea();
        _lastArea = area;
        if (waveChanged)
        {
            SpawnBosses(wave, area);
            ScheduleEvents(wave);
        }
        TickEvents(area);
        _enemies.RecycleOutside(area, area.Expand(_stage.RecycleMargin));
        if (wave.Enemies.Count == 0) return;

        FillMinimum(wave, area);

        _spawnTimer -= dt;
        if (_spawnTimer > 0f) return;
        _spawnTimer += Mathf.Max(wave.SpawnInterval, MinSpawnInterval);
        foreach (var data in wave.Enemies)
        {
            if (!TrySpawn(data, area)) break;
        }
    }

    private bool UpdateWave()
    {
        int index = Mathf.Min((int)(_elapsed / Mathf.Max(_stage.WaveDuration, 1f)), _stage.Waves.Count - 1);
        if (index == _waveIndex) return false;
        _waveIndex = index;
        _waveStartTime = _elapsed;
        _spawnTimer = Mathf.Max(_stage.Waves[index].SpawnInterval, MinSpawnInterval);
        _typeCursor = 0;
        Debug.Log($"Wave {_waveIndex}"); // tmp, sau nay thay bang UI
        return true;
    }

    private void SpawnBosses(WaveData wave, SpawnArea area)
    {
        foreach (var data in wave.Bosses)
        {
            if (data != null) _enemies.Spawn(data, area.RandomPointOnEdge());
        }
    }

    private void ScheduleEvents(WaveData wave)
    {
        _eventTimers.Clear();
        foreach (var entry in wave.Events)
        {
            if (entry.Event == null) continue;
            _eventTimers.Add(new EventTimer { Entry = entry, NextTime = entry.Delay, Remaining = entry.Repeat + 1 });
        }
    }

    private void TickEvents(SpawnArea area)
    {
        float waveTime = _elapsed - _waveStartTime;
        for (int i = _eventTimers.Count - 1; i >= 0; i--)
        {
            EventTimer timer = _eventTimers[i];
            if (waveTime < timer.NextTime) continue;

            if (timer.Entry.Chance > 0f && Random.value <= timer.Entry.Chance)
            {
                timer.Entry.Event.Execute(_enemies, area);
            }
            timer.Remaining--;
            timer.NextTime += Mathf.Max(timer.Entry.RepeatInterval, MinSpawnInterval);

            if (timer.Remaining <= 0) _eventTimers.RemoveAt(i);
            else _eventTimers[i] = timer;
        }
    }

    private SpawnArea CurrentSpawnArea()
    {
        return new SpawnArea(_player.Position, SpawnArea.CameraHalfExtents(_camera)).Expand(_stage.SpawnMargin);
    }

    private void FillMinimum(WaveData wave, SpawnArea area)
    {
        int missing = wave.Minimum - _enemies.ActiveCount;
        for (int i = 0; i < missing; i++)
        {
            EnemyData data = wave.Enemies[_typeCursor % wave.Enemies.Count];
            _typeCursor++;
            if (!TrySpawn(data, area)) return;
        }
    }

    private bool TrySpawn(EnemyData data, SpawnArea area)
    {
        if (_enemies.ActiveCount >= _stage.MaxEnemies) return false;
        if (data == null) return true;
        _enemies.Spawn(data, area.RandomPointOnEdge());
        return true;
    }

    public void DrawGizmos()
    {
        _lastArea.DrawGizmos(Color.yellow);
        _lastArea.Expand(_stage != null ? _stage.RecycleMargin : 0f).DrawGizmos(new Color(1f, 0.5f, 0f));
    }
}
