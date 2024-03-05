RoboDK API for MATLAB
======================

MATLAB is a proprietary programming language developed by [MathWorks](https://www.mathworks.com/). Among other things, MATLAB allows matrix manipulations, plotting of functions and data and implementation of algorithms. RoboDK is an official [MathWorks Connections Program Partner](https://www.mathworks.com/products/connections/product_detail/robodk.html).

The [RoboDK API description](https://robodk.com/doc/en/RoboDK-API.html) explains the advantages of using the RoboDK API with a widely used programming language such as MATLAB for robot programming.

The RoboDK API for MATLAB is provided as a group of script files (m-files), available here:
* In the installation folder of RoboDK, typically `C:/RoboDK/Matlab/`
* On MathWorks [MATLAB Central](https://www.mathworks.com/matlabcentral/fileexchange/65690-robodk-api-for-matlab)
* On the RoboDK API [GitHub](https://github.com/RoboDK/RoboDK-API/tree/master/Matlab)

The RoboDK API for MATLAB includes:
* `Robolink.m` is a class that interfaces with RoboDK. Any object in the RoboDK Station Tree can be retrieved using the Robolink object and it is represented by the RobolinkItem object (same as Python’s [Robolink](https://robodk.com/doc/en/PythonAPI/robodk.html#robodk.robolink.Robolink) class).
* `RobolinkItem.m` is a class that represents a RoboDK item in the Station Tree. It is possible to perform different operations on that item (same as Python’s [Item](https://robodk.com/doc/en/PythonAPI/robodk.html#robodk.robolink.Item) class).
* `transl.m`, `rotx.m`, `roty.m` and `rotz.m` are functions that create pose matrices given an XYZ translation vector or rotations along a specific axis.
* `Pose_2_XYZRPW.m` and `XYZRPW_2_Pose.m` allow converting poses to XYZ position and RPW Euler angles and vice versa.

The following page presents multiple examples of the RoboDK MATLAB API, such as manipulating items, generating robot programs and controlling the robot:
* RoboDK MATLAB example: https://robodk.com/Matlab-API.

Additional Resources:
* For detailed documentation on the Robolink class, type "`doc Robolink`" in the MATLAB Command Window.
* For information on the RobolinkItem class, type "`doc RobolinkItem`".
* To view more examples demonstrating the use of the RoboDK API, type "`showdemo Example_RoboDK`".
* For the RoboDK MATLAB API documentation, visit: https://robodk.com/doc/en/RoboDK-API.html#MatlabAPI.


Simulink
-----------------
A Simulink project is available as an example. In the simulation, the robot is moved along a set of XYZ coordinates generated arbitrarily.
[![RoboDK Simulink](https://img.youtube.com/vi/7DDBMwa0-Oc/0.jpg)](https://www.youtube.com/watch?v=7DDBMwa0-Oc)


Requirements
------------
- [MATLAB](https://www.mathworks.com/products/matlab.html)
- [RoboDK](https://robodk.com/download)

No specific toolbox is required for MATLAB 2014b or later.
For MATLAB versions prior to 2014b, it is required to have the Instrument Control Toolbox (use the Robolink.m file in the Robolink-ICT-tcpip folder).


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



