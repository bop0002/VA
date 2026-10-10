using System;
using UnityEngine;

public class PlayerController : ITargetable
{
    private PlayerView _playerView;
    private PlayerStats _playerStats;
    private Player _player;
    private float _invulnerableTimer;

    public Vector3 PlayerPosition { get; private set; }
    public Vector3 LastMoveDirection { get; private set; }

    // ITargetable
    public Vector2 Position => PlayerPosition;
    public float Radius => _playerStats.BodyRadius;
    public bool IsAlive => _player.IsAlive;

    public PlayerController(PlayerView playerView, PlayerStats playerStats)
    {
        _playerStats = playerStats;
        _player = new Player(playerStats);
        _playerView = playerView;
        playerView.InitStat(_player);
        PlayerPosition = playerView.Position;
    }

    public void Tick(float dt)
    {
        PlayerPosition = _playerView.Position;
        LastMoveDirection = _playerView.LastMoveDirection;
        if (_invulnerableTimer > 0f) _invulnerableTimer -= dt;
    }

    public void TakeDamage(DamagingContext ctx, Action onDead = null)
    {
        if (!IsAlive || _invulnerableTimer > 0f) return; //iframe
        float taken = _player.ApplyDamage(ctx.Damage);
        _invulnerableTimer = _playerStats.HitInvulnerability;
        _playerView.PlayHitFeedback();
        Debug.Log($"Player -{taken} hp, con {_player.CurrentHealth}"); // tmp

        if (!IsAlive)
        {
            _playerView.PlayDeath();
            onDead?.Invoke();
        }
    }

    public Player GetPlayer() => _player;
}
