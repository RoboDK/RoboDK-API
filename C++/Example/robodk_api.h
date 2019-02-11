// Copyright 2015-2018 - RoboDK Inc. - https://robodk.com/
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
// http://www.apache.org/licenses/LICENSE-2.0
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
//
// --------------------------------------------
// --------------- DESCRIPTION ----------------
// This file defines the following two classes:
//     Joints : for 1D arrays representing joint values
//     Mat : for pose multiplications
//     RoboDK (Robolink()) : Main interface with RoboDK
//     Item : Represents an item in the RoboDK station
// These classes are the objects used to interact with RoboDK and create macros.
// An item is an object in the RoboDK tree (it can be either a robot, an object, a tool, a frame, a program, ...).
// Items can be retrieved from the RoboDK station using the Robolink() object (such as Robolink.Item() method)
//
// In this document: pose = transformation matrix = homogeneous matrix = 4x4 matrix
//
// More information about the RoboDK API here:
//     https://robodk.com/doc/en/RoboDK-API.html
//     https://robodk.com/doc/en/PythonAPI/index.html
//
// More information about RoboDK post processors here:
//     https://robodk.com/help#PostProcessor
//
// Visit the Matrix and Quaternions FAQ for more information about pose/homogeneous transformations
//     http://www.j3d.org/matrix_faq/matrfaq_latest.html
//
//---------------------------------------------
// TIPS:
//  1- Add #define RDK_SKIP_NAMESPACE
//     to avoid using the RoboDK_API namespace
//  2- Add #define RDK_WITH_EXPORTS  (and RDK_EXPORTS)
//     to generate/import as a DLL
//---------------------------------------------

#ifndef ROBODK_API_H
#define ROBODK_API_H



#ifdef RDK_WITH_EXPORTS
    #ifdef RDK_EXPORTS
    #define ROBODK __declspec(dllexport)
    #else
    #define ROBODK __declspec(dllimport)
    #endif
#else
    #define ROBODK
#endif


#include <QtCore/QString>
#include <QtGui/QMatrix4x4> // this should not be part of the QtGui! it is just a matrix


class QTcpSocket;


#ifndef RDK_SKIP_NAMESPACE
namespace RoboDK_API {
#endif


class Item;
class RoboDK;


/// maximum size of robot joints (maximum allowed degrees of freedom for a robot)
#define RDK_SIZE_JOINTS_MAX 12
// IMPORTANT!! Do not change this value

/// Constant defining the size of a robot configuration (at least 3 doubles are required)
#define RDK_SIZE_MAX_CONFIG 4
// IMPORTANT!! Do not change this value

/// Six doubles that represent robot joints (usually in degrees)
//typedef double tJoints[RDK_SIZE_JOINTS_MAX];


/// @brief tXYZWPR (mm, rad) holds the same information as a \ref tMatrix4x4 pose but represented as XYZ position (in mm) and WPR orientation (in rad) (XYZWPR = [X,Y,Z,W,P,R])
/// This type of variable is easier to read and it is what most robot controllers use to input a pose. However, for internal calculations it is better to use a 4x4 pose matrix as it is faster and more accurate.
/// To calculate a 4x4 matrix: pose4x4 = transl(X,Y,Z)*rotx(W)*roty(P)*rotz(R)
/// See \ref POSE_2_XYZWPR and \ref XYZWPR_2_POSE to exchange between \ref tMatrix4x4 and \ref tXYZWPR
typedef double tXYZWPR[6];

/// @brief tXYZ (mm) represents a position or a vector in mm
typedef double tXYZ[3];


/// @brief The robot configuration defines a specific state of the robot without crossing any singularities. Changing the configuration requires crossing a singularity.
/// There are 2x2x2=8 different configurations.
/// A robot configurations is also known by "Assembly mode"
/// The robot configuration is defined as an array of 3 doubles: [FACING REAR, LOWER ARM, WRIST FLIP].
/// FACING REAR=0 means FACING FRONT
/// LOWER ARM=0 means ELBOW UP
/// WRIST FLIP=0 means WRIST NON FLIP
/// the 4th value is reserved
typedef double tConfig[RDK_SIZE_MAX_CONFIG];

//////////////////////////////////////////
// Variable size 2d Matrix
struct tMatrix2D {
  double *data;
  int *size;
  int allocatedSize;
  int numDimensions;
  bool canFreeData;
};

struct Color{
    float r;
    float g;
    float b;
    float a;
};







//--------------------- Joints class -----------------------
class ROBODK tJoints {
public:
    tJoints(int ndofs = 0);
    tJoints(const tJoints &jnts);
    tJoints(const tMatrix2D *mat2d, int column=0, int ndofs=-1);
    tJoints(const QString &str);

