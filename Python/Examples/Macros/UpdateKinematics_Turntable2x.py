# This script allows you to define the turntable kinematics accoding to your KUKA KRC robot controller
# Modify the values according to the Machine data definition

# Define the name of your turntable in RoboDK (name in the RoboDK tree)
# Make sure the joint sense is set to [1,1] (do not invert axes)
turntable_name = "Positioner"

# KUKA values to model a 2 axis turntable
# ROOT_POINT: The ROOT Point is the position of the turntable with respect to the robot
# This value is not required to model the turntable,
# however, it represents the location of the turntable base with respect to the robot base
ROOT_POSE = [20.903679, 1929.991330, 209.270615, 0.905965, -0.140198, -179.285088]
#ROOT_POSE = None # Set to None to skip placing the turntable

# Enter the position of axis 1 with respect to the turntable ROOT point
# Variable: $ET1_TA1KR
ROOT_2_E1 = [0, 0, 0, 0, 90, 0]

# Enter the position of axis 2 with respect to axis 1
# KUKA SRC Variable: $ET1_TA2A1
E1_2_E2 = [75.581, 2.737, -5.883, 90.42, 89.373, 89.674]

# Enter the position of the turntable flange with respect to axis 2
# KUKA SRC Variable: $ET1_TFLA3
E2_2_Flange = [0, 0, 0, -90, 0.117, -179.898]

# Enter the position of the measurement point and flange
# Note: this value is not used
# KUKA SRC Variable: $ET1_TPINFL
Measurement_Point = [-850.078, 0, 0, 0, 0, 0]

#-------------------------------------------------------------------------
#-------------------------------------------------------------------------
#-------------------------------------------------------------------------
#-------------------------------------------------------------------------
#-------------------------------------------------------------------------
from robodk.robolink import *
from robodk.robomath import *
import math

# Calculate poses
pose_2_e1 = KUKA_2_Pose(ROOT_2_E1)
pose_2_e2 = KUKA_2_Pose(E1_2_E2)
pose_2_flange = KUKA_2_Pose(E2_2_Flange)
flange_2_point = KUKA_2_Pose(Measurement_Point)

#flange_Z = Measurement_Point[2]
#flange_angle_rad = math.atan2(Measurement_Point[1],Measurement_Point[0])
#flange_angle_deg = flange_angle_rad*180/pi
#flange_pose = transl(0,0,flange_Z) * rotz(flange_angle_rad)
#flange_pose_str = "transl(0,0,%.6f)*rotz(%.6f)" % (flange_Z, flange_angle_deg)


# Function to simulate the forward kinematics of a 2 axis mechanism given linking poses
# (simulation according to KUKA controller)
def FK_Turntable(ax12):
    pose_fk = pose_2_e1 * rotz(ax12[0] * pi / 180) * pose_2_e2 * rotz(ax12[1] * pi / 180) * pose_2_flange
    return pose_fk


# Start the RoboDK API
RDK = Robolink()

# Retrieve the turntable object in RoboDK
turntable = RDK.Item(turntable_name, ITEM_TYPE_ROBOT)
if not turntable.Valid():
    print("Turntable does not exist: " + turntable_name)
    quit()

# Simulate a list of points (moving axis 1 and 2 independently)
joints = []  # List of joints to test
points_kuka = []  # points according to KUKA kinematics
points_robodk = []  # points according to RoboDK kinematics

range_axis = [-90, -60, -30, 0, 30, 60, 90]
for ax1 in range_axis:
    joints.append([ax1, 0])

for ax2 in range_axis:
    joints.append([0, ax2])

print("List of points according to KUKA Kinematics (mm):")
for j in joints:
    pose_fk_kuka = FK_Turntable(j) * flange_2_point
    xyz_kuka = pose_fk_kuka.Pos()
    x, y, z = xyz_kuka
    print("%.3f, %.3f, %.3f" % (x, y, z))
    points_kuka.append(xyz_kuka)

print("\n\nUpdating turntable kinematics...")
# This operation can be done manually using the UI:
# Utilities-Calibrate Reference (if a turntable is provided as a robot and we calibrate using points)
pose_flange, stats = RDK.CalibrateReference(points_kuka, CALIBRATE_TURNTABLE_2X, False, turntable)

