using UnityEngine;

public class PlayerAnimator : MonoBehaviour
{
    private PlayerView _playerView;
    private Animator _animator;
    private SpriteRenderer _spriteRenderer;

    private void Awake()
    {
        _playerView = GetComponent<PlayerView>();
        _animator = GetComponent<Animator>();
        _spriteRenderer = GetComponent<SpriteRenderer>();
    }

    private void Update()
    {
        if (_playerView.moveDirection.x != 0 || _playerView.moveDirection.y != 0)
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
        if(_playerView.lastMoveDirection.x <0)
        {
            _spriteRenderer.flipX = true;
        }
        else
        {
            _spriteRenderer.flipX = false;
        }
    }
    
}
