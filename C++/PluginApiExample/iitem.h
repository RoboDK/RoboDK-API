#ifndef IITEM_H
#define IITEM_H

#include <QString>
#include "robodktypes.h"
#include "irobodk.h"


/// \brief The Item class represents an item in RoboDK station. An item can be a robot, a frame, a tool, an object, a target, ... any item visible in the <strong>station tree</strong>.
/// An item can also be seen as a node where other items can be attached to (child items).
/// Every item has one parent item/node and can have one or more child items/nodes
///
/// \image html station-tree.png
class IItem {
public:

    /// Tree item types
    enum TypeItem {
        /// Any item type
        ITEM_TYPE_ANY = -1,

        /// Item of type station (RDK file)
        ITEM_TYPE_STATION = 1,

        /// Item of type robot (.robot file)
        ITEM_TYPE_ROBOT = 2,

        /// Item of type reference frame
        ITEM_TYPE_FRAME = 3,

        /// Item of type tool (.tool)
        ITEM_TYPE_TOOL = 4,

        /// Item of type object (.stl, .step or .iges for example)
        ITEM_TYPE_OBJECT = 5,

        /// Target item
        ITEM_TYPE_TARGET = 6,

        /// Program item
        ITEM_TYPE_PROGRAM = 8,

        /// Instruction
        ITEM_TYPE_INSTRUCTION = 9,

        /// Python script
        ITEM_TYPE_PROGRAM_PYTHON = 10,

        /// Robot machining project, curve follow, point follow or 3D printing project
        ITEM_TYPE_MACHINING = 11,

        /// Ballbar validation project
        ITEM_TYPE_BALLBARVALIDATION = 12,

        /// Robot calibration project
        ITEM_TYPE_CALIBPROJECT = 13,

        /// Robot path accuracy validation project
        ITEM_TYPE_VALID_ISO9283 = 14,

        /// Folders
        ITEM_TYPE_FOLDER=17,

        /// Robot arms only
        ITEM_TYPE_ROBOT_ARM=18,

        /// Camera
        ITEM_TYPE_CAMERA=19,

        /// Generic custom items (customizable)
        ITEM_TYPE_GENERIC=20,

        /// Mechanisms and axes of up to 3 degrees of freedom
        ITEM_TYPE_ROBOT_AXES=21
    };

public:

    virtual ~IItem(){}

    /// Item type (object, robot, tool, reference, robot machining project, ...)
    virtual int Type()=0;

    /// <summary>
    /// Save a station, a robot, a tool or an object to a file
    /// </summary>
    /// <param name="filename">path and file name</param>
    virtual bool Save(const QString &filename)=0;

    /// <summary>
    /// Deletes an item and its childs from the station.
    /// </summary>
    virtual void Delete()=0;

    /// <summary>
    /// Attaches the item to a new parent while maintaining the relative position with its parent. The absolute position is changed.
    /// </summary>
    /// <param name="parent"></param>
    virtual void setParent(Item parent)=0;

    /// <summary>
    /// Attaches the item to another parent while maintaining the current absolute position in the station.
    /// The relationship between this item and its parent is changed to maintain the abosolute position.
    /// </summary>
    /// <param name="parent">parent item to attach this item to</param>
    virtual void setParentStatic(Item parent)=0;

    /// <summary>
    /// Return the parent item of this item
    /// </summary>
    /// <returns>Parent item</returns>
    virtual Item Parent()=0;

    /// <summary>
    /// Returns a list of the item childs that are attached to the provided item.
    /// Exceptionally, if Childs is called on a program it will return the list of subprograms called by this program.
    /// </summary>
    /// <returns>item x n: list of child items</returns>
    virtual QList<Item> Childs()=0;

    /// <summary>
    /// Returns 1 if the item is visible, otherwise, returns 0
    /// </summary>
    /// <returns>true if visible, false if not visible</returns>
    virtual bool Visible()=0;

    /// <summary>
    /// Sets the item visiblity status
    /// </summary>
    /// <param name="visible"></param>
    /// <param name="visible_reference">set the visible reference frame (1) or not visible (0)</param>
    virtual void setVisible(bool visible, int visible_frame = -1)=0;

    /// <summary>
    /// Returns the name of an item. The name of the item is always displayed in the RoboDK station tree
    /// </summary>
    /// <returns>name of the item</returns>
    virtual QString Name()=0;

    /// <summary>
    /// Set the name of a RoboDK item.
    /// </summary>
    /// <param name="name">New item name</param>
    virtual void setName(const QString &name)=0;

    // Do not use this function. Just check if the item is nullptr (for example, using ItemValid())
    //virtual bool Valid()=0;

    /// <summary>
    /// Send a special command. These commands are meant to have a specific effect in RoboDK, such as changing a global setting or provoke specific events.
    /// </summary>
    /// <param name="cmd">Command Name, such as Trace, Threads or Window.</param>
    /// <param name="value">Comand value (optional, not all commands require a value)</param>
    /// <returns>Response ("OK" if success)</returns>
    virtual QString Command(const QString &cmd, const QString &value="")=0;

