clc
clear
close all

INTERACTIVE_MODE = false;

%------------------------------------------------
% Create a link to the RoboDK instance.
% If RoboDK is not running, a new instance will be created.
RDK = Robolink;

% Prompt the user with some usefull information
RDK.ShowMessage('Welcome to the RoboDK API demo!<br><br>This demo presents common use cases and features of the RoboDK API.', INTERACTIVE_MODE)

% Retrieve some information regarding RoboDK
RDK.ShowMessage(sprintf('Here is some information regarding your RoboDK:<br>Version: %s<br>License: %s', RDK.Command('Version'), RDK.License()), INTERACTIVE_MODE)

%------------------------------------------------
% Create a new, empty station
station = RDK.AddStation('RoboDK API Demo');
disp(station.Name())

%------------------------------------------------
% Add a robot to the station from a local file
% This examples requires a Mecademic Meca500
library_path = RDK.getParam('PATH_LIBRARY');
robot_path = [library_path, 'Mecademic-Meca500-R3.robot'];
robot = RDK.AddFile(robot_path);

if ~robot.Valid()
    RDK.ShowMessage(sprintf('This example requires a Mecademic Meca500 in your library folder:<br>%s.<br><br>You can download this robot at https://robodk.com/robot/Mecademic/Meca500-R3.', library_path))
    return
end

robot_frame = robot.Parent();

% Add a TCP
tool_1 = robot.AddTool(transl(0, 0, 10), 'Tool 1');
tool_2 = robot.AddTool(transl(0, 0, 50), 'Tool 2');

% Set the active tool and frame
robot.setPoseFrame(robot_frame)
robot.setPoseTool(tool_1)

%------------------------------------------------
% Add dynamically created curves and points
npoints = 100 + 1;
points_mtx = zeros(3, npoints);

for i = 1:npoints
    points_mtx(:, i) = [i, sin(i), 0]; % Create XYZ points as a function of sinus
end

points = RDK.AddPoints(points_mtx);
points.setName('Points')
points.setParent(robot_frame)
points.setPose(transl(120, -20, 70))

curve_mtx = zeros(3, npoints);

for i = 1:npoints
    curve_mtx(:, i) = [i, cos(i), 0]; % Create XYZ points as a function of cosinus
end

curve = RDK.AddCurve(curve_mtx);
curve.setName('Curve')
curve.setParent(robot_frame)
curve.setPose(transl(220, -20, 70) * rotz(pi / 2))

