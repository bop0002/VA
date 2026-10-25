using UnityEngine;


public readonly struct SpawnArea
{
    public readonly Vector2 Center;
    public readonly Vector2 HalfExtents;

    public SpawnArea(Vector2 center, Vector2 halfExtents)
    {
        Center = center;
        HalfExtents = halfExtents;
    }

    // Ortho and per
    public static Vector2 CameraHalfExtents(Camera camera)
    {
        float halfHeight = camera.orthographic
            ? camera.orthographicSize
            : Mathf.Abs(camera.transform.position.z) * Mathf.Tan(camera.fieldOfView * 0.5f * Mathf.Deg2Rad);
        return new Vector2(halfHeight * camera.aspect, halfHeight);
    }

    public SpawnArea Expand(float margin) => new SpawnArea(Center, HalfExtents + Vector2.one * margin);

    public Vector2 RandomPointOnEdge()
    {
        float w = HalfExtents.x * 2f;
        float h = HalfExtents.y * 2f;
        Vector2 min = Center - HalfExtents;
        float t = Random.value * (w + h) * 2f;

        if (t < w) return new Vector2(min.x + t, min.y);      
        
        if (t < h) return new Vector2(min.x + w, min.y + t);    
        t -= h;
        if (t < w) return new Vector2(min.x + w - t, min.y + h); 
        t -= w;
        return new Vector2(min.x, min.y + h - t);                
    }

    public bool Contains(Vector2 point)
    {
        Vector2 d = point - Center;
        return Mathf.Abs(d.x) <= HalfExtents.x && Mathf.Abs(d.y) <= HalfExtents.y;
    }

    public Vector2 OppositeEdgePoint(Vector2 point)
    {
        Vector2 mirrored = Center - point;
        float scale = Mathf.Max(Mathf.Abs(mirrored.x) / HalfExtents.x, Mathf.Abs(mirrored.y) / HalfExtents.y);
        if (scale < 0.0001f) return RandomPointOnEdge();
        return Center + mirrored / scale;
    }

    public void DrawGizmos(Color color)
    {
        Gizmos.color = color;
        Gizmos.DrawWireCube(Center, HalfExtents * 2f);
    }
}
