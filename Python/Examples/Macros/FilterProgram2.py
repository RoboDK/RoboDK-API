# This example shows how to filter a program to increase accuracy.
# The robot needs to be calibrated to be able to filter programs
# More information here:
# https://robodk.com/doc/en/Robot-Calibration-LaserTracker.html#FilterProgAPI-LT

from robodk.robolink import *  # API to communicate with RoboDK
from robodk.robomath import *  # basic matrix operations
import os  # Path operations

# Get the current working directory
CWD = os.path.dirname(os.path.realpath(__file__))

# Start RoboDK if it is not running and link to the API
RDK = Robolink()
RDK.ShowRoboDK()

# optional: provide the following arguments to run behind the scenes
#RDK = Robolink(args='/NOSPLASH /NOSHOW /HIDDEN')

# Get the calibrated station (.rdk file) or robot file (.robot):
# Tip: after calibration, right click a robot and select "Save as .robot"
calibration_file = CWD + '/RoboDK Project File.rdk'

# Get the program file:
#file_program = CWD + '/Prog1.src'
file_program = CWD + '/program_in.src'

#quit()

# Load the RDK file or the robot file:
station = RDK.AddFile(calibration_file)
if not station.Valid():
    raise Exception("Something went wrong loading " + calibration_file)

# Retrieve the robot (no popup if there is only one robot):
robot = RDK.Item('KUKA KR 210-2', ITEM_TYPE_ROBOT)
if not robot.Valid():
    raise Exception("Robot not selected or not available")

# Activate accuracy
robot.setAccuracyActive(1)

# Force a specific tool and reference frame given XYZABC values
robot.setPoseFrame(KUKA_2_Pose([0, 0, 150, 0, 0, 0]))
robot.setPoseTool(KUKA_2_Pose([558.165, 0.000, 176.431, 0.000, 90.000, 0.000]))

# Filter program: this will automatically save a program copy
# with a renamed file depending on the robot brand
status, summary = robot.FilterProgram(file_program)

if status == 0:
    print("Program filtering succeeded")
    print(summary)
    RDK.ShowMessage(summary)
    #station.Delete()
    #RDK.CloseRoboDK()

else:
    print("Program filtering failed! Error code: %i" % status)
    print(summary)
    RDK.ShowRoboDK()