    /// <summary>
    /// Sets the local position (pose) of an object, target or reference frame. For example, the position of an object/frame/target with respect to its parent.
    /// If a robot is provided, it will set the pose of the end efector.
    /// </summary>
    /// <param name="pose">4x4 homogeneous matrix</param>
    virtual bool setPose(const Mat pose)=0;

    /// <summary>
    /// Returns the local position (pose) of an object, target or reference frame. For example, the position of an object/frame/target with respect to its parent.
    /// If a robot is provided, it will get the pose of the end efector
    /// </summary>
    /// <returns>4x4 homogeneous matrix (pose)</returns>
    virtual Mat Pose()=0;

    /// <summary>
    /// Sets the position (pose) the object geometry with respect to its own reference frame. This procedure works for tools and objects.
    /// </summary>
    /// <param name="pose">4x4 homogeneous matrix</param>
    /// <param name="apply_movement">Apply the movement to the inner geometry and not as a pose shift</param>
    virtual void setGeometryPose(Mat pose, bool apply_transf=false)=0;

    /// <summary>
    /// Returns the position (pose) the object geometry with respect to its own reference frame. This procedure works for tools and objects.
    /// </summary>
    /// <returns>4x4 homogeneous matrix (pose)</returns>
    virtual Mat GeometryPose()=0;

    /// <summary>
    /// Returns the tool pose of an item. If a robot is provided it will get the tool pose of the active tool held by the robot.
    /// </summary>
    /// <returns>4x4 homogeneous matrix (pose)</returns>
    virtual Mat PoseTool()=0;

    /// <summary>
    /// Returns the reference frame pose of an item. If a robot is provided it will get the tool pose of the active reference frame used by the robot.
    /// </summary>
    /// <returns>4x4 homogeneous matrix (pose)</returns>
    virtual Mat PoseFrame()=0;

    /// <summary>
    /// Sets the reference frame of a robot(user frame). The frame can be either an item or a pose.
    /// If "frame" is an item, it links the robot to the frame item. If frame is a pose, it updates the linked pose of the robot frame (with respect to the robot reference frame).
    /// </summary>
    /// <param name="frame_pose">4x4 homogeneous matrix (pose)</param>
    virtual void setPoseFrame(const Mat frame_pose)=0;

    /// <summary>
    /// Sets the tool of a robot or a tool object (Tool Center Point, or TCP). The tool pose can be either an item or a 4x4 Matrix.
    /// If the item is a tool, it links the robot to the tool item.If tool is a pose, it updates the current robot TCP.
    /// </summary>
    /// <param name="pose">4x4 homogeneous matrix (pose)</param>
    virtual void setPoseFrame(const Item frame_item)=0;

    /// <summary>
    /// Sets the tool of a robot or a tool object (Tool Center Point, or TCP). The tool pose can be either an item or a 4x4 Matrix.
    /// If the item is a tool, it links the robot to the tool item.If tool is a pose, it updates the current robot TCP.
    /// </summary>
    /// <param name="tool_pose">4x4 homogeneous matrix (pose)</param>
    virtual void setPoseTool(const Mat tool_pose)=0;

    /// <summary>
    /// Sets the tool of a robot or a tool object (Tool Center Point, or TCP). The tool pose can be either an item or a 4x4 Matrix.
    /// If the item is a tool, it links the robot to the tool item.If tool is a pose, it updates the current robot TCP.
    /// </summary>
    /// <param name="tool_item">Tool item</param>
    virtual void setPoseTool(const Item tool_item)=0;


    /// <summary>
    /// Sets the global position (pose) of an item. For example, the position of an object/frame/target with respect to the station origin.
    /// </summary>
    /// <param name="pose">4x4 homogeneous matrix (pose)</param>
    virtual void setPoseAbs(const Mat pose)=0;

    /// <summary>
    /// Returns the global position (pose) of an item. For example, the position of an object/frame/target with respect to the station origin.
    /// </summary>
    /// <returns>4x4 homogeneous matrix (pose)</returns>
    virtual Mat PoseAbs()=0;

    /// <summary>
    /// Set the color of an object, tool or robot. A color must in the format COLOR=[R, G, B,(A = 1)] where all values range from 0 to 1.
    /// Optionally set the RBG to -1 to modify the Alpha channel (transparency)
    /// </summary>
    /// <param name="clr">color to set</param>
    virtual void setColor(const tColor &clr)=0;

//---------- add more


    /// <summary>
    /// Apply a scale to an object to make it bigger or smaller.
    /// The scale can be uniform (if scale is a float value) or per axis (if scale is a vector).
    /// </summary>
    virtual void Scale(double scale)=0;    

    /// <summary>
    /// Apply a per-axis scale to an object to make it bigger or smaller.
    /// The scale can be uniform (if scale is a float value) or per axis (if scale is a vector).
    /// </summary>
    /// <param name="scale">scale to apply as [scale_x, scale_y, scale_z]</param>
    virtual void Scale(double scale_xyz[3])=0;

    /// <summary>
    /// Sets a target as a cartesian target. A cartesian target moves to cartesian coordinates.
    /// </summary>
    virtual void setAsCartesianTarget()=0;

    /// <summary>
    /// Sets a target as a joint target. A joint target moves to a joints position without regarding the cartesian coordinates.
    /// </summary>
    virtual void setAsJointTarget()=0;

