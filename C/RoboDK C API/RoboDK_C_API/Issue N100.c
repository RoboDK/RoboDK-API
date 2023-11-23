#include "robodk_api_c.h"

typedef enum BinaryLogicValuesEnum {
    NO,
    YES
} logic_e;

typedef struct azimuth_t { //!< Structure defining an azimuthal orientation in two angles (α, ι).
    double alpha; //!< Azimuth angle (from X axis, CCW).
    double iota; //!< Zenith angle
} azimuth_t;

typedef struct RobotArmControllerType {
    WSADATA wsaData; //!< Winsocket data.
    logic_e socketOpen; //!< Communication sockets to the RoboDK library open.
    logic_e conn; //!< Robot controller connected [NO | YES]
    logic_e present; //!< Robot controller presence status [NO | YES]
    enum eRobotRunMode runMode; //!< RoboDK running mode [SIMULATION | RUN_ROBOT]
    logic_e running; //!< Controller is running RAPID code
    char DIval; //!< Digital Input line value
} robCtrlr_t;

typedef struct RobotArmToolType { //!< For a robot-held tool, describes the tool load
    struct Item_t item; //!< RoboDK probe's item instance.
    char name[64]; //!< RoboDK probe's name.
    struct Mat_t pose; //!< RoboDK probe's current pose in 3D space in the BCS.
    struct XYZWPR_t ABBpose; //!< Probe's pose according to ABB reference definitions.
    azimuth_t oriAzim; //!< Probe's orientation in azimuthal coordinates (alpha, iota) above the reference point.
    struct Mat_t tcp; //!< Tool TCP's pose in the wrist coordinates' system (centre of the mounting flange on axis 6)
    struct XYZWPR_t ABBtcp; //!< Tool TCP's pose in the wrist coordinates' system (centre of the mounting flange on axis 6) according to ABB reference definitions
    struct Mat_t target; //!< RoboDK target pose (to be reached) in the "Home" reference frame.
    struct XYZWPR_t ABBtarget; //!< Target pose according to ABB reference definitions.
    azimuth_t targetAzim; //!< Target orientation in azimuthal coordinates (alpha, iota) above the reference point.
    struct Mat_t filTarget; //!< RoboDK target pose filtered.
    struct Mat_t transform; //!< Transformation matrix to go from target to filtered target.
    double jogStep; //< Step (mm or °) to be used for jogging motions
    double refDist; //< Probe measurement distance (121.22 mm)
    double offset; //< Probe measurement offset (distance from the fiber exit to the robot arm Y axis)
} robTool_t;

typedef struct RobotArmType {
    robCtrlr_t ctrl; //!< Robot arm controller
    struct RoboDK_t rdk; //!< RoboDK-controlled robot arm.
    struct Item_t robot; //!< RoboDK robot item.
    char name[64]; //!< Controller name
    robTool_t probe; //!< Description of the probe mounted at the robot arm wrist.
    struct Item_t ocs; //!< RoboDK Object Coordinates System reference. Used to manipulate the inspected tile.
    struct Mat_t refFrame; //!< RoboDK reference frame pose for the probe.
    struct XYZWPR_t ABBrefFrame; //!< RoboDK reference frame expressed in the ABB-style 6 coordinates.
    logic_e moving; //!< "Arm is moving" status
} robotArm_t;

typedef enum RobotArmJog_Enum { //!< Enumeration type defining the different jogging movements
    ARM_JOG_PSI = -6,
    ARM_JOG_THETA,
    ARM_JOG_PHI,
    ARM_JOG_Z,
    ARM_JOG_Y,
    ARM_JOG_X,
    ARM_JOGX = 1,
    ARM_JOGY,
    ARM_JOGZ,
    ARM_JOGPHI,
    ARM_JOGTHETA,
    ARM_JOGPSI
} armJog_e;

char svcBuffer[BUFSIZ]; //!< Char buffer used to prepare strings

#define SIGN(A)             (((A) < 0) ? -1 : (((A) > 0) ? 1 : 0))

