#ifndef IROBODK_H
#define IROBODK_H


#include "robodktypes.h"
#include <QString>


/// <summary>
/// This class is the iterface to the RoboDK API. With the RoboDK API you can automate certain tasks and operate on items.
/// Interactions with items in the station tree are made through Items (IItem).
/// An item is an object in the RoboDK tree (it can be either a robot, an object, a tool, a frame, a program, ...).
/// </summary>
class IRoboDK {

public:

    virtual ~IRoboDK(){}

public:

    /// Instruction types for programs
    enum TypeInstruction {
        /// Invalid instruction.
        INS_TYPE_INVALID = -1,

        /// Linear or joint movement instruction.
        INS_TYPE_MOVE = 0,

        /// Circular movement instruction.
        INS_TYPE_MOVEC = 1,

        /// Set speed instruction.
        INS_TYPE_CHANGESPEED = 2,

        /// Set reference frame instruction.
        INS_TYPE_CHANGEFRAME = 3,

        /// Set the tool (TCP) instruction.
        INS_TYPE_CHANGETOOL = 4,

        /// Set the robot instruction (obsolete).
        INS_TYPE_CHANGEROBOT = 5,

        /// Pause instruction.
        INS_TYPE_PAUSE = 6,

        /// Simulation event instruction.
        INS_TYPE_EVENT = 7,

        /// Program call or raw code output.
        INS_TYPE_CODE = 8,

        /// Display message on the teach pendant.
        INS_TYPE_PRINT = 9
    };

    /// Movement types
    enum TypeMovement {
        /// Invalid robot movement.
        MOVE_TYPE_INVALID = -1,

        /// Joint axes movement (MoveJ).
        MOVE_TYPE_JOINT = 1,

        /// Linear movement (MoveL).
        MOVE_TYPE_LINEAR = 2,

        /// Circular movement (MoveC).
        MOVE_TYPE_CIRCULAR = 3,

        /// Linear search function
        MOVE_TYPE_LINEARSEARCH = 4
    };

    /// Script execution types used by IRoboDK.setRunMode and IRoboDK.RunMode
    enum TypeRunMode {
        /// Performs the simulation moving the robot (default)
        RUNMODE_SIMULATE = 1,

        /// Performs a quick check to validate the robot movements.
        RUNMODE_QUICKVALIDATE = 2,

        /// Makes the robot program.
        RUNMODE_MAKE_ROBOTPROG = 3,

        /// Makes the robot program and updates it to the robot.
        RUNMODE_MAKE_ROBOTPROG_AND_UPLOAD = 4,

        /// Makes the robot program and starts it on the robot (independently from the PC).
        RUNMODE_MAKE_ROBOTPROG_AND_START = 5,

        /// Moves the real robot from the PC (PC is the client, the robot behaves like a server).
        RUNMODE_RUN_ROBOT = 6
    };

    /// Program execution type
    enum TypeProgramRun {
        /// Set the robot program to run on the simulator.
        PROGRAM_RUN_ON_SIMULATOR = 1,

        /// Set the robot program to run on the robot.
        PROGRAM_RUN_ON_ROBOT = 2
    };

    /// TCP calibration types
    enum TypeCalibrateTCP{

        /// Calibrate the TCP by poses touching the same point.
        CALIBRATE_TCP_BY_POINT = 0,

        /// Calibrate the TCP by poses touching the same plane.
        CALIBRATE_TCP_BY_PLANE = 1
    };

    /// Reference frame calibration types
    enum TypeCalibrateFrame {
        /// Calibrate by 3 points: [X, X+, Y+] (p1 on X axis).
        CALIBRATE_FRAME_3P_P1_ON_X = 0,

        /// Calibrate by 3 points: [Origin, X+, XY+] (p1 is origin).
        CALIBRATE_FRAME_3P_P1_ORIGIN = 1,

        /// Calibrate by 6 points.
        CALIBRATE_FRAME_6P = 2,

        /// Calibrate turntable.
        CALIBRATE_TURNTABLE = 3,

        /// Calibrate a 2 axis turntable
        CALIBRATE_TURNTABLE_2X = 4
    };

    /// projection types for AddCurve
    enum TypeProjection {
        /// No curve projection
        PROJECTION_NONE                = 0,

        /// The projection will the closest point on the surface.
        PROJECTION_CLOSEST             = 1,

        /// The projection will be done along the normal.
        PROJECTION_ALONG_NORMAL        = 2,

        /// The projection will be done along the normal. Furthermore, the normal will be recalculated according to the surface normal.
        PROJECTION_ALONG_NORMAL_RECALC = 3,

        /// The projection will be the closest point on the surface and the normals will be recalculated.
        PROJECTION_CLOSEST_RECALC      = 4,

        /// The normals are recalculated according to the surface normal of the closest projection. The points are not changed.
        PROJECTION_RECALC              = 5
    };

    /// Euler angles type
    enum TypeEuler {

        /// joints.
        JOINT_FORMAT      = -1,

        /// Staubli, Mecademic.
        EULER_RX_RYp_RZpp = 0,

        /// ABB RobotStudio.
        EULER_RZ_RYp_RXpp = 1,

        /// Kawasaki, Adept, Staubli.
        EULER_RZ_RYp_RZpp = 2,

        /// CATIA, SolidWorks.
        EULER_RZ_RXp_RZpp = 3,

        /// Fanuc, Kuka, Motoman, Nachi.
        EULER_RX_RY_RZ    = 4,

        /// CRS.
        EULER_RZ_RY_RX    = 5,

        /// ABB Rapid.
        EULER_QUEATERNION = 6
    };

    /// State of the RoboDK window
    enum TypeWindowState {
        /// Hide the RoboDK window. RoboDK will keep running as a process.
        WINDOWSTATE_HIDDEN = -1,

        /// Display the RoboDK window.
        WINDOWSTATE_SHOW = 0,

        /// Minimize the RoboDK window.
        WINDOWSTATE_MINIMIZED = 1,

