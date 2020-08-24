#include <stdio.h>

#include "robodk_api_c.h"

int main()
{
	WSADATA wsaData;
	int iResult = WSAStartup(MAKEWORD(2, 2), &wsaData);
	if (iResult != 0) {
		printf("WSAStartup failed with error: %d\n", iResult);
		return 1;
	}

	//The RoboDK_t structures store the socket and parameters passed to robodk
	//This structure's pointer must remain valid as long as you are using the api,
	//all the api items  it's used to create keep a copy of it's location.
	struct RoboDK_t rdk;
	RoboDK_Connect_default(&rdk);

	if (!_RoboDK_connected(&rdk)) {
		fprintf(stderr, "Failed to start RoboDK API!!");
		return -1;
	}
	char bufferOut[1024];

	RoboDK_ShowMessage(&rdk, "Hello world!\nLine 2", false);
	struct Item_t robotItem = RoboDK_getItem(&rdk, "", (enum eITEM_TYPE)ITEM_TYPE_ROBOT);
	if (!Item_Valid(&robotItem)) {
		printf("Currently open station has no robots\n");
		return -1;
	}
	Item_Name(&robotItem, bufferOut);
	printf("Robot Name: %s\n", bufferOut);
	struct Mat_t poseStart = Item_Pose(&robotItem);
	Mat_ToString(&poseStart, bufferOut, false);
	printf("Matrix values retrieved:\n%s", bufferOut);

	//Matrix value 500 x offset
	struct Mat_t poseTranslated = Mat_makeCopy(&poseStart);
	struct Mat_t poseTransform = Mat_transl(500, 0, 0);
	Mat_Multiply_cumul(&poseTranslated, &poseTransform);
	Mat_ToString(&poseTranslated, bufferOut, false);
	printf("Matrix values translated by 500 in the x:\n%s", bufferOut);

	struct Mat_t poseTransformed = Mat_makeCopy(&poseStart);
	Mat_Multiply_rotxyz(&poseTransformed, 0, 0, 0);
	Mat_Multiply_cumul(&poseTransformed, &poseStart);
	Mat_ToString(&poseTransformed, bufferOut, false);
	printf("Matrix values transformed by 500 in the x:\n%s", bufferOut);

	printf("\n");
	struct Joints_t curJoints = Item_Joints(&robotItem);
	Joints_ToString(&curJoints, bufferOut);
	printf(bufferOut);

	struct Joints_t targetJoints = Joints_create(6);
	for (int i = 0; i < 6; i++) {
		targetJoints._Values[i] = i * 10;
	}
	printf("Moving to joint position\n");
	Item_MoveJ_joints(&robotItem, &targetJoints, true);
	printf("Moving to Start position\n");
	Item_MoveJ_mat(&robotItem, &poseStart, true);

	// Connect to real robot
	if (Item_Connect(&robotItem,""))
	{
		// Set simulation mode
		RoboDK_setRunMode(&rdk,RUNMODE_RUN_ROBOT);
		printf("Warning future moves will operate on the real robot!\n");
	}
	else
	{
		printf("Could not connect to real robot, running in simulation mode.\n");
		RoboDK_setRunMode(&rdk, RUNMODE_SIMULATE);
	}

	printf("Input e to exit, any other character causes a random movement\n");
	while (getchar() != 'e') {
		int offSetX = rand() % 150 - 75;
		int offSetY = rand() % 150 - 75;
		int offSetZ = rand() % 150 - 75;
		poseTranslated = Mat_makeCopy(&poseStart);
		poseTransform = Mat_transl(offSetX, offSetY, offSetZ);
		Mat_Multiply_cumul(&poseTranslated, &poseTransform);
		Mat_ToString(&poseTranslated, bufferOut, true);
		printf("Moving to the following position:\n%s", bufferOut);
		Item_MoveJ_mat(&robotItem, &poseTranslated, true);
		ThreadSleep(100);
		while (getchar() != '\n') {};
	}

	printf("Restoring robot to Start position\n");
	Item_MoveJ_mat(&robotItem, &poseStart, true);


	printf("Done");

}
