# This macro shows how to load a list of XYZ points including speed
# The list must be provided as X,Y,Z,Speed. Speed is optional. Units must be mm and mm/s respectively
# The file can be loaded as a program in the GUI or directly simulated.

from robodk.robodialogs import *
from robodk.robofileio import *
from robodk.robolink import *

#----------------------------
# Global variables:

# LOAD_AS_PROGRAM flag:
# Set to True to generate a program in the UI: we can modify targets manually and properly see the program
# Set to False, it will simulate or generate the robot program directly when running the macro
LOAD_AS_PROGRAM = True

# Set the name of the reference frame to place the targets:
#REFERENCE_NAME = 'Reference CSV'

# Set the name of the reference target (optional)
# (orientation will be kept constant with respect to this target)
#TARGET_NAME = 'Home'

#---------------------------
# Start the RoboDK API
RDK = Robolink()

# Ask the user to pick a file:
rdk_file_path = RDK.getParam("PATH_OPENSTATION")
path_file = getOpenFile(rdk_file_path + "/")
if not path_file:
    print("Nothing selected")
    quit()

# Get the program name from the file path
program_name = getFileName(path_file)

# Load the CSV file as a list of list [[x,y,z,speed],[x,y,z,speed],...]
data = LoadList(path_file)

# Delete previously generated programs that follow a specific naming
#list_names = RDK.ItemList(False)
#for item_name in list_names:
#    if item_name.startswith('Auto'):
#        RDK.Item(item_name).Delete()

# Select the robot (the popup is diplayed only if there are 2 or more robots)
robot = RDK.ItemUserPick('Select a robot', ITEM_TYPE_ROBOT)
if not robot.Valid():
    raise Exception("Robot not selected or not valid")
    quit()

# Get the reference frame to generate the path
#frame = RDK.Item(REFERENCE_NAME,ITEM_TYPE_FRAME)
frame = robot.getLink(ITEM_TYPE_FRAME)
if not frame.Valid():
    frame = robot.Parent()

if not frame.Valid():
    raise Exception("Reference frame not found")

#----------
# Use a reference/home target as a reference orientation (optional)
#target = RDK.Item(TARGET_NAME, ITEM_TYPE_TARGET)
#if not target.Valid():
#    raise Exception("Home target is not valid. Set a home target named: %s" % TARGET_NAME)

# Set the robot to the home position
# robot.setJoints(target.Joints())

# Get the pose reference from the home target
pose_ref = robot.Pose()

if LOAD_AS_PROGRAM:
    # Add a new program
    program = RDK.AddProgram(program_name, robot)

    # Turn off rendering (faster)
    RDK.Render(False)

    # Speed up by not showing the instruction:
    program.ShowInstructions(False)

    # Remember the speed so that we don't set it with every instruction
    current_speed = None
    target = None

    # Very important: Make sure we set the reference frame and tool frame so that the robot is aware of it
    program.setPoseFrame(frame)
    program.setPoseTool(robot.PoseTool())

    # Iterate through all the points
    for i in range(len(data)):
        x, y, z, _ = data[i]
        if type(x) is str or type(y) is str or type(z) is str:
            print("Ignored data row: " + str(data[i]))
            continue

        pi = pose_ref
        pi.setPos(data[i])

        # Update speed if there is a 4th column
        if len(data[i]) >= 3:
            speed = data[i][3]
            # Update the program if the speed is different than the previously set speed
            if type(speed) is not str and speed != current_speed:
                program.setSpeed(speed)
                current_speed = speed

        target = RDK.AddTarget('T%i' % i, frame)
        target.setPose(pi)
        pi = target

        # Add a linear movement (with the exception of the first point which will be a joint movement)
        if i == 0:
            program.MoveJ(pi)
        else:
            program.MoveL(pi)

        # Update from time to time to notify the user about progress
        if i % 100 == 0:
            program.ShowTargets(False)
            RDK.ShowMessage("Loading %s: %.1f %%" % (program_name, 100 * i / len(data)), False)
            RDK.Render()

    program.ShowTargets(False)

else:
    # Very important: Make sure we set the reference frame and tool frame so that the robot is aware of it
    robot.setPoseFrame(frame)
    robot.setPoseTool(robot.PoseTool())

    # Remember the speed so that we don't set it with every instruction
    current_speed = None

    # Iterate through all the points
    for i in range(len(data)):
        pi = pose_ref
        pi.setPos(data[i][0:3])

        # Update speed if there is a 4th column
        if len(data[i]) >= 3:
            speed = data[i][3]
            # Update the program if the speed is different than the previously set speed
            if type(speed) != str and speed != current_speed:
                robot.setSpeed(speed)
                current_speed = speed

        # Add a linear movement (with the exception of the first point which will be a joint movement)
        if i == 0:
            robot.MoveJ(pi)
        else:
            robot.MoveL(pi)

        # Update from time to time to notify the user about progress
        #if i % 200 == 0:
        RDK.ShowMessage("Program %s: %.1f %%" % (program_name, 100 * i / len(data)), False)

RDK.ShowMessage("Done", False)
print("Done")
