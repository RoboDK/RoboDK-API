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

/// \brief The Matrix2D_t struct represents a variable size 2d Matrix. Use the Matrix2D_... functions to oeprate on this variable sized matrix.
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


//Platform indepedant IO operations
void ThreadSleep(unsigned long nMilliseconds);
void StartProcess(const char* applicationPath, const char* arguments, int64_t* processID);
int  SocketWrite(SOCKET, void *buffer, int bufferSize);

//RoboDK class Functions
void RoboDK_Connect_default(struct RoboDK_t *inst); //Complete
void RoboDK_Connect(struct RoboDK_t *inst, const char* robodk_ip, int com_port, const char *args, const char *path); //Complete
void RoboDK_ShowMessage(struct RoboDK_t *inst, const char *message, bool isPopup); //Complete
struct Item_t RoboDK_getItem(struct RoboDK_t *inst, const char *name, enum eITEM_TYPE itemtype); //Complete
void RoboDK_setRunMode(struct RoboDK_t *inst, int run_mode); //Complete

//RoboDK item class functions
bool Item_Valid(const struct Item_t *item);
void Item_Name(const struct Item_t *inst, char *nameOut); //Complete
struct Mat_t Item_Pose(const struct Item_t *inst); //Complete
//Robot specific item commands
struct Joints_t Item_Joints(const struct Item_t *inst); //Complete
void Item_MoveJ_joints(struct Item_t *inst, struct Joints_t *joints, bool isBlocking); //Complete
void Item_MoveJ_mat(struct Item_t *inst, struct Mat_t *joints, bool isBlocking); //Complete
void Item_WaitMove(const struct Item_t *inst, double timeout_sec); //Complete
bool Item_Connect(const struct Item_t *inst, const char *robot_ip); //Complete

//Matrix functions, not directly related to robodk's api but needed to manipulate matrices as double[16] arrays.
//Upercase first letter after _ means it operates on an instance of the struct while lowercase creates a new instance of the struct.
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

/////////////////////////////////////////////////////////////////
/// @brief Creates a new 2D matrix \ref Matrix2D_t.. Use \ref Matrix2D_Delete to delete the matrix (to free the memory).
/// The Procedure @ref Debug_Matrix2D shows an example to read data from a Matrix2D_t
struct Matrix2D_t* Matrix2D_Create();

/// @brief Deletes a \ref Matrix2D_t.
/// @param[in] mat: Pointer of the pointer to the matrix
void Matrix2D_Delete(struct Matrix2D_t **mat);

/// @brief Sets the size of a \ref Matrix2D_t.
/// @param[in/out] mat: Pointer to the matrix
/// @param[in] rows: The number of rows.
/// @param[in] cols: The number of columns.
void Matrix2D_Set_Size(struct Matrix2D_t *mat, int rows, int cols);

/// @brief Sets the size of a \ref Matrix2D_t.
/// @param[in/out] mat: Pointer to the matrix
/// @param[in] dim: Dimension (1 or 2)
int Matrix2D_Size(const struct Matrix2D_t *mat, int dim);

/// @brief Returns the number of columns of a \ref Matrix2D_t.
/// @param[in] mat: Pointer to the matrix
/// Returns the number of columns (Second dimension)
int Matrix2D_Get_ncols(const struct Matrix2D_t *var);

/// @brief Returns the number of rows of a \ref Matrix2D_t.
/// @param[in] mat: Pointer to the matrix
/// Returns the number of rows (First dimension)
int Matrix2D_Get_nrows(const struct Matrix2D_t *var);

/// @brief Returns the value at location [i,j] of a \ref Matrix2D_t.
/// @param[in] mat: Pointer to the matrix
/// Returns the value of the cell
double Matrix2D_Get_ij(const struct Matrix2D_t *var, int i, int j);

/// @brief Returns the pointer of a column of a \ref Matrix2D_t.
/// A column has \ref Matrix2D_Get_nrows values that can be accessed/modified from the returned pointer continuously.
/// @param[in] mat: Pointer to the matrix
/// @param[in] col: Column to retreive.
/// /return double array (internal pointer) to the column
double* Matrix2D_Get_col(const struct Matrix2D_t *var, int col);

/// @brief Show an array through STDOUT
/// Given an array of doubles, it generates a string
void Debug_Array(const double *array, int arraysize);

/// @brief Display the content of a \ref Matrix2D_t through STDOUT. This is only intended for debug purposes.
/// @param[in] mat: Pointer to the matrix
void Debug_Matrix2D(const struct Matrix2D_t *mat);


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
bool          _RoboDK_connected(struct RoboDK_t *inst); //Complete
bool          _RoboDK_check_connection(struct RoboDK_t *inst); //Complete

bool          _RoboDK_send_Int(struct RoboDK_t *inst, int32_t number); //Complete
bool          _RoboDK_send_Line(struct RoboDK_t *inst, const char *); //Complete
bool          _RoboDK_send_Item(struct RoboDK_t *inst, const struct Item_t *item); //Complete
bool          _RoboDK_send_Array(struct RoboDK_t *inst, const double *values, int size); //Complete

int32_t       _RoboDK_recv_Int(struct RoboDK_t *inst); //Complete
bool          _RoboDK_recv_Line(struct RoboDK_t *inst, char *output); //Complete
struct Item_t _RoboDK_recv_Item(struct RoboDK_t *inst); //Complete
struct Mat_t  _RoboDK_recv_Pose(struct RoboDK_t *inst); //Complete
bool		  _RoboDK_recv_Array(struct RoboDK_t *inst, double *pValues, int *pSize); //Complete
struct Joints_t _RoboDK_recv_Array_Joints(struct RoboDK_t *inst); //Complete

bool          _RoboDK_check_status(struct RoboDK_t *inst); //Complete

void          _RoboDK_moveX(struct RoboDK_t *inst, const struct Item_t *target, const struct Joints_t *joints, const struct Mat_t *mat_target, const struct Item_t *itemrobot, int movetype, bool blocking);

