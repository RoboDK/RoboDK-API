# This script will display reachable poses around the current robot position
#
# Press F5 to run the script
# Documentation: https://robodk.com/doc/en/RoboDK-API.html
# Reference:     https://robodk.com/doc/en/PythonAPI/index.html
# Note: It is not required to keep a copy of this file, your python script is saved with the station

# Define the ranges to test
Range_RX = range(-180,180, 60)
Range_RY = Range_RX
Range_RZ = Range_RX

# Reachable display timeouts in milliseconds
timeout_reachable = 60*60*1000

# Non reachable display timeout in milliseconds
timeout_unreachable = 1000

# Start the RoboDK API
from robolink import *    # RoboDK API
from robodk import *      # Robot toolbox
RDK = Robolink()

# Get the robot
robot = RDK.ItemUserPick('Select a robot to test reachability', ITEM_TYPE_ROBOT)
if not robot.Valid():
    quit()

# Get the current pose of the robot:
robot_pose_ref = robot.Pose()
robot_tool = robot.PoseTool()
robot_base = robot.PoseFrame()
robot_joints = robot.Joints()

# Iterate through all pose combinations and collect all valid poses
reachable_poses = []
unreachable_poses = []
for rx in Range_RX:
    for ry in Range_RY:
        for rz in Range_RZ:
            print("Testing rotation: " + str([rx,ry,rz]))
            pose_add = rotx(rx*pi/180) * roty(ry*pi/180) * rotz(rz*pi/180)
            pose_test = robot_pose_ref * pose_add
            jnts_sol = robot.SolveIK(pose_test, None, robot_tool, robot_base)
            print(jnts_sol.list())
            if len(jnts_sol.list()) <= 1:
                print("Not reachable")
                unreachable_poses.append(pose_test)
                #reachable_poses.append(pose_test)
            else:
                print("Reachable")
                reachable_poses.append(pose_test)

# Display "ghost" tools in RoboDK
Display_Default = 1
Display_Normal = 2
Display_Green = 3
Display_Red = 4


Display_Invisible = 64
Display_NotActive = 128
Display_RobotPoses = 256
Display_RobotPosesRotZ = 512
Display_Reset = 1048

Display_Options = 0
Display_Options += Display_Invisible # Show invisible tools
Display_Options += Display_NotActive # Show non active tools
Display_Options += Display_RobotPoses # Show robot joints if reachable
#Display_Options += Display_RobotPosesRotZ # Show robot joints if reachable (tests rotating around the Z axis)
#Display_Options += Display_Reset # Reset flag (clears the trace)


robot.ShowSequence([]) # Force reset
robot.ShowSequence(reachable_poses, Display_Options+Display_Default, timeout_reachable)
robot.ShowSequence(unreachable_poses, Display_Options+Display_Red, timeout_unreachable)



