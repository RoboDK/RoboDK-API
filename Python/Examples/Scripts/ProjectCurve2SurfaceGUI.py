# This script shows an example to create a raster curve that can be added programmatically to a RoboDK station
# The curve can be optionally projected to an existing object (either along the curve normals or a projection the closest surface)

# projection types (for AddCurve, as defined in robodk.robolink):
#PROJECTION_NONE                = 0 # No curve projection
#PROJECTION_CLOSEST             = 1 # The projection will the closest point on the surface
#PROJECTION_ALONG_NORMAL        = 2 # The projection will be done along the normal.
#PROJECTION_ALONG_NORMAL_RECALC = 3 # The projection will be done along the normal. Furthermore, the normal will be recalculated according to the surface normal.
#
# More information about the RoboDK API here:
# https://robodk.com/doc/en/PythonAPI/robolink.html
# https://robodk.com/doc/en/RoboDK-API.html
#
# This macro uses advanced Python programming. It uses the exec() and eval() statements to execute Python code from a string generated on the fly.
# The GUI is created automatically based on the variables defined in PARAM_VARS (global variables) and PARAM_LABELS (description to show on the menu)

# Press F5 to run the script
# Type help("robodk.robolink") or help("robodk.robomath") for more information

from robodk.robolink import *    # API to communicate with RoboDK
from robodk.robomath import *    # Robot toolbox
import threading

# Set default/global parameters. This is only useful for the first time we execute this macro on a new RDK file.
# These global parameters are saved with the RoboDK station as Station parameters (right click the Station root and select "Station Parameters" to see the parameters saved)
SIZE_X = 500  # Size along the X axis
SIZE_Y = 500  # Size along the Y axis
STEP_X = 20  # Step along the X axis
STEP_Y = 50  # Step along the Y axis
SPEED_OPERATION = 20  # Operation speed
REPEAT_TIMES = 3  # Number of times to run the same program
REPEAT_OFFSET = 2  # Offset along Z axis in mm
ANGLE_TCP_X = 10
ANGLE_TCP_Y = 20
OVERTRAVEL = 25

REMEMBER_LAST_VALUES = True

#--------------------------------------------
# List the variables that will be remembered by the station and provided through the GUI
PARAM_VARS = []
PARAM_LABELS = []
PARAM_VARS += ["STEP_X", "STEP_Y"]
PARAM_LABELS += ["Step along X (mm)", "Step along Y (mm)"]

PARAM_VARS += ["SPEED_OPERATION"]
PARAM_LABELS += ["Operation speed (mm/s)"]

PARAM_VARS += ["REPEAT_TIMES", "REPEAT_OFFSET"]
PARAM_LABELS += ["Repeat times", "Repeat Offset along Z (mm)"]

PARAM_VARS += ["ANGLE_TCP_X", "ANGLE_TCP_Y"]
PARAM_LABELS += ["Tool angle X (deg)", "Tool angle Y (deg)"]

PARAM_VARS += ["OVERTRAVEL"]
PARAM_LABELS += ["Overtravel (mm)"]

PARAM_VARS += ["SIZE_X", "SIZE_Y"]
PARAM_LABELS += ["Size along X (mm)", "Size along Y (mm)"]

# Optionally provide a part name to auto select it without asking the user
PART_NAME = None  # 'Paint Part'

#------------------------------------------------------------------
#--------------- PROGRAM START ---------------------

# Initialize the RoboDK API
RDK = Robolink()

# Set other constants:
TOL_PROJ_Z = sqrt(2)  # Tolerance to ignore a point as a ratio (if it falls through a window for example)

#---------------------------------------------
# First: Retrieve the part item
# Name of the reference used for the path projection
#

if PART_NAME is None:
    PART = RDK.ItemUserPick("Select a part", ITEM_TYPE_OBJECT)
    if PART is None:
        print("Operation cancelled by user")
        quit()
else:
    PART = RDK.Item(PART_NAME, ITEM_TYPE_OBJECT)

if not PART.Valid():
    msg = "The selected part is not valid or not available"
    RDK.ShowMessage(msg, False)
    raise Exception(msg)

#---------------------------------------------
# List all the reference frames that we want to use to create
# raster paths (references attached to the object reference
part_ref = PART.Parent()

# Get the list of items attached to the part reference
ref_pattern_candidates = part_ref.Childs()
# Iterate through these child items and list the reference frames
# optionally add ignore in the name
REF_PATTERN_LIST = []
for ref_i in ref_pattern_candidates:
    if ref_i.Type() == ITEM_TYPE_FRAME and (not "ignore" in ref_i.Name()):
        REF_PATTERN_LIST.append(ref_i)

if len(REF_PATTERN_LIST) <= 0:
    RDK.ShowMessage("No reference frames found. Add one or more frames attached to " + part_ref.Name())
    quit()

