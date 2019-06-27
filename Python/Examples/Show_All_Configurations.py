# This example shows how to calculate all the possible joints configurations to attain the current robot position
# This example also provides information about the configuration status (Front/Back, ElbowUp/ElbowDown, Flip/NonFlip)
from robolink import *    # API to communicate with RoboDK
from robodk import *      # basic matrix operations
RDK = Robolink()

# Get the first robot available
robot = RDK.Item('', ITEM_TYPE_ROBOT)
if not robot.Valid():
    raise Exception("No robot in the station!")

# Get the current robot joints
robot_joints = robot.Joints()

# Get the robot position from the joints (calculate forward kinematics)
# This is the position of the robot flange with respect to the robot base
robot_position = robot.SolveFK(robot_joints)

# Get the robot configuration (robot joint state) as 0/1 bits
robot_config = robot.JointsConfig(robot_joints)

# If desired, calculate a new robot position relative to the tool
new_robot_position = robot_position*transl(0,0,0)*rotz(0)

# Calculate the new robot joints
joints_options = robot.SolveIK_All(new_robot_position)

if joints_options.size(1) < 1:
    raise Exception("No robot solution!! The new position is too far, out of reach or close to a singularity")

print("Possible joint configurations to attain this position:")
for joints in joints_options:
    # Filter joints (additional information provided by SolveIK_All is not required):
    joints = joints[0:6]
    
    # Get the robot configuration for the new joints
    cnf_flags = robot.JointsConfig(joints).list()

    # Provide a description message for each solution:
    cnf_flags_str = ['','','']
    cnf_flags_str[0] = "Rear" if cnf_flags[0] != 0 else "Front"
    cnf_flags_str[1] = "Down" if cnf_flags[1] != 0 else "Up"
    cnf_flags_str[2] = "Flip" if cnf_flags[2] != 0 else "NonFlip"
    print("%.1f , %.1f , %.1f , %.1f , %.1f , %.1f ,   %s , %s , %s" % tuple(joints + cnf_flags_str))

    # Move the robot to the new position
    robot.MoveJ(joints)
    

