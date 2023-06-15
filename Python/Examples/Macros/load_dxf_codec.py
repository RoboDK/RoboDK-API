# This macro fixes encoding issues from DXF files. It should be used with DXF2Gcode project
from robodk.robolink import *
from robodk.robodialogs import *
from robodk.robofileio import *

RDK = Robolink()

import codecs

#file_location = r'C:\Users\albert\Desktop\Sunpattern2D123.dxf'
file_location = getOpenFileName()
if not file_location or not file_location.endswith('.dxf'):
    raise Exception('dxf file not provided')

file_location_ok = getFileDir(file_location) + '/' + getFileName(file_location) + '-RDK.dxf'

print(file_location_ok)

unknown_names = []

file_stream = codecs.open(file_location, 'r', 'utf-8')
file_output = codecs.open(file_location_ok, 'w', 'cp1252')
line = 0
for l in file_stream:
    line = line + 1
    try:
        file_output.write(l)
    except:
        print('Error reading line %i' % line)
        try:
            idx = unknown_names.index(l)
        except ValueError:
            idx = len(unknown_names)
            unknown_names.append(l)
        file_output.write('Object%i\n' % idx)

file_stream.close()
file_output.close()

RDK.AddFile(file_location_ok)
#input()
