// ----------------------------------------------------------------------------------------------------------
// Copyright 2018 - RoboDK Inc. - https://robodk.com/
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
// http://www.apache.org/licenses/LICENSE-2.0
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
// ----------------------------------------------------------------------------------------------------------

// ----------------------------------------------------------------------------------------------------------
// This file (RoboDK.cs) implements the RoboDK API for C#
// This file defines the following classes:
//     Mat: Matrix class, useful pose operations
//     RoboDK: API to interact with RoboDK
//     RoboDK.IItem: Any item in the RoboDK station tree
//
// These classes are the objects used to interact with RoboDK and create macros.
// An item is an object in the RoboDK tree (it can be either a robot, an object, a tool, a frame, a program, ...).
// Items can be retrieved from the RoboDK station using the RoboDK() object (such as RoboDK.GetItem() method) 
//
// In this document: pose = transformation matrix = homogeneous matrix = 4x4 matrix
//
// More information about the RoboDK API for Python here:
//     https://robodk.com/doc/en/CsAPI/index.html
//     https://robodk.com/doc/en/RoboDK-API.html
//     https://robodk.com/doc/en/PythonAPI/index.html
//
// More information about RoboDK post processors here:
//     https://robodk.com/help#PostProcessor
//
// Visit the Matrix and Quaternions FAQ for more information about pose/homogeneous transformations
//     http://www.j3d.org/matrix_faq/matrfaq_latest.html
//
// This library includes the mathematics to operate with homogeneous matrices for robotics.
// ----------------------------------------------------------------------------------------------------------


#region Namespaces

using System;
using System.Collections.Generic;
using System.Diagnostics;
#if NET45
using System.Windows.Media;
#else
using System.Drawing;
#endif
using RoboDk.API.Model;

#endregion

namespace RoboDk.API
{
    public interface IRoboDK
    {
        #region Properties

        /// <summary>
        /// Name of the RoboDK instance.
        /// In case of multiple instances the name can help to identify the instance.
        /// </summary>
        string Name { get; set; }

        Process Process { get; }
        string LastStatusMessage { get; } // holds any warnings for the last call

        string ApplicationDir { get; }

        /// <summary>
        /// TCP Server Port to which this instance is connected to.
        /// </summary>
        int RoboDKServerPort { get; }

        /// <summary>
        /// TCP Client Port
        /// </summary>
        int RoboDKClientPort { get; }

        /// <summary>
        /// Default Socket Timeout in Milliseconds.
        /// </summary>
        int DefaultSocketTimeoutMilliseconds { get; set; }

        /// <summary>
        /// Allows to install a function which can intercept all interface methods.
        /// Used for Aspect oriented programming (e.g. Add loging to an Interface).
        /// Example:
        ///     rdk.InterceptorFunction = ItemInterceptorFunction;
        ///     private IItem ItemInterceptorFunction(IItem item)
        ///     {
        ///         var behaviour = new LoggingAspect(_logger);
        ///         var itemProxy = Unitity.Interception.Intercept.ThroughProxy(item, new InterfaceInterceptor(), new[] {behaviour});
        ///         return itemProxy;
        ///     }
        /// </summary>
        Func<IItem, IItem> ItemInterceptFunction { set; get; }

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
        /// Open a new additional RoboDK Link to the same already existing RoboDK instance.
        /// NOTE: Use IItem.Clone() to use an already existing item on the new RoboDk connection.
        /// </summary>
        /// <returns>New RoboDK Link</returns>
        IRoboDK CloneRoboDkConnection(RoboDK.ConnectionType connectionType = RoboDK.ConnectionType.Api);

        /// <summary>
        /// Get RoboDK's main window handle
        /// </summary>
        /// <returns></returns>
        IntPtr GetWindowHandle();

        /// <summary>
        /// Start the event communication channel.
        /// Use WaitForEvent to wait for a new event.
        /// </summary>
        /// <returns>new event channel instance</returns>
        IRoboDKEventSource OpenRoboDkEventChannel();

        /// <summary>
        /// Close RoboDK window and finish RoboDK process.
        /// </summary>
        void CloseRoboDK();

        /// <summary>
        /// Return the vesion of RoboDK as a 4 digit string: Major.Minor.Revision.Build
        /// </summary>
        string Version();

        /// <summary>
        /// Set the state of the RoboDK window
        /// </summary>
        /// <param name="windowState">Window state to be set.</param>
        void SetWindowState(WindowState windowState = WindowState.Normal);


        /// <summary>
        /// Makes a copy of an item (same as Ctrl+C), which can be pasted (Ctrl+V) using Paste().
        /// </summary>        
        /// <param name="tocopy">Item to copy</param>
        /// <param name="copy_children">Set to false to prevent copying all items attached to this item</param>
        void Copy(IItem tocopy, bool copy_children = true);

        /// <summary>
        /// Paste the copied item as a dependency of another item (same as Ctrl+V). Paste should be used after Copy(). It returns the newly created item. 
        /// </summary>
        /// <param name="paste_to">Item to attach the copied item (optional)</param>
        /// <returns>New item created</returns>
        IItem Paste(IItem paste_to = null);

        /// <summary>
        /// Paste the copied item as a dependency of another item (same as Ctrl+V). Paste should be used after Copy(). It returns the newly created item. 
        /// </summary>
        /// <param name="paste_to">Item to attach the copied item</param>
        /// <param name="paste_times">Number of times to replicate the copied object</param>
        /// <returns>New item created</returns>
        List<IItem> Paste(IItem paste_to, int paste_times);

        /// <summary>
        /// Load a file and attaches it to parent and returns the newly added IItem. 
        /// </summary>
        /// <param name="filename">
        ///     Any file to load, supported by RoboDK. 
        ///     Supported formats include STL, STEP, IGES, ROBOT, TOOL, RDK,... 
        ///     It is also possible to load supported robot programs, such as SRC (KUKA), 
        ///     SCRIPT (Universal Robots), LS (Fanuc), JBI (Motoman), MOD (ABB), PRG (ABB), ...
        /// </param>
        /// <param name="parent">item to attach the newly added object (optional)</param>
        /// <returns></returns>
        IItem AddFile(string filename, IItem parent = null);

