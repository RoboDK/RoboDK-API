# This script shows how to filter an existing target as a pose
# This is useful for a robot that has been calibrated and we need to get the filtered pose
# Important: It is assumed that the robot will reach the pose with the calculated configuration

from robodk.robolink import *    # API to communicate with RoboDK
from robodk.robomath import *    # basic matrix operations


def XYZWPR_2_Pose(xyzwpr):
    # Convert X,Y,Z,A,B,C to a pose
    return KUKA_2_Pose(xyzwpr)


def Pose_2_XYZWPR(pose):
    # Convert a pose to X,Y,Z,A,B,C
    return Pose_2_KUKA(pose)


# Start the RoboDK API and retrieve the robot:
RDK = Robolink()
robot = RDK.Item('', ITEM_TYPE_ROBOT)
if not robot.Valid():
    raise Exception("Robot not available")

# Define the TCP
pose_tcp = XYZWPR_2_Pose([0, 0, 200, 0, 0, 0])

# Define the reference frame
pose_ref = XYZWPR_2_Pose([400, 0, 0, 0, 0, 0])

# Update the robot TCP and reference frame
robot.setTool(pose_tcp)
robot.setFrame(pose_ref)

# Accuracy can be ON or OFF:
# Very important for SolveFK and SolveIK (Forward/Inverse kinematics)
robot.setAccuracyActive(False)

# Define a nominal target in the joint space:
joints = [0, 0, 90, 0, 90, 0]

# Calculate the nominal robot position for the joint target:
# robot flange with respect to the robot base (4x4 pose)
pose_rob = robot.SolveFK(joints)

# Calculate pose_target: the TCP with respect to the reference frame
# (same value as shown in the Cartesian jog of the robot)
pose_target = invH(pose_ref) * pose_rob * pose_tcp

# The same pose target can be retrieved by calling robot.Pose() when the robot is at the target
# Example:
# robot.setJoints(joints)
# pose_target_2 = robot.Pose()

print('Target not filtered:')
print(joints)
print(Pose_2_XYZWPR(pose_target))
print('')

# Filter target: automatically filters a pose target according to calibrated kinematics
# IMPORTANT: Set the TCP and reference frame first
joints_approx = joints  # joints_approx must be within 20 deg
pose_target_filtered, real_joints = robot.FilterTarget(pose_target, joints_approx)
print('Target filtered:')
print(real_joints.tolist())
print(Pose_2_XYZWPR(pose_target_filtered))


##########################################
# The following procedure how the filterim mechanism works behind the scenes
# This procedure is equivalent to FilterTarget() and does not need to be used
def FilterTarget(target, ref, tcp):
    """Target: pose of the TCP (tcp) with respect to the reference frame (ref)
    jnts_ref: preferred joints for inverse kinematics calculation"""
    # First: we need to calculate the accurate inverse kinematics to calculate the accurate joint data for the desired target
    # Note: SolveIK and SolveFK take the robot into account (from the robot base frame to the robot flange)
    robot.setAccuracyActive(True)
    pose_rob = ref * target * invH(tcp)
    robot_joints = robot.SolveIK(pose_rob)
    # Second: Calculate the nominal forward kinematics as this is the calculation that the robot performs
    robot.setAccuracyActive(False)
    pose_rob_fixed = robot.SolveFK(robot_joints)
    target_filtered = invH(ref) * pose_rob_fixed * tcp
    return target_filtered


# We should get the same result by running the custom made filter:
#pose_target_filtered_2 = FilterTarget(pose_target, pose_ref, pose_tcp)
#print(Pose_2_XYZWPR(pose_target_filtered_2))