# This macro will update all tools that have a Length flag in the tool name (Tool L220.551) with respect to a reference tool.
# The reference tool must have a reference Length (example: Calib Point L164.033).
# This is useful to specify a standoff or define a specific milling tool with respect to a reference tool.
# Tip: Define the first tool with a length of 0 Example: Spindle L0 and it will be placed at the root of the tool holder
#
# More information about the RoboDK API here:
# https://robodk.com/doc/en/RoboDK-API.html
# For more information visit:
# https://robodk.com/doc/en/PythonAPI/robodk.html#robolink-py

from robodk.robolink import *  # RoboDK API
from robodk.robomath import *  # Robot toolbox
from robodk.robodialogs import *

# Name of the reference tool (name in the RoboDK tree)
# The name must contain the length in mm
TOOL_NAME_REF = 'Calib Point L164.033'


# Get the nominal tool length based on the tool name and the L keyword
def get_len_tool(toolname):
    toolnamelist = toolname.split(" ")
    for w in toolnamelist:
        if w.startswith("L"):
            try:
                len_tcp_definition = float(w[1:])
                return len_tcp_definition
            except:
                print("Unable to convert word: " + str(w))
                continue

    print("Warning! Unknown length")
    return None


# Start the API
RDK = Robolink()

# Retrieve the reference tool and make sure it exists
tcpref1 = RDK.Item(TOOL_NAME_REF, ITEM_TYPE_TOOL)
if not tcpref1.Valid():
    raise Exception('The reference TCP does not exist')

# Get the reference length
len_ref = get_len_tool(tcpref1.Name())
if len_ref is None:
    print("Reference length not specified, 0 assumed")
    len_ref = 0

# Retrieve the pose of both tools
pose1 = tcpref1.PoseTool()

# Iterate through all tools
for tcpref2 in tcpref1.Parent().Childs():

    if tcpref2.Type() != ITEM_TYPE_TOOL:
        # Not a tool item, skip
        continue

    if tcpref1 == tcpref2:
        # this is the same tool, skip
        continue

    # Get the tool pose
    pose2 = tcpref2.PoseTool()

    # Retrieve the current relationship:
    pose_shift = invH(pose1) * pose2
    x, y, z, w, p, r = Pose_2_TxyzRxyz(pose_shift)

    # Variable that holds the new offset along Z axis
    newZ = None

    toolname = tcpref2.Name()
    len_tcp_definition = get_len_tool(toolname)
    if len_tcp_definition is None:
        print("Skipping tool without L length: " + toolname)
        continue

    # Calculate the offset according to "L" naming:
    nominal_offset = len_tcp_definition - len_ref

    while True:
        message = 'Tool:\n%s\n\nEnter the new Z offset (mm)\nCurrent offset is: %.3f' % (toolname, z)

        if abs(nominal_offset - z) > 0.001:
            message += '\n\nNote:\nNominal offset (%.3f-%.3f): %.3f mm\nvs.\nCurrent offset: %.3f mm\nDoes not match' % (len_tcp_definition, len_ref, nominal_offset, z)
        else:
            message += '\nOffset currently matches'

        if abs(x) > 0.001 or abs(y) > 0.001 or abs(w) > 0.001 or abs(p) > 0.001 or abs(r) > 0.001:
            message += '\n\nImportant: Current offset:\n[X,Y,Z,W,P,R]=[%.2f,%.2f,%.2f,%.2f,%.2f,%.2f]' % (x, y, z, w, p, r)

        value = mbox(message, entry=('%.3f - %.3f' % (len_tcp_definition, len_ref)))

        if value is False:
            print("Cancelled by the user")
            #quit()# stop
            break  # go to next

        try:
            newZ = eval(value)  #float(value)
            break
        except ValueError:
            print("This is not a number, try again")

    # Update the tool if an offset has been calculated
    if newZ is not None:
        pose_newtool = pose1 * transl(0, 0, newZ)
        tcpref2.setPoseTool(pose_newtool)
        print("Done. Pose set to:")
        print(pose_newtool)
