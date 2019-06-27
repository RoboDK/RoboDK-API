# type help("robolink") or help("robodk") for more information
# (note: you do not need to keep a copy of this file, your python script is saved with the station)
from robolink import *    # API to communicate with robodk
from robodk import *      # basic matrix operations
from random import uniform
import sys      # to exit the script without errors (sys.exit(0))
import re       # to convert a string list into a list of values

DEFAULT_NMEASURES = 80
# Default limit space in the Cartesian space
DEFAULT_XYZ_MIN = [-5000, -5000, 0]
DEFAULT_XYZ_MAX = [ 5000,  5000, 5000]

TRACKER_REF_NAME = 'Tracker reference' # keyword of the measurement system reference (in RoboDK)

# Use the tag CHECK_COLLISION_NAME to automatically turn the objects visible. This will allow to detect collisions.
CHECK_COLLISION_MOVE = True
CHECK_COLLISION_NAME = 'collision'
CHECK_COLLISION_STEP = 10 # in degrees, step to check for collisions. higher is faster.

# Use the tag CHECK_COLLISION_NAME to automatically turn the objects visible. This will allow to detect collisions.
CHECK_WORKSPACE = True
CHECK_WORKSPACE_NAME = 'Workspace'




# use FILE_SAVE_PREFIX to automatically save the file, otherwise, comment this line
# FILE_SAVE_PREFIX = 'CalibrationSequence'


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
    if type(show_value) == Mat:
        show_value = show_value.tolist()
    answer = mbox(title_msg, entry=str(show_value))
    if answer is False:
        print('Operation cancelled by user')
        sys.exit(0)
        #raise Exception('Operation cancelled by user')
    #print('Input value: ' + answer)
    values = to_list(answer, expected_values)
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
NMEASURES = RDK.getParam('CALIB_MEASUREMENTS')
JOINTS_REF = to_list(RDK.getParam('CALIB_JOINTS_REF'), 6)
ANG_MIN = to_list(RDK.getParam('CALIB_JOINTLIM_LOW'), 6)
ANG_MAX = to_list(RDK.getParam('CALIB_JOINTLIM_HIGH'), 6)
XYZ_MIN = to_list(RDK.getParam('CALIB_XYZLIM_LOW'), 3)
XYZ_MAX = to_list(RDK.getParam('CALIB_XYZLIM_HIGH'), 3)


INPUT_VALUES = False
# force user input if one of the variables is not set
if NMEASURES is None or JOINTS_REF is None or ANG_MIN is None or ANG_MAX is None or XYZ_MIN is None or XYZ_MAX is None:
    INPUT_VALUES = True

#----------------------- Select robot ---------------
robot = RDK.ItemUserPick("Select a robot for calibration/validation", ITEM_TYPE_ROBOT)
if not robot.Valid():
    raise Exception('Robot not selected or no robot available')
print('Using robot: %s' % robot.Name())
#------------------------------------------------------------

#----------------------- Select the tracker reference ---------------
tracker = RDK.Item(TRACKER_REF_NAME)
if not tracker.Valid():
    frame_ref = RDK.AddFrame('Measurements Reference', robot.Parent())
    frame_ref.setPose(transl(500,0,-500));
    tracker = RDK.AddFrame(TRACKER_REF_NAME, frame_ref)
    tracker.setPose(transl(2000,0,0)*rotx(-pi/2))
    #tracker = RDK.ItemUserPick('Select the measurement system reference:<br>(avoid this message by naming the tracker reference "%s")' % TRACKER_REF_NAME, ITEM_TYPE_FRAME)
    #if not tracker.Valid():
    #    stop_script()



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
    JOINTS_REF = robot.JointsHome().tolist()

if XYZ_MIN is None:
    XYZ_MIN = DEFAULT_XYZ_MIN

if XYZ_MAX is None:
    XYZ_MAX = DEFAULT_XYZ_MAX

[ang_min_robot, ang_max_robot, JOINTS_TYPE] = robot.JointLimits()
if ANG_MIN is None or ANG_MAX is None:
    ANG_MIN = ang_min_robot.tolist()
    ANG_MAX = ang_max_robot.tolist()
    # limit joint axes from -180 to +180 (no need to go farther for calibration)
    for i in [0,3,5]:
        ANG_MIN[i] = max(ANG_MIN[i], -180)
        ANG_MAX[i] = min(ANG_MAX[i],  180)
        
    ANG_MIN[4] = max(ANG_MIN[4], -90)
    ANG_MAX[4] = min(ANG_MAX[4],  90)    

    print('Using default robot joint limits:')
    print(ANG_MIN)
    print(ANG_MAX)
    

