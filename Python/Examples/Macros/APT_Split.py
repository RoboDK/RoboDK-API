# This Python macro shows how to split long GOTO movements from an APT file
from robolink import *
import os
import re

FILE_PATH = os.path.dirname(os.path.realpath(__file__))


APT_FILE        = FILE_PATH + '/apt-in.apt'
APT_FILE_SAVE   = FILE_PATH + '/apt-out.apt'
MAX_STEP_MM     = 100


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
            if line == "RAPID":
                fout.write("FEDRAT/ MMPM,60000\n")
            elif line.startswith("GOTO/"):
                xyzijk = str_2_list(line)
                if xyzijk_last is None:
                    xyzijk_last = xyzijk
                else:
                    x,y,z,i,j,k = xyzijk
                    x_last, y_last, z_last, i_last, j_last, k_last = xyzijk_last                    
                    if i == i_last and j == j_last and k == k_last:                        
                        travel_mm = distance(xyzijk, xyzijk_last)
                        steps = int(travel_mm/MAX_STEP_MM)
                        if steps > 1:
                            extra_lines = extra_lines + steps
                            steps = float(steps)                            
                            fout.write('; next move is a TCP travel of %.3f mm and is divided in %i steps\n' % (travel_mm, steps))
                            print('; next move is a TCP travel of %.3f mm and is divided in %i steps' % (travel_mm, steps))
                            xd = (x-x_last)/steps
                            yd = (y-y_last)/steps
                            zd = (z-z_last)/steps
                            for stp in range(1,int(steps)):
                                xyzijk_now = [x_last+xd*stp, y_last+yd*stp, z_last+zd*stp, i,j,k]
                                fout.write("GOTO/ %.3f, %.3f, %.3f, %.3f, %.3f, %.3f\n" % tuple(xyzijk_now))
                    else:
                        print("changing ijk will not split long paths")
                    xyzijk_last = xyzijk      
                    
                fout.write(line + '\n')
            else:
                fout.write(line + '\n')       
            
            line = fin.readline().strip()
            
            #input("enter to continue")
print("Finished: processed %i lines and generated %i lines" % (line_count, line_count + extra_lines))          
            