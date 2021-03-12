#include "robodk_api_c.h"

//Platform indepedant IO operations
void ThreadSleep(unsigned long nMilliseconds) {
#if defined(_WIN32)
	Sleep(nMilliseconds);
#elif defined(POSIX)
	usleep(nMilliseconds * 1000);
#endif
}

int SocketWrite(SOCKET sock, void *buffer, int bufferSize) {
#if defined(_WIN32)
	return send(sock, (char *)buffer, bufferSize, 0);
#elif defined(POSIX)
	#warning todo
#endif
}



int socketRead(SOCKET sock, void *outBuffer, int bufferSize) {
#if defined(_WIN32)
	return recv(sock, (char *)outBuffer, bufferSize, 0);
#elif defined(POSIX)
	#warning todo
#endif
}

//Takes timeout in ms
void setSocketTimeout(SOCKET sock, int timeout_ms) {
	struct timeval timeout;      
#if defined(_WIN32)
	timeout.tv_sec = timeout_ms * 0.001;
	timeout.tv_usec = 0;
	setsockopt(sock, SOL_SOCKET, SO_RCVTIMEO, (char *)&timeout,sizeof(struct timeval));
#elif defined(POSIX)
	#warning todo
#endif
}

int socketBytesAvailable(SOCKET sock) {
#if defined(_WIN32)
	unsigned long bytes_available;
	ioctlsocket(sock, FIONREAD, &bytes_available);
	return bytes_available;
#elif defined(POSIX)
	#warning todo
#endif

}

void StartProcess(const char* applicationPath, const char* arguments, int64_t* processID) {
#if defined(_WIN32)
	wchar_t ProcessName[MAX_STR_LENGTH];
	STARTUPINFOA si;
	PROCESS_INFORMATION pi;
	mbstowcs(ProcessName, applicationPath, MAX_STR_LENGTH);
	//wcscpy(ProcessName, applicationPath);
	ZeroMemory(&si, sizeof(si));
	si.cb = sizeof(si);
	ZeroMemory(&pi, sizeof(pi));
	/*
	if( argc != 2 )
	{
		printf("Usage: %s [cmdline]\n", argv[0]);
		return;
	}
	*/
	// Start the child process. 
	if (!CreateProcessA(NULL,   // No module name (use command line)
		(LPSTR)applicationPath,        // Command line
		NULL,           // Process handle not inheritable
		NULL,           // Thread handle not inheritable
		FALSE,          // Set handle inheritance to FALSE
		0,              // No creation flags
		NULL,           // Use parent's environment block
		NULL,           // Use parent's starting directory 
		&si,            // Pointer to STARTUPINFO structure
		&pi)           // Pointer to PROCESS_INFORMATION structure
		)
	{
		printf("CreateProcess failed (%d).\n", GetLastError());
		return;
	}

	// Wait until child process exits.
	WaitForSingleObject(pi.hProcess, 500);
	*processID = pi.dwProcessId;

	// Close process and thread handles. 
	CloseHandle(pi.hProcess);
	CloseHandle(pi.hThread);
#elif defined(POSIX)
	#warning todo
#endif
}


void RoboDK_Connect_default(struct RoboDK_t *inst) {
	RoboDK_Connect(inst, "", -1, "", "");
}

void RoboDK_Connect(struct RoboDK_t *inst, const char* robodk_ip, int com_port, const char *args, const char *path) {
	//_COM = nullptr;
	//_IP = robodk_ip;
	strcpy(inst->_IP, robodk_ip);
	strcpy(inst->_ARGUMENTS, args);
	//_TIMEOUT = ROBODK_API_TIMEOUT;
	inst->_TIMEOUT = ROBODK_API_TIMEOUT;
	inst->_PROCESS = 0;

	inst->_PORT = com_port;
	strcpy(inst->_ROBODK_BIN, path);
	if (inst->_PORT < 0) {
		inst->_PORT = ROBODK_DEFAULT_PORT;
	}
	if (strlen(inst->_ROBODK_BIN) == 0) {
		strcpy(inst->_ROBODK_BIN, ROBODK_DEFAULT_PATH_BIN);
	}
	//_ARGUMENTS = args;
	if (com_port > 0) {
		char portStr[8];
		sprintf(portStr, "%d", com_port);
		strcat(inst->_ARGUMENTS, " /PORT=");
		strcat(inst->_ARGUMENTS, portStr);
	}
	_RoboDK_connect_smart(inst);
}

void RoboDK_ShowMessage(struct RoboDK_t *inst, const char *message, bool isPopup) {
	_RoboDK_check_connection(inst);
	if (isPopup)
	{
		_RoboDK_send_Line(inst, "ShowMessage");
		_RoboDK_send_Line(inst, message);
		inst->_TIMEOUT = 3600 * 1000;
		_RoboDK_check_status(inst);
		inst->_TIMEOUT = ROBODK_API_TIMEOUT;
	}
	else
	{
		_RoboDK_send_Line(inst, "ShowMessageStatus");
		_RoboDK_send_Line(inst, message);
		_RoboDK_check_status(inst);
	}
}

struct Item_t RoboDK_getItem(struct RoboDK_t *inst, const char *name, enum eITEM_TYPE itemtype) {
	_RoboDK_check_connection(inst);
	if (itemtype < 0) {
		_RoboDK_send_Line(inst, "G_Item");
		_RoboDK_send_Line(inst, name);
	}
	else {
		_RoboDK_send_Line(inst, "G_Item2");
		_RoboDK_send_Line(inst, name);
		_RoboDK_send_Int(inst, itemtype);
	}
	struct Item_t item = _RoboDK_recv_Item(inst);
	_RoboDK_check_status(inst);
	return item;
}

bool Item_Valid(const struct Item_t *item) {
	return item->_PTR != 0;
}

void Item_Name(const struct Item_t *inst, char *nameOut) {
	_RoboDK_check_connection(inst->_RDK);
	_RoboDK_send_Line(inst->_RDK, "G_Name");
	_RoboDK_send_Item(inst->_RDK, inst);
	_RoboDK_recv_Line(inst->_RDK, nameOut);
	_RoboDK_check_status(inst->_RDK);
	return;
}

struct Mat_t Item_Pose(const struct Item_t *inst) {  
	struct Mat_t pose;
	_RoboDK_check_connection(inst->_RDK);
	_RoboDK_send_Line(inst->_RDK, "G_Hlocal");
	_RoboDK_send_Item(inst->_RDK, inst);
	pose = _RoboDK_recv_Pose(inst->_RDK);
	_RoboDK_check_status(inst->_RDK);
	return pose;
}

struct Joints_t Item_Joints(const struct Item_t *inst) {
	struct Joints_t jnts;
	_RoboDK_check_connection(inst->_RDK);
	_RoboDK_send_Line(inst->_RDK, "G_Thetas");
	_RoboDK_send_Item(inst->_RDK, inst);
	jnts = _RoboDK_recv_Array_Joints(inst->_RDK);
	_RoboDK_check_status(inst->_RDK);
	return jnts;
}



////////////////////////////////////////////////////////////////////////////////////////////////////////////////

//Move using Joint angles


void Item_MoveJ_joints(struct Item_t *inst, struct Joints_t *joints, bool isBlocking) {

	_RoboDK_moveX(inst->_RDK, NULL, joints, NULL, inst, 1, isBlocking);
}

void Item_MoveL_joints(struct Item_t* inst, struct Joints_t* joints, bool isBlocking) {

	_RoboDK_moveX(inst->_RDK, NULL, joints, NULL, inst, 2, isBlocking);
}

void Item_MoveC_joints(struct Item_t* inst, struct Joints_t* joints1, struct Joints_t* joints2, bool isBlocking) {

	_RoboDK_moveC(inst->_RDK, NULL, joints1, NULL, NULL, joints2, NULL, inst, isBlocking);
}




//Move using items in the station tree (Targets)
void Item_MoveJ(struct Item_t* inst, struct Item_t* inst2, bool isBlocking) {

	_RoboDK_moveX(inst->_RDK, inst2, NULL, NULL, inst, 1, isBlocking);

}
void Item_MoveL(struct Item_t* inst, struct Item_t* inst2, bool isBlocking) {

	_RoboDK_moveX(inst->_RDK, inst2, NULL, NULL, inst, 2, isBlocking);

}

void Item_MoveC(struct Item_t* inst, struct Item_t* inst2, struct Item_t* inst3, bool isBlocking) {

	_RoboDK_moveC(inst->_RDK, inst2, NULL , NULL, inst3, NULL, NULL, inst, isBlocking);

}

//Move using mat entered as a Target Pose
void Item_MoveJ_mat(struct Item_t* inst, struct Mat_t* targetPose, bool isBlocking) {

	_RoboDK_moveX(inst->_RDK, NULL, NULL, targetPose, inst, 1, isBlocking);

}

void Item_MoveL_mat(struct Item_t* inst, struct Mat_t* targetPose, bool isBlocking) {

	_RoboDK_moveX(inst->_RDK, NULL, NULL, targetPose, inst, 2, isBlocking);

}
void Item_MoveC_mat(struct Item_t* inst, struct Mat_t* targetPose1, struct Mat_t* targetPose2, bool isBlocking) {

	_RoboDK_moveC(inst->_RDK, NULL, NULL, targetPose1, NULL, NULL,targetPose2,inst, isBlocking);

}

/////////////////////////////////////////////////////////////////////////////////////////////////////////////

void Item_setDO(const struct Item_t* inst, const char *io_var, const char *io_value) {
	_RoboDK_check_connection(inst->_RDK);
	_RoboDK_send_Line(inst->_RDK,"setDO");
	_RoboDK_send_Item(inst->_RDK, inst);
	_RoboDK_send_Line(inst->_RDK, io_var);
	_RoboDK_send_Line(inst->_RDK, io_value);
	_RoboDK_check_status(inst->_RDK);
}

