# This program simulates waiting for a virtual Input to be activated or deactivated in RoboDK (or Station parameters)
# More information about the RoboDK API here:
# https://robodk.com/doc/en/RoboDK-API.html
# For more information visit:
# https://robodk.com/doc/en/PythonAPI/robodk.html#robolink-py

import sys  # allows getting the passed argument parameters
from robodk.robomath import *  # Robot toolbox
from robodk.robodialogs import *

# Name or number of the IO
IO_NAME = 'IO_3'

# Value of the IO (Accepted values are 1, 0, 'ON', 'OFF', 'On', ...
IO_VALUE = 0

if len(sys.argv) < 2:
    print('Invalid parameters. This function must be called as WaitIO(IO_NAME, IO_VALUE)')
    print('Number of arguments: ' + str(len(sys.argv)))
    #raise Exception('Invalid parameters provided: ' + str(sys.argv))
    entry = mbox('Wait for an IO to be a specific value. Type:\nIO_NUMBER-STATUS\n\nNote: this can be called as a program.\nExample: WaitIO(IO_NAME, VALUE)', entry='12-ON')
    if not entry:
        raise Exception('Operation cancelled by user')
    name_value = entry.split('-')
    if len(name_value) < 2:
        raise Exception('Invalid entry: ' + entry)
    IO_NAME = name_value[0]
    IO_VALUE = name_value[1]
else:
    IO_NAME = sys.argv[1]
    IO_VALUE = sys.argv[2]

if IO_NAME.isdigit():
    IO_NAME = 'IO_' + IO_NAME

if not IO_VALUE.isdigit():
    if IO_VALUE == 'ON' or IO_VALUE == 'on':
        IO_VALUE = 1
    else:
        IO_VALUE = 0

from robodk.robolink import *  # API to communicate with RoboDK

print('Wait for %s to equal %s' % (IO_NAME, IO_VALUE))

RDK = Robolink()

# infinite loop until the IO_NAME reaches de desired IO_VALUE
while RDK.getParam(IO_NAME) != IO_VALUE:
    pause(0.001)

print('Done')
