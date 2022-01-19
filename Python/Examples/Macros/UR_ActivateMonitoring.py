# This script creates a thread to monitor the position and other variables from a real UR robot
# With this script active, RoboDK will create a new target when the robot is moved a certain tolerance
#
# More information about the RoboDK API here:
# https://robodk.com/doc/en/RoboDK-API.html
# Press F5 to run the script
# Or visit: https://robodk.com/doc/en/PythonAPI/index.html
from robodk.robolink import *    # API to communicate with RoboDK
from robodk.robomath import *    # Robot toolbox
import threading
import socket
import struct
import os
import time

# Refresh the screen every time the robot position changes
TOLERANCE_JOINTS_REFRESH = 0.1
RETRIEVE_JOINTS_ONCE = False  # If True, the current robot position will be retrieved once only

# Create targets given a tolerance in degrees
CREATE_TARGETS = False
TOLERANCE_JOINTS_NEWTARGET = 10  # in degrees

REFRESH_RATE = 0.01

# Make current robot joints accessible in case we run it on a separate thread
global ROBOT_JOINTS


# Procedure to check if robot joint positions are different according to a certain tolerance
def Robot_Joints_Check(jA, jB, tolerance_deg=1):
    if jA is None:
        return True

    for i in range(6):
        if abs(jA[i] - jB[i]) > tolerance_deg * pi / 180:
            return True
    return False


#########################################################################
# Byte shifts to point to the right byte data inside a packet
UR_GET_TIME = 1
UR_GET_JOINT_POSITIONS = 252
UR_GET_JOINT_SPEEDS = 300
UR_GET_JOINT_CURRENTS = 348
UR_GET_TCP_FORCES = 540


# Get packet size according to the byte array
def packet_size(buf):
    if len(buf) < 4:
        return 0
    return struct.unpack_from("!i", buf, 0)[0]


# Check if a packet is complete
def packet_check(buf):
    msg_sz = packet_size(buf)
    if len(buf) < msg_sz:
        print("Incorrect packet size %i vs %i" % (msg_sz, len(buf)))
        return False

    return True


# Get specific information from a packet
def packet_value(buf, offset, nval=6):
    if len(buf) < offset + nval:
        print("Not available offset (maybe older Polyscope version?): %i - %i" % (len(buf), offset))
        return None
    format = '!'
    for i in range(nval):
        format += 'd'
    return list(struct.unpack_from(format, buf, offset))  #return list(struct.unpack_from("!dddddd", buf, offset))


# Action to take when a new packet arrives
def on_packet(packet):
    global ROBOT_JOINTS
    # Retrieve desired information from a packet
    rob_joints_RAD = packet_value(packet, UR_GET_JOINT_POSITIONS)
    ROBOT_JOINTS = [ji * 180.0 / pi for ji in rob_joints_RAD]
    #ROBOT_SPEED = packet_value(packet, UR_GET_JOINT_SPEEDS)
    #ROBOT_CURRENT = packet_value(packet, UR_GET_JOINT_CURRENTS)
    #print(ROBOT_JOINTS)


# Monitor thread to retrieve information from the robot
def UR_Monitor():
    while True:
        rt_socket = socket.create_connection((ROBOT_IP, ROBOT_PORT))
        buf = b''
        packet_count = 0
        packet_time_last = time.time()
        while True:
            more = rt_socket.recv(4096)
            if more:
                buf = buf + more
                if packet_check(buf):
                    packet_len = packet_size(buf)
                    packet, buf = buf[:packet_len], buf[packet_len:]
                    on_packet(packet)
                    packet_count += 1
                    if packet_count % 125 == 0:
                        t_now = time.time()
                        print("Monitoring at %.1f packets per second" % (packet_count / (t_now - packet_time_last)))
                        packet_count = 0
                        packet_time_last = t_now

        rt_socket.close()


#########################################################################

# Enter RoboDK IP and Port
ROBOT_IP = None  #'192.168.2.31'
ROBOT_PORT = 30003

# Start RoboDK API
RDK = Robolink()

# Retrieve a robot
robot = RDK.ItemUserPick('Select a UR robot to retrieve current position', ITEM_TYPE_ROBOT)
if not robot.Valid():
    quit()

# Retrieve Robot's IP:
if ROBOT_IP is None:
    ip, port, path, ftpuser, ftppass = robot.ConnectionParams()
    ROBOT_IP = ip

ROBOT_JOINTS = None
last_joints_target = None
last_joints_refresh = None

# Start the Robot Monitor thread
#q = queue.Queue()
t = threading.Thread(target=UR_Monitor)
t.daemon = True
t.start()
#UR_Monitor()

# Start the main loop to refresh RoboDK and create targets/programs automatically
target_count = 0
while True:
    # Wait for a valid robot joints reading
    if ROBOT_JOINTS is None:
        continue

    # Set the robot to that position
    if Robot_Joints_Check(last_joints_refresh, ROBOT_JOINTS, TOLERANCE_JOINTS_REFRESH):
        last_joints_refresh = ROBOT_JOINTS
        robot.setJoints(ROBOT_JOINTS)

    # Stop here if we need only the current position
    if RETRIEVE_JOINTS_ONCE:
        quit(0)

    # Check if the robot has moved enough to create a new target
    if CREATE_TARGETS and Robot_Joints_Check(last_joints_target, ROBOT_JOINTS, TOLERANCE_JOINTS_NEWTARGET):
        last_joints_target = ROBOT_JOINTS
        target_count = target_count + 1
        newtarget = RDK.AddTarget('T %i' % target_count, 0, robot)

    # Take a short break
    pause(REFRESH_RATE)