    /// <summary>
    /// Returns True if a target is a joint target (green icon). Otherwise, the target is a Cartesian target (red icon).
    /// </summary>
    virtual bool isJointTarget()=0;

    /// <summary>
    /// Returns the current joints of a robot or the joints of a target. If the item is a cartesian target, it returns the preferred joints (configuration) to go to that cartesian position.
    /// </summary>
    /// <returns>double x n: joints matrix</returns>
    virtual tJoints Joints()=0;

    /// <summary>
    /// Returns the home joints of a robot. These joints can be manually set in the robot "Parameters" menu, then select "Set home position"
    /// </summary>
    /// <returns>joint values for the home position</returns>
    virtual tJoints JointsHome()=0;

    /// <summary>
    /// Set robot joints for the home position
    /// </summary>
    virtual void setJointsHome(const tJoints &jnts)=0;

    /// <summary>
    /// Returns an item pointer to the geometry of a robot link. This is useful to show/hide certain robot links or alter their geometry.
    /// </summary>
    /// <param name="link_id">link index(0 for the robot base, 1 for the first link, ...)</param>
    /// <returns>Internal geometry item</returns>
    virtual Item ObjectLink(int link_id = 0)=0;    

    /// <summary>
    /// Returns an item linked to a robot, object, tool, program or robot machining project. This is useful to retrieve the relationship between programs, robots, tools and other specific projects.
    /// </summary>
    /// <param name="type_linked">type of linked object to retrieve</param>
    /// <returns>Linked object</returns>
    virtual Item getLink(int type_linked = ITEM_TYPE_ROBOT)=0;

    /// <summary>
    /// Set robot joints or the joints of a target
    /// </summary>
    virtual void setJoints(const tJoints &jnts)=0;

    /// <summary>
    /// Retrieve the joint limits of a robot
    /// </summary>
    virtual int JointLimits(tJoints *lower_limits, tJoints *upper_limits)=0;

    /// <summary>
    /// Set the joint limits of a robot
    /// </summary>
    virtual int setJointLimits(const tJoints &lower_limits, const tJoints &upper_limits)=0;

    /// <summary>
    /// Sets the robot of a program or a target. You must set the robot linked to a program or a target every time you copy paste these objects.
    /// If the robot is not provided, the first available robot will be chosen automatically.
    /// </summary>
    /// <param name="robot">Robot item</param>
    virtual void setRobot(const Item &robot)=0;

    /// <summary>
    /// Adds an empty tool to the robot provided the tool pose (4x4 Matrix) and the tool name.
    /// </summary>
    /// <param name="tool_pose">TCP as a 4x4 Matrix (pose of the tool frame)</param>
    /// <param name="tool_name">New tool name</param>
    /// <returns>new item created</returns>
    virtual Item AddTool(const Mat &tool_pose, const QString &tool_name = "New TCP")=0;

    /// <summary>
    /// Computes the forward kinematics of the robot for the provided joints. The tool and the reference frame are not taken into account.
    /// </summary>
    /// <param name="joints"></param>
    /// <returns>4x4 homogeneous matrix: pose of the robot flange with respect to the robot base</returns>
    virtual Mat SolveFK(const tJoints &joints, const Mat *tool_pose=nullptr, const Mat *reference_pose=nullptr)=0;

    /// <summary>
    /// Returns the robot configuration state for a set of robot joints.
    /// </summary>
    /// <param name="joints">array of joints</param>
    /// <param name="config">configuration status as [REAR, LOWERARM, FLIP]</returns>
    virtual void JointsConfig(const tJoints &joints, tConfig config)=0;

    /// <summary>
    /// Computes the inverse kinematics for the specified robot and pose. The joints returned are the closest to the current robot configuration (see SolveIK_All())
    /// </summary>
    /// <param name="pose">4x4 matrix -> pose of the robot flange with respect to the robot base frame</param>
    /// <param name="joints_close">Aproximate joints solution to choose among the possible solutions. Leave this value empty to return the closest match to the current robot position.</param>
    /// <param name="tool_pose">Optionally provide a tool pose, otherwise, the robot flange is used. Tip: use robot.PoseTool() to retrieve the active robot tool.</param>
    /// <param name="reference_pose">Optionally provide a reference pose, otherwise, the robot base is used. Tip: use robot.PoseFrame() to retrieve the active robot reference frame.</param>
    /// <returns>array of joints</returns>
    virtual tJoints SolveIK(const Mat &pose, const tJoints *joints_close=nullptr, const Mat *tool_pose=nullptr, const Mat *reference_pose=nullptr)=0;

    /// <summary>
    /// Computes the inverse kinematics for the specified robot and pose. The function returns all available joint solutions as a 2D matrix.
    /// </summary>
    /// <param name="pose">4x4 matrix -> pose of the robot tool with respect to the robot frame</param>
    /// <param name="tool_pose">Optionally provide a tool pose, otherwise, the robot flange is used. Tip: use robot.PoseTool() to retrieve the active robot tool.</param>
    /// <param name="reference_pose">Optionally provide a reference pose, otherwise, the robot base is used. Tip: use robot.PoseFrame() to retrieve the active robot reference frame.</param>
    /// <returns>double x n x m -> joint list (2D matrix)</returns>
    virtual QList<tJoints> SolveIK_All(const Mat &pose, const Mat *tool_pose=nullptr, const Mat *reference_pose=nullptr)=0;

