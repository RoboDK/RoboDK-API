#pragma once
//Standard libraries used by the robodk api
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
//Networking includes
#ifdef _WIN32
#include <Ws2tcpip.h>
#pragma comment(lib, "ws2_32.lib")
#include <winsock2.h>
#endif // _WIN32

//Robodk defines from c++
#ifdef _WIN32
// Default path on Windows:
#define ROBODK_DEFAULT_PATH_BIN "C:/RoboDK/bin/RoboDK.exe"
#elif __APPLE__
// Default Install Path on Mac
#define ROBODK_DEFAULT_PATH_BIN "~/RoboDK/Applications/RoboDK.app/Contents/MacOS/RoboDK"

#else

// Default Install Path on Linux:
#define ROBODK_DEFAULT_PATH_BIN "~/RoboDK/bin/RoboDK"

#endif

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

#define ROBODK_DEFAULT_PORT 20500

#define ROBODK_API_TIMEOUT 1000 // communication timeout. Raise this value for slow computers
#define ROBODK_API_START_STRING "CMD_START"
#define ROBODK_API_READY_STRING "READY"
#define ROBODK_API_LF "\n"

/// maximum size of robot joints (maximum allowed degrees of freedom for a robot)
#define RDK_SIZE_JOINTS_MAX 12
// IMPORTANT!! Do not change this value

/// Constant defining the size of a robot configuration (at least 3 doubles are required)
#define RDK_SIZE_MAX_CONFIG 4
// IMPORTANT!! Do not change this value

//Maximum string lenth for string based parameters like IP and names
static const int MAX_STR_LENGTH = 1024;

//Enums
/// Tree item types
enum eITEM_TYPE {
	/// Any item type.
	ITEM_TYPE_ANY = -1,

	/// Item of type station (RDK file).
	ITEM_TYPE_STATION = 1,

	/// Item of type robot (.robot file).
	ITEM_TYPE_ROBOT = 2,

	/// Item of type reference frame.
	ITEM_TYPE_FRAME = 3,

	/// Item of type tool (.tool).
	ITEM_TYPE_TOOL = 4,

	/// Item of type object (.stl, .step or .iges for example).
	ITEM_TYPE_OBJECT = 5,

	/// Target item.
	ITEM_TYPE_TARGET = 6,

	/// Program item.
	ITEM_TYPE_PROGRAM = 8,

	/// Instruction.
	ITEM_TYPE_INSTRUCTION = 9,

	/// Python macro.
	ITEM_TYPE_PROGRAM_PYTHON = 10,

	/// Robot machining project, curve follow, point follow or 3D printing project.
	ITEM_TYPE_MACHINING = 11,

	/// Ballbar validation project.
	ITEM_TYPE_BALLBARVALIDATION = 12,

	/// Robot calibration project.
	ITEM_TYPE_CALIBPROJECT = 13,

	/// Robot path accuracy validation project.
	ITEM_TYPE_VALID_ISO9283 = 14
};

enum {
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



/// Script execution types used by IRoboDK.setRunMode and IRoboDK.RunMode
enum eRobotRunMode{
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

//Structures
//Represents an instance of the RoboDK communication class
struct RoboDK_t {
	SOCKET _COM;
	bool _isConnected;
	char _IP[MAX_STR_LENGTH];
	int _PORT;
	int _TIMEOUT;
	int64_t _PROCESS;

	char _ROBODK_BIN[MAX_STR_LENGTH]; // file path to the robodk program (executable), typically C:/RoboDK/bin/RoboDK.exe. Leave empty to use the registry key: HKEY_LOCAL_MACHINE\SOFTWARE\RoboDK
	char _ARGUMENTS[MAX_STR_LENGTH];  // arguments to provide to RoboDK on startup
};

//Represents an instance of a RoboDK Item class
struct Item_t {
	struct RoboDK_t *_RDK;

	/// Pointer to the item inside RoboDK
	uint64_t _PTR;