void Item_setAO(const struct Item_t* inst, const char* io_var, const char* io_value) {
	_RoboDK_check_connection(inst->_RDK);
	_RoboDK_send_Line(inst->_RDK, "setAO");
	_RoboDK_send_Item(inst->_RDK, inst);
	_RoboDK_send_Line(inst->_RDK, io_var);
	_RoboDK_send_Line(inst->_RDK, io_value);
	_RoboDK_check_status(inst->_RDK);
}

char Item_getDI(const struct Item_t* inst, char* io_var) {
	_RoboDK_check_connection(inst->_RDK);
	_RoboDK_send_Line(inst->_RDK,"getDI");
	_RoboDK_send_Item(inst->_RDK, inst);
	_RoboDK_send_Line(inst->_RDK,io_var);
	_RoboDK_recv_Line(inst->_RDK, io_var);
	char io_value = *io_var;
	_RoboDK_check_status(inst->_RDK);
	return io_value;
}

char Item_getAI(const struct Item_t* inst, char* io_var) {
	_RoboDK_check_connection(inst->_RDK);
	_RoboDK_send_Line(inst->_RDK,"getAI");
	_RoboDK_send_Item(inst->_RDK, inst);
	_RoboDK_send_Line(inst->_RDK, io_var);
	_RoboDK_recv_Line(inst->_RDK, io_var);
	char di_value = *io_var;
	_RoboDK_check_status(inst->_RDK);
	return di_value;
}

/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

void Item_WaitMove(const struct Item_t *inst, double timeout_sec) {
	_RoboDK_check_connection(inst->_RDK);
	_RoboDK_send_Line(inst->_RDK, "WaitMove");
	_RoboDK_send_Item(inst->_RDK, inst);
	_RoboDK_check_status(inst->_RDK);
	inst->_RDK->_TIMEOUT = (int)(timeout_sec * 1000.0);
	_RoboDK_check_status(inst->_RDK); //Will wait here
	inst->_RDK->_TIMEOUT = ROBODK_API_TIMEOUT;
}

bool Item_Connect(const struct Item_t *inst,const char *robot_ip) {
	_RoboDK_check_connection(inst->_RDK);
	_RoboDK_send_Line(inst->_RDK,"Connect");
	_RoboDK_send_Item(inst->_RDK, inst);
	_RoboDK_send_Line(inst->_RDK,robot_ip);
	int status = _RoboDK_recv_Int(inst->_RDK);
	_RoboDK_check_status(inst->_RDK);
	return status != 0;
}

bool Item_Disconnect(const struct Item_t* inst) {
	_RoboDK_check_connection(inst->_RDK);
	_RoboDK_send_Line(inst->_RDK, "Disconnect");
	_RoboDK_send_Item(inst->_RDK, inst);
	int status = _RoboDK_recv_Int(inst->_RDK);
	_RoboDK_check_status(inst->_RDK);
	return status != 0;
}

int Item_Type(const struct Item_t* inst) {
	_RoboDK_check_connection(inst->_RDK);
	_RoboDK_send_Line(inst->_RDK, "G_Item_Type");
	_RoboDK_send_Item(inst->_RDK, inst);

	int itemtype = _RoboDK_recv_Int(inst->_RDK);
	_RoboDK_check_status(inst->_RDK);
	return itemtype;
}

void Item_Save(const struct Item_t* inst, char* filename) {
	//_RoboDK_Save(filename, inst->_RDK);
}

void Item_Delete(struct Item_t* inst) {
	_RoboDK_check_connection(inst->_RDK);
	_RoboDK_send_Line(inst->_RDK, "Remove");
	_RoboDK_send_Item(inst->_RDK, inst);
	_RoboDK_check_status(inst->_RDK);
	inst->_PTR = 0;
	inst->_TYPE = -1;
}

void Item_setParent(const struct Item_t* inst1, const struct Item_t* inst2) {
	_RoboDK_check_connection(inst1->_RDK);
	_RoboDK_send_Line(inst1->_RDK,"S_Parent");
	_RoboDK_send_Item(inst1->_RDK, inst1);
	_RoboDK_send_Item(inst2->_RDK, inst2);
	_RoboDK_check_status(inst1->_RDK);
}

void Item_setParentStatic(const struct Item_t* inst1, const struct Item_t* inst2) {
	_RoboDK_check_connection(inst1->_RDK);
	_RoboDK_send_Line(inst1->_RDK, "S_Parent_Static");
	_RoboDK_send_Item(inst1->_RDK, inst1);
	_RoboDK_send_Item(inst2->_RDK, inst2);
	_RoboDK_check_status(inst1->_RDK);
}

struct Item_t Item_AttachClosest(const struct Item_t* inst) {
	struct Item_t item_attached;
	_RoboDK_check_connection(inst->_RDK);
	_RoboDK_send_Line(inst->_RDK, "Attach_Closest");
	_RoboDK_send_Item(inst->_RDK, inst);
	item_attached = _RoboDK_recv_Item(inst->_RDK);
	_RoboDK_check_status(inst->_RDK);
	return item_attached;
}

struct Item_t Item_DetachClosest(const struct Item_t* inst1, const struct Item_t* inst2) {
	struct Item_t item_detached;
	_RoboDK_check_connection(inst1->_RDK);
	_RoboDK_send_Line(inst1->_RDK, "Detach_Closest");
	_RoboDK_send_Item(inst1->_RDK, inst1);
	_RoboDK_send_Item(inst2->_RDK, inst2);
	item_detached = _RoboDK_recv_Item(inst1->_RDK);
	_RoboDK_check_status(inst1->_RDK);
	return item_detached;
}

void Item_DetachAll(const struct Item_t* inst) {
	_RoboDK_check_connection(inst->_RDK);
	_RoboDK_send_Line(inst->_RDK, "Detach_All");
	_RoboDK_send_Item(inst->_RDK, inst);
	_RoboDK_send_Item(inst->_RDK, inst); //inst > parent here ;to be tested
	_RoboDK_check_status(inst->_RDK);
}



void Item_Scale(const struct Item_t* inst, double scale_xyz[3]) {
	_RoboDK_check_connection(inst->_RDK);
	_RoboDK_send_Line(inst->_RDK, "Scale");
	_RoboDK_send_Item(inst->_RDK, inst);
	_RoboDK_send_Array(inst->_RDK,scale_xyz, 3);
	_RoboDK_check_status(inst->_RDK);
}


struct Item_t Item_setMachiningParameters(const struct Item_t* inst, char ncfile, const struct Item_t* part_obj, char *options)
{
	struct Item_t program;
	_RoboDK_check_connection(inst->_RDK);
	_RoboDK_send_Line(inst->_RDK, "S_MachiningParams");
	_RoboDK_send_Item(inst->_RDK, inst);
	_RoboDK_send_Line(inst->_RDK, &ncfile);
	_RoboDK_send_Item(inst->_RDK, part_obj);
	//_RoboDK_send_Line(inst->_RDK, "NO_UPDATE " + options);
	_RoboDK_send_Line(inst->_RDK, options);
	inst->_RDK->_TIMEOUT = 3600 * 1000;
	program =_RoboDK_recv_Item(inst->_RDK);
	inst->_RDK->_TIMEOUT = ROBODK_API_TIMEOUT;
	double status = _RoboDK_recv_Int(inst->_RDK) / 1000.0;
	_RoboDK_check_status(inst->_RDK);
	return program;
}




void Item_setAsCartesianTarget(const struct Item_t* inst) {
	_RoboDK_check_connection(inst->_RDK);
	_RoboDK_send_Line(inst->_RDK, "S_Target_As_RT");
	_RoboDK_send_Item(inst->_RDK, inst);
	_RoboDK_check_status(inst->_RDK);
}

void Item_setAsJointTarget(const struct Item_t* inst) {
	_RoboDK_check_connection(inst->_RDK);
	_RoboDK_send_Line(inst->_RDK, "S_Target_As_JT");
	_RoboDK_send_Item(inst->_RDK, inst);
	_RoboDK_check_status(inst->_RDK);
}

bool Item_isJointTarget(const struct Item_t* inst) {
	_RoboDK_check_connection(inst->_RDK);
	_RoboDK_send_Line(inst->_RDK, "Target_Is_JT");
	_RoboDK_send_Item(inst->_RDK, inst);
	int is_jt = _RoboDK_recv_Int(inst->_RDK);
	_RoboDK_check_status(inst->_RDK);
	return is_jt > 0;
}

struct Joints_t Item_JointsHome(const struct Item_t* inst) {
	struct Joints_t jnts;
	_RoboDK_check_connection(inst->_RDK);
	_RoboDK_send_Line(inst->_RDK, "G_Home");
	_RoboDK_send_Item(inst->_RDK, inst);
	jnts = _RoboDK_recv_Array_Joints(inst->_RDK);
	_RoboDK_check_status(inst->_RDK);
	return jnts;
}

void Item_setJointsHome(const struct Item_t* inst, struct Joints_t jnts) {
	double angles[6];
	angles[0] = jnts._Values[0];
	angles[1] = jnts._Values[1];
	angles[2] = jnts._Values[2];
	angles[3] = jnts._Values[3];
	angles[4] = jnts._Values[4];
	angles[5] = jnts._Values[5];
	_RoboDK_check_connection(inst->_RDK);
	_RoboDK_send_Line(inst->_RDK, "S_Home");
	_RoboDK_send_Array(inst->_RDK, angles, jnts._nDOFs);
	_RoboDK_send_Item(inst->_RDK,inst);
	_RoboDK_check_status(inst->_RDK);
}

struct Item_t Item_ObjectLink(const struct Item_t* inst,int link_id) {

	struct Item_t item1;
	_RoboDK_check_connection(inst->_RDK);
	_RoboDK_send_Line(inst->_RDK, "G_LinkObjId");
	_RoboDK_send_Item(inst->_RDK, inst);
	_RoboDK_send_Int(inst->_RDK,link_id);
	item1 = _RoboDK_recv_Item(inst->_RDK);
	_RoboDK_check_status(inst->_RDK);
	return item1;
}
struct Item_t Item_getLink(const struct Item_t* inst, int link_id) {

