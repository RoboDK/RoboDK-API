# This script allows you to schedule taking measurements in a cube
# The script makes sure that points are reachable
from robolink import *  # API to communicate with robodk
from robodk import *  # basic matrix operations
from random import uniform
import sys  # to exit the script without errors (sys.exit(0))
import re  # to convert a string list into a list of values

# Default number of measurements
DEFAULT_NMEASURES = 80

# Define the cube range to create poses with respect to the reference position
#           MIN,  MAX, STEP
TX_RANGE = [-200, 200, 100]
TY_RANGE = [-200, 200, 100]
TZ_RANGE = [-100, 100, 100]

# Use the tag CHECK_COLLISION_NAME to automatically turn the objects visible. This will allow to detect collisions.
CHECK_WORKSPACE = False
CHECK_WORKSPACE_NAME = 'Workspace'

TRACKER_REF_NAME = 'Tracker reference'  # keyword of the measurement system reference (in RoboDK)
TCP_PREFIX = 'CalibTool'

# Use the tag CHECK_COLLISION_NAME to automatically turn the objects visible. This will allow to detect collisions.
CHECK_COLLISION = True
CHECK_COLLISION_MOVE = True
CHECK_COLLISION_NAME = 'collision'
CHECK_COLLISION_STEP = -1  # in degrees, step to check for collisions. higher is faster.

# Default limit space in the Cartesian space
DEFAULT_XYZ_MIN = [-5000, -5000, 0]
DEFAULT_XYZ_MAX = [5000, 5000, 5000]

# Avoid a cylinder located at X=0, Y=0 or radius R_MIN
R_MIN = 100
R_MIN_Z = 200

# use FILE_SAVE_PREFIX to automatically save the file, otherwise, comment this line
# FILE_SAVE_PREFIX = 'CalibrationSequence'

# Create the list of poses:
POSES = []
# You can optionally add rotation around Z axis:
#for rz in [-60, -30, 30, 60]:
for rz in [0]:
    for tz in range(TZ_RANGE[0], TZ_RANGE[1] + 1, TZ_RANGE[2]):
        for ty in range(TY_RANGE[0], TY_RANGE[1] + 1, TY_RANGE[2]):
            for tx in range(TX_RANGE[0], TX_RANGE[1] + 1, TX_RANGE[2]):
                pose = transl(tx, ty, tz) * rotz(rz * pi / 180.0)
                POSES.append(pose)


# --------------------------------------------------------------
def str2floatlist(str_values, expected_values):
    """Converts a string to a list of values. It returns None if the array is smaller than the expected size."""
    if str_values is None:
        return None
    values = re.findall("[-+]?\d+[\.]?\d*", str_values)
    if len(values) < expected_values:
        return None
    for i in range(len(values)):
        values[i] = float(values[i])
    #print('Read values: ' + repr(values))
    return values


def mbox_getfloatlist(title_msg, show_value, expected_values):
    """Get a list of values from the user, stops the script if the user hits cancel"""
    if type(show_value) == Mat:
        show_value = show_value.tolist()
    answer = mbox(title_msg, entry=str(show_value))
    if answer is False:
        print('Operation cancelled by user')
        sys.exit(0)
        #raise Exception('Operation cancelled by user')

    #print('Input value: ' + answer)
    values = str2floatlist(answer, expected_values)
    #if len(values) < expected_values:
    #    raise Exception('%i values expected' % expected_values)
    return values


def stop_script():
    """Forces the script to finish with/without errors"""
    # raise Exception('Operation cancelled by user')
    print('Operation cancelled by user')
    sys.exit(0)


# ---------------------------------
RDK = Robolink()

# get previously set variables
JOINTS_REF = str2floatlist(RDK.getParam('CALIB_JOINTS_REF'), 6)
ANG_MIN = str2floatlist(RDK.getParam('CALIB_JOINTLIM_LOW'), 6)
ANG_MAX = str2floatlist(RDK.getParam('CALIB_JOINTLIM_HIGH'), 6)
XYZ_MIN = None  #str2floatlist(RDK.getParam('CALIB_XYZLIM_LOW'), 3)
XYZ_MAX = None  #str2floatlist(RDK.getParam('CALIB_XYZLIM_HIGH'), 3)

INPUT_VALUES = False
# force user input if one of the variables is not set
if ANG_MIN is None or ANG_MAX is None:
    INPUT_VALUES = True

#----------------------- Select robot ------------------
robot = RDK.ItemUserPick("Select a robot for calibration/validation", ITEM_TYPE_ROBOT)
if not robot.Valid():
    raise Exception('Robot not selected or no robot available')
