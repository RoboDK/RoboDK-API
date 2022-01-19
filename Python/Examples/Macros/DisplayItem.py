# This script allows you to show or hide any objects as a program call
#
# For example, you can call the program like this:
# DisplayItem(KUKA KR3, Show)
# DisplayItem(KUKA KR3, Hide)

from robodk.robolink import *
from robodk.robodialogs import *

# Name and visible variables
ItemName = ''
visible = True

if len(sys.argv) < 2:
    # Ask the user to change the visiblity
    print("Invalid parameters. This function must be called as DisplayItem(ItemName, show/hide)")
    print('Number of arguments: ' + str(len(sys.argv)))
    #raise Exception('Invalid parameters provided: ' + str(sys.argv))
    entry = mbox('Alter the visibility of any item. Type:\nRobotName-show/hide\n\nNote: this can be called as a program.\nExample: DisplayItem(RobotName, hide)', entry='RobotName-hide')
    if not entry:
        print('Operation cancelled')
        quit(0)

    name_value = entry.split('-')
    if len(name_value) < 2:
        raise Exception('Invalid entry: ' + entry)

    ItemName = name_value[0].strip()
    visible = name_value[1].strip().lower() != "hide"
else:
    # Parse command line options
    ItemName = sys.argv[1].strip()
    visible = sys.argv[2].strip().lower() != "hide"

# Start the RoboDK API and set the item visibility
RDK = Robolink()
item = RDK.Item(ItemName)
item.setVisible(visible)