while True:
    # Loop until the user inputs variables that are accepted
    if INPUT_VALUES:
        # Ask the user to validate/enter all the settings

        # ---------------- getting the number of measurements
        if NMEASURES is None or type(NMEASURES) == str:
            NMEASURES = DEFAULT_NMEASURES
        input_val = mbox('Enter the number of measurements:\n(at least 60 measurements are recommended for robot calibration)', entry=str(NMEASURES))
        if input_val is False:
            stop_script()

        NMEASURES = int(float(input_val))
        RDK.setParam('CALIB_MEASUREMENTS', NMEASURES)

        # ---------------- getting the Reference Joints
        robot.setJoints(JOINTS_REF)
        answer = mbox('Set the robot reference joints and select OK. The tool must be facing the tracker for this position.\nCurrent values: %s' % str(JOINTS_REF))
        if answer is False:
            stop_script()

        JOINTS_REF = robot.Joints().tolist()
        RDK.setParam('CALIB_JOINTS_REF', JOINTS_REF)

        # ---------------- getting the Joint limits (lower bound)
        robot.setJoints(ANG_MIN)
        answer = mbox('Set the Joint limits (LOWER bound, in deg), then select OK.\nCurrent values: %s' % str(ANG_MIN))
        if answer is False:
            stop_script()

        ANG_MIN = robot.Joints().tolist()
        RDK.setParam('CALIB_JOINTLIM_LOW', ANG_MIN)

        # ---------------- getting the Joint limits (upper bound)
        robot.setJoints(ANG_MAX)
        answer = mbox('Set the Joint limits (UPPER bound, in deg), then select OK.\nCurrent values: %s' % str(ANG_MAX))
        if answer is False:
            stop_script()

        ANG_MAX = robot.Joints().tolist()
        RDK.setParam('CALIB_JOINTLIM_HIGH', ANG_MAX)

        # ---------------- getting the XYZ limits (lower bound)
        XYZ_MIN = get_values('Enter the Cartesian limits (lower bound, in mm), then select OK.', XYZ_MIN, 3)
        RDK.setParam('CALIB_XYZLIM_LOW', XYZ_MIN)

        # ---------------- getting the XYZ limits (upper bound)
        XYZ_MAX = get_values('Enter the Cartesian limits (upper bound, in mm), then select OK.', XYZ_MAX, 3)
        RDK.setParam('CALIB_XYZLIM_HIGH', XYZ_MAX)

    # show summary of parameters
    robot.setJoints(JOINTS_REF)
    summary_msg = 'Current settings to generate robot calibration configurations:\n\n'
    summary_msg += ('Number of points: %i\n' % NMEASURES)
    summary_msg += ('Reference joints (deg): %s\n' % str([ round(elem) for elem in JOINTS_REF ]))
    summary_msg += ('Tracker object: %s\n' % tracker.Name())
    if tool_object is not None and workspace_object is not None and workspace_object.Valid() and workspace_object.Visible():
        CHECK_WORKSPACE = True
        summary_msg += ('Creating targets inside tracker workspace (hide workspace to deactivate)\n\n')
    else:
        CHECK_WORKSPACE = False
        summary_msg += ('Skip creating targets inside the tracker workspace (show workspace to activate)\n\n')
    summary_msg += ('Lower joint limits (deg): %s\n' % str(ANG_MIN))
    summary_msg += ('Upper joint limits (deg): %s\n\n' % str(ANG_MAX))
    summary_msg += ('Lower Cartesian limits (mm): %s\n' % str(XYZ_MIN))
    summary_msg += ('Upper Cartesian limits (mm): %s\n\n' % str(XYZ_MAX))
    summary_msg += ('Important: Define collision map settings to check for collisions (select: Tools->Collision Map)\n\n')
    summary_msg += ('Continue?')

    answer = mbox(summary_msg, b1=('Start','s'), b2=('Edit','e'))
    if answer == 'e':
        # Continue loop until the summary is accepted
        INPUT_VALUES = True
        continue

    # if paramters are OK, exit the loop and continue
    break



# raise Exception('done')



