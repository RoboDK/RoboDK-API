#region Namespaces

using System.Diagnostics;
using System.Windows.Media;

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
            return new double[] {color.ScR, color.ScG, color.ScB, color.ScA};
        }

        public static Color FromRoboDKColorArray(this double[] array)
        {
            Debug.Assert(array.Length == 4);
            var color = new Color
            {
                ScR = (float)array[0],
                ScG = (float)array[1],
                ScB = (float)array[2],
                ScA = (float)array[3]
            };
            return color;
        }
    }

}