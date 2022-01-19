# This script will check collisions accurately for all programs in a RoboDK station independently of the robot speed
# Press F5 to run the script
# More information about the RoboDK API here:
# https://robodk.com/doc/en/RoboDK-API.html
# Or visit: https://robodk.com/doc/en/PythonAPI/index.html
# Note: you do not need to keep a copy of this file, your python script is saved with the station
from robodk.robolink import *    # API to communicate with RoboDK
from robodk.robomath import *    # basic matrix operations
RENDER_ALWAYS = True  # Set to False
STEP_MM = 2  # Step in MM for linear moves
STEP_DEG = 1  # Step in DEG for joint moves (approach/retract)

# Start a connection with the RoboDK API
RDK = Robolink()

# Select the first/only robot in the cell:
robot = RDK.Item('', ITEM_TYPE_ROBOT)
if not robot.Valid():
    raise Exception("No robot available! Load a robot or a station first")
print("Using robot %s" % robot.Name())

# Define home joints for each of the sides, use target "Home1" if it is available, otherwise, use the robot "Home" joints
joints_home = robot.JointsHome()
t_home1 = RDK.Item('Home1', ITEM_TYPE_TARGET)
if t_home1.Valid():
    joints_home = t_home1.Joints()

#joints_home2 = t_home1_joints
#t_home2 = RDK.Item('Home2', ITEM_TYPE_TARGET)
#if t_home2.Valid():
#    t_home2_joints = t_home2.Joints()


def joint_move(j1, j2, ndof=6):
    '''Strip a joint move between two points (j1, j2) in small movements (STEP_DEG)'''
    # Check if j1 and j2 come from a matrix column
    if not type(j1) is list:
        j1 = j1.tolist()
    if not type(j2) is list:
        j2 = j2.tolist()

    # Get the joint shift that moves the most
    max_dj = 0
    dj = []
    for i in range(ndof):
        dji = j2[i] - j1[i]
        dj.append(dji)
        max_dj = max(max_dj, abs(dji))

    # Calculate in how many steps it should be cut
    size_list = int(max_dj / STEP_DEG)
    if size_list < 1:
        return Mat()

    # Calculate the delta per joint for each iteration
    for i in range(ndof):
        dj[i] = dj[i] / size_list

    # Build a matrix to go from j1 to j2 by steps of STEP_DEG
    j_list = Mat(ndof, size_list)
    for j in range(size_list):
        for i in range(ndof):
            j_list[i, j] = j1[i] + j * dj[i]
    return j_list


#test = joint_move([10,20,30,40,50,60], [10,21,35,40,60,60])
#print(test)
#quit()

# Get all programs available in the station as pointers
programs = RDK.ItemList(ITEM_TYPE_PROGRAM, False)

# Turn of auto rendering, if desired (Faster)
RDK.Render(RENDER_ALWAYS)

if True:
    # Option 1: accurate but might take more time. It is not affected by different robot speeds
    # Important! We assume we go Home
    prog_count = 0
    prog_total = len(programs)

    # Let's assume we always start from a home/safe position
    joints_last = joints_home

    # Iterate through each program
    for prog in programs:
        # Get the program name
        name = prog.Name()

        # Get the program as a list of joint values
        progok_jlist = prog.InstructionListJoints(STEP_MM, STEP_DEG)
        progok = progok_jlist[0]  # String that indicates if there are any issues with the program
        jlist = progok_jlist[1]  # List of joints

        # Check that the program is correct and has at least a movement
        njoints = jlist.size(1)
        if njoints < 1:
            print("Program %s has no movements" % name)
            continue

        if progok != "Success":
            raise Exception("Problems with program %s: %s. A finer tolerance might be required if the path is correct." % (name, progok))

        # Get the approach and retract movements, build a matrix with all the movements: approach from Home, program, retract to home
        approach = joint_move(joints_last, jlist[:, 0])
        retract = joint_move(jlist[:, -1], joints_home)
        jlist_all = catH(catH(approach, jlist[:6, :]), retract)

        # Iterate through all joints in the matrix and check for collisions
        njoints_all = jlist_all.size(1)
        for i in range(njoints_all):
            ji = jlist_all[:, i].tolist()
            robot.setJoints(ji)
            # Update a message in RoboDK from time to time
            if i % 5 == 0:
                msg = "Checking %s (%.1f %%) - (%i/%i)" % (name, 100.0 * (i / njoints_all), prog_count + 1, prog_total)
                print(msg)
                RDK.ShowMessage(msg, False)

            # Check collisions (this might take some time depending on the collision map and complexity of the cell)
            if RDK.Collisions() > 0:
                raise Exception("Collision detected for %s!!! Robot stopped" % name)

            # Render from time to time even if we have render deactivated
            if not RENDER_ALWAYS and i % 100 == 0:
                RDK.Render()

        msg = "No collisions detected for %s" % name
        print(msg)
        RDK.ShowMessage(msg, False)
        prog_count = prog_count + 1

else:
    # Option 2: less accurate. Sections with faster speed are less likely to detect a collision
    # This is the default collision check in RoboDK when collision checking is activated
    RDK.setSimulationSpeed(2)
    for prog in programs:
        prog.RunProgram()
        while prog.Busy():
            if RDK.Collisions() > 0:
                programs = RDK.ItemList(ITEM_TYPE_PROGRAM, False)
                for prog in programs:
                    prog.Stop()
                raise Exception("Collision detected!!! Robots stopped")

RDK.ShowMessage("No collisions detected!")
