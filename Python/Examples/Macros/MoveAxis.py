# This macro allows changing the position of an external axis by hand or within a program as a function call.
# Example of a function call (units are in mm or deg):
#    MoveAxis(0)
#    MoveAxis(100)
# https://robodk.com/doc/en/RoboDK-API.html
import sys  # allows getting the passed argument parameters
from robodk.robodialogs import *

# Enter the name of the axis (leave empty to select the first mechanism/robot available
MECHANISM_NAME = ''

# Enter the default value:
DEFAULT_VALUE = 0

# Set to blocking to make the program wait until it the axis stopped moving
BLOCKING = True

# --------------- PROGRAM START -------------------------
VALUE = DEFAULT_VALUE

if len(sys.argv) < 2:
    # Promt the user to enter a new value if the macro is just double clicked
    print('This macro be called as MoveAxis(value)')
    print('Number of arguments: ' + str(len(sys.argv)))
    #raise Exception('Invalid parameters provided: ' + str(sys.argv))
    entry = mbox('Move one axis. Enter the new value in mm or deg\n\nNote: this can be called as a program.\nExample: MoveAxis(VALUE)', entry=str(DEFAULT_VALUE))
    if not entry:
        #raise Exception('Operation cancelled by user')
        quit()

    VALUE = float(entry)

else:
    # Take the argument as new joint value
    VALUE = float(sys.argv[1])

# Use the RoboDK API:
from robodk.robolink import *  # API to communicate with RoboDK

RDK = Robolink()

# Get the robot item:
axis = RDK.Item(MECHANISM_NAME, ITEM_TYPE_ROBOT)

# Move the robot/mechanism
axis.MoveJ([VALUE], BLOCKING)
