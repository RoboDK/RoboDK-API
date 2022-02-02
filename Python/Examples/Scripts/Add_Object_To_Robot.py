# This script allows you to attach an object to a robot link

from robodk.robolink import *  # API to communicate with RoboDK
from robodk.robodialogs import *

RDK = Robolink()  # Initialize the RoboDK API

# Select the robot
# Add the shape to a robot link
robot = RDK.ItemUserPick('Select a robot to add an object', ITEM_TYPE_ROBOT)
if not robot.Valid():
    raise Exception('No robot selected. Add a robot to attach this geometry to a link')

while True:
    value = mbox('Enter the joint to attach the object to:\n' + robot.Name() + '\nExample: 0 is the base, 3 is joint 3', entry='3')
    if not value:
        quit(0)

    link_id = int(value)
    robotlink = robot.ObjectLink(link_id)
    if robotlink.Valid():
        break

    RDK.ShowMessage("Invalid link. Select a valid robot link")

object = RDK.ItemUserPick('Select the object to add', ITEM_TYPE_OBJECT)
if not object.Valid():
    raise Exception('Object not selected')

# List of objects to merge (first one must be the robot link)
merge = [robotlink, object]

# Merge the object
RDK.MergeItems(merge)

# Set original object invisible (or delete)
object.setVisible(False)
# object.Delete()
