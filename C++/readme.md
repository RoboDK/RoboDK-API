RoboDK API for C++
======================

Read the [RoboDK API description](../README.md) for more information.

Requirements
------------
- [Qt](https://www.qt.io/download) Open Source or Commercial
- [RoboDK](https://robodk.com/download)

How to install
------------
Just include the robodk_api.h and robodk_api.cpp files to your project.

C++ Example
------------

The Mat class represents a 4x4 matrix (pose) and it is a subclass of QMatrix4x4

```cpp
#include "robodk_api.h"

// TIP: use #define RDK_SKIP_NAMESPACE to avoid using namespaces
using namespace RoboDK_API;

RoboDK *RDK = NULL;  // RDK is the interface with RoboDK
Item *ROBOT = NULL;  // ROBOT is the robot item

/// Start the RoboDK API
void RoboDK_Start(){
    // RoboDK starts when a RoboDK object is created.
    RDK = new RoboDK();    
    
    // Retrieve the robot
    ROBOT = new Item(RDK->getItem("Motoman SV3"));
}

/// Delete RDK and ROBOT objects
void RoboDK_Finish(){
    delete RDK;
    delete ROBOT;
}

void RoboDK_Test(){
    // Start RoboDK
    RoboDK_Start();
    
    if (ROBOT == NULL || !ROBOT->Valid()){
        // Something is wrong!
        return;
    }

    // Draw a hexagon inside a circle of radius 100.0 mm
    int n_sides = 6;
    float size = 100.0;

    // retrieve the reference frame and the tool frame (TCP)
    Mat pose_frame = ROBOT->PoseFrame();
    Mat pose_tool = ROBOT->PoseTool();

    // retrieve the pose of the TCP with respect to the reference frame
    Mat pose_ref = ROBOT->Pose();

    // Optional: set the run mode (define if you want to simulate, 
    // generate the program or run the program on the robot)
    // RDK->setRunMode(RoboDK::RUNMODE_MAKE_ROBOTPROG)
    // RDK->ProgramStart('MatlabTest');

    // Program start
    ROBOT->MoveJ(pose_ref);
    ROBOT->setPoseFrame(pose_frame);  // set the reference frame
    ROBOT->setPoseTool(pose_tool);    // set the tool frame: important for Online Programming
    ROBOT->setSpeed(100);             // Set Speed to 100 mm/s
    ROBOT->setRounding(5);            // set the rounding instruction 
                                      //(C_DIS & APO_DIS / CNT / ZoneData / Blend Radius / ...)
    ROBOT->RunCodeCustom("CallOnStart"); // run a program
    for (int i = 0; i <= n_sides; i++) {
        // calculate angle in degrees:
        double angle = ((double) i / n_sides) * 360.0;

        // create a pose relative to the pose_ref
        Mat pose_i(pose_ref);
        pose_i.rotate(angle,0,0,1.0);
        pose_i.translate(size, 0, 0);
        pose_i.rotate(-angle,0,0,1.0);

        // add a comment (when generating code)
        ROBOT->RunCodeCustom("Moving to point " + QString::number(i), RoboDK::INSTRUCTION_COMMENT);

        // example to retrieve the pose as Euler angles (X,Y,Z,W,P,R)
        double xyzwpr[6];
        pose_i.ToXYZRPW(xyzwpr);

        ROBOT->MoveL(pose_i);  // move the robot
    }
    ROBOT->RunCodeCustom("CallOnFinish");
    ROBOT->MoveL(pose_ref);     // move back to the reference point
    
    // Delete allocated items
    RoboDK_Finish();
}
```
