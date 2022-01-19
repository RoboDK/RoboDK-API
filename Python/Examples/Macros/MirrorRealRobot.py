# This macro moves a real robot according to the simulated robot
# This macro is useful to move a robot from a 3D mouse for example
#
# Documentation: https://robodk.com/doc/en/RoboDK-API.html
# Reference:     https://robodk.com/doc/en/PythonAPI/index.html
# Note: It is not required to keep a copy of this file, your python script is saved with the station

TOLERANCE_MOVE_DEG = 1  # Tolerance to move the robot in degrees

from robolink import *  # RoboDK API
from robodk import *  # Robot toolbox

RDK = Robolink()

robot = RDK.ItemUserPick("Select a robot", ITEM_TYPE_ROBOT)

robot.Connect()
# RDK.setRunMode(RUNMODE_RUN_ROBOT) (redundant with connect)
connected, message = robot.ConnectedState()

print("Connexion status:")
print(message)


# Check if the robot joints need to be updated (according to the tolerance)
def update_joints(j1, j2):
    if j1 is None or j2 is None:
        return True

    for i in range(len(j1)):
        if abs(j1[i] - j2[i]) > TOLERANCE_MOVE_DEG:
            return True

    return False


joints_last = None
while True:
    # Retrieve the robot joints from the simulator (not the real robot)
    joints_sim = robot.SimulatorJoints()
    if update_joints(joints_sim, joints_last):
        # Move the robot
        print("Moving the robot to: " + str(joints_sim))
        robot.MoveJ(joints_sim)
        joints_last = joints_sim

    pause(0.01)