	struct Item_t item1;
	_RoboDK_check_connection(inst->_RDK);
	_RoboDK_send_Line(inst->_RDK, "G_LinkType");
	_RoboDK_send_Item(inst->_RDK, inst);
	_RoboDK_send_Int(inst->_RDK, link_id);
	item1 = _RoboDK_recv_Item(inst->_RDK);
	_RoboDK_check_status(inst->_RDK);
	return item1;
}



void Item_JointLimits(const struct Item_t* inst, struct Joints_t *lower_limits, struct Joints_t *upper_limits) {
	_RoboDK_check_connection(inst->_RDK);
	_RoboDK_send_Line(inst->_RDK, "G_RobLimits");
	_RoboDK_send_Item(inst->_RDK, inst);
	_RoboDK_recv_Array(inst->_RDK, lower_limits->_Values, &lower_limits->_nDOFs);
	_RoboDK_recv_Array(inst->_RDK, upper_limits->_Values, &lower_limits->_nDOFs);
	double joints_type = _RoboDK_recv_Int(inst->_RDK) / 1000.0;
	_RoboDK_check_status(inst->_RDK);
}


void Item_setJointLimits(const struct Item_t* inst,struct Joints_t *lower_limits, struct Joints_t *upper_limits) {
	_RoboDK_check_connection(inst->_RDK);
	_RoboDK_send_Line(inst->_RDK, "S_RobLimits");
	_RoboDK_send_Item(inst->_RDK, inst);
	_RoboDK_send_Array(inst->_RDK,lower_limits->_Values,lower_limits->_nDOFs);
	_RoboDK_send_Array(inst->_RDK,upper_limits->_Values, lower_limits->_nDOFs);
	_RoboDK_check_status(inst->_RDK);
}

void Item_setRobot(const struct Item_t* inst) {
	_RoboDK_check_connection(inst->_RDK);
	_RoboDK_send_Line(inst->_RDK, "S_Robot");
	_RoboDK_send_Item(inst->_RDK, inst);
	//_RDK->_send_Item(robot);
	_RoboDK_check_status(inst->_RDK);
}

struct Item_t Item_AddTool(const struct Item_t* inst, const Mat_t &tool_pose, const char &tool_name) {
	_RoboDK_check_connection(inst->_RDK);
	_RoboDK_send_Line(inst->_RDK, "AddToolEmpty");
	_RoboDK_send_Item(inst->_RDK, inst);
	_RoboDK_send_Pose(inst->_RDK, tool_pose);
	_RoboDK_send_Line(inst->_RDK, &tool_name);
	struct Item_t newtool = _RoboDK_recv_Item(inst->_RDK);
	_RoboDK_check_status(inst->_RDK);
	return newtool;
}



void Item_setJoints(const struct Item_t* inst, struct Joints_t jnts) {
	double angles[6];
	angles[0] = jnts._Values[0];
	angles[1] = jnts._Values[1];
	angles[2] = jnts._Values[2];
	angles[3] = jnts._Values[3];
	angles[4] = jnts._Values[4];
	angles[5] = jnts._Values[5];
	_RoboDK_check_connection(inst->_RDK);
	_RoboDK_send_Line(inst->_RDK, "S_Thetas");
	_RoboDK_send_Array(inst->_RDK, angles, jnts._nDOFs);
	_RoboDK_send_Item(inst->_RDK, inst);
	_RoboDK_check_status(inst->_RDK);
}




struct Mat_t Item_PoseFrame(const struct Item_t* inst) { //in progress
	struct Mat_t pose;
	_RoboDK_check_connection(inst->_RDK);
	_RoboDK_send_Line(inst->_RDK, "G_Frame");
	_RoboDK_send_Item(inst->_RDK, inst);
	pose = _RoboDK_recv_Pose(inst->_RDK);
	_RoboDK_check_status(inst->_RDK);
	printf("Retrieving Active Reference Frame...\n");
	return pose;
}


struct Mat_t Item_PoseTool(const struct Item_t* inst) { //in progress
	struct Mat_t pose;
	_RoboDK_check_connection(inst->_RDK);
	_RoboDK_send_Line(inst->_RDK, "G_Tool");
	_RoboDK_send_Item(inst->_RDK, inst);
	pose = _RoboDK_recv_Pose(inst->_RDK);
	_RoboDK_check_status(inst->_RDK);
	printf("Retrieving Pose of Tool...\n");
	return pose;
}

void Item_setPose(const struct Item_t* inst, const struct Mat_t pose) {
	_RoboDK_check_connection(inst->_RDK);
	_RoboDK_send_Line(inst->_RDK, "S_Hlocal");
	_RoboDK_send_Item(inst->_RDK, inst);
	_RoboDK_send_Pose(inst->_RDK, pose);
	
	_RoboDK_check_status(inst->_RDK);

}



void Item_setPoseTool(const struct Item_t *inst, const struct Mat_t pose) {
	_RoboDK_check_connection(inst->_RDK);
	_RoboDK_send_Line(inst->_RDK, "S_Tool");
	_RoboDK_send_Pose(inst->_RDK,pose);
	_RoboDK_send_Item(inst->_RDK, inst);
	_RoboDK_check_status(inst->_RDK);
}

void Item_setPoseFrame(const struct Item_t *inst, const struct Mat_t pose) {
	_RoboDK_check_connection(inst->_RDK);
	_RoboDK_send_Line(inst->_RDK, "S_Frame");
	_RoboDK_send_Pose(inst->_RDK, pose);
	_RoboDK_send_Item(inst->_RDK, inst);
	_RoboDK_check_status(inst->_RDK);
}

void Item_setName(const struct Item_t* inst, const char *name) {

	_RoboDK_check_connection(inst->_RDK);
	_RoboDK_send_Line(inst->_RDK, "S_Name");
	_RoboDK_send_Item(inst->_RDK, inst);
	_RoboDK_send_Line(inst->_RDK, name);
	_RoboDK_check_status(inst->_RDK);
}

void Item_setAccuracyActive(const struct Item_t *inst, const int accurate) {
	_RoboDK_check_connection(inst->_RDK);
	_RoboDK_send_Line(inst->_RDK, "S_AbsAccOn");
	_RoboDK_send_Item(inst->_RDK, inst);
	_RoboDK_send_Int(inst->_RDK, accurate);
	_RoboDK_check_status(inst->_RDK);
}

struct Item_t Item_AddFrame(const char* framename, const struct Item_t* inst) {//in progress
	_RoboDK_check_connection(inst->_RDK);//initiating
	_RoboDK_send_Line(inst->_RDK, "Add_FRAME");//command
	_RoboDK_send_Line(inst->_RDK, framename);//frame name passed by user
	_RoboDK_send_Item(inst->_RDK, inst); //sending parent
	struct Item_t frame = _RoboDK_recv_Item(inst->_RDK);
	_RoboDK_check_status(inst->_RDK);
	printf("New Frame Added\n");
	return frame;

}


void Item_setRounding(const struct Item_t* inst, double zonedata) { //in progress
	_RoboDK_check_connection(inst->_RDK);
	_RoboDK_send_Line(inst->_RDK,"S_ZoneData");
	_RoboDK_send_Int(inst->_RDK, ((int)(zonedata * 1000.0)));
	_RoboDK_send_Item(inst->_RDK, inst);
	_RoboDK_check_status(inst->_RDK);
	printf("Rounding Value changed to %d\n", int(zonedata));
}

void Item_setSpeed(const struct Item_t* inst, double speed_linear, double accel_linear, double speed_joints , double accel_joints ) {
	_RoboDK_check_connection(inst->_RDK);
	_RoboDK_send_Line(inst->_RDK,"S_Speed4");
	_RoboDK_send_Item(inst->_RDK, inst);
	double speed_accel[4];
	speed_accel[0] = speed_linear;
	speed_accel[1] = accel_linear;
	speed_accel[2] = speed_joints;
	speed_accel[3] = accel_joints;
	_RoboDK_send_Array(inst->_RDK,speed_accel, 4);
	_RoboDK_check_status(inst->_RDK);
	printf("Speed Changed to new values\n");
}

bool Item_Busy(const struct Item_t* inst) { //pass program
	_RoboDK_check_connection(inst->_RDK);
	_RoboDK_send_Line(inst->_RDK, "IsBusy");
	_RoboDK_send_Item(inst->_RDK, inst);
	int busy = _RoboDK_recv_Int(inst->_RDK);
	_RoboDK_check_status(inst->_RDK);
	if (busy>0){
		printf("Program is running\n");
	}
	else {
		printf("Program is paused\n");
	}
	return(busy > 0);
}


void Item_Stop(const struct Item_t* inst) { //pass program
	_RoboDK_check_connection(inst->_RDK);
	_RoboDK_send_Line(inst->_RDK,"Stop");
	_RoboDK_send_Item(inst->_RDK, inst);
	_RoboDK_check_status(inst->_RDK);
}




void Item_setSimulationSpeed(const struct Item_t* inst, double speed) { 
	_RoboDK_check_connection(inst->_RDK);
	_RoboDK_send_Line(inst->_RDK, "SimulateSpeed");
	_RoboDK_send_Int(inst->_RDK, (int)(speed * 1000));
	_RoboDK_check_status(inst->_RDK);

}

double Item_SimulationSpeed(const struct Item_t* inst) {
	double speed = 0.000;
	_RoboDK_check_connection(inst->_RDK);
	_RoboDK_send_Line(inst->_RDK, "GetSimulateSpeed");
	speed = 0.001*(double)_RoboDK_recv_Int(inst->_RDK);
	_RoboDK_check_status(inst->_RDK);
	return speed;
}

void Item_ShowInstructions(const struct Item_t* inst, bool visible) { // pass Item with ITEM_TYPE_PROGRAM
	int t = 0;
	_RoboDK_check_connection(inst->_RDK);
	_RoboDK_send_Line(inst->_RDK, "Prog_ShowIns");
	_RoboDK_send_Item(inst->_RDK, inst);
	if (visible) {
		t = 1;
		printf("Instructions are visible\n");
	}
	else {
		t = 0;
		printf("Instructions are hidden\n");
	}
	_RoboDK_send_Int(inst->_RDK, t);
	_RoboDK_check_status(inst->_RDK);
}

