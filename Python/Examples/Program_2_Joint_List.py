# API to communicate with RoboDK
from robolink import *    

# Link to the RoboDK API
RDK = Robolink()

# Get the robot and the program available in the open station:
prog = RDK.ItemUserPick('', ITEM_TYPE_PROGRAM)
if not prog.Valid():
    quit()

# Get the robot linked to the program
robot = prog.getLink(ITEM_TYPE_ROBOT)

# Option one: retrieve joint list as a matrix (not through a file:
STEP_MM = 1
STEP_DEG = 1
error_msg, joint_list, error_code = prog.InstructionListJoints(STEP_MM, STEP_DEG,None, COLLISION_OFF, 2)

# Option two: write the joint list to a file (faster. Recommended if step is very small or a large program is used)
#STEP_MM = 0.05
#STEP_DEG = 0.05
#error_msg, joint_list, error_code = prog.InstructionListJoints(STEP_MM, STEP_DEG, 'C:/Users/Albert/Desktop/file.txt', COLLISION_OFF, 2)

# Display error messages (if any)
print(error_msg)

# detect if joint_list is a file or a list
if type(joint_list) is str:
    print('Program saved to %s' % joint_list)
    
else:
    # Display the result
    print(joint_list.tr())
    
    # Show the sequence in RoboDK
    print('Showing joint sequencence in RoboDK')
    robot.ShowSequence(joint_list[:6,:])