    /// <summary>
    /// Connect to a real robot using the corresponding robot driver.
    /// </summary>
    /// <param name="robot_ip">IP of the robot to connect. Leave empty to use the one defined in RoboDK</param>
    /// <returns>true if connected successfully, false if connection failed</returns>
    virtual bool Connect(const QString &robot_ip = "")=0;

    /// <summary>
    /// Disconnect from a real robot (when the robot driver is used)
    /// </summary>
    /// <returns>true if disconnected successfully, false if it failed. It can fail if it was previously disconnected manually for example.</returns>
    virtual bool Disconnect()=0;


    /// <summary>
    /// Add a joint move to a program or move a robot to a target item ("Move Joint" mode). This function does not block.
    /// </summary>
    /// <param name="target">Target to move to as a target item (RoboDK target item)</param>
    virtual bool MoveJ(const Item &itemtarget)=0;

    /// <summary>
    /// Add a joint move to a program or move a robot to a joint target ("Move Joint" mode). This function does not block.
    /// </summary>
    /// <param name="target">Robot joints to move to</param>
    virtual bool MoveJ(const tJoints &joints)=0;

    /// <summary>
    /// Add a joint move to a program or move a robot to a pose target ("Move Joint" mode). This function does not block.
    /// </summary>
    /// <param name="target">Pose target to move to. It must be a 4x4 Homogeneous matrix</param>
    virtual bool MoveJ(const Mat &target)=0;

    /// <summary>
    /// Add a linear move to a program or move a robot to a target item ("Move Linear" mode). This function does not block.
    /// </summary>
    /// <param name="itemtarget">Target to move to as a target item (RoboDK target item)</param>
    virtual bool MoveL(const Item &itemtarget)=0;

    /// <summary>
    /// Add a linear move to a program or move a robot to a joint target ("Move Linear" mode). This function does not block.
    /// </summary>
    /// <param name="joints">Robot joints to move to</param>
    virtual bool MoveL(const tJoints &joints)=0;

    /// <summary>
    /// Add a linear move to a program or move a robot to a pose target  ("Move Linear" mode). This function does not block.
    /// </summary>
    /// <param name="target">Pose target to move to. It must be a 4x4 Homogeneous matrix</param>
    virtual bool MoveL(const Mat &target)=0;

    /// <summary>
    /// Add a circular move to a program or move a robot through an arc given two target items ("Move Circular" mode). This function does not block.
    /// </summary>
    /// <param name="itemtarget1">Intermediate target to move to as a target item (target item)</param>
    /// <param name="itemtarget2">Final target to move to as a target item (target item)</param>
    virtual bool MoveC(const Item &itemtarget1, const Item &itemtarget2)=0;

    /// <summary>
    /// Add a circular move to a program or move a robot through an arc given two joint targets ("Move Circular" mode). This function does not block.
    /// </summary>
    /// <param name="joints1">Intermediate joint target to move to.</param>
    /// <param name="joints2">Final joint target to move to.</param>
    virtual bool MoveC(const tJoints &joints1, const tJoints &joints2)=0;

    /// <summary>
    /// Add a circular move to a program or move a robot through an arc given two pose targets ("Move Circular" mode). This function does not block.
    /// </summary>
    /// <param name="target1">Intermediate pose target to move to. It must be a 4x4 Homogeneous matrix</param>
    /// <param name="target2">Final pose target to move to. It must be a 4x4 Homogeneous matrix</param>
    virtual bool MoveC(const Mat &target1, const Mat &target2)=0;

    /// <summary>
    /// Checks if a joint movement is possible and, optionally, free of collisions.
    /// </summary>
    /// <param name="j1">Start joints</param>
    /// <param name="j2">Destination joints</param>
    /// <param name="minstep_deg">Maximum joint step in degrees. If this value is not provided it will use the path step defined in Tools-Options-Motion (degrees).</param>
    /// <returns>collision : returns 0 if the movement is free of collision. Otherwise it returns the number of pairs of objects that collided if there was a collision.</returns>
    virtual int MoveJ_Test(const tJoints &j1, const tJoints &j2, double minstep_deg = -1)=0;

    /// <summary>
    /// Checks if a linear movement is free of issues and, optionally, collisions.
    /// </summary>
    /// <param name="joints1">Start joints</param>
    /// <param name="pose2">Destination pose (active tool with respect to the active reference frame)</param>
    /// <param name="minstep_mm">Maximum joint step in mm. If this value is not provided it will use the path step defined in Tools-Options-Motion (mm).</param>
    /// <returns>collision : returns 0 if the movement is free of collision. Otherwise it returns the number of pairs of objects that collided if there was a collision.</returns>
    virtual int MoveL_Test(const tJoints &joints1, const Mat &pose2, double minstep_mm = -1)=0;

