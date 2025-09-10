% Original file from MathWorks: https://github.com/mathworks-robotics/intelligent-bin-picking-example-with-simulink/blob/main/example2-urCobot-gazebo/MotionPlanning/exampleHelperAddGripper.m 

function outputRobot = exampleHelperAddGripper(inputRobot)
%This function is for internal use only and may be removed in the future.
% exampleHelperAddGripper attaches Robotiq EPick gripper and IO Coupling to
% UR5e robot
%   The single bellow is made with MathWorks tools

%Copyright 2023 The MathWorks, Inc.

% Add I/O Coupling
coupling = rigidBody('IO_Coupling','MaxNumCollisions',1);
tf = eul2tform([0 0 0]);
tf(:,4) = [0; 0; 0.008; 1]; % To avoid collision
addCollision(coupling,'cylinder',[0.083/2 0.0139],tf);
couplingJoint = rigidBodyJoint('couplingJoint','fixed');
coupling.Joint = couplingJoint;
curEndEffectorBodyName = inputRobot.BodyNames{10};
addBody(inputRobot,coupling,curEndEffectorBodyName);

% Add Gripper Unit
transformGripper = eul2tform([0 0 0]);
transformGripper(:,4) = [0; 0; 0.0139; 1]; % The width is 16.9 or 13.9
gripper = rigidBody('EPick','MaxNumCollisions',1);
tf = eul2tform([0 0 0]);
tf(:,4) = [0; 0; 0.045; 1]; % Gripper Width
addCollision(gripper,'cylinder',[0.083/2 0.1023],tf);
gripperJoint = rigidBodyJoint('gripperJoint','fixed');
gripper.Joint = gripperJoint;
setFixedTransform(gripper.Joint, transformGripper);
curEndEffectorBodyName = inputRobot.BodyNames{11};
addBody(inputRobot,gripper,curEndEffectorBodyName);

% Add Extention tube
transformTube = eul2tform([0 0 0]);
transformTube(:,4) = [0; 0; 0.101; 1]; % The width is 101
tube = rigidBody('Tube','MaxNumCollisions',1);
tf = eul2tform([0 0 0]);
tf(:,4) = [0; 0; 0.101; 1]; % Gripper Width
addCollision(tube,'cylinder',[0.005 0.2],tf);
tubeJoint = rigidBodyJoint('tubeJoint','fixed');
tube.Joint = tubeJoint;
setFixedTransform(tube.Joint, transformTube);
curEndEffectorBodyName = inputRobot.BodyNames{12};
addBody(inputRobot,tube,curEndEffectorBodyName);

% Add Bellow Small
transformBellow = eul2tform([0 0 0]);
transformBellow(:,4) = [0; 0; 0.21; 1]; % The width is 101
bellow = rigidBody('tcp');
bellowJoint = rigidBodyJoint('bellowJoint','fixed');
bellow.Joint = bellowJoint;
setFixedTransform(bellow.Joint, transformBellow);
curEndEffectorBodyName = inputRobot.BodyNames{13};
addBody(inputRobot,bellow,curEndEffectorBodyName);
    
outputRobot = inputRobot;
end
