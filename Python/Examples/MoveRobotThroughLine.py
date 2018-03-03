# Move a robot along a line given a start and end point by steps
# This macro shows three different ways of programming a robot using a Python script and the RoboDK API

# More information about the RoboDK API here:
# https://robodk.com/doc/en/RoboDK-API.html
# For more information visit:
# https://robodk.com/doc/en/PythonAPI/robolink.html

# Default parameters:
P_START = [1755, -500, 2155]    # Start point with respect to the robot base frame
P_END   = [1755,  600, 2155]    # End point with respect to the robot base frame
NUM_POINTS  = 10                # Number of points to interpolate

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
    x_steps = (xEnd[0] - xStart[0])/(numPoints-1)
    y_steps = (xEnd[1] - xStart[1])/(numPoints-1)
    z_steps = (xEnd[2] - xStart[2])/(numPoints-1)

    # Incrementally add to each point until the end point is reached
    for i in range(numPoints):
        point_i = [x,y,z] # create a point
        #append the point to the list
        pt_list.append(point_i)
        x = x + x_steps
        y = y + y_steps
        z = z + z_steps
    return pt_list

#---------------------------------------------------
#--------------- PROGRAM START ---------------------
from robolink import *    # API to communicate with RoboDK
from robodk import *      # basic library for robots operations

# Generate the points curve path
POINTS = MakePoints(P_START, P_END, NUM_POINTS)

# Initialize the RoboDK API
RDK = Robolink()

# turn off auto rendering (faster)
RDK.Render(False) 

# Automatically delete previously generated items (Auto tag)
list_names = RDK.ItemList() # list all names
for item_name in list_names:
    if item_name.startswith('Auto'):
        RDK.Item(item_name).Delete()

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
# Option 1: Move the robot using the Python script

# We can automatically force the "Create robot program" action using a RUNMODE state
# RDK.setRunMode(RUNMODE_MAKE_ROBOTPROG)

# Iterate through all the points
for i in range(NUM_POINTS):
    # update the reference target with the desired XYZ coordinates
    pose_i = pose_ref
    pose_i.setPos(POINTS[i])
    
    # Move the robot to that target:
    robot.MoveJ(pose_i)
    
# Done, stop program execution
quit()


#-------------------------------------------------------------
# Option 2: Create the program on the graphical user interface
# Turn off rendering
RDK.Render(False)
prog = RDK.AddProgram('AutoProgram')

# Iterate through all the points
for i in range(NUM_POINTS):
    # add a new target and keep the reference to it
    ti = RDK.AddTarget('Auto Target %i' % (i+1))
    # use the reference pose and update the XYZ position
    pose_i = pose_ref
    pose_i.setPos(POINTS[i])
    ti.setPose(pose_i)
    # force to use the target as a Cartesian target
    ti.setAsCartesianTarget()

    # Optionally, add the target as a Linear/Joint move in the new program
    prog.MoveL(ti)

# Turn rendering ON before starting the simulation
RDK.Render(True) 

# Run the program on the simulator (simulate the program):
prog.RunProgram()
# prog.WaitFinished() # wait for the program to finish

# We can create the program automatically
# prog.MakeProgram()

# Also, if we have the robot driver we could use the following call to provoke a "Run on robot" action (simulation and the robot move simultaneously)
# prog.setRunType(PROGRAM_RUN_ON_ROBOT)

# Done, stop program execution
quit()


#-------------------------------------------------------------
# Option 3: Move the robot using the Python script and detect if movements can be linear
# This is an improved version of option 1
#
# We can automatically force the "Create robot program" action using a RUNMODE state
# RDK.setRunMode(RUNMODE_MAKE_ROBOTPROG)

