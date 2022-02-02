# This example shows how to automatically move and measure a set of points using a laser tracker.
from robodk.robolink import *  # API to communicate with RoboDK for simulation and offline/online programming
from robodk.robomath import *  # Robotics toolbox for industrial robots
from robodk.robodialogs import *

# Any interaction with RoboDK must be done through RDK:
RDK = Robolink()

# Enter the points (joint coordinates) to measure manually
JOINTS_LIST = []
JOINTS_LIST.append([60.851545, 60.851555, 60.851598, 60.851598, 60.851555, 60.851545])
JOINTS_LIST.append([65.851545, 65.851555, 65.851598, 65.851598, 65.851555, 65.851545])
JOINTS_LIST.append([55.851545, 55.851555, 55.851598, 55.851598, 55.851555, 55.851545])

# Alternatively: load the list from a CSV file
#JOINTS_LIST = LoadMat("Path-to-file.csv")

# Select a robot (popup is displayed if more than one robot is available)
robot = RDK.ItemUserPick('Select a robot', ITEM_TYPE_ROBOT)
if not robot.Valid():
    raise Exception('No robot selected or available')

# As if we want to just simulate the movements
RUN_ON_ROBOT = mbox("Run on real robot?")

# Important: by default, the run mode is RUNMODE_SIMULATE
# If the program is generated offline manually the runmode will be RUNMODE_MAKE_ROBOTPROG,
# Therefore, we should not run the program on the robot
if RDK.RunMode() != RUNMODE_SIMULATE:
    RUN_ON_ROBOT = False

# Connect to the robot if we are moving the real robot:
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
#target_ref = robot.Pose()
#pos_ref = target_ref.Pos()
#print(Pose_2_TxyzRxyz(target_ref))

# move the robot to the first point:
#robot.MoveJ(target_ref)

# It is important to provide the reference frame and the tool frames when generating programs offline
# It is important to update the TCP on the robot mostly when using the driver
#robot.setPoseFrame(robot.PoseFrame())
#robot.setPoseTool(robot.PoseTool())
#robot.setZoneData(-1) # Set the rounding parameter (Also known as: CNT, APO/C_DIS, ZoneData, Blending radius, cornering, ...)
robot.setSpeed(100)  # Set linear speed in mm/s

# Run the measurements
njoints = len(JOINTS_LIST)

# Store the measurements in an array
DATA = []

for i in range(njoints):
    joints = JOINTS_LIST[i]

    print("Moving robot to %i = %s" % (i, str(joints)))
    robot.MoveJ(joints)
    print("Done")

    if not RUN_ON_ROBOT:
        continue

    #measure = mbox("Robot at position %i=%s. Select OK to take measurement or Cancel to continue." % (i, str(joints)))
    measure = True
    pause(1)

    while measure:
        print("Measuring target")
        xyz = RDK.LaserTracker_Measure()
        if xyz is None:
            if mbox("Measurment not visible. Try again?"):
                continue
            else:
                measure = False
                break

        x, y, z = xyz

        # Display the data as [time, x,y,z]
        data = '%i, %.3f, %.6f, %.6f, %.6f' % (i, toc(), x, y, z)
        print(data)
        measure = False

# Optionally, save the data to a file
#DATA_MAT = Mat(DATA).tr()
#DATA_MAT.SaveMat("Path-to-measurements-file.csv")

print('Done')
