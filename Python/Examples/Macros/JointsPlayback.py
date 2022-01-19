# This macro will move the robot along a list of joints in a CSV file
# Tip: Use the macro MonitorJoints.py to record a CSV file that can be loaded by this script

TIME_MATCH = False
MEASURE_COLLISIONS = False

from robodk.robolink import *    # API to communicate with RoboDK
from robodk.robomath import *    # basic matrix operations
from robodk.robofileio import *
from time import gmtime, strftime

RDK = Robolink()

# Turn off collision checking
RDK.setCollisionActive(COLLISION_OFF)

# Ask the user to select a robot arm (mechanisms are ignored)
robot = RDK.ItemUserPick('Select a robot', ITEM_TYPE_ROBOT_ARM)
if not robot.Valid():
    raise Exception("Robot is not available")

# Generate a file in the same folder where we have the RDK file
folder_path = RDK.getParam('PATH_OPENSTATION')

# Ask the user to select a file
#filename = getOpenFile(path_preference=folder_path, strfile='', strtitle='Open CSV file ...', defaultextension='.csv', filetypes=[('CSV files', '*.csv'), ('All files', '*.*')])
filename = RDK.getParam('PATH_OPENSTATION') + '/joints-test.csv'

# Load the CSV file as a list of lists (each row is a list)
csvdata = LoadList(filename)

# Iterate through each row
total_collision_time = 0
max_collision_time = 0
count = 0
last_row = None
for row in csvdata:
    joints = row

    # Match timings
    if TIME_MATCH and last_row is not None:
        t_step = row[-1] - last_row[-1]
        pause(t_step)

    robot.setJoints(row)

    lastrow = row

    # Measure collision time
    if MEASURE_COLLISIONS:
        ncol = RDK.Collisions()
        collision_time = int(RDK.Command("CollisionCalcTime"))

        total_collision_time = total_collision_time + collision_time
        count = count + 1
        max_collision_time = max(max_collision_time, collision_time)
        time_average = total_collision_time / count
        msg = "Collision time (ms):    Max: %i | Average: %.1f | Last: %i" % (max_collision_time, time_average, collision_time)
        RDK.ShowMessage(msg, False)
        print(msg)
