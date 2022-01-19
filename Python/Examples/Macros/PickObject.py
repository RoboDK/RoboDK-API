# This macro shows how to generate a station event to pick a specific object with a specific tool
# Using a macro like this one is an alternative to the Event instruction.
# By default, the Event instruction in RoboDK picks the closest object within a certain distance

# Set the tool to use as a gripper
TOOL_NAME = 'Tool Gripper'

# Set the object to pick
OBJECT_PICK = 'Part'

#---------------------------------------------------
# Start the RoboDK API
from robolink import *

RDK = Robolink()

# Select the tool and object, then, grab it
tool = RDK.Item(TOOL_NAME, ITEM_TYPE_TOOL)
obj = RDK.Item(OBJECT_PICK, ITEM_TYPE_OBJECT)

# Maintain the absolute position of the object
obj.setParentStatic(tool)

# Keep the relative position of the object (existing relationship)
#obj.setParent(tool)

# Example to set the relative position
#obj.setPose(transl(0,0,0)*rotz(pi))

# Example to set the absolute position
#obj.setPoseAbs(transl(0,0,0)*rotz(pi))
