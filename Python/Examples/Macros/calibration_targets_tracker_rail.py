# This scripts allows creating points to calibrate a rail (1 to 3 axis rail, with a robot mounted on it or not)
from robodk.robolink import *  # API to communicate with robodk
from robodk.robomath import *  # basic matrix operations
from robodk.robodialogs import *
from random import uniform
import sys  # to exit the script without errors (sys.exit(0))
import re  # to convert a string list into a list of values

# Default calibration steps
CALIB_STEPS = [20, 2, 4]
TCP_PREFIX = 'CalibTool'
TARGET_PREFIX = 'CalibTarget'

# Connect to RoboDK
RDK = Robolink()

# Ask user to select a robot to calibrate
robot = RDK.ItemUserPick("Select a robot or rail to calibrate", ITEM_TYPE_ROBOT)

# Retrieve parent robot
parent_robot = robot.getLink(ITEM_TYPE_ROBOT)
if robot != parent_robot:
    print("User selected a rail linked to a robot")

robot = parent_robot

joints_ref = robot.Joints().list()
lim_inf, lim_sup, type = robot.JointLimits()
lim_inf = lim_inf.list()
lim_sup = lim_sup.list()
ndofs = len(lim_inf)
ndofs_ext = ndofs

# Retrieve joint indexs
id_from = 0
id_to = ndofs
if ndofs_ext > 3:
    ndofs_ext = ndofs_ext - 6
    id_from = 6
    id_to = ndofs
    print("Using robot + rail to calibrate")

if ndofs_ext == 0 or ndofs_ext > 4:
    RDK.ShowMessage("Invalid robot selected: select a rail or a robot synchronized with a rail")
    quit()

lim_inf_ext = lim_inf[id_from:id_to]
lim_sup_ext = lim_sup[id_from:id_to]

lim_inf_ext = [round(elem, 0) for elem in lim_inf_ext]
lim_sup_ext = [round(elem, 0) for elem in lim_sup_ext]
print("Using limit ranges: ")
print(lim_inf_ext)
print(lim_sup_ext)

# Retrieve tools
tools = robot.Childs()
Htools = []
list_Targets = []
ntools = len(tools)
for i in range(ntools):
    tooli = tools[i]
    tooli_name = tooli.Name()
    if tooli_name.find(TCP_PREFIX) == 0:
        Htooli = tooli.PoseTool()
        print('Using tool %s to calibrate' % tooli_name)
        #print(Htooli)
        Htools.append(Htooli)

ntools = len(Htools)

tool_cal_1 = [0, 0, 0]

# Automatically add tools if they are not found, warn the user
if ntools < 3:
    # Retrieve targets
    for i in range(4):
        ti = RDK.Item(TARGET_PREFIX + ' ' + str(i + 1), ITEM_TYPE_TARGET)
        if ti.Valid():
            print('Using target %s to calibrate' % ti.Name())
            #print(Htooli)
            list_Targets.append(ti.Joints().list())
        else:
            break

    if len(list_Targets) >= 3:
        #if (ntools < 1):
        #    RDK.ShowMessage("At least 1 tool called CalibTool 1 must be created to calibrate the rail.")
        #    quit()

        tool_cal_1 = Htools[0].Pos()
        Htools = []  # do not use tools

    else:
        for i in range(ntools, 4):
            tooli = robot.AddTool(transl(100, 0, 100), TCP_PREFIX + ' ' + str(i + 1))
            Htools.append(tooli.PoseTool())
            ntools = len(Htools)
            # raise Exception('No tools found with prefix: ' + TCP_PREFIX + '.\nRename the tools that you need to calibrate with the prefix: ' + TCP_PREFIX)

        RDK.ShowMessage("At least 3 tools or 3 targets must be used to calibrate the rail. Enter accurate or estimated values before taking measurements.")
        quit()

# Use 4 tools at most
Htools = Htools[:min(4, ntools)]


# --------------------------------------------------------------
def to_list(str_values, expected_values):
    """Converts a string into a list of values. It returns None if the array is smaller than the expected size."""
    if str_values is None:
        return None
    values = re.findall("[-+]?\d+[\.]?\d*", str_values)
    if len(values) < expected_values:
        return None
    for i in range(len(values)):
        values[i] = float(values[i])
    print('Read values: ' + repr(values))
    return values


def get_values(title_msg, show_value, expected_values):
    """Gets a list of values from the user, stops the script if the user hits cancel"""
    answer = mbox(title_msg, entry=str(show_value))
    if answer is False:
        print('Operation cancelled by user')
        sys.exit(0)

    values = to_list(answer, expected_values)
    return values