# Avoid a cylinder located at X=0, Y=0 or radius R_MIN
R_MIN = 100
R_MIN_Z = 200

# Allow rotations of the tool pointing to the measurement system
ROTX_MIN = -5
ROTX_MAX =  5
ROTY_MIN = -5
ROTY_MAX =  5
ROTZ_MIN = -180
ROTZ_MAX =  180


NDOFS = len(ANG_MAX)

# -----------------------------------------------------
# Custom-made procedures
def randjoints():
    """Returns a random set of robot joints within the joint limits."""
    angrand = Mat(NDOFS,1)
    for i in range(NDOFS):
        angrand[i,:] = uniform(ANG_MIN[i], ANG_MAX[i])
    #jrand = angles_2_joints(angrand.tolist(), JOINTS_TYPE)
    jrand = angrand.tolist()
    return Mat(jrand)

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
            return False
    return True
    
def check_pose(hin):
    """Returns true if the pose is within the accepted limits."""
    x = hin[0,3]
    y = hin[1,3]
    z = hin[2,3]
    if x < XYZ_MIN[0] or x > XYZ_MAX[0] or y < XYZ_MIN[1] or y > XYZ_MAX[1] or z < XYZ_MIN[2] or z > XYZ_MAX[2]:
        return False
    elif x*x + y*y < R_MIN*R_MIN and z < R_MIN_Z:
        return False
    return True

#def randpose(rob, htool, href):
#    """Returns a random pose taking into account the robot joint limits"""
#    jrand = randjoints()
#    try:
#        hrand = rob.SolveFK(jrand)*htool
#    except:
#        return False
#    hrandorient = hrand
#    hrandorient[0:3,0:3] = href[0:3,0:3]
#    rx = uniform(ROTX_MIN, ROTX_MAX)*pi/180
#    ry = uniform(ROTY_MIN, ROTY_MAX)*pi/180
#    rz = uniform(ROTZ_MIN, ROTZ_MAX)*pi/180
#    hrandorient = hrandorient*rotx(rx)*roty(ry)*rotz(rz)
#    return hrandorient
def randpose(rob, htool, point):
    """Returns a random pose where the Z axis points to the measurement system within the accepted rotation limits.
    The point must be given with respect to the robot reference frame."""
    while True:
        jrand = randjoints()
        try:
            hrand = rob.SolveFK(jrand)*htool
        except:
            continue
        hrandorient = hrand
        hrandorient[0:3,0:3] = href[0:3,0:3]
        rx = uniform(ROTX_MIN, ROTX_MAX)*pi/180
        ry = uniform(ROTY_MIN, ROTY_MAX)*pi/180
        rz = uniform(ROTZ_MIN, ROTZ_MAX)*pi/180
        hrandorient = hrandorient*rotx(rx)*roty(ry)*rotz(rz)
        return hrandorient

def randorient():
    """Returns a random orientation pose given the custom settings"""
    rx = uniform(ROTX_MIN, ROTX_MAX)*pi/180
    ry = uniform(ROTY_MIN, ROTY_MAX)*pi/180
    rz = uniform(ROTZ_MIN, ROTZ_MAX)*pi/180
    return rotz(rz)*roty(ry)*rotx(rx)

def pose_facing(pose, point):
    """Returns a pose where the Z axis points to the measurement system.
    The Y axis points towards the Z negative direction of the reference coordinates"""
    pose_xyz = pose.Pos()
    zaxis = normalize3(subs3(point,pose_xyz))
    yaprox = [0,0,-1]
    if angle3(zaxis, yaprox) < 2*pi/180:
        yaprox = [0,-1,0]
    xaxis = normalize3(cross(yaprox, zaxis))
    yaxis = cross(zaxis, xaxis)
    pose.setVX(xaxis)
    pose.setVY(yaxis)
    pose.setVZ(zaxis)
    return pose
    
def randpose_facing(rob, htool, point):
    """Returns a random pose where the Z axis of the tool points to the measurement system. An additional pose rotation is added according to the settings.
    The point is where the Z axis points and it must be provided with respect to the robot reference frame.
    The Y axis points towards the floor (robot negative Z-axis)"""
    jrand = randjoints()
    hrand = rob.SolveFK(jrand)*htool
    hrand = pose_facing(hrand, point)
    hrand = hrand*randorient()
    return hrand

