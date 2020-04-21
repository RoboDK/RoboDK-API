# This example shows how to programmatically select (and, if necessary, automatically create) a tool that does not exist
# This is meant to be used for robot machining projects where a tool holder is used as a reference tool
# 
# Documentation: https://robodk.com/doc/en/RoboDK-API.html
# Reference:     https://robodk.com/doc/en/PythonAPI/index.html
# Note: It is not required to keep a copy of this file, your python script is saved with the station

# Set the tool to use as a reference (tool holder or robot flange if the robot has the spindle)
FLANGE_NAME = "Flange"


# ---------------------------------------------------------
from robolink import *    # RoboDK API
from robodk import *      # Robot toolbox
RDK = Robolink()

# Get the tool holder or create it if it does not exist
tool_holder = None
tools_available = RDK.ItemList(ITEM_TYPE_TOOL)

if len(tools_available) == 0:
    robot  = RDK.ItemUserPick('Select the robot to add a new tool', ITEM_TYPE_ROBOT)
    if not robot.Valid():
        print("Operation aborted")
        quit()

    # The tool holder will be automatically selected if it is the only tool available
    tool_holder = robot.AddTool(eye(4), FLANGE_NAME)
else:
    tool_holder = RDK.Item(FLANGE_NAME, ITEM_TYPE_TOOL)

if not tool_holder.Valid(): 
    # Ask the user to select a tool holder
    tool_holder = RDK.ItemUserPick('Select a the tool holder (TCP spindle reference)', ITEM_TYPE_TOOL)
# Alernatively, pick a named tool holder:
# tool_holder = RDK.Item('Tool Holder', ITEM_TYPE_TOOL)
# Or, the first tool of a robot:
# tool_holder = robot.Childs()[0]

# Exit if the tool does not exist
if not tool_holder.Valid():
    raise Exception("The tool holder was not selected")

# Retrieve the robot
robot = tool_holder.Parent()

# Ask the user to enter the tool parameters
user_input = mbox("Enter the tool diameter and length (in mm) using the following format:\ndiameter-length\n\nExample:\n10-150", entry="10-150")
if user_input is False:
    print("Operation cancelled")
    quit(0)

# Convert the string to diameter and length variables
diam_length = user_input.split('-')
try:
    diameter = float(diam_length[0])
    length = float(diam_length[1])
except:
    raise Exception("Invalid input: " + diam_length)

# Create a new tool and add the geometry to it
tool_i_name = 'Tool %s' % user_input
tool_i = RDK.Item(tool_i_name, ITEM_TYPE_TOOL)
if tool_i.Valid():
    print("The tool already exists")

else:
    # If the tool holder Z axis points towards the outsite:
    tool_i = None
    tool_i_pose = tool_holder.PoseTool() * transl(0,0,length)

    if True:
        # Add as a tool
        tool_i = RDK.AddFile(RDK.getParam('PATH_LIBRARY') + '/Part.sld', robot)
        tool_i.setName(tool_i_name)
        tool_i.setPoseTool(tool_i_pose)
        tool_i_shape = tool_i
        tool_i_shape.setGeometryPose(rotx(0))
                
    else:
        # Add as an object nested to a tool        
        # If the tool holder Z axis points towards the inside:
        #tool_i_pose = tool_holder.PoseTool() * transl(0,0,length) * rotx(pi)
        tool_i = robot.AddTool(tool_i_pose, tool_i_name)

        # RoboDK library comes with a sample part that always has the same name
        # this Part.sld is 80 mm in diameter and 100 mm long
        tool_i_shape = RDK.AddFile(RDK.getParam('PATH_LIBRARY') + '/Part.sld', tool_i)
        
        tool_i_shape.setName("Cutter %s" % user_input)

        # Move the tool geometry to make it point against negative Z axis
        tool_i_shape.setGeometryPose(rotx(pi))

    # Scale the object accordingly
    tool_i_shape.Scale([ diameter/60,   diameter/60,   length/80  ])
    # Change the color
    tool_i_shape.Recolor([0,0,1,0.6]) # make the drill bit blue & transparent (RGBA): if transparency is under 80% it won't check for collisions (when you activate collision checking).


# Set the tool as the active tool
robot.setTool(tool_i)


