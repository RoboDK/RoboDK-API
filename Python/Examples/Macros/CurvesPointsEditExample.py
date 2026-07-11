# Example to operate (add/edit/remove) points, curves or single points of a curve
# 
# More information about the RoboDK API here:
# https://robodk.com/doc/en/RoboDK-API.html
# For more information visit:
# https://robodk.com/doc/en/PythonAPI/robodk.html#robolink-py

# Default parameters:
P_START = [0, 0, 0]  # Start point with respect to the robot base frame
P_END = [100, 0, 2000]  # End point with respect to the robot base frame
NUM_POINTS = 10  # Number of points to interpolate


# Function definition to create a list of points (line)
def MakePoints(xStart, xEnd, numPoints):
    """Generates a list of points"""
    if len(xStart) != 3 or len(xEnd) != 3:
        raise Exception("Start and end point must be 3-dimensional vectors")
    if numPoints < 2:
        raise Exception("At least two points are required")

    # Starting Points
    pt_list = []
    x = xStart[0]
    y = xStart[1]
    z = xStart[2]

    # How much we add/subtract between each interpolated point
    x_steps = (xEnd[0] - xStart[0]) / (numPoints - 1)
    y_steps = (xEnd[1] - xStart[1]) / (numPoints - 1)
    z_steps = (xEnd[2] - xStart[2]) / (numPoints - 1)

    # Incrementally add to each point until the end point is reached
    for i in range(numPoints):
        point_i = [x, y, z]  # create a point
        #append the point to the list
        pt_list.append(point_i)
        x = x + x_steps
        y = y + y_steps
        z = z + z_steps
    return pt_list


#---------------------------------------------------
#--------------- PROGRAM START ---------------------
from robodk.robolink import *  # API to communicate with RoboDK
from robodk.robomath import *  # basic matrix operations

# Generate the points curve path
POINTS = MakePoints(P_START, P_END, NUM_POINTS)

# Initialize the RoboDK API
RDK = Robolink()

# turn off auto rendering (faster)
RDK.Render(False)

# Automatically delete previously generated items (Auto tag)
list_names = RDK.ItemList()  # list all names
for itm in reversed(list_names):
    if itm.Name().startswith('Auto'):
        itm.Delete()

# ---------------
# Full curve operations examples:
object_curve = RDK.AddCurve(POINTS)
object_curve.setName('AutoCurve')

# Add another curve to the existing object
object_curve.setValue("PointAdd Curve", robomath.Mat(POINTS).tr()*2)

# Add another curve to the existing object at the given index (1), offsetting existing index 0 to 1 and so on
object_curve.setValue("PointAdd Curve 0", robomath.Mat(POINTS).tr()*10)

# ---------------
# Single point operations on a curve
# Remove a point at location 1 to a curve of index 0
object_curve.setValue("PointRemove Curve 0 1")

# Edit a point at the new location 1 to a curve of index 0
object_curve.setValue("PointEdit Curve 0 1", robomath.Mat([51,52,53]))

# Add a point at location 9 to a curve of index 0: 
# -> NOT SUPPORTED: delete the curve at index 0 and add it again
# object_curve.setValue("PointAdd Curve 0 9", robomath.Mat([61,62,63]))


# -----------------------
# Point operations examples
# Create a new object given the list of points (the 3xN vector can be extended to 6xN to provide the normal)
object_points = RDK.AddPoints(POINTS)
object_points.setName('AutoPoints')

# Add a point to the list of points (added at the end)
object_points.setValue("PointAdd Point", robomath.Mat([25,50,60]).tr())

# Add a point at index 1, offsetting existing index 1 to index 2 and onwards
object_points.setValue("PointAdd Point 1", robomath.Mat([[25,25,25],[44,44,44]]))

# Remove a point at a certain index (zero based)
object_points.setValue("PointRemove Point 10")
