# Type help("robolink") or help("robodk") for more information
# Press F5 to run the script
# Documentation: https://robodk.com/doc/en/RoboDK-API.html
# Reference:     https://robodk.com/doc/en/PythonAPI/index.html
#
# This example shows an advanced pick and place application using a Fanuc M-710iC/50 robot (Example 2 from the RoboDK library)

from robolink import *    # API to communicate with RoboDK for simulation and offline/online programming
from robodk import *      # Robotics toolbox for industrial robots

# Setup global parameters
BALL_DIAMETER = 100 # diameter of one ball
APPROACH = 100      # approach distance to grab each part, in mm
nTCPs = 6           # number of TCP's in the tool

#----------------------------------------------
# Function definitions

def box_calc(BALLS_SIDE=4, BALLS_MAX=None):
    """Calculate a list of points (ball center) as if the balls were stored in a box"""
    if BALLS_MAX is None: BALLS_MAX = BALLS_SIDE**3
    xyz_list = []
    for h in range(BALLS_SIDE):
        for i in range(BALLS_SIDE):
            for j in range(BALLS_SIDE):
                xyz_list = xyz_list + [[(i+0.5)*BALL_DIAMETER, (j+0.5)*BALL_DIAMETER, (h+0.5)*BALL_DIAMETER]]
                if len(xyz_list) >= BALLS_MAX:
                    return xyz_list
    return xyz_list

def pyramid_calc(BALLS_SIDE=4):
    """Calculate a list of points (ball center) as if the balls were place in a pyramid"""
    #the number of balls can be calculated as: int(BALLS_SIDE*(BALLS_SIDE+1)*(2*BALLS_SIDE+1)/6)
    BALL_DIAMETER = 100
    xyz_list = []
    sqrt2 = 2**(0.5)
    for h in range(BALLS_SIDE):
        for i in range(BALLS_SIDE-h):
            for j in range(BALLS_SIDE-h):
                height = h*BALL_DIAMETER/sqrt2 + BALL_DIAMETER/2
                xyz_list = xyz_list + [[i*BALL_DIAMETER + (h+1)*BALL_DIAMETER*0.5, j*BALL_DIAMETER + (h+1)*BALL_DIAMETER*0.5, height]]
    return xyz_list

def balls_setup(frame, positions):
    """Place a list of balls in a reference frame. The reference object (ball) must have been previously copied to the clipboard."""
    nballs = len(positions)
    step = 1.0/(nballs - 1)
    for i in range(nballs):
        newball = frame.Paste()
        newball.setName('ball ' + str(i)) #set item name
        newball.setPose(transl(positions[i])) #set item position with respect to parent
        newball.setVisible(True, False) #make item visible but hide the reference frame
        newball.Recolor([1-step*i, step*i, 0.2, 1]) #set RGBA color

def cleanup_balls(parentnodes):
    """Delete all child items whose name starts with \"ball\", from the provided list of parent items."""
    todelete = []
    for item in parentnodes:
        todelete = todelete + item.Childs()

    for item in todelete:
        if item.Name().startswith('ball'):
            item.Delete()

def TCP_On(toolitem, tcp_id):
    """Attach the closest object to the toolitem tool pose,
    furthermore, it will output appropriate function calls on the generated robot program (call to TCP_On)"""
    toolitem.AttachClosest()
    toolitem.RDK().RunMessage('Set air valve %i on' % (tcp_id+1))
    toolitem.RDK().RunProgram('TCP_On(%i)' % (tcp_id+1));
        
def TCP_Off(toolitem, tcp_id, itemleave=0):
    """Detaches the closest object attached to the toolitem tool pose,
    furthermore, it will output appropriate function calls on the generated robot program (call to TCP_Off)"""
    toolitem.DetachAll(itemleave)
    toolitem.RDK().RunMessage('Set air valve %i off' % (tcp_id+1))
    toolitem.RDK().RunProgram('TCP_Off(%i)' % (tcp_id+1));


#----------------------------------------------------------
# The program starts here:

# Any interaction with RoboDK must be done through RDK:
RDK = Robolink()

# Turn off automatic rendering (faster)
RDK.Render(False)

