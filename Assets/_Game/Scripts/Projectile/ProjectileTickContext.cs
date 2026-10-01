
using UnityEngine;

public struct ProjectileTickContext
{
    public readonly Vector3 Position;
    public readonly ISpatialGridQuery Grid;

    public ProjectileTickContext(Vector3 position, ISpatialGridQuery grid)
    {
        Position = position;
        Grid = grid;
    }
}
