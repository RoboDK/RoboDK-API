# This macro will record the robot joints (in degrees) in a CSV file (including a time stamp in seconds). This file avoids recording the same joints twice.
# Tip: Use the script JointsPlayback.py to move along the recorded joints

from robolink import *    # API to communicate with RoboDK
from robodk import *      # basic matrix operations
from time import gmtime, strftime

RDK = Robolink()

# Ask the user to select a robot arm (mechanisms are ignored)
robot = RDK.ItemUserPick('Select a robot',ITEM_TYPE_ROBOT_ARM)
if not robot.Valid():
    raise Exception("Robot is not available")

# Generate a file in the same folder where we have the RDK file
file_path = RDK.getParam('PATH_OPENSTATION') + '/joints-' + strftime("%Y-%m-%d %H-%M-%S", gmtime()) + '.csv'

def joints_changed(j1, j2, tolerance=0.0001):
    """Returns True if joints 1 and joints 2 are different"""
    if j1 is None or j2 is None:
        return True
        
    for j1,j2 in zip(j1,j2):
        if abs(j1-j2) > tolerance:
            return True
            
    return False

# Infinite loop to record robot joints
joints_last = None
print("Recording robot joints to file: " + file_path)
with open(file_path,'a') as fid:
    tic()
    while True:
        time = toc()
        joints = robot.Joints().list()
        if joints_changed(joints, joints_last):
            print('Time (s): ' + str(time))
            fid.write(str(joints)[1:-1] + (", %.3f" % time) + '\n')
            joints_last = joints
            pause(0.01)


            