        /// Display the RoboDK window in a normal state (not maximized)
        WINDOWSTATE_NORMAL = 2,

        /// Maximize the RoboDK Window.
        WINDOWSTATE_MAXIMIZED = 3,

        /// Make the RoboDK window fullscreen.
        WINDOWSTATE_FULLSCREEN = 4,

        /// Display RoboDK in cinema mode (hide the toolbar and the menu).
        WINDOWSTATE_CINEMA = 5,

        /// Display RoboDK in cinema mode and fullscreen.
        WINDOWSTATE_FULLSCREEN_CINEMA = 6,

        /// Display RoboDK in video mode
        WINDOWSTATE_VIDEO = 7
    };

    /// Instruction program call type:
    enum TypeInstructionCall {
        /// Instruction to call a program.
        INSTRUCTION_CALL_PROGRAM = 0,

        /// Instructio to insert raw code (this will not provoke a program call).
        INSTRUCTION_INSERT_CODE = 1,

        /// Instruction to start a parallel thread. Program execution will continue and also trigger a thread.
        INSTRUCTION_START_THREAD = 2,

        /// Comment output.
        INSTRUCTION_COMMENT = 3,

        /// Instruction to pop up a message on the robot teach pendant.
        INSTRUCTION_SHOW_MESSAGE = 4
    };

    /// Object features for selection and filtering
    enum TypeFeature {
        /// No selection
        FEATURE_NONE = 0,

        /// Surface selection
        FEATURE_SURFACE = 1,

        /// Curve selection
        FEATURE_CURVE = 2,

        /// Point selection
        FEATURE_POINT = 3
    };

    /// Spray gun simulation:
    enum TypeSpray {
        /// Activate the spray simulation
        SPRAY_OFF = 0,
        SPRAY_ON = 1
    };

    /// Collision checking state
    enum TypeCollision {
        /// Do not use collision checking
        COLLISION_OFF = 0,

        /// Use collision checking
        COLLISION_ON = 1
    };

    /// RoboDK Window Flags
    enum TypeFlagsRoboDK {
        /// Allow using the RoboDK station tree.
        FLAG_ROBODK_TREE_ACTIVE = 1,

        /// Allow using the 3D navigation.
        FLAG_ROBODK_3DVIEW_ACTIVE = 2,

        /// Allow left clicks on the 3D navigation screen.
        FLAG_ROBODK_LEFT_CLICK = 4,

        /// Allow right clicks on the 3D navigation screen.
        FLAG_ROBODK_RIGHT_CLICK = 8,

        /// Allow double clicks on the 3D navigation screen.
        FLAG_ROBODK_DOUBLE_CLICK = 16,

        /// Enable/display the menu bar.
        FLAG_ROBODK_MENU_ACTIVE = 32,

        /// Enable the file menu (FLAG_ROBODK_MENU_ACTIVE must be allowed).
        FLAG_ROBODK_MENUFILE_ACTIVE = 64,

        /// Enable the edit menu (FLAG_ROBODK_MENU_ACTIVE must be allowed).
        FLAG_ROBODK_MENUEDIT_ACTIVE = 128,

        /// Enable the program menu (FLAG_ROBODK_MENU_ACTIVE must be allowed).
        FLAG_ROBODK_MENUPROGRAM_ACTIVE = 256,

        /// Enable the tools menu (FLAG_ROBODK_MENU_ACTIVE must be allowed).
        FLAG_ROBODK_MENUTOOLS_ACTIVE = 512,

        /// Enable the utilities menu (FLAG_ROBODK_MENU_ACTIVE must be allowed).
        FLAG_ROBODK_MENUUTILITIES_ACTIVE = 1024,

        /// Enable the connect menu (FLAG_ROBODK_MENU_ACTIVE must be allowed).
        FLAG_ROBODK_MENUCONNECT_ACTIVE = 2048,

        /// Allow using keyboard shortcuts.
        FLAG_ROBODK_WINDOWKEYS_ACTIVE = 4096,

        /// Make the tree visible
        FLAG_ROBODK_TREE_VISIBLE = 8192,

        /// Make the reference frames visible
        FLAG_ROBODK_REFERENCES_VISIBLE = 16384,

        /// Make the statusbar visible
        FLAG_ROBODK_STATUSBAR_VISIBLE = 32768,

        /// Disallow everything.
        FLAG_ROBODK_NONE = 0,

        /// Allow everything (default).
        FLAG_ROBODK_ALL = 0xFFFF,

        /// Allow using the full menu.
        FLAG_ROBODK_MENU_ACTIVE_ALL = FLAG_ROBODK_MENU_ACTIVE | FLAG_ROBODK_MENUFILE_ACTIVE | FLAG_ROBODK_MENUEDIT_ACTIVE | FLAG_ROBODK_MENUPROGRAM_ACTIVE | FLAG_ROBODK_MENUTOOLS_ACTIVE | FLAG_ROBODK_MENUUTILITIES_ACTIVE | FLAG_ROBODK_MENUCONNECT_ACTIVE
    };

    /// RoboDK Item Flags
    enum TypeFlagsItem {
        /// Allow selecting RoboDK items.
        FLAG_ITEM_SELECTABLE = 1,

        /// Allow modifying RoboDK items.
        FLAG_ITEM_EDITABLE = 2,

        /// Allow draggin an item.
        FLAG_ITEM_DRAGALLOWED = 4,

        /// Allow dropping to an item.
        FLAG_ITEM_DROPALLOWED = 8,

        /// Enable the item.
        FLAG_ITEM_ENABLED = 32,

        /// Allow having nested items, expand and collapse the item.
        FLAG_ITEM_AUTOTRISTATE = 64,

        /// Do not allow adding nested items.
        FLAG_ITEM_NOCHILDREN = 128,
        FLAG_ITEM_USERTRISTATE = 256,

        /// Disallow everything.
        FLAG_ITEM_NONE = 0,

        /// Allow everything (default).
        FLAG_ITEM_ALL = 64 + 32 + 8 + 4 + 2 + 1
    };

