# This example shows how to simulate a program call passing arguments
# You can generate program calls using APT or Gcode command "CALL"
# An example APT file is available here:
# C:/RoboDK/Library/ExampleAPT.apt
from robodk.robolink import *  # RoboDK API
from robodk.robomath import *  # Robot toolbox

RDK = Robolink()

# Simulated time, in seconds
TimeDrill = 5

# Retrieve the robot (needed if we want to move the robot given passed parameters
robot = RDK.Item('', ITEM_TYPE_ROBOT)

import sys

# Request at least 3 arguments (the first one is the program file, so ignore it
# Otherwise we'll ignore it
if len(sys.argv) > 3:
    input_values = []
    for i in range(1, len(sys.argv)):
        input_values.append(float(sys.argv[i].strip()))

    # Assume we got at least 3 parameters as X,Y,Z
    x = input_values[0]
    y = input_values[1]
    z = input_values[2]

    # Display message in the status bar of RoboDK
    msg = "Calling CallNC(%s)" % (str(input_values)[1:-1])
    RDK.ShowMessage(msg, False)
    print(msg)

    # Retrieve the robot position at the moment of the call:
    pose = robot.Pose()
    # Update the pose with the new XYZ coordinates
    pose.setPos([x, y, z])
    # Move the robot to the desired position
    robot.MoveL(pose)

    # Simulate the pause (apply real time ratio)
    pause(TimeDrill / RDK.SimulationSpeed())