#---------------------------------------------
# Retrieve Global parameters or set defaults as found in RoboDK
if REMEMBER_LAST_VALUES:
    for strvar in PARAM_VARS:
        var_value = RDK.getParam(strvar)
        if var_value is not None:
            exec(strvar + " = " + str(var_value))

#---------------------------------------------
# Load GUI tools
from tkinter import *
import tkinter.font as font

# Generate the main window
root = Tk()

# define a label to notify the user
NotifyGUI = StringVar()


#---------------------------------------------
# Function to change the coordinates of a point and a normal
# given a pose. The point and the normal must be in xyzijk format
def Pose_x_XYZijk(pose, xyzijk):
    new_xyz = pose * xyzijk[0:3]
    new_ijk = pose[:3, :3] * xyzijk[3:6]
    return new_xyz + new_ijk


#---------------------------------------------
# Function definition to create a list of points as zig-zag pattern (curve)
def GridPoints(ref, size_x, size_y, step_x, step_y):
    """Generates a list of points given dimensions of a grid"""
    points = []
    xx = 0
    flip = 1
    while xx <= size_x:
        yy = 0
        if flip > 0:
            yy = 0
        else:
            yy = size_y

        while yy <= size_y and yy >= 0:
            # Create a new point as [x,y,z , i,j,k]
            xyzijk = Pose_x_XYZijk(ref, [xx, yy, 0, 0, 0, -1])
            points.append(xyzijk)
            yy = yy + flip * step_y

        xx = xx + step_x
        flip = -1 * flip
    return points


#---------------------------------------------
# Function definition to offset a list of points
def PointsOffset(points, offset):
    points_offset = []
    for pi in points:
        x, y, z, i, j, k = pi
        xyz2 = add3([x, y, z], mult3([i, j, k], offset))
        xyzijk2 = xyz2 + [i, j, k]
        points_offset.append(xyzijk2)
    return points_offset


# Show message through the GUI, RoboDK and the console
def ShowMsg(msg):
    print(msg)
    NotifyGUI.set(msg)
    root.update_idletasks()
    RDK.ShowMessage(msg, False)


#---------------------------------------------
# Main program call that will project the path to a surface
def CreatePaths():
    prog_name_list = []
    for REF in REF_PATTERN_LIST:
        # Retrieve the reference name
        REF_NAME = REF.Name()

        ShowMsg("Working with %s ..." % REF_NAME)

        # Get the pose of the reference with respect to the part:
        pose_ref_wrt_part = invH(PART.Parent().PoseAbs()) * REF.PoseAbs()

        # For later: calculate the inverse pose (part with respect to the reference)
        pose_part_wrt_ref = invH(pose_ref_wrt_part)

        # Generate the curve path
        # IMPORTANT: the point coordinates must be relative to the part reference
        points = GridPoints(pose_ref_wrt_part, SIZE_X, SIZE_Y, STEP_X, STEP_Y)
        # points is a list of points with respect to the part
        # Another option is to load the grid from a CSV file:
        #file = RDK.getParam('PATH_OPENSTATION') + '/test.csv'
        #POINTS = LoadList(file)
        #POINTS.pop(0)
        # display the points
        #print(CURVE)
        if len(points) == 0:
            ShowMsg("No points found for: " + REF_NAME)
            continue

        # Project the points on the object surface
        #pts_projected = PART.AddPoints(POINTS)
        ShowMsg("Projecting %s to surface..." % REF_NAME)
        points_projected = PART.ProjectPoints(Mat(points).tr(), PROJECTION_ALONG_NORMAL_RECALC)

        # Patch
        points_projected = points_projected.tr().rows

        points_projected_filtered = []

        ShowMsg("Filtering %s..." % REF_NAME)

        # Remember the last valid projection
        pti_last = None
        for i in range(0, len(points_projected) - 1):
            # retrieve projected and non projected points, with respect to the reference frame
            # retrieve the next point to test if the projection went too far
            pti = Pose_x_XYZijk(pose_part_wrt_ref, points[i])
            pti_proj = Pose_x_XYZijk(pose_part_wrt_ref, points_projected[i])

            # Ignore non projected points (z coordinate is 0 mm, prevent numerical errors as well)
            if abs(pti_proj[2]) < 0.1:
                continue

            # Check if we have the first valid projected point
            if pti_last is None:
                points_projected_filtered.append(pti_proj)
                pti_last = pti
                pti_proj_last = pti_proj
                continue

            # Check if the projection falls through a "window" or "climbs" a wall with respect to the previous pointS
            if distance(pti_proj, pti_proj_last) < TOL_PROJ_Z * distance(pti, pti_last):
                # List the point as valid
                points_projected_filtered.append(pti_proj)

                # Remember the last valid projection
                pti_last = pti
                pti_proj_last = pti_proj

        # Remove any previously generated objects with the same name as the reference frame:
        obj_delete = RDK.Item(REF_NAME, ITEM_TYPE_OBJECT)
        if obj_delete.Valid():
            obj_delete.Delete()

        ShowMsg("Creating object for %s..." % REF_NAME)
        # Add the points as an object in the RoboDK station tree
        points_object = RDK.AddCurve(points_projected_filtered)
        # Add the points to the reference and set the reference name
        points_object.setParent(REF)
        points_object.setName(REF_NAME)

        for rep in range(1, round(REPEAT_TIMES)):
            # Calculate a new curve with respect to the reference curve
            points_projected_filtered_rep = PointsOffset(points_projected_filtered, REPEAT_OFFSET * rep)

            #  Add the shifted curve without projecting it
            points_object = RDK.AddCurve(points_projected_filtered_rep, points_object, True, PROJECTION_NONE)

        curve_follow = RDK.Item(REF_NAME, ITEM_TYPE_MACHINING)
        if not curve_follow.Valid():
            curve_follow = RDK.AddMillingProject(REF_NAME)

        ShowMsg("Solving toolpath for %s" % REF_NAME)

        # Use the current reference frame:
        curve_follow.setPoseFrame(REF)

        # RoboDK 3.3.7 or later required:
        curve_follow.setSpeed(SPEED_OPERATION)
        curve_follow.setPoseTool(rotx(ANGLE_TCP_X * pi / 180.0) * roty(ANGLE_TCP_Y * pi / 180.0))
        prog, status = curve_follow.setMillingParameters(part=points_object)
        print(status)
        if status == 0:
            ShowMsg("Program %s generated successfully" % REF_NAME)
        else:
            ShowMsg("Issues found generating program %s!" % REF_NAME)

        # get the program name
        prog_name = prog.Name()
        prog_name_list.append(prog_name)

    # Create a new program that calls the auto generated program
    # Make sure we delete any previously generated programs with the same name
    ShowMsg("Creating Main program ...")
    prog_main_name = "Main" + PART.Name()
    prog_main = RDK.Item(prog_main_name, ITEM_TYPE_PROGRAM)
    if prog_main.Valid():
        prog_main.Delete()
    prog_main = RDK.AddProgram(prog_main_name)

    # Add a number of program calls to the first program by providing inline code
    #prog_main.RunCodeCustom("FOR i=1 TO 5", INSTRUCTION_INSERT_CODE)
    #prog_main.RunCodeCustom(prog_name, INSTRUCTION_CALL_PROGRAM)
    #prog_main.RunCodeCustom("NEXT", INSTRUCTION_INSERT_CODE)
    #for i in range(4):
    for pr_name in prog_name_list:
        prog_main.RunCodeCustom(pr_name, INSTRUCTION_CALL_PROGRAM)

    # Start the program simulation:
    prog_main.RunProgram()
    ShowMsg("Done!!")


