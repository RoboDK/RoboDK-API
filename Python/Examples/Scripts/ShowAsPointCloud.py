# This script shows how to change the appearance of points and lines in objects
# Changing the point style can help speed up rendering

# For more information about the RoboDK API:
# Documentation: https://robodk.com/doc/en/RoboDK-API.html
# Reference:     https://robodk.com/doc/en/PythonAPI/index.html
#-------------------------------------------------------
from robolink import *

# Start the RoboDK API
RDK = Robolink()

# Retrieve current selection
selection = RDK.Selection()
selected = None

# Check if the first selected item is an object or a tool
if len(selection) > 0:
    selected = selection[0]
    if not selected.type == ITEM_TYPE_OBJECT or selected.type == ITEM_TYPE_TOOL:
        selected = None
        RDK.setSelection([])
        
# If nothing is selected, ask the user to select an item
if selected is None:
    selected = RDK.ItemUserPick('Select an object to optimize for point cloud', ITEM_TYPE_OBJECT)
    
    if not selected.Valid():
        # User cancelled object selection
        exit()

# Display points as simple dots given a certain size (suitable for fast rendering)
# Color is defined as AARRGGBB
selected.setParam('Display', 'POINTSIZE=4 COLOR=#FF771111')

# Display each point as a cube of a given size in mm
#selected.setParam('Display','PARTICLE=CUBE(0.2,0.2,0.2) COLOR=#FF771111')

# Another way to change display style of points to display as a sphere (size,rings):
#selected.setParam('Display','PARTICLE=SPHERE(4,8) COLOR=red')

# Example to change the size of displayed curves:
#selected.setParam('Display','LINEW=4')   

# Example to change the curve colors
#selected.setColorCurve([1,1,1,1])