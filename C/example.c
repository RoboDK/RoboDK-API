#include <stdio.h>

#include "robodk_api_c.h"

int main()
{
    //The RoboDK_t structures store the socket and parameters passed to robodk
    //This structure's pointer must remain valid as long as you are using the api,
    //all the api items  it's used to create keep a copy of it's location.
    struct RoboDK_t rdk;
    //RoboDK_Connect(&rdk, "", 0, "-SKIPMAINT", "");
    RoboDK_Connect_default(&rdk);

    if (!_RoboDK_connected(&rdk)) {
        fprintf(stderr, "Failed to start RoboDK API!!\n");
        return -1;
    }


    // Test retrieving all items at once
    #define MAX_ITEMS 1000
    struct Item_t itemlist[MAX_ITEMS];
    int size_out = 0;
    RoboDK_getItemList(&rdk, itemlist, MAX_ITEMS, &size_out);
    //RoboDK_getItemListFilter(&rdk, ITEM_TYPE_ROBOT, itemlist, MAX_ITEMS, &size_out);
    if (size_out > MAX_ITEMS){
        fprintf(stderr, "Warning! Max size item size exceeded\n");
    }

    if (size_out > MAX_ITEMS)
        size_out = MAX_ITEMS;

    printf("Items in the station: %i\n", size_out);
    for (int i=0; i<size_out; i++){
        char item_name[MAX_STR_LENGTH];
        Item_Name(&itemlist[i], item_name);
        printf("  %i -> %llu, %s\n", i, itemlist[i]._PTR, item_name);
    }
    return 0;

    // Test collision line:
    double p1XYZ[3] = {1,0,-1000};
    double p2XYZ[3] = {1,0,2000};
    double xyz_col[3] = {0,0,0};
    struct Item_t item;
    bool collided = RoboDK_Collision_Line(&rdk, p1XYZ, p2XYZ, 0, &item, xyz_col);
    return 0;


    // To prevent memory allocation issues, keep your string MAX_STR_LENGTH long
    char robotName[MAX_STR_LENGTH];
    char bufferOut[MAX_STR_LENGTH];
    struct Item_t robotItem = RoboDK_getItem(&rdk, "", (enum eITEM_TYPE)ITEM_TYPE_ROBOT);
    if (!Item_Valid(&robotItem)) {
        printf("Currently open station has no robots\n");
        return -1;
    }

    // Retrieve the item/robot name and print current joints
    Item_Name(&robotItem, robotName);
    printf("Selected robot: \n%s\n\n", robotName);

    printf("Current robot joints: \n");
    struct Joints_t joints = Item_Joints(&robotItem);
    for (int i=0;i<joints._nDOFs; i++){
        printf("J%i = %.3f deg\n", i+1, joints._Values[i]);
    }

    struct Item_t t1Item = RoboDK_getItem(&rdk, "T1", (enum eITEM_TYPE)ITEM_TYPE_TARGET);
    struct Item_t t2Item = RoboDK_getItem(&rdk, "T2", (enum eITEM_TYPE)ITEM_TYPE_TARGET);

    struct Mat_t t1_pose = Item_Pose(&t1Item);
    struct Mat_t t2_pose = Item_Pose(&t2Item);


    printf("Moving...\n");
    Item_MoveL_mat(&robotItem, &t1_pose, true);
    Item_MoveL_mat(&robotItem, &t2_pose, true);
    printf("Done\n");


    return 0;

    //Demo for target filtering
    struct Mat_t pose_tcp;
    Mat_SetPose_KUKA(&pose_tcp, XYZWPR_Create(0, 0, 200, 0, 0, 0));

    struct Mat_t pose_ref;
    Mat_SetPose_KUKA(&pose_ref, XYZWPR_Create(400, 0, 0, 0, 0, 0));

    //Update the robot TCP and reference frame
    Item_SetPoseTool(&robotItem, pose_tcp);
    Item_SetPoseFrame(&robotItem, pose_ref);
    Item_SetAccuracyActive(&robotItem, false);

    //Define a nominal target in the joint space:
    const double jointsDouble[] = { 0, 0, 90, 0, 90, 0 };
    //struct Joints_t joints;
    Joints_SetValues(&joints, jointsDouble, sizeof(jointsDouble) / sizeof(double));

    struct Mat_t pose_robot = Item_SolveFK(&robotItem, &joints, NULL, NULL);

    //Calculate pose_target: the TCP with respect to the reference frame
    struct Mat_t pose_target;
    struct Mat_t pose_ref_inverted;
    Mat_Inv_out(&pose_ref_inverted, &pose_ref);
    Mat_Multiply_out(&pose_target, &pose_ref_inverted, &pose_robot);
    Mat_Multiply_cumul(&pose_target, &pose_tcp);

    printf("Target not filtered:\n");
    Mat_ToString(&pose_target, bufferOut, true);
    fputs(bufferOut, stdout);
    Joints_ToString(&joints, bufferOut);
    fputs(bufferOut, stdout);

    //joints_approx must be within 20 deg
    struct Joints_t joints_approx = joints;

    struct Mat_t pose_target_filt;
    struct Joints_t joints_filtered;
    Item_FilterTarget(&robotItem, &pose_target, &joints_approx, &pose_target_filt, &joints_filtered);

    printf("Target filtered:\n");
    Mat_ToString(&pose_target_filt, bufferOut, true);
    fputs(bufferOut, stdout);
    Joints_ToString(&joints_filtered, bufferOut);
    fputs(bufferOut, stdout);


    return 0;

    // Demo Connect to real robot
    if (false) {
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
        fputs(bufferOut, stdout);

        struct Joints_t targetJoints = Joints_create(6);
        for (int i = 0; i < 6; i++) {
            targetJoints._Values[i] = i * 10;
        }

        printf("Moving to simulation robot to joint position\n");
        Item_MoveJ_joints(&robotItem, &targetJoints, true);
        printf("Moving to simulation robot to Start position\n");
        Item_MoveJ_mat(&robotItem, &poseStart, true);

        if (Item_Connect(&robotItem, ""))
        {
            // Set simulation mode
            RoboDK_SetRunMode(&rdk, RUNMODE_RUN_ROBOT);
            printf("Warning future moves will operate on the real robot!\n");
        }
        else
        {
            printf("Could not connect to real robot, running in simulation mode.\n");
            RoboDK_SetRunMode(&rdk, RUNMODE_SIMULATE);
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
    }

    printf("Done");

}
