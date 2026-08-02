using System.Collections.Generic;
using UnityEngine;

public class WeaponController : MonoBehaviour
{
    [SerializeField] private PlayerView _playerView;
    [SerializeField] private List<WeaponData>  startingWeapons;
    private List<Weapon> _weapons = new List<Weapon>();

    private Player _player;
    private bool _initialized = false;
    
    public IReadOnlyList<Weapon> Weapons => _weapons; //???

    public void Init(Player owner)
    {
        _player = owner;
        _weapons.Clear();
        foreach (WeaponData data in startingWeapons)
        {
            if (data != null) Acquire(data);
        }

        _initialized = true;
    }

    private void Acquire(WeaponData data)
    {
        Weapon exiting = _weapons.Find(w=>w.Id==data.Id);
        if (exiting != null)
        {
            exiting.TryLevelUp();
            return;
        }
        _weapons.Add(data.CreateRunTime());
    }
    
    void Update()
    {
        if (!_initialized)
        {
            return;
        }
        WeaponContext ctx = new WeaponContext(_playerView.transform, _playerView.lastMoveDirection,_player.Stats);
        float deltaTime = Time.deltaTime;
        for (int i = 0; i < _weapons.Count; i++)
        {
            _weapons[i].Tick(deltaTime,ctx);
        }
    }
}
