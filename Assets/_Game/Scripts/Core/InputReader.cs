using System;
using UnityEngine;
using UnityEngine.InputSystem;

[CreateAssetMenu(fileName = "InputReader", menuName = "Input/Input Reader")]
public class InputReader : ScriptableObject, GameInput.IPlayerActions
{
    
    private GameInput _gameInput;
    public Action<Vector2> OnMovePerformed;
    
    private void OnEnable()
    {
        _gameInput = new GameInput();
        _gameInput.Player.SetCallbacks(this);
        _gameInput.Player.Enable();
    }

    private void OnDisable()
    {
        _gameInput.Player.SetCallbacks(null);
        _gameInput.Player.Disable();
    }
    
    public void OnMove(InputAction.CallbackContext context)
    {
        OnMovePerformed?.Invoke(context.ReadValue<Vector2>());
    }
}
