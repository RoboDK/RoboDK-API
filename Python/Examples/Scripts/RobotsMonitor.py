# Connect to a robot and monitor the position from the real robot to RoboDK environment

# More information about the RoboDK API here:
# https://robodk.com/doc/en/RoboDK-API.html

from robolink import *  # API to communicate with RoboDK
from robodk import *  # basic matrix operations

# Start RoboDK API
RDK = Robolink()

# Retrieve all robots available
all_robots = RDK.ItemList(ITEM_TYPE_ROBOT, False)

# Connect to robots and keep the list of the connected robots
robots_monitor = []
for robot in all_robots:
    if robot.ConnectSafe() == ROBOTCOM_READY:
        RDK.ShowMessage("Connected to robot: " + robot.Name(), False)
        robots_monitor.append(robot)

    else:
        RDK.ShowMessage("Unable to connect to robot: " + robot.Name(), False)

if len(robots_monitor) <= 0:
    RDK.ShowMessage("No robots connected", False)
    exit()

while len(robots_monitor) > 0:
    # Iterate through all robots
    for robot in robots_monitor[:]:
        # Check if we are still connected and the robot is ready (not doing anything else), otherwise, stop
        status, msg_status = robot.ConnectedState()
        if status != ROBOTCOM_READY:
            robots_monitor.remove(robot)
            continue

        # Retrieve the position from the robot (automatically updates the robot in RoboDK)
        joints = robot.Joints()
        print(joints.list())

RDK.ShowMessage("Monitoring finished", False)

# Alternatively, the following code will simply connect to one robot and monitor in an infinite loop:
#robot = RDK.Item('', ITEM_TYPE_ROBOT)
#if robot.ConnectSafe() != ROBOTCOM_READY:
#    raise Exception("Robot not connected")
#
#while True:
#    # When connected, this will retrieve the position of the real robot
#    robot.Joints()
