using System;
using UnityEngine;
using UnityEngine.InputSystem;

public class PlayerMovement : MonoBehaviour
{
    public float moveSpeed;
    public Vector2 moveDirection;
    public Vector2 lastMoveDirection;
    
    [SerializeField] private InputReader  _inputReader;
    private Rigidbody2D _rigidbody2D;

    private void Awake()
    {
        _rigidbody2D = GetComponent<Rigidbody2D>();
    }
    
    private void OnEnable()
    {
        _inputReader.OnMovePerformed += HandleMove;
    }

    private void OnDisable()
    {
        _inputReader.OnMovePerformed -= HandleMove;
    }
    
    private void HandleMove(Vector2 direction)
    {
        moveDirection = new Vector2(direction.x, direction.y).normalized;
        if (moveDirection.x != 0)
        {
            lastMoveDirection.x = moveDirection.x;
        }

        if (moveDirection.y != 0)
        {
            lastMoveDirection.y = moveDirection.y;
        }
        _rigidbody2D.linearVelocity = new Vector2(moveSpeed * moveDirection.x, moveSpeed * moveDirection.y);
    }
}
