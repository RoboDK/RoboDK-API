# This macro provides an example to extract the joints of a program. 
# The joints extracted take into account the rounding effect.
from robolink import *    # API to communicate with RoboDK
from robodk import *      # basic matrix operations
import sys
import os

# Set to False to have a more customized output as dictated by this script
FAST_SAVE = False

# Start the RoboDK API:
RDK = Robolink()

# Get the robot and the program available in the open station:
#robot = RDK.Item('', ITEM_TYPE_ROBOT_ARM)

# Option one, retrieve joint list as a matrix (not through a file):
prog = RDK.ItemUserPick('Select a Program', ITEM_TYPE_PROGRAM)


if not prog.Valid():
    print("No program selected")
    quit()
    
robot = prog.getLink(ITEM_TYPE_ROBOT)
ndofs = len(robot.Joints().list())

    
path_table = RDK.getParam("PATH_OPENSTATION") + "/" + prog.Name() + "-Table-"
path_table_csv = path_table + "1.csv"

count = 1
while os.path.isfile(path_table_csv) and count < 20:
    count = count + 1
    path_table_csv = path_table + str(count) + ".csv"


# Define the way we want to output the list of joints
Position = 1        # Only provide the joint position and XYZ values
Speed = 2           # Calculate speed (added to position)
SpeedAndAcceleration = 3 # Calculate speed and acceleration (added to position)
TimeBased = 4       # Make the calculation time-based (adds a time stamp added to the previous options)
TimeBasedFast = 5   # Make the calculation time-based and avoids calculating speeds and accelerations (adds a time stamp added to the previous options)

FLAGS = TimeBasedFast

STEP_MM = 0.01  # Step in mm
STEP_DEG = 0.01 # Step in deg
TIME_STEP = 0.01 # time step in seconds

if FAST_SAVE:
    FLAGS = TimeBased
    error_msg, joint_list, error_code = prog.InstructionListJoints(STEP_MM, STEP_DEG, path_table_csv, flags=FLAGS, time_step=TIME_STEP)
    print(error_msg)
    quit()

# If not FAST_SAVE
FLAGS = TimeBasedFast    
error_msg, joint_list, error_code = prog.InstructionListJoints(STEP_MM, STEP_DEG, None, flags=FLAGS, time_step=TIME_STEP)
print(error_msg)

def diff(j1, j2, dt, dofs):
    """Returns True if joints 1 and joints 2 are different"""
    if j2 is None or dt <= 0:
        return [0]*dofs
    
    res = []
    for j1,j2 in zip(j1,j2):
        res.append((j1-j2)/dt)
    
    return res
    
    
joints_last = None
speeds_last = None
t_last = None

print("Saving joints to file: " + path_table_csv)
with open(path_table_csv,'w') as fid:
    joints_header = ",".join(["Joint J" + str(i+1) for i in range(ndofs)])
    speeds_header = ",".join(["Speed J" + str(i+1) for i in range(ndofs)])
    accel_header = ",".join(["Accel J" + str(i+1) for i in range(ndofs)])
    t_now = 0
    
    fid.write("Time (s)," + joints_header + ",,Error,Step (mm), Step (deg), Move ID,,Time (s)," + speeds_header + ",,Time (s)," + accel_header)
    fid.write("\n")
    for line in joint_list:
        joints = line[:ndofs]
        error = line[ndofs]
        step_mm = line[ndofs+1]
        step_deg = line[ndofs+2]
        move_id = line[ndofs+3]
        t_delta = line[ndofs+4]
        t_now += t_delta        
        
        # Miscelaneous: Error,Step (mm), Step (deg), Move ID
        misc_str = "%.1f,%.3f,%.3f,%.0f" % (error, step_mm, step_deg, move_id)

        # Calculate speeds
        speeds = diff(joints, joints_last, t_delta, ndofs)
        
        # Calcualte accelerations
        accels = diff(speeds, speeds_last, t_delta, ndofs)            

        print('Time +S: %.3f s' % t_now)
        joints_str = ",".join(["%.6f" % x for x in joints])
        speeds_str = ",".join(["%.6f" % x for x in speeds])
        accels_str = ",".join(["%.6f" % x for x in accels])
        
        time_str = ("%.6f," % t_now)
        fid.write(time_str + joints_str + ",," + misc_str + ",," + time_str + speeds_str + ",," + time_str + accels_str)
        fid.write("\n")
        t_last = t_now
        joints_last = joints
        speeds_last = speeds
        
        


print(error_msg)