    double *Data();
    int Length();

    int GetValues(double *joints);
    void SetValues(const double *joints, int ndofs = -1);
    QString ToString(const QString &separator=" , ", int precision = 3);
    bool FromString(const QString &str);


public:
    int nDOFs;
    double Values[RDK_SIZE_JOINTS_MAX];
};


//---------------------------------------------------------
class ROBODK Mat : public QMatrix4x4 {
public:
    Mat();
    Mat(const QMatrix4x4 &matrix);
    Mat(double nx, double ox, double ax, double tx, double ny, double oy, double ay, double ty, double nz, double oz, double az, double tz);
    ~Mat();

    void setVX(double x, double y, double z);
    void VX(tXYZ xyz);
    void setVY(double x, double y, double z);
    void VY(tXYZ xyz);
    void setVZ(double x, double y, double z);
    void VZ(tXYZ xyz);
    void setPos(double x, double y, double z);
    void Pos(tXYZ xyz);

    /// Invert the pose (homogeneous matrix assumed)
    Mat inv() const;

    void Set(int i, int j, double value);
    double Get(int i, int j) const;

    void ToXYZRPW(tXYZWPR xyzwpr);
    QString ToString(const QString &separator, int precision = 3, bool in_xyzwpr = true);
    bool FromString(const QString &str);


    void FromXYZRPW(tXYZWPR xyzwpr);

    static Mat XYZRPW_2_Mat(double x, double y, double z, double r, double p, double w);
    static Mat XYZRPW_2_Mat(tXYZWPR xyzwpr);

};



class ROBODK RoboDK {
    friend class RoboDK_API::Item;


public:
    RoboDK(const QString &robodk_ip="", int com_port=-1, const QString &args="", const QString &path="");
    ~RoboDK();

    quint64 ProcessID();
    quint64 WindowID();

    bool Connected();
    bool Connect();

    void Disconnect();
    void Finish();

    Item getItem(QString name, int itemtype = -1);
    QStringList getItemListNames(int filter = -1);
    QList<Item> getItemList(int filter = -1);
    Item ItemUserPick(const QString &message = "Pick one item", int itemtype = -1);

    void ShowRoboDK();
    void HideRoboDK();
    void CloseRoboDK();
    QString Version();
    void setWindowState(int windowstate = WINDOWSTATE_NORMAL);
    void setFlagsRoboDK(int flags = FLAG_ROBODK_ALL);
    void setFlagsItem(Item item, int flags = FLAG_ITEM_ALL);
    int getFlagsItem(Item item);
    void ShowMessage(const QString &message, bool popup = true);
    Item AddFile(const QString &filename, const Item *parent=NULL);
    void Save(const QString &filename, const Item *itemsave=NULL);
    Item AddShape(Mat *trianglePoints,Item *addTo = NULL, bool shapeOverride = false, Color *color = NULL);
    Item AddCurve(Mat *curvePoints,Item *referenceObject = NULL,bool addToRef = false,int ProjectionType = PROJECTION_ALONG_NORMAL_RECALC);
    Item AddPoints(Mat *points, Item *referenceObject = NULL, bool addToRef = false, int ProjectionType =  PROJECTION_ALONG_NORMAL_RECALC);
    Mat ProjectPoints(Mat *points, Item objectProject, int ProjectionType = PROJECTION_ALONG_NORMAL_RECALC);


    void CloseStation();
    Item AddTarget(const QString &name, Item *itemparent = NULL, Item *itemrobot = NULL);

    Item AddFrame(const QString &name, Item *itemparent = NULL);

