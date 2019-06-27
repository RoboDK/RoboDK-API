# This macro provides an example to extract the joints of a program. 
# The joints extracted take into account the rounding effect.
from robolink import *    # API to communicate with RoboDK
from robodk import *      # basic matrix operations

# Start the RoboDK API:
RDK = Robolink()

# Get the robot and the program available in the open station:
# robot = RDK.Item('', ITEM_TYPE_ROBOT)
prog = RDK.ItemUserPick('Select a Program', ITEM_TYPE_PROGRAM)
robot = prog.getLink(ITEM_TYPE_ROBOT)

# Get the list of instructions (for internal use)
#inslist, status = prog.InstructionList()
#print(inslist.tr())
#raise Exception('Stopped')

# Get the list of joints for the program prog
# set the start smoothing value to 50 mm (this can be modified by the program)
# robot.setZoneData(50)

# Option one, retrieve joint list as a matrix (not through a file:
STEP_MM = 1
STEP_DEG = 1
error_msg, joint_list, error_code = prog.InstructionListJoints(STEP_MM, STEP_DEG)

# Option two, write the joint list to a file (recommended if step is very small
STEP_MM = 0.5
STEP_DEG = 0.5
#error_msg, joint_list, error_code = prog.InstructionListJoints(STEP_MM, STEP_DEG, 'C:/Users/Albert/Desktop/file.txt')

print(joint_list)
print(error_msg)

# detect if joint_list is a file or a list
if type(joint_list) is str:
    print('Program saved to %s' % joint_list)
else:
    print('Showing joint sequencence in RoboDK')
    robot.ShowSequence(joint_list[:6,:])
