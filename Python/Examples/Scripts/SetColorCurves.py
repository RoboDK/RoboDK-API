# Change the color of object curves

from robolink import *  # RoboDK API
from robodk import *  # Robot toolbox

RDK = Robolink()

# Set the line width for display purposes
LINE_WIDTH = 0.5

object_list = RDK.ItemList(ITEM_TYPE_OBJECT, False)
ncolors = len(object_list)

if ncolors == 0:
    quit()

# Turn Off rendering (Optional)
# RDK.Render(False)
color = [1, 0, 0.2, 1]  # set RGBA color
color_step = 0
if ncolors > 1:
    color_step = 1.0 / (ncolors - 1)

for object in object_list:
    # Set the curve width
    #object.setValue('DISPLAY','LINEW=2')
    object.setValue('Display', 'LINEW=%.3f' % LINE_WIDTH)

    # Set the curve color
    object.setColorCurve(color)
    color[0] = color[0] - color_step
    color[1] = color[1] + color_step

print("Done")