        /// <summary>
        /// Add Text to 3D View
        /// </summary>
        /// <param name="text">Text to add to the scene</param>
        /// <param name="parent">item to attach the newly added text object (optional)</param>
        /// <returns></returns>
        IItem AddText(string text, IItem parent = null);

        /// <summary>
        /// Add a new target that can be reached with a robot.
        /// </summary>
        /// <param name="name">Target name</param>
        /// <param name="parent">Reference frame to attach the target</param>
        /// <param name="robot">Robot that will be used to go to target (optional)</param>
        /// <returns>Newly created target item.</returns>
        IItem AddTarget(string name, IItem parent = null, IItem robot = null);

        /// <summary>
        /// Add a new program to the RoboDK station. 
        /// Programs can be used to simulate a specific sequence, to generate vendor specific programs (Offline Programming) 
        /// or to run programs on the robot (Online Programming).
        /// </summary>
        /// <param name="name">Name of the program</param>
        /// <param name="robot">Robot that will be used for this program. It is not required to specify the robot if the station has only one robot or mechanism.</param>
        /// <returns>Newly created Program IItem</returns>
        IItem AddProgram(string name, IItem robot = null);

        /// <summary>
        /// Add a new empty station.
        /// </summary>
        /// <param name="name">Name of the station</param>
        /// <returns>Newly created station IItem</returns>
        IItem AddStation(string name);

        /// <summary>
        /// Add a new robot machining project. Machining projects can also be used for 3D printing, following curves and following points. 
        /// It returns the newly created :class:`.IItem` containing the project settings.
        /// Tip: Use the macro /RoboDK/Library/Macros/MoveRobotThroughLine.py to see an example that creates a new "curve follow project" given a list of points to follow(Option 4).
        /// </summary>
        /// <param name="name">Name of the project settings</param>
        /// <param name="itemrobot">Robot to use for the project settings(optional). It is not required to specify the robot if only one robot or mechanism is available in the RoboDK station.</param>
        /// <returns></returns>
        IItem AddMachiningProject(string name = "Curve follow settings", IItem itemrobot = null);

        /// <summary>
        /// Returns the list of open stations in RoboDK
        /// </summary>
        /// <returns></returns>
        List<IItem> GetOpenStation();

        /// <summary>
        /// Set the active station (project currently visible)
        /// </summary>
        /// <param name="station">station item, it can be previously loaded as an RDK file</param>
        void SetActiveStation(IItem station);

        /// <summary>
        /// Returns the active station item (station currently visible)
        /// </summary>
        /// <returns></returns>
        IItem GetActiveStation();

        /// <summary>
        /// Display/render the scene: update the display. 
        /// This function turns default rendering (rendering after any modification of the station unless alwaysRender is set to true). 
        /// Use Update to update the internal links of the complete station without rendering 
        /// (when a robot or item has been moved).
        /// </summary>
        /// <param name="alwaysRender">Set to True to update the screen every time the station is modified (default behavior when Render() is not used).</param>
        void Render(bool alwaysRender = false);

        /// <summary>
        /// Update the screen. 
        /// This updates the position of all robots and internal links according to previously set values.
        /// </summary>
        void Update();

        /// <summary>
        /// Returns an item by its name. If there is no exact match it will return the last closest match.
        /// Specify what type of item you are looking for with itemtype.
        /// This is useful if 2 items have the same name but different type.
        /// </summary>
        /// <param name="name">name of the item (name of the item shown in the RoboDK station tree)</param>
        /// <param name="itemType">type of the item to be retrieved (avoids confusion if there are similar name matches).</param>
        /// <returns>Returns an item by its name.</returns>
        IItem GetItemByName(string name, ItemType itemType = ItemType.Any);

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
        List<IItem> GetItemList(ItemType itemType = ItemType.Any);

        /// <summary>
        /// Shows a RoboDK popup to select one object from the open station.
        /// An item type can be specified to filter desired items. If no type is specified, all items are selectable.
        /// The method always returns an IItem. Use item.Valid() to check if the selected item is a valid item.
        /// E.g. if the user exits the dialog without selecting an item, the method still returns an item object, but item.Valid() will return False.
        /// </summary>
        /// <param name="message">Message to pop up</param>
        /// <param name="itemType">optionally filter by ItemType</param>
        /// <returns>User selected item. Use item.Valid() to check if the item is valid</returns>
        IItem ItemUserPick(string message = "Pick one item", ItemType itemType = ItemType.Any);

        /// <summary>
        /// Shows or raises the RoboDK window.
        /// </summary>
        void ShowRoboDK();

        /// <summary>
        /// Fit all
        /// </summary>
        void FitAll();

        /// <summary>
        /// Hides the RoboDK window.
        /// </summary>
        void HideRoboDK();

        /// <summary>
        /// Update the RoboDK flags. 
        /// RoboDK flags allow defining how much access the user has to RoboDK features. 
        /// Use the flags defined in WindowFlags to set one or more flags.
        /// </summary>
        /// <param name="flags">RoboDk Window Flags</param>
        void SetWindowFlags(WindowFlags flags);

        /// <summary>
        /// Retrieve current item flags.
        /// Item flags allow defining how much access the user has to item-specific features.
        /// </summary>
        /// <param name="item">Item to get flags</param>
        /// <returns>Returns ItemFlags of the item.</returns>
        ItemFlags GetItemFlags(IItem item);

        /// <summary>
        /// Update global item flags.
        /// Item flags allow defining how much access the user has to item-specific features.
        /// </summary>
        /// <param name="item">Item to set (use null to apply to all items)</param>
        /// <param name="itemFlags">Item flags</param>
        void SetItemFlags(IItem item, ItemFlags itemFlags = ItemFlags.All);

        /// <summary>
        /// Show a message in RoboDK (it can be blocking or non blocking in the status bar)
        /// </summary>
        /// <param name="message">Message to display</param>
        /// <param name="popup">Set to true to make the message blocking or set to false to make it non blocking</param>
        void ShowMessage(string message, bool popup = true);

        /// <summary>
        /// Save an item to a file. If no item is provided, the open station is saved.
        /// </summary>
        /// <param name="filename">absolute path to save the file</param>
        /// <param name="itemsave">object or station to save. Leave empty to automatically save the current station.</param>
        void Save(string filename, IItem itemsave = null);