void Item_ShowTargets(const struct Item_t* inst, bool visible) { // pass Item with ITEM_TYPE_PROGRAM
	int t = 0;  
	_RoboDK_check_connection(inst->_RDK);
	_RoboDK_send_Line(inst->_RDK, "Prog_ShowTargets");
	_RoboDK_send_Item(inst->_RDK, inst);
	if (visible) {
		t = 1;
		printf("Targets are visible\n");
	}
	else  {
		t = 0;
		printf("Targets are hidden\n");
	}

	_RoboDK_send_Int(inst->_RDK, t);
	_RoboDK_check_status(inst->_RDK);
}



int Item_InstructionCount(const struct Item_t* inst) {

	_RoboDK_check_connection(inst->_RDK);
	_RoboDK_send_Line(inst->_RDK, "Prog_Nins");
	_RoboDK_send_Item(inst->_RDK, inst);
	int nins = _RoboDK_recv_Int(inst->_RDK);
	_RoboDK_check_status(inst->_RDK);
	return nins;

}


void Item_setPoseAbs(const struct Item_t* inst, const struct Mat_t pose) {
	_RoboDK_check_connection(inst->_RDK);
	_RoboDK_send_Line(inst->_RDK, "S_Hlocal_Abs");
	_RoboDK_send_Item(inst->_RDK, inst);
	_RoboDK_send_Pose(inst->_RDK, pose);
	_RoboDK_check_status(inst->_RDK);
}


struct Mat_t Item_PoseAbs(const struct Item_t* inst) {
	struct Mat_t pose;
	_RoboDK_check_connection(inst->_RDK);
	_RoboDK_send_Line(inst->_RDK, "G_Hlocal_Abs");
	_RoboDK_send_Item(inst->_RDK, inst);
	pose = _RoboDK_recv_Pose(inst->_RDK);
	_RoboDK_check_status(inst->_RDK);
	return pose;
}



void Item_setGeometryPose(const struct Item_t* inst, const struct Mat_t pose) {
	_RoboDK_check_connection(inst->_RDK);
	_RoboDK_send_Line(inst->_RDK, "S_Hgeom");
	_RoboDK_send_Item(inst->_RDK, inst);
	_RoboDK_send_Pose(inst->_RDK, pose);
	_RoboDK_check_status(inst->_RDK);
}

struct Mat_t Item_GeometryPose(const struct Item_t* inst) {
	struct Mat_t pose;
	_RoboDK_check_connection(inst->_RDK);
	_RoboDK_send_Line(inst->_RDK, "G_Hgeom");
	_RoboDK_send_Item(inst->_RDK, inst);
	pose = _RoboDK_recv_Pose(inst->_RDK);
	_RoboDK_check_status(inst->_RDK);
	return pose;
}



void Item_setColor(const struct Item_t* inst, double R, double G, double B, double A) {
	_RoboDK_check_connection(inst->_RDK);
	_RoboDK_send_Line(inst->_RDK,"S_Color");
	_RoboDK_send_Item(inst->_RDK, inst);
	double color[4];
	color[0] = R;
	color[1] = G;
	color[2] = B;
	color[3] = A;
	_RoboDK_send_Array(inst->_RDK, color, 4);
	_RoboDK_check_status(inst->_RDK);

}

struct Item_t Item_Parent(const struct Item_t* inst) {
	struct Item_t parent; 
	_RoboDK_check_connection(inst->_RDK);
	_RoboDK_send_Line(inst->_RDK, "G_Parent");
	_RoboDK_send_Item(inst->_RDK, inst);
	parent = _RoboDK_recv_Item(inst->_RDK);
	_RoboDK_check_status(inst->_RDK);
	return parent;
}

bool Item_Visible(const struct Item_t* inst) {
	_RoboDK_check_connection(inst->_RDK);
	_RoboDK_send_Line(inst->_RDK, "G_Visible");
	_RoboDK_send_Item(inst->_RDK, inst);
	int visible = _RoboDK_recv_Int(inst->_RDK);
	_RoboDK_check_status(inst->_RDK);
	return (visible != 0);
}

void Item_setVisible(const struct Item_t* inst, bool visible, int visible_frame) {
	if (visible_frame < 0)
	{
		visible_frame = visible ? 1 : 0;
	}
	_RoboDK_check_connection(inst->_RDK);
	_RoboDK_send_Line(inst->_RDK, "S_Visible");
	_RoboDK_send_Item(inst->_RDK, inst);
	_RoboDK_send_Int(inst->_RDK,visible ? 1 : 0);
	_RoboDK_send_Int(inst->_RDK,visible_frame);
	_RoboDK_check_status(inst->_RDK);
}












struct Joints_t Item_SolveIK(const struct Item_t* inst, const struct Mat_t* pose, const struct Mat_t* tool, const struct Mat_t* ref) {
	struct Joints_t jnts;
	struct Mat_t base2flange = *pose; //pose of the robot flange with respect to the robot base frame
	if (tool != NULL) {
		struct Mat_t poseInv;
		//Mat_Inv_out();
		//base2flange = pose * tool->inv();
	}
	if (ref != NULL) {
		//base2flange = (*ref) * base2flange;
	}
	_RoboDK_check_connection(inst->_RDK);
	_RoboDK_send_Line(inst->_RDK, "G_IK");
	_RoboDK_send_Pose(inst->_RDK, base2flange);
	_RoboDK_send_Item(inst->_RDK, inst);
	jnts = _RoboDK_recv_Array_Joints(inst->_RDK); //&jnts  VS
	_RoboDK_check_status(inst->_RDK);
	return jnts;
}


struct Mat_t Item_solveFK(const struct Item_t *inst, const struct Joints_t *joints, const struct Mat_t *tool_pose, const struct Mat_t *reference_pose) {
	_RoboDK_check_connection(inst->_RDK);
	_RoboDK_send_Line(inst->_RDK, "G_FK");
	_RoboDK_send_Array(inst->_RDK, joints->_Values, joints->_nDOFs);
	_RoboDK_send_Item(inst->_RDK, inst);
	struct Mat_t pose = _RoboDK_recv_Pose(inst->_RDK);
	_RoboDK_check_status(inst->_RDK);

	struct Mat_t base2flange;
	Mat_Copy(&base2flange,&pose);
	if (tool_pose != NULL) {
		Mat_Multiply_out(&base2flange,&pose,tool_pose);
	}
	if (reference_pose != NULL) {
		struct Mat_t temp;
		Mat_Inv_out(&temp, reference_pose);
		Mat_Multiply_cumul(&base2flange, &temp);
	}

	return base2flange;
}

void Item_FilterTarget(const struct Item_t *inst, const struct Mat_t *pose, const struct Joints_t *joints_approx,
	struct Mat_t *out_poseFiltered, struct Joints_t *out_joints_filtered) {
	const struct Joints_t *joints_approx_validPtr = joints_approx;
	struct Joints_t default_value = Joints_create(6);

	if (joints_approx == NULL) {
		joints_approx_validPtr = &default_value;
	}

	_RoboDK_check_connection(inst->_RDK);
	_RoboDK_send_Line(inst->_RDK, "FilterTarget");
	_RoboDK_send_Pose(inst->_RDK, *pose);
	_RoboDK_send_Array(inst->_RDK, joints_approx_validPtr->_Values, joints_approx_validPtr->_nDOFs);
	_RoboDK_send_Item(inst->_RDK, inst);
	struct Mat_t pose_filtered = _RoboDK_recv_Pose(inst->_RDK);
	struct Joints_t joints_filtered =_RoboDK_recv_Array_Joints(inst->_RDK);
	_RoboDK_check_status(inst->_RDK);
	*out_poseFiltered = pose_filtered;
	*out_joints_filtered = joints_filtered;

}

void RoboDK_setRunMode(struct RoboDK_t *inst,int run_mode) {
	_RoboDK_check_connection(inst);
	_RoboDK_send_Line(inst,"S_RunMode");
	_RoboDK_send_Int(inst,run_mode);
	_RoboDK_check_status(inst);
}

struct Mat_t Mat_eye() {
	struct Mat_t matTemp;
	Mat_SetEye(&matTemp);
	return matTemp;
}

struct Mat_t Mat_transl(const double x, const double y, const double z) {
	struct Mat_t matTemp;
	Mat_SetEye(&matTemp);
	Mat_SetPos(&matTemp, x, y, z);
	return matTemp;
}

struct Mat_t Mat_rotx(const double rx) {
	double cx = cos(rx);
	double sx = sin(rx);
	return Mat_values(1, 0, 0, 0, 0, cx, -sx, 0, 0, sx, cx, 0);
}

struct Mat_t Mat_roty(const double ry) {
	double cy = cos(ry);
	double sy = sin(ry);
	return Mat_values(cy, 0, sy, 0, 0, 1, 0, 0, -sy, 0, cy, 0);
}

struct Mat_t Mat_rotz(const double rz) {
	double cz = cos(rz);
	double sz = sin(rz);
	return Mat_values(cz, -sz, 0, 0, sz, cz, 0, 0, 0, 0, 1, 0);
}

struct Mat_t Mat_makeCopy(struct Mat_t *inst) {
	struct Mat_t tempMat;
	Mat_Copy(&tempMat, inst);
	return tempMat;
}

struct Mat_t Mat_values(const double nx, const double ox, const double ax, const double tx,
	const double ny, const double oy, const double ay, const double ty,
	const double nz, const double oz, const double az, const double tz) {
	struct Mat_t matTemp;
	matTemp.arr16[0] = nx;
	matTemp.arr16[1] = ox;
	matTemp.arr16[2] = ax;
	matTemp.arr16[3] = tx;
	matTemp.arr16[4] = ny;
	matTemp.arr16[5] = oy;
	matTemp.arr16[6] = ay;
	matTemp.arr16[7] = ty;
	matTemp.arr16[8] = nz;
	matTemp.arr16[9] = oz;
	matTemp.arr16[10] = az;
	matTemp.arr16[11] = tz;
	matTemp.arr16[12] = 0;
	matTemp.arr16[13] = 0;
	matTemp.arr16[14] = 0;
	matTemp.arr16[15] = 1;
	return matTemp;
}