CALIB_STEPS = get_values("Enter the rail steps", CALIB_STEPS[0:ndofs_ext], ndofs_ext)

#-----------------------------------------------------------------------
SAVE_MAT = []
SAVE_MAT.append([0] * len(joints_ref) + [0, 0, 0, 0, 0, 0])
JLIST = []
if ndofs_ext == 1:
    dlta_e1 = (lim_sup_ext[0] - lim_inf_ext[0]) / CALIB_STEPS[0]
    jnts = list(joints_ref)

    val_e1 = lim_inf_ext[0]
    for i in range(int(CALIB_STEPS[0]) + 1):
        jnts[id_from] = val_e1

        for tl in Htools:
            col_add = jnts + [0, 0, 0] + tl.Pos()
            JLIST.append(list(jnts))
            SAVE_MAT.append(col_add)

        for jnts in list_Targets:
            jnts[id_from] = val_e1
            col_add = jnts + [0, 0, 0] + tool_cal_1
            JLIST.append(list(jnts))
            SAVE_MAT.append(col_add)

        val_e1 = val_e1 + dlta_e1

elif ndofs_ext == 2:
    dlta_e1 = (lim_sup_ext[0] - lim_inf_ext[0]) / CALIB_STEPS[0]
    dlta_e2 = (lim_sup_ext[1] - lim_inf_ext[1]) / CALIB_STEPS[1]
    jnts = list(joints_ref)

    val_e1 = lim_inf_ext[0]
    for i in range(int(CALIB_STEPS[0]) + 1):
        jnts[id_from + 0] = val_e1

        val_e2 = lim_inf_ext[1]
        for j in range(int(CALIB_STEPS[1]) + 1):
            jnts[id_from + 1] = val_e2

            for tl in Htools:
                JLIST.append(list(jnts))
                col_add = jnts + [0, 0, 0] + tl.Pos()
                SAVE_MAT.append(col_add)

            for jnts in list_Targets:
                jnts[id_from] = val_e1
                jnts[id_from + 1] = val_e2
                col_add = jnts + [0, 0, 0] + tool_cal_1
                JLIST.append(list(jnts))
                SAVE_MAT.append(col_add)

            val_e2 = val_e2 + dlta_e2

        val_e1 = val_e1 + dlta_e1

else:
    dlta_e1 = (lim_sup_ext[0] - lim_inf_ext[0]) / CALIB_STEPS[0]
    dlta_e2 = (lim_sup_ext[1] - lim_inf_ext[1]) / CALIB_STEPS[1]
    dlta_e3 = (lim_sup_ext[2] - lim_inf_ext[2]) / CALIB_STEPS[2]
    jnts = list(joints_ref)

    val_e1 = lim_inf_ext[0]
    for i in range(int(CALIB_STEPS[0]) + 1):
        jnts[id_from + 0] = val_e1
        val_e2 = lim_inf_ext[1]
        for j in range(int(CALIB_STEPS[1]) + 1):
            jnts[id_from + 1] = val_e2
            val_e3 = lim_inf_ext[2]
            for k in range(int(CALIB_STEPS[2]) + 1):
                jnts[id_from + 2] = val_e3

                for tl in Htools:
                    col_add = jnts + [0, 0, 0] + tl.Pos()
                    JLIST.append(list(jnts))
                    SAVE_MAT.append(col_add)

                for jnts in list_Targets:
                    jnts[id_from] = val_e1
                    jnts[id_from + 1] = val_e2
                    jnts[id_from + 2] = val_e3
                    col_add = jnts + [0, 0, 0] + tool_cal_1
                    JLIST.append(list(jnts))
                    SAVE_MAT.append(col_add)

                val_e3 = val_e3 + dlta_e3

            val_e2 = val_e2 + dlta_e2

        val_e1 = val_e1 + dlta_e1

# Load the data to the project
calibitem = RDK.ItemUserPick("Select the calibration project", ITEM_TYPE_CALIBPROJECT)
if not calibitem.Valid():
    raise Exception("No calibration project selected or available")

value = mbox('Do you want to use these targets for rail calibration or validation?', ('Rail Calibration', 'CALIB_RAIL'), ('Validation', 'VALID_TARGETS'))
SAVE_MAT = Mat(SAVE_MAT).tr()
calibitem.setValue(value, SAVE_MAT)

# Display the robot sequence
robot.ShowSequence(JLIST)
RDK.ShowMessage('Done', False)
