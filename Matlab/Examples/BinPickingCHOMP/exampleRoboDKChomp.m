% This is an example that combines RoboDK and Matlab to generate collision-free motion using CHOMP.


clc;
clear;
close all;

if ~exist('meshtsdf','class')
    error('Navigation Toolbox is required  for this example!');
end

addpath("C:\RoboDK\Matlab")

storageFolder = 'saved_objects';
if ~exist(storageFolder, 'dir')
    mkdir(storageFolder);
end

INTERACTIVE_MODE = false;
ENABLE_VIEWER = true;

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function surfaces=getItemMesh(item)
% Get the complete mesh from RoboDK
i = 0;
surfaces = {};
while 1
    [vertices, ~] = item.GetPoints(item.RDK.FEATURE_OBJECT_MESH, i);
    if isempty(vertices)
        break;
    end
    surfaces{end+1} = vertices(:, 1:3) / 1000; % drop normals, mm to m
    i=i+1;
end
end

function triObj=mesh2triangulation(surfaces)
% Initialize P (points) and T (triangulation connectivity list)
P = []; % Combined list of points
T = []; % Combined triangulation connectivity list
offset = 0; % Offset for indexing triangles

% Process each surface
for s = 1:numel(surfaces)
    surfaceVertices = surfaces{s}; % Get the vertices for the current surface
    numVertices = size(surfaceVertices, 1); % Number of vertices in this surface

    % Append vertices to P
    P = [P; surfaceVertices];

    % Generate connectivity list for this surface
    if mod(numVertices, 3) ~= 0
        error('Each surface must contain vertices divisible by 3.');
    end
    localT = reshape(offset + (1:numVertices), 3, [])'; % Connectivity for this surface
    T = [T; localT]; % Append connectivity to global T

    % Update offset
    offset = offset + numVertices;
end

% Create the triangulation object
triObj = triangulation(T, P);
end

function success=loadTrajectoryInRoboDK(wptsamples,program_name,robot_item,RDK,validate)
if nargin < 5
    validate = 1;
end

% Create a new program in RoboDK
disp("Loading " + program_name + " in RoboDK..");
RDK.ShowMessage("Loading " + program_name + " in RoboDK..", 0);

RDK.Render(false);
program_rdk = RDK.Item(program_name, RDK.ITEM_TYPE_PROGRAM);
parent=RDK.ActiveStation();
if program_rdk.Valid()
    parent=program_rdk.Parent();
    program_rdk.Delete()
end
program_rdk = RDK.AddProgram(program_name, robot_item);
program_rdk.setParent(parent);
program_rdk.ShowInstructions(0);

% Store trajectory points in the program
num_samples = size(wptsamples, 1);
for i = 1:num_samples
    % Convert the trajectory point to degrees (RoboDK expects degrees)
    joint_angles_deg = rad2deg(wptsamples(i, :));

    % Add MoveJ command to the program
    program_rdk.MoveJ(joint_angles_deg);
end
RDK.Render(true);

if validate
    [valid_instructions, program_time, program_distance, valid_ratio, readable_msg] = program_rdk.Update(0);
    if valid_ratio < 1.0
        disp("Trajectory failed in RoboDK.");
        disp(readable_msg);
        throw(MException(readable_msg))
        success=false;
        return
    end
end

disp("Trajectory loading completed in RoboDK.");
success=true;
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
if ENABLE_VIEWER
    fig = figure;
end

RDK = Robolink;

% Fetch object meshes from RoboDK
% Exclude the tool as it is being attached in MATLAB -> TODO: Dynamically
% load the tool from mesh?
RDK.ShowMessage('Initializing scene..', 0);
exclude = ["Floor", "Extension Tube", "Suction Cup"];
env_objects = RDK.ItemList(RDK.ITEM_TYPE_OBJECT);
env = {};
for i = 1 : numel(env_objects)
    item = env_objects{i};
    if ~item.Visible() || any(contains(exclude, item.Name()))
        continue;
    end

    item_pose = item.PoseAbs();
    item_pose(1:3,4) = item_pose(1:3,4) / 1000; % mm -> m


    disp(['Processing ' item.Name()]);
    %disp(item_pose);

    objName = item.Name();
    matFile = fullfile(storageFolder, [objName '.mat']);

    if isfile(matFile)
        % Load pre-saved collision mesh
        loadedData = load(matFile);
        meshColl = loadedData.meshColl;
        disp(['Loaded mesh from file: ' objName]);
    else
        % Fetch from RoboDK
        disp(['Fetching new mesh from RoboDK: ' objName]);
        surfaces = getItemMesh(item);
        meshTri = mesh2triangulation(surfaces);

        % Create collision mesh
        meshColl = collisionVHACD(meshTri);

        % Save to .mat
        save(matFile, 'meshColl');
    end

    for j = 1:length(meshColl)
        meshColl{j}.Pose = item_pose;
    end
    %showCollisionArray([meshColl {}]);

    env{end + 1} = meshColl;
