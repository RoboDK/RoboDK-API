# This script allows you to load the same kinematics used in your UR robot controller. 
# You'll need a URP file generated using the real UR controller (not RoboDK or the UR simulator)
# This script will load the unique UR robot kinematics in RoboDK and you'll be able to switch between nominal and controller kinematics in the Parameters menu from the robot panel

import os
from robolink import *
import tkinter as tk
from tkinter import filedialog
import xml.etree.ElementTree as ET

# Define the (to be maintained by RoboDK only)
class Robolink2(Robolink):
    def UpdateKinematicsUR(self, robot, dh_ur, tolerance):
        self._check_connection()
        self._send_line('UpdateKinematicsUR')
        self._send_item(robot)
        self._send_matrix(dh_ur)
        self._send_array([tolerance])
        status = self._rec_int()
        msg = self._rec_line()
        errors_before = self._rec_array()
        errors_after = self._rec_array()
        self._check_status()
        return status, msg, errors_before.list(), errors_after.list()

# Start the RoboDK API
RDK = Robolink2()

# Select the robot to update
robot = RDK.ItemUserPick('Select a UR robot', ITEM_TYPE_ROBOT)
if not robot.Valid():
    RDK.ShowMessage("UR robot not found. Load your UR robot first from the RoboDK library")
    quit()

# Retrieve URP file
root = tk.Tk()
root.withdraw()
#root.lift()
root.attributes("-topmost", True)
rdk_path = RDK.getParam('PATH_OPENSTATION')
fileopen_urp = filedialog.askopenfilename(initialdir=rdk_path, title = "Select a URP file generated using Polyscope on the real robot (not generated using RoboDK or UR Simulator)", filetypes = (("URP files","*.urp"),("all files","*.*")))
if not fileopen_urp:
    quit()

# Read the compressed URP file
urp_xml = None
import gzip
with gzip.open(fileopen_urp, 'rb') as fid_gz:
    urp_xml = fid_gz.read()
    
# Retrieve the kinematic parameters from the URP file
dh_alpha = None
dh_a = None
dh_dTheta = None
dh_d = None

# Added support for old versions and new versions
urp_xml = urp_xml.decode('utf-8')
id_1 = urp_xml.index('<kinematics')
id_2 = urp_xml.index('</kinematics')

if id_1 >= 0 and id_2 > id_1:
    urp_xml = urp_xml[id_1:id_2+13]

    xml = ET.fromstring(urp_xml)
    #for kin_node in xml:#.iterfind('kinematics'):
    #    for child in kin_node:
    for child in xml:
        if child.tag == 'alpha':
            if len(child.attrib) == 0:
                # New version
                dh_alpha = []
                for d in child:
                    dh_alpha.append(float(d.text))
            else:
                value = child.attrib['value']
                dh_alpha = [float(v) for v in value.replace(' ','').split(',')]

            print('alpha: ' + str(dh_alpha))

        if child.tag == 'a':
            if len(child.attrib) == 0:
                # New version
                dh_a = []
                for d in child:
                    dh_a.append(float(d.text)*1000.0)
            else:
                value = child.attrib['value']
                dh_a = [float(v)*1000.0 for v in value.replace(' ','').split(',')]

            print('a: ' + str(dh_a))

        if child.tag == 'deltaTheta':
            if len(child.attrib) == 0:
                # New version
                dh_dTheta = []
                for d in child:
                    dh_dTheta.append(float(d.text))
            else:
                value = child.attrib['value']
                dh_dTheta = [float(v) for v in value.replace(' ','').split(',')]

            print('deltaTheta: ' + str(dh_dTheta))

        if child.tag == 'd':
            if len(child.attrib) == 0:
                # New version
                dh_d = []
                for d in child:
                    dh_d.append(float(d.text)*1000.0)
            else:
                value = child.attrib['value']
                dh_d = [float(v)*1000.0 for v in value.replace(' ','').split(',')]
            
            print('d: ' + str(dh_d))


# Make sure we found all the information regarding the DH table
if dh_alpha is None or dh_a is None or dh_dTheta is None or dh_d is None:
    RDK.ShowMessage("Kinematics information not found in the URP file provided.<br><br>Did you select a URP file generated from the real UR controller?")
    quit()

# Update the DH table information in RoboDK
dh_mat = Mat([dh_alpha, dh_a, dh_dTheta, dh_d]).tr()

# Numeric tolerance for the virtual/g calibration:
tolerance = 0.001

# Update the robot kinematics. RoboDK calculates the DHM table given the DH parameters
status, msg, errors_before, errors_after = RDK.UpdateKinematicsUR(robot, dh_mat, tolerance)

# Show status message to the user
if status >= 0:
    msg = '<font color="green"><strong>' + msg + '.</strong></font>'
    
    # Make sure the nominal error is within reasonable limits (max error of 20 mm should be safe)
    if errors_before[3] > 20.0:
        msg += '<br><br><font color="red"><strong>Warning! Something does NOT look right. Did you select the right robot in RoboDK?</strong></font>'

    msg += '<br><br>Select <strong>Parameters</strong> in the robot panel to switch between nominal and UR controller kinematics. Important: the table shows the DHM parameters (Denavit Hartenberg Modified)'

else:
    msg = '<font color="red"><strong>' + msg + '</strong></font>'
    msg += '<br><br>Warning! Something went wrong'
    
print(msg)
print(errors_before)
print(errors_after)
RDK.ShowMessage(msg)






