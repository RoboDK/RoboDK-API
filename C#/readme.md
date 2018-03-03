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

Python Example
------------
```c#
// retrieve the reference frame and the tool frame (TCP)
Mat frame = ROBOT.PoseFrame();
Mat tool = ROBOT.PoseTool();
int runmode = RDK.RunMode(); // retrieve the run mode 

// Program start
ROBOT.MoveJ(pose_ref);
ROBOT.setPoseFrame(frame);  // set the reference frame
ROBOT.setPoseTool(tool);    // set the tool frame: important for Online Programming
ROBOT.setSpeed(100);        // Set Speed to 100 mm/s
ROBOT.setZoneData(5);       // set the rounding instruction (C_DIS & APO_DIS / CNT / ZoneData / Blend Radius / ...)
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
