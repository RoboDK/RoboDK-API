# Scale an object given a per-axis scale ratio

# Documentation: https://robodk.com/doc/en/RoboDK-API.html
# Reference:     https://robodk.com/doc/en/PythonAPI/index.html
# Note: It is not required to keep a copy of this file, your python script is saved with the station
from robolink import *  # RoboDK API
from robodk import *  # Robot toolbox


def str2floatlist(str_values, expected_values):
    """Converts a string to a list of values. It returns None if the array is smaller than the expected size."""
    import re
    if str_values is None:
        return None
    values = re.findall("[-+]?\d+[\.]?\d*", str_values)
    if len(values) < expected_values:
        return None
    for i in range(len(values)):
        values[i] = float(values[i])
    #print('Read values: ' + repr(values))
    return values


def mbox_getfloatlist(title_msg, show_value, expected_values):
    """Get a list of values from the user, stops the script if the user hits cancel"""
    if type(show_value) == Mat:
        show_value = show_value.tolist()
    answer = mbox(title_msg, entry=str(show_value))
    if answer is False:
        print('Operation cancelled by user')
        quit(0)
        #raise Exception('Operation cancelled by user')

    #print('Input value: ' + answer)
    values = str2floatlist(answer, expected_values)
    #if len(values) < expected_values:
    #    raise Exception('%i values expected' % expected_values)
    return values


# Connect to RoboDK API
RDK = Robolink()

# Remove selection to force selecting an object
RDK.setSelection([])

# Ask the user to select an object or tool
obj = RDK.ItemUserPick('Select an object or tool to scale')
if not obj.Valid():
    quit(0)

scale_xyz = mbox_getfloatlist("Enter a per-axis scale", [1, 1, 1], 3)
if not scale_xyz:
    quit(0)

# Trigger scaling
obj.Scale(scale_xyz)