    /// <summary>
    /// Sets the speed and/or the acceleration of a robot.
    /// </summary>
    /// <param name="speed_linear">linear speed in mm/s (-1 = no change)</param>
    /// <param name="accel_linear">linear acceleration in mm/s2 (-1 = no change)</param>
    /// <param name="speed_joints">joint speed in deg/s (-1 = no change)</param>
    /// <param name="accel_joints">joint acceleration in deg/s2 (-1 = no change)</param>
    virtual void setSpeed(double speed_linear, double accel_linear = -1, double speed_joints = -1, double accel_joints = -1)=0;

    /// <summary>
    /// Sets the robot movement smoothing accuracy (also known as zone data value).
    /// </summary>
    /// <param name="rounding_mm">Rounding value (double) (robot dependent, set to -1 for accurate/fine movements)</param>
    virtual void setRounding(double zonedata)=0;

    /// <summary>
    /// Displays a sequence of joints
    /// </summary>
    /// <param name="sequence">joint sequence as a 6xN matrix or instruction sequence as a 7xN matrix</param>
    virtual void ShowSequence(tMatrix2D *sequence)=0;

    /// <summary>
    /// Checks if a robot or program is currently running (busy or moving)
    /// </summary>
    /// <returns>busy status (true=moving, false=stopped)</returns>
    virtual bool Busy()=0;

    /// <summary>
    /// Stops a program or a robot
    /// </summary>
    virtual void Stop()=0;

    /// <summary>
    /// Saves a program to a file.
    /// </summary>
    /// <param name="filename">File path of the program</param>
    /// <param name="run_mode">RUNMODE_MAKE_ROBOTPROG to generate the program file.Alternatively, Use RUNMODE_MAKE_ROBOTPROG_AND_UPLOAD or RUNMODE_MAKE_ROBOTPROG_AND_START to transfer the program through FTP and execute the program.</param>
    /// <returns>Transfer succeeded is True if there was a successful program transfer (if RUNMODE_MAKE_ROBOTPROG_AND_UPLOAD or RUNMODE_MAKE_ROBOTPROG_AND_START are used)</returns>
    virtual bool MakeProgram(const QString &filename)=0;


    /// <summary>
    /// Sets if the program will be run in simulation mode or on the real robot (same flag obtained when right clicking a program and checking/unchecking the "Run on robot" option).
    /// Use: "PROGRAM_RUN_ON_SIMULATOR" to set the program to run on the simulator only or "PROGRAM_RUN_ON_ROBOT" to force the program to run on the robot.
    /// </summary>
    /// <returns>number of instructions that can be executed</returns>
    virtual void setRunType(int program_run_type)=0;

    /// <summary>
    /// Runs a program. It returns the number of instructions that can be executed successfully (a quick program check is performed before the program starts)
    /// This is a non-blocking call. Use IsBusy() to check if the program execution finished.
    /// Notes:
    /// if setRunMode(RUNMODE_SIMULATE) is used  -> the program will be simulated (default run mode)
    /// if setRunMode(RUNMODE_RUN_ROBOT) is used -> the program will run on the robot (default when RUNMODE_RUN_ROBOT is used)
    /// if setRunMode(RUNMODE_RUN_ROBOT) is used together with program.setRunType(PROGRAM_RUN_ON_ROBOT) -> the program will run sequentially on the robot the same way as if we right clicked the program and selected "Run on robot" in the RoboDK GUI
    /// </summary>
    /// <returns>True if successful</returns>
    virtual bool RunProgram(const QString &params = "")=0;

    /// <summary>
    /// Adds a program call, code, message or comment inside a program.
    /// </summary>
    /// <param name="code"><string of the code or program to run/param>
    /// <param name="run_type">INSTRUCTION_* variable to specify if the code is a progra</param>
    virtual int RunInstruction(const QString &code, int run_type = RoboDK::INSTRUCTION_CALL_PROGRAM)=0;

    /// <summary>
    /// Generates a pause instruction for a robot or a program when generating code. Set it to -1 (default) if you want the robot to stop and let the user resume the program anytime.
    /// </summary>
    /// <param name="time_ms">Time in milliseconds</param>
    virtual void Pause(double time_ms = -1)=0;


    /// <summary>
    /// Sets a variable (output) to a given value. This can also be used to set any variables to a desired value.
    /// </summary>
    /// <param name="io_var">io_var -> digital output (string or number)</param>
    /// <param name="io_value">io_value -> value (string or number)</param>
    virtual void setDO(const QString &io_var, const QString &io_value)=0;

    /// <summary>
    /// Waits for an input io_id to attain a given value io_value. Optionally, a timeout can be provided.
    /// </summary>
    /// <param name="io_var">io_var -> digital output (string or number)</param>
    /// <param name="io_value">io_value -> value (string or number)</param>
    /// <param name="timeout_ms">int (optional) -> timeout in miliseconds</param>
    virtual void waitDI(const QString &io_var, const QString &io_value, double timeout_ms = -1)=0;

    /// <summary>
    /// Add a custom instruction. This instruction will execute a Python file or an executable file.
    /// </summary>
    /// <param name="name"></param>
    /// <param name="path_run">path to run(relative to RoboDK/bin folder or absolute path)</param>
    /// <param name="path_icon">icon path(relative to RoboDK/bin folder or absolute path)</param>
    /// <param name="blocking">True if blocking, 0 if it is a non blocking executable trigger</param>
    /// <param name="cmd_run_on_robot">Command to run through the driver when connected to the robot</param>
    /// :param name: digital input (string or number)
    virtual void customInstruction(const QString &name, const QString &path_run, const QString &path_icon = "", bool blocking = true, const QString &cmd_run_on_robot = "")=0;

