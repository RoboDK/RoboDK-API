# Draw a hexagon around the current robot position

from robodk.robolink import *  # RoboDK's API
from robodk.robomath import *  # Robot toolbox

# Start the RoboDK API:
RDK = Robolink()

# Get the robot (first robot found):
robot = RDK.Item('', ITEM_TYPE_ROBOT)

# Get the reference target by name:
#target = RDK.Item('Target 1')
#target_pose = target.Pose()
#robot.MoveJ(target)

target_pose = robot.Pose()
xyz_ref = target_pose.Pos()

# Move the robot to the reference point (current position/redundant):
robot.MoveJ(target_pose)

# Draw a hexagon around the reference target:
for i in range(7):
    ang = i * 2 * pi / 6  # Angle = 0,60,120,...,360
    R = 200  # Polygon radius

    # Calculate the new position around the reference:
    x = xyz_ref[0] + R * cos(ang)  # new X coordinate
    y = xyz_ref[1] + R * sin(ang)  # new Y coordinate
    z = xyz_ref[2]  # new Z coordinate
    target_pose.setPos([x, y, z])

    # Move to the new target:
    robot.MoveL(target_pose)

# Trigger a program call at the end of the movement
robot.RunInstruction('Program_Done')

# Move back to the reference target:
robot.MoveL(target_pose)