        /// <summary>
        ///     Adds a shape provided triangle coordinates. Triangles must be provided as a list of vertices. A vertex normal can
        ///     be provided optionally.
        /// </summary>
        /// <param name="trianglePoints">
        ///     List of vertices grouped by triangles (3xN or 6xN matrix, N must be multiple of 3 because
        ///     vertices must be stacked by groups of 3)
        /// </param>
        /// <param name="addTo">item to attach the newly added geometry (optional). Leave empty to create a new object.</param>
        /// <param name="shapeOverride">Set to true to replace any other existing geometry</param>
        /// <param name="color">Color of the added shape</param>
        /// <returns>added object/shape (use item.Valid() to check if item is valid.)</returns>
        IItem AddShape(Mat trianglePoints, IItem addTo = null, bool shapeOverride = false, Color? color = null);

        /// <summary>
        /// Adds a shape provided triangle coordinates. Triangles must be provided as a list of vertices. A vertex normal can be provided optionally.
        /// </summary>
        /// <param name="listTrianglePoints">List of Mat objects. Each mat object is a list of vertices grouped by triangles of the same color (3xN or 6xN matrix, N must be multiple of 3 because vertices must be stacked by groups of 3)</param>
        /// <param name="addTo">item to attach the newly added geometry (optional). Leave empty to create a new object.</param>
        /// <param name="shapeOverride">Set to true to replace any other existing geometry</param>
        /// <param name="listColor">Optionally specify the color as RGBA [0-1] (list of same length as triangle_points_list)</param>
        /// <returns></returns>
        IItem AddShape(List<Mat> listTrianglePoints, IItem addTo = null, bool shapeOverride = false, List<Color> listColor = null);

        /// <summary>
        /// Adds a curve provided point coordinates.
        /// The provided points must be a list of vertices.
        /// A vertex normal can be provided optionally.
        /// </summary>
        /// <param name="curvePoints">matrix 3xN or 6xN -> N must be multiple of 3</param>
        /// <param name="referenceObject">object to add the curve and/or project the curve to the surface</param>
        /// <param name="addToRef">
        ///     If True, the curve will be added as part of the object in the RoboDK item tree (a reference
        ///     object must be provided)
        /// </param>
        /// <param name="projectionType">
        ///     Type of projection. For example:  ProjectionType.AlongNormalRecalc will project along the
        ///     point normal and recalculate the normal vector on the surface projected.
        /// </param>
        /// <returns>added object/curve (use item.Valid() to check if item is valid.)</returns>
        IItem AddCurve(Mat curvePoints, IItem referenceObject = null, bool addToRef = false,
            ProjectionType projectionType = ProjectionType.AlongNormalRecalc);

        /// <summary>
        /// Adds a list of points to an object. The provided points must be a list of vertices. A vertex normal can be provided optionally.
        /// </summary>
        /// <param name="points">list of points as a matrix (3xN matrix, or 6xN to provide point normals as ijk vectors)</param>
        /// <param name="referenceObject">item to attach the newly added geometry (optional)</param>
        /// <param name="addToRef">If True, the points will be added as part of the object in the RoboDK item tree (a reference object must be provided)</param>
        /// <param name="projectionType">Type of projection.Use the PROJECTION_* flags.</param>
        /// <returns>added object/shape (0 if failed)</returns>
        IItem AddPoints(Mat points, IItem referenceObject = null, bool addToRef = false, ProjectionType projectionType = ProjectionType.AlongNormalRecalc);

        /// <summary>
        /// Projects a point given its coordinates.
        /// The provided points must be a list of [XYZ] coordinates.
        /// Optionally, a vertex normal can be provided [XYZijk].
        /// </summary>
        /// <param name="points">matrix 3xN or 6xN -> list of points to project</param>
        /// <param name="objectProject">object to project</param>
        /// <param name="projectionType">
        ///     Type of projection. For example: ProjectionType.AlongNormalRecalc will project along the
        ///     point normal and recalculate the normal vector on the surface projected.
        /// </param>
        /// <returns>
        ///     It returns the projected points as a list of points (empty matrix if failed).
        /// </returns>
        Mat ProjectPoints(Mat points, IItem objectProject, ProjectionType projectionType = ProjectionType.AlongNormalRecalc);

        /// <summary>
        /// Closes the current station without suggesting to save
        /// </summary>
        void CloseStation();

        /// <summary>
        /// Delete a list of items
        /// </summary>
        void Delete(List<IItem> item_list);

        /// <summary>
        ///  Adds a new Frame that can be referenced by a robot.
        /// </summary>
        /// <param name="name">name of the reference frame</param>
        /// <param name="parent">parent to attach to (such as the robot base frame)</param>
        /// <returns>The new reference frame created</returns>
        IItem AddFrame(string name, IItem parent = null);

        /// <summary>
        ///     Adds a function call in the program output. RoboDK will handle the syntax when the code is generated for a specific
        ///     robot. If the program exists it will also run the program in simulate mode.
        /// </summary>
        /// <param name="function">Function name with parameters (if any)</param>
        /// <returns>
        /// TODO: Document possible return values.
        /// </returns>
        int RunProgram(string function);

        /// <summary>
        /// Adds code to run in the program output. 
        /// If the program exists it will also run the program in simulate mode.
        /// </summary>
        /// <param name="code">program name or code to generate</param>
        /// <param name="codeIsFunctionCall">
        ///     Set to True if the provided code corresponds to a function call (same as RunProgram()), if so, 
        ///     RoboDK will handle the syntax when the code is generated for a specific robot.
        /// </param>
        /// <returns>
        /// TODO: Document possible return values.
        /// </returns>
        int RunCode(string code, bool codeIsFunctionCall = false);

        /// <summary>
        /// Shows a message or a comment in the output robot program.
        /// </summary>
        /// <param name="message">message or comment to display.</param>
        /// <param name="messageIsComment">
        /// Set to True to generate a comment in the generated code instead of displaying a message on the teach pendant of the robot.
        /// </param>
        void RunMessage(string message, bool messageIsComment = false);

        /// <summary>
        /// Check if objectInside is inside the objectParent.
        /// </summary>
        /// <param name="objectInside"></param>
        /// <param name="objectParent"></param>
        /// <returns>Returns true if objectInside is inside the objectParent</returns>
        bool IsInside(IItem objectInside, IItem objectParent);

