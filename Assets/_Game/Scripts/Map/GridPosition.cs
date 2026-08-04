using System;
using UnityEngine;
[Serializable]
    public record GridPosition
    {
        public int X;
        public int Y; // this game using Y-up

        public GridPosition(int x, int y)
        {
            X = x;
            Y = y;
        }
        
        public override string ToString()
        {
            return $"({X}, {Y})";
        }

        // Addition operator
        public static GridPosition operator +(GridPosition a, GridPosition b)
        {
            return new GridPosition(a.X + b.X, a.Y + b.Y);
        }

        // Subtraction operator
        public static GridPosition operator -(GridPosition a, GridPosition b)
        {
            return new GridPosition(a.X - b.X, a.Y - b.Y);
        }

        // Multiplication operator (scalar)
        public static GridPosition operator *(GridPosition a, int scalar)
        {
            return new GridPosition(a.X * scalar, a.Y * scalar);
        }

        public static GridPosition operator *(int scalar, GridPosition a)
        {
            return new GridPosition(a.X * scalar, a.Y * scalar);
        }

        // Multiplication operator (component-wise)
        public static GridPosition operator *(GridPosition a, GridPosition b)
        {
            return new GridPosition(a.X * b.X, a.Y * b.Y);
        }

        // Division operator (scalar)
        public static GridPosition operator /(GridPosition a, int scalar)
        {
            return new GridPosition(a.X / scalar, a.Y / scalar);
        }

        // Division operator (component-wise)
        public static GridPosition operator /(GridPosition a, GridPosition b)
        {
            return new GridPosition(a.X / b.X, a.Y / b.Y);
        }

        public void Deconstruct(out int x, out int y)
        {
            x = X;
            y = Y;
        }
    }

    public static class GridPositionExtensions
    {
        /// <summary>
        /// Calculates the squared distance between two grid positions.
        /// This is more efficient than calculating actual distance when comparing distances.
        /// Formula: (x1-x2)^2 + (y1-y2)^2
        /// </summary>
        public static int EuclideanDistance(this GridPosition from, GridPosition to)
        {
            var dx = from.X - to.X;
            var dy = from.Y - to.Y;
            return dx * dx + dy * dy;
        }

        public static Vector2 GridToWorld(this GridPosition gridPosition,int cellPerChunk = 20,int cellSize = 1)
        {
            return new Vector2(gridPosition.X * cellPerChunk * cellSize, gridPosition.Y  * cellPerChunk  * cellSize);
        }

        public static GridPosition WorldToGrid(this Vector3 position,int cellPerChunk = 20,int cellSize = 1)
        {
            return new GridPosition(Mathf.RoundToInt(position.x/ cellPerChunk),
                Mathf.RoundToInt(position.y / cellPerChunk));
        }
        
        public static int Dot(this GridPosition first, GridPosition second)
        {
            return first.X * second.X + first.Y * second.Y;
        }
        
    }