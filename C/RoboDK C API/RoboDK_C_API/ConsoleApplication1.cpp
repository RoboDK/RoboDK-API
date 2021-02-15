#include <stdio.h>

#include "robodk_api_c.h"

int main()
{
	WSADATA wsaData;
	int iResult = WSAStartup(MAKEWORD(2, 2), &wsaData);
	if (iResult != 0) {
		printf("WSAStartup failed with error: %d\n", iResult);
		return 1;}


	struct RoboDK_t rdk;
	RoboDK_Connect_default(&rdk);
	RoboDK_ShowMessage(&rdk, "Hello world!\nLine 2", false);

	printf("Address of rdk %p\n ", &rdk);

	if (!_RoboDK_connected(&rdk)) {
		fprintf(stderr, "Failed to start RoboDK API!!");
		return -1;
	}

	char bufferOut[1024];


	struct Item_t robotItem = RoboDK_getItem(&rdk, "", (enum eITEM_TYPE)ITEM_TYPE_ROBOT);
	
	
	if (!Item_Valid(&robotItem)) {
		printf("No Robot Selected");
		return -1;
	}






	if (Item_Valid(&robotItem)) {
		Item_Name(&robotItem, bufferOut);
		printf("Robot Name: %s\n", bufferOut);



		struct Mat_t pose1 = Item_Pose(&robotItem);
		Mat_ToString(&pose1, bufferOut, false);
		printf("Matrix values retrieved:\n%s", bufferOut);

		struct Mat_t pose2 = Mat_makeCopy(&pose1);

		struct Joints_t curJoints = Item_Joints(&robotItem);
		Joints_ToString(&curJoints, bufferOut);
		printf(bufferOut);

	

		struct Joints_t jointsfrIK = Item_SolveIK(&robotItem, &pose1, nullptr, nullptr);
		Joints_ToString(&jointsfrIK, bufferOut);
		printf("Inverse Kinematics:\n%s", bufferOut);
	}


}