print('Using robot: %s' % robot.Name())
robot.setAccuracyActive(False)
#------------------------------------------------------------

#----------------------- Select tracker ------------------
tracker = RDK.Item(TRACKER_REF_NAME)
if not tracker.Valid():
    frame_ref = RDK.AddFrame('Measurements Reference', robot.Parent())
    frame_ref.setPose(transl(2000, 0, 1000))
    tracker = RDK.AddFrame(TRACKER_REF_NAME, frame_ref)
    tracker.setPose(transl(0, 0, 0))
    tracker.setVisible(False)
#    tracker = RDK.ItemUserPick('Select the measurement system reference:<br>(avoid this message by naming the tracker reference "%s")' % TRACKER_REF_NAME, ITEM_TYPE_FRAME)
#    if not tracker.Valid():
#        stop_script()

#----------------------- Select tool and workspace object to verify if tool is inside the object
tool_object = None
workspace_object = None
if CHECK_WORKSPACE:
    # tool_object is the geometry of the tool used to check if the tool is inside the workspace
    robot_tools = robot.Childs()
    for tooli in robot_tools:
        if tooli.Name().find(CHECK_COLLISION_NAME) >= 0:
            tool_object = tooli
    if tool_object is None and len(robot_tools) > 0:
        tool_object = robot_tools[0]

    # workspace object is the workspace of the tracker (object)
    workspace_object = RDK.Item(CHECK_WORKSPACE_NAME, ITEM_TYPE_OBJECT)
#------------------------------------------------------------

if JOINTS_REF is None:
    # Use robot home position as default reference joints
    JOINTS_REF = robot.Joints().list()  #.JointsHome().tolist()

else:
    robot.setJoints(JOINTS_REF)

if XYZ_MIN is None:
    XYZ_MIN = DEFAULT_XYZ_MIN

if XYZ_MAX is None:
    XYZ_MAX = DEFAULT_XYZ_MAX

[ang_min_robot, ang_max_robot, JOINTS_TYPE] = robot.JointLimits()
if ANG_MIN is None or ANG_MAX is None:
    ANG_MIN = ang_min_robot.tolist()
    ANG_MAX = ang_max_robot.tolist()
    # limit joint axes from -180 to +180 (no need to go farther for calibration)
    for i in [0, 3, 5]:
        ANG_MIN[i] = max(ANG_MIN[i], -180)
        ANG_MAX[i] = min(ANG_MAX[i], 180)

    ANG_MIN[4] = max(ANG_MIN[4], -90)
    ANG_MAX[4] = min(ANG_MAX[4], 90)

    print('Using default robot joint limits:')
    print(ANG_MIN)
    print(ANG_MAX)

while True:
    # Loop until the user inputs variables that are accepted
    if INPUT_VALUES:
        # ---------------- getting the Reference Joints
        robot.setJoints(JOINTS_REF)
        answer = mbox('Set the robot reference joints and select OK. The tool must be facing the tracker for this position.\nCurrent values: %s' % str(JOINTS_REF))
        if answer is False:
            stop_script()

        JOINTS_REF = robot.Joints().tolist()
        RDK.setParam('CALIB_JOINTS_REF', JOINTS_REF)

        # ---------------- getting the Joint limits (lower bound)
        #robot.setJoints(ANG_MIN)
        #answer = mbox('Set the Joint limits (LOWER bound, in deg), then select OK.\nCurrent values: %s' % str(ANG_MIN))
        #if answer is False:
        #    stop_script()

        #ANG_MIN = robot.Joints().tolist()
        #RDK.setParam('CALIB_JOINTLIM_LOW', ANG_MIN)

        # ---------------- getting the Joint limits (upper bound)
        #robot.setJoints(ANG_MAX)
        #answer = mbox('Set the Joint limits (UPPER bound, in deg), then select OK.\nCurrent values: %s' % str(ANG_MAX))
        #if answer is False:
        #    stop_script()

        #ANG_MAX = robot.Joints().tolist()
        #RDK.setParam('CALIB_JOINTLIM_HIGH', ANG_MAX)

        # ---------------- getting the XYZ limits (lower bound)
        #XYZ_MIN = get_values('Enter the Cartesian limits (lower bound, in mm), then select OK.', XYZ_MIN, 3)
        #RDK.setParam('CALIB_XYZLIM_LOW', XYZ_MIN)

        # ---------------- getting the XYZ limits (upper bound)
        #XYZ_MAX = get_values('Enter the Cartesian limits (upper bound, in mm), then select OK.', XYZ_MAX, 3)
        #RDK.setParam('CALIB_XYZLIM_HIGH', XYZ_MAX)

    # show summary of parameters
    #robot.setJoints(JOINTS_REF)
    summary_msg = 'Current settings to generate robot calibration configurations:\n\n'
    if tool_object is not None and workspace_object is not None and workspace_object.Valid() and workspace_object.Visible():
        CHECK_WORKSPACE = True
        summary_msg += ('Creating targets inside tracker workspace (hide workspace to deactivate)\n\n')
    else:
        CHECK_WORKSPACE = False
        summary_msg += ('Skip creating targets inside the tracker workspace (show workspace to activate)\n\n')

    summary_msg += ('Reference joints   (deg): %s\n' % str(JOINTS_REF))
    summary_msg += ('Lower joint limits (deg): %s\n' % str(ANG_MIN))
    summary_msg += ('Upper joint limits (deg): %s\n\n' % str(ANG_MAX))
    summary_msg += ('Lower Cartesian limits (mm): %s\n' % str(XYZ_MIN))
    summary_msg += ('Upper Cartesian limits (mm): %s\n\n' % str(XYZ_MAX))
    summary_msg += ('Important: Define collision map settings to check for collisions (select: Tools->Collision Map)\n\n')
    summary_msg += ('Continue?')

    answer = mbox(summary_msg, b1=('Start', 's'), b2=('Edit', 'e'))
    if answer == 'e':
        # Continue loop until the summary is accepted
        INPUT_VALUES = True
        continue

    # if paramters are OK, exit the loop and continue
    break