    Item AddProgram(const QString &name, Item *itemrobot = NULL);
    Item AddStation(QString name);
    Item AddMachiningProject(QString name = "Curve follow settings",Item *itemrobot = NULL);
    QList<Item> getOpenStation();
    void setActiveStation(Item stn);
    Item getActiveStation();
    int RunProgram(const QString &function_w_params);
    int RunCode(const QString &code, bool code_is_fcn_call = false);
    void RunMessage(const QString &message, bool message_is_comment = false);
    void Render(bool always_render = false);
    void Update();
    bool IsInside(Item object_inside, Item object_parent);
    int setCollisionActive(int check_state = COLLISION_ON);
    bool setCollisionActivePair(int check_state, Item item1, Item item2, int id1 = 0, int id2 = 0);
    int Collisions();
    int Collision(Item item1, Item item2);
    QList<Item> getCollisionItems(QList<int> link_id_list);
    void setSimulationSpeed(double speed);
    double SimulationSpeed();
    void setRunMode(int run_mode = 1);
    int RunMode();

    QList<QPair<QString, QString> > getParams();
    QString getParam(const QString &param);
    void setParam(const QString &param, const QString &value);
    QString Command(const QString &cmd, const QString &value="");

    // --- add calibrate reference, calibrate tool, measure tracker, etc...
    bool LaserTrackerMeasure(tXYZ xyz, tXYZ estimate, bool search = false);
    bool CollisionLine(tXYZ p1, tXYZ p2);
    void setVisible(QList<Item> itemList, QList<bool> visibleList, QList<int> visibleFrames);
    void ShowAsCollided(QList<Item> itemList, QList<bool> collidedList, QList<int> *robot_link_id = NULL);
    void CalibrateTool(tMatrix2D *poses_joints, tXYZ tcp_xyz, int format=EULER_RX_RY_RZ, int algorithm=CALIBRATE_TCP_BY_POINT, Item *robot=NULL, double *error_stats=NULL);
    Mat CalibrateReference(tMatrix2D *poses_joints, int method = CALIBRATE_FRAME_3P_P1_ON_X, bool use_joints = false, Item *robot = NULL);


    int ProgramStart(const QString &progname, const QString &defaultfolder = "", const QString &postprocessor = "", Item *robot = NULL);
    void setViewPose(const Mat &pose);
    Mat ViewPose();
    bool SetRobotParams(Item *robot,tMatrix2D dhm, Mat poseBase, Mat poseTool);
    Item getCursorXYZ(int x = -1, int y = -1, tXYZ xyzStation = NULL);
    QString License();
    QList<Item> Selection();
    Item Popup_ISO9283_CubeProgram(Item *robot=NULL, tXYZ center=NULL, double side=-1, bool blocking=true);



public:

    // Tree item types
    enum {
        ITEM_TYPE_ANY = -1,
        ITEM_TYPE_STATION = 1,
        ITEM_TYPE_ROBOT = 2,
        ITEM_TYPE_FRAME = 3,
        ITEM_TYPE_TOOL = 4,
        ITEM_TYPE_OBJECT = 5,
        ITEM_TYPE_TARGET = 6,
        ITEM_TYPE_PROGRAM = 8,
        ITEM_TYPE_INSTRUCTION = 9,
        ITEM_TYPE_PROGRAM_PYTHON = 10,
        ITEM_TYPE_MACHINING = 11,
        ITEM_TYPE_BALLBARVALIDATION = 12,
        ITEM_TYPE_CALIBPROJECT = 13,
        ITEM_TYPE_VALID_ISO9283 = 14
    };

    // Instruction types
    enum {
        INS_TYPE_INVALID = -1,
        INS_TYPE_MOVE = 0,
        INS_TYPE_MOVEC = 1,
        INS_TYPE_CHANGESPEED = 2,
        INS_TYPE_CHANGEFRAME = 3,
        INS_TYPE_CHANGETOOL = 4,
        INS_TYPE_CHANGEROBOT = 5,
        INS_TYPE_PAUSE = 6,
        INS_TYPE_EVENT = 7,
        INS_TYPE_CODE = 8,
        INS_TYPE_PRINT = 9
    };

    // Move types
    enum {
        MOVE_TYPE_INVALID = -1,
        MOVE_TYPE_JOINT = 1,
        MOVE_TYPE_LINEAR = 2,
        MOVE_TYPE_CIRCULAR = 3
    };