    /// Different render levels to update the screen
    enum TypeRender {
        /// Do not render the screen.
        RenderNone = 0,

        /// Redisplay the screen.
        RenderScreen = 1,

        /// Update all positions of modified items (robots, references and objects) and their child items.
        RenderUpdateOnly = 2,

        /// Provokes an update and then screen display (full update and render).
        RenderComplete = 0xff
    };

    /// Display geometry in 3D, with respect to the station coordinate system. This should be called using \ref DrawGeometry ONLY when a \ref PluginEvent of type \ref EventRender is triggered.
    enum TypeDraw {
        /// Draw surfaces
        DrawTriangles = 1,

        /// Draw lines
        DrawLines = 2,

        /// Draw points
        DrawPoints = 3,

        /// Draw spheres
        DrawSpheres = 4
    };


public:

    /// <summary>
    /// Returns an item by its name. If there is no exact match it will return the last closest match.
    /// </summary>
    /// <param name="name">Item name</param>
    /// <param name="itemtype">Filter by item type RoboDK.ITEM_TYPE_...</param>
    /// <returns>Item or nullptr if no item was found</returns>
    virtual Item getItem(const QString &name, int itemtype = -1)=0;

    /// <summary>
    /// Returns a list of items (list of names or Items) of all available items in the currently open station in RoboDK.
    /// Optionally, use a filter to return specific items (example: getItemListNames(filter = ITEM_TYPE_ROBOT))
    /// </summary>
    /// <param name="filter">ITEM_TYPE_...</param>
    /// <returns>List of item names</returns>
    virtual QStringList getItemListNames(int filter = -1)=0;

    /// <summary>
    /// Returns a list of items (list of names or pointers) of all available items in the currently open station in RoboDK.
    /// Optionally, use a filter to return specific items (example: getItemListNames(filter = ITEM_CASE_ROBOT))
    /// </summary>
    /// <param name="filter">ITEM_TYPE</param>
    /// <returns>List of items with a match</returns>
    virtual QList<Item> getItemList(int filter = -1)=0;

    ///
    /// \brief Check if an item is valid (not null and available in the open station)
    /// \param item_check Item to check
    /// \return True if the item exists, false otherwise
    virtual bool Valid(const Item item_check)=0;

    /// <summary>
    /// Shows a RoboDK popup to select one object from the open RoboDK station.
    /// An item type can be specified to filter desired items. If no type is specified, all items are selectable.
    /// </summary>
    /// <param name="message">Message to show in the pop up</param>
    /// <param name="itemtype">optionally filter by RoboDK.ITEM_TYPE_*</param>
    /// <returns>Picked item or nullptr if the user selected Cancel</returns>
    virtual Item ItemUserPick(const QString &message = "Pick one item", int itemtype = -1)=0;

    /// <summary>
    /// Shows a RoboDK popup to select one object from the open RoboDK station.
    /// You can provide a few items to choose from and, optionally, a selected index.
    /// </summary>
    /// <param name="message">Message to show in the pop up</param>
    /// <param name="list_choices">Items to choose from</param>
    /// <param name="id_selected">Selected id from list_choices if we want to select an item</param>
    /// <returns>Picked item or nullptr if the user selected Cancel</returns>
    virtual Item ItemUserPick(const QString &message, const QList<Item> &list_choices, int id_selected=-1)=0;

    /// <summary>
    /// Shows or raises the RoboDK window.
    /// </summary>
    virtual void ShowRoboDK()=0;

    /// <summary>
    /// Hides the RoboDK window. RoboDK will continue running in the background.
    /// </summary>
    virtual void HideRoboDK()=0;

    /// <summary>
    /// Closes RoboDK window and finishes RoboDK execution
    /// </summary>
    virtual void CloseRoboDK()=0;

    /// <summary>
    /// Return the vesion of RoboDK as a 4 digit string: Major.Minor.Revision.Build
    /// </summary>
    virtual QString Version()=0;

    /// <summary>
    /// Set the state of the RoboDK window
    /// </summary>
    /// <param name="windowstate"></param>
    virtual void setWindowState(int windowstate = WINDOWSTATE_NORMAL)=0;

    /// <summary>
    /// Update the RoboDK flags. RoboDK flags allow defining how much access the user has to certain RoboDK features. Use FLAG_ROBODK_* variables to set one or more flags.
    /// </summary>
    /// <param name="flags">state of the window(FLAG_ROBODK_*)</param>
    virtual void setFlagsRoboDK(int flags = FLAG_ROBODK_ALL)=0;

    /// <summary>
    /// Update item flags. Item flags allow defining how much access the user has to item-specific features. Use FLAG_ITEM_* flags to set one or more flags.
    /// </summary>
    /// <param name="item"></param>
    /// <param name="flags">New flags</param>
    virtual void setFlagsItem(int flags = FLAG_ITEM_ALL, Item item=nullptr)=0;

    /// <summary>
    /// Retrieve current item flags. Item flags allow defining how much access the user has to item-specific features. Use FLAG_ITEM_* flags to set one or more flags.
    /// </summary>
    /// <param name="item"></param>
    /// <returns></returns>
    virtual int getFlagsItem(Item item)=0;


    /// <summary>
    /// Show a message in RoboDK (it can be blocking or non blocking in the status bar)
    /// </summary>
    /// <param name="message">Message to display</param>
    /// <param name="popup">Set to true to make the message blocking or set to false to make it non blocking</param>
    virtual void ShowMessage(const QString &message, bool popup = true)=0;

    /// <summary>
    /// Loads a file and attaches it to parent. It can be any file supported by RoboDK.
    /// </summary>
    /// <param name="filename">Absolute path of the file.</param>
    /// <param name="parent">Parent to attach. Leave empty for new stations or to load an object at the station root.</param>
    /// <returns>Newly added object. Check with item.Valid() for a successful load.</returns>
    virtual Item AddFile(const QString &filename, const Item parent=nullptr)=0;

