RoboDK API for Matlab
======================

The Robolink class (Robolink.m) is the implementation of the RoboDK API for Matlab.
This class allows creating macros for RoboDK and program industrial robots offline.

Any interaction with RoboDK is made through "items" (RobolinkItem.m). An item is an object in the
Robodk tree (it can be either a robot, an object, a tool, a frame, a 
program, ...). An item is a unique number (pointer) that represents one object.

The RoboDK API for Matlab is implemented with the following classes (files):
 * Robolink.m
 * RobolinkItem.m

RoboDK API Help:
 * Type "doc Robolink" in Matlab for more help about the Robolink class
 * Type "doc RobolinkItem" for more help about the RobolinkItem item class
 * Type "showdemo Example_RoboDK" for examples to use RoboDK's API using the last two classes

More information:
 * RoboDK documentation: https://robodk.com/doc/en/RoboDK-API.html
 * Robolink class: https://robodk.com/doc/en/PythonAPI/robolink.html#robolink.Robolink
 * Item class: https://robodk.com/doc/en/PythonAPI/robolink.html#robolink.Item
 
Requirements
------------
- [Matlab](https://www.mathworks.com/products/matlab.html)
- [RoboDK](https://robodk.com/download)

No specific toolbox is required for Matlab 2014b or later. 
For Matlab versions prior to 2014b it is required to have the Instrument Control Toolbox (use the Robolink.m file in the Robolink-ICT-tcpip folder).


Examples
------------

Run one of the Example files to see some examples to use the API. Such as:
 * Example_RoboDK.m

The following files are used by the Simulink model:
 * RoboDK_Sample.mdl
 * RoboDK_getRobot.m
 * RoboDK_Pose2Joints.m
 * RoboDK_ShowPose.mdl
 
 
Other
------
    
Read the full [RoboDK API description](../README.md) for more information

More information in [Matlab Central](https://www.mathworks.com/matlabcentral/fileexchange/65690-robodk-api-for-matlab)


