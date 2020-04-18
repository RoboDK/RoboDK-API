# This script projects a TCP to an axis defined by two other TCPs, 
# adjusting the position of the TCP and the Z axis along the line defined by the two calibration TCPs
#
# More information about the RoboDK API here:
# https://robodk.com/doc/en/RoboDK-API.html
# For more information visit:
# https://robodk.com/doc/en/PythonAPI/robolink.html

# Enter the calibrated reference tools (Z+ defined as Point1 to Point2)
AXIS_POINT_1 = 'CalibTool 1'
AXIS_POINT_2 = 'CalibTool 2'

# Set the following variable to False to not move the TCP
# (only a reorientation of the Z axis will be done)
PROJECT_POINT = True

#-----------------------------------------------------------------
#-----------------------------------------------------------------
#-----------------------------------------------------------------
#-----------------------------------------------------------------
#-----------------------------------------------------------------

from robolink import *    # API to communicate with RoboDK
from robodk import *      # basic matrix operations

RDK = Robolink()

# Get TCP to project
tcpitem = RDK.ItemUserPick('Select a tool to calibrate Z axis', ITEM_TYPE_TOOL)

if not tcpitem.Valid():
    quit()

H_TCP = tcpitem.PoseTool()
P_TCP = H_TCP.Pos()

# Get spindle axis
tcp_item_1 = RDK.Item(AXIS_POINT_1,ITEM_TYPE_TOOL)
tcp_item_2 = RDK.Item(AXIS_POINT_2,ITEM_TYPE_TOOL)

if not tcp_item_1.Valid():
    raise Exception("Define the first calibration TCP as: %s" % AXIS_POINT_1)

if not tcp_item_2.Valid():
    raise Exception("Define the second calibration TCP as: %s" % AXIS_POINT_2)


axis_p1 = tcp_item_1.PoseTool().Pos()
axis_p2 = tcp_item_2.PoseTool().Pos()


# Alternative Manual input for P_TCP:
# P_TCP = [ -51.240000,   -94.004000,   266.281000,    60.150000,     0.000000,   -26.760000  ] # [2,0,10]
# H_TCP = Motoman_2_Pose(P_TCP)

# Alternative manual input for spindle axis
# axis_p1 = [-43.74331, -83.59345, 259.19644]  #[0,0,0]
# axis_p2 = [-56.48556, -107.99492, 274.96115] #[0,0,1]
axis_v12 = normalize3(subs3(axis_p2,axis_p1))


# TCP calculation
TCP_OK = proj_pt_2_line(P_TCP, axis_p1, axis_v12)

TCP_verror = subs3(P_TCP,TCP_OK)

print('Projected TCP to Spindle axis:\n[X,Y,Z] = [%.3f,%.3f,%.3f] mm'%(TCP_OK[0],TCP_OK[1],TCP_OK[2]))
msg_proj_error = 'Projection Error = %.3f mm' % norm(TCP_verror)
print(msg_proj_error)


# TCP reference frame adjustment (correct Z axis)
TCP_Yvect = H_TCP.VY()
TCP_Zvect = H_TCP.VZ()

angle_error = angle3(axis_v12, TCP_Zvect) * 180 / pi
msg_angle_error = 'Z angle error = %.3f deg' % angle_error
print(msg_angle_error)
H_TCP_OK = eye(4)
if PROJECT_POINT:
    H_TCP_OK[0:3,3] = TCP_OK
else:
    H_TCP_OK[0:3,3] = P_TCP
    
H_TCP_OK[0:3,2] = axis_v12
x_axis = normalize3(cross(TCP_Yvect, axis_v12))
y_axis = normalize3(cross(axis_v12, x_axis))
H_TCP_OK[0:3,0] = x_axis
H_TCP_OK[0:3,1] = y_axis

TCP_OK = Pose_2_Motoman(H_TCP_OK)
msg_newtcp = 'Updated TCP [X,Y,Z,w,p,r] = [%.3f,%.3f,%.3f,%.3f,%.3f,%.3f]'%(TCP_OK[0],TCP_OK[1],TCP_OK[2],TCP_OK[3],TCP_OK[4],TCP_OK[5])
print(msg_newtcp)

# Ask user to update TCP
answer = mbox(msg_newtcp + '\n\n' + msg_proj_error+ '\n' + msg_angle_error + '\n\nUpdate TCP?')
if answer == True:
    tcpitem.setPoseTool(H_TCP_OK)






