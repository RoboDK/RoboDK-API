RoboDK API for C#
======================
Read the [RoboDK API description](../README.md) for information about the RoboDK API.

Full description and template available on [Visual Studio Marketplace](https://marketplace.visualstudio.com/items?itemName=RoboDK.RoboDK-Template)

Requirements
------------
- [Visual Studio](https://www.visualstudio.com/downloads/) (it works with the Visual Studio community version and .NET framework >= 2.0)
- [RoboDK](https://robodk.com/download)

How to install
------------
Simply include RoboDK.cs file to your project

C# Example
------------
```csharp
// RDK holds the main object to interact with RoboDK.
// RoboDK starts when a RoboDK object is created.
RoboDK RDK = new RoboDK();

// Select the robot among all available robots (there is no popup if there is only 1 robot)
RoboDK.Item ROBOT = RDK.ItemUserPick("Select a robot", RoboDK.ITEM_TYPE_ROBOT);

// retrieve the reference frame and the tool frame (TCP) as poses
Mat frame = ROBOT.PoseFrame();
Mat tool = ROBOT.PoseTool();

// Optional: set the run mode (define if you want to simulate, generate the program or run the program on the robot)
// RDK.setRunMode(RoboDK.RUNMODE_MAKE_ROBOTPROG)
// RDK.ProgramStart("MatlabTest");

// Program start
ROBOT.MoveJ(pose_ref);
ROBOT.setPoseFrame(frame);  // set the reference frame
ROBOT.setPoseTool(tool);    // set the tool frame: important for Online Programming
ROBOT.setSpeed(100);        // Set Speed to 100 mm/s
ROBOT.setZoneData(5);       // set the rounding instruction 
                            // (C_DIS & APO_DIS / CNT / ZoneData / Blend Radius / ...)
ROBOT.RunCodeCustom("CallOnStart");
for (int i = 0; i <= n_sides; i++)
{
    double angle = ((double) i / n_sides) * 2.0 * Math.PI;
    Mat pose_i = pose_ref * Mat.rotz(angle) * Mat.transl(100, 0, 0) * Mat.rotz(-angle);
    ROBOT.RunCodeCustom("Moving to point " + i.ToString(), RoboDK.INSTRUCTION_COMMENT);
    double[] xyzwpr = pose_i.ToXYZRPW();
    ROBOT.MoveL(pose_i);
}
ROBOT.RunCodeCustom("CallOnFinish");
ROBOT.MoveL(pose_ref);
```
