#This Script changes the normals of the curve to point in +Z direction by changing the i,j,k vectors to (0,0,1)

#----------------------------------------
# Start the RoboDK API
from robolink import *    # RoboDK API
from robodk import *      # Robot toolbox
RDK = Robolink()

# Ask the user to select the object
obj = RDK.ItemUserPick("Select the object or the tool to filter curves") # we can optionally filter by ITEM_TYPE_OBJECT or ITEM_TYPE_TOOL (not both)
# Exit if the user selects cancel
if not obj.Valid():
    quit()

curve_list = []
i = 0

# Iterate through all object curves, extract the curve points and retrieve the curves in a list
while True:
    curve_points, name_feature = obj.GetPoints(FEATURE_CURVE, i)      
    if len(curve_points) == 0:
        break
    i = i + 1
    curve_list.append(curve_points)
# Retrieved list contains each points as [x,y,z,i,j,k]
# Change the i,j,k vectors to 0,0,1
for curve in curve_list:
    for idx in range(len(curve)):
        i,j,k = curve[idx][3:6]
        curve[idx][3:6] = [0,0,1]
    #print(new_curve)

#Add all maniplated curves as a new object
obj_new = None
for curve in curve_list:
    obj_new = RDK.AddCurve(curve, obj_new, True, PROJECTION_NONE)

# Set the new object name and parent
obj_new.setName(obj.Name() + " New")
obj_new.setParent(obj.Parent())
obj_new.setGeometryPose(obj_new.GeometryPose())

# Set the curve display width
obj_new.setValue('Display','LINEW=4')

# Set the curve color as RGBA values [0-1.0]
obj_new.setColorCurve([0.0,0.5,1.0, 0.8])

#Delete all curves on the object first retrieved
obj.setParam("DeleteCurves")