# raise Exception('done')

NDOFS = len(ANG_MAX)


# -----------------------------------------------------
# Custom-made procedures
def check_joints(jin):
    """Returns true if the joints are within the accepted limits."""
    if not isinstance(jin, Mat):
        return False
    if jin.size(0) < 6:
        return False
    #angles = joints_2_angles(jin.tolist(), JOINTS_TYPE)
    angles = jin.tolist()
    for i in range(NDOFS):
        if angles[i] > ANG_MAX[i] or angles[i] < ANG_MIN[i]:
            print("        Joint %i out of limits (%.1f)" % ((i + 1), angles[i]))
            return False
    return True


def check_pose(hin):
    """Returns true if the pose is within the accepted limits."""
    x = hin[0, 3]
    y = hin[1, 3]
    z = hin[2, 3]
    if x < XYZ_MIN[0] or x > XYZ_MAX[0]:
        print("        X coordinate out of limits %.1f" % x)
    elif y < XYZ_MIN[1] or y > XYZ_MAX[1]:
        print("        Y coordinate out of limits %.1f" % y)
    elif z < XYZ_MIN[2] or z > XYZ_MAX[2]:
        print("        Z coordinate out of limits %.1f" % z)
    elif x * x + y * y < R_MIN * R_MIN and z < R_MIN_Z:
        print("        Robot wrist too close to the robot")
    else:
        return True
    return False


# -------------------------------------------------------------
# Program start:

# Get the robot tool list
tools = robot.Childs()

# Get tools to calibrate (tools nambed with TCP_PREFIX):
# Also, set visible the tools named with CHECK_COLLISION_NAME to check collisions

sethidden = []
print('Robot tools:')
Htools = []
ntools = len(tools)
for i in range(ntools):
    tooli = tools[i]
    tooli_name = tooli.Name()
    if tooli_name.find(TCP_PREFIX) == 0:
        Htooli = tooli.PoseTool()
        print('Using %s to calibrate' % tooli_name)
        print(Htooli)
        Htools.append(Htooli)

    if tooli_name.find(CHECK_COLLISION_NAME) >= 0:
        print('Using TCP %s to check collision' % tooli_name)
        # Set the tool visible and remember if it was invisible to turn it off
        if not tooli.Visible():
            sethidden.append(tooli)
            tooli.setVisible(True)

# Get objects to check collisions:
all_objects = RDK.ItemList(ITEM_TYPE_OBJECT, True)
nobjects = len(all_objects)
for i in range(nobjects):
    objecti = RDK.Item(all_objects[i])
    objecti_name = objecti.Name()
    if objecti_name.find(CHECK_COLLISION_NAME) >= 0:
        print('Using object %s to check collision' % objecti_name)
        # Set the object visible and remember if it was hidden to turn it off
        if not objecti.Visible():
            sethidden.append(objecti)
            objecti.setVisible(True)