    /// <summary>
    /// Show or hide instruction items of a program in the RoboDK tree
    /// </summary>
    /// <param name="show"></param>
    virtual void ShowInstructions(bool visible=true)=0;

    /// <summary>
    /// Show or hide targets of a program in the RoboDK tree
    /// </summary>
    /// <param name="show"></param>
    virtual void ShowTargets(bool visible=true)=0;

    /// <summary>
    /// Returns the number of instructions of a program.
    /// </summary>
    /// <returns></returns>
    virtual int InstructionCount()=0;

    /// <summary>
    /// Returns the program instruction at position id
    /// </summary>
    /// <param name="ins_id"></param>
    /// <param name="name"></param>
    /// <param name="instype"></param>
    /// <param name="movetype"></param>
    /// <param name="isjointtarget"></param>
    /// <param name="target"></param>
    /// <param name="joints"></param>
    virtual void InstructionAt(int ins_id, QString &name, int &instype, int &movetype, bool &isjointtarget, Mat &target, tJoints &joints)=0;

    /// <summary>
    /// Sets the program instruction at position id
    /// </summary>
    /// <param name="ins_id"></param>
    /// <param name="name"></param>
    /// <param name="instype"></param>
    /// <param name="movetype"></param>
    /// <param name="isjointtarget"></param>
    /// <param name="target"></param>
    /// <param name="joints"></param>
    virtual void setInstruction(int ins_id, const QString &name, int instype, int movetype, bool isjointtarget, const Mat &target, const tJoints &joints)=0;

    /// <summary>
    /// Returns the list of program instructions as an MxN matrix, where N is the number of instructions and M equals to 1 plus the number of robot axes.
    /// </summary>
    /// <param name="instructions">the matrix of instructions</param>
    /// <returns>Returns 0 if success</returns>
    virtual int InstructionList(tMatrix2D *instructions)=0;

    /// <summary>
    /// Updates a program and returns the estimated time and the number of valid instructions.
    /// An update can also be applied to a robot machining project. The update is performed on the generated program.
    /// </summary>
    /// <param name="collision_check">check_collisions: Check collisions (COLLISION_ON -yes- or COLLISION_OFF -no-)</param>
    /// <param name="timeout_sec">Maximum time to wait for the update to complete (in seconds)</param>
    /// <param name="out_nins_time_dist">optional double array [3] = [valid_instructions, program_time, program_distance]</param>
    /// <param name="mm_step">Maximum step in millimeters for linear movements (millimeters). Set to -1 to use the default, as specified in Tools-Options-Motion.</param>
    /// <param name="deg_step">Maximum step for joint movements (degrees). Set to -1 to use the default, as specified in Tools-Options-Motion.</param>
    /// <returns>1.0 if there are no problems with the path or less than 1.0 if there is a problem in the path (ratio of problem)</returns>
    virtual double Update(double out_nins_time_dist[4], int collision_check = RoboDK::COLLISION_OFF, double mm_step = -1, double deg_step = -1)=0;

    /// <summary>
    /// Update the robot milling path input and parameters. Parameter input can be an NC file (G-code or APT file) or an object item in RoboDK. A curve or a point follow project will be automatically set up for a robot manufacturing project.
    /// <br>Tip: Use getLink() and setLink() to get/set the robot tool, reference frame, robot and program linked to the project.
    /// <br>Tip: Use setPose() and setJoints() to update the path to tool orientation or the preferred start joints.
    /// <br>Tip: Use setPoseTool() and setPoseFrame() to link to the corresponding tool and reference frames.
    /// @code
    /// Item object_curves = RDK->ItemUserPick("Select an object with curves or points to follow", RoboDK::ITEM_TYPE_OBJECT);
    /// if (!object_curves.Valid()){
    ///     // operation cancelled
    ///     return;
    /// }
    ///
    /// // Assuming ROBOT is a robot item
    /// Item project = RDK->AddMachiningProject("Curve1 Settings", ROBOT);
    ///
    /// // set the reference link:
    /// project.setPoseFrame(ROBOT->getLink(RoboDK::ITEM_TYPE_FRAME));
    ///
    /// // set the tool link:
    /// project.setPoseTool(ROBOT->getLink(RoboDK::ITEM_TYPE_TOOL));
    ///
    /// // set preferred start joints position (value automatically set by default)
    /// project.setJoints(ROBOT->JointsHome());
    ///
    /// // link the project to the part and provide additional settings
    /// QString additional_options = "RotZ_Range=45 RotZ_Step=5 NormalApproach=50 No_Update";
    ///
    /// project.setMachiningParameters("", object_curves, additional_options);
    /// // in this example:
    /// //RotZ_Range=45 RotZ_Step=5
    /// //allow a tool z rotation of +/- 45 deg by steps of 5 deg
    ///
    /// // NormalApproach=50
    /// //Use 50 mm as normal approach by default
    ///
    /// // No_Update
    /// // Do not attempt to solve the path. It can be later updated by running project.Update()
    /// @endcode
    /// </summary>
    /// <param name="ncfile">path to the NC (G-code/APT/Point cloud) file to load (optional)</param>
    /// <param name="part_obj">object holding curves or points to automatically set up a curve/point follow project (optional)</param>
    /// <param name="options">Additional options (optional)</param>
    /// <returns>Program (can be null it has not been updated). Use Update() to retrieve the result</returns>
    virtual Item setMachiningParameters(const QString &ncfile="", Item part_obj=nullptr, const QString &options="")=0;