enum RobotArm_Enum {
    ARM_X,
    ARM_Y,
    ARM_Z,
    ARM_PSI,
    ARM_THETA,
    ARM_PHI
};

void armGetABBpose(const struct Mat_t* pose, struct XYZWPR_t* ABBpose) {
    sprintf(svcBuffer, "Pose in the current reference frame:");
    // LOG_UPDATE(svcBuffer, 1);
    Mat_ToString(pose, svcBuffer, true);
    sscanf(svcBuffer, "Mat(XYZRPW_2_Mat(%lf,%lf,%lf,%lf,%lf,%lf))", &ABBpose->arr6[ARM_X], &ABBpose->arr6[ARM_Y], &ABBpose->arr6[ARM_Z], &ABBpose->arr6[ARM_PSI], &ABBpose->arr6[ARM_THETA], &ABBpose->arr6[ARM_PHI]);
    sprintf(svcBuffer, "%.2lf, %.2lf, %.2lf, %.2lf, %.2lf, %.2lf", ABBpose->arr6[ARM_X], ABBpose->arr6[ARM_Y], ABBpose->arr6[ARM_Z], ABBpose->arr6[ARM_PSI], ABBpose->arr6[ARM_THETA], ABBpose->arr6[ARM_PHI]);
    // LOG_UPDATE(svcBuffer, 5);
}

int armMove(robotArm_t* arm) {
    //errReset();

    while (Item_Busy(&arm->robot)) {    // Do NOT operate while robot is busy
        // LOG_UPDATE("Robot arm BUSY!", 1);
    };
    // LOG_UPDATE("Moving probe to pose:", 1);
    sprintf(svcBuffer, "%.2lf, %.2lf, %.2lf, %.2lf, %.2lf, %.2lf", arm->probe.ABBtarget.arr6[ARM_X], arm->probe.ABBtarget.arr6[ARM_Y], arm->probe.ABBtarget.arr6[ARM_Z], arm->probe.ABBtarget.arr6[ARM_PSI], arm->probe.ABBtarget.arr6[ARM_THETA], arm->probe.ABBtarget.arr6[ARM_PHI]);
    // LOG_UPDATE(svcBuffer, 5);
    Mat_SetPose_KUKA(&arm->probe.target, arm->probe.ABBtarget);
    Item_MoveL_mat(&arm->robot, &arm->probe.target, true);
    Mat_Inv_out(&arm->probe.transform, &arm->probe.target);
    Mat_Multiply_cumul(&arm->probe.transform, &arm->probe.target);
    //armGetPose(arm);
    return 0; // (errNum());
}

int armJog(robotArm_t* arm, armJog_e motion) {
    arm->probe.target = Mat_makeCopy(&arm->probe.pose);
    armGetABBpose(&arm->probe.target, &arm->probe.ABBtarget);
    arm->probe.ABBtarget.arr6[abs(motion) - 1] += (SIGN(motion) * arm->probe.jogStep);
    Mat_SetPose_KUKA(&arm->probe.target, arm->probe.ABBtarget);

    return (armMove(arm));
}

int main() {
    WSADATA wsaData;
    int iResult = WSAStartup(MAKEWORD(2, 2), &wsaData);
    if (iResult != 0) {
        printf("WSAStartup failed with error: %d\n", iResult);
        return 1;
    }

    robotArm_t arm;
    memset(&arm, 0, sizeof(arm));

    arm.probe.jogStep = 100.0;

    RoboDK_Connect_default(&arm.rdk);

    if (!_RoboDK_connected(&arm.rdk)) {
        printf("Failed to start RoboDK API!!\n");
        return -1;
    }

    int32_t count = 0;
    RoboDK_getItemListFilter(&arm.rdk, ITEM_TYPE_ROBOT, &arm.robot, 1, &count);
    if (count < 1) {
        printf("There's no robot in the station\n");
        return -1;
    }

    char robotName[MAX_STR_LENGTH];
    memset(robotName, 0, sizeof(robotName));
    Item_Name(&arm.robot, robotName);
    printf("Found: %s\n", robotName);

    armJog(&arm, ARM_JOGX);

    return 0;
}