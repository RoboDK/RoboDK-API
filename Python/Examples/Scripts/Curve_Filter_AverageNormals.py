# This macro shows how to average the normals of an object containing curves.
# This macro can also filter points that are too close to each other.
# The use must select an object, then, a copy of this object is created with the normals averaged.

# For more information about the RoboDK API:
# Documentation: https://robodk.com/doc/en/RoboDK-API.html
# Reference:     https://robodk.com/doc/en/PythonAPI/index.html
#-------------------------------------------------------

# Enter the size of the average filter, in number of samples.
# If this value is set to -1 it will popup a message asking the user to enter a value
FilterNormalSamples = -1  # in samples

# Enter the distance, in mm, to filter close points.
# For example, if we want one point each 2 mm at most, we should enter 2.
# Set to -1 to not filter the number of points.
FilterPointDistance = -1  # in mm

# ------------------------------------------------------
# Start the RoboDK API
from robolink import *  # RoboDK API
from robodk import *  # Robot toolbox

RDK = Robolink()

# Ask the user to select the object
obj = RDK.ItemUserPick("Select the object or the tool to filter curves")  # we can optionally filter by ITEM_TYPE_OBJECT or ITEM_TYPE_TOOL (not both)
# Exit if the user selects cancel
if not obj.Valid():
    quit()

# Ask the user to enter the filter size
if FilterNormalSamples <= 0:
    str_avg_filter = mbox("Enter the filter size (the number of points/normals used for the average filter).\nFor example, if the filter size is 10 units, the 10 closest normals are used to average each individual normal.", entry="10")
    if not str_avg_filter:
        # The user selected cancel
        quit()
    # Convert the user input to an integer
    FilterNormalSamples = int(str_avg_filter)
    if FilterNormalSamples <= 0:
        RDK.ShowMessage("Invalid Filter value. Enter a value >= 1", False)
        raise Exception(msg)

# Iterate through all object curves, extract the curve points and average the normals
curve_id = 0
obj_filtered = None
while True:
    points, name_feature = obj.GetPoints(FEATURE_CURVE, curve_id)
    # points is a double array of float with np points and xyzijk data for each point
    # point[np] = [x,y,z,i,j,k] # where xyz is the position and ijk is the tool orientation (Z axis, usually the normal to the surface)
    np = len(points)
    # when curve_id is out of bounds, an empty double array is returned
    if np == 0 or len(points[0]) < 6:
        break

    msg = "Filtering: " + name_feature
    print(msg)
    RDK.ShowMessage(msg, False)
    curve_id = curve_id + 1

    # For each point, average the normals in the range of points [-FilterNormalSamples/2 ; +FilterNormalSamples/2]
    new_normals = []
    for i in range(np):
        id_avg_from = round(max(0, i - 0.5 * FilterNormalSamples))
        id_avg_to = round(min(np - 1, i + 0.5 * FilterNormalSamples))

        # Make sure we account for the start and end sections (navg is usually FilterNormalSamples, except near the borders)
        n_avg = id_avg_to - id_avg_from
        normal_i = [0, 0, 0]
        for j in range(id_avg_from, id_avg_to):
            ni = points[j][3:6]
            normal_i = add3(normal_i, ni)

        # Normalize
        normal_i = normalize3(normal_i)
        #this would not be correct: normal_i = mult3(normal_i, 1.0/n_avg)

        # Add the new normal to the list
        new_normals.append(normal_i)

    # Combine the normals with the list of points
    for i in range(np):
        points[i][3:6] = new_normals[i][0:3]

    # Filter points, if desired
    if FilterPointDistance > 0:
        lastp = None
        points_filtered = []
        points_filtered.append(points[0])
        lastp = points[0]

        for i in range(1, np):
            if distance(lastp, points[i]) > FilterPointDistance:
                points_filtered.append(points[i])
                lastp = points[i]

        points = points_filtered

    # For the first curve: create a new object, rename it and place it in the same location of the original object
    if obj_filtered is None:
        obj_filtered = RDK.AddCurve(points, 0, False, PROJECTION_NONE)
        obj_filtered.setName(obj.Name() + " Filtered")
        obj_filtered.setParent(obj.Parent())
        obj_filtered.setGeometryPose(obj_filtered.GeometryPose())

    else:
        # After the first curve has been added, add following curves to the same object
        RDK.AddCurve(points, obj_filtered, True, PROJECTION_NONE)

# Set the curve display width
obj_filtered.setValue('DISPLAY', 'LINEW=2')
# Set the curve color as RGBA values [0-1.0]
obj_filtered.setColorCurve([0.0, 0.5, 1.0, 0.8])
