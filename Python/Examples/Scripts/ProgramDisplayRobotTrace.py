# This script allows you to display the robot in multiple locations along a program
from robolink import *    # API to communicate with RoboDK
from robodk import *      # basic matrix operations
import sys

# Maximum number of robots to display
N_ROBOTS = 100

# Minimum time space in seconds
MIN_TIME_STEP = 1

# Reachable display timeouts in milliseconds
timeout_display_ghost = 3600*1000

#----------------------------------------------
# Start the RoboDK API:
RDK = Robolink()

# Option one, retrieve joint list as a matrix (not through a file):
prog = RDK.ItemUserPick('Select a Program', ITEM_TYPE_PROGRAM)

if not prog.Valid():
    # nothing selected or no program available
    quit()
    
robot = prog.getLink(ITEM_TYPE_ROBOT)
if not robot.Valid():
    RDK.ShowMessage("Invalid robot")
    quit()

# Calculate delta time to display robots
prog_stats = prog.Update()
time_estimate = prog_stats[1]
TIME_STEP = max(MIN_TIME_STEP, time_estimate / N_ROBOTS)

# Define the way we want to output the list of joints
Position = 1        # Only provide the joint position and XYZ values
Speed = 2           # Calculate speed (added to position)
SpeedAndAcceleration = 3 # Calculate speed and acceleration (added to position)
TimeBased = 4       # Make the calculation time-based (adds a time stamp added to the previous options)
TimeBasedFast = 5   # Make the calculation time-based and avoids calculating speeds and accelerations (adds a time stamp added to the previous options)

STEP_MM = 1
STEP_DEG = 1
FLAGS = TimeBasedFast       
status_msg, joint_list, status_code = prog.InstructionListJoints(STEP_MM, STEP_DEG, flags=FLAGS, time_step=TIME_STEP)

# Option two, write the joint list to a file (recommended if step is very small
#STEP_MM = 0.5
#STEP_DEG = 0.5
#status_msg, joint_list, status_code = prog.InstructionListJoints(STEP_MM, STEP_DEG, 'C:/Users/Albert/Desktop/file.txt')

# Status code is negative if there are errors in the program
print("Status code:" + str(status_code))
print("Status message: " + status_msg)
    
print(joint_list.tr())    
print("Size: " + str(len(joint_list)))


# Show as a sequence with a slider
if False:
    # detect if joint_list is a file or a list
    if type(joint_list) is str:
        print('Program saved to %s' % joint_list)
    else:
        print('Showing joint sequencence in RoboDK')
        robot.ShowSequence(joint_list[:6,:])
    quit()

# Show as ghost robot
joints = []
for j in joint_list:
    joints.append(j)

# Display "ghost" tools in RoboDK
Display_Default = 2
Display_Normal = 2
Display_Green = 3
Display_Red = 4

Display_Invisible = 0*64 # or 0
Display_NotActive = 0*128 # or 0
Display_Joints = 2096 # Important flag to display the robot instead of joints
Display_Options = Display_Invisible + Display_NotActive + Display_Joints


robot.ShowSequence([]) # reset
robot.ShowSequence(joints, Display_Options+Display_Normal, timeout_display_ghost)
                
    
    
    
