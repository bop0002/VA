using System.Collections.Generic;
using UnityEngine;

public class WeaponController
{
    private PlayerController _playerController;
    private List<WeaponData>  _startingWeapons;
    private List<Weapon> _weapons = new List<Weapon>();

    private Player _player;
    private bool _initialized = false;
    private IProjectileService _projectileService;
    public IReadOnlyList<Weapon> Weapons => _weapons; //???

    public WeaponController(PlayerController playerController, List<WeaponData> startingWeapons,IProjectileService projectileService)
    {
        _playerController = playerController;
        _startingWeapons = startingWeapons;
        _projectileService = projectileService;
        Init(_playerController.GetPlayer());
    }
    
    public void Init(Player owner)
    {
        _player = owner;
        _weapons.Clear();
        foreach (WeaponData data in _startingWeapons)
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
    
    public void Tick(float dt)
    {
        if (!_initialized)
        {
            return;
        }
        WeaponContext ctx = new WeaponContext(_playerController.PlayerPosition,_playerController.LastMoveDirection,_player.Stats,_projectileService);
        float deltaTime = dt;
        for (int i = 0; i < _weapons.Count; i++)
        {
            _weapons[i].Tick(deltaTime,ctx);
        }
    }
}
