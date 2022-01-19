# This macro allows synchronizing more than one robot along specific key points (given a Move ID)
# This is a blocking procedure that will stop robot movement until all robots reach the same keypoint
#
# More information about the RoboDK API here:
# https://robodk.com/doc/en/RoboDK-API.html
# For more information visit:
# https://robodk.com/doc/en/PythonAPI/robolink.html

import sys  # allows getting the argument parameters
from robodk.robolink import *
from robodk.robomath import *    # basic matrix operations

#---------------------------------------------
# Synchronization program for a specific robot
# Enter the ID of the robot:
ROBOT_ID = 1
# Enter the total number of robots to wait
TOTAL_ROBOTS = 2
# Important: if we have 3 robots, we need to have:
# SyncRobot1  (ROBOT_ID = 1)
# SyncRobot2  (ROBOT_ID = 2)
# SyncRobot3  (ROBOT_ID = 3)
#-----------------------------
# We can use SyncRobot in 2 different ways:
# 1- Call: SyncRobot1(1) or SyncRobot1(12.34)
#    which will make sure all robots reach the same movement number id (tag)
# 2- Call: SynchRobot1    (no argument required)
#    which will automatically increase the move ID by 1 each time
#    on start, we can force it to SyncRobot1(0) to reset the counter

# Station variable used to save the current Move ID for each robot
# We can access station variables by right clicking the station, then, select "Station variables"
MOVE_ID_VAR_STN = 'MOVE_ID_R%i' % ROBOT_ID

# Connect to the RoboDK API
RDK = Robolink()

# Variable holding the current movement ID
MOVE_ID = 0
if len(sys.argv) > 1:
    # If a value is provided as an argument, take the move ID * 1000 to allow decimal numbers
    MOVE_ID = int(float(sys.argv[1]) * 1000)
else:
    # If no move ID provided for synchronization, automatically increase index
    MOVE_ID = RDK.getParam(MOVE_ID_VAR_STN)
    if MOVE_ID is None:
        # In this case, it means it is the first time we run it, so reset counter
        MOVE_ID = 0
    else:
        # If the station variable exists: increase the Move ID by 1 automatically
        MOVE_ID = MOVE_ID + 1

# Save the current move id as a station variable to notify that this robot reached a specific movement
# (other robots may be waiting for this robot)
RDK.setParam(MOVE_ID_VAR_STN, MOVE_ID)

# If Move ID is 0 we can skip synchronisation (counter reset is made)
if MOVE_ID == 0:
    quit()

# Wait until all robots reach the same Move ID
waiting = True
while waiting:
    waiting = False
    for i in range(TOTAL_ROBOTS):
        Rid = i + 1

        # Skip the same robot ID
        if Rid == ROBOT_ID:
            continue

        # Hold on until all robots reach the same Move ID
        if RDK.getParam('MOVE_ID_R%i' % Rid) < MOVE_ID:
            waiting = True
            break
    pause(0.1)

print('All robots are at MOVE_ID = %i' % MOVE_ID)
