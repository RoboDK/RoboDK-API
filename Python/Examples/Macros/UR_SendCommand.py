# This macro shows how to send UR code (URscript) to the robot. The robot will execute it on the fly.

from robodk.robolink import *  # RoboDK API
from robodk.robomath import *  # Robot toolbox
import threading
import time
import serial
import socket

#HOST = "192.167.0.4" # The remote host - Robot
#PORT = 30002 # The same port as used by the server
#s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#s.connect((HOST, PORT))
#time.sleep(0.5)

RDK = Robolink()
robot = RDK.Item('UR5e', ITEM_TYPE_ROBOT)

# Get the robot IP and port
ROBOT_HOST, ROBOT_PORT, remote_path, ftp_user, ftp_pass = robot.ConnectionParams()

# Override the port set in RoboDK so that it corresponds to UR RTDE
ROBOT_PORT = 30002


def driver_movej_pose(pose):
    """Provide a robot pose (TCP with respect to the reference frame)"""

    # Move the robot to the desired pose in RoboDK
    robot.MoveJ(pose)

    # Retrieve the tool pose to update the robot
    pose_tool = robot.PoseTool()

    # Retrieve the robot joints to send (important to virtually move the robot there first)
    joints = robot.Joints()

    # Convert degrees to radians
    joints_rad = []
    for j in joints.list():
        joints_rad.append(j * pi / 180)

    # Send required information to the robot
    string = ""
    x, y, z, u, v, w = Pose_2_UR(pose_tool)
    string += "set_tcp(p[%.6f,%.6f,%.6f,%.6f,%.6f,%.6f])\n" % (x * .001, y * .001, z * .001, u, v, w)
    string += "movej([%.6f,%.6f,%.6f,%.6f,%.6f,%.6f])\n" % tuple(joints_rad)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ROBOT_PORT = 30002
    s.connect((ROBOT_HOST, ROBOT_PORT))
    s.send(string.encode('utf-8'))
    time.sleep(0.5)
    received = s.recv(4096)
    #print(received)
    #from rtde import serialize
    #returned = serialize.Message.unpack(received)
    #print(returned)

    return


# Test moving the robot to the position defined in RoboDK
driver_movej_pose(robot.Pose())