    /// <summary>
    /// Save an item to a file. If no item is provided, the open station is saved.
    /// </summary>
    /// <param name="filename">Absolute path to save the file</param>
    /// <param name="itemsave">Object or station to save. Leave empty to automatically save the current station.</param>
    virtual void Save(const QString &filename, const Item itemsave=nullptr)=0;

    /// <summary>
    /// Adds a shape provided triangle coordinates. Triangles must be provided as a list of vertices. A vertex normal can be provided optionally.
    /// </summary>
    /// <param name="trianglePoints">List of vertices grouped by triangles (3xN or 6xN matrix, N must be multiple of 3 because vertices must be stacked by groups of 3)</param>
    /// <param name="addTo">item to attach the newly added geometry (optional). Leave empty to create a new object.</param>
    /// <param name="shapeOverride">Set to true to replace any other existing geometry</param>
    /// <param name="color">Optionally specify the color as RGBA [0-1]</param>
    /// <returns>Added or modified item</returns>
    virtual Item AddShape(const tMatrix2D *trianglePoints, Item addTo = nullptr, bool shapeOverride = false, tColor *color = nullptr)=0;


    /// <summary>
    /// Adds a curve provided point coordinates. The provided points must be a list of vertices. A vertex normal can be provided optionally.
    /// </summary>
    /// <param name="curve_points">matrix 3xN or 6xN -> N must be multiple of 3</param>
    /// <param name="reference_object">object to add the curve and/or project the curve to the surface</param>
    /// <param name="add_to_ref">If True, the curve will be added as part of the object in the RoboDK item tree (a reference object must be provided)</param>
    /// <param name="projection_type">Type of projection. For example: PROJECTION_ALONG_NORMAL_RECALC will project along the point normal and recalculate the normal vector on the surface projected.</param>
    /// <returns>added object/curve (null if failed)</returns>
    virtual Item AddCurve(const tMatrix2D *curvePoints, Item referenceObject = nullptr,bool addToRef = false,int ProjectionType = PROJECTION_ALONG_NORMAL_RECALC)=0;


    /// <summary>
    /// Adds a list of points to an object. The provided points must be a list of vertices. A vertex normal can be provided optionally.
    /// </summary>
    /// <param name="points">list of points as a matrix (3xN matrix, or 6xN to provide point normals as ijk vectors)</param>
    /// <param name="reference_object">item to attach the newly added geometry (optional)</param>
    /// <param name="add_to_ref">If True, the points will be added as part of the object in the RoboDK item tree (a reference object must be provided)</param>
    /// <param name="projection_type">Type of projection.Use the PROJECTION_* flags.</param>
    /// <returns>added object/shape (0 if failed)</returns>
    virtual Item AddPoints(const tMatrix2D *points, Item referenceObject = nullptr, bool addToRef = false, int ProjectionType =  PROJECTION_ALONG_NORMAL_RECALC)=0;

    /// <summary>
    /// Projects a list of points given its coordinates. The provided points must be a list of [XYZ] coordinates. Optionally, a vertex normal can be provided [XYZijk].
    /// </summary>
    /// <param name="points">Matrix 3xN or 6xN: list of points to project. This matrix will contain the modified points after the projection.</param>
    /// <param name="object_project">Object to project.</param>
    /// <param name="projection_type">Type of projection. For example: PROJECTION_ALONG_NORMAL_RECALC will project along the point normal and recalculate the normal vector on the surface projected.</param>
    /// <returns>True if projection succeeded, False if input is not correct</returns>
    virtual bool ProjectPoints(tMatrix2D *points, Item objectProject, int ProjectionType = PROJECTION_ALONG_NORMAL_RECALC)=0;

    /// <summary>
    /// Close the current station without asking to save.
    /// </summary>
    virtual void CloseStation()=0;

    /// <summary>
    /// Adds a new target that can be reached with a robot.
    /// </summary>
    /// <param name="name">Name of the target.</param>
    /// <param name="itemparent">Parent to attach to (such as a frame).</param>
    /// <param name="itemrobot">Main robot that will be used to go to self target.</param>
    /// <returns>the new target created</returns>
    virtual Item AddTarget(const QString &name, Item itemparent = nullptr, Item itemrobot = nullptr)=0;

    /// <summary>
    /// Adds a new Frame that can be referenced by a robot.
    /// </summary>
    /// <param name="name">Name of the reference frame.</param>
    /// <param name="itemparent">Parent to attach to (such as the robot base frame).</param>
    /// <returns>The new reference frame created.</returns>
    virtual Item AddFrame(const QString &name, Item itemparent = nullptr)=0;

    /// <summary>
    /// Adds a new Frame that can be referenced by a robot.
    /// </summary>
    /// <param name="name">Name of the program.</param>
    /// <param name="itemrobot">Robot that will be used.</param>
    /// <returns>the new program created</returns>
    virtual Item AddProgram(const QString &name, Item itemrobot = nullptr)=0;

    /// <summary>
    /// Add a new empty station. It returns the station item added.
    /// </summary>
    /// <param name="name">Name of the station (the title bar will be renamed to match the station name).</param>
    virtual Item AddStation(QString name)=0;

    /// <summary>
    /// Add a new robot machining project. Machining projects can also be used for 3D printing, following curves and following points.
    /// It returns the newly created Item containing the project settings.
    /// Tip: Use the macro /RoboDK/Library/Macros/MoveRobotThroughLine.py to see an example that creates a new "curve follow project" given a list of points to follow(Option 4).
    /// </summary>
    /// <param name="name">Name of the project settings.</param>
    /// <param name="itemrobot">Robot to use for the project settings(optional). It is not required to specify the robot if only one robot or mechanism is available in the RoboDK station.</param>
    /// <returns></returns>
    virtual Item AddMachiningProject(QString name = "Curve follow settings", Item itemrobot = nullptr)=0;

    /// <summary>
    /// Returns the list of open stations in RoboDK.
    /// </summary>
    /// <returns></returns>
    virtual QList<Item> getOpenStations()=0;

    /// <summary>
    /// Set the active station (project currently visible).
    /// </summary>
    /// <param name="station">station item, it can be previously loaded as an RDK file.</param>
    virtual void setActiveStation(Item stn)=0;

