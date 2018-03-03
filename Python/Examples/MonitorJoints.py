# This macro will save a time stamp and robot joints each 50 ms
from robolink import *    # API to communicate with RoboDK
from robodk import *      # basic matrix operations
RDK = Robolink()

robot = RDK.Item('',ITEM_TYPE_ROBOT)

if not robot.Valid():
    raise Exception("Robot is not available")

file_path = RDK.getParam('PATH_OPENSTATION') + '/joints.txt'

fid = open(file_path,'w')
tic()
while True:
    time = toc()
    print('Current time (s):' + str(time))
    joints = str(robot.Joints().tolist())
    fid.write(str(time) + ', ' + joints[1:-1] + '\n')
    pause(0.05)

fid.close()
            