        /// <summary>
        /// Set collision checking ON or OFF (CollisionCheckOff/CollisionCheckOn) according to the collision map. 
        /// If collision check is activated it returns the number of pairs of objects that are currently in a collision state.
        /// </summary>
        /// <param name="collisionCheck">collision checking ON or OFF</param>
        /// <returns>Number of pairs of objects in a collision state</returns>
        int SetCollisionActive(CollisionCheckOptions collisionCheck = CollisionCheckOptions.CollisionCheckOn);

        /// <summary>
        /// Set all pairs as checking for collisions: 
        /// </summary>
        void EnableCollisionCheckingForAllItems();

        /// <summary>
        /// Set all pairs as NOT checking for collisions:  
        /// </summary>
        void DisableCollisionCheckingForAllItems();

        /// <summary>
        /// Set collision checking ON or OFF (COLLISION_ON/COLLISION_OFF) for a specific pair of objects. This allows altering
        /// the collision map for Collision checking.
        /// Specify the link id for robots or moving mechanisms (id 0 is the base).
        /// </summary>
        /// <param name="collisionCheck">Set to COLLISION_ON or COLLISION_OFF</param>
        /// <param name="collisionPair">Collision pair (item1, id1, item2, id2) to set</param>
        /// <returns>Returns true if succeeded. Returns false if setting the pair failed (wrong id was provided)</returns>
        bool SetCollisionActivePair(CollisionCheckOptions collisionCheck, CollisionPair collisionPair);


        /// <summary>
        /// Set collision checking ON or OFF (COLLISION_ON/COLLISION_OFF) for a specific list of pairs of objects. This allows altering the collision map for Collision checking. 
        /// Specify the link id for robots or moving mechanisms (id 0 is the base).
        /// </summary>
        /// <param name="checkState">Set to COLLISION_ON or COLLISION_OFF</param>
        /// <param name="collisionPairs">List of collision pairs to set</param>
        /// <returns>Returns true if succeeded. Returns false if setting the pair failed (wrong id was provided)</returns>
        bool SetCollisionActivePair(List<CollisionCheckOptions> checkState, IReadOnlyList<CollisionPair> collisionPairs);

        /// <summary>
        /// Returns the number of pairs of objects that are currently in a collision state.
        /// </summary>
        /// <returns>Number of pairs of objects in a collision state.</returns>
        int Collisions();

        /// <summary>
        /// Check if item1 and item2 collided.
        /// </summary>
        /// <param name="item1"></param>
        /// <param name="item2"></param>
        /// <param name="useCollisionMap">Turn off collision map check to force collision checking even if it is not set in the collision map</param>
        /// <returns>Returns true if item1 collides with item2; false otherwise.</returns>
        bool Collision(IItem item1, IItem item2, bool useCollisionMap = true);

        /// <summary>
        /// Return the list of items that are in a collision state. This call will run a check for collisions if collision checking is not activated (if SetCollisionActive is set to Off).
        /// </summary>
        /// <returns>List of items that are in a collision state</returns>
        List<CollisionItem> GetCollisionItems();

        /// <summary>
        /// Returns the list of pairs of items that are in a collision state. This call will run a check for collisions if collision checking is not activated (if SetCollisionActive is set to Off).
        /// </summary>
        /// <returns></returns>
        List<CollisionPair> GetCollisionPairs();

        /// <summary>
        /// Set the simulation speed. A simulation speed of 5 (default) means that 1 second of simulation 
        /// time equals to 5 seconds in a real application. The slowest speed ratio allowed is 0.001. 
        /// Set a large simmulation ratio (>100) for fast simulation results.
        /// </summary>
        /// <param name="speed">simulation ratio.</param>
        void SetSimulationSpeed(double speed);

        /// <summary>
        /// Gets the current simulation speed. 
        /// A speed if 1 means real-time simulation.
        /// </summary>
        /// <returns>Simulation Speed. 1.0=real-time simulation.</returns>
        double GetSimulationSpeed();

        /// <summary>
        /// Sets the behavior of the RoboDK API. 
        /// By default, robodk shows the path simulation for movement instructions (RunMode.Simulate).
        /// Setting the run_mode to RunMode.QuickValidate allows performing a quick check to see if the path is feasible.
        /// If robot.Connect() is used, RUNMODE_RUN_FROM_PC is selected automatically.
        /// </summary>
        /// <param name="runMode">program run mode.</param>
        void SetRunMode(RunMode runMode = RunMode.Simulate);

        /// <summary>
        /// Returns the behavior of the RoboDK API. By default, robodk shows the path simulation for movement instructions
        /// (RunMode.Simulate)
        /// </summary>
        /// <returns>Returns the currently active RunMode.</returns>
        RunMode GetRunMode();

        /// <summary>
        /// Gets all the user parameters from the open RoboDK station.
        /// The parameters can also be modified by right clicking the station and selecting "shared parameters"
        /// User parameters can be added or modified by the user
        /// </summary>
        /// <returns>list of param-value pair</returns>
        List<KeyValuePair<string, string>> GetParameterList();

        /// <summary>
        /// Gets a global or a user parameter from the open RoboDK station.
        /// The parameters can also be modified by right clicking the station and selecting "shared parameters"
        /// Some available parameters:
        /// PATH_OPENSTATION = folder path of the current .stn file
        /// FILE_OPENSTATION = file path of the current .stn file
        /// PATH_DESKTOP = folder path of the user's folder
        /// Other parameters can be added or modified by the user
        /// </summary>
        /// <param name="parameter">RoboDK parameter</param>
        /// <returns>parameter value. Null if parameter does not exist.</returns>
        string GetParameter(string parameter);

        /// <summary>
        /// Sets a global parameter from the RoboDK station. If the parameters exists, it will be modified. If not, it will be added to the station.
        /// The parameters can also be modified by right clicking the station and selecting "shared parameters"
        /// </summary>
        /// <param name="parameter">RoboDK parameter name</param>
        /// <param name="value">parameter value</param>
        void SetParameter(string parameter, string value);

        /// <summary>
        /// Sets a global parameter from the RoboDK station. If the parameters exists, it will be modified. If not, it will be added to the station.
        /// The parameters can also be modified by right clicking the station and selecting "shared parameters"
        /// </summary>
        /// <param name="parameter">RoboDK parameter name</param>
        /// <param name="value">parameter value (number)</param>
        void SetParameter(string parameter, double value);

