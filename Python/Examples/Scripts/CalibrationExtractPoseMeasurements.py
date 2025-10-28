# This script extracts the measurement poses as reference frames from a robot calibration project

from robodk import *  # API to communicate with RoboDK
from robolink import *
import tempfile

# Force adding an additional pose to the measured reference
FORCE_POSE_OFFSET = transl(0, 0, 0)

# Start RoboDK API
RDK = Robolink()

# Select the robot
calib = RDK.ItemUserPick('Select a calibration project', ITEM_TYPE_CALIBPROJECT)
if not calib.Valid():
    RDK.ShowMessage("No calibration project selected or available", False)
    quit()
    
measframe = RDK.Item("Measurements reference", ITEM_TYPE_FRAME)
if not measframe.Valid():
    measframe = calib.getLink(ITEM_TYPE_FRAME)
    if not measframe.Valid():
        robot = calib.getLink(ITEM_TYPE_ROBOT)
        if not robot.Valid():
            robot = RDK.ItemUserPick('Select a robot', ITEM_TYPE_ROBOT)
            if not robot.Valid():
                RDK.ShowMessage("Add a robot to your station and link it to your calibration project", False)
                quit()
                
        measframe = robot.Parent()

# Create a temporary file to save the measurements before importing them in RoboDK
temp_dir = tempfile.gettempdir()
temp_csv_file = temp_dir + '/RoboDK-Calibration-Measurements.csv'

# Types of measurements:
meas_options = ["Base", "Tool", "Calibration", "Validation"]
meas_idx = 1

# Ask the user to enter the type of measurement to extract:
str_options = ""
for idx, meastype in enumerate(meas_options):
    str_options += "  %i -> %s\n" % (idx+1, meas_options[idx])
    
meas_idx = InputDialog("What type of mesaurement would you like to extract?\n" + str_options + "\nEnter a number 1-4:", 1)
if meas_idx is None:
    quit()
    
meas_idx = int(meas_idx)
meas_idx = min(max(meas_idx, 1), 4)
meas_idx = meas_idx - 1
meastype = meas_options[meas_idx]

# Save the measurements to a temporary directory
print(calib.setParam("SaveTable"+meastype, temp_csv_file))
    
print("Using measurement reference: " + measframe.Name())
csvdata = LoadList(temp_csv_file)

if len(csvdata) < 2 or len(csvdata[0]) < 18:
    RDK.ShowMessage("No pose measurements found", False)
    quit()

# Retrieve the TCP (for 6DOF measurements it should be the same TCP that applies to all measurements)
if False:
    xyzwpr_tcp = csvdata[1][12:18]
    #x,y,z,w,p,r = xyzwpr_tcp  #[-135.22663, -53.15329,  71.31105,  -3.13948*180.0/pi,   0.00114*180.0/pi,  -1.15271*180.0/pi]
    #xyzwpr_tcp = [x,y,z,w,p,r]

    htcp = TxyzRxyz_2_Pose(xyzwpr_tcp)

    # Force to shift the TCP a specific value. For example, to check accuracy at the origin of the tool.
    shift_tcp = invH(htcp)
    #shift_tcp = eye(4)

    htcp = htcp * shift_tcp

RDK.Render(False)

pattern_name = "M. " + meastype + " "
# Delete previous poses, if any:
for i in range(500):
    itm = RDK.Item(pattern_name + str(i+1))
    if itm.Valid() and itm.Parent() == measframe:
        print("Deleting item " + str(i))
        itm.Delete()        
    else:
        break

# Iterate between consecutive points and check distances
num_points = len(csvdata) - 1
count_points = 0
for i in range(1, num_points):
    # TCP pose (i) measured by the tracker
    xyzwpr = csvdata[i][6:12]
    x,y,z,w,p,r = xyzwpr
    if (abs(x) + abs(y) + abs(z)) < 1e-3:
        print("Measurement %i incomplete" % i)
        continue
    
    print("Adding measurement " + str(i))
    count_points = count_points + 1
    
    # hi_ref = TxyzRxyz_2_Pose(xyzwpr) * shift_tcp
    hi_ref = TxyzRxyz_2_Pose(xyzwpr) * FORCE_POSE_OFFSET
    new_frame = RDK.AddFrame(pattern_name + str(i), measframe)
    new_frame.setPose(hi_ref)

    # Robot joints for point i
    # ji = csvdata[i][0:6]

    # Calculate the pose (homogeneous matrix) of the TCP using nominal kinematics (hi_nom)
    #robot.setAccuracyActive(False)
    #hi_nom = robot.SolveFK(ji) * htcp

    # Calculate TCP using accurate kinematics (hi_acc)
    #robot.setAccuracyActive(True)
    #hi_acc = robot.SolveFK(ji) * htcp


RDK.Render(True)
RDK.ShowMessage("Extracted %i poses" % count_points, False)