end

if isempty(env)
    error('No valid meshes found in the environment.');
end

% Load environnement to meshtsdf
manager=meshtsdf(Resolution=150, TruncationDistance=0.15);

c = 1;
for i = 1:numel(env)
    vhacdObj = env{i};
    for j = 1:length(vhacdObj)
        meshStruct = geom2struct(vhacdObj{j}, c);
        manager.addMesh(meshStruct);
        c = c + 1;
    end
end

% Display visualization
if ENABLE_VIEWER
    % hold on
    show(manager);
    disp('Waiting on user to close figure..');
    waitfor(fig);
end


% Initialize RoboDK
robot_item = RDK.Item('UR5e');
home_target_item = RDK.Item('Wait Camera');
pick_target_item = RDK.Item('Pick App'); % Dynamic
place_target_item = RDK.Item('Place App'); % Dynamic
trans_target_item = RDK.Item('Fly By');

% Load robot and initialize CHOMP
robot = loadrobot("universalUR5e", DataFormat="row");
tformZYX = eul2tform([0 0 0]);
setFixedTransform(robot.Base.Children{1,2}.Joint,tformZYX);

robot = exampleHelperAddGripper(robot);
if ENABLE_VIEWER
    hold on;
    show(robot, deg2rad(home_target_item.Joints()), Collisions="on", Visuals="on");
    show(manager);
    waitfor(fig);
end

% 1. Pick Motion

% Fetch robot's current joints and target joint configurations
startconfig = deg2rad(home_target_item.Joints()); % Current location
goalconfig = deg2rad(pick_target_item.Joints());

% CHOMP options
chompPick = manipulatorCHOMP(robot,MeshTSDF=manager);
chompPick.SmoothnessOptions = chompSmoothnessOptions(SmoothnessCostWeight=1e-5);
chompPick.CollisionOptions = chompCollisionOptions(CollisionCostWeight=10);
chompPick.SolverOptions = chompSolverOptions(LearningRate=5, Verbosity="detailed");

% Define trajectory optimization parameters
timepoints = [0 5];
timestep = 0.1;
trajtype = "minjerkpolytraj";

% Optimize trajectory
RDK.ShowMessage('Optimizing PICK trajectory..', 0);
disp('Optimizing PICK trajectory..');
[wptsamples, tsamples] = optimize(chompPick, ...
    [startconfig; goalconfig], ...
    timepoints, ...
    timestep, ...
    InitialTrajectoryFitType=trajtype);

% Visualize optimized trajectory
if ENABLE_VIEWER
    show(chompPick, wptsamples, NumSamples=5, CollisionObjects=[env{:}]);
    %zlim([-0.5 1.3]);
    disp('Waiting on user to close figure..');
    waitfor(fig);
end

% Create a new program in RoboDK
loadTrajectoryInRoboDK(wptsamples, 'Pick', robot_item,RDK);

% 2. Place Motion

% Attach part to body
robot = exampleHelperAttachPartAtEndEffector(robot,-pi/2);
if ENABLE_VIEWER
    hold on;
    show(robot, deg2rad(pick_target_item.Joints()), Collisions="on", Visuals="on");
end

% Fetch robot's current joints and target joint configurations
startconfig = deg2rad(pick_target_item.Joints()); % Current location
transconfig = deg2rad(trans_target_item.Joints());
goalconfig = deg2rad(place_target_item.Joints());

% CHOMP options
chompPlace = manipulatorCHOMP(robot,MeshTSDF=manager);
chompPlace.SmoothnessOptions = chompSmoothnessOptions(SmoothnessCostWeight=1e-5);
chompPlace.CollisionOptions = chompCollisionOptions(CollisionCostWeight=2);
chompPlace.SolverOptions = chompSolverOptions(LearningRate=5, Verbosity="detailed");


% Define trajectory optimization parameters
timepoints = [0 2 5];
timestep = 0.1;
trajtype = "minjerkpolytraj";

% Optimize trajectory
RDK.ShowMessage('Optimizing PLACE trajectory..', 0);
disp('Optimizing PLACE trajectory..');
[wptsamples, tsamples] = optimize(chompPlace, ...
    [startconfig; transconfig; goalconfig], ...
    timepoints, ...
    timestep, ...
    InitialTrajectoryFitType=trajtype);

% Visualize optimized trajectory
if ENABLE_VIEWER
    show(chompPlace, wptsamples, NumSamples=5, CollisionObjects=[env{:}]);
    %zlim([-0.5 1.3]);
    disp('Waiting on user to close figure..');
    waitfor(fig);
end

% Create a new program in RoboDK
loadTrajectoryInRoboDK(wptsamples, 'Place', robot_item, RDK);