	/// Item type
	int32_t _TYPE;
};

//Represents a 4x4 matrix from robodk, represented as an array of 16 doubles
//Units are in mm/radians
struct Mat_t {
	double arr16[16];
};


struct Joints_t {
	/// number of degrees of freedom
	int _nDOFs;

	/// joint values (doubles, used to store the joint values)
	double _Values[RDK_SIZE_JOINTS_MAX];
};

/// \brief The Matrix2D_t struct represents a variable size 2d Matrix. Use the Matrix2D_... functions to operate on this variable sized matrix.
/// This type of data can be used to get/set a program as a list. This is also useful for backwards compatibility functions related to RoKiSim.
struct Matrix2D_t {
	/// Pointer to the data
	double *data;

	/// Pointer to the size array.
	int *size;

	/// Allocated size.
	int allocatedSize;


	/// Number of dimensions (usually 2)
	int numDimensions;

	bool canFreeData;
};

//Wraps a xyz array in a struct so that functions can return it by value
struct XYZ_t {
	double arr3[3];
};

struct  XYZWPR_t {
	double arr6[6];
};


//Platform indepedent IO operations
void ThreadSleep(unsigned long nMilliseconds);
void StartProcess(const char* applicationPath, const char* arguments, int64_t* processID);
int  SocketWrite(SOCKET, void *buffer, int bufferSize);

//RoboDK class Functions
void RoboDK_Connect_default(struct RoboDK_t *inst); //Complete
void RoboDK_Connect(struct RoboDK_t *inst, const char* robodk_ip, int com_port, const char *args, const char *path); //Complete
void RoboDK_ShowMessage(struct RoboDK_t *inst, const char *message, bool isPopup); //Complete
struct Item_t RoboDK_getItem(struct RoboDK_t *inst, const char *name, enum eITEM_TYPE itemtype); //Complete
void RoboDK_setRunMode(struct RoboDK_t *inst, int run_mode); //Complete
void RoboDK_setParam(struct RoboDK_t* inst, const char* param, const char* value);
void RoboDK_getParam(struct RoboDK_t* inst, const char* param, char* value);
void RoboDK_License(struct RoboDK_t* inst, char* license);
void RoboDK_setViewPose(struct RoboDK_t* inst, struct Mat_t* pose);
void RoboDK_ShowRoboDK(struct RoboDK_t* inst);
void RoboDK_HideRoboDK(struct RoboDK_t* inst);
void RoboDK_CloseRoboDK(struct RoboDK_t* inst);
void RoboDK_setWindowState(struct RoboDK_t* inst, int windowstate);
void RoboDK_setFlagsRoboDK(struct RoboDK_t* inst, int flags);
void RoboDK_setFlagsItem(struct RoboDK_t* inst1, struct Item_t* inst2, int flags);

//RoboDK item class functions
bool Item_Valid(const struct Item_t *item); //Done
void Item_Name(const struct Item_t *inst, char *nameOut); //Complete
struct Mat_t Item_Pose(const struct Item_t *inst); //Complete

//Robot specific item commands
struct Joints_t Item_Joints(const struct Item_t *inst); //Complete
void Item_WaitMove(const struct Item_t *inst, double timeout_sec); //
bool Item_Connect(const struct Item_t *inst, const char *robot_ip); //Complete

// Pose Functions
void Item_setAccuracyActive(const struct Item_t* inst, const int accurate);
void Item_setPose(const struct Item_t* inst, const struct Mat_t pose); //done 
void Item_setPoseTool(const struct Item_t *inst, const struct Mat_t pose);
void Item_setPoseFrame(const struct Item_t *inst,const struct Mat_t pose);

//Move Functions
void Item_MoveJ_joints(struct Item_t* inst, struct Joints_t* joints, bool isBlocking); //Complete
void Item_MoveJ_mat(struct Item_t* inst, struct Mat_t* joints, bool isBlocking); //Complete
void Item_MoveJ(struct Item_t* inst, struct Item_t* inst2, bool isBlocking); //Done 
void Item_MoveL(struct Item_t* inst, struct Item_t* inst2, bool isBlocking); //Done
void Item_MoveL_joints(struct Item_t* inst, struct Joints_t* joints, bool isBlocking);
void Item_MoveL_mat(struct Item_t* inst, struct Mat_t* targetPose, bool isBlocking);
void Item_MoveC_joints(struct Item_t* inst, struct Joints_t* joints1, struct Joints_t* joints2, bool isBlocking);
void Item_MoveC(struct Item_t* inst, struct Item_t* inst2, struct Item_t* inst3, bool isBlocking);
void Item_MoveC_mat(struct Item_t* inst, struct Mat_t* targetPose1, struct Mat_t* targetPose2, bool isBlocking);
void Item_customInstruction(const struct Item_t* inst, const char* name, const char* path_run, const char* path_icon, bool blocking, const char* cmd_run_on_robot);
///
void Item_setName(const struct Item_t* inst, const char* name); //progress
struct Item_t Item_AddFrame(const char* framename, const struct Item_t* inst );// 
void Item_setRounding(const struct Item_t* inst, double zonedata);// Done 
void Item_ShowSequence(const struct Item_t* inst, struct Matrix2D_t* sequence);
bool Item_MakeProgram(const struct Item_t* inst, const char* filename);
void Item_setRunType(const struct Item_t* inst, int program_run_type);
int Item_RunProgram(const struct Item_t* inst);
int Item_RunCode(const struct Item_t* inst, char* parameters);
int Item_RunInstruction(const struct Item_t* inst, const char* code, int run_type);
void Item_Pause(const struct Item_t* inst, double time_ms);
void Item_setSimulationSpeed(const struct Item_t* inst, double speed);//Done  
double Item_SimulationSpeed(const struct Item_t* inst);//In Progress   
void Item_ShowInstructions(const struct Item_t* inst, bool visible); //Done 
int Item_InstructionCount(const struct Item_t* inst);//Done 
void Item_ShowTargets(const struct Item_t* inst, bool visible);//In Progress //pass program  item 
void Item_setSpeed(const struct Item_t* inst, double speed_linear, double accel_linear, double speed_joints , double accel_joints);//Done 
bool Item_Busy(const struct Item_t* inst);//Done
void Item_Stop(const struct Item_t* inst);//Done
bool Item_Disconnect(const struct Item_t* inst); //Done
int Item_Type(const struct Item_t* inst);
void Item_Save(const struct Item_t* inst, char* filename);
void Item_Delete(struct Item_t* inst);
void Item_setParent(const struct Item_t* inst1, const struct Item_t* inst2);
void Item_setParentStatic(const struct Item_t* inst1, const struct Item_t* inst2);
struct Item_t Item_AttachClosest(const struct Item_t* inst);
struct Item_t Item_DetachClosest(const struct Item_t* inst1, const struct Item_t* inst2);
void Item_DetachAll(const struct Item_t* inst);
bool Item_Visible(const struct Item_t* inst);
void Item_setVisible(const struct Item_t* inst, bool visible, int visible_frame);
void Item_Scale(const struct Item_t* inst, double scale_xyz[3]);
void Item_JointLimits(const struct Item_t* inst, struct Joints_t* lower_limits, struct Joints_t* upper_limits); //done
void Item_setJointLimits(const struct Item_t* inst, struct Joints_t* lower_limits, struct Joints_t* upper_limits);
void Item_setRobot(const struct Item_t* inst, const struct Item_t* robot);
struct Item_t Item_AddTool(const struct Item_t* inst, const Mat_t* tool_pose, const char* tool_name);
struct Item_t Item_setMachiningParameters(const struct Item_t* inst, char ncfile, const struct Item_t* part_obj, char *options);
void Item_setAsCartesianTarget(const struct Item_t* inst);
void Item_setAsJointTarget(const struct Item_t* inst);
bool Item_isJointTarget(const struct Item_t* inst);
struct Joints_t Item_JointsHome(const struct Item_t* inst);
void Item_setJointsHome(const struct Item_t* inst, struct Joints_t jnts);
struct Item_t Item_ObjectLink(const struct Item_t* inst, int link_id);
struct Item_t Item_getLink(const struct Item_t* inst, int link_id);
void Item_setJoints(const struct Item_t* inst, struct Joints_t jnts);
void Item_setPoseAbs(const struct Item_t* inst, const struct Mat_t pose); //Done
struct Mat_t Item_PoseAbs(const struct Item_t* inst);//Done
struct Mat_t Item_PoseTool(const struct Item_t* inst); //Done Returns the pose (Mat) of the robot tool (TCP) with respect to the robot flange
struct Mat_t Item_PoseFrame(const struct Item_t* inst); //Done Returns the pose (Mat) of the Active reference frame with respect to the robot base 
void Item_setGeometryPose(const struct Item_t* inst, const struct Mat_t pose); //done
struct Mat_t Item_GeometryPose(const struct Item_t* inst); //done
void Item_setColor(const struct Item_t* inst,double R, double G, double B, double A); //Done
struct Item_t Item_Parent(const struct Item_t* inst); //Done
struct Joints_t Item_SolveIK(const struct Item_t* inst, const struct Mat_t* pose, const struct Mat_t* tool, const struct Mat_t *ref);
struct Mat_t Item_solveFK(const struct Item_t *inst, const struct Joints_t *joints, const struct Mat_t *tool_pose, const struct Mat_t *reference_pose);
void Item_JointsConfig(const struct Item_t* inst, const struct Joints_t *joints, double config);
void Item_FilterTarget(const struct Item_t *inst, const struct Mat_t *pose, const struct Joints_t *joints_approx,struct Mat_t *out_poseFiltered,struct Joints_t *joints_filtered);

//DI and DO
char Item_getDI(const struct Item_t* inst, char* io_var);
char Item_getAI(const struct Item_t* inst, char* io_var);
void Item_setDO(const struct Item_t* inst, const char* io_var, const char* io_value);
void Item_setAO(const struct Item_t* inst, const char* io_var, const char* io_value);
void Item_waitDI(const struct Item_t* inst, const char* io_var, const char* io_value, double timeout_ms);

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

//Matrix functions, not directly related to robodk's api but needed to manipulate matrices as double[16] arrays.
//Uppercase first letter after _ means it operates on an instance of the struct while lowercase creates a new instance of the struct.
struct Mat_t Mat_eye();
struct Mat_t Mat_transl(const double x, const double y, const double z);
struct Mat_t Mat_rotx(const double rx);
struct Mat_t Mat_roty(const double ry);
struct Mat_t Mat_rotz(const double rz);
struct Mat_t Mat_makeCopy(struct Mat_t *inst);
struct Mat_t Mat_values(const double nx, const double ox, const double ax, const double tx,
	const double ny, const double oy, const double ay, const double ty,
	const double nz, const double oz, const double az, const double tz);


void Mat_Copy(struct Mat_t *out1, const struct Mat_t *in1);
void Mat_SetEye(struct Mat_t *inout);
void Mat_Inv(struct Mat_t *inout);
void Mat_Multiply_cumul(struct Mat_t *in1out, const struct Mat_t *in2);
void Mat_Multiply_rotxyz(struct Mat_t *in1out, const double rx, const double ry, const double rz);
bool Mat_isHomogeneous(const struct Mat_t *inst);
void Mat_SetPos(struct Mat_t *in1out, const double x, const double y, const double z);
void Mat_SetPose_KUKA(struct Mat_t *in1out, const struct XYZWPR_t in);
void Mat_Get_VX(const struct Mat_t *inst, struct XYZ_t *out);
void Mat_Get_VY(const struct Mat_t *inst, struct XYZ_t *out);
void Mat_Get_VZ(const struct Mat_t *inst, struct XYZ_t *out);
void Mat_ToString(const struct Mat_t *inst, char *output, bool xyzwprOnly);

//These functions are mostly here as helpers 
void Mat_Inv_out(struct Mat_t *out, const struct Mat_t *in);
void Mat_Multiply_out(struct Mat_t *out, const struct Mat_t *inA, const struct Mat_t *inB);

//Functions to operate on the joints class
struct Joints_t Joints_create(int ndofs);
struct Joints_t Joints_copy(const double *joints, int ndofs);
void Joints_SetValues(struct Joints_t *inst, const double *values, int ndofs);
bool Joints_Valid(struct Joints_t *inst);
void Joints_ToString(struct Joints_t *inst, char *output);

struct Matrix2D_t* Matrix2D_Create();
void Matrix2D_Delete(struct Matrix2D_t **mat);
void Matrix2D_Set_Size(struct Matrix2D_t *mat, int rows, int cols);
int Matrix2D_Size(const struct Matrix2D_t *mat, int dim);
int Matrix2D_Get_ncols(const struct Matrix2D_t *var);
int Matrix2D_Get_nrows(const struct Matrix2D_t *var);
double Matrix2D_Get_ij(const struct Matrix2D_t *var, int i, int j);
double* Matrix2D_Get_col(const struct Matrix2D_t *var, int col);

void Debug_Array(const double *array, int arraysize);
void Debug_Matrix2D(const struct Matrix2D_t *mat);


struct XYZWPR_t XYZWPR_Create(double x,double y,double z,
						      double w,double p,double r);

//XYZ functions, consider adding inline if debug performance matters
double XYZ_Dot(const struct XYZ_t *v, const struct XYZ_t *q);
double XYZ_Norm(const struct XYZ_t *v);
void XYZ_Cross(struct XYZ_t *in1out, const struct XYZ_t *in2);
void XYZ_Normalize(struct XYZ_t *in1out);
//These functions are mostly here as helpers 
void XYZ_Cross_out(struct XYZ_t *out, const struct XYZ_t *in1, const struct XYZ_t *in2);
void XYZ_Copy(struct XYZ_t *out, const struct XYZ_t *in);


//Internal functions
bool		  _RoboDK_connect_smart(struct RoboDK_t *inst); //Complete
bool          _RoboDK_connect(struct RoboDK_t *inst); //Complete

bool          _RoboDK_disconnect(struct RoboDK_t* inst); /// 

bool          _RoboDK_connected(struct RoboDK_t *inst); //Complete
bool          _RoboDK_check_connection(struct RoboDK_t *inst); //Complete

bool          _RoboDK_send_Int(struct RoboDK_t *inst, int32_t number); //Complete
bool          _RoboDK_send_Line(struct RoboDK_t *inst, const char *); //Complete
bool          _RoboDK_send_Item(struct RoboDK_t *inst, const struct Item_t *item); //Complete
bool          _RoboDK_send_Array(struct RoboDK_t *inst, const double *values, int size); //Complete
bool          _RoboDK_send_Pose(struct RoboDK_t *inst, const struct Mat_t pose); //Complete


int32_t       _RoboDK_recv_Int(struct RoboDK_t *inst); //Complete
bool          _RoboDK_recv_Line(struct RoboDK_t *inst, char *output); //Complete
struct Item_t _RoboDK_recv_Item(struct RoboDK_t *inst); //Complete
struct Mat_t  _RoboDK_recv_Pose(struct RoboDK_t *inst); //Complete
bool		  _RoboDK_recv_Array(struct RoboDK_t *inst, double *pValues, int *pSize); //Complete
struct Joints_t _RoboDK_recv_Array_Joints(struct RoboDK_t *inst); //Complete

bool          _RoboDK_check_status(struct RoboDK_t *inst); //Complete

void          _RoboDK_moveX(struct RoboDK_t *inst, const struct Item_t *target, const struct Joints_t *joints, const struct Mat_t *mat_target, const struct Item_t *itemrobot, int movetype, bool blocking);
void          _RoboDK_moveC(struct RoboDK_t* inst, const struct Item_t* target1, const struct Joints_t* joints1, const struct Mat_t* mat_target1, const struct Item_t* target2, const struct Joints_t* joints2, const struct Mat_t* mat_target2, const struct Item_t* itemrobot, bool blocking);