        /// <summary>
        /// Gets a global or a user binary parameter from the open RoboDK station
        /// </summary>
        /// <param name="parameter">RoboDK parameter</param>
        /// <returns>Arrray of bytes.</returns>
        byte[] GetBinaryParameter(string parameter);

        /// <summary>
        /// Sets a global binary parameter from the RoboDK station. If the parameters exists, it will be modified. If not, it will be added to the station.
        /// The parameters can also be modified by right clicking the station and selecting "shared parameters"
        /// </summary>
        /// <param name="parameter">RoboDK parameter name</param>
        /// <param name="data">Parameter binary data</param>
        void SetBinaryParameter(string parameter, byte[] data);


        /// <summary>
        /// Send a special command. These commands are meant to have a specific effect in RoboDK, such as changing a specific setting or provoke specific events.
        /// </summary>
        /// <param name="cmd">Command Name, such as Trace, Threads or Window.</param>
        /// <param name="value">Comand value (optional, not all commands require a value)</param>
        /// <returns></returns>
        string Command(string cmd, string value = "");

        /// <summary>
        /// Send a special command. These commands are meant to have a specific effect in RoboDK, such as changing a specific setting or provoke specific events.
        /// </summary>
        /// <param name="cmd">Command Name, such as Trace, Threads or Window.</param>
        /// <param name="value">Command value</param>
        /// <returns></returns>
        string Command(string cmd, bool value);

        /// <summary>
        /// Send a special command. These commands are meant to have a specific effect in RoboDK, such as changing a specific setting or provoke specific events.
        /// </summary>
        /// <param name="cmd">Command Name, such as Trace, Threads or Window.</param>
        /// <param name="value">Command value</param>
        /// <returns></returns>
        string Command(string cmd, double value);

        /// <summary>
        /// Send a special command. These commands are meant to have a specific effect in RoboDK, such as changing a specific setting or provoke specific events.
        /// </summary>
        /// <param name="cmd">Command Name, such as Trace, Threads or Window.</param>
        /// <param name="value">Command value</param>
        /// <returns></returns>
        string Command(string cmd, int value);

        /// <summary>
        /// Takes a laser tracker measurement with respect to its own reference frame. If an estimate point is provided, the
        /// laser tracker will first move to those coordinates. 
        /// </summary>
        /// <param name="estimate">estimate point [x,y,z]</param>
        /// <param name="search">If search is True, the tracker will search for a target.</param>
        /// <returns>
        /// Returns the XYZ coordinates of the target (in mm). 
        /// If the target was not found it retuns a null pointer.
        /// </returns>
        double[] LaserTrackerMeasure(double[] estimate, bool search = false);

        /// <summary>
        ///     Takes a measurement with the C-Track stereocamera. It returns two poses, the base reference frame and the measured
        ///     object reference frame.Status is 0 if measurement succeeded.
        /// </summary>
        /// <param name="pose1">Pose of the measurement reference</param>
        /// <param name="pose2">Pose of the tool measurement</param>
        /// <param name="npoints1">number of visible targets for the measurement pose</param>
        /// <param name="npoints2">number of visible targets for the tool pose</param>
        /// <param name="time">time stamp in milliseconds</param>
        /// <param name="status">Status is 0 if measurement succeeded</param>
        void StereoCameraMeasure(out Mat pose1, out Mat pose2, out int npoints1, out int npoints2, out int time,
            out int status);

        /// <summary>
        /// Checks the collision between a line and any objects in the station. The line is composed by 2 points.
        /// </summary>
        /// <param name="p1">Start point [x,y,z] of the line</param>
        /// <param name="p2">End point [x,y,z] of the line</param>
        /// <returns>Return true if there is a collision; false otherwise</returns>
        bool CollisionLine(double[] p1, double[] p2);

        /// <summary>
        /// Calculate the forward kinematics solution for multiple robots at the same time (faster)
        /// </summary>
        /// <param name="robotList">list of items</param>
        /// <param name="jointsList">list of joint</param>
        /// <param name="solutionOkList">optional list of bool flags to notify about failed/invalid result</param>
        List<Mat> SolveFK(List<IItem> robotList, List<double[]> jointsList, List<bool> solutionOkList = null);

        /// <summary>
        /// Calculate the inverse kinematics solution for multiple robots at the same time (faster)
        /// </summary>
        /// <param name="robotList">list of items</param>
        /// <param name="poseList">list of poses</param>
        List<double[]> SolveIK(List<IItem> robotList, List<Mat> poseList);

        /// <summary>
        /// Calculate the inverse kinematics solution for multiple robots at the same time (faster)
        /// </summary>
        /// <param name="robotList">list of items</param>
        /// <param name="poseList">list of poses</param>
        /// <param name="japroxList"></param>
        List<double[]> SolveIK(List<IItem> robotList, List<Mat> poseList, List<double[]> japroxList);

        /// <summary>
        /// Calculate the inverse kinematics solution for multiple robots at the same time. This call allows you to have a bulk calculation for faster performance.
        /// </summary>
        /// <param name="robotList">list of items</param>
        /// <param name="poseList">list of poses</param>
        /// <param name="solution_ok_list">optional list of bool flags to notify about failed/invalid result</param>
        List<Mat> SolveIK_All(List<IItem> robotList, List<Mat> poseList);

        /// <summary>
        /// Returns the robot configuration state for a set of robot joints.
        /// </summary>
        /// <param name="robotList">list of items</param>
        /// <param name="jointsList">array of joints</param>
        /// <returns>3-array -> configuration status as [REAR, LOWERARM, FLIP]</returns>
        List<double[]> JointsConfig(List<IItem> robotList, List<double[]> jointsList);

        /// <summary>
        /// Sets the visibility for a list of items
        /// </summary>
        /// <param name="itemList">list of items</param>
        /// <param name="visibleList">list visible flags (bool)</param>
        /// <param name="visibleFrames">list visible frames (optional, hidden by default)</param>
        void SetVisible(List<IItem> itemList, List<bool> visibleList, List<int> visibleFrames = null);

        /// <summary>
        /// Sets the color for a list of items given the a color object
        /// </summary>
        /// <param name="item_list">list of items</param>
        /// <param name="color_list">list of colors</param>
        void SetColor(List<IItem> item_list, List<Color> color_list);

