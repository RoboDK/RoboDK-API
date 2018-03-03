function joints = RoboDK_Pose2Joints(pose)

robot = RoboDK_getRobot();

joints = robot.SolveIK(pose);
if isempty(joints)
    joints = zeros(6,1);
    warning('No robot solution');
end

