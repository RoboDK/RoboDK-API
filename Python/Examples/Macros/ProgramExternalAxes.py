# This example shows how to create a program that involves moving axes
# You should use a target to hold the information of the external axes
# The additional joint values will be used to move the external axes in synchronization with the robot
# This example creates a sample program with the project: "C:/RoboDK/Library/Example 14.rdk" (machining with a linear track and a turntable):

from robolink import *    # RoboDK API
from robodk import *      # Robot toolbox
RDK = Robolink()

# Retrieve the robot, reference frame and create a program
robot = RDK.Item('', ITEM_TYPE_ROBOT)
if not robot.Valid():
    raise Exception("Robot not selected or available")
    
# get the parent/master robot. 
# For example, if we selected a synchronized external axis this will return the robot that drives this external axis
robot = robot.getLink(ITEM_TYPE_ROBOT) 
    
print("Using robot: " + robot.Name())
#reference = robot.Parent() # get the robot base (parent item)
reference = robot.getLink(ITEM_TYPE_FRAME) # get the linked/active reference frame

# Create a new program
program = RDK.AddProgram('Test')

# Define a reference pose (orientation is important)
pos = transl(100,-500,300)*rotx(-90*pi/180)

# Turn Off automatic rendering (faster)
RDK.Render(False) 

# Don't show instructions (faster)
program.ShowInstructions(False) 

# Specify the reference frame you want to use
program.setPoseFrame(reference)

npoints = 25
for i in range(npoints):
    targetname='Target %i' % i
    target=RDK.AddTarget(targetname,reference,robot)
    target.setPose(transl(0, -10.0**(3.0*i/npoints), 100*i) * pos)
    
    # Set the external axes
    axes = [i*100 + 50, 180]
    
    # For cartesian targets RoboDK will ignore robot joints but not external axes
    all_axes = [0]*6 + axes
    # Quick way to create an array:
    # [0,0,0,0,0,0, ext_axis_1, ext_axis_2]
    
    # Set the target and create a move instruction
    target.setJoints(all_axes)
    target.setAsCartesianTarget()
    if i == 0:
        program.MoveJ(target)
    else:
        program.MoveL(target)
    
    # If you are creating a long program, this helps keeping the tree small (faster)
    if i % 20 == 0:
        program.ShowTargets(False)

# Hide all targets (saved with the instruction)
program.ShowTargets(False)

# If desired, show the program at the end
program.ShowInstructions(True)