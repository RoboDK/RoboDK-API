# This script retrieves the robot joints from a Fanuc controller and updates the robot in RoboDK
# Make sure to enter the correct IP, FTP username and password in the robot connection menu.

from robodk.robolink import *
import os
import sys
import time
import socket
import ftplib
from ftplib import FTP
import tempfile

print

TEMP_FILE_PATH = ''
#TEMP_FILE_PATH = tempfile.gettempdir()


def GetCurJoints():
    """Get the current robot joints based on the retrieved file"""
    FILE_CURPOS = TEMP_FILE_PATH + 'curpos.dg'
    joints = [0] * 20
    nDOFs = 0
    with open(FILE_CURPOS, 'r') as fid:
        lines = fid.readlines()
        for line in lines:
            line = line.strip()
            if line.startswith("Joint ") and ':' in line:
                lineinfo = line.replace(':', ' ').split(' ')
                lineinfo = [x for x in lineinfo if x]
                if len(lineinfo) >= 3:
                    jid = int(lineinfo[1])
                    jval = float(lineinfo[2])
                    joints[nDOFs] = jval
                    nDOFs += 1

                else:
                    print("Something is wrong: " + str(lineinfo))

    joints = joints[:nDOFs]
    return joints


def GetFilesFromFTP():
    """Retrieve files of interest from the robot controller"""
    ftpRobot.cwd("md:")
    ftpRobot.retrbinary('RETR curpos.dg', open(TEMP_FILE_PATH + 'curpos.dg', 'wb+').write)
    #ftpRobot.retrbinary('RETR prgstate.dg', open('prgstate.dg', 'wb+').write)
    #ftpRobot.cwd(RobotFTPPath)
    return


# Program start
if __name__ == "__main__":

    # Start the RoboDK API
    RDK = Robolink()
    robot = RDK.ItemUserPick("Select a robot to retrieve the position", ITEM_TYPE_ROBOT)

    # Retrieve robot parameters
    RobotFTPIP, port, RobotFTPUsername, RobotFTPUpassword, remotepath = robot.ConnectionParams()

    # Change current directory to this directory (temporary folder)
    folder_files = os.path.dirname(__file__)
    print("Program files directory: " + folder_files)
    os.chdir(folder_files)

    if (RobotFTPIP == ""):
        input("Robot FTP IP not defined, edit the top of the script to fix")
        sys.exit()

    if (RobotFTPUsername == ""):
        RobotFTPUsername = "anonymous"
        #input("Robot FTP username not defined, edit the top of the script to fix")
        #sys.exit()

    print("Trying to connect to: " + RobotFTPIP)
    ftpRobot = FTP(RobotFTPIP)  #Connect
    ftpRobot.login()
    GetFilesFromFTP()
    joints = GetCurJoints()

    if joints:
        robot.setJoints(joints)
        RDK.ShowMessage("Robot Joints updated to " + str(joints), False)