    // Script execution types
    enum {
        RUNMODE_SIMULATE = 1,                      // performs the simulation moving the robot (default)
        RUNMODE_QUICKVALIDATE = 2,                 // performs a quick check to validate the robot movements
        RUNMODE_MAKE_ROBOTPROG = 3,                // makes the robot program
        RUNMODE_MAKE_ROBOTPROG_AND_UPLOAD = 4,     // makes the robot program and updates it to the robot
        RUNMODE_MAKE_ROBOTPROG_AND_START = 5,      // makes the robot program and starts it on the robot (independently from the PC)
        RUNMODE_RUN_ROBOT = 6                     // moves the real robot from the PC (PC is the client, the robot behaves like a server)
    };

    // Program execution type
    enum {
        PROGRAM_RUN_ON_SIMULATOR = 1,        // Set the program to run on the simulator
        PROGRAM_RUN_ON_ROBOT = 2            // Set the program to run on the robot
    };

    // TCP calibration types
    enum {
        CALIBRATE_TCP_BY_POINT = 0,
        CALIBRATE_TCP_BY_PLANE = 1
    };

    // Reference frame calibration types
    enum {
        CALIBRATE_FRAME_3P_P1_ON_X = 0,    //Calibrate by 3 points: [X, X+, Y+] (p1 on X axis)
        CALIBRATE_FRAME_3P_P1_ORIGIN = 1,  //Calibrate by 3 points: [Origin, X+, XY+] (p1 is origin)
        CALIBRATE_FRAME_6P = 2,            //Calibrate by 6 points
        CALIBRATE_TURNTABLE = 3           //Calibrate turntable
    };

    // projection types (for AddCurve)
    enum {
        PROJECTION_NONE                = 0, // No curve projection
        PROJECTION_CLOSEST             = 1, // The projection will the closest point on the surface
        PROJECTION_ALONG_NORMAL        = 2, // The projection will be done along the normal.
        PROJECTION_ALONG_NORMAL_RECALC = 3, // The projection will be done along the normal. Furthermore, the normal will be recalculated according to the surface normal.
        PROJECTION_CLOSEST_RECALC      = 4, // The projection will be the closest point on the surface and the normals will be recalculated
        PROJECTION_RECALC              = 5  // The normals are recalculated according to the surface normal of the closest projection. The points are not changed.
    };

    // Euler type
    enum {
        JOINT_FORMAT      = -1, // joints
        EULER_RX_RYp_RZpp = 0, // generic
        EULER_RZ_RYp_RXpp = 1, // ABB RobotStudio
        EULER_RZ_RYp_RZpp = 2, // Kawasaki, Adept, Staubli
        EULER_RZ_RXp_RZpp = 3, // CATIA, SolidWorks
        EULER_RX_RY_RZ    = 4, // Fanuc, Kuka, Motoman, Nachi
        EULER_RZ_RY_RX    = 5, // CRS
        EULER_QUEATERNION = 6 // ABB Rapid
    };

    // State of the RoboDK window
    enum {
        WINDOWSTATE_HIDDEN = -1,
        WINDOWSTATE_SHOW = 0,
        WINDOWSTATE_MINIMIZED = 1,
        WINDOWSTATE_NORMAL = 2,
        WINDOWSTATE_MAXIMIZED = 3,
        WINDOWSTATE_FULLSCREEN = 4,
        WINDOWSTATE_CINEMA = 5,
        WINDOWSTATE_FULLSCREEN_CINEMA = 6
    };

    // Instruction program call type:
    enum {
        INSTRUCTION_CALL_PROGRAM = 0,
        INSTRUCTION_INSERT_CODE = 1,
        INSTRUCTION_START_THREAD = 2,
        INSTRUCTION_COMMENT = 3,
        INSTRUCTION_SHOW_MESSAGE = 4
    };

    // Object selection features:
    enum {
        FEATURE_NONE = 0,
        FEATURE_SURFACE = 1,
        FEATURE_CURVE = 2,
        FEATURE_POINT = 3
    };

    // Spray gun simulation:
    enum {
        SPRAY_OFF = 0,
        SPRAY_ON = 1
    };

    // Collision checking state
    enum {
        COLLISION_OFF = 0,
        COLLISION_ON = 1
    };

