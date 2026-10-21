using UnityEngine;

public class PooledFx : MonoBehaviour, IPoolable
{
    [SerializeField] private float _lifetime = 0.4f;
    [SerializeField] private float _fadeDuration = 0.15f; 
    private float _timeLeft;
    private SpriteRenderer[] _renderers;
    private Color[] _baseColors;

    private void Awake()
    {
        _renderers = GetComponentsInChildren<SpriteRenderer>(true);
        _baseColors = new Color[_renderers.Length];
        for (int i = 0; i < _renderers.Length; i++)
        {
            _baseColors[i] = _renderers[i].color;
        }
    }

    public void OnSpawn()
    {
        _timeLeft = _lifetime;
        SetAlpha(1f);
    }

    public void OnDespawn()
    {
        SetAlpha(1f);
    }

    private void Update()
    {
        _timeLeft -= Time.deltaTime;
        if (_timeLeft <= 0f)
        {
            ObjectPoolingManager.Instance.DespawnObject(gameObject, ObjectPoolingManager.PoolType.Fx);
            return;
        }

        if (_fadeDuration > 0f && _timeLeft < _fadeDuration)
        {
            SetAlpha(_timeLeft / _fadeDuration);
        }
    }

    private void SetAlpha(float t)
    {
        for (int i = 0; i < _renderers.Length; i++)
        {
            Color c = _baseColors[i];
            c.a *= t;
            _renderers[i].color = c;
        }
    }
}
