# Type help("robolink") or help("robodk") for more information
# Press F5 to run the script

# This script shows an example of how a path curve can be added to a RoboDK station.
# The curve can be optionally projected to an existing object (either along the curve normals or to the closes distance)
#
# projection types (for AddCurve, as defined in robolink.py):
#PROJECTION_NONE                = 0 # No curve projection
#PROJECTION_CLOSEST             = 1 # The projection will the closest point on the surface
#PROJECTION_ALONG_NORMAL        = 2 # The projection will be done along the normal.
#PROJECTION_ALONG_NORMAL_RECALC = 3 # The projection will be done along the normal. Furthermore, the normal will be recalculated according to the surface normal.
# More information about the RoboDK API here:
# https://robodk.com/doc/en/RoboDK-API.html


# Function definition to create a list of points (curve)
def CirclePoints(radius, xStart, xEnd, xStep, accuracy, ycoord, projection):
    """Generates a list of points given circle dimensions"""
    nx, ny, nz = projection  # normal/projection direction
    # Safe checks:
    radius = abs(radius)
    xStep = abs(xStep)
    accuracy = abs(accuracy)
    if abs(xStart) >= radius:
        raise Exception("Start point is outside the circle")
    if abs(xEnd) >= radius:
        raise Exception("End point is outside the circle")
    if xStart > xEnd:
        xStep = -xStep

    # Iterate on X coordinate, then on Z coordinate
    POINTS = []
    zSense = +1.0
    x = xStart
    x_steps = int(abs((xEnd - xStart) / xStep))
    y = ycoord
    for i in range(x_steps + 1):
        z_abs = sqrt(radius * radius - x * x)
        z_steps = int(2 * z_abs / accuracy)
        z_step = -zSense * 2 * z_abs / z_steps
        z = zSense * z_abs
        for j in range(z_steps + 1):
            point_i = [x, y, z, nx, ny, nz]  # create a ne point with normal/projection direction
            POINTS.append(point_i)
            z = z + z_step
        zSense = zSense * (-1.0)
        x = x + xStep
    return POINTS


#------------------------------------------------------------------
#--------------- PROGRAM START ---------------------
from robolink import *  # API to communicate with RoboDK
from robodk import *  # basic matrix operations

# Default parameters:
RADIUS = 475  # Radius of the outer circle
xSTART = -450  # Start point for the zig-zag
xEND = 450  # End point for the zig-zag
xSTEP = 50  # Step between passes
ACCURACY = 5  # Accuracy to cut the passes

# Other parameters:
yLEVEL = 200  # y coordinate, to start projection
proj_dir = [0, 1, 0]  # projection direction -> normal/direction of the projection

# Initialize the RoboDK API
RDK = Robolink()

# Ask the user to select an object to project the curve
obj = RDK.ItemUserPick('Select object to project the path<br>(select cancel if you do not want to project the path)', ITEM_TYPE_OBJECT)

# Show message to the user
text = mbox("Enter the path parameters. Example:\n[RADIUS  xSTART  xEND  xSTEP  ACCURACY]", entry="475  -450  450  50  5")
if text:
    print("User entered:")
    print(text)
    # if the user entered the values, retrieve the list of values
    numbers = [float(x) for x in text.split()]  # convert strings to numbers
    if len(numbers) >= 5:
        RADIUS, xSTART, xEND, xSTEP, ACCURACY = numbers  # split array into variables
    else:
        print("Using default parameters")

else:
    print("Using default parameters")

# Generate the curve path
CURVE = CirclePoints(RADIUS, xSTART, xEND, xSTEP, ACCURACY, yLEVEL, proj_dir)

# display the points
#print(CURVE)

# Add the curve to the object with the option to project along the normals and recalculate the normals according to the surface normal
curve = obj.AddCurve(CURVE, False, PROJECTION_ALONG_NORMAL_RECALC)
# last call is equivalent to:
#RDK.AddCurve(CURVE, obj, False, PROJECTION_ALONG_NORMAL_RECALC)

curve.setName('Curve:R%.0f;X%.0f;D%.0f;A%.0f' % (RADIUS, xSTART, xSTEP, ACCURACY))