    // RoboDK Window Flags
    enum {
        FLAG_ROBODK_TREE_ACTIVE = 1,
        FLAG_ROBODK_3DVIEW_ACTIVE = 2,
        FLAG_ROBODK_LEFT_CLICK = 4,
        FLAG_ROBODK_RIGHT_CLICK = 8,
        FLAG_ROBODK_DOUBLE_CLICK = 16,
        FLAG_ROBODK_MENU_ACTIVE = 32,
        FLAG_ROBODK_MENUFILE_ACTIVE = 64,
        FLAG_ROBODK_MENUEDIT_ACTIVE = 128,
        FLAG_ROBODK_MENUPROGRAM_ACTIVE = 256,
        FLAG_ROBODK_MENUTOOLS_ACTIVE = 512,
        FLAG_ROBODK_MENUUTILITIES_ACTIVE = 1024,
        FLAG_ROBODK_MENUCONNECT_ACTIVE = 2048,
        FLAG_ROBODK_WINDOWKEYS_ACTIVE = 4096,
        FLAG_ROBODK_NONE = 0,
        FLAG_ROBODK_ALL = 0xFFFF,
        FLAG_ROBODK_MENU_ACTIVE_ALL = FLAG_ROBODK_MENU_ACTIVE | FLAG_ROBODK_MENUFILE_ACTIVE | FLAG_ROBODK_MENUEDIT_ACTIVE | FLAG_ROBODK_MENUPROGRAM_ACTIVE | FLAG_ROBODK_MENUTOOLS_ACTIVE | FLAG_ROBODK_MENUUTILITIES_ACTIVE | FLAG_ROBODK_MENUCONNECT_ACTIVE
    };

    // RoboDK Item Flags
    enum {
        FLAG_ITEM_SELECTABLE = 1,
        FLAG_ITEM_EDITABLE = 2,
        FLAG_ITEM_DRAGALLOWED = 4,
        FLAG_ITEM_DROPALLOWED = 8,
        FLAG_ITEM_ENABLED = 32,
        FLAG_ITEM_AUTOTRISTATE = 64,
        FLAG_ITEM_NOCHILDREN = 128,
        FLAG_ITEM_USERTRISTATE = 256,
        FLAG_ITEM_NONE = 0,
        FLAG_ITEM_ALL = 64 + 32 + 8 + 4 + 2 + 1
    };




private:
    QTcpSocket *_COM;
    QString _IP;
    int _PORT;
    int _TIMEOUT;
    qint64 _PROCESS;

    QString _ROBODK_BIN; // file path to the robodk program (executable), typically C:/RoboDK/bin/RoboDK.exe. Leave empty to use the registry key: HKEY_LOCAL_MACHINE\SOFTWARE\RoboDK
    QString _ARGUMENTS;       // arguments to provide to RoboDK on startup

    bool _connected();
    bool _connect();
    bool _connect_smart(); // will attempt to start RoboDK
    void _disconnect();

    bool _check_connection();
    bool _check_status();

    bool _waitline();
    QString _recv_Line();//QString &string);
    bool _send_Line(const QString &string);
    int _recv_Int();//qint32 &value);
    bool _send_Int(const qint32 value);
    Item _recv_Item();//Item *item);
    bool _send_Item(const Item *item);
    bool _send_Item(const Item &item);
    Mat _recv_Pose();//Mat &pose);
    bool _send_Pose(const Mat &pose);
    bool _recv_XYZ(tXYZ pos);
    bool _send_XYZ(const tXYZ pos);
    bool _recv_Array(double *values, int *psize=NULL);
    bool _send_Array(const double *values, int nvalues);
    bool _recv_Array(tJoints *jnts);
    bool _send_Array(const tJoints *jnts);
    bool _send_Array(const Mat *mat);
    bool _recv_Matrix2D(tMatrix2D **mat);
    bool _send_Matrix2D(tMatrix2D *mat);


    void _moveX(const Item *target, const tJoints *joints, const Mat *mat_target, const Item *itemrobot, int movetype, bool blocking);
    void _moveC(const Item *target1, const tJoints *joints1, const Mat *mat_target1, const Item *target2, const tJoints *joints2, const Mat *mat_target2, const Item *itemrobot, bool blocking);
};


class ROBODK Item {
    friend class RoboDK_API::RoboDK;
    
public:
    Item(RoboDK *rdk=nullptr, quint64 ptr=0, qint32 type=-1);
    Item(const Item &other);

