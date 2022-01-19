# This macro disconnects all robots so that programs can be run in simulation mode only
#
# More information about the RoboDK API here:
# https://robodk.com/doc/en/RoboDK-API.html
# For more information visit:
# https://robodk.com/doc/en/PythonAPI/robolink.html

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
    RDK.ShowMessage("Disconnecting robot %s..." % robot_name, False)
    robot.Disconnect()
    # robot.Disconnect() # calling disconnect twice in a row will force stop (same as double click)

# Iterate through all programs and uncheck the "Run on robot" option
programs = RDK.ItemList(ITEM_TYPE_PROGRAM, False)
for prog in programs:
    prog.setRunType(PROGRAM_RUN_ON_SIMULATOR)
    #if prog.Name().startswith("Curve"):
    #    prog.setRunType(PROGRAM_RUN_ON_SIMULATOR)