    /// <summary>
    /// Returns the active station item (station currently visible).
    /// </summary>
    /// <returns></returns>
    virtual Item getActiveStation()=0;

    /// <summary>
    /// Adds a function call in the program output. RoboDK will handle the syntax when the code is generated for a specific robot. If the program exists it will also run the program in simulate mode.
    /// </summary>
    /// <param name="function_w_params">Function name with parameters (if any).</param>
    /// <returns></returns>
    virtual int RunProgram(const QString &function_w_params)=0;

    /// <summary>
    /// Adds code to run in the program output. If the program exists it will also run the program in simulation mode.
    /// </summary>
    /// <param name="code"></param>
    /// <param name="code_is_fcn_call"></param>
    /// <returns></returns>
    virtual int RunCode(const QString &code, bool code_is_fcn_call = false)=0;

    /// <summary>
    /// Shows a message or a comment in the output robot program.
    /// </summary>
    /// <param name="message"></param>
    /// <param name="message_is_comment"></param>
    virtual void RunMessage(const QString &message, bool message_is_comment = false)=0;

    /// <summary>
    /// Update the scene.
    /// </summary>
    /// <param name="flags">Set to RenderComplete for a full update or RenderScreen to redraw the scene without internally updating dependencies.</param>
    virtual void Render(int flags=RenderComplete)=0;

    /// <summary>
    /// Check if an object is fully inside another one.
    /// </summary>
    /// <param name="object_inside"></param>
    /// <param name="object_parent"></param>
    /// <returns>Returns true if object_inside is inside the object_parent</returns>
    virtual bool IsInside(Item object_inside, Item object_parent)=0;

    /// <summary>
    /// Turn collision checking ON or OFF (COLLISION_OFF/COLLISION_OFF) according to the collision map. If collision checking is activated it returns the number of pairs of objects that are currently in a collision state.
    /// </summary>
    /// <param name="check_state"></param>
    /// <returns>Number of pairs of objects in a collision state (0 if no collisions).</returns>
    virtual int setCollisionActive(int check_state = COLLISION_ON)=0;

    /// <summary>
    /// Set collision checking ON or OFF (COLLISION_ON/COLLISION_OFF) for a specific pair of objects. This allows altering the collision map for Collision checking.
    /// Specify the link id for robots or moving mechanisms (id 0 is the base).
    /// </summary>
    /// <param name="check_state">Set to COLLISION_ON or COLLISION_OFF</param>
    /// <param name="item1">Item 1</param>
    /// <param name="item2">Item 2</param>
    /// <param name="id1">Joint id for Item 1 (if Item 1 is a robot or a mechanism)</param>
    /// <param name="id2">Joint id for Item 2 (if Item 2 is a robot or a mechanism)</param>
    /// <returns>Returns true if succeeded. Returns false if setting the pair failed (wrong id was provided)</returns>
    virtual bool setCollisionActivePair(int check_state, Item item1, Item item2, int id1 = 0, int id2 = 0)=0;

    /// <summary>
    /// Returns the number of pairs of objects that are currently in a collision state. If collision checking is not active it will calculate collision checking.
    /// </summary>
    /// <returns>0 if no collisions are found.</returns>
    virtual int Collisions()=0;

    /// <summary>
    /// Returns 1 if item1 and item2 collided. Otherwise returns 0.
    /// </summary>
    /// <param name="item1"></param>
    /// <param name="item2"></param>
    /// <returns>0 if no collisions are found.</returns>
    virtual int Collision(Item item1, Item item2)=0;

    /// <summary>
    /// Return the list of items that are in a collision state. This function can be used after calling Collisions() to retrieve the items that are in a collision state.
    /// </summary>
    /// <param name="link_id_list">List of robot link IDs that are in collision (0 for objects and tools).</param>
    /// <returns>List of items that are in a collision state.</returns>
    virtual QList<Item> getCollisionItems(QList<int> *link_id_list=nullptr)=0;

    /// <summary>
    /// Sets the current simulation speed. Set the speed to 1 for a real-time simulation. The slowest speed allowed is 0.001 times the real speed. Set to a high value (>100) for fast simulation results.
    /// </summary>
    /// <param name="speed">Simulation speed ratio (1 means real time simulation)</param>
    virtual void setSimulationSpeed(double speed)=0;

    /// <summary>
    /// Gets the current simulation speed. Set the speed to 1 for a real-time simulation.
    /// </summary>
    /// <returns>Simulation speed ratio (1 means real time simulation)</returns>
    virtual double SimulationSpeed()=0;

    /// <summary>
    /// Sets the behavior of the RoboDK API. By default, RoboDK shows the path simulation for movement instructions (run_mode=1=RUNMODE_SIMULATE).
    /// Setting the run_mode to RUNMODE_QUICKVALIDATE allows performing a quick check to see if the path is feasible.
    /// if robot.Connect() is used, RUNMODE_RUN_FROM_PC is selected automatically.
    /// </summary>
    /// <param name="run_mode">int = RUNMODE
    /// RUNMODE_SIMULATE=1        performs the simulation moving the robot (default)
    /// RUNMODE_QUICKVALIDATE=2   performs a quick check to validate the robot movements
    /// RUNMODE_MAKE_ROBOTPROG=3  makes the robot program
    /// RUNMODE_RUN_REAL=4        moves the real robot is it is connected</param>
    virtual void setRunMode(int run_mode = 1)=0;

    /// <summary>
    /// Returns the behavior of the RoboDK API. By default, RoboDK shows the path simulation for movement instructions (run_mode=1).
    /// </summary>
    /// <returns>int = RUNMODE
    /// RUNMODE_SIMULATE=1        performs the simulation moving the robot (default)
    /// RUNMODE_QUICKVALIDATE=2   performs a quick check to validate the robot movements
    /// RUNMODE_MAKE_ROBOTPROG=3  makes the robot program
    /// RUNMODE_RUN_REAL=4        moves the real robot is it is connected</returns>
    virtual int RunMode()=0;

