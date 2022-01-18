# This macro provides an example to convert a program to another program with joint splitting
# The joints extracted take into account the rounding effect.
from robolink import *    # API to communicate with RoboDK
from robodk import *      # basic matrix operations
import sys

# Start the RoboDK API:
RDK = Robolink()

# Get the robot and the program available in the open station:
robot = RDK.Item('', ITEM_TYPE_ROBOT_ARM)


# First, check if we are getting a list of joints through the command line:
if len(sys.argv) >= 2:
    joint_list = Mat(LoadList(sys.argv[1]))

#elif True:
#    joint_list = Mat(LoadList(r'joints.csv'))
    
else:
    # Option one, retrieve joint list as a matrix (not through a file):
    prog = RDK.ItemUserPick('Select a Program', ITEM_TYPE_PROGRAM)
    
    # Define the way we want to output the list of joints
    Position = 1        # Only provide the joint position and XYZ values
    Speed = 2           # Calculate speed (added to position)
    SpeedAndAcceleration = 3 # Calculate speed and acceleration (added to position)
    TimeBased = 4       # Make the calculation time-based (adds a time stamp added to the previous options)
    TimeBasedFast = 5   # Make the calculation time-based and avoids calculating speeds and accelerations (adds a time stamp added to the previous options)
    
    STEP_MM = 1
    STEP_DEG = 1
    #FLAGS = TimeBasedFast
    FLAGS = Position
    TIME_STEP = 0.005 # time step in seconds
    status_msg, joint_list, status_code = prog.InstructionListJoints(STEP_MM, STEP_DEG, flags=FLAGS, time_step=TIME_STEP)

    # Option two, write the joint list to a file (recommended if step is very small
    #STEP_MM = 0.5
    #STEP_DEG = 0.5
    #status_msg, joint_list, status_code = prog.InstructionListJoints(STEP_MM, STEP_DEG, 'C:/Users/Albert/Desktop/file.txt')
    
    # Status code is negative if there are errors in the program
    print(joint_list.tr())    
    print("Size: " + str(len(joint_list)))
    print("Status code:" + str(status_code))
    print("Status message: " + status_msg)

    if int(status_code) < 0:
        ShowMessage("Program problems: " + status_msg)

# Create the program
ndofs = len(robot.Joints().list())
p = RDK.AddProgram(prog.Name()+"Jnts", robot)
RDK.Render()
for j in joint_list:
    j = j[:ndofs]
    print(j)
    p.MoveJ(j)



