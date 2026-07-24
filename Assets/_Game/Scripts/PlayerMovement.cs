using System;
using UnityEngine;
using UnityEngine.InputSystem;

public class PlayerMovement : MonoBehaviour
{
    public Vector2 moveDirection { get; private set; }
    public Vector2 lastMoveDirection { get; private set; }
    
    [SerializeField] private InputReader  _inputReader; //Later refactor
    [SerializeField] private float moveSpeed;
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
            Vector2 tempVector = lastMoveDirection;
            tempVector.x = moveDirection.x;
            lastMoveDirection = tempVector;
        }

        if (moveDirection.y != 0)
        {
            Vector2 tempVector = lastMoveDirection;
            tempVector.y = moveDirection.y;
            lastMoveDirection = tempVector;
        }
        _rigidbody2D.linearVelocity = new Vector2(moveSpeed * moveDirection.x, moveSpeed * moveDirection.y);
    }
}
