RoboDK API for Matlab
======================

The Robolink class (Robolink.m) is the implementation of the RoboDK API for Matlab.
This class allows creating macros for RoboDK and program industrial robots offline.

The RoboDK API for Matlab is implemented with the following classes (files):
 * Robolink.m
 * RobolinkItem.m
 
Any interaction with RoboDK is made through "items" (RobolinkItem.m). An item is an object in the
Robodk tree (it can be either a robot, an object, a tool, a frame, a 
program, ...). An item is a unique number (pointer) that represents one object.

RoboDK API Help:
 * Type "doc Robolink" in Matlab for more help about the Robolink class
 * Type "doc RobolinkItem" for more help about the RobolinkItem item class
 * Type "showdemo Example_RoboDK" for examples to use RoboDK's API using the last two classes

More information:
 * RoboDK documentation: https://robodk.com/doc/en/RoboDK-API.html
 * Robolink class: https://robodk.com/doc/en/PythonAPI/robodk.html#robodk.robolink.Robolink
 * Item class: https://robodk.com/doc/en/PythonAPI/robodk.html#robodk.robolink.Item
 
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
 
 
```Matlab
clc
clear
close all

% Generate a Robolink object RDK. This object is the interface with RoboDK.
RDK = Robolink;

% Set the simulation speed. This is a ratio, for example, simulation speed
% of 5 (default) means that 1 second of simulated time corresponds to 1
% second of real time.
RDK.setSimulationSpeed(5);

% Optionally, change the run mode and generate the program (ignores simulation to 
% generate the robot program). This will generate a program file suitable for 
% your robot
% RDK.setRunMode(RDK.RUNMODE_MAKE_ROBOTPROG)
% RDK.ProgramStart('MatlabProgram');

% Retrieve the robot item from the RoboDK station
robot = RDK.Item('UR10');

% Set the robot at the home position
robot.setJoints(jhome); % Immediate move
robot.MoveJ(jhome); % Joint move

% Make sure we are using the selected tool and reference frames with the
% robot
robot.setPoseTool(tool); % Set the tool frame (as item or as pose)
robot.setPoseFrame(ref_object); % Set the reference frame (as item or pose)
robot.setSpeed(100); % Set the TCP linear speed in mm/s

% Retrieve all the reference frame dependencies (items attached to it)
ref_object_items = ref_object.Childs();

for i = 1:numel(ref_object_items)
    item_i = ref_object_items{i};
    if item_i.Type() ~= Robolink.ITEM_TYPE_TARGET
        fprintf('Skipping: %s\n', item_i.Name());
        continue
    end
    fprintf('Moving to: %s ...\n', item_i.Name());
    robot.MoveJ(item_i)
    
    % Alternatively, we can move the robot given a 4x4 pose:
%     robot.MoveL(item_i.Pose())
    
    % Alternatively, we can also move the robot given the joint values:
%     robot.MoveJ(item_i.Joints())
    
end
fprintf('Done!\n');

% Signal the end of generated program (when program generation is used it will display the file)
RDK.Finish()
```
 
Other
------
   
Read the full [RoboDK API description](../README.md) for more information

More information in [Matlab Central](https://www.mathworks.com/matlabcentral/fileexchange/65690-robodk-api-for-matlab)


