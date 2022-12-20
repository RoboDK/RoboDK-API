% This is an example that uses the RoboDK API for Matlab.
% This is a .m file (Matlab file).
% The RoboDK API for Matlab requires the files in this folder.
% This example requires RoboDK to be running
% (otherwise, RoboDK will be started if it was installed in the default location)
% This example automatically loads the Example 01 installed by default in the "Library" folder

% Note: This program is not meant to accomplish a specific goal, only to
% show how to use the Matlab API
%
% RoboDK api Help:
% ->Type "doc Robolink"            for more help on the Robolink class
% ->Type "doc RobolinkItem"        for more help on the RobolinkItem item class
% ->Type "showdemo Example_RoboDK" for examples on how to use RoboDK's API using the last two classes

clc
close
clear

% Generate a Robolink object RDK. This object interfaces with RoboDK.
RDK = Robolink;

% Display the list of all items in the main tree
fprintf('Available items in the station:\n');
disp(RDK.ItemList(-1, 1));

robot = RDK.ItemUserPick('Select one robot', RDK.ITEM_TYPE_ROBOT);

if robot.Valid() == 0
    error('No robot selected');
end

fprintf('Selected robot: %s\n', robot.Name());

% return;

%% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

fprintf('Current robot joints:\n');
disp(robot.Joints());

fprintf('Current robot pose:\n');
pose = robot.Pose();
disp(pose);

fprintf('Current robot pose (xyzrpw format)\n');
xyzrpw = Pose_2_XYZRPW(pose);
disp(xyzrpw);
