# Change the color of robot machining toolpaths

from robolink import *    # RoboDK API
from robodk import *      # Robot toolbox
RDK = Robolink()

# Set the line width for display purposes
LINE_SIZE_RATIO = 0.3

# Change default curve size ratio
RDK.Command("SizeRatioCurves", LINE_SIZE_RATIO)

machining_list = RDK.ItemList(ITEM_TYPE_MACHINING, False)
ncolors = len(machining_list)

if ncolors == 0:
    quit()

# Turn Off rendering (Optional)
# RDK.Render(False)
color = [1, 0, 0.2, 1] # set RGBA color
color_step = 0
if ncolors > 1:
    color_step = 1.0/(ncolors-1)
       
for machining in machining_list:
    # Set the curve width
    #object.setValue('DISPLAY','LINEW=2')
    
    # Set the curve color
    machining.setColor(color)
    color[0] = color[0] - color_step
    color[1] = color[1] + color_step
    

print("Done")
