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

# Retrieve the bounding box
bbox = obj.setParam('BoundingBox')
current_size = bbox['size']

# TODO Current size in the absolute coordinate system. Convert to object coordinate system.

# Retrieve the scaling factors
new_size = InputDialog("Enter per-axis size [mm]", current_size)
if not new_size:
    quit(0)
scale_xyz = [j / i for i, j in zip(current_size, new_size)]

# Trigger scaling
obj.Scale(scale_xyz)