void Mat_Copy(struct Mat_t *out, const struct Mat_t *in) {
	(out->arr16)[0] = (in->arr16)[0];
	(out->arr16)[1] = (in->arr16)[1];
	(out->arr16)[2] = (in->arr16)[2];
	(out->arr16)[3] = (in->arr16)[3];
	(out->arr16)[4] = (in->arr16)[4];
	(out->arr16)[5] = (in->arr16)[5];
	(out->arr16)[6] = (in->arr16)[6];
	(out->arr16)[7] = (in->arr16)[7];
	(out->arr16)[8] = (in->arr16)[8];
	(out->arr16)[9] = (in->arr16)[9];
	(out->arr16)[10] = (in->arr16)[10];
	(out->arr16)[11] = (in->arr16)[11];
	(out->arr16)[12] = (in->arr16)[12];
	(out->arr16)[13] = (in->arr16)[13];
	(out->arr16)[14] = (in->arr16)[14];
	(out->arr16)[15] = (in->arr16)[15];
}

void Mat_SetEye(struct Mat_t *inout) {
	(inout->arr16)[0] = 1;
	(inout->arr16)[1] = 0;
	(inout->arr16)[2] = 0;
	(inout->arr16)[3] = 0;
	(inout->arr16)[4] = 0;
	(inout->arr16)[5] = 1;
	(inout->arr16)[6] = 0;
	(inout->arr16)[7] = 0;
	(inout->arr16)[8] = 0;
	(inout->arr16)[9] = 0;
	(inout->arr16)[10] = 1;
	(inout->arr16)[11] = 0;
	(inout->arr16)[12] = 0;
	(inout->arr16)[13] = 0;
	(inout->arr16)[14] = 0;
	(inout->arr16)[15] = 1;
}

void Mat_Inv(struct Mat_t *inout) {
	struct Mat_t matTemp;
	Mat_Inv_out(&matTemp, inout);
	Mat_Copy(inout, &matTemp);
}

void Mat_Multiply_cumul(struct Mat_t *in1out, const struct Mat_t *in2) {
	struct Mat_t matTemp;
	Mat_Multiply_out(&matTemp, in1out, in2);
	Mat_Copy(in1out, &matTemp);
}

void Mat_Multiply_rotxyz(struct Mat_t *in1out, const double rx, const double ry, const double rz) {
	struct Mat_t matResult;
	struct Mat_t matTemp;
	matTemp = Mat_rotx(0);
	Mat_Multiply_cumul(&matResult, &matTemp);
	matTemp = Mat_roty(0);
	Mat_Multiply_cumul(&matResult, &matTemp);
	matTemp = Mat_rotz(0);
	Mat_Multiply_cumul(&matResult, &matTemp);
	return;
}

bool Mat_isHomogeneous(const struct Mat_t *inst) {
	const bool debug_info = true;
	struct XYZ_t vx, vy, vz;
	const double tol = 1e-7;
	Mat_Get_VX(inst, &vx);
	Mat_Get_VX(inst, &vy);
	Mat_Get_VX(inst, &vz);
	if (fabs(XYZ_Dot(&vx, &vy) > tol)) {
		if (debug_info) {
			fprintf(stderr, "Vector X and Y are not perpendicular!");
		}
		return false;
	}
	else if (fabs(XYZ_Dot(&vx, &vz) > tol)) {
		if (debug_info) {
			fprintf(stderr, "Vector X and Z are not perpendicular!");
		}
		return false;
	}
	else if (fabs(XYZ_Dot(&vy, &vz) > tol)) {
		if (debug_info) {
			fprintf(stderr, "Vector Y and Z are not perpendicular!");
		}
		return false;
	}
	else if (fabs((double)(XYZ_Norm(&vx) - 1.0)) > tol) {
		if (debug_info) {
			fprintf(stderr, "Vector X is not unitary! %f", XYZ_Norm(&vx));
		}
		return false;
	}
	else if (fabs((double)(XYZ_Norm(&vy) - 1.0)) > tol) {
		if (debug_info) {
			fprintf(stderr, "Vector Y is not unitary! %f", XYZ_Norm(&vy));
		}
		return false;
	}
	else if (fabs((double)(XYZ_Norm(&vz) - 1.0)) > tol) {
		if (debug_info) {
			fprintf(stderr, "Vector Z is not unitary! %f", XYZ_Norm(&vz));
		}
		return false;
	}
	return true;
}

void Mat_SetPos(struct Mat_t *in1out, const double x, const double y, const double z) {
	in1out->arr16[12] = x;
	in1out->arr16[13] = y;
	in1out->arr16[14] = z;
}

void Mat_SetPose_KUKA(struct Mat_t *in1out, const struct XYZWPR_t in) {
	double x = in.arr6[0];
	double y = in.arr6[1];
	double z = in.arr6[2];
	double r = in.arr6[3];
	double p = in.arr6[4];
	double w = in.arr6[5];

	double a = r * M_PI / 180.0;
	double b = p * M_PI / 180.0;
	double c = w * M_PI / 180.0;

	double ca = cos(a);
	double sa = sin(a);
	double cb = cos(b);
	double sb = sin(b);
	double cc = cos(c);
	double sc = sin(c);

	in1out->arr16[0] = cb * ca;
	in1out->arr16[4] = ca * sc*sb - cc * sa;
	in1out->arr16[8] = sc * sa + cc * ca*sb;
	in1out->arr16[12] = x;

	in1out->arr16[1] = cb * sa;
	in1out->arr16[5] = cc * ca + sc * sb*sa;
	in1out->arr16[9] = cc * sb*sa - ca * sc;
	in1out->arr16[13] = y;

	in1out->arr16[2] = -sb;
	in1out->arr16[6] = cb * sc;
	in1out->arr16[10] = cc * cb;
	in1out->arr16[14] = z;

	in1out->arr16[3] = 0.0;
	in1out->arr16[7] = 0.0;
	in1out->arr16[11] = 0.0;
	in1out->arr16[15] = 1.0;
}

void Mat_Get_VX(const struct Mat_t *inst, struct XYZ_t *out) {
	out->arr3[0] = inst->arr16[0];
	out->arr3[1] = inst->arr16[1];
	out->arr3[2] = inst->arr16[2];
}

void Mat_Get_VY(const struct Mat_t *inst, struct XYZ_t *out) {
	out->arr3[0] = inst->arr16[4];
	out->arr3[1] = inst->arr16[5];
	out->arr3[2] = inst->arr16[6];
}

void Mat_Get_VZ(const struct Mat_t *inst, struct XYZ_t *out) {
	out->arr3[0] = inst->arr16[8];
	out->arr3[1] = inst->arr16[9];
	out->arr3[2] = inst->arr16[10];
}


void Mat_ToString(const struct Mat_t *inst, char *output, bool xyzwprOnly) {
	strcpy(output, "");

	strcat(output, "Mat(XYZRPW_2_Mat(");
	double x = inst->arr16[12];
	double y = inst->arr16[13];
	double z = inst->arr16[14];
	double w, p, r;
	if (inst->arr16[2] > (1.0 - 1e-6)) {
		p = -M_PI * 0.5;
		r = 0;
		w = atan2(-inst->arr16[9], inst->arr16[5]);
	}
	else if (inst->arr16[2] < -1.0 + 1e-6) {
		p = 0.5*M_PI;
		r = 0;
		w = atan2(inst->arr16[9], inst->arr16[5]);
	}
	else {
		p = atan2(-inst->arr16[2], sqrt(inst->arr16[0] * inst->arr16[0] + inst->arr16[1] * inst->arr16[1]));
		w = atan2(inst->arr16[1], inst->arr16[0]);
		r = atan2(inst->arr16[6], inst->arr16[10]);
	}
	r = r * 180.0 / M_PI;
	p = p * 180.0 / M_PI;
	w = w * 180.0 / M_PI;
	char bufferTemp[128];
	sprintf(bufferTemp, "%12.3f,%12.3f,%12.3f,%12.3f,%12.3f,%12.3f))\n", x, y, z, w, p, r);
	strcat(output, bufferTemp);

	if (xyzwprOnly == true) {
		return;
	}
	for (int i = 0; i < 4; i++) {
		for (int j = 0; j < 4; j++) {
			char tempbuffer[20];
			if (inst->arr16[j * 4 + i] < 1e9) {
				sprintf(tempbuffer, "%12.3f,", inst->arr16[j * 4 + i]);
			}
			else {
				sprintf(tempbuffer, "%12.3g,", inst->arr16[j * 4 + i]);
			}
			strcat(output, tempbuffer);
		}
		strcat(output, "\n");
	}
}

void Mat_Inv_out(struct Mat_t *out, const struct Mat_t *in) {
	(out->arr16)[0] = (in->arr16)[0];
	(out->arr16)[1] = (in->arr16)[4];
	(out->arr16)[2] = (in->arr16)[8];
	(out->arr16)[3] = 0;
	(out->arr16)[4] = (in->arr16)[1];
	(out->arr16)[5] = (in->arr16)[5];
	(out->arr16)[6] = (in->arr16)[9];
	(out->arr16)[7] = 0;
	(out->arr16)[8] = (in->arr16)[2];
	(out->arr16)[9] = (in->arr16)[6];
	(out->arr16)[10] = (in->arr16)[10];
	(out->arr16)[11] = 0;
	(out->arr16)[12] = -((in->arr16)[0] * (in->arr16)[12] + (in->arr16)[1] * (in->arr16)[13] + (in->arr16)[2] * (in->arr16)[14]);
	(out->arr16)[13] = -((in->arr16)[4] * (in->arr16)[12] + (in->arr16)[5] * (in->arr16)[13] + (in->arr16)[6] * (in->arr16)[14]);
	(out->arr16)[14] = -((in->arr16)[8] * (in->arr16)[12] + (in->arr16)[9] * (in->arr16)[13] + (in->arr16)[10] * (in->arr16)[14]);
	(out->arr16)[15] = 1;
}

