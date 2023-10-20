# Scale an object given a per-axis scale ratio

# Documentation: https://robodk.com/doc/en/RoboDK-API.html
# Reference:     https://robodk.com/doc/en/PythonAPI/index.html
# Note: It is not required to keep a copy of this file, your python script is saved with the station
from robodk.robolink import *  # RoboDK API
from robodk.robomath import *  # Robot toolbox
from robodk.robodialogs import *

# Connect to RoboDK API
RDK = Robolink()

# Remove selection to force selecting an object
RDK.setSelection([])

# Ask the user to select an object or tool
obj = RDK.ItemUserPick('Select an object or tool to scale', RDK.ItemList(ITEM_TYPE_TOOL) + RDK.ItemList(ITEM_TYPE_OBJECT))
if not obj.Valid():
    quit(0)

# Retrieve the scaling factors
scale_xyz = InputDialog("Enter a per-axis scale", [1.0, 1.0, 1.0])
if not scale_xyz:
    quit(0)

# Trigger scaling
obj.Scale(scale_xyz)