    /// <summary>
    /// Gets all the user parameters from the open RoboDK station.
    /// The parameters can also be modified by right clicking the station and selecting "shared parameters"
    /// User parameters can be added or modified by the user
    /// </summary>
    /// <returns>List of pairs of strings as parameter-value (list of a list)</returns>
    virtual QList<QPair<QString, QString> > getParams()=0;

    /// <summary>
    /// Gets a global or a user parameter from the open RoboDK station.
    /// The parameters can also be modified by right clicking the station and selecting "shared parameters"
    /// Some available parameters:
    /// PATH_OPENSTATION = folder path of the current .stn file
    /// FILE_OPENSTATION = file path of the current .stn file
    /// PATH_DESKTOP = folder path of the user's folder
    /// Other parameters can be added or modified by the user
    /// </summary>
    /// <param name="param">RoboDK parameter</param>
    /// <returns>Parameter value.</returns>
    virtual QString getParam(const QString &param)=0;


    /// <summary>
    /// Sets a global parameter from the RoboDK station. If the parameters exists, it will be modified. If not, it will be added to the station.
    /// The parameters can also be modified by right clicking the station and selecting "shared parameters".
    /// </summary>
    /// <param name="param">RoboDK parameter</param>
    /// <param name="value">value</param>
    /// <returns></returns>
    virtual void setParam(const QString &param, const QString &value)=0;

    /// <summary>
    /// Send a special command. These commands are meant to have a specific effect in RoboDK, such as changing a specific setting or provoke specific events.
    /// </summary>
    /// <param name="cmd">Command Name, such as Trace, Threads or Window.</param>
    /// <param name="value">Comand value (optional, not all commands require a value)</param>
    /// <returns>Command result.</returns>
    virtual QString Command(const QString &cmd, const QString &value="")=0;


    // --- add calibrate reference, calibrate tool, measure tracker, etc...


    /// <summary>
    /// Takes a laser tracker measurement with respect to its own reference frame. If an estimate point is provided, the laser tracker will first move to those coordinates. If search is True, the tracker will search for a target.
    /// </summary>
    /// <param name="xyz"></param>
    /// <param name="estimate"></param>
    /// <param name="search">True to search near the estimated value.</param>
    /// <returns>True if successful.</returns>
    virtual bool LaserTrackerMeasure(tXYZ xyz, const tXYZ estimate, bool search = false)=0;

    /// <summary>
    /// Takes a pose measurement (requires a supported measurement system).
    /// </summary>
    /// <param name="pose">Measured pose</param>
    /// <param name="pose">Additional returned data [visible targets, button state, average error, max error]</param>
    /// <param name="target">Target type</param>
    /// <param name="time_avg_ms">Average the pose from the buffer</param>
    /// <param name="tool_tip">XYZ position of the tool tip for average calculation</param>
    /// <returns>True if successful, false if unable to measure.</returns>
    virtual bool MeasurePose(Mat *pose, double data[10], int target=-1, int time_avg_ms=0, const tXYZ tool_tip=nullptr)=0;

    /// <summary>
    /// Checks the collision between a line and any objects in the station. The line is composed by 2 points.
    /// Returns the collided item. Use Item.Valid() to check if there was a valid collision.
    /// </summary>
    /// <param name="p1">Start point of the line (absolute coordinates).</param>
    /// <param name="p2">End point of the line (absolute coordinates).</param>
    /// <param name="xyz_collision">Collided point.</param>
    /// <returns>True if collision found.</returns>
    virtual bool CollisionLine(const tXYZ p1, const tXYZ p2)=0;

    /// <summary>
    /// Calibrate a tool (TCP) given a number of points or calibration joints. Important: If the robot is calibrated, provide joint values to maximize accuracy.
    /// </summary>
    /// <param name="poses_joints">matrix of poses in a given format or a list of joints</param>
    /// <param name="error_stats">stats[mean, standard deviation, max] - Output error stats summary.</param>
    /// <param name="format">Euler format. Optionally, use JOINT_FORMAT and provide the robot.</param>
    /// <param name="algorithm">type of algorithm (by point, plane, ...)</param>
    /// <param name="robot">Robot used for the identification (if using joint values).</param>
    /// <returns>TCP as [x, y, z] - calculated TCP</returns>
    virtual void CalibrateTool(const tMatrix2D *poses_joints, tXYZ tcp_xyz, int format=EULER_RX_RY_RZ, int algorithm=CALIBRATE_TCP_BY_POINT, Item robot=nullptr, double *error_stats=nullptr)=0;

    /// <summary>
    /// Calibrate a Reference Frame given a list of points or joint values. Important: If the robot is calibrated, provide joint values to maximize accuracy.
    /// </summary>
    /// <param name="joints">points as a 3xN matrix or nDOFsxN) - List of points or a list of robot joints.</param>
    /// <param name="method">type of algorithm(by point, plane, ...) CALIBRATE_FRAME_...</param>
    /// <param name="use_joints">use points or joint values. The robot item must be provided if joint values is used.</param>
    /// <param name="robot">Robot used for the identification (if using joint values).</param>
    /// <returns></returns>
    virtual Mat CalibrateReference(const tMatrix2D *poses_joints, int method = CALIBRATE_FRAME_3P_P1_ON_X, bool use_joints = false, Item robot = nullptr)=0;

    /// <summary>
    /// Defines the name of the program when the program is generated. It is also possible to specify the name of the post processor as well as the folder to save the program.
    /// This method must be called before any program output is generated (before any robot movement or other instruction).
    /// </summary>
    /// <param name="progname">Name of the program.</param>
    /// <param name="defaultfolder">Folder to save the program, leave empty to use the default program folder.</param>
    /// <param name="postprocessor">Name of the post processor (for a post processor in C:/RoboDK/Posts/Fanuc_post.py it is possible to provide "Fanuc_post.py" or simply "Fanuc_post").</param>
    /// <param name="robot">Robot to link.</param>
    /// <returns></returns>
    virtual bool ProgramStart(const QString &progname, const QString &defaultfolder = "", const QString &postprocessor = "", Item robot = nullptr)=0;