#-----------------------------------------
# Create a GUI menu using tkinter

# Use StringVar variables linked to the global variables for the GUI
txtSpeed_Operation = StringVar()
txtSpeed_Operation.set(str(SPEED_OPERATION))

for strvar, hint in zip(PARAM_VARS, PARAM_LABELS):
    var = eval(strvar)
    txtvar = "txt" + strvar
    #txtSize_X = StringVar()
    #txtSize_X.set(str(SIZE_X))
    #Label(root, text="Window Size X (mm)").pack()
    #Entry(root, textvariable=txtSize_X).pack()
    exec(txtvar + " = StringVar()")
    exec(txtvar + ".set(str(" + str(var) + "))")
    exec("Label(root, text='" + hint + "').pack()")
    exec("Entry(root, textvariable=" + txtvar + ").pack()")


# Add a button and default action to execute the current choice of the user
def btnUpdate():
    # List the global variables so that we can read or modify the latest values
    #exec(PARAM_GLOBALS)
    def run_thread():
        try:
            for strvar in PARAM_VARS:
                #SIZE_X = float(txtSize_X.get())
                # Update global variable
                exec("%s = float(txt%s.get())" % (strvar, strvar), globals())

        except Exception as e:
            RDK.ShowMessage("Invalid input!! " + str(e), False)
            return

        # Remember the last settings in the RoboDK station
        for strvar in PARAM_VARS:
            value = eval(strvar)
            RDK.setParam(strvar, value)

        # Run the main program once all the global variables have been set
        CreatePaths()

    threading.Thread(target=run_thread).start()


# Add an update button that calls btnUpdate()
font_large = font.Font(family='Helvetica', size=18, weight=font.BOLD)
Label(root, text=" ").pack()  # Just a spacer
Label(root, textvariable=NotifyGUI).pack()  # information variable
Button(root, text='Update', font=font_large, width=20, height=3, command=btnUpdate, bg='green').pack()

# Set window name
window_title = "Create curve on Surface"
root.title(window_title)

# We can embed the window into RoboDK as a docked window
# Make sure the window title is unique
EmbedWindow(window_title)

# Important to display the graphical user interface
root.mainloop()
