# This program simulates changing the value of virtual Input/Outputs in RoboDK (or Station parameters)
# More information about the RoboDK API here:
# https://robodk.com/doc/en/RoboDK-API.html
import sys  # allows getting the passed argument parameters
from robodk.robodialogs import *

# Name or number of the IO
IO_NAME = 'IO_3'

# Value of the IO (Accepted values are 1, 0, 'ON', 'OFF', 'On', ...
IO_VALUE = 0

if len(sys.argv) < 2:
    print('Invalid parameters. This function must be called as SetIO(IO_NAME, IO_VALUE)')
    print('Number of arguments: ' + str(len(sys.argv)))
    #raise Exception('Invalid parameters provided: ' + str(sys.argv))
    entry = mbox('Alter state of an IO. Type:\nIO_NUMBER-STATUS\n\nNote: this can be called as a program.\nExample: SetIO(IO_NAME, VALUE)', entry='12-ON')
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

RDK = Robolink()
# Set the IO as a station parameter
RDK.setParam(IO_NAME, IO_VALUE)
