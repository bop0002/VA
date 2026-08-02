using System;
using System.Numerics;
using UnityEngine;
using UnityEngine.InputSystem;
using Vector2 = UnityEngine.Vector2;

public class PlayerView : MonoBehaviour
{
    public Vector2 moveDirection { get; private set; }
    public Vector2 lastMoveDirection { get; private set; }
    
    [SerializeField] private InputReader  _inputReader; //Later refactor
    private Vector2 currentVelocity;
    [SerializeField] private float moveSpeed = 10;
    private Rigidbody2D _rigidbody2D;

    private void Awake()
    {
        _rigidbody2D = GetComponent<Rigidbody2D>();
        lastMoveDirection = Vector2.right;
    }
    
    public void InitStat(float speedRate)
    {
        moveSpeed = speedRate * moveSpeed;
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
    
    private void HandleMove(Vector2 direction)
    {
        moveDirection = new Vector2(direction.x, direction.y);
        if (moveDirection.sqrMagnitude > 0.0001f)
        {
            lastMoveDirection = moveDirection;  //!!!
        }
        Debug.Log("lastMoveDirection:" + lastMoveDirection);
        currentVelocity = new Vector2(moveSpeed * moveDirection.x, moveSpeed * moveDirection.y);
    }
}