    /// <summary>
    /// Set the pose of the wold reference frame with respect to the user view (camera/screen).
    /// </summary>
    /// <param name="pose">View pose.</param>
    virtual void setViewPose(const Mat &pose)=0;

    /// <summary>
    /// Get the pose of the wold reference frame with respect to the user view (camera/screen).
    /// </summary>
    /// <returns>View pose.</returns>
    virtual Mat ViewPose()=0;

    /// <summary>
    /// Set the nominal robot parameters.
    /// </summary>
    /// <param name="robot"></param>
    /// <param name="dhm">D-H Modified table (Denavit Hartenberg Modified)</param>
    /// <param name="poseBase"></param>
    /// <param name="poseTool"></param>
    /// <returns></returns>
    virtual bool SetRobotParams(Item robot,tMatrix2D dhm, Mat poseBase, Mat poseTool)=0;

    /// <summary>
    /// Returns the position of the cursor as XYZ coordinates (by default), or the 3D position of a given set of 2D coordinates of the window (x & y coordinates in pixels from the top left corner)
    /// The XYZ coordinates returned are given with respect to the RoboDK station(absolute reference).
    /// If no coordinates are provided, the current position of the cursor is retrieved.
    /// </summary>
    /// <param name="x">X coordinate in pixels</param>
    /// <param name="y">Y coordinate in pixels</param>
    /// <param name="xyzStation"></param>
    /// <returns>Item under the mouse cursor.</returns>
    virtual Item getCursorXYZ(int x = -1, int y = -1, tXYZ xyzStation = nullptr)=0;

    /// <summary>
    /// Returns the license as a readable string (same name shown in the RoboDK's title bar, on top of the main menu).
    /// </summary>
    /// <returns></returns>
    virtual QString License()=0;

    /// <summary>
    /// Returns the list of items selected (it can be one or more items).
    /// </summary>
    /// <returns>List of selected items.</returns>
    virtual QList<Item> Selection()=0;

    /// <summary>
    /// Show the popup menu to create the ISO9283 path for position accuracy, repeatability and path accuracy performance testing.
    /// </summary>
    /// <param name="robot"></param>
    /// <param name="center">XYZ position of the center of the cube with respect to the robot base, in mm.</param>
    /// <param name="side">Cube side, in mm.</param>
    /// <returns>IS9283 Program or nullptr if the user cancelled.</returns>
    virtual Item Popup_ISO9283_CubeProgram(Item robot=nullptr, tXYZ center=nullptr, double side=-1)=0;


    /// <summary>
    /// Gets a plugin defined parameter from the open RoboDK station.
    /// Saved parameters can be viewed or deleted by right clicking the station and selecting "shared parameters".
    /// </summary>
    /// <param name="param">RoboDK data parameter</param>
    /// <returns>Data value.</returns>
    virtual QByteArray getData(const QString &param)=0;


    /// <summary>
    /// Sets a data parameter saved with the RoboDK station. If the parameters exists, it will be updated. If not, it will be added to the station.
    /// Saved parameters can be viewed or deleted by right clicking the station and selecting "shared parameters".
    /// </summary>
    /// <param name="param">RoboDK data parameter name</param>
    /// <param name="value">data value</param>
    /// <returns></returns>
    virtual void setData(const QString &param, const QByteArray &value)=0;


    /// \brief Returns the status of collision checking (COLLISION_ON=1 if the user want to have collision checking or COLLISION_OFF=0 if the user disabled collision checking).
    /// \return COLLISION_ON=1 or COLLISION_OFF=0
    virtual int CollisionActive()=0;

    /// <summary>
    /// Draw geometry in the RoboDK's 3D view. This function must be called only inside a \ref PluginEvent of type \ref EventRender is triggered.
    /// </summary>
    /// <param name="drawtype">type of geometry (triangles, lines, points or spheres)</param>
    /// <param name="vtx_pointer">Pointer to an array of vertexs in mm, with respect to the RoboDK station (absolute reference)</param>
    /// <param name="vtx_size">Size of the geometry (number of triangles, number of vertex lines or number of points)</param>
    /// <param name="color">Color as RGBA [0,1]</param>
    /// <param name="geo_size">Size of the lines or points (ignored for surfaces)</param>
    /// <param name="vtx_normals">vertex normals as unitary vectors (optional, only used to draw surfaces)</param>
    /// <returns>true if successful, false if input is not correct or build does not support drawing in double or single precision floating point</returns>
    virtual bool DrawGeometry(int drawtype, float *vtx_pointer, int vtx_size, float color[4], float geo_size=2.0, float *vtx_normals=nullptr)=0;

    /// <summary>
    /// Draw a texture in the RoboDK's 3D view. This function must be called only inside a \ref PluginEvent of type \ref EventRender is triggered.
    /// </summary>
    /// <param name="image">Pointer to an image in RGBA format (it is important to have it in RGBA)</param>
    /// <param name="vtx_pointer">Pointer to an array of vertexs in mm, with respect to the RoboDK station (absolute reference)</param>
    /// <param name="texture_coords">Texture coordinates (2D coordinates per vertex)</param>
    /// <param name="num_triangles">Size of the geometry (number of triangles)</param>
    /// <param name="vtx_normals">vertex normals as unitary vectors (optional)</param>
    /// <returns>true if successful, false if input is not correct or build does not support drawing in double or single precision floating point</returns>
    virtual bool DrawTexture(const QImage *image, const float *vtx_pointer, const float *texture_coords, int num_triangles, float *vtx_normals=nullptr)=0;


    //-----------------------------------------------------
    // added after 2020-08-21 with version RoboDK 5.1.0

    /// <summary>
    /// Set the selection in the tree
    /// </summary>
    virtual void setSelection(const QList<Item> &listitems)=0;

