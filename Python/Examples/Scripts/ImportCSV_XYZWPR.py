# This macro can load CSV files from Denso programs in RoboDK.
# Supported types of files are:
#  1-Tool data : Tool.csv
#  2-Work object data: Work.csv
#  3-Target data: P_Var.csv
# This macro can also filter a given targets file

# Type help("robodk.robolink") or help("robodk.robomath") for more information
# Press F5 to run the script
# Visit: http://www.robodk.com/doc/PythonAPI/
# For RoboDK API documentation

from robodk.robolink import *  # API to communicate with RoboDK
from robodk.robomath import *  # Robot toolbox
from robodk.robodialogs import *
from robodk.robofileio import *

# Start communication with RoboDK
RDK = Robolink()

# Ask the user to select the robot (ignores the popup if only
ROBOT = RDK.ItemUserPick('Select a robot', ITEM_TYPE_ROBOT)

# Check if the user selected a robot
if not ROBOT.Valid():
    quit()

# Automatically retrieve active reference and tool
FRAME = ROBOT.getLink(ITEM_TYPE_FRAME)
TOOL = ROBOT.getLink(ITEM_TYPE_TOOL)

#FRAME = RDK.ItemUserPick('Select a reference frame', ITEM_TYPE_FRAME)
#TOOL = RDK.ItemUserPick('Select a tool', ITEM_TYPE_TOOL)

if not FRAME.Valid() or not TOOL.Valid():
    raise Exception("Select appropriate FRAME and TOOL references")


# Function to convert XYZWPR to a pose
# Important! Specify the order of rotation
def xyzwpr_to_pose(xyzwpr):
    x, y, z, rx, ry, rz = xyzwpr
    return transl(x, y, z) * rotz(rz * pi / 180) * roty(ry * pi / 180) * rotx(rx * pi / 180)
    #return transl(x,y,z)*rotx(rx*pi/180)*roty(ry*pi/180)*rotz(rz*pi/180)
    #return KUKA_2_Pose(xyzwpr)


# csv_file = 'C:/Users/Albert/Desktop/Var_P.csv'
csv_file = getOpenFileName(RDK.getParam('PATH_OPENSTATION'))

# Specify file codec
codec = 'utf-8'  #'ISO-8859-1'


# Load P_Var.CSV data as a list of poses, including links to reference and tool frames
def load_targets(strfile):
    csvdata = LoadList(strfile, ',', codec)
    poses = []
    idxs = []
    for i in range(0, len(csvdata)):
        x, y, z, rx, ry, rz = csvdata[i][0:6]
        poses.append(xyzwpr_to_pose([x, y, z, rx, ry, rz]))
        #idxs.append(csvdata[i][6])
        idxs.append(i)

    return poses, idxs


# Load and display Targets from P_Var.CSV in RoboDK
def load_targets_GUI(strfile):
    poses, idxs = load_targets(strfile)
    program_name = getFileName(strfile)
    program_name = program_name.replace('-', '_').replace(' ', '_')
    program = RDK.Item(program_name, ITEM_TYPE_PROGRAM)
    if program.Valid():
        program.Delete()
    program = RDK.AddProgram(program_name, ROBOT)
    program.setFrame(FRAME)
    program.setTool(TOOL)
    ROBOT.MoveJ(ROBOT.JointsHome())

    for pose, idx in zip(poses, idxs):
        name = '%s-%i' % (program_name, idx)
        target = RDK.Item(name, ITEM_TYPE_TARGET)
        if target.Valid():
            target.Delete()
        target = RDK.AddTarget(name, FRAME, ROBOT)
        target.setPose(pose)

        try:
            program.MoveJ(target)
        except:
            print('Warning: %s can not be reached. It will not be added to the program' % name)


def load_targets_move(strfile):
    poses, idxs = load_targets(strfile)

    ROBOT.setFrame(FRAME)
    ROBOT.setTool(TOOL)

    ROBOT.MoveJ(ROBOT.JointsHome())

    for pose, idx in zip(poses, idxs):
        try:
            ROBOT.MoveJ(pose)
        except:
            RDK.ShowMessage('Target %i can not be reached' % idx, False)


# Force just moving the robot after double clicking
#load_targets_move(csv_file)
#quit()

# Recommended mode of operation:
# 1-Double click the python file creates a program in RoboDK station
# 2-Generate program generates the program directly

MAKE_GUI_PROGRAM = False

ROBOT.setFrame(FRAME)
ROBOT.setTool(TOOL)

if RDK.RunMode() == RUNMODE_SIMULATE:
    MAKE_GUI_PROGRAM = True
    # MAKE_GUI_PROGRAM = mbox('Do you want to create a new program? If not, the robot will just move along the tagets', 'Yes', 'No')
else:
    # if we run in program generation mode just move the robot
    MAKE_GUI_PROGRAM = False

if MAKE_GUI_PROGRAM:
    RDK.Render(False)  # Faster if we turn render off
    load_targets_GUI(csv_file)
else:
    load_targets_move(csv_file)
