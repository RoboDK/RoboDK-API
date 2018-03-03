
RoboDK API for Python
======================

Full package description on PyPi
https://pypi.python.org/pypi/robodk/

Read the [RoboDK API description](../README.md) for more information

Requirements
------------
- [Python](https://www.python.org/downloads/) (Python 2 and Python 3 supported)
- [RoboDK](https://robodk.com/download)

How to install
------------
RoboDK automatically uses the PYTHONPATH environment variable pointing to the /RoboDK/Python/ folder to use the robodk.py and robolink.py modules.

Alternatively, you can also install the RoboDK package for Python:
```
  # cd path-to-python/Scripts
  pip install robodk
```

Python Example
------------
```python
from robolink import *    # RoboDK's API
from robodk import *      # Math toolbox for robots

# Start the RoboDK API:
RDK = Robolink()

# Get the robot item by name:
robot = RDK.Item('Fanuc LR Mate 200iD', ITEM_TYPE_ROBOT)

# Get the reference target by name:
target = RDK.Item('Target 1')
target_pose = target.Pose()
xyz_ref = target_pose.Pos()

# Move the robot to the reference point:
robot.MoveJ(target)

# Draw a hexagon around the reference target:
for i in range(7):
    ang = i*2*pi/6 #ang = 0, 60, 120, ..., 360

    # Calculate the new position around the reference:
    x = xyz_ref[0] + R*cos(ang) # new X coordinate
    y = xyz_ref[1] + R*sin(ang) # new Y coordinate
    z = xyz_ref[2]              # new Z coordinate
    target_pos.setPos([x,y,z])

    # Move to the new target:
    robot.MoveL(target_pos)

# Trigger a program call at the end of the movement
robot.RunCode('Program_Done')

# Move back to the reference target:
robot.MoveL(target)
```
