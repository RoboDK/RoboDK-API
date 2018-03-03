The Robolink class is an implementation of the RoboDK API for Matlab.
This class allows creating macros for RoboDK and program industrial
robots offline.

Any interaction is made through "items". An item is an object in the
Robodk tree (it can be either a robot, an object, a tool, a frame, a 
program, ...).
An item is a unique number (pointer) that represents one object.

The RoboDK API for Matlab is implemented with the following classes (files):
    Robolink.m
    RobolinkItem.m

RoboDK API Help:
->Type "doc Robolink"            for more help on the Robolink class
->Type "doc RobolinkItem"        for more help on the RobolinkItem item class
->Type "showdemo Example_RoboDK" for examples on how to use RoboDK's API using the last two classes

More information:
    RoboDK documentation: https://robodk.com/doc/en/RoboDK-API.html
    Robolink class: https://robodk.com/doc/en/PythonAPI/robolink.html#robolink.Robolink
    Item class: https://robodk.com/doc/en/PythonAPI/robolink.html#robolink.Item

--------------------------------------------------------------------------------
The following files are used by the Simulink model:
    RoboDK_Sample.mdl
    RoboDK_getRobot.m
    RoboDK_Pose2Joints.m
    RoboDK_ShowPose.mdl
    
Run one of the Example files to see some examples to use the API. Such as:
    Example_RoboDK.m

The RoboDK API is also available for Python, C# and VB.

Note for versions prior to Matlab 2014b:
Use the Robolink.m file in the Robolink-ICT-tcpip.zip folder.
This requires the Instrument Control Toolbox.