    /// \brief Retrieve the robot connection status.
    /// \param msg pass a non null pointer to retrieve a readable message (same message seen in the roboto connection status bar)
    /// \return
    /// Robot connection status: 0 = ready  ;  > 0 = busy/working  ;  -1 = connection problems
    virtual int ConnectedState(QString *msg=nullptr)=0;

    /// \brief Returns true if the item is selected by the user (in the tree or the screen)
    /// \return
    virtual bool Selected()=0;

    /// \brief Returns true if the object is in a collision state (collision checking must be activated manually or using setCollisionActive. Alternatively, use RDK->Collisions() to update collision flags)
    /// \param id Optionally retrieve the index of the object (used for robot joints)
    /// \return
    virtual bool Collided(int *id=nullptr)=0;

    /// <summary>
    /// Check if a set of joints are valid
    /// </summary>
    virtual bool JointsValid(const tJoints &jnts)=0;    

    /// <summary>
    /// Get if the program will be run in simulation mode or on the real robot (same flag obtained when right clicking a program and checking/unchecking the "Run on robot" option).
    /// Use: "PROGRAM_RUN_ON_SIMULATOR" to set the program to run on the simulator only or "PROGRAM_RUN_ON_ROBOT" to force the program to run on the robot.
    /// </summary>
    /// <returns>number of instructions that can be executed</returns>
    virtual int RunType()=0;

    /// <summary>
    /// Scale an object given a per-axis scale. Optionally provide a transformation matrix before and after the scale takes place. If the transformation after scaling is not provided it will use the inverse transformation of the pre-scaled pose automatically.
    /// </summary>
    /// <param name="ins_id"></param>
    virtual bool Scale(const double scalexyz[3], const Mat *tr_pre_scale, const Mat *tr_post_scale=nullptr)=0;

    /// <summary>
    /// Returns the target item at the specified program instruction. It returns a null pointer if the instruction does not have a target or is not a movement instruction.
    /// </summary>
    /// <param name="ins_id"></param>
    virtual Item InstructionTargetAt(int ins_id)=0;

    // added with RoboDK 4.2.1 on 2020-01-31

    /// <summary>
    /// Attach the closest object to the tool. Returns the item that was attached.
    /// </summary>
    /// <returns>Attached item</returns>
    virtual Item AttachClosest()=0;

    /// <summary>
    /// Detach the closest object attached to the tool (see also setParentStatic).
    /// </summary>
    /// <returns>Detached item</returns>
    virtual Item DetachClosest(Item parent=nullptr)=0;

    /// <summary>
    /// Detach any object attached to a tool.
    /// </summary>
    virtual void DetachAll(Item parent=nullptr)=0;

    /// <summary>
    /// Returns a list of joints an MxN matrix, where M is the number of robot axes plus 4 columns. Linear moves are rounded according to the smoothing parameter set inside the program.
    /// </summary>
    /// <param name="error_msg">Returns a human readable error message (if any)</param>
    /// <param name="joint_list">Returns the list of joints as [J1, J2, ..., Jn, ERROR, MM_STEP, DEG_STEP, MOVE_ID] if a file name is not specified</param>
    /// If flags == LISTJOINTS_SPEED: [J1, J2, ..., Jn, ERROR, MM_STEP, DEG_STEP, MOVE_ID,   TIME, X_TCP, Y_TCP, Z_TCP,  Speed_J1, Speed_J2, ..., Speed_Jn]
    /// If flags == LISTJOINTS_ACCEL: [J1, J2, ..., Jn, ERROR, MM_STEP, DEG_STEP, MOVE_ID,   TIME, X_TCP, Y_TCP, Z_TCP,  Speed_J1, Speed_J2, ..., Speed_Jn,   Accel_J1, Accel_J2, ..., Accel_Jn] </param>
    /// <param name="mm_step">Maximum step in millimeters for linear movements (millimeters)</param>
    /// <param name="deg_step">Maximum step for joint movements (degrees)</param>
    /// <param name="collision_check">Check for collisions</param>
    /// <param name="result_flag">set to 1 to include the timings between movements, set to 2 to also include the joint speeds (deg/s), set to 3 to also include the accelerations, set to 4 to include all previous information and make the splitting time-based.</param>
    /// <param name="time_step_s">(optional) set the time step in seconds for time based calculation. This value is only used when the result flag is set to 4 (time based).</param>
    /// <returns>Returns 0 if success, otherwise, it will return negative values</returns>
    virtual int InstructionListJoints(QString &error_msg, tMatrix2D *matrix, double step_mm=1, double step_deg=1, int check_collisions=IRoboDK::COLLISION_OFF, int flags=0, double time_step=0.1)=0;

