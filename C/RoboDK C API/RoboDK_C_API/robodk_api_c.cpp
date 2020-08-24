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

void Item_MoveJ_joints(struct Item_t *inst, struct Joints_t *joints, bool isBlocking) {
	_RoboDK_moveX(inst->_RDK, NULL, joints, NULL, inst, 1, isBlocking);
}

void Item_MoveJ_mat(struct Item_t *inst, struct Mat_t *targetPose, bool isBlocking) {
	_RoboDK_moveX(inst->_RDK, NULL, NULL, targetPose, inst, 1, isBlocking);

}

void Item_WaitMove(const struct Item_t *inst, double timeout_sec) {
	_RoboDK_check_connection(inst->_RDK);
	_RoboDK_send_Line(inst->_RDK, "WaitMove");
	_RoboDK_send_Item(inst->_RDK, inst);
	_RoboDK_check_status(inst->_RDK);
	inst->_RDK->_TIMEOUT = (int)(timeout_sec * 1000.0);
	_RoboDK_check_status(inst->_RDK); //Will wait heres
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
		w = atan2(-inst->arr16[6], inst->arr16[5]);
	}
	else if (inst->arr16[2] < -1.0 + 1e-6) {
		p = 0.5*M_PI;
		r = 0;
		w = atan2(inst->arr16[9], inst->arr16[5]);
	}
	else {
		p = atan2(-inst->arr16[2], sqrt(inst->arr16[0] * inst->arr16[0] + inst->arr16[1] * inst->arr16[1]));
		w = atan2(inst->arr16[1], inst->arr16[0]);
		r = atan2(inst->arr16[6], inst->arr16[8]);
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
	for (int i = 1; i < inst->_nDOFs; i++) {
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


int32_t _RoboDK_recv_Int(struct RoboDK_t *inst) {
	int32_t value = -1; // do not change type
	int i;
	if (inst->_isConnected == false) { return false; }
	if (socketBytesAvailable(inst->_COM) <= sizeof(int32_t)) {
		char buffer[sizeof(int32_t)];
		int bytesReceived = socketRead(inst->_COM, buffer, sizeof(int32_t));
		if (bytesReceived <= 0) {
			return -1;
		}
		for (i = 0; i < 4; i++) {
			value = buffer[i] << (24 - i * 8);
		}
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
	if (socketBytesAvailable(inst->_COM) <= size) {
		char bufferBytes[16 * sizeof(double)];
		socketRead(inst->_COM, bufferBytes, 16 * sizeof(double));
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
	if (socketBytesAvailable(inst->_COM) <= (size + 4)) {
		double valuei;
		for (int i = 0; i < nvalues; i++) {
			char bufferCurValue[sizeof(double)];
			char valueIBytes[sizeof(double)];
			socketRead(inst->_COM, &bufferCurValue, sizeof(double));
			for (int k = 0; k < sizeof(double); k++) {
				valueIBytes[sizeof(double) - 1 - k] = bufferCurValue[k];
			}
			memcpy(&valuei, &valueIBytes, sizeof(double));
			pValues[i] = valuei;
		}
	}
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


void _RoboDK_moveX(struct RoboDK_t *inst, const struct Item_t *target, const struct Joints_t *joints, const struct Mat_t *mat_target, const struct Item_t *itemrobot, int movetype, bool blocking) {
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