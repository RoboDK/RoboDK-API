#region Namespaces

using System.Collections.Generic;
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
        /// Establish a connection with RoboDK. 
        /// If RoboDK is not running it will attempt to start RoboDK from the default installation path.
        /// (otherwise APPLICATION_DIR must be set properly). 
        /// </summary>
        /// <returns>If the connection succeeds it returns True, otherwise it returns False.</returns>
        bool Connect();

        /// <summary>
        /// Checks if the RoboDK Link is connected.
        /// </summary>
        /// <returns>
        /// True if connected; False otherwise
        /// </returns>
        bool Connected();

        /// <summary>
        /// Stops the communication with RoboDK. 
        /// If setRunMode is set to MakeRobotProgram for offline programming, 
        /// any programs pending will be generated.
        /// </summary>
        void Disconnect();

        /// <summary>
        /// Close RoboDK window and finish RoboDK process.
        /// </summary>
        void CloseRoboDK();

        /// <summary>
        /// Set the state of the RoboDK window
        /// </summary>
        /// <param name="windowState">Window state to be set.</param>
        void SetWindowState(WindowState windowState = WindowState.Normal);

        /// <summary>
        /// Load a file and attaches it to parent and returns the newly added Item. 
        /// </summary>
        /// <param name="filename">
        /// Any file to load, supported by RoboDK. 
        /// Supported formats include STL, STEP, IGES, ROBOT, TOOL, RDK,... 
        /// It is also possible to load supported robot programs, such as SRC (KUKA), 
        /// SCRIPT (Universal Robots), LS (Fanuc), JBI (Motoman), MOD (ABB), PRG (ABB), ...
        /// </param>
        /// <param name="parent">item to attach the newly added object (optional)</param>
        /// <returns></returns>
        Item AddFile(string filename, Item parent = null);

        /// <summary>
        /// Add a new target that can be reached with a robot.
        /// </summary>
        /// <param name="name">Target name</param>
        /// <param name="parent">Reference frame to attach the target</param>
        /// <param name="robot">Robot that will be used to go to target (optional)</param>
        /// <returns>Newly created target item.</returns>
        Item AddTarget(string name, Item parent = null, Item robot = null);

        /// <summary>
        /// Add a new program to the RoboDK station. 
        /// Programs can be used to simulate a specific sequence, to generate vendor specific programs (Offline Programming) 
        /// or to run programs on the robot (Online Programming).
        /// </summary>
        /// <param name="name">Name of the program</param>
        /// <param name="robot">Robot that will be used for this program. It is not required to specify the robot if the station has only one robot or mechanism.</param>
        /// <returns>Newly created Program Item</returns>
        Item AddProgram(string name, Item robot = null);


        /// <summary>
        /// Display/render the scene: update the display. 
        /// This function turns default rendering (rendering after any modification of the station unless alwaysRender is set to true). 
        /// Use Update to update the internal links of the complete station without rendering 
        /// (when a robot or item has been moved).
        /// </summary>
        /// <param name="alwaysRender">Set to True to update the screen every time the station is modified (default behavior when Render() is not used).</param>
        void Render(bool alwaysRender = false);

        /// <summary>
        /// Returns an item by its name. If there is no exact match it will return the last closest match.
        /// Specify what type of item you are looking for with itemtype.
        /// This is useful if 2 items have the same name but different type.
        // (check variables itemType)
        /// </summary>
        /// <param name="name">name of the item (name of the item shown in the RoboDK station tree)</param>
        /// <param name="itemType">type of the item to be retrieved (avoids confusion if there are similar name matches).</param>
        /// <returns>Returns an item by its name.</returns>
        Item GetItemByName(string name, ItemType itemType = ItemType.Any);

        /// <summary>
        ///     Returns a list of items (list of names) of all available items in the currently open station in robodk.
        ///     Optionally, use a filter to return specific items (example: GetItemListNames(itemType = ItemType.Robot))
        /// </summary>
        /// <param name="itemType">Only return items of this type.</param>
        /// <returns>List of item Names</returns>
        List<string> GetItemListNames(ItemType itemType = ItemType.Any);

        /// <summary>
        ///     Returns a list of items of all available items in the currently open station in robodk.
        ///     Optionally, use a filter to return items of a specific type
        /// </summary>
        /// <param name="itemType">Only return items of this type</param>
        /// <returns>List of Items (optionally filtered by ItemType).</returns>
        List<Item> GetItemList(ItemType itemType = ItemType.Any);

        #endregion
    }
}