        /// <summary>
        /// Sets the color for a list of items given a 4D, 3D or 1D array of doubles
        /// </summary>
        /// <param name="item_list">list of items</param>
        /// <param name="color_list">list of colors as an array of doubles. Valid colors and alpha channel must be within the range [0-1]. Each array of doubles can be provided as a 4D, 3D or 1D array. Options: [r,g,b,a], [r,g,b], [a]. If you provide [-1,-1,-1,a] only the alpha channel is modified.</param>
        void SetColor(List<IItem> item_list, List<double[]> color_list);

        /// <summary>
        /// Show a list of objects or a robot link as collided (red) or as not collided (normal color)
        /// </summary>
        /// <param name="item_list">List of items</param>
        /// <param name="collided_list">List of collided flags (True=show as collided)</param>
        /// <param name="robot_link_id">Robot link ID, when applicable</param>
        void ShowAsCollided(List<IItem> item_list, List<bool> collided_list, List<int> robot_link_id = null);

        /// <summary>
        /// Get Joint positions of all robots defined in the robotItemList.
        /// </summary>
        /// <param name="robotItemList">list of robot items</param>
        /// <returns>list of robot joints (double x nDOF)</returns>
        List<double[]> Joints(List<IItem> robotItemList);

        /// <summary>
        /// Sets the current robot joints for a list of robot items and a list of a set of joints.
        /// </summary>
        /// <param name="robotItemList">list of robot items.</param>
        /// <param name="jointsList">list of robot joints (double x nDOF).</param>
        void SetJoints(List<IItem> robotItemList, List<double[]> jointsList);


        /// <summary>
        ///     Calibrate a tool (TCP) given a number of points or calibration joints. Important: If the robot is calibrated,
        ///     provide joint values to maximize accuracy.
        /// </summary>
        /// <param name="posesJoints">matrix of poses in a given format or a list of joints</param>
        /// <param name="errorStats">stats[mean, standard deviation, max] - Output error stats summary</param>
        /// <param name="format">Euler format. Optionally, use EulerType.JointFormat and provide the robot.</param>
        /// <param name="algorithm">type of algorithm (by point, plane, ...)</param>
        /// <param name="robot">Robot used for calibration (if using joint values)</param>
        /// <returns>TCP as [x, y, z] - calculated TCP</returns>
        double[] CalibrateTool(Mat posesJoints, out double[] errorStats,
            EulerType format = EulerType.EulerRxRyRz,
            TcpCalibrationType algorithm = TcpCalibrationType.CalibrateTcpByPoint,
            IItem robot = null);

        /// <summary>
        ///     Calibrate a Reference Frame given a list of points or joint values. Important: If the robot is calibrated, provide
        ///     joint values to maximize accuracy.
        /// </summary>
        /// <param name="joints">points as a 3xN matrix or nDOFsxN) - List of points or a list of robot joints</param>
        /// <param name="method">type of algorithm(by point, plane, ...)</param>
        /// <param name="useJoints">use points or joint values. The robot item must be provided if joint values is used.</param>
        /// <param name="robot"></param>
        /// <returns>TODO: Document return value.</returns>
        Mat CalibrateReference(Mat joints,
            ReferenceCalibrationType method = ReferenceCalibrationType.Frame3P_P1OnX,
            bool useJoints = false, IItem robot = null);


        /// <summary>
        ///     Defines the name of the program when the program is generated. It is also possible to specify the name of the post
        ///     processor as well as the folder to save the program.
        ///     This method must be called before any program output is generated (before any robot movement or other instruction).
        /// </summary>
        /// <param name="progname">name of the program</param>
        /// <param name="defaultfolder">folder to save the program, leave empty to use the default program folder</param>
        /// <param name="postprocessor">
        ///     name of the post processor (for a post processor in C:/RoboDK/Posts/Fanuc_post.py it is
        ///     possible to provide "Fanuc_post.py" or simply "Fanuc_post")
        /// </param>
        /// <param name="robot">Robot to link</param>
        /// <returns>TODO: Document return value.</returns>
        int ProgramStart(string progname, string defaultfolder = "", string postprocessor = "", IItem robot = null);

        /// <summary>
        /// Set the pose of the wold reference frame with respect to the view (camera/screen).
        /// </summary>
        /// <param name="pose">view pose frame.</param>
        void SetViewPose(Mat pose);

        /// <summary>
        /// Get the pose of the wold reference frame with respect to the view (camera/screen)
        /// </summary>
        /// <param name="preset">Optionally specify a ViewPoseType to retrieve the pose for a specific view</param>
        /// <returns>Returns the current view pose.</returns>
        Mat GetViewPose(ViewPoseType preset = ViewPoseType.ActiveView);

        /// <summary>
        /// Gets the nominal robot parameters.
        /// </summary>
        /// <param name="robot"></param>
        /// <param name="dhm"></param>
        /// <param name="poseBase"></param>
        /// <param name="poseTool"></param>
        /// <returns></returns>
        bool SetRobotParams(IItem robot, double[][] dhm, Mat poseBase, Mat poseTool);

        /// <summary>
        /// Create a new robot or mechanism.
        /// </summary>
        /// <param name="type">Type of the mechanism</param>
        /// <param name="list_obj">list of object items that build the robot</param>
        /// <param name="param">robot parameters in the same order as shown in the RoboDK menu: Utilities-Build Mechanism or robot</param>
        /// <param name="joints_build">Current state of the robot joints when you build it</param>
        /// <param name="joints_home">Joints for the home position (it can be changed later)</param>
        /// <param name="joints_senses">sense of rotation (same sense of rotation that can be specified in Parameters->Joint senses)</param>
        /// <param name="joints_lim_low">joint lower limits (you can also double click the robot label in the robot panel to update)</param>
        /// <param name="joints_lim_high">joint upper limits (you can also double click the robot label in the robot panel to update)</param>
        /// <param name="base_frame">base pose</param>
        /// <param name="tool">tool pose</param>
        /// <param name="name">robot name (you can also use setName()</param>
        /// <param name="robot">existing robot in the station to replace it (optional)</param>
        /// <returns></returns>
        IItem BuildMechanism(int type, List<IItem> listObj, List<double> param, List<double> jointsBuild, List<double> jointsHome, List<double> jointsSenses, List<double> jointsLimLow, List<double> jointsLimHigh, Mat baseFrame = null, Mat tool = null, string name = "New robot", IItem robot = null);

