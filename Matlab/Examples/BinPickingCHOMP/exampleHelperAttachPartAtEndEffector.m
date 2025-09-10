% Original file from MathWorks: https://github.com/mathworks-robotics/intelligent-bin-picking-example-with-simulink/blob/main/example2-urCobot-gazebo/MotionPlanning/exampleHelperAttachPartAtEndEffector.m 

function ur5e = exampleHelperAttachPartAtEndEffector(ur5e,rotation)
%This function is for internal use only and may be removed in the future.
% This helper function is used to attach a part body to the
% end-effector to update the rigid body tree for collision free
% trajectory in the given environment

%   Copyright 2023 The MathWorks, Inc.

% Part Dimenssions in meters
partwidth = 0.0508;
partheight = 0.0508;
partLength = 0.1016;

% Computed transformation matrix for adding collision object
transformForCollision = eul2tform([rotation+pi/2 0 0]);
transformForCollision(:,4) = [0; 0; partheight/2-0.01; 1];

% Attach collision box to the rigid body model
part = rigidBody('part','MaxNumCollisions',1);
box = [partLength partwidth partheight];
addCollision(part,'box',box,transformForCollision);

% Computed transformation matrix for adding fixed joint for object
transformPart = eul2tform([0 0 0]);
transformPart(:,4) = [0; 0; 0.005; 1]; % To avoid self collision add 0.005m offset

% Create a fixed joint and attach it to the robot end-effector body
partJoint = rigidBodyJoint('partJoint','fixed');
part.Joint = partJoint;
setFixedTransform(part.Joint, transformPart);
curEndEffectorBodyName = ur5e.BodyNames{end};
if strcmp(ur5e.BodyNames{end}, part.Name)
    ur5e.removeBody(part.Name);
    curEndEffectorBodyName = ur5e.BodyNames{end};
end
addBody(ur5e,part,curEndEffectorBodyName);
end