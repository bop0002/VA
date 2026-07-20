using UnityEngine;

public class PlayerAnimator : MonoBehaviour
{
    PlayerMovement _playerMovement;
    Animator _animator;
    SpriteRenderer _spriteRenderer;

    private void Awake()
    {
        _playerMovement = GetComponent<PlayerMovement>();
        _animator = GetComponent<Animator>();
        _spriteRenderer = GetComponent<SpriteRenderer>();
    }

    private void Update()
    {
        if (_playerMovement.moveDirection.x != 0 || _playerMovement.moveDirection.y != 0)
        {
            _animator.SetBool("Move", true);
            CheckSpirteDirection();
        }
        else
        {
            _animator.SetBool("Move", false);
        }
    }
    
    private void CheckSpirteDirection()
    {
        if(_playerMovement.lastMoveDirection.x <0)
        {
            _spriteRenderer.flipX = true;
        }
        else
        {
            _spriteRenderer.flipX = false;
        }
        Debug.Log(_playerMovement.lastMoveDirection);
    }
    
}
