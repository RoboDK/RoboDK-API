# This macro shows an example to run a program on the robot from the Python API (online programming)
#
# Important: By default, right clicking a program on the RoboDK API and selecting "Run On Robot" has the same effect as running this example.
# Use the Example_OnlineProgramming.py instead if the program is run from the RoboDK Station Tree
#
# This example forces the connection to the robot by using:
# robot.Connect()
# and
# RDK.setRunMode(RUNMODE_RUN_ROBOT)

# In this script, if the variable RUN_ON_ROBOT is set to True, an attempt will be made to connect to the robot
# Alternatively, if the RUN_ON_ROBOT variable is set to False, the program will be simulated (offline programming)
#
# More information about the RoboDK API here:
# https://robodk.com/doc/en/RoboDK-API.html

from robolink import *  # API to communicate with RoboDK
from robodk import *  # robodk robotics toolbox

# Any interaction with RoboDK must be done through RDK:
RDK = Robolink()

# Select a robot (popup is displayed if more than one robot is available)
robot = RDK.ItemUserPick('Select a robot', ITEM_TYPE_ROBOT)
if not robot.Valid():
    raise Exception('No robot selected or available')

RUN_ON_ROBOT = True

# Important: by default, the run mode is RUNMODE_SIMULATE
# If the program is generated offline manually the runmode will be RUNMODE_MAKE_ROBOTPROG,
# Therefore, we should not run the program on the robot
if RDK.RunMode() != RUNMODE_SIMULATE:
    RUN_ON_ROBOT = False

if RUN_ON_ROBOT:
    # Update connection parameters if required:
    # robot.setConnectionParams('192.168.2.35',30000,'/', 'anonymous','')

    # Connect to the robot using default IP
    success = robot.Connect()  # Try to connect once
    #success robot.ConnectSafe() # Try to connect multiple times
    status, status_msg = robot.ConnectedState()
    if status != ROBOTCOM_READY:
        # Stop if the connection did not succeed
        print(status_msg)
        raise Exception("Failed to connect: " + status_msg)

    # This will set to run the API programs on the robot and the simulator (online programming)
    RDK.setRunMode(RUNMODE_RUN_ROBOT)
    # Note: This is set automatically when we Connect() to the robot through the API

#else:
# This will run the API program on the simulator (offline programming)
# RDK.setRunMode(RUNMODE_SIMULATE)
# Note: This is the default setting if we do not execute robot.Connect()
# We should not set the RUNMODE_SIMULATE if we want to be able to generate the robot programm offline

# Get the current joint position of the robot
# (updates the position on the robot simulator)
joints_ref = robot.Joints()

# get the current position of the TCP with respect to the reference frame:
# (4x4 matrix representing position and orientation)
target_ref = robot.Pose()
pos_ref = target_ref.Pos()
print("Drawing a polygon around the target: ")
print(Pose_2_TxyzRxyz(target_ref))

# move the robot to the first point:
robot.MoveJ(target_ref)

# It is important to provide the reference frame and the tool frames when generating programs offline
# It is important to update the TCP on the robot mostly when using the driver
robot.setPoseFrame(robot.PoseFrame())
robot.setPoseTool(robot.PoseTool())
robot.setZoneData(10)  # Set the rounding parameter (Also known as: CNT, APO/C_DIS, ZoneData, Blending radius, cornering, ...)
robot.setSpeed(200)  # Set linear speed in mm/s

# Set the number of sides of the polygon:
n_sides = 6
R = 100

# make a hexagon around reference target:
for i in range(n_sides + 1):
    ang = i * 2 * pi / n_sides  #angle: 0, 60, 120, ...

    #-----------------------------
    # Movement relative to the reference frame
    # Create a copy of the target
    target_i = Mat(target_ref)
    pos_i = target_i.Pos()
    pos_i[0] = pos_i[0] + R * cos(ang)
    pos_i[1] = pos_i[1] + R * sin(ang)
    target_i.setPos(pos_i)
    print("Moving to target %i: angle %.1f" % (i, ang * 180 / pi))
    print(str(Pose_2_TxyzRxyz(target_i)))
    robot.MoveL(target_i)

    #-----------------------------
    # Post multiply: relative to the tool
    #target_i = target_ref * rotz(ang) * transl(R,0,0) * rotz(-ang)
    #robot.MoveL(target_i)

# move back to the center, then home:
robot.MoveL(target_ref)

print('Done')

## Example to run a program created using the GUI from the API
#prog = RDK.Item('MainProgram', ITEM_TYPE_PROGRAM)
## prog.setRunType(PROGRAM_RUN_ON_ROBOT) # Run on robot option
## prog.setRunType(PROGRAM_RUN_ON_SIMULATOR) # Run on simulator (default on startup)
#prog.RunProgram()
#while prog.Busy() == 1:
#    pause(0.1)
#print("Program done")
