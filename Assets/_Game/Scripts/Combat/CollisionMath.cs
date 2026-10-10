using UnityEngine;

public static class CollisionMath
{
    public static bool CircleOverlapsCircle(Vector2 a, float radiusA, Vector2 b, float radiusB)
    {
        float r = radiusA + radiusB;
        return (a - b).sqrMagnitude <= r * r;
    }

    // OBB: halfSize.x doc theo right, halfSize.y doc theo up. right phai normalize.
    public static bool CircleOverlapsBox(Vector2 circle, float radius, Vector2 boxCenter, Vector2 halfSize, Vector2 right)
    {
        Vector2 up = new Vector2(-right.y, right.x);
        Vector2 d = circle - boxCenter;
        Vector2 local = new Vector2(Vector2.Dot(d, right), Vector2.Dot(d, up)); // toa do tam tron trong he truc cua box
        Vector2 closest = new Vector2(
            Mathf.Clamp(local.x, -halfSize.x, halfSize.x),
            Mathf.Clamp(local.y, -halfSize.y, halfSize.y)); // diem tren box gan tam tron nhat
        return (local - closest).sqrMagnitude <= radius * radius;
    }
}
