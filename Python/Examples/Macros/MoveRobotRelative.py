# This macro shows how to move the robot relative to the TCP by applying rotation increments
#
# Press F5 to run the script
# Documentation: https://robodk.com/doc/en/RoboDK-API.html
# Reference:     https://robodk.com/doc/en/PythonAPI/index.html
# Note: It is not required to keep a copy of this file, your python script is saved with the station
from robolink import *  # RoboDK API
from robodk import *  # Robot toolbox

# ***** Set the program parameters ******

# Set the step increment in degrees
STEP = 1

# Another option is to provoke a popup
# STEP = float(mbox("Enter the step in deg", entry=0.1))

# Minimum rotation in degrees
ROT_MIN = -20

# Maximum rotation in degrees
ROT_MAX = 20

# Set a pause in milliseconds
PAUSE = 500

#******************************

# Start the RoboDK API
RDK = Robolink()

# Choose the tool used for relative movements
tool = RDK.ItemUserPick("Select a tool for incremental movements", ITEM_TYPE_TOOL)

# Stop if tool is not selected or the robot has no tool
if not tool:
    raise Exception("Tool not selected or available")

print("Using tool: " + tool.Name())

# Automatically select the robot (parent of the tool)
robot = tool.Parent()
print("Using robot: " + robot.Name())

# Make sure we set the correct tool for program generation
robot.setPoseTool(tool)

# Set the robot base as a reference frame
robot.setPoseFrame(robot.Parent())

# Retrieve the start position (used as reference position for relative movements)
robot_joints = robot.Joints()
robot_pose = robot.Pose()

# Move the robot to the start position (required for robot programming)
robot.MoveJ(robot_joints)

# Apply incremental movements
# Move around the reference position
rz = ROT_MIN
while rz <= ROT_MAX:
    pose_delta = rotz(rz * pi / 180)
    # you can also do:
    # pose_delta = rotx(rx * pi/180)*roty(ry*pi/180)*rotz(rz*pi/180)
    # Post multiply: the movement is made relative to the TCP
    new_pose = robot_pose * pose_delta
    robot.MoveL(new_pose)
    robot.Pause(PAUSE)
    rz = rz + STEP

robot.MoveL(robot_pose)