void Mat_Multiply_out(struct Mat_t *out, const struct Mat_t *inA, const struct Mat_t *inB) {
	(out->arr16)[0] = (inA->arr16)[0] * (inB->arr16)[0] + (inA->arr16)[4] * (inB->arr16)[1] + (inA->arr16)[8] * (inB->arr16)[2];
	(out->arr16)[1] = (inA->arr16)[1] * (inB->arr16)[0] + (inA->arr16)[5] * (inB->arr16)[1] + (inA->arr16)[9] * (inB->arr16)[2];
	(out->arr16)[2] = (inA->arr16)[2] * (inB->arr16)[0] + (inA->arr16)[6] * (inB->arr16)[1] + (inA->arr16)[10] * (inB->arr16)[2];
	(out->arr16)[3] = 0;
	(out->arr16)[4] = (inA->arr16)[0] * (inB->arr16)[4] + (inA->arr16)[4] * (inB->arr16)[5] + (inA->arr16)[8] * (inB->arr16)[6];
	(out->arr16)[5] = (inA->arr16)[1] * (inB->arr16)[4] + (inA->arr16)[5] * (inB->arr16)[5] + (inA->arr16)[9] * (inB->arr16)[6];
	(out->arr16)[6] = (inA->arr16)[2] * (inB->arr16)[4] + (inA->arr16)[6] * (inB->arr16)[5] + (inA->arr16)[10] * (inB->arr16)[6];
	(out->arr16)[7] = 0;
	(out->arr16)[8] = (inA->arr16)[0] * (inB->arr16)[8] + (inA->arr16)[4] * (inB->arr16)[9] + (inA->arr16)[8] * (inB->arr16)[10];
	(out->arr16)[9] = (inA->arr16)[1] * (inB->arr16)[8] + (inA->arr16)[5] * (inB->arr16)[9] + (inA->arr16)[9] * (inB->arr16)[10];
	(out->arr16)[10] = (inA->arr16)[2] * (inB->arr16)[8] + (inA->arr16)[6] * (inB->arr16)[9] + (inA->arr16)[10] * (inB->arr16)[10];
	(out->arr16)[11] = 0;
	(out->arr16)[12] = (inA->arr16)[0] * (inB->arr16)[12] + (inA->arr16)[4] * (inB->arr16)[13] + (inA->arr16)[8] * (inB->arr16)[14] + (inA->arr16)[12];
	(out->arr16)[13] = (inA->arr16)[1] * (inB->arr16)[12] + (inA->arr16)[5] * (inB->arr16)[13] + (inA->arr16)[9] * (inB->arr16)[14] + (inA->arr16)[13];
	(out->arr16)[14] = (inA->arr16)[2] * (inB->arr16)[12] + (inA->arr16)[6] * (inB->arr16)[13] + (inA->arr16)[10] * (inB->arr16)[14] + (inA->arr16)[14];
	(out->arr16)[15] = 1;
}


struct Joints_t Joints_create(int ndofs) {
	struct Joints_t tempJoints2 = { 0, {0} };
	tempJoints2._nDOFs = min(ndofs, RDK_SIZE_JOINTS_MAX);
	for (int i = 0; i < tempJoints2._nDOFs; i++) {
		tempJoints2._Values[i] = 0.0;
	}
	return tempJoints2;
}

struct Joints_t Joints_copy(const double *joints, int ndofs) {
	struct Joints_t tempJoints;
	Joints_SetValues(&tempJoints, joints, ndofs);
	return tempJoints;
}

void Joints_SetValues(struct Joints_t *inst, const double *values, int ndofs) {
	if (ndofs > 0) {
		inst->_nDOFs = ndofs;
	}

	for (int i = 0; i < inst->_nDOFs; i++) {
		inst->_Values[i] = values[i];
	}
}

bool Joints_Valid(struct Joints_t *inst) {
	return inst->_nDOFs > 0;
}

void Joints_ToString(struct Joints_t *inst, char *output) {
	strcpy(output, "");
	if (!Joints_Valid(inst)) {
		strcat(output, "tJoints(Invalid)");
		return;
	}
	strcat(output, "tJoints({");
	char tempbuffer[20];
	for (int i = 0; i < inst->_nDOFs; i++) {
		if (inst->_Values[i] < 1e9) {
			sprintf(tempbuffer, "%10.2f,", inst->_Values[i]);
		}
		else {
			sprintf(tempbuffer, "%10.2g,", inst->_Values[i]);
		}
		strcat(output, tempbuffer);
	}
	strcat(output, "}  ,  ");
	sprintf(tempbuffer, "%d)\n", inst->_nDOFs);
	strcat(output, tempbuffer);
	return;
}

/////////////////////////////////////
// 2D matrix functions
/////////////////////////////////////
void emxInit_real_T(struct Matrix2D_t **pEmxArray, int numDimensions)
{
	struct Matrix2D_t *emxArray;
	int i;
	*pEmxArray = (struct Matrix2D_t *)malloc(sizeof(struct Matrix2D_t));
	emxArray = *pEmxArray;
	emxArray->data = (double *)NULL;
	emxArray->numDimensions = numDimensions;
	emxArray->size = (int *)malloc((unsigned int)(sizeof(int) * numDimensions));
	emxArray->allocatedSize = 0;
	emxArray->canFreeData = true;
	for (i = 0; i < numDimensions; i++) {
		emxArray->size[i] = 0;
	}
}
///
struct Matrix2D_t* Matrix2D_Create() {
	struct Matrix2D_t *matrix;
	emxInit_real_T((struct Matrix2D_t**)(&matrix), 2);
	return matrix;
}


void emxFree_real_T(struct Matrix2D_t **pEmxArray) {
	if (*pEmxArray != (struct Matrix2D_t *)NULL) {
		if (((*pEmxArray)->data != (double *)NULL) && (*pEmxArray)->canFreeData) {
			free((void *)(*pEmxArray)->data);
		}
		free((void *)(*pEmxArray)->size);
		free((void *)*pEmxArray);
		*pEmxArray = (struct Matrix2D_t *)NULL;
	}
}

void Matrix2D_Delete(struct Matrix2D_t **mat) {
	emxFree_real_T((struct Matrix2D_t**)(mat));
}



void emxEnsureCapacity(struct Matrix2D_t *emxArray, int oldNumel, unsigned int elementSize) {
	int newNumel;
	int i;
	double *newData;
	if (oldNumel < 0) {
		oldNumel = 0;
	}
	newNumel = 1;
	for (i = 0; i < emxArray->numDimensions; i++) {
		newNumel *= emxArray->size[i];
	}
	if (newNumel > emxArray->allocatedSize) {
		i = emxArray->allocatedSize;
		if (i < 16) {
			i = 16;
		}
		while (i < newNumel) {
			if (i > 1073741823) {
				i = (2147483647);//MAX_int32_T;
			}
			else {
				i <<= 1;
			}
		}
		newData = (double*)calloc((unsigned int)i, elementSize);
		if (emxArray->data != NULL) {
			memcpy(newData, emxArray->data, elementSize * oldNumel);
			if (emxArray->canFreeData) {
				free(emxArray->data);
			}
		}
		emxArray->data = newData;
		emxArray->allocatedSize = i;
		emxArray->canFreeData = true;
	}
}

void Matrix2D_Set_Size(struct Matrix2D_t *mat, int rows, int cols) {
	int old_numel;
	int numbel;
	old_numel = mat->size[0] * mat->size[1];
	mat->size[0] = rows;
	mat->size[1] = cols;
	numbel = rows * cols;
	emxEnsureCapacity(mat, old_numel, sizeof(double));
	/*for (i=0; i<numbel; i++){
	mat->data[i] = 0.0;
	}*/
}

int Matrix2D_Size(const struct Matrix2D_t *var, int dim) { // ONE BASED!!
	if (var->numDimensions >= dim) {
		return var->size[dim - 1];
	}
	else {
		return 0;
	}
}
int Matrix2D_Get_ncols(const struct Matrix2D_t *var) {
	return Matrix2D_Size(var, 2);
}
int Matrix2D_Get_nrows(const struct Matrix2D_t *var) {
	return Matrix2D_Size(var, 1);
}
double Matrix2D_Get_ij(const struct Matrix2D_t *var, int i, int j) { // ZERO BASED!!
	return var->data[var->size[0] * j + i];
}
void Matrix2D_SET_ij(const struct Matrix2D_t *var, int i, int j, double value) { // ZERO BASED!!
	var->data[var->size[0] * j + i] = value;
}

double *Matrix2D_Get_col(const struct Matrix2D_t *var, int col) { // ZERO BASED!!
	return (var->data + var->size[0] * col);
}


void Matrix2D_Add_Double(struct Matrix2D_t *var, const double *array, int numel) {
	int oldnumel;
	int size1 = var->size[0];
	int size2 = var->size[1];
	oldnumel = size1 * size2;
	var->size[1] = size2 + 1;
	emxEnsureCapacity(var, oldnumel, (int)sizeof(double));
	numel = min(numel, size1);
	for (int i = 0; i < numel; i++) {
		var->data[size1*size2 + i] = array[i];
	}
}

void Matrix2D_Add_Mat2D(struct Matrix2D_t *var, const struct Matrix2D_t *varadd) {
	int oldnumel;
	int size1 = var->size[0];
	int size2 = var->size[1];
	int size1_ap = varadd->size[0];
	int size2_ap = varadd->size[1];
	int numel = size1_ap * size2_ap;
	if (size1 != size1_ap) {
		return;
	}
	oldnumel = size1 * size2;
	var->size[1] = size2 + size2_ap;
	emxEnsureCapacity(var, oldnumel, (int)sizeof(double));
	for (int i = 0; i < numel; i++) {
		var->data[size1*size2 + i] = varadd->data[i];
	}
}

