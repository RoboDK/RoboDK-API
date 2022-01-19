# This script will copy the motion from one robot to other robots

from robodk.robolink import *    # API to communicate with RoboDK
from robodk.robomath import *    # basic matrix operations

# Ask the user to select the leader robot
RDK = Robolink()

robots = RDK.ItemList(ITEM_TYPE_ROBOT, False)

nrobots = len(robots)
if nrobots < 2:
    raise Exception('Two or more robots required!')

r_lead = RDK.ItemUserPick('Select the leader robot', ITEM_TYPE_ROBOT)
if not r_lead.Valid():
    raise Exception('No robot selected')

robots.remove(r_lead)


def joints_changed(j1, j2, tolerance=0.0001):
    """Returns True if joints 1 and joints 2 are different"""
    if j1 is None or j2 is None:
        return True

    for j1, j2 in zip(j1, j2):
        if abs(j1 - j2) > tolerance:
            return True

    return False


# Infinite loop to record robot joints
joints_last = None

while True:
    joints = r_lead.Joints().list()
    if joints_changed(joints, joints_last):
        joints_last = joints
        for r in robots:
            r.setJoints(joints)
            #r.MoveJ(joints) # to use with the driver

        RDK.Render(True)
        pause(0.00)