    /// <summary>
    /// Copy this item (similar to Ctrl+C). The user clipboard is not altered.
    /// </summary>
    virtual void Copy()=0;

    /// <summary>
    /// Paste the copied item to this item (similar to Ctrl+V). For example, you can paste to a station, or coordinate system. Paste should be used after Copy(). It returns the newly created item.
    /// </summary>
    virtual Item Paste()=0;

    // added with RoboDK 4.2.2 on 2020-02-07

    /// <summary>
    /// Set a specific parameter associated with an item (used for specific parameters, commands and internal use).
    /// </summary>
    virtual QString setParam(const QString &param, const QString &value="", QList<Item> *itemlist=nullptr, double *values=nullptr, tMatrix2D *matrix=nullptr)=0;

    /// <summary>
    /// Set a custom parameter to store data with an item. If the parameter name does not exist it will create a new parameter. This function always returns true.
    /// </summary>
    virtual bool setParam(const QString &name, const QByteArray &value)=0;

    /// <summary>
    /// Get a custom parameter associated with an item. Returns False if the parameter name does not exist.
    /// </summary>
    virtual bool getParam(const QString &name, QByteArray &value)=0;


    //-----------------------------------------------------
    // added after 2020-08-21 with version RoboDK 5.1.0

    /// <summary>
    /// Sets the accuracy of the robot active or inactive. A robot must have been calibrated to properly use this option.
    /// </summary>
    virtual void setAccuracyActive(bool accurate=true)=0;

    /// <summary>
    /// Return the current joint position of a robot (only from the simulator, never from the real robot).
    //// This should be used only when RoboDK is connected to the real robot and only the simulated robot needs to be retrieved (for example, if we want to move the robot using a spacemouse).
    /// </summary>
    /// <returns>double x n: joints matrix</returns>
    virtual tJoints SimulatorJoints()=0;

    /// <summary>
    /// Select an instruction in the program as a reference to add new instructions. New instructions will be added after the selected instruction. If no instruction ID is specified, the active instruction will be selected and returned.
    /// </summary>
    virtual int InstructionSelect(int ins_id=-1)=0;

    /// <summary>
    /// Delete an instruction of a program
    /// </summary>
    virtual int InstructionDelete(int ins_id=0)=0;

    /// <summary>
    /// Set an Analog Output (AO).
    /// </summary>
    /// <param name="io_var">analog output (string or number)</param>
    /// <param name="io_value">value (string or number)</param>
    virtual void setAO(const QString &io_var, const QString &io_value)=0;

    /// <summary>
    /// Get a Digital Input (DI). This function is only useful when connected to a real robot using the robot driver. It returns a string related to the state of the Digital Input (1=True, 0=False). This function returns an empty string if the script is not executed on the robot.
    /// </summary>
    /// <param name="io_var">Digital Input (string or number)</param>
    virtual QString getDI(const QString &io_var)=0;

    /// <summary>
    /// Returns the robot connection parameters
    /// </summary>
    /// <param name="robotIP">Robot IP</param>
    /// <param name="port">Communication port</param>
    /// <param name="remote_path">Remote path to place sent programs</param>
    /// <param name="FTP_user">FTP User</param>
    /// <param name="FTP_pass">FTP Password</param>
    virtual void ConnectionParams(QString &robotIP, int &port, QString &remote_path, QString &FTP_user, QString &FTP_pass)=0;

    /// <summary>
    /// Set the robot connection parameters
    /// </summary>
    /// <param name="robotIP">Robot IP</param>
    /// <param name="port">Communication port</param>
    /// <param name="remote_path">Remote path to place sent programs</param>
    /// <param name="FTP_user">FTP User</param>
    /// <param name="FTP_pass">FTP Password</param>
    virtual void setConnectionParams(const QString &robotIP, const int &port=2000, const QString &remote_path="/", const QString &FTP_user="", const QString &FTP_pass="")=0;

    /// <summary>
    /// Return the color of an :class:`.Item` (object, tool or robot). If the item has multiple colors it returns the first color available).
    /// </summary>
    virtual void Color(tColor &clr_out)=0;

    /// <summary>
    /// Retrieve the currently selected feature for this object.
    /// </summary>
    virtual void SelectedFeature(bool &is_selected, int feature_type, int &feature_id)=0;


    //-----------------------------------------------------
    // added after 2021-09-17 with version RoboDK 5.3.0

    /// <summary>
    /// Returns the positions of the joint links for a provided robot configuration (joints). If no joints are provided it will return the poses for the current robot position. Out 1 : 4x4 x n -> array of 4x4 homogeneous matrices. Index 0 is the base frame reference (it never moves when the joints move).
    /// </summary>
    /// <returns>List of poses</returns>
    virtual QList<Mat> JointPoses(const tJoints &jnts)=0;



};


//inline QDebug operator<<(QDebug dbg, const IItem *itm){ return dbg.noquote() << (itm == nullptr ? "Item(null)" : itm); }

// Allows us to use Item as a QVariant. Example:
// QVariant::fromValue<Item>(item)
Q_DECLARE_METATYPE (Item);

//Q_DECLARE_INTERFACE(IAppRoboDK, "RoboDK.IItem")


#endif // IITEM_H
