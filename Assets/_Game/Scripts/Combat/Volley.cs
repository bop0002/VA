using UnityEngine;

// Dem nhip 1 loat N vien cach nhau interval
public class Volley
{
    private int _shotsRemaining;
    private int _shotIndex;
    private float _timer;
    private float _interval;

    public bool IsFiring => _shotsRemaining > 0;

    public void Start(int shotCount, float interval)
    {
        _shotsRemaining = Mathf.Max(1, shotCount);
        _shotIndex = 0;
        _timer = 0f; // vien dau ban ngay
        _interval = interval;
    }

    public void Stop()
    {
        _shotsRemaining = 0;
    }

    public void Advance(float dt)
    {
        _timer -= dt;
    }
    
    public bool TryConsumeShot(out int shotIndex)
    {
        if (_shotsRemaining <= 0 || _timer > 0f)
        {
            shotIndex = -1;
            return false;
        }
        shotIndex = _shotIndex++;
        _shotsRemaining--;
        _timer += _interval;
        return true;
    }
}
