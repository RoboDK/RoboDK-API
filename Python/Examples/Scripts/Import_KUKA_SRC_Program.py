# This macro shows how to load a KUKA SRC file
# PTP movements with joint coordinates and LIN movements with Cartesian information (XYZABC) will be imported as a program.
# This macro also supports defining the tool and the base inline and changing the speed using the VEL.CP global variable

## Example program:
# DEF Milling ( )
#
# $BASE = {FRAME: X 0.000,Y -1000.000,Z 0.000,A 0.000,B 0.000,C 0.000}
# $TOOL = {FRAME: X 466.604,Y -4.165,Z 109.636,A -0.000,B 90.000,C 0.000}
#
# $VEL.CP = 1.00000
#
# PTP {A1 107.78457,A2 -44.95260,A3 141.64681,A4 107.66839,A5 -87.93467,A6 6.37710}
# LIN {X -0.000,Y -0.000,Z 6.350,A -180.000,B 0.000,C -180.000}
#
# $VEL.CP = 0.02117
# LIN {X 276.225,Y 0.000,Z 6.350,A 180.000,B 0.000,C -180.000}
# LIN {X 276.225,Y 323.850,Z 6.350,A -160.000,B 0.000,C 180.000}
# LIN {X -0.000,Y 323.850,Z 6.350,A -180.000,B -0.000,C -180.000}
# LIN {X -0.000,Y -0.000,Z 6.350,A -180.000,B 0.000,C -180.000}
# $VEL.CP = 1.00000
# LIN {X -0.000,Y -0.000,Z 106.350,A -180.000,B 0.000,C -180.000}
#
# END

from robodk.robomath import *  # Robot toolbox
from robodk.robodialogs import *
from robodk.robofileio import *
from robodk.robolink import *

#---------------------------
# Start the RoboDK API
RDK = Robolink()

# Ask the user to pick an SRC file:
rdk_file_path = RDK.getParam("PATH_OPENSTATION")
src_file_path = getOpenFileName(rdk_file_path + "/")
if not src_file_path:
    print("Nothing selected")
    quit()

# Get the program name from the file path
program_name = getFileName(src_file_path)
print("Loading program: " + program_name)

if not src_file_path.lower().endswith(".src"):
    raise Exception("Invalid file selected. Select an SRC file.")


def GetValues(line):
    """Get all the numeric values from a line"""
    # LIN {X 1671.189,Y -562.497,Z -243.070,A 173.363,B -8.525,C -113.306} C_DIS
    line = line.replace(",", " ")
    line = line.replace("}", " ")
    values = line.split(" ")

    list_values = []
    for value in values:
        try:
            value = float(value)
        except:
            continue

        list_values.append(value)

    return list_values


# Ask the user to select a robot (if more than a robot is available)
robot = RDK.ItemUserPick('Select a robot', ITEM_TYPE_ROBOT)
if not robot.Valid():
    raise Exception("Robot not selected or not valid")

# Get the active reference frame
frame = robot.getLink(ITEM_TYPE_FRAME)
if not frame.Valid():
    # If there is no active reference frame, use the robot base
    frame = robot.Parent()

# Get the active tool frame
tool = robot.getLink(ITEM_TYPE_TOOL)

# Add a new program
program = RDK.AddProgram(program_name, robot)

# Turn off rendering (faster)
RDK.Render(False)

# Speed up by not showing the instruction:
program.ShowInstructions(False)

# Open the file and iterate through each line
with open(src_file_path) as f:
    count = 0
    for line in f:
        # Remove empty characters:
        line = line.strip()
        print("Loading line: " + line)

        # Get all the numeric values in order
        values = GetValues(line)

        # Increase the counter
        count = count + 1

        # Update TCP speed (KUKA works in m/s, RoboDK works in mm/s)
        if line.startswith("$VEL.CP"):
            program.setSpeed(values[0]*1000)
            continue
            
        # Check operations that involve a pose
        if len(values) < 6:
            print("Warning! Invalid line: " + line)
            continue

        # Check what instruction we need to add:
        if line.startswith("LIN"):
            target = RDK.AddTarget('T%i'% count, frame)
            
            # Check if we have external axes information, if so, provided it to joints E1 to En
            if len(values) > 6:
                target.setJoints([0,0,0,0,0,0] + values[6:])
                
            target.setPose(KUKA_2_Pose(values[:6]))
            program.MoveL(target)

        # Check PTP move
        elif line.startswith("PTP"):
            target = RDK.AddTarget('T%i'% count, frame)
            target.setAsJointTarget()
            target.setJoints(values)
            program.MoveJ(target)

        # Set the tool
        elif line.startswith("$TOOL"):
            pose = KUKA_2_Pose(values[:6])
            tool = robot.AddTool(pose, "SRC TOOL")
            program.setTool(tool)

        # Set the reference frame
        elif line.startswith("$BASE"):
            frame = RDK.AddFrame("SRC BASE", robot.Parent())
            frame.setPose(KUKA_2_Pose(values[:6]))
            program.setFrame(frame)

# Hide the targets
program.ShowTargets(False)

# Show the instructions
program.ShowInstructions(True)

RDK.ShowMessage("Done", False)
print("Done")
