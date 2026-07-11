# This script show how to recalculate normals of an G-code file to make the Z axis point at an angle with respect to IJK=[0,0,1]
from robolink import *
from robodk import *
import os
import re

FILE_PATH = os.path.dirname(os.path.realpath(__file__))

# APT_FILE = 'C:/Users/Albert/Desktop/test3.ngc'
APT_FILE = getOpenFileName(FILE_PATH)

if not APT_FILE:
    quit()
#APT_FILE        = FILE_PATH + '/apt-in.apt'
#APT_FILE_SAVE   = FILE_PATH + '/apt-out.apt'
APT_FILE_SAVE = APT_FILE[:-4] + "_radial" + APT_FILE[-4:]


def str_2_list(str_values, expected_values=6):
    """Converts a string into a list of values. It returns None if the array is smaller than the expected size."""
    if str_values is None:
        return None
    values = re.findall("[-+]?\d+[\.]?\d*", str_values)
    if len(values) < expected_values:
        return None
    for i in range(len(values)):
        values[i] = float(values[i])
    #print('Read values: ' + repr(values))
    return values

line_count = 0
extra_lines = 0

# Set the minimum Z vector tilt in radians:
MIN_ROTATION_Z = 5*pi/180

with open(APT_FILE_SAVE, 'w') as fout:
    with open(APT_FILE, 'r') as fin:  
        xyzijk_last = None
        line_count = 0
        line = fin.readline()
        while line:
            line = line.strip()            
            # Typical gcode move line:
            # G1 X-182.53 Y77.82 Z266.36 I-0.032 J0.014 K0.999 E5.465 F20.00 
            line_count = line_count + 1        
            if line.startswith("G1 "):
                xyzijk = str_2_list(line[3:])
                x,y,z = xyzijk[:3]
                ijk = normalize3(xyzijk[3:6])
                if angle3(ijk,[0,0,1]) < MIN_ROTATION_Z:
                    # force the Z axis to to be tilted towards the radial direction
                    angle_xyplane = atan2(y,x)
                    rot_matrix = rotz(angle_xyplane)*roty(MIN_ROTATION_Z)
                    ijk_rotated = rot_matrix[:3,:3] * [0,0,1]
                    i,j,k = ijk_rotated
                else:
                    i,j,k = ijk
                
                str_trailing = " ".join(line.split(" ")[7:])
                fout.write("G1 X%.4f Y%.4f Z%.4f I%.5f J%.5f K%.5f " % (x,y,z,i,j,k))
                fout.write(str_trailing)
                fout.write("\n")
                
            else:
                fout.write(line + '\n')       
            
            line = fin.readline()
            
            if line_count % 5000 == 0:
                print("Working... (line %i)\n" % line_count)
            
            #input("enter to continue")
print("Finished: processed %i lines and generated %i lines" % (line_count, line_count + extra_lines))          
            