    /// <summary>
    /// Set the interactive mode to define the behavior when navigating and selecting items in RoboDK's 3D view.
    /// </summary>
    /// <param name="mode_type">The mode type defines what accion occurs when the 3D view is selected (Select object, Pan, Rotate, Zoom, Move Objects, ...)</param>
    /// <param name="default_ref_flags">When a movement is specified, we can provide what motion we allow by default with respect to the coordinate system (set apropriate flags)</param>
    /// <param name="custom_object">Provide a list of optional items to customize the move behavior for these specific items (important: the length of custom_ref_flags must match)</param>
    /// <param name="custom_ref_flags">Provide a matching list of flags to customize the movement behavior for specific items</param>
    virtual void setInteractiveMode(int mode_type, int default_ref_flags, const QList<Item> *custom_object=nullptr, int custom_ref_flags=0)=0;

    /// <summary>
    /// Load or unload the specified plugin (path to DLL, dylib or SO file). If the plugin is already loaded it will unload the plugin and reload it. Pass an empty plugin_name to reload all plugins.
    /// </summary>
    /// <param name="plugin_name">Name of the plugin or path (if it is not in the default directory.</param>
    /// <param name="load">load the plugin (1/default) or unload (0)</param>
    virtual void PluginLoad(const QString &plugin_name="", int load=1)=0;

    /// <summary>
    /// Send a specific command to a RoboDK plugin. The command and value (optional) must be handled by your plugin. It returns the result as a string.
    /// </summary>
    /// <param name="plugin_name">The plugin name must match the PluginName() implementation in the RoboDK plugin.</param>
    /// <param name="plugin_command">Specific command handled by your plugin.</param>
    /// <param name="value">Specific value (optional) handled by your plugin.</param>
    virtual QString PluginCommand(const QString &plugin_name="", const QString &plugin_command="", const QString &value="")=0;

    /// <summary>
    /// Gets a user parameter from the open RoboDK station (Bytes type).
    /// Special QByteArray parameters can be added or modified by plugins and scripts (not by the user).
    /// </summary>
    /// <param name="param">RoboDK parameter</param>
    /// <returns>Parameter data.</returns>
    virtual QByteArray getParamBytes(const QString &param)=0;


    /// <summary>
    /// Gets a user parameter from the open RoboDK station (Bytes type).
    /// Special QByteArray parameters can be added or modified by plugins and scripts (not by the user).
    /// </summary>
    /// <param name="param">RoboDK parameter</param>
    /// <param name="value">Data value</param>
    virtual void setParamBytes(const QString &param, const QByteArray &value)=0;

    /// <summary>
    /// Takes a measurement with a 6D measurement device. It returns two poses, the base reference frame and the measured object reference frame. Status is negative if the measurement failed. extra data is [error_avg, error_max] in mm, if we are averaging a pose.
    /// </summary>
    /// <param name="pose1">Pose of the main object</param>
    /// <param name="pose2">Pose of the reference object</param>
    /// <param name="npoints1">Number of points visible for object 1</param>
    /// <param name="npoints2">Number of points visible for object 2t</param>
    /// <param name="status">Status flag</param>
    /// <param name="data">Additional data from the device</param>
    /// <param name="time_avg">Take the measurement for a period of time and average the result.</param>
    /// <param name="tip_xyz">Offet the measurement to the tip.</param>
    /// <returns>Status flags.</returns>
    virtual int StereoCamera_Measure(Mat pose1, Mat pose2, int &npoints1, int &npoints2, double *data=nullptr, float time_avg=0, const tXYZ tip_xyz=nullptr)=0;

    /// <summary>
    /// Takes a measurement with a 6D measurement device. It returns two poses, the base reference frame and the measured object reference frame. Status is negative if the measurement failed. extra data is [error_avg, error_max] in mm, if we are averaging a pose.
    /// </summary>
    /// <param name="type">Type of the mechanism</param>
    /// <param name="list_obj">list of object items that build the robot</param>
    /// <param name="parameters">robot parameters in the same order as shown in the RoboDK menu: Utilities-Build Mechanism or robot</param>
    /// <param name="joints_build">Current state of the robot (joint axes) to build the robot</param>
    /// <param name="joints_home">joints for the home position (it can be changed later)</param>
    /// <param name="joints_senses">Sense of rotation of each axis (+1 or -1)</param>
    /// <param name="joints_lim_low">Lower joint limits</param>
    /// <param name="joints_lim_high">Upper joint limits</param>
    /// <param name="base">Base pose offset (robot pose)</param>
    /// <param name="tool">Tool flange pose offset</param>
    /// <param name="name">Robot name</param>
    /// <param name="robot">Modify existing robot</param>
    /// <returns>New robot or mechanism created.</returns>
    virtual Item BuildMechanism(int type, const QList<Item> &list_obj, const double *parameters, const tJoints &joints_build, const tJoints &joints_home, const tJoints &joints_senses, const tJoints &joints_lim_low, const tJoints &joints_lim_high, const Mat base, const Mat tool, const QString &name, Item robot=nullptr)=0;


    //-----------------------------------------------------
    // added after 2021-09-17 with version RoboDK 5.3.0


    /// <summary>
    /// Open a simulated 2D camera view. Returns a handle pointer that can be used in case more than one simulated view is used.
    /// </summary>
    /// <returns>Camera item</returns>
    virtual Item Cam2D_Add(const Item attach_to, const QString &params="")=0;

    /// <summary>
    /// Take a snapshot from a simulated camera view and save it to a file. Returns 1 if success, 0 otherwise.
    /// </summary>
    /// <returns>Valid QImage if a file was not provided or an invalid/empty QImage if we are saving the file to disk</returns>
    virtual QImage Cam2D_Snapshot(const QString &file, const Item camera=nullptr, const QString &params="")=0;



    /// <summary>
    /// Merge multiple object items as one. Source objects are not deleted and a new object is created.
    /// </summary>
    virtual Item MergeItems(const QList<Item> &listitems)=0;

    /*

    SprayAdd
    */

};


//Q_DECLARE_INTERFACE(IRoboDK, "RoboDK.IRoboDK")

#endif // IROBODK_H