#----------------------------------------------------------------------------
# Important: RoboDK does not add a flange rotation, so we need to calculate it
turntable.setParam("KinematicsPoseTool", "transl(0,0,0)")  # this is redundant (the pose should already be eye(4))
joints_ref = [0, 0]
pose_fk_robodk = turntable.SolveFK(joints_ref)
pose_fk_kuka = FK_Turntable(joints_ref)
flange_pose_rdk = invH(pose_fk_robodk) * pose_fk_kuka
#flange_pose = transl(0,0,flange_Z) * rotz(flange_angle_rad)
#flange_pose_str = "transl(0,0,%.6f)*rotz(%.6f)" % (flange_Z, flange_angle_deg)
x, y, z, w, p, r = Pose_2_TxyzRxyz(flange_pose_rdk)
flange_pose_str = "transl(%.6f,%.6f,%.6f)*rotx(%.6f)*roty(%.6f)*rotz(%.6f)" % (x, y, z, w * 180 / pi, p * 180 / pi, r * 180 / pi)
turntable.setParam("KinematicsPoseTool", flange_pose_str)

#print(pose_flange)
#print("\nStatistics:")
#print(stats)

print("\nList of poinst according to RoboDK kinematics (mm):")
for i in range(len(joints)):
    jnts = joints[i]
    pose_fk = turntable.SolveFK(jnts) * flange_2_point
    xyz_robodk = pose_fk.Pos()
    points_robodk.append(xyz_robodk)
    x, y, z = xyz_robodk
    print("%.3f, %.3f, %.3f" % (x, y, z))

print("\nErrors (KUKA vs. RoboDK) (mm):")
max_error = -1
for i in range(len(joints)):
    jnts = joints[i]
    xyz_kuka = points_kuka[i]
    xyz_robodk = points_robodk[i]

    # Calculate error vector
    error = subs3(xyz_kuka, xyz_robodk)
    ex, ey, ez = error

    e_mm = norm(error)
    if e_mm > max_error:
        max_error = e_mm

    print("%.3f -> [%.3f, %.3f, %.3f]" % (e_mm, ex, ey, ez))

# Update the ROOT coordinate system, if provided
if ROOT_POSE is not None:
    print("\nTrying to update root pose")
    root_frame = turntable.Parent()
    if root_frame.type != ITEM_TYPE_FRAME:
        RDK.ShowMessage("Place your positionner on a reference frame")
        quit()

    # retrieve the robot base:
    robot_base = root_frame.Parent()
    if robot_base.type != ITEM_TYPE_FRAME:
        RDK.ShowMessage("Place the reference of your positionner directly attached to the robot base")
        quit()

    robot_base_childs = robot_base.Childs()
    if len(robot_base_childs) > 0 and robot_base_childs[0].type == ITEM_TYPE_ROBOT:
        pose_root = KUKA_2_Pose(ROOT_POSE)
        root_frame.setPose(pose_root)
        print("Root pose updated to: " + str(ROOT_POSE))

    else:
        RDK.ShowMessage("Place the reference of your positionner directly attached to the robot base (the robot must be attached to the robot base)")
        quit()
else:
    print("\nMake sure to manually update the root pose (turntable base coordinate system)")

# Done!
if max_error < 1e-3:
    print("\nCompleted successfully!\n\n")
else:
    print("\nCompleted with errors (%.3f mm)\n\n" % max_error)

quit()

#-----------------------------------------------------
#-----------------------------------------------------
#-----------------------------------------------------
#-----------------------------------------------------
#-----------------------------------------------------
#-----------------------------------------------------
# Example to create a 2 axis turntable using the API
robot_name = 'Turntable 2x'

# Joint values
joints_build = [0, 0]
joints_home = [0, 0]
lower_limits = [-120, -360]
upper_limits = [120, 360]

parameters = []
# Define the joint sense (set to +1 or -1 for each axis (+1 is used as a reference for the ABB IRB120 robot)
joints_senses = [+1, +1]

base_pose = eye(4)
tool_pose = eye(4)

# Retrieve all your items from RoboDK (they should be previously loaded manually or using the API's command RDK.AddFile())
DOFs = len(joints_build)
list_objects = []
for i in range(DOFs + 1):
    itm = None
    if i == 0:
        itm = RDK.Item(robot_name + ' Base', ITEM_TYPE_OBJECT)
    else:
        itm = RDK.Item(robot_name + ' ' + str(i), ITEM_TYPE_OBJECT)

    list_objects.append(itm)

# Create the robot/mechanism
turntable = RDK.BuildMechanism(MAKE_ROBOT_2R, list_objects, parameters, joints_build, joints_home, joints_senses, lower_limits, upper_limits, base_pose, tool_pose, robot_name)
if not turntable.Valid():
    print("Failed to create the robot. Check input values.")
    quit()
else:
    print("Robot/mechanism created: " + turntable.Name())