        /// <summary>
        /// Open a simulated 2D camera view. 
        /// Returns a handle pointer that can be used in case more than one simulated view is used.
        /// </summary>
        /// <param name="item">Reference frame or other object to attach the camera</param>
        /// <param name="cameraParameters">Camera parameters as a string. Refer to the documentation for more information.</param>
        /// <returns>Camera pointer/handle. Keep the handle if more than 1 simulated camera is used</returns>
        long Cam2DAdd(IItem item, string cameraParameters = "");

        /// <summary>
        /// Take a snapshot from a simulated camera view and save it to a file. 
        /// </summary>
        /// <param name="fileSaveImg">file path to save.Formats supported include PNG, JPEG, TIFF, ...</param>
        /// <param name="camHandle">Camera handle(pointer returned by Cam2DAdd)</param>
        /// <returns>Returns true if image has been saved successfully.</returns>
        bool Cam2DSnapshot(string fileSaveImg, long camHandle = 0);

        /// <summary>
        /// Take a snapshot from a simulated camera view and save it to a file. 
        /// </summary>
        /// <param name="fileSaveImg">file path to save.Formats supported include PNG, JPEG, TIFF, ...</param>
        /// <param name="cam">Camera handle(pointer returned by Cam2DAdd)</param>
        /// <param name="cameraParameters">Camera parameters as a string. Refer to the documentation for more information.</param>
        /// <returns>Returns true if image has been saved successfully.</returns>
        bool Cam2DSnapshot(string fileSaveImg, IItem cam, string cameraParameters = "");

        /// <summary>
        /// Closes all camera windows or one specific camera if the camera handle is provided. 
        /// </summary>
        /// <param name="camHandle">
        /// Camera handle(pointer returned by Cam2DAdd). 
        /// Leave to 0 to close all simulated views.
        /// </param>
        /// <returns>Returns true if success, false otherwise.</returns>
        bool Cam2DClose(long camHandle = 0);

        /// <summary>
        /// Set the parameters of the simulated camera.
        /// </summary>
        /// <param name="cameraParameters">parameter settings according to the parameters supported by Cam2D_Add</param>
        /// <param name="camHandle">camera handle (optional)</param>
        /// <returns>Returns true if success, false otherwise.</returns>
        bool Cam2DSetParameters(string cameraParameters, long camHandle = 0);

        /// <summary>
        /// Returns the license string (as shown in the RoboDK main window)
        /// </summary>
        /// <returns>license string.</returns>
        string GetLicense();

        /// <summary>
        /// Returns the list of items selected (it can be one or more items)
        /// </summary>
        /// <returns>Returns the list of selected items.</returns>
        List<IItem> GetSelectedItems();

        /// <summary>
        /// Set the selection in the tree
        /// </summary>
        /// <returns></returns>
        void SetSelectedItems(List<IItem> item_list);

        /// <summary>
        /// Merge multiple object items as one. Source objects are not deleted and a new object is created.
        /// </summary>
        /// <returns>New item</returns>
        IItem MergeItems(List<IItem> item_list);

        /// <summary>
        /// Show the popup menu to create the ISO9283 path for path accuracy and performance testing
        /// </summary>
        /// <returns>IS9283 Program</returns>
        IItem Popup_ISO9283_CubeProgram(IItem robot = null);

        /// <summary>
        /// Set the interactive mode to define the behavior when navigating and selecting items in RoboDK's 3D view.
        /// </summary>
        /// <param name="modeType">The mode type defines what accion occurs when the 3D view is selected (Select object, Pan, Rotate, Zoom, Move Objects, ...)</param>
        /// <param name="defaultRefFlags">When a movement is specified, we can provide what motion we allow by default with respect to the coordinate system (set apropriate flags)</param>
        /// <param name="customItems">Provide a list of optional items to customize the move behavior for these specific items (important: the lenght of custom_ref_flags must match)</param>
        /// <param name="customRefFlags">Provide a matching list of flags to customize the movement behavior for specific items</param>
        void SetInteractiveMode(InteractiveType modeType = InteractiveType.MoveReferences, DisplayRefType defaultRefFlags = DisplayRefType.DEFAULT, List<IItem> customItems = null, List<DisplayRefType> customRefFlags = null);

        /// <summary>
        /// Returns the position of the cursor as XYZ coordinates (by default), or the 3D position of a given set of 2D coordinates of the window (x and y coordinates in pixels from the top left corner)
        /// The XYZ coordinates returned are given with respect to the RoboDK station(absolute reference).
        /// If no coordinates are provided, the current position of the cursor is retrieved.
        /// </summary>
        /// <param name="xCoord">X coordinate in pixels</param>
        /// <param name="yCoord">Y coordinate in pixels</param>
        /// <param name="xyzStation">XYZ coordinates in mm (absolute coordinates)</param>
        /// <returns>Item under the mouse cursor.</returns>
        IItem GetCursorXYZ(int xCoord = -1, int yCoord = -1, List<double> xyzStation = null);

        /// <summary>
        /// Add a joint movement to a program
        /// </summary>
        /// <param name="pgm"></param>
        /// <param name="targetName"></param>
        /// <param name="joints"></param>
        /// <param name="robotBase"></param>
        /// <param name="robot"></param>
        /// <returns>New target item created.</returns>
        IItem AddTargetJ(IItem pgm, string targetName, double[] joints, IItem robotBase = null, IItem robot = null);

        /// <summary>
        /// Embed a window from a separate process in RoboDK as a docked window
        /// </summary>
        /// <param name="windowName">The name of the window currently open. Make sure the window name is unique and it is a top level window</param>
        /// <param name="dockedName">Name of the docked tab in RoboDK (optional, if different from the window name)</param>
        /// <param name="width"></param>
        /// <param name="height"></param>
        /// <param name="pid">Process ID (optional)</param>
        /// <param name="areaAdd">Set to 1 (right) or 2 (left) (default is 1)</param>
        /// <param name="areaAllowed">Areas allowed (default is 15: no constrain)</param>
        /// <param name="timeout">Timeout to abort attempting to embed the window (optional)</param>
        /// <returns>Returns true if successful.</returns>
        bool EmbedWindow(string windowName, string dockedName = null, int width = -1, int height = -1, int pid = 0, int areaAdd = 1, int areaAllowed = 15, int timeout = 500);

