# Type help("robolink") or help("robodk") for more information
# Press F5 to run the script
# Documentation: https://robodk.com/doc/en/RoboDK-API.html
# Reference:     https://robodk.com/doc/en/PythonAPI/index.html
#
# This example models the forward and inverse kinematics of an ABB IRB 120 robot using the RoboDK API for Python

from robodk.robolink import *  # API to communicate with RoboDK for simulation and offline/online programming
from robodk.robomath import *  # Robot toolbox

#----------------------------------------------
# Function definitions


def FK_Robot(dh_table, joints):
    """Computes the forward kinematics of the robot.
    dh_table must be in mm and radians, the joints array must be given in degrees."""
    Habs = []
    Hrel = []
    nlinks = len(dh_table)
    HiAbs = eye(4)
    for i in range(nlinks):
        [rz, tx, tz, rx] = dh_table[i]
        rz = rz + joints[i] * pi / 180
        Hi = dh(rz, tx, tz, rx)
        HiAbs = HiAbs * Hi
        Hrel.append(Hi)
        Habs.append(HiAbs)

    return [HiAbs, Habs, Hrel]


def Frames_setup_absolute(frameparent, nframes):
    """Adds nframes reference frames to frameparent"""
    frames = []
    for i in range(nframes):
        newframe = frameparent.RDK().AddFrame('frame %i' % (i + 1), frameparent)
        newframe.setPose(transl(0, 0, 100 * i))
        frames.append(newframe)

    return frames


def Frames_setup_relative(frameparent, nframes):
    """Adds nframes reference frames cascaded to frameparent"""
    frames = []
    parent = frameparent
    for i in range(nframes):
        newframe = frameparent.RDK().AddFrame('frame %i' % (i + 1), parent)
        parent = newframe
        newframe.setPose(transl(0, 0, 100))
        frames.append(newframe)

    return frames


def Set_Items_Pose(itemlist, poselist):
    """Sets the pose (3D position) of each item in itemlist"""
    for item, pose in zip(itemlist, poselist):
        item.setPose(pose)


def are_equal(j1, j2):
    """Returns True if j1 and j2 are equal, False otherwise"""
    if j1 is None or j2 is None:
        return False
    sum_diffs_abs = sum(abs(a - b) for a, b in zip(j1, j2))
    if sum_diffs_abs > 1e-3:
        return False
    return True


#----------------------------------------------------------
# The program starts here:
RDK = Robolink()

#-----------------------------------------------------
# DH table of the robot: ABB IRB 120-3/0.6
DH_Table = []
#                 rZ (theta),   tX,   tZ,   rX (alpha)
DH_Table.append([0, 0, 290, -90 * pi / 180])
DH_Table.append([-90 * pi / 180, 270, 0, 0])
DH_Table.append([0, 70, 0, -90 * pi / 180])
DH_Table.append([0, 0, 302, 90 * pi / 180])
DH_Table.append([0, 0, 0, -90 * pi / 180])
DH_Table.append([180 * pi / 180, 0, 72, 0])

# degrees of freedom: (6 for ABB IRB 120-3/0.6)
DOFs = len(DH_Table)

# get the robot:
robot = RDK.Item('ABB IRB 120-3/0.6')

# cleanup of all items containing "Mirror tests" from previous tests
while True:
    todelete = RDK.Item('Robot base')
    # make sure an item was found
    if not todelete.Valid():
        break
    # delete only frames
    if todelete.Type() == ITEM_TYPE_FRAME:
        print('Deleting: ' + todelete.Name())
        todelete.Delete()

# setup the parent frames for the test:
parent_frameabs = RDK.AddFrame('Robot base (absolute frames)')
parent_framerel = RDK.AddFrame('Robot base (relative frames)')

# setup the child frames for the test:
frames_abs = Frames_setup_absolute(parent_frameabs, DOFs)
frames_rel = Frames_setup_relative(parent_framerel, DOFs)

# remember the last robot joints to update when necessary
last_joints = None

# infinite loop
while True:
    # get the current robot joints as a float array (list)
    joints = robot.Joints().tolist()

    # do not update if joints are the same as before
    if are_equal(joints, last_joints):
        continue

    # if joints changed, compute the forward kinematics for this position
    [Hrobot, HabsList, HrelList] = FK_Robot(DH_Table, joints)

    # turn off rendering while we update all frames:
    RDK.Render(False)
    # update all frames
    Set_Items_Pose(frames_abs, HabsList)
    Set_Items_Pose(frames_rel, HrelList)

    # render and turn on rendering
    RDK.Render(True)

    # remember the last robot joints
    last_joints = joints

    print('Current robot joints:')
    print(joints)
    print('Pose of the robot (forward kinematics):')
    print(Hrobot)
    print('\n\n')
