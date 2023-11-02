#region Namespaces

using System.Diagnostics;
#if NET45
using System.Windows.Media;
#else
using System.Drawing;
#endif

#endregion

namespace RoboDk.API.Model
{
    /// <summary>
    /// Extension methods to convert between System.Windows.Media.Color and RoboDK color array [R,G,B,A]
    /// </summary>
    // ReSharper disable once InconsistentNaming
    public static class RDKColorExtension
    {
        public static double[] ToRoboDKColorArray(this Color color)
        {
            return new[] { color.R / 255.0, color.G / 255.0, color.B / 255.0, color.A / 255.0 };
        }

        public static Color FromRoboDKColorArray(this double[] array)
        {
            Debug.Assert(array.Length == 4);
            var color = Color.FromArgb(
                (byte) (array[3] * 255.0),
                (byte) (array[0] * 255.0),
                (byte) (array[1] * 255.0),
                (byte) (array[2] * 255.0)
            );
            return color;
        }
    }

}