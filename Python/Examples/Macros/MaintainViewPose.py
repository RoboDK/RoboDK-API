# This script shows how to maintain the 3D view (position of the camera) relative to the robot position
from robodk.robolink import *  # RoboDK API
from robodk.robomath import *  # Robot toolbox

RDK = Robolink()

# Select a robot
robot = RDK.ItemUserPick('Select a Robot to attach the camera view', ITEM_TYPE_ROBOT)

rf = robot.PoseFrame()  # Robot position
RP = rf * robot.Pose()  #Robot Pose
VP = RDK.ViewPose()  #View Pose
DIFF = VP * RP  #from VP to RP
last_joints = None


def SameJoints(j1, j2):
    if j1 is None:
        return False
    for i in range(len(j1)):
        if abs(j1[i] - j2[i]) > 0.0001:
            return False

    return True


# Infinite loop
while True:
    RP_c = rf * robot.Pose()  #current robot pose
    VP_c = DIFF * invH(RP_c)  #new view pose

    # Check if the robot moved, otherwise, ignore an update
    current_joints = robot.Joints().list()
    if SameJoints(last_joints, current_joints):
        continue

    last_joints = current_joints

    RDK.setViewPose(VP_c)
    RDK.Update()
    RDK.Render()
    pause(0.01)
    #RDK.ShowMessage('View Pose %s' % Pose_2_TxyzRxyz(VP_c) ,False)
