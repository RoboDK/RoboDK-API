from robolink import *    # API to communicate with RoboDK
from robodk import *      # basic matrix operations
import os                 # Path operations
 
# Get the current working directory
CWD = os.path.dirname(os.path.realpath(__file__))
 
# Start RoboDK if it is not running and link to the API
RDK = Robolink()
# optional: provide the following arguments to run behind the scenes
#RDK = Robolink(args='/NOSPLASH /NOSHOW /HIDDEN')
 
# Get the calibrated station (.rdk file) or robot file (.robot):
# Tip: after calibration, right click a robot and select "Save as .robot"
calibration_file = CWD + '/KUKA-KR6.rdk'
 
# Get the program file:
file_program = CWD + '/Prog1.src'
 
# Load the RDK file or the robot file:
calib_item = RDK.AddFile(calibration_file)
if not calib_item.Valid():
    raise Exception("Something went wrong loading " + calibration_file)
 
# Retrieve the robot (no popup if there is only one robot):
robot = RDK.ItemUserPick('Select a robot to filter', ITEM_TYPE_ROBOT)
if not robot.Valid():
    raise Exception("Robot not selected or not available")
 
# Activate accuracy
robot.setAccuracyActive(1)
# Filter program: this will automatically save a program copy
# with a renamed file depending on the robot brand
status, summary = robot.FilterProgram(file_program)
 
if status == 0:
    print("Program filtering succeeded")
    print(summary)
    calib_item.Delete()
    RDK.CloseRoboDK()
else:
    print("Program filtering failed! Error code: %i" % status)
    print(summary)    
    RDK.ShowRoboDK()