    ~Item();

    RoboDK* RDK();

    void NewLink();
    int Type();
    void Save(const QString &filename);
    void Delete();
    bool Valid();
    void setParent(Item parent);
    void setParentStatic(Item parent);

    QList<Item> Childs();
    bool Visible();
    void setVisible(bool visible, int visible_frame = -1);
    QString Name();
    void setName(const QString &name);
    void setPose(Mat pose);
    Mat Pose();
    void setGeometryPose(Mat pose);
    Mat GeometryPose();
    void setHtool(Mat pose);
    Mat Htool();
    Mat PoseTool();
    Mat PoseFrame();
    void setPoseFrame(Mat frame_pose);
    void setPoseFrame(Item frame_item);
    void setPoseTool(Mat tool_pose);
    void setPoseTool(Item tool_item);
    void setPoseAbs(Mat pose);
    Mat PoseAbs();

    void setColor(double colorRGBA[4]);

//---------- add more

    void Scale(double scale);
    void Scale(double scale_xyz[3]);
    Item setMachiningParameters(QString ncfile = "", Item part_obj = nullptr, QString options = "");

    void setAsCartesianTarget();
    void setAsJointTarget();
    bool isJointTarget();
    tJoints Joints();
    tJoints JointsHome();
    void setJointsHome(const tJoints &jnts);
    Item ObjectLink(int link_id = 0);
    Item getLink(int type_linked = RoboDK::ITEM_TYPE_ROBOT);

    void setJoints(const tJoints &jnts);
    void JointLimits(tJoints *lower_limits, tJoints *upper_limits);
    void setRobot(const Item &robot);

    Item AddTool(const Mat &tool_pose, const QString &tool_name = "New TCP");
    Mat SolveFK(const tJoints &joints);
    void JointsConfig(const tJoints &joints, tConfig config);
    tJoints SolveIK(const Mat &pose, const Mat *tool=nullptr, const Mat *ref=nullptr);
    tMatrix2D *SolveIK_All_Mat2D(const Mat &pose, const Mat *tool=nullptr, const Mat *ref=nullptr);
    QList<tJoints> SolveIK_All(const Mat &pose, const Mat *tool=nullptr, const Mat *ref=nullptr);
    bool Connect(const QString &robot_ip = "");
    bool Disconnect();
    void MoveJ(const Item &itemtarget, bool blocking = true);
    void MoveJ(const tJoints &joints, bool blocking = true);
    void MoveJ(const Mat &target, bool blocking = true);
    void MoveL(const Item &itemtarget, bool blocking = true);
    void MoveL(const tJoints &joints, bool blocking = true);
    void MoveL(const Mat &target, bool blocking = true);
    void MoveC(const Item &itemtarget1, const Item &itemtarget2, bool blocking = true);
    void MoveC(const tJoints &joints1, const tJoints &joints2, bool blocking = true);
    void MoveC(const Mat &target1, const Mat &target2, bool blocking = true);
    int MoveJ_Test(const tJoints &j1, const tJoints &j2, double minstep_deg = -1);
    int MoveL_Test(const tJoints &joints1, const Mat &pose2, double minstep_mm = -1);
    void setSpeed(double speed_linear, double accel_linear = -1, double speed_joints = -1, double accel_joints = -1);
    void setRounding(double zonedata);
    void ShowSequence(tMatrix2D *sequence);
    bool Busy();
    void Stop();
    void WaitMove(double timeout_sec = 300) const;
    void setAccuracyActive(int accurate = 1);
    bool MakeProgram(const QString &filename);
    void setRunType(int program_run_type);
    int RunProgram();
    int RunCode(const QString &parameters);
    int RunInstruction(const QString &code, int run_type = RoboDK::INSTRUCTION_CALL_PROGRAM);
    void Pause(double time_ms = -1);
    void setDO(const QString &io_var, const QString &io_value);
    void waitDI(const QString &io_var, const QString &io_value, double timeout_ms = -1);
    void customInstruction(const QString &name, const QString &path_run, const QString &path_icon = "", bool blocking = true, const QString &cmd_run_on_robot = "");
    //void addMoveJ(const Item &itemtarget);
    //void addMoveL(const Item &itemtarget);
    void ShowInstructions(bool visible=true);
    void ShowTargets(bool visible=true);
    int InstructionCount();
    void Instruction(int ins_id, QString &name, int &instype, int &movetype, bool &isjointtarget, Mat &target, tJoints &joints);
    void setInstruction(int ins_id, const QString &name, int instype, int movetype, bool isjointtarget, const Mat &target, const tJoints &joints);
    int InstructionList(tMatrix2D *instructions);
    double Update(int collision_check = RoboDK::COLLISION_OFF, int timeout_sec = 3600, double *out_nins_time_dist = nullptr, double mm_step = -1, double deg_step = -1);
    int InstructionListJoints(QString &error_msg, tMatrix2D **joint_list, double mm_step = 10.0, double deg_step = 5.0, const QString &save_to_file = "");
    bool Finish();

