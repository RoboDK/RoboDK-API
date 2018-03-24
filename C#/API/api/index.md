RoboDK API for C#
=================

With the RoboDK API for C# it is possible to simulate and program any industrial robot using C# programming language. This avoids using vendor-specific programming languages.

Requirements
============

RoboDK must be installed:
 * RoboDK Software: https://robodk.com/

Install this nuget package (to complete)

Example
=======

The following script shows an example that uses the RoboDK package for robot simulation and offline programming::

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

The same script used for simulation can be used for offline programming, which means that the appropriate program can be generated for the robot being used. RoboDK supports a large number of robot controllers and it is easy to include compatibility for new robot controllers using Post Processors.

For more information about robot post processors:
 * https://robodk.com/help#PostProcessor
 * https://robodk.com/doc/en/Post-Processors.html
 * https://robodk.com/doc/en/PythonAPI/postprocessor.html

For more Examples:
 * https://robodk.com/doc/en/PythonAPI/examples.html

 
Other
=====

A partial implementation of the RoboDK API for Visual Basic is also available:
 * RoboDK API for VB .Net: https://robodk.com/doc/examples/RoboDK-Visual-Basic-VB.Net-SampleProject.zip

Supported robots
================

The following list includes the robot controllers supported by RoboDK:
 * ABB RAPID IRC5: for ABB IRC5 robot controllers
 * ABB RAPID S4C: for ABB S4C robot controllers
 * Adept Vplus: for Adept V+ programming language
 * Allen Bradley Logix5000: for Allen Bradley Logix5000 PCL
 * Comau C5G: for Comau C5G robot controllers
 * CLOOS: for CLOOS robot controllers
 * Denso PAC: for Denso RC7 (and older) robot controllers (PAC programming language)
 * Denso RC8: for Denso RC8 (and newer) robot controllers (PacScript programming language)
 * Dobot: for educational Dobot robots
 * Fanuc R30iA: for Fanuc R30iA and R30iB robot controllers
 * Fanuc R30iA Arc: for Fanuc Arc welding
 * Fanuc RJ3: for Fanuc RJ3 robot controllers
 * G-Code BnR: for B&R robot controllers
 * GSK: for GSK robots
 * HIWIN HRSS: for HIWIN robots
 * KAIRO: for Keba Kairo robot controllers
 * KUKA IIWA: for KUKA IIWA sunrise programming in Java
 * KUKA KRC2: for KUKA KRC2 robot controllers
 * KUKA KRC2 CamRob: for KUKA CamRob milling option
 * KUKA KRC2 DAT: for KUKA KRC2 robot controllers including DAT data files
 * KUKA KRC4: for KUKA KRC4 robot controllers
 * KUKA KRC4 Config: for KUKA KRC4 robot controllers with configuration data in each line
 * KUKA KRC4 DAT: for KUKA KRC4 robot controllers including DAT data files
 * Kawasaki: for Kawasaki AS robot controllers
 * Mecademic: for Mecademic Meca500 robot
 * Mitsubishi: for Mitsubishi robot controllers
 * Motoman: for Yaskawa/Motoman robot controllers (JBI Inform programming)
 * Nachi AX FD: for Nachi AX and FD robot controllers
 * Daihen OTC: for Daihen OTC robot controllers
 * Precise: for Precise Scara robots
 * Siemens Sinumerik: for Siemens Sinumerik ROBX robot controller
 * Staubli VAL3: for Staubli VAL3 robot programs (CS8 controllers and later)
 * Staubli VAL3 InlineMove: to generate Staubli VAL3 programs with inline movement data
 * Staubli S6: for Staubli S6 robot controllers
 * Toshiba: for Toshiba robots
 * Universal Robots: for UR robots, generates linear movements as pose targets
 * Universal Robots RobotiQ: for UR robots including support for RobotiQ gripper
 * Universal Robots joints: for UR robots, generates linear movements as joint targets
 * Yamaha: for Yamaha robots