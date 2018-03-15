#region Namespaces

using System.Diagnostics;
using RoboDk.API.Model;

#endregion

namespace RoboDk.API
{
    public interface IRoboDK
    {
        #region Properties

        Process Process { get; }

        string ApplicationDir { get; }

        #endregion

        #region Public Methods

        /// <summary>
        ///     Starts the link with RoboDK (automatic upon creation of the object)
        /// </summary>
        /// <returns>True if connected; False otherwise</returns>
        bool Connect();

        /// <summary>
        ///     Checks if the object is currently linked to RoboDK
        /// </summary>
        /// <returns></returns>
        bool Connected();

        /// <summary>
        ///     Disconnect from the RoboDK API. This flushes any pending program generation.
        /// </summary>
        void Disconnect();

        void SetWindowState(WindowState windowState);

        Item AddFile(string filename, Item parent = null);

        Item AddProgram(string name, Item itemrobot = null);

        Item AddTarget(string name, Item itemparent = null, Item itemrobot = null);
        
        Item AddShape(Mat shape, Item addTo = null, bool shapeOverride = false);

        void SetViewPose(Mat mat);

        Item AddStation(string name);

        void Render(bool always_render = false);

        void CloseRoboDK();

        #endregion

    }
}