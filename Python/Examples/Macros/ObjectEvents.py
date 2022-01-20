# This macro shows how to add new points on object surfaces
# This macro can be run through command line and it can also be attached as an event
# Example: In RoboDK follow these steps:
# 1- Double an object
# 2- Select More Options
# 3- Select Edit Events
# 4- Enter the following:
# Create a new Point->ObjectEvents NEWPOINT %ID%
# Create a new Target->ObjectEvents NEWTARGET %ID%
# Point Coordinates->ObjectEvents SHOWPOINT %ID%
# Curve to Targets->ObjectEvents CURVE_2_TARGETS %ID%
#
# This will add two new entries when we right click the object:
#   "Create a new point" : this will provide the command NEWPOINT to this script and will add a point on the cursor location
#   "Point Coordinates" : this will show the point coordinates (surface point or selected point)
#
# More information about the RoboDK API here:
# https://robodk.com/doc/en/RoboDK-API.html

import sys  # allows getting the argument parameters
from robodk.robolink import *  # API to communicate with RoboDK
from robodk.robomath import *  # basic matrix operations

print('Number of arguments: ' + str(len(sys.argv)) + ' arguments.')

OBJECT = None
COMMAND = "SHOWPOINT_ALL"  # Default command if we just double click the macro
# other available commands through command line: NEWPOINT SHOWPOINT

# Start RoboDK API
RDK = Robolink()

# If the two arguments from the object events are provided, retrieve the command and the object ID
if len(sys.argv) >= 3:
    COMMAND = sys.argv[1]
    OBJECT = Item(RDK, int(sys.argv[2]))
    #RDK.ShowMessage("%s : %s" % (str(sys.argv), COMMAND))

else:
    # If the macro is double clicked, pop up a message
    OBJECT = RDK.ItemUserPick("Select an object", ITEM_TYPE_OBJECT)
    if not OBJECT.Valid():
        quit()

print("Selected object: %s" % OBJECT.Name())

if COMMAND == "SHOWPOINT_ALL":
    # Show all points in the object
    points, name = OBJECT.GetPoints(FEATURE_POINT)
    message = 'List of points for object<br>%s<br>' % OBJECT.Name()
    i = 0
    for pt in points:
        i = i + 1
        message += "p%i : %.3f , %.3f , %.3f <br>" % (i, pt[0], pt[1], pt[2])

    RDK.ShowMessage(message)

elif COMMAND == "SHOWPOINT":
    # Shows the point selected
    is_selected, feature_type, feature_id = OBJECT.SelectedFeature()
    if feature_type != FEATURE_POINT:
        RDK.ShowMessage("The selected feature is not a point")
        quit()

    points, name_selected = OBJECT.GetPoints(feature_type, feature_id)
    point = None
    if len(points) > 1:
        point = points[feature_id]
    else:
        point = points[0]
    RDK.ShowMessage("Selected Point: %s<br>XYZ = [%.3f, %.3f, %.3f]<br>ijk = [%.3f, %.3f, %.3f]" % (name_selected, point[0], point[1], point[2], point[3], point[4], point[5]))

elif COMMAND == "NEWPOINT":
    # create a new point under the mouse cursor
    is_selected, feature_type, feature_id = OBJECT.SelectedFeature()
    if feature_type != FEATURE_SURFACE:
        RDK.ShowMessage("The selected feature is not a surface")
        quit()

    point_mouse, name_feature = OBJECT.GetPoints(FEATURE_SURFACE)
    if 'point on surface' in name_feature.lower():
        point_rel = point_mouse[0]
        RDK.ShowMessage("%s -> XYZ = [%.3f, %.3f, %.3f] , ijk = [%.3f, %.3f, %.3f]" % (name_feature, point_rel[0], point_rel[1], point_rel[2], point_rel[3], point_rel[4], point_rel[5]), False)
        ADD_POINT_ON_OBJECT = True
        OBJECT.AddPoints([point_rel], ADD_POINT_ON_OBJECT, PROJECTION_NONE)
    else:
        RDK.ShowMessage("Select a surface")

elif COMMAND == "NEWTARGET":
    # create a new point under the mouse cursor
    point_mouse, name_feature = OBJECT.GetPoints(FEATURE_SURFACE)
    if 'point on surface' in name_feature.lower():
        point_rel = point_mouse[0]
        RDK.ShowMessage("%s -> XYZ = [%.3f, %.3f, %.3f] , ijk = [%.3f, %.3f, %.3f]" % (name_feature, point_rel[0], point_rel[1], point_rel[2], point_rel[3], point_rel[4], point_rel[5]), False)

        angle_Z = 0 * pi / 180
        pose = point_Zaxis_2_pose(point_rel[0:3], point_rel[3:6]) * rotx(pi) * rotz(angle_Z)
        # poseref = robot.Pose()
        target = RDK.AddTarget('NewTarget', OBJECT.Parent())
        target.setPose(pose)
    else:
        RDK.ShowMessage("Select a surface")

elif COMMAND == "CURVE_2_TARGETS":
    # Convert a curve to a list of targets
    is_selected, feature_type, feature_id = OBJECT.SelectedFeature()
    if feature_type != FEATURE_CURVE:
        RDK.ShowMessage("The selected feature is not a curve")
        quit()

    point_list, name_feature = OBJECT.GetPoints(FEATURE_CURVE, feature_id)
    last_pose = None
    npoints = len(point_list)
    if npoints < 2:
        RDK.ShowMessage("Select a curve")
        quit()

    TOLERANCE = 1

    pi_last = None

    for i in range(npoints):
        p_i = point_list[i]
        if pi_last is not None and distance(pi_last, p_i) < TOLERANCE:
            continue

        pose = last_pose
        if i < npoints - 1:
            p_i2 = point_list[i + 1]
            vy = subs3(p_i2, p_i)
            vz = [-p_i[3], -p_i[4], -p_i[5]]
            pose = point_Zaxis_2_pose(p_i[0:3], vz, vy)

        else:
            pose.setPos(p_i[0:3])

        target = RDK.AddTarget("T%i " % i + name_feature, OBJECT.Parent())
        target.setPose(pose)
        last_pose = pose

        pi_last = p_i

        RDK.ShowMessage("Adding target", False)

else:
    raise Exception("Invalid operation specified")