        /// <summary>
        /// Retrieves the object under the mouse cursor
        /// </summary>
        /// <param name="featureType">Set to ObjectSelectionType.HoverObjectMesh to retrieve object under the mouse cursor, the selected feature and mesh, or ObjectSelectionType.HoverObject if you don't need the mesh (faster)</param>
        /// <returns>Returns GetPointsResult with an object under the mouse cursor, selected feature, feature id, list of points and description.</returns>
        GetPointsResult GetPoints(ObjectSelectionType featureType = ObjectSelectionType.HoverObjectMesh);

        /// <summary>
        /// Takes a measurement with a 6D measurement device
        /// </summary>
        /// <param name="target">Target type</param>
        /// <param name="averageTime">Take the measurement for a period of time and average the result</param>
        /// <param name="tipOffset">Offet the measurement to the tip</param>
        /// <returns>Returns MeasurePoseResult with a pose of measured object reference frame, and error values in mm.</returns>
        MeasurePoseResult MeasurePose(int target = -1, int averageTime = 0, List<double> tipOffset = null);

        /// <summary>
        /// Send a specific command to a RoboDK plugin. The command and value (optional) must be handled by your plugin
        /// </summary>
        /// <param name="pluginName">The plugin name must match the PluginName() implementation in the RoboDK plugin</param>
        /// <param name="command">Specific command handled by your plugin</param>
        /// <param name="value">Specific value (optional) handled by your plugin</param>
        /// <returns>Returns the result as a string.</returns>
        string PluginCommand(string pluginName, string command, string value);

        /// <summary>
        /// Load or unload the specified plugin (path to DLL, dylib or SO file). If the plugin is already loaded it will unload the plugin and reload it. Pass an empty plugin name to reload all plugins
        /// </summary>
        /// <param name="pluginName">The name of the plugin or path (if it is not in the default directory)</param>
        /// <param name="operation">Type of operation (load, unload, reload)</param>
        /// <returns>Returns boolean result of operation.</returns>
        bool PluginLoad(string pluginName, PluginOperation operation = PluginOperation.Load);

        /// <summary>
        ///     Retrieve the simulation time (in seconds). Time of 0 seconds starts with the first time this function is called.
        ///     The simulation time changes depending on the simulation speed.
        ///     The simulation time is usually faster than the real time (5 times by default)
        /// </summary>
        /// <returns>Returns the simulation time in seconds.</returns>
        double GetSimulationTime();

        /// <summary>
        ///     Add a simulated spray gun that allows projecting particles to a part.
        ///     This is useful to simulate applications such as: arc welding, spot welding, 3D printing, painting, inspection or robot machining to verify the trace
        /// </summary>
        /// <param name="tool">Active tool (null for auto detect)</param>
        /// <param name="referenceObject">Object in active reference frame (null for auto detect)</param>
        /// <param name="parameters">A string specifying the behavior of the simulated particles</param>
        /// <param name="points">Provide the volume as a list of points as described in the sample macro SprayOn.py</param>
        /// <param name="geometry">Provide a list of points describing triangles to define a specific particle geometry</param>
        /// <returns>Returns ID of the spray gun.</returns>
        int SprayAdd(IItem tool = null, IItem referenceObject = null, string parameters = "", Mat points = null, Mat geometry = null);

        /// <summary>
        /// Stops simulating a spray gun. This will clear the simulated particles
        /// </summary>
        /// <param name="sprayId">Spray ID (value returned by SprayAdd). Leave the default -1 to apply to all simulated sprays</param>
        /// <returns>Returns result code of the operation.</returns>
        int SprayClear(int sprayId = -1);

        /// <summary>
        /// Gets statistics from all simulated spray guns or a specific spray gun
        /// </summary>
        /// <param name="data">Extra data output</param>
        /// <param name="sprayId">Spray ID (value returned by SprayAdd). Leave the default -1 to apply to all simulated sprays</param>
        /// <returns>Returns statistics string.</returns>
        string SprayGetStats(out Mat data, int sprayId = -1);

        /// <summary>
        /// Sets the state of a simulated spray gun (ON or OFF)
        /// </summary>
        /// <param name="state">Set to SprayGunStates.SprayOn or SprayGunStates.SprayOff</param>
        /// <param name="sprayId">Spray ID (value returned by SprayAdd). Leave the default -1 to apply to all simulated sprays</param>
        /// <returns>Returns result code of the operation.</returns>
        int SpraySetState(SprayGunStates state = SprayGunStates.SprayOn, int sprayId = -1);

        /// <summary>
        ///     Sets the relative positions (poses) of a list of items with respect to their parent.
        ///     For example, the position of an object/frame/target with respect to its parent.
        ///     Use this function instead of SetPose() for faster speed.
        /// </summary>
        /// <param name="items">List of items</param>
        /// <param name="poses">List of poses for each item</param>
        void SetPoses(List<IItem> items, List<Mat> poses);

        /// <summary>
        ///     Set the absolute positions (poses) of a list of items with respect to the station reference.
        ///     For example, the position of an object/frame/target with respect to its parent.
        ///     Use this function instead of SetPoseAbs() for faster speed.
        /// </summary>
        /// <param name="items">List of items</param>
        /// <param name="poses">List of poses for each item</param>        
        void SetPosesAbs(List<IItem> items, List<Mat> poses);

        /// <summary>
        ///     Displays a sequence of joints
        /// </summary>
        /// <param name="sequence">joint sequence as a 6xN matrix or instruction sequence as a 7xN matrix</param>
        void ShowSequence(Mat sequence);

        /// <summary>
        ///     Displays a sequence of joints or poses
        /// </summary>
        /// <param name="joints">List of joint arrays</param>
        /// <param name="poses">List of poses</param>
        /// <param name="flags">Display options</param>
        /// <param name="timeout">Display timeout, in milliseconds (default: -1)</param>        
        void ShowSequence(List<double[]> joints = null, List<Mat> poses = null, SequenceDisplayFlags flags = SequenceDisplayFlags.Default, int timeout = -1);

        #endregion
    }
}