# Iterate through all the points
ROBOT_JOINTS = None
for i in range(NUM_POINTS):
    # update the reference target with the desired XYZ coordinates
    pose_i = pose_ref
    pose_i.setPos(POINTS[i])
    
    # Move the robot to that target:
    if i == 0:
        # important: make the first movement a joint move!
        robot.MoveJ(pose_i)
        ROBOT_JOINTS = robot.Joints()
    else:
        # test if we can do a linear movement from the current position to the next point
        if robot.MoveL_Collision(ROBOT_JOINTS, pose_i) == 0:
            robot.MoveL(pose_i)
        else:
            robot.MoveJ(pose_i)
        ROBOT_JOINTS = robot.Joints()
    
# Done, stop program execution
quit()


#-------------------------------------------------------------
# Option 4: Create a follow curve project

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
# Option 5: Create a follow points project (similar to Option 4)

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




#-------------------------------------------------------------
# Option 6: Move the robot using the Python script and measure using an external measurement system
# This example is meant to help validating robot accuracy through distance measurements and using a laser tracker or a stereo camera

if robot.ConnectSafe() <= 0:
    raise Exception("Can't connect to robot")

RDK.setRunMode(RUNMODE_RUN_ROBOT) # It is redundant if connection worked successfully

POINTS_NOMINAL = []
POINTS_ACCURATE = []
STABILIZATION_TIME = 2 # stabilization time in seconds before taking a measurement
for i in range(NUM_POINTS):
    # build a target using the reference orientation and the XYZ coordinates
    pose_i = pose_ref
    pose_i.setPos(LINE[i])
    
    # Move to the target with the nomrinal kinematics    
    RDK.RunMessage('Moving to point %i (Nominal kinematics)' % (i+1))
    RDK.RunMessage(str(Pose_2_KUKA(pose_i)))
    # Solve nominal inverse kinematics
    robot.setAccuracyActive(False)
    ji = robot.SolveIK(pose_i)
    robot.MoveL(ji)
    robot.Pause(STABILIZATION_TIME)

    # Take the measurement
    while True:
        pose1, pose2, npoints1, npoints2, time, errors = RDK.StereoCamera_Measure()
        if errors != 0 or npoints1 < 4 or npoints2 < 4:
            print('Invalid measurement. Retrying in 2 seconds...')
            pause(2)
        else:
            # calculate the pose of the tool with respect to the reference frame
            measured = invH(pose1)*pose2
            # retrieve XYZ value of the measurement
            POINTS_NOMINAL = measured.Pos()
            break
        
    # Move to the target with the accurate kinematics
    RDK.RunMessage('Moving to point %i (Accurate kinematics)' % (i+1))
    robot.setAccuracyActive(True)
    ji = robot.SolveIK(pose_i)
    robot.MoveL(ji)
    robot.Pause(STABILIZATION_TIME)
    while True:
        pose1, pose2, npoints1, npoints2, time, errors = RDK.StereoCamera_Measure()
        if errors != 0 or npoints1 < 4 or npoints2 < 4:
            print('Invalid measurement. Retrying in 2 seconds...')
            pause(2)
        else:
            # calculate the pose of the tool with respect to the reference frame
            measured = invH(pose1)*pose2
            # retrieve XYZ value of the measurement
            POINTS_ACCURATE = measured.Pos()
            break

# At this point we can check the accurate vs the nominal kinematics and create the following table:
print('pa\tpb\tdist\tdist nom\tdist acc\terror nom\terror acc')
for i in range(numPoints):
    for j in range(numPoints+1, numPoints):
        dist_program = distance(LINE[i], LINE[j])
        dist_nominal = distance(POINTS_NOMINAL[i], POINTS_NOMINAL[j])
        dist_accurate = distance(POINTS_ACCURATE[i], POINTS_ACCURATE[j])
        error_nominal = abs(dist_nominal - dist_program)
        error_accurate = abs(dist_accurate - dist_program)        
        print('%i\t%i\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f' % (i+1,j+1,dist_program, dist_nominal, dist_accurate, error_nominal, error_accurate))

quit()


