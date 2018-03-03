function robot_item = RoboDK_getRobot()

persistent RDK
persistent robot

if isempty(robot)
    RDK = Robolink();
    robot = RDK.ItemUserPick('Select a robot',RDK.ITEM_TYPE_ROBOT);
    if robot.Valid() == 0
        error('No robot selected or available');
    end
    fprintf('Robot selected: %s\n', robot.Name());
end

robot_item = robot;