# -----------------------------------------------------------------------
# calculate the position of the tracker with respect to the robot reference frame
Htracker_wrt_robot = invH(robot.PoseAbs())*tracker.PoseAbs()
ptracker = Htracker_wrt_robot.Pos()

# -----------------------------------------------------------------------
# Calculate the tool pose with the Z axis of the tool facing to the tracker:
Htool = robot.PoseTool() # use active tool
# Htool = robot.Childs()[0].PoseTool() # use the first available tool
# Htool = rotx(90*pi/180) # use a custom input tool
# Make the Z axis face the tracker
robot_pose = robot.SolveFK(JOINTS_REF)
Htool_wrt_robot = pose_facing(robot_pose*Htool, ptracker)
Htool = invH(robot_pose)*Htool_wrt_robot

print('Modified Tool pose with the Z axis pointing towards the tracker at the reference position:')
print(Htool)
iHtool = invH(Htool)

#Href = robot.SolveFK(JOINTS_REF)*Htool
#print('Href')
#print(Href)


# -----------------------------------------------------------------------
# Get objects to check collisions:
sethidden = []
all_objects = RDK.ItemList(None, True)
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

#jref = Mat(JOINTS_REF)
#robot.setJoints(jref);


# -----------------------------------------------------------------------
print('Generating ' + repr(NMEASURES) + ' calibration/validation measurements.')
JLIST = Mat(6,0)
LAST_JOINTS = JOINTS_REF

i = -1
id_measure = 0
timeused = 0
timeleft = -1;
tic()
while id_measure < NMEASURES:
    i = i + 1
    hi = randpose_facing(robot, Htool, ptracker)
    #if not isinstance(hi,Mat):
    #    continue
    print('Number of measurements found: %i' % id_measure)
    #try:
    ji = robot.SolveIK(hi*iHtool)
    print(ji)
    #except:
    #    RDK.Connect() # I do not know why this is needed
    #    print('    Cant solve ' + repr(i))
    #    #print(hi)
    #    continue
    if not check_joints(ji):
        print('    Joints outside limits %i' % i)
        continue
    if not check_pose(hi):
        print('    Pose outside limits %i' % i)
        continue
    
    # display potentially good configuration
    robot.setJoints(ji)
    if CHECK_WORKSPACE and not tool_object.IsInside(workspace_object):
        print('    Tool object outside measurement workspace %i' % i)
        continue
    if CHECK_COLLISION_MOVE and robot.MoveJ_Test(LAST_JOINTS, ji, CHECK_COLLISION_STEP) > 0:
        print('    MoveJ causes collision %i' % i)
        continue

    #robot.setJoints(ji) #this is made automatically by MoveJ_Collision
    LAST_JOINTS = ji
    JLIST = catH(JLIST, ji)
    id_measure = id_measure + 1

    # Calculate time
    timeused = toc()
    timeavg = timeused/id_measure
    timeleft = (NMEASURES-id_measure)*timeavg
    print('Elapsed time      : %.1f sec ' % timeused)
    #print('Expected time left: %.1f sec  (average time x measure: %.1f sec)' % (timeleft, timeavg))
    message = 'Calculating measurement configurations. Expected time left: %.1f sec  (found %i/%i measurements)' % (timeleft, id_measure, NMEASURES)
    print(message)
    RDK.ShowMessage(message, False)

NMEASURES_OK = id_measure

SAVE_MAT = JLIST

# -----------------------------------------------------------------------
# Save file if requested
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

# -----------------------------------------------------------------------
# Hide objects that we used to check collisions:
nhide = len(sethidden)
for i in range(nhide):
    sethidden[i].setVisible(False)

# -----------------------------------------------------------------------
calibitem = RDK.ItemUserPick("Select the calibration project", ITEM_TYPE_CALIBPROJECT)
if not calibitem.Valid():
    raise Exception("No calibration project selected or available")

value = mbox('Do you want to use these targets for calibration or validation?', ('Calibration', 'CALIB_TARGETS'), ('Validation', 'VALID_TARGETS'))
calibitem.setValue(value, SAVE_MAT)

RDK.ShowMessage('Done', False)

#mbox('Done')
# -----------------------------------------------------------------------

#RDK.ShowSequence(Mat([[1, 10 ,10 ,10 ,10 ,10 ,10],[ 2, 20 ,20 ,20 ,20 ,20 ,20]]))


