RoboDK API for C# - Main Page
=============================

The RoboDK API for C# allows you to simulate and program robots from your C# code for robot automation project. The RoboDK API also allows you to automate tasks within RoboDK software and customize your manufacturing applications.

Learn more about the RoboDK API in the [RoboDK documentation page](https://robodk.com/doc/en/RoboDK-API.html).

Requirements
------------

 * RoboDK Software: [https://robodk.com/download](https://robodk.com/download)
 * RoboDK API for C# (GitHub): [https://github.com/RoboDK/RoboDK-API/tree/master/C%23](https://github.com/RoboDK/RoboDK-API/tree/master/C%23)
 * RoboDK API on GitHub (main page): [https://github.com/RoboDK/RoboDK-API](https://github.com/RoboDK/RoboDK-API)
 * Miscrosoft Visual Studio: [Miscrosoft Visual Studio](https://www.visualstudio.com/downloads/) (it works with the Visual Studio community version and .NET framework >= 2.0)

How to install
------------
The RoboDK API for C# can be installed and used in one of the following ways:
 * Simply include RoboDK.cs file to your project from the Example folder
 * Install the NuGet package from the API folder
The NuGet package follows the C# naming conventions and interfaces (including its own documentation) whereas the single file RoboDK.cs API follows the Python API naming.

Documentation
-------------
Depending on what version of the API you use:
 * Python-based naming in C# (single file RoboDK.cs API): https://robodk.com/doc/en/PythonAPI/robodk.html#robolink-py
 * NuGet C# Package: https://robodk.com/doc/en/CsAPI/index.html

The single file RoboDK.cs API is available as a template on [Visual Studio Marketplace](https://marketplace.visualstudio.com/items?itemName=RoboDK.RoboDK-Template)

Example
-------
The following script shows an example that uses the RoboDK package for robot simulation and offline programming:
```csharp
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

The same script used for simulation can be used for offline programming, which means that the appropriate program can be generated for the robot being used. RoboDK supports a large number of robot controllers and it is easy to include compatibility for new robot controllers using Post Processors.

For more information about robot post processors:
 * https://robodk.com/help#PostProcessor
 * https://robodk.com/doc/en/Post-Processors.html
 * https://robodk.com/doc/en/PythonAPI/postprocessor.html

For more Examples:
 * [https://robodk.com/doc/en/PythonAPI/examples.html](https://robodk.com/doc/en/PythonAPI/examples.html)