    quint64 GetID();


private:
    RoboDK *_RDK;
    quint64 _PTR;
    qint32 _TYPE;
};


Mat transl(double x, double y, double z);
Mat rotx(double rx);
Mat roty(double ry);
Mat rotz(double rz);




/////////////////////////////////////////////////////////////////
/// @brief Creates a new 2D matrix \ref Matrix2D.. Use \ref Matrix2D_Delete to delete the matrix (to free the memory).
/// The Procedure @ref Debug_Matrix2D shows an example to read data from a tMatrix2D
ROBODK tMatrix2D* Matrix2D_Create();

/// @brief Deletes a \ref tMatrix2D.
/// @param[in] mat: Pointer of the pointer to the matrix
ROBODK void Matrix2D_Delete(tMatrix2D **mat);

/// @brief Sets the size of a \ref tMatrix2D.
/// @param[in/out] mat: Pointer to the matrix
/// @param[in] rows: The number of rows.
/// @param[in] cols: The number of columns.
ROBODK void Matrix2D_Set_Size(tMatrix2D *mat, int rows, int cols);

/// @brief Sets the size of a \ref tMatrix2D.
/// @param[in/out] mat: Pointer to the matrix
/// @param[in] dim: Dimension (1 or 2)
ROBODK int Matrix2D_Size(const tMatrix2D *mat, int dim);

/// @brief Returns the number of columns of a \ref tMatrix2D.
/// @param[in] mat: Pointer to the matrix
/// Returns the number of columns (Second dimension)
ROBODK int Matrix2D_Get_ncols(const tMatrix2D *var);

/// @brief Returns the number of rows of a \ref tMatrix2D.
/// @param[in] mat: Pointer to the matrix
/// Returns the number of rows (First dimension)
ROBODK int Matrix2D_Get_nrows(const tMatrix2D *var);

/// @brief Returns the value at location [i,j] of a \ref tMatrix2D.
/// @param[in] mat: Pointer to the matrix
/// Returns the value of the cell
ROBODK double Matrix2D_Get_ij(const tMatrix2D *var, int i, int j);

/// @brief Returns the pointer of a column of a \ref tMatrix2D.
/// A column has \ref Matrix2D_Get_nrows(mat) values that can be accessed/modified from the returned pointer continuously.
/// @param[in] mat: Pointer to the matrix
/// @param[in] col: Column to retreive.
/// /return double array (internal pointer) to the column
ROBODK double* Matrix2D_Get_col(const tMatrix2D *var, int col);

/// @brief Show an array through STDOUT
/// Given an array of doubles, it generates a string
ROBODK void Debug_Array(const double *array, int arraysize);

/// @brief Display the content of a \ref tMatrix2D through STDOUT. This is only intended for debug purposes.
/// @param[in] mat: Pointer to the matrix
ROBODK void Debug_Matrix2D(const tMatrix2D *mat);


/// @brief Displays the content of a \ref tMatrix4x4 through STDOUT. This is only intended for debug purposes.
/// @param[in] mat: pose matrix
/// @param[in] show_full_pose: set to false to display the 6 values of the pose as XYZWPR instead of the 4x4 matrix
//ROBODK void Debug_Mat(Mat pose, char show_full_pose);



#ifndef RDK_SKIP_NAMESPACE
}
#endif




#endif // ROBODK_API