ntools = len(Htools)
if ntools <= 0:
    tooli = robot.AddTool(transl(100, 0, 100), TCP_PREFIX + ' 1')
    Htools.append(tooli.PoseTool())
    ntools = len(Htools)
    # raise Exception('No tools found with prefix: ' + TCP_PREFIX + '.\nRename the tools that you need to calibrate with the prefix: ' + TCP_PREFIX)

# Calculate the reference pose according to the first tool
POSE_REF = robot.SolveFK(JOINTS_REF, Htools[0])

Htracker_wrt_robot = invH(robot.PoseAbs()) * tracker.PoseAbs()
ptracker = Htracker_wrt_robot[0:3, 3].tolist()

# -----------------------------------------------------------------------
print('Generating calibration/validation measurements.')

NMEASURES = len(POSES)
print("Scheduled points: %i" % NMEASURES)

JLIST = Mat(6, 0)
JOINTS_REF = robot.JointsHome()
LAST_JOINTS = JOINTS_REF  #robot.Joints()
TCPLIST = Mat(3, 0)
id_measure = 0

for pose in POSES:
    idtool = 0
    Htool = Htools[idtool]
    ptool = Htool.Pos()
    iHtool = invH(Htool)
    hi = pose.translationPose() * POSE_REF * pose.rotationPose()
    pose_flange = hi * iHtool
    print(pose_flange)
    ji = robot.SolveIK(pose_flange, JOINTS_REF)
    if not check_joints(ji):
        print('    Joint outside limits')
        continue

    if not check_pose(pose_flange):  #check_pose(hi):
        print('    Pose outside limits')
        continue

    # display potentially good configuration
    robot.setJoints(ji)
    if CHECK_COLLISION and RDK.Collisions():
        print('    End point is in a collision state %i' % i)
        continue
    if CHECK_WORKSPACE and not tool_object.IsInside(workspace_object):
        print('    Tool object outside measurement workspace %i' % i)
        continue
    if CHECK_COLLISION_MOVE and robot.MoveJ_Test(LAST_JOINTS, ji, CHECK_COLLISION_STEP) > 0:
        print('    MoveJ causes collision %i' % i)
        continue

    # robot.setJoints(ji) #this is made automatically by MoveJ_Collision
    LAST_JOINTS = ji

    for idtool in range(len(Htools)):
        Htool = Htools[idtool]
        ptool = Htool.Pos()

        JLIST = catH(JLIST, ji)
        TCPLIST = catH(TCPLIST, ptool)
        id_measure = id_measure + 1

        # Calculate time
        timeused = toc()
        print('Elapsed time      : %.1f sec ' % timeused)
        #print('Expected time left: %.1f sec  (average time x measure: %.1f sec)' % (timeleft, timeavg))
        message = 'found %i/%i measurements' % (id_measure, NMEASURES)
        print(message)
        RDK.ShowMessage(message, False)

if id_measure < 0:
    RDK.ShowMessage("No measurements found. Make sure your collisions map settings is properly set")

NMEASURES_OK = id_measure
SAVE_MAT = catV(JLIST, TCPLIST)

if 'FILE_SAVE_PREFIX' in locals():
    strsave = RDK.getParam('PATH_OPENSTATION') + '/' + FILE_SAVE_PREFIX + repr(NMEASURES_OK) + '.txt'
    SAVE_MAT.save(strsave)
#else:
#    strsave = getSaveFile(RDK.getParam('PATH_OPENSTATION'))
#    strsave = strsave.name
#    SAVE_MAT.save(strsave)

# -----------------------------------------------------------------------
print(tr(JLIST))
robot.ShowSequence(JLIST)
RDK.ShowMessage('Calibration/validation sequence found', False)

# Hide objects that we used to check collisions:
nhide = len(sethidden)
for i in range(nhide):
    sethidden[i].setVisible(False)

# -----------------------------------------------------------------------
calibitem = RDK.ItemUserPick("Select the calibration project", ITEM_TYPE_CALIBPROJECT)
if not calibitem.Valid():
    raise Exception("No calibration project selected or available")

value = mbox('Do you want to use these targets for calibration or validation?\nUsing project: ' + calibitem.Name(), ('Calibration', 'CALIB_TARGETS'), ('Validation', 'VALID_TARGETS'))
calibitem.setValue(value, SAVE_MAT)

RDK.ShowMessage('Done', False)

#mbox('Done')
# -----------------------------------------------------------------------

#RDK.ShowSequence(Mat([[1, 10 ,10 ,10 ,10 ,10 ,10],[ 2, 20 ,20 ,20 ,20 ,20 ,20]]))