#RDK.Set_Simulation_Speed(500); # set the simulation speed

# Gather required items from the station tree
robot = RDK.Item('Fanuc M-710iC/50')
robot_tools = robot.Childs()
#robottool = RDK.Item('MainTool')
frame1 = RDK.Item('Table 1')
frame2 = RDK.Item('Table 2')

# Copy a ball as an object (same as CTRL+C)
ballref = RDK.Item('reference ball')
ballref.Copy()

# Run a pre-defined station program (in RoboDK) to replace the two tables
prog_reset = RDK.Item('Replace objects')
prog_reset.RunProgram()

# Call custom procedure to remove old objects
cleanup_balls([frame1, frame2])

# Make a list of positions to place the objects
frame1_list = pyramid_calc(4)
frame2_list = pyramid_calc(4)

# Programmatically place the objects with a custom-made procedure
balls_setup(frame1, frame1_list)

# Delete previously generated tools
for tool in robot_tools:
    if tool.Name().startswith('TCP'):
        tool.Delete()
        
# Calculate tool frames for the suction cup tool of 6 suction cups
TCP_list = []
for i in range(nTCPs):
    TCPi_pose = transl(0,0,100)*rotz((360/nTCPs)*i*pi/180)*transl(125,0,0)*roty(pi/2)
    TCPi = robot.AddTool(TCPi_pose, 'TCP %i' % (i+1))
    TCP_list.append(TCPi)

TCP_0 = TCP_list[0]

# Turn on automatic rendering
RDK.Render(True)

# Move balls    
robot.setPoseTool(TCP_list[0])
nballs_frame1 = len(frame1_list)
nballs_frame2 = len(frame2_list)
idTake = nballs_frame1 - 1
idLeave = 0
idTCP = 0
target_app_frame = transl(2*BALL_DIAMETER, 2*BALL_DIAMETER, 4*BALL_DIAMETER)*roty(pi)*transl(0,0,-APPROACH)

while idTake >= 0:
    # ------------------------------------------------------------------
    # first priority: grab as many balls as possible
    # the tool is empty at this point, so take as many balls as possible (up to a maximum of 6 -> nTCPs)
    ntake = min(nTCPs, idTake + 1)

    # approach to frame 1
    robot.setPoseFrame(frame1)
    robot.setPoseTool(TCP_0)
    robot.MoveJ([0,0,0,0,10,-200])
    robot.MoveJ(target_app_frame)

    # grab ntake balls from frame 1
    for i in range(ntake):
        TCPi = TCP_list[i]
        robot.setPoseTool(TCPi)
        # calculate target wrt frame1: rotation about Y is needed since Z and X axis are inverted
        target = transl(frame1_list[idTake])*roty(pi)*rotx(30*pi/180)
        target_app = target*transl(0,0,-APPROACH)
        idTake = idTake - 1        
        robot.MoveL(target_app)
        robot.MoveL(target)
        TCP_On(TCPi, i)
        robot.MoveL(target_app)
 
    # ------------------------------------------------------------------
    # second priority: unload the tool     
    # approach to frame 2 and place the tool balls into table 2
    robot.setPoseTool(TCP_0)
    robot.MoveJ(target_app_frame)
    robot.MoveJ([0,0,0,0,10,-200])
    robot.setPoseFrame(frame2)    
    robot.MoveJ(target_app_frame)
    for i in range(ntake):
        TCPi = TCP_list[i]
        robot.setPoseTool(TCPi)
        if idLeave > nballs_frame2-1:
            raise Exception("No room left to place objects in Table 2")
        
        # calculate target wrt frame1: rotation of 180 about Y is needed since Z and X axis are inverted
        target = transl(frame2_list[idLeave])*roty(pi)*rotx(30*pi/180)
        target_app = target*transl(0,0,-APPROACH)
        idLeave = idLeave + 1        
        robot.MoveL(target_app)
        robot.MoveL(target)
        TCP_Off(TCPi, i, frame2)
        robot.MoveL(target_app)

    robot.MoveJ(target_app_frame)

# Move home when the robot finishes
robot.MoveJ([0,0,0,0,10,-200])