void Debug_Array(const double *array, int arraysize) {
	int i;
	for (i = 0; i < arraysize; i++) {
		//char chararray[500];  // You had better have room for what you are sprintf()ing!
		//sprintf(chararray, "%.3f", array[i]);
		//std::cout << chararray;
		printf("%.3f", array[i]);
		if (i < arraysize - 1) {
			//std::cout << " , ";
			printf(" , ");
		}
	}
}

void Debug_Matrix2D(const struct Matrix2D_t *emx) {
	int size1;
	int size2;
	int j;
	double *column;
	size1 = Matrix2D_Get_nrows(emx);
	size2 = Matrix2D_Get_ncols(emx);
	printf("Matrix size = [%i, %i]\n", size1, size2);
	//std::out << "Matrix size = [%i, %i]" << size1 << " " << size2 << "]\n";
	for (j = 0; j < size2; j++) {
		column = Matrix2D_Get_col(emx, j);
		Debug_Array(column, size1);
		printf("\n");
		//std::cout << "\n";
	}
}

struct XYZWPR_t XYZWPR_Create(double x, double y, double z,
	double w, double p, double r) {
	struct XYZWPR_t out;
	out.arr6[0] = x;
	out.arr6[1] = y;
	out.arr6[2] = z;
	out.arr6[3] = w;
	out.arr6[4] = p;
	out.arr6[5] = r;
	return out;
}

double XYZ_Dot(const struct XYZ_t *v, const struct XYZ_t *q) {
	return ((v->arr3)[0] * (q->arr3)[0] + (v->arr3)[1] * (q->arr3)[1] + (v->arr3)[2] * (q->arr3)[2]);
}

double XYZ_Norm(const struct XYZ_t *v) {
	return (sqrt((v->arr3)[0] * (v->arr3)[0] + (v->arr3)[1] * (v->arr3)[1] + (v->arr3)[2] * (v->arr3)[2]));
}

void XYZ_Cross(struct XYZ_t *in1out, const struct XYZ_t *in2) {
	struct XYZ_t xyzTemp;
	XYZ_Cross_out(&xyzTemp, in1out, in2);
	XYZ_Copy(in1out, &xyzTemp);
}

void XYZ_Normalize(struct XYZ_t *inout) {
	double norm;
	norm = sqrt((inout->arr3)[0] * (inout->arr3)[0] + (inout->arr3)[1] * (inout->arr3)[1] + (inout->arr3)[2] * (inout->arr3)[2]);
	(inout->arr3)[0] = (inout->arr3)[0] / norm;
	(inout->arr3)[1] = (inout->arr3)[1] / norm;
	(inout->arr3)[2] = (inout->arr3)[2] / norm;

}

void XYZ_Cross_out(struct XYZ_t *out, const struct XYZ_t *in1, const struct XYZ_t *in2) {
	(out->arr3)[0] = (in1->arr3)[1] * (in2->arr3)[2] - (in2->arr3)[1] * (in1->arr3)[2];
	(out->arr3)[1] = (in1->arr3)[2] * (in2->arr3)[0] - (in2->arr3)[2] * (in1->arr3)[0];
	(out->arr3)[2] = (in1->arr3)[0] * (in2->arr3)[1] - (in2->arr3)[0] * (in1->arr3)[1];
}

void XYZ_Copy(struct XYZ_t *out, const struct XYZ_t *in) {
	out->arr3[0] = in->arr3[0];
	out->arr3[1] = in->arr3[1];
	out->arr3[2] = in->arr3[2];
}




bool _RoboDK_connect_smart(struct RoboDK_t *inst) {
	//Establishes a connection with robodk. robodk must be running, otherwise, it will attempt to start it
	if (_RoboDK_connect(inst)) {
		fprintf(stderr, "The RoboDK API is connected!\n");
		return true;
	}
	fprintf(stderr, "...Trying to start RoboDK: ");
	fprintf(stderr, inst->_ROBODK_BIN);
	fprintf(stderr, " %s\n\0", inst->_ARGUMENTS);
	// Start RoboDK
	StartProcess(inst->_ROBODK_BIN, inst->_ARGUMENTS, &inst->_PROCESS);
	bool is_connected = _RoboDK_connect(inst);
	if (is_connected) {
		fprintf(stderr, "The RoboDK API is connected\n");
		return is_connected;
	}
	else {
		fprintf(stderr, "The RoboDK API is NOT connected!\n");
	}
	fprintf(stderr, "Could not start RoboDK!\n");
	return false;
}

bool _RoboDK_connect(struct RoboDK_t *inst) {
	//_disconnect();
	//_COM = new QTcpSocket();
	struct sockaddr_in _COM_PORT;
	inst->_COM = socket(AF_INET, SOCK_STREAM, 0);
	_COM_PORT.sin_family = AF_INET;
	_COM_PORT.sin_port = htons((uint16_t)inst->_PORT);
	if (strlen(inst->_IP) == 0) {
		//_COM->connectToHost("127.0.0.1", _PORT); //QHostAddress::LocalHost, _PORT);
		if (inet_pton(AF_INET, "127.0.0.1", &_COM_PORT.sin_addr.s_addr) == 0) {
			return false;
		}
		int retCode = connect(inst->_COM, (struct sockaddr *)&(_COM_PORT), sizeof(struct sockaddr_in));
		if (retCode == -1) {
			return false;
		}
	}
	else {
		//_COM->connectToHost(_IP, _PORT);
		if (inet_pton(AF_INET, inst->_IP, &_COM_PORT.sin_addr.s_addr) == 0) {
			return false;
		}
		int retCode = connect(inst->_COM, (struct sockaddr *)&(_COM_PORT), sizeof(struct sockaddr_in));
		if (retCode == -1) {
			return false;
		}
	}

	/*
	// RoboDK protocol to check that we are connected to the right port
	_COM->write(ROBODK_API_START_STRING); _COM->write(ROBODK_API_LF, 1);
	_COM->write("1 0"); _COM->write(ROBODK_API_LF, 1);
	*/
	SocketWrite(inst->_COM, (void *)ROBODK_API_START_STRING, sizeof(ROBODK_API_START_STRING));
	SocketWrite(inst->_COM, (void *)ROBODK_API_LF, 1);
	SocketWrite(inst->_COM, (void *) "1 0\n", sizeof("1 0\n"));
	SocketWrite(inst->_COM, (void *)ROBODK_API_LF, 1);
	//ThreadSleep(inst->_TIMEOUT);
	//QString read(_COM->readAll());
	char receiveBuffer[MAX_STR_LENGTH];
	int ret = socketRead(inst->_COM, receiveBuffer, MAX_STR_LENGTH);
	// make sure we receive the OK from RoboDK
	if ((ret <= 0) || strstr(receiveBuffer, ROBODK_API_READY_STRING) == NULL) {
		inst->_isConnected = false;
		return false;
	}
	inst->_isConnected = true;
	return true;
}

bool _RoboDK_connected(struct RoboDK_t *inst) {
	return inst->_isConnected;
}

bool _RoboDK_disconnect(struct RoboDK_t* inst) {
	if (inst->_isConnected == false) {
		return false;
	}
	closesocket(inst->_COM);
	return true;
}


bool _RoboDK_check_connection(struct RoboDK_t *inst) {
	if (_RoboDK_connected(inst)) {
		return true;
	}

	bool connection_ok = _RoboDK_connect_smart(inst);
	return connection_ok;
}


bool _RoboDK_send_Int(struct RoboDK_t *inst, int32_t number) {
	int32_t networkOrderNumber = 0;
	int i;
	for (i = 0; i < 4; i++) {
		networkOrderNumber += (((number >> (i * 8)) & (0xFF)) << (24 - i * 8));
	}

	SocketWrite(inst->_COM, &networkOrderNumber, sizeof(int32_t));
	return true;
}

bool _RoboDK_send_Line(struct RoboDK_t *inst, const char *inputLine) {
	char sendBuffer[MAX_STR_LENGTH];
	memset(sendBuffer, 0, MAX_STR_LENGTH);
	char *outputChar = sendBuffer;
	strcat(sendBuffer, inputLine);
	int i = 0;

	//Replace instances of newline
	while (inputLine[i] != '\0')
	{
		/* If occurrence of character is found */
		if (inputLine[i] == '\n')
		{
			*outputChar = '<';
			*outputChar++;
			*outputChar = 'b';
			*outputChar++;
			*outputChar = 'r';
			*outputChar++;
			*outputChar = '>';
			*outputChar++;
		}
		else {
			*outputChar = inputLine[i];
			*outputChar++;
		}
		i++;
	}

	SocketWrite(inst->_COM, sendBuffer, strlen(sendBuffer));
	SocketWrite(inst->_COM, (void *)ROBODK_API_LF, 1);
	return true;
}

bool _RoboDK_send_Item(struct RoboDK_t *inst, const struct Item_t *item) {
	if (inst->_isConnected == false) {
		return false;
	}
	char buffer[sizeof(uint64_t)];
	uint64_t ptrVal;
	if (item == NULL) {
		ptrVal = NULL;
	}
	else {
		ptrVal = item->_PTR;
	}
	for (int i = 0; i < 8; i++) {
		buffer[i] = (ptrVal >> (i * 8)) & 0xFF;
	}
	SocketWrite(inst->_COM, buffer, sizeof(uint64_t));
	return true;
}

bool _RoboDK_send_Array(struct RoboDK_t *inst, const double *values, int nvalues) {
	if (nvalues == 0) {
		return _RoboDK_send_Int(inst, 0);
	}
	if ((inst->_isConnected == false) || (values == NULL)) {
		return false;
	}
	if (!_RoboDK_send_Int(inst, nvalues)) { return false; }
	for (int i = 0; i < nvalues; i++) {
		double iValue = values[i];
		char valueIBytesSend[sizeof(double)];
		char valueIBytesNative[sizeof(double)];
		memcpy(valueIBytesNative, &iValue, sizeof(double));
		for (int k = 0; k < sizeof(double); k++) {
			valueIBytesSend[k] = valueIBytesNative[sizeof(double) - 1 - k];
		}
		SocketWrite(inst->_COM, &valueIBytesSend, sizeof(double));
	}

	return true;
}

