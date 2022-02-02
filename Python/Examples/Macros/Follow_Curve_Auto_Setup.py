# This example takes 2 objects:
# 1 - Object with curves or points
# 2 - Curve follow project or point follow project
# Then, it creates a curve follow project if the object has curves, or a point follow project if it has points but no curves

from robodk.robolink import *  # RoboDK API

RDK = Robolink()

#-------------------------------------------------------------
# Ask the user to select an object
obj = RDK.ItemUserPick("Select an object", ITEM_TYPE_OBJECT)
if not obj.Valid():
    print("Cancelled")
    quit()

# Ask the user to select a curve follow project (optional)
proj = RDK.ItemUserPick("Select an curve follow project or select cancel to create a new one", ITEM_TYPE_MACHINING)
if not proj.Valid():
    proj = RDK.AddMachiningProject("%s settings" % obj.Name())

# Link the curve follow project to the object
proj.setMachiningParameters(part=obj, params="RotZ_Range=45 RotZ_Step=5 NormalApproach=50 Optim_Turntable=Yes Offset_Turntable=90 No_Update")

# Generate the program, if possible
status = proj.Update()
print(status)
