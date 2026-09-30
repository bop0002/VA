using UnityEngine;

public class PlayerController
{
    private PlayerView _playerView;
    private PlayerStats _playerStats;
    private Player _player;
    
    public Vector3 PlayerPosition { get; private set; }
    public Vector3 LastMoveDirection { get; private set; }
    public PlayerController(PlayerView playerView, PlayerStats playerStats)
    {
        _player = new Player(playerStats);
        _playerView = playerView;
        playerView.InitStat(_player);
    }

    public void Tick(float dt)
    {
        PlayerPosition = _playerView.Position;
        LastMoveDirection =_playerView.LastMoveDirection;
    }

    public Player GetPlayer() =>  _player;

}
