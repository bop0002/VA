using System;
using System.Collections;
using UnityEngine;
using UnityEngine.InputSystem;
using Vector2 = UnityEngine.Vector2;

public class PlayerView : MonoBehaviour
{
    public Vector3 Position => transform.position;
    public Vector2 MoveDirection { get; private set; }
    public Vector2 LastMoveDirection { get; private set; }
    [SerializeField] private InputReader  _inputReader; //Later refactor
    private Vector2 currentVelocity;
    [SerializeField] private float moveSpeed = 5;
    private Rigidbody2D _rigidbody2D;
    private Player _player;
    private PlayerStats Stats => _player.Stats;

    [SerializeField] private float _hitFlashDuration = 0.1f;
    private SpriteRenderer _renderer;
    private Coroutine _hitFlash;
    

    private void Awake()
    {
        _rigidbody2D = GetComponent<Rigidbody2D>();
        _renderer = GetComponent<SpriteRenderer>();
        LastMoveDirection = Vector2.right;
    }
    
    public void InitStat(Player player)
    {
        _player = player;
        moveSpeed = Stats.SpeedRate*moveSpeed;
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

    public void PlayHitFeedback()
    {
        if (_hitFlash != null) StopCoroutine(_hitFlash);
        _hitFlash = StartCoroutine(HitFlashRoutine());
    }

    private IEnumerator HitFlashRoutine()
    {
        _renderer.color = Color.red;
        yield return new WaitForSeconds(_hitFlashDuration);
        _renderer.color = Color.white;
        _hitFlash = null;
    }

    public void PlayDeath()
    {
        _inputReader.OnMovePerformed -= HandleMove; // chet thi het nhan input
        MoveDirection = Vector2.zero;
        currentVelocity = Vector2.zero;
        Debug.Log("Player is ded");
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
