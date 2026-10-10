using System.Collections.Generic;
using UnityEngine;

public interface ITargetQuery
{
    void QueryCircle(Vector2 center, float radius, List<ITargetable> result);
    void QueryBox(Vector2 center, Vector2 halfSize, Vector2 right, List<ITargetable> result);
}
