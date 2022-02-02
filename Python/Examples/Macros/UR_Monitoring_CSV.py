# This script creates a thread to monitor the position and other variables from a real UR robot and stores the data to a CSV file
# With this script running, RoboDK will save a CSV file of the robot status
#
# Press F5 to run the script
# Or visit: http://www.robodk.com/doc/en/PythonAPI/
from robodk.robolink import *  # API to communicate with RoboDK
from robodk.robomath import *  # Robot toolbox
import threading
import socket
import struct
import os
import time

TOLERANCE_JOINTS_REFRESH = 1e9  # Refresh the screen every time the robot position changes by this much (in deg)
RETRIEVE_JOINTS_ONCE = False  # If True, the current robot position will be retrieved once only
SAVE_CSV_FILE = True  # If True, the position and speed of the TCP will be recorded with a time stamp

# Create targets given a tolerance in degrees
CREATE_TARGETS = False
TOLERANCE_JOINTS_NEWTARGET = 1e9  # tolerance in degrees

REFRESH_RATE = 0.01  # Display rate in RoboDK

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
UR_GET_JOINT_POSITIONS = 252  # Real Joint Position
UR_GET_JOINT_SPEEDS = 300  # Real Joint Speeds
UR_GET_JOINT_CURRENTS = 348
UR_GET_TCP_POSITION = 444  # Real TCP position
UR_GET_TCP_SPEED = 492  # Real TCP speed
UR_GET_TCP_FORCES = 540
UR_GET_INPUTS = (86 - 32) * 8 + 252
UR_GET_OUTPUTS = (131 - 32) * 8 + 252


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
    fmt = '!'
    for i in range(nval):
        fmt += 'd'
    return list(struct.unpack_from(fmt, buf, offset))  #return list(struct.unpack_from("!dddddd", buf, offset))


# Get packet bits
def packet_value_bin(buf, offset, nval=8):
    if len(buf) < offset + nval:
        print("Not available offset (maybe older Polyscope version?): %i - %i" % (len(buf), offset))
        return None
    hex_list = ''
    return ''.join(format(x, '02x') for x in buf[offset:(offset + nval)])


#########################################################################

# Enter RoboDK IP and Port
ROBOT_IP = None  #'192.168.2.31'
ROBOT_PORT = 30003

# Start RoboDK API
RDK = Robolink()

# Retrieve a robot
robot = RDK.ItemUserPick('Select a UR robot to monitor', ITEM_TYPE_ROBOT)
if not robot.Valid():
    quit()

robotname = robot.Name()
print("Using robot %s" % robotname)

# Retrieve Robot's IP:
if ROBOT_IP is None:
    ip, port, path, ftpuser, ftppass = robot.ConnectionParams()
    ROBOT_IP = ip

if SAVE_CSV_FILE:
    # Save monitoring to file:
    file_path = RDK.getParam('FILE_OPENSTATION')[:-4] + '_Monitoring_%s_%s.csv' % (robotname, time.strftime("%Y-%m-%d-%Hh%Mm%Ss", time.gmtime()))
    print("Monitoring robot %s to %s" % (robotname, file_path))
    fid = open(file_path, 'w')
    fid.write('time (s), Speed (m/s), Speed (rad/s), J1 (deg), J2 (deg), J3 (deg), J4 (deg), J5 (deg), J6 (deg), TCP X (m), TCP Y (m), TCP Z (m), TCP u (rad), TCP v (rad), TCP w (rad), Speed X (m/s), Speed Y (m/s), Speed Z (m/s), Speed u (rad/s), Speed v (rad/s), Speed w (rad/s), Inputs, Outputs\n')
    tic()


# Action to take when a new packet arrives
def on_packet(packet, packet_id):
    global ROBOT_JOINTS
    # Retrieve desired information from a packet
    rob_joints_RAD = packet_value(packet, UR_GET_JOINT_POSITIONS)
    ROBOT_JOINTS = [ji * 180.0 / pi for ji in rob_joints_RAD]
    ROBOT_TCP_XYZUVW = packet_value(packet, UR_GET_TCP_POSITION)
    ROBOT_TCP_SPEED = packet_value(packet, UR_GET_TCP_SPEED)
    ROBOT_INPUTS = packet_value_bin(packet, UR_GET_INPUTS)
    ROBOT_OUTPUTS = packet_value_bin(packet, UR_GET_OUTPUTS)
    #print("Output:")
    #print(ROBOT_OUTPUTS)

    #ROBOT_SPEED = packet_value(packet, UR_GET_JOINT_SPEEDS)
    #ROBOT_CURRENT = packet_value(packet, UR_GET_JOINT_CURRENTS)
    #print(ROBOT_JOINTS)

    # Record once every 5 packets (125/5=25 Hz)
    if SAVE_CSV_FILE:
        if packet_id % 5 == 0:
            fid.write(str(toc()))  # Write time stamp in seconds
            fid.write(',%.6f' % norm(ROBOT_TCP_SPEED[0:3]))  # Position speed
            fid.write(',%.6f' % norm(ROBOT_TCP_SPEED[3:6]))  # Orientation speed

            for value in ROBOT_JOINTS:
                fid.write(',%.6f' % value)

            for value in ROBOT_TCP_XYZUVW:
                fid.write(',%.6f' % value)

            for value in ROBOT_TCP_SPEED:
                fid.write(',%.6f' % value)

            fid.write(',' + ROBOT_INPUTS)
            fid.write(',' + ROBOT_OUTPUTS)
            fid.write('\n')


# Monitor thread to retrieve information from the robot
def UR_Monitor():
    while True:
        print("Connecting to robot %s -> %s:%i" % (robotname, ROBOT_IP, ROBOT_PORT))
        rt_socket = socket.create_connection((ROBOT_IP, ROBOT_PORT))
        print("Connected")
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
                    on_packet(packet, packet_count)
                    packet_count += 1
                    if packet_count % 250 == 0:
                        t_now = time.time()
                        msg = "Monitoring %s at %.1f packets per second" % (robotname, packet_count / (t_now - packet_time_last))
                        print(msg)
                        RDK.ShowMessage(msg, False)
                        packet_count = 0
                        packet_time_last = t_now

        rt_socket.close()


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
