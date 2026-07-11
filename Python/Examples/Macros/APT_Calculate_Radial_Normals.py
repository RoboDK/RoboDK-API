# This Python macro shows how to recalculate normals of an APT file to make them radial
from robolink import *
import os
import re

FILE_PATH = os.path.dirname(os.path.realpath(__file__))

#APT_FILE = 'C:/Users/Albert/Downloads/RingPattern.tap'
APT_FILE = getOpenFile(FILE_PATH)
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

with open(APT_FILE_SAVE, 'w') as fout:
    with open(APT_FILE, 'r') as fin:    
        line = fin.readline().strip()
        xyzijk_last = None
        line_count = 0
        while line:  
            line_count = line_count + 1        
            if line.startswith("GOTO/"):
                xyzijk = str_2_list(line)
                x,y,z = xyzijk[:3]
                i,j,k = normalize3([x,y,0])
                fout.write("GOTO/ %.4f, %.4f, %.4f, %.5f, %.5f, %.5f\n" % (x,y,z,i,j,k))
                #fout.write(line + '\n')
            else:
                fout.write(line + '\n')       
            
            line = fin.readline().strip()
            
            #input("enter to continue")
print("Finished: processed %i lines and generated %i lines" % (line_count, line_count + extra_lines))          
            