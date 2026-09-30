using System;
using UnityEngine;
using UnityEngine.InputSystem;
using Vector2 = UnityEngine.Vector2;

public class PlayerView : MonoBehaviour,IDamageable
{
    public Vector3 Position => transform.position;
    public Vector2 MoveDirection { get; private set; }
    public Vector2 LastMoveDirection { get; private set; }
    [SerializeField] private InputReader  _inputReader; //Later refactor
    private Vector2 currentVelocity;
    [SerializeField] private float moveSpeed = 5;
    public bool IsAlive { get; private set; }
    private Rigidbody2D _rigidbody2D;
    private Player _player;
    private PlayerStats Stats => _player.Stats;
    

    private void Awake()
    {
        _rigidbody2D = GetComponent<Rigidbody2D>();
        LastMoveDirection = Vector2.right;
    }
    
    public void InitStat(Player player)
    {
        _player = player;
        moveSpeed = Stats.SpeedRate*moveSpeed;
        IsAlive = true;
    }
    
    private void OnEnable()
    {
        _inputReader.OnMovePerformed += HandleMove;
        
    }

    private void OnDisable()
    {
        _inputReader.OnMovePerformed -= HandleMove;
    }
    
    private void FixedUpdate()
    {
        if (_rigidbody2D.linearVelocity != currentVelocity)
        {
            _rigidbody2D.linearVelocity = currentVelocity;
        }
    }

    public void TakeDamage(DamagingContext ctx,Action onDead = null)
    {
        if (!IsAlive) return;
        _player.CurrentHealth -= ctx.Damage; //Tru vao stast ????
        Debug.Log($"{gameObject.name} dealt {ctx.Damage} damage to {_player.CurrentHealth}");
        if(_player.CurrentHealth <= 0)
        {
            Debug.Log("Player is dead");
            IsAlive = false;
        }
    }

    private void HandleMove(Vector2 direction)
    {
        MoveDirection = new Vector2(direction.x, direction.y);
        if (MoveDirection.sqrMagnitude > 0.0001f)
        {
            LastMoveDirection = MoveDirection;  //!!!
        }
        //Debug.Log("LastMoveDirection:" + LastMoveDirection);
        currentVelocity = new Vector2(moveSpeed * MoveDirection.x, moveSpeed * MoveDirection.y);
    }
}
