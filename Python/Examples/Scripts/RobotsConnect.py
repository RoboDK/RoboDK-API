# WARNING:
# This macro connects to all robots available in the RoboDK station and moves them to the HOME position
#
# More information about the RoboDK API here:
# https://robodk.com/doc/en/RoboDK-API.html

from robolink import *  # API to communicate with RoboDK
from robodk import *  # basic matrix operations

# Start RoboDK API
RDK = Robolink()

# Retrieve all robots as pointers
robots = RDK.ItemList(ITEM_TYPE_ROBOT, False)

# Iterate through all robots trying to connect, if success then move to the home position.
# Note: The home position can be updated per robot
# Note: The robot movement and connection can be non blocking if it is started on a separate tread with a different Robolink object
nrobots = len(robots)
for i in range(nrobots):
    robot = robots[i]
    robot_name = robot.Name()
    RDK.ShowMessage("Trying to connect to %s..." % robot_name, False)
    success = robot.ConnectSafe()
    if success > 0:
        RDK.ShowMessage("Connection with %s succeeded." % robot_name, False)
        #RDK.ShowMessage("Connection with %s succeeded. Moving robot Home" % robot_name, False)
        #robot.MoveJ(robot.JointsHome())
    else:
        RDK.ShowMessage("Connection with %s Failed" % robot_name, False)
        pause(2)