bool _RoboDK_send_Pose(struct RoboDK_t *inst, const struct Mat_t pose) {
	if (inst->_isConnected == false) { return false; }
	char bufferBytes[16 * sizeof(double)];
	double valuei;
	for (int j = 0; j < 4; j++) {
		for (int i = 0; i < 4; i++) {
			valuei = pose.arr16[(j * 4) + i];
			char valueIBytes[sizeof(double)];
			memcpy(&valueIBytes, &valuei, sizeof(double));
			for (int k = 0; k < sizeof(double); k++) {
				bufferBytes[((i + (j * 4)) * 8) + k] = valueIBytes[sizeof(double) - 1 - k];
			}
		}
	}
	SocketWrite(inst->_COM, &bufferBytes, sizeof(bufferBytes));

	return true;
}


int32_t _RoboDK_recv_Int(struct RoboDK_t *inst) {
	int32_t value = -1; // do not change type
	int i;
	if (inst->_isConnected == false) { return false; }
	char buffer[sizeof(int32_t)];
	int bytesReceived = socketRead(inst->_COM, buffer, sizeof(int32_t));
	if (bytesReceived <= 0) {
		return -1;
	}
	for (i = 0; i < 4; i++) {
		value = buffer[i] << (24 - i * 8);
	}
	return value;
}


bool _RoboDK_recv_Line(struct RoboDK_t *inst, char *output) {
	int i = 0;
	bool isDone = false;
	while (!isDone) {
		char curByte;
		socketRead(inst->_COM, &curByte, 1);
		if (curByte == '\n') {
			output[i] = '\0';
			isDone = true;
		}
		else {
			output[i] = curByte;
		}
		i++;
	}
	return true;
}

struct Item_t _RoboDK_recv_Item(struct RoboDK_t *inst) {
	struct Item_t item;
	int i;
	item._RDK = inst;
	item._PTR = 0;
	item._TYPE = -1;
	if (inst->_isConnected == false) { return item; }
	if (socketBytesAvailable(inst->_COM) <= sizeof(uint64_t) + sizeof(int32_t)) {
		unsigned char buffer[8 + 4];
		int bytesReceived = socketRead(inst->_COM, buffer, sizeof(uint64_t) + sizeof(int32_t));
		if (bytesReceived <= 0) {
			return item;
		}
		item._PTR = 0;
		for (i = 0; i < 8; i++) {
			item._PTR += ((uint64_t)buffer[0 + i]) << (i * 8);
		}
		item._TYPE = 0;
		for (i = 0; i < 4; i++) {
			item._TYPE += buffer[sizeof(uint64_t) + i] << (24 - i * 8);
		}
	}

	return item;
}

struct Mat_t  _RoboDK_recv_Pose(struct RoboDK_t *inst) {
	struct Mat_t pose;
	memset(pose.arr16, 0, sizeof(double[16]));
	if (inst->_isConnected == false) { return pose; }
	int size = 16 * sizeof(double);
	char bufferBytes[16 * sizeof(double)];
	socketRead(inst->_COM, bufferBytes, size);
	for (int j = 0; j < 4; j++) {
		for (int i = 0; i < 4; i++) {
			char valueIBytes[sizeof(double)];
			for (int k = 0; k < sizeof(double); k++) {
				valueIBytes[sizeof(double) - 1 - k] = bufferBytes[((i + (j * 4)) * 8) + k];
			}
			double valuei;
			memcpy(&valuei, &valueIBytes, sizeof(double));
			pose.arr16[(j * 4) + i] = valuei;
		}
	}
	return pose;
}

bool _RoboDK_recv_Array(struct RoboDK_t *inst, double *pValues, int *pSize) {
	int nvalues = _RoboDK_recv_Int(inst);
	if ((inst->_isConnected == false) || nvalues < 0) { return false; }
	if (pSize != NULL) {
		*pSize = nvalues;
	}
	if (nvalues < 0 || nvalues > 50) { return false; } //check if the value is not too big
	int size = nvalues * sizeof(double);
	//if (socketBytesAvailable(inst->_COM) <= (size + 4)) {
	double valuei;
	for (int i = 0; i < nvalues; i++) {
		char bufferCurValue[sizeof(double)];
		char valueIBytes[sizeof(double)];
		int nread = socketRead(inst->_COM, &bufferCurValue, sizeof(double));
		if (nread < 0) {
			return false;
		}
		for (int k = 0; k < sizeof(double); k++) {
			valueIBytes[sizeof(double) - 1 - k] = bufferCurValue[k];
		}
		memcpy(&valuei, &valueIBytes, sizeof(double));
		pValues[i] = valuei;
	}
	//}
	return true;
}

struct Joints_t _RoboDK_recv_Array_Joints(struct RoboDK_t *inst) {
	struct Joints_t jnts;
	_RoboDK_recv_Array(inst, jnts._Values, &(jnts._nDOFs));
	return jnts;
}

bool _RoboDK_check_status(struct RoboDK_t *inst) {
	int32_t status = _RoboDK_recv_Int(inst);
	if (status == 0) {
		// everything is OK
		//status = status
	}
	else if (status > 0 && status < 10) {
		if (status == 1) {
			fprintf(stderr, "Invalid item provided: The item identifier provided is not valid or it does not exist.\n");
		}
		else if (status == 2) { //output warning only
			char strProblems[MAX_STR_LENGTH];
			_RoboDK_recv_Line(inst, strProblems);
			fprintf(stderr, "RoboDK API WARNING: %s\n", strProblems);
			return 0;
		}
		else if (status == 3) { // output error
			char strProblems[MAX_STR_LENGTH];
			_RoboDK_recv_Line(inst, strProblems);
			fprintf(stderr, "RoboDK API ERROR: %s\n", strProblems);
		}
		else if (status == 9) {
			fprintf(stderr, "Invalid RoboDK License");
		}
		else {
			fprintf(stderr, "Unknown error");
		}
		//print(strproblems);
		//throw new RDKException(strproblems); //raise Exception(strproblems)
	}
	else if (status < 100) {
		char strProblems[MAX_STR_LENGTH];
		_RoboDK_recv_Line(inst, strProblems);
		fprintf(stderr, "RoboDK API ERROR: %s\n", strProblems);
	}
	else {
		fprintf(stderr, "Communication problems with the RoboDK API");
	}
	return status;
}


void _RoboDK_moveX(struct RoboDK_t* inst, const struct Item_t* target, const struct Joints_t* joints, const struct Mat_t* mat_target, const struct Item_t* itemrobot, int movetype, bool blocking) {
	Item_WaitMove(itemrobot, 300);
	_RoboDK_send_Line(inst, "MoveX");
	_RoboDK_send_Int(inst, movetype);
	if (target != NULL) {
		_RoboDK_send_Int(inst, 3);
		_RoboDK_send_Array(inst, NULL, 0);
		_RoboDK_send_Item(inst, target);
	}
	else if (joints != NULL) {
		_RoboDK_send_Int(inst, 1);
		_RoboDK_send_Array(inst, joints->_Values, joints->_nDOFs);
		_RoboDK_send_Item(inst, NULL);
	}
	else if (mat_target != NULL) {// && mat_target.IsHomogeneous()) {
		_RoboDK_send_Int(inst, 2);
		_RoboDK_send_Array(inst, mat_target->arr16, 16); // keep it as array!
		_RoboDK_send_Item(inst, NULL);
	}
	else {
		//throw new RDKException("Invalid target type"); //raise Exception('Problems running function');
		fprintf(stderr, "Invalid target type");
		return;
	}
	_RoboDK_send_Item(inst, itemrobot);
	_RoboDK_check_status(inst);
	if (blocking) {
		Item_WaitMove(itemrobot, 300);
	}
}



void _RoboDK_moveC(struct RoboDK_t* inst, const struct Item_t* target1, const struct Joints_t* joints1, const struct Mat_t* mat_target1, const struct Item_t* target2, const struct Joints_t* joints2, const struct Mat_t* mat_target2, const struct Item_t* itemrobot, bool isblocking) {
	Item_WaitMove(itemrobot, 300);
	_RoboDK_send_Line(inst, "MoveC");
	_RoboDK_send_Int(inst,3);
	if (target1 != NULL) {
		_RoboDK_send_Int(inst, 3);
		_RoboDK_send_Array(inst, NULL, 0);
		_RoboDK_send_Item(inst, target1);
	}
	else if (joints1 != NULL) {
		_RoboDK_send_Int(inst, 1);
		_RoboDK_send_Array(inst, joints1->_Values, joints1->_nDOFs);
		_RoboDK_send_Item(inst, NULL);
	}
	else if (mat_target1 != NULL) {// && mat_target.IsHomogeneous()) {
		_RoboDK_send_Int(inst, 2);
		_RoboDK_send_Array(inst, mat_target1->arr16, 16); // keep it as array!
		_RoboDK_send_Item(inst, NULL);
	}
	else {
		//throw new RDKException("Invalid target type"); //raise Exception('Problems running function');
		fprintf(stderr, "Invalid target type");
		return;
	}



	if (target2 != NULL) {
		_RoboDK_send_Int(inst, 3);
		_RoboDK_send_Array(inst, NULL, 0);
		_RoboDK_send_Item(inst, target2);
	}
	else if (joints2 != NULL) {
		_RoboDK_send_Int(inst, 1);
		_RoboDK_send_Array(inst, joints2->_Values, joints2->_nDOFs);
		_RoboDK_send_Item(inst, NULL);
	}
	else if (mat_target2 != NULL) {// && mat_target.IsHomogeneous()) {
		_RoboDK_send_Int(inst, 2);
		_RoboDK_send_Array(inst, mat_target2->arr16, 16); // keep it as array!
		_RoboDK_send_Item(inst, NULL);
	}
	else {
		//throw new RDKException("Invalid target type"); //raise Exception('Problems running function');
		fprintf(stderr, "Invalid target type");
		return;
	}


	_RoboDK_send_Item(inst, itemrobot);
	_RoboDK_check_status(inst);
	if (isblocking) {
		Item_WaitMove(itemrobot, 300);
	}
}


