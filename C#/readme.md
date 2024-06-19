RoboDK API for C#
======================
The RoboDK API for C# allows you to simulate and program robots from your C# code for robot automation project. The RoboDK API also allows you to automate tasks within RoboDK software and customize your manufacturing applications.

Learn more about the RoboDK API in the [RoboDK documentation page](https://robodk.com/doc/en/RoboDK-API.html).

Requirements
------------
- [Visual Studio](https://www.visualstudio.com/downloads/) (it works with the Visual Studio community version and .NET framework >= 2.0)
- [RoboDK](https://robodk.com/download)

How to install
------------
The RoboDK API for C# can be installed and used in one of the following ways:
- Simply include RoboDK.cs file to your project from the Example folder
- Install the NuGet package from the API folder
The NuGet package follows the C# naming conventions and interfaces (including its own documentation) whereas the single file RoboDK.cs API follows the Python API naming.

Documentation
-------------
Depending on what version of the API you use:
- Python-based naming in C# (single file RoboDK.cs API): https://robodk.com/doc/en/PythonAPI/robodk.html#robolink-py
- NuGet C# Package: https://robodk.com/doc/en/CsAPI/index.html

The single file RoboDK.cs API is available as a template on [Visual Studio Marketplace](https://marketplace.visualstudio.com/items?itemName=RoboDK.RoboDK-Template)

Video Overview
--------------
<a href="http://www.youtube.com/watch?feature=player_embedded&v=3I6OK1Kd2Eo " target="_blank"><img src="http://img.youtube.com/vi/3I6OK1Kd2Eo/0.jpg" alt="Robot programming using the RoboDK API for C#" width="360" height="240" border="10" /></a>

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

/// Optional: set the run mode 
/// (define if you want to simulate, generate the program or run the program on the robot)
// RDK.setRunMode(RoboDK.RUNMODE_MAKE_ROBOTPROG)
// RDK.ProgramStart("MatlabTest");

// Program start
ROBOT.MoveJ(pose_ref);
ROBOT.setPoseFrame(frame);  // set the reference frame
ROBOT.setPoseTool(tool);    // set the tool frame: important for Online Programming
ROBOT.setSpeed(100);        // Set Speed to 100 mm/s
ROBOT.setZoneData(5);       // set the rounding instruction 
                            // (C_DIS & APO_DIS / CNT / ZoneData / Blend Radius / ...)
ROBOT.RunInstruction("CallOnStart");
for (int i = 0; i <= n_sides; i++)
{
    double angle = ((double) i / n_sides) * 2.0 * Math.PI;
    Mat pose_i = pose_ref * Mat.rotz(angle) * Mat.transl(100, 0, 0) * Mat.rotz(-angle);
    ROBOT.RunInstruction("Moving to point " + i.ToString(), RoboDK.INSTRUCTION_COMMENT);
    double[] xyzwpr = pose_i.ToXYZRPW();
    ROBOT.MoveL(pose_i);
}
ROBOT.RunInstruction("CallOnFinish");
ROBOT.MoveL(pose_ref);
```