% Change the colors
curve.setColorCurve([1, 0, 0, 1]) % Solid red
points.setValue('Display', 'PARTICLE=SPHERE(1,10) COLOR=#FF00FF00') % Green spheres (#AARRGGBB)

% Retrieve curves and points
[points_list, x] = points.GetPoints(RDK.FEATURE_POINT);
[curve_list, x] = curve.GetPoints(RDK.FEATURE_CURVE);

%------------------------------------------------
% Create programs from points or curve points
prog_targets = RDK.AddProgram('Target', robot);
prog_targets.ShowInstructions(false) % Hide instructions, as there will be a lot!
prog_targets.setPoseFrame(robot_frame)
prog_targets.setPoseTool(tool_1)

for i = 1:length(curve_list)
    point = curve_list(i, :);
    xyz = point(1:3);
    ijk = -1 * point(4:6); % IJK is the surface normal. Point the TCP to Z-
    pose = transl(xyz(1), xyz(2), xyz(3));
    pose(1, 3) = ijk(1);
    pose(2, 3) = ijk(2);
    pose(3, 3) = ijk(3);
    pose = curve.Pose() * pose; % Points are in the object frame, translate to the parent frame

    if i < 10
        % Add to program using targets
        target = RDK.AddTarget(sprintf('Target %i', i), robot_frame, robot);
        target.setPose(pose)

        if i == 0
            prog_targets.MoveJ(target)
        else
            prog_targets.MoveL(target)
        end

    else
        % Add to program using poses
        prog_targets.MoveJ(pose)
    end

    RDK.Command('ProgressBar', num2str(100 * (i - 1) / 100, 2)); % Show a progress bar in the status bar of RoboDK
end

RDK.Command('ProgressBar', '-1'); % Hide the progress bar once we are done

% Create machining programs from curves and points
proj_points = RDK.AddMachiningProject('Point Follow Settings', robot);
proj_points.setMachiningParameters('', points);
proj_points.setPoseTool(tool_1)

proj_curve = RDK.AddMachiningProject('Curve Follow Settings', robot);
proj_curve.setMachiningParameters('', curve);
proj_curve.setPoseTool(tool_2)

% Verify the integrity of the projects/programs
disp(proj_points.Update())
disp(proj_curve.Update())
disp(prog_targets.Update())

% Get the program generated from the machining project
prog_points = proj_points.getLink(RDK.ITEM_TYPE_PROGRAM);
prog_curve = proj_curve.getLink(RDK.ITEM_TYPE_PROGRAM);

%------------------------------------------------
% Add dynamically created objects using triangle mesh
A = [0; 0; 0];
B = [100; 0; 0];
C = [100; 100; 0];
D = [0; 100; 0];

% Add a triangle
triangle = RDK.AddShape([A, B, C]);
triangle.setName('Triangle')
triangle.setParent(robot_frame)
triangle.setPose(transl(120, -20, 70))

% Add a square / plane
square = RDK.AddShape([A, C, B, A, D, C]);
square.setName('Square')
square.setGeometryPose(transl(-50, -50, 0), true) % Center the object reference
square.setParent(robot_frame)
square.setPose(transl(0, -170, 70))

% Add a cube
RDK.Render(false) % Set the render off, so that intermediary objects are never shown
square.Copy() % Use the previously created square as a baseline object
face_items = cell(1, 6); % 6 faces of a cube
face_poses = cell(1, 6);

for i = 0:4
    face_poses{i + 1} = rotx(i * (pi / 2));
end

face_poses{5} = roty(pi / 2);
face_poses{6} = roty(-pi / 2);

for i = 1:length(face_poses)
    plane_item = RDK.Paste();
    plane_item.setGeometryPose(transl(0, 0, 50), true)
    plane_item.setPose(face_poses{i})
    face_items{i} = plane_item;
end

cube = RDK.MergeItems(face_items); % Merge the faces together into a new object
cube.setName('Cube')
cube.setParent(robot_frame)
cube.setPose(transl(0, 170, 70))
RDK.Render(true) % Set the render back on

% Add a square prism
RDK.Render(false) % Set the render off, so that intermediary objects are never shown
cube.Copy()
prism = robot_frame.Paste();
prism.setName('Prism')
prism.Scale([0.5, 0.5, 1])
prism.setPose(transl(0, 290, 70))
RDK.Render(true) % Set the render back on

% Retrieve the mesh of objects
[triangle_mesh, x] = triangle.GetPoints(RDK.FEATURE_OBJECT_MESH);
[square_mesh, x] = square.GetPoints(RDK.FEATURE_OBJECT_MESH);
[cube_mesh, x] = cube.GetPoints(RDK.FEATURE_OBJECT_MESH);
[prism_mesh, x] = prism.GetPoints(RDK.FEATURE_OBJECT_MESH);

% Change colors
triangle.setColor([1, 0, 0, 1]) % Solid red
square.setColor([0, 1, 0, 0.85]) % Transparent green
cube.setColor([0, 0, 1, 0.49]) % Transparent blue, click-through (alpha < 0.5)
prism.setColor(triangle.Color())

%------------------------------------------------
% Reconstruct a robot from scratch
% The values below are intended for a Mecademic Meca500

robot_name = robot.Name();
DOFs = length(robot.Joints());

% Define the joints of the robot/mechanism
joints_build = [0, 0, 0, 0, 0, 0];

% Define the home position of the robot/mechanism (default position when you build the mechanism)
% This is also the position the robot goes to if you select "Home"
joints_home = robot.JointsHome();

% Define the robot parameters. The parameters must be provided in the same order they appear in the menu Utilities-Model Mechanism or robot
parameters = [135, 0, 0, 135, 38, 120, 70, 0, -90, 0, 0, 0, 180];

% Define the joint sense (set to +1 or -1 for each axis
joints_senses = [1, 1, 1, 1, 1, 1];

% Joint limits (upper/lower limits for each axis)
[lower_limits, upper_limits, joints_type] = robot.JointLimits();
lower_limits = transpose(lower_limits);
upper_limits = transpose(upper_limits);

% Base frame pose (offset the model by applying a base frame transformation)
base_pose = eye(4);

% Tool frame pose (offset the tool flange by applying a tool frame transformation)
tool_pose = eye(4);

% Robot objects representing each links
RDK.Render(false)

list_objects = {};

for i = 0:DOFs
    link = robot.ObjectLink(i);
    link.Copy()
    nlink = RDK.Paste();
    nlink.setName(sprintf('J%i', i))
    nlink.setPoseAbs(link.PoseAbs())
    RDK.Update()
    list_objects{end + 1} = nlink;
end

% Create the robot/mechanism
new_robot = RDK.BuildMechanism(RDK.MAKE_ROBOT_6DOF, list_objects, parameters, joints_build, joints_home, joints_senses, lower_limits, upper_limits, base_pose, tool_pose, robot_name);
RDK.Delete(list_objects)

RDK.Render(true)

%------------------------------------------------
% Move the robots

% Move by program. This is a non-blocking call associated with the original robot
prog_points.RunCode()

while prog_points.Busy()
    % Relative move with the copy
    new_robot.MoveJ(transl(0, 0, -0.1) * new_robot.Pose())
end

% Wait for the first program to finish
prog_points.WaitFinished()

% Home the robots at the same time
robot.MoveJ(robot.JointsHome(), false)
new_robot.MoveJ(new_robot.JointsHome())

%------------------------------------------------
% Manipulate the 3D view pose

% Zoom to fit
RDK.Command('FitIsometric')

% Rotate 180 degrees
view_pose = RDK.ViewPose();
RDK.setViewPose(view_pose * rotz(pi))

%------------------------------------------------
% Manipulate the 3D view pose
RDK.setSelection(RDK.ItemList()) % Set a custom selection
selection = RDK.Selection(); % Retrieve the selection
cellfun(@(x) disp(x.Name()), selection)
RDK.setSelection([]) % Clear the selection
