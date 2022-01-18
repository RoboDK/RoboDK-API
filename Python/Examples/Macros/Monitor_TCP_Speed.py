# This script calculates the speed of the TCP in mm/s
# Tip: Use the script JointsPlayback.py to move along the recorded joints

# force monitoring the real robot
FORCE_REAL_ROBOT = False

from robolink import *    # API to communicate with RoboDK
from robodk import *      # basic matrix operations
from time import gmtime, strftime
import time

# Connect to RoboDK
RDK = Robolink()

# Ask the user to select a robot arm (mechanisms are ignored)
robot = RDK.ItemUserPick('Select a robot',ITEM_TYPE_ROBOT_ARM)
if not robot.Valid():
    raise Exception("Robot is not available")

if FORCE_REAL_ROBOT:
    if robot.Connect() == 0:
        raise Exception("Error connecting to robot")
    
# Generate a file in the same folder where we have the RDK file
#file_path = RDK.getParam('PATH_OPENSTATION') + '/joints-' + strftime("%Y-%m-%d %H-%M-%S", gmtime()) + '.csv'

def joints_changed(j1, j2, tolerance=0.0001):
    """Returns True if joints 1 and joints 2 are different"""
    if j1 is None or j2 is None:
        return True
        
    for j1,j2 in zip(j1,j2):
        if abs(j1-j2) > tolerance:
            return True
            
    return False


joints_last = None
t_last = None
tcp_xyz_last = None

print("Move the robot to calculate the TCP speed")

# Infinite loop to calculate speed
while True:
    # If we are connected to the real robot, this retrieves the position of the real robot 
    # (blocks until it receives an update from the real robot)
    joints = robot.Joints().list()
    if joints_changed(joints, joints_last):
        # Get the TCP with respect to the coordinate system 
        # (the robot position was just updated from the real robot using Joints())
        tcp_xyz = robot.Pose().Pos()
        x,y,z = tcp_xyz
        print("TCP position [X,Y,Z] (mm): [%.3f,%.3f,%.3f]" % (x,y,z))
        
        t = time.time()
        if t_last is not None: # Skip the first update            
            # Calculate delta time (s) and delta travel (mm)
            d_time = t - t_last
            # d_time = d_time * RDK.SimulationSpeed() # adjust for real time when simulating
            d_move = norm(subs3(tcp_xyz, tcp_xyz_last))
            if d_time > 0:
                speed = d_move / d_time
                print("TCP speed (mm/s): %.1f" % speed)
        
        joints_last = joints
        tcp_xyz_last = tcp_xyz
        t_last = t
        
        #pause(0.01)
