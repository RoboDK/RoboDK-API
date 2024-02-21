clc
clear
close

% Start the RoboDK API for Matlab:
RDK = Robolink();

% Get the robot item:
robot = RDK.Item('', RDK.ITEM_TYPE_ROBOT);
if ~robot.Valid()
    return
end

% Get the robot position (simulated or real if we are connected to
% the robot)
poseref = robot.Pose();

% Get the home target and the welding targets:
%home = RDK.Item('Home');
%target = RDK.Item('Target 1');

% Get the pose of a target (4x4 matrix representing
% position and orientation):
%poseref = target.Pose();

% move the robot to home, then to the Target 1:
%robot.MoveJ(home)
%robot.MoveJ(target)

% Draw a polygon around the Target 1:
nsides = 100;

for i = 0:nsides
    ang = i * 2 * pi / nsides; % angle: 0, 60, 120, ...
    posei = poseref * rotz(ang) * transl(200, 0, 0) * rotz(-ang);
    robot.MoveL(posei);
end

% Move back to the original position:
robot.MoveL(poseref);

% Move back to the center, then home:
%robot.MoveL(target)
%robot.MoveJ(home)
