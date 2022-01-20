# This macro will reposition one TCP with respect ot another TCP along the Z axis of the
# This is useful to specify a standoff or define a specific milling tool with respect to a reference tool
#
# Press F5 to run the script
# Documentation: https://robodk.com/doc/en/RoboDK-API.html
# Reference:     https://robodk.com/doc/en/PythonAPI/index.html
from robodk.robolink import *  # RoboDK API
from robodk.robomath import *  # basic matrix operations
from robodk.robodialogs import *

RDK = Robolink()

# Retrieve the reference tool
tcpref1 = RDK.Item('Tool Reference', ITEM_TYPE_TOOL)

# Retrieve to tool to modify
#tcpref2 = RDK.Item('Tool Offset', ITEM_TYPE_TOOL)# Specific tool
tcpref2 = RDK.ItemUserPick('Select the tool to offset', ITEM_TYPE_TOOL)  # pop up a message

if not tcpref1.Valid():
    raise Exception('The reference TCP does not exist')

if not tcpref2.Valid():
    raise Exception('The TCP to reposition does not exist')

# Retrieve the pose of both tools
pose1 = tcpref1.PoseTool()
pose2 = tcpref2.PoseTool()

# Retrieve the current relationship:
pose_shift = invH(pose1) * pose2
x, y, z, w, p, r = Pose_2_TxyzRxyz(pose_shift)

# Variable that holds the new offset along Z axis
newZ = 0

while True:
    message = 'Enter the new Z offset (mm)'
    if abs(x) > 0.001 or abs(y) > 0.001 or abs(w) > 0.001 or abs(p) > 0.001 or abs(r) > 0.001:
        message += '\n\nNote: Current offset:\n[X,Y,Z,W,P,R]=[%.2f,%.2f,%.2f,%.2f,%.2f,%.2f]' % (x, y, z, w, p, r)

    value = mbox(message, entry=('%.3f' % z))

    if value is False:
        print("Cancelled by the user")
        quit()

    try:
        newZ = float(value)
        break
    except ValueError:
        print("This is not a number, try again")

pose_newtool = pose1 * transl(0, 0, newZ)
tcpref2.setPoseTool(pose_newtool)
print("Done. Pose set to:")
print(pose_newtool)
