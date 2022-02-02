# Type help("robolink") or help("robodk") for more information
# Press F5 to run the script
# Documentation: https://robodk.com/doc/en/RoboDK-API.html
# Reference:     https://robodk.com/doc/en/PythonAPI/index.html
#
# Move a robot along a line given a start and end point by steps
# This macro shows different ways of programming a robot using a Python script and the RoboDK API

# Default parameters:
P_START = [1755, -500, 2155]  # Start point with respect to the robot base frame
P_END = [1755, 600, 2155]  # End point with respect to the robot base frame
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
from robodk.robolink import *  # API to communicate with RoboDK for simulation and offline/online programming
from robodk.robomath import *  # Robotics toolbox for industrial robots

# Generate the points curve path
POINTS = MakePoints(P_START, P_END, NUM_POINTS)

# Initialize the RoboDK API
RDK = Robolink()

# turn off auto rendering (faster)
RDK.Render(False)

# Automatically delete previously generated items (Auto tag)
list_items = RDK.ItemList()  # list all names
for item in list_items:
    if item.Name().startswith('Auto'):
        item.Delete()

# Promt the user to select a robot (if only one robot is available it will select that robot automatically)
robot = RDK.ItemUserPick('Select a robot', ITEM_TYPE_ROBOT)

# Turn rendering ON before starting the simulation
RDK.Render(True)

# Abort if the user hits Cancel
if not robot.Valid():
    quit()

# Retrieve the robot reference frame
reference = robot.Parent()

# Use the robot base frame as the active reference
robot.setPoseFrame(reference)

# get the current orientation of the robot (with respect to the active reference frame and tool frame)
pose_ref = robot.Pose()
print(Pose_2_TxyzRxyz(pose_ref))
# a pose can also be defined as xyzwpr / xyzABC
#pose_ref = TxyzRxyz_2_Pose([100,200,300,0,0,pi])

#-------------------------------------------------------------
# Option 1: Create a curve follow project

# First we need to create an object from the provided points or add the points to an existing object and optionally project them on the surface

# Create a new object given the list of points (the 3xN vector can be extended to 6xN to provide the normal)
object_points = RDK.AddPoints(POINTS)

# Alternatively, we can project the points on the object surface
# object = RDK.Item('Object', ITEM_TYPE_OBJECT)
# object_points = object.AddPoints(POINTS, PROJECTION_ALONG_NORMAL_RECALC)
# Place the points at the same location as the reference frame of the object
# object_points.setParent(object.Parent())

# Set the name of the object containing points
object_points.setName('AutoPoints n%i' % NUM_POINTS)

path_settings = RDK.AddMillingProject("AutoPointFollow settings")
prog, status = path_settings.setMillingParameters(part=object_points)
# At this point, we may have to manually adjust the tool object or the reference frame

# Run the create program if success
prog.RunProgram()

# Done
quit()

#-------------------------------------------------------------
# Option 2: Create a point follow project (similar to Option 4)

# First we need to create an object from the provided points or add the points to an existing object and optionally project them on the surface

# Create a new object given the list of points:
object_curve = RDK.AddCurve(POINTS)

# Alternatively, we can project the points on the object surface
# object = RDK.Item('Object', ITEM_TYPE_OBJECT)
# object_curve = object.AddCurve(POINTS, PROJECTION_ALONG_NORMAL_RECALC)
# Place the curve at the same location as the reference frame of the object
# object_curve.setParent(object.Parent())

# Set the name of the object containing points
object_curve.setName('AutoPoints n%i' % NUM_POINTS)

# Create a new "Curve follow project" to automatically follow the curve
path_settings = RDK.AddMillingProject("AutoCurveFollow settings")
prog, status = path_settings.setMillingParameters(part=object_curve)
# At this point, we may have to manually adjust the tool object or the reference frame

# Run the create program if success
prog.RunProgram()

# Done
quit()
