using UnityEngine;

public class PlayerController : MonoBehaviour
{
    [SerializeField] private PlayerView playerView;

    [SerializeField] private WeaponController weaponController;
    [SerializeField] private PlayerStats playerStats;
    private Player _player;
    private void Awake()
    {

        _player = new Player(playerStats);
        playerView.InitStat(_player);
        weaponController.Init(_player);
    }

    // Update is called once per frame
    private void Update()
    {
        
    }
}
