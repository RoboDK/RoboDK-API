# This macro allows simulating a spray gun for painting or to simulate the trace of inspaction
#
# You can call SprayOn(1) to simulate turning the Spray gun ON or SprayOn(0) to stop simulating the gun
# Calling SprayOn(-1) clears all displayed data
# The macro will output spray gun statistics
#
# --------------------------------------------------------------
# This script shows how to create "spray" object in RoboDK that allows simulating particle deposition by using:
# RDK.Spray_Add(tool, object, options_command, volume, geometry)
#    tool: tool item (TCP) to use
#    object: object to project the particles
#    options_command (optional): string to specify options.
#    volume (optional): Matrix of parameters defining the volume of the spray gun
#    geometry (optional): Matrix of vertices defining the triangles.
#
# More information here:
# https://robodk.com/doc/en/PythonAPI/robolink.html#robolink.Robolink.Spray_Add
# https://robodk.com/doc/en/RoboDK-API.html
#
# The scripts ArcStart, ArcEnd and WeldOn and SpindleOn behave in a similar way, the only difference is the default behavior
# This behavior simmulates Fanuc Arc Welding and triggers appropriate output when using the customized post processor.
# Select ESC to clear the trace manually.
#
# Example scripts that use Spray_Add:
#     SpindleOn / SpindleOff    -> Turn trace On/Off
#     ArcOn / ArcOff            -> Turn trace On/Off
#     SprayOn / SprayOff        -> Simulate a spray given a workspace volume (for painting)
#     WeldOn / WeldOff          -> Support for multiple weld guns

#------------------------------------------------------------------

# Use a specific tool as a spray gun
Tool_Name = None
#Tool_Name = 'Tool 2'

# Use a specific object to project particles:
Object_Name = None
#Object_Name = 'Part'

# Define the default action (0 to deactivate, +1 to activate, -1 to clear any spray gun simulation)
# Setting it to None will display a message
ACTION = None

from robolink import *  # API to communicate with RoboDK
from robodk import *  # basic matrix operations

RDK = Robolink()

# quit if we are not in simulation mode
if RDK.RunMode() != RUNMODE_SIMULATE:
    quit()

# Get any previously added spray gun simulations and display statistics (spray on the part vs spray falling out of the part)
info, data = RDK.Spray_GetStats()
if data.size(1) > 0:
    print("Spray gun statistics:")
    print(info)
    print(data.tr())
    # # Diplay statistics
    # RDK.ShowMessage("Material used: %.1f%%<br>Material waisted: %.1f%%<br>Total particles: %.1f" % (data[1,0],data[2,0],data[3,0]), True)
    # # Clear previous spray
    # RDK.Spray_Clear()

# Check if we are running this program inside another program and passing arguments
import sys
if len(sys.argv) > 1:
    ACTION = int(sys.argv[1])

# If the default ACTION is None, display a message to activate/deactivate the spray gun
if ACTION is None:
    print('Note: This macro can be called as Spray(1) or SprayOn(0)')
    entry = mbox('Turn gun ON or OFF', ('On', '1'), ('Off', '0'))
    if not entry:
        quit()
    ACTION = int(entry)

if ACTION == 0:
    # Turn the gun off
    RDK.Spray_SetState(SPRAY_OFF)

elif ACTION < 0:
    # Clear all spray simulations (same as pressing ESC key)
    RDK.Spray_Clear()

elif ACTION > 0:
    # Create a new spray gun object in RoboDK
    # by using RDK.Spray_Add(tool, object, options_command, volume, geometry)
    # tool: tool item (TCP) to use
    # object: object to project the particles
    # options_command (optional): string to specify options. Example:
    #     STEP=AxB: Defines the grid to be projected 1x1 means only one line of particle projection (for example, for welding)
    #     PARTICLE: Defines the shape and size of particle (sphere or particle), unless a specific geometry is provided:
    #       a- SPHERE(radius, facets)
    #       b- SPHERE(radius, facets, scalex, scaley, scalez)
    #       b- CUBE(sizex, sizey, sizez)
    #     RAND=factor: Defines a random factor factor 0 means that the particles are not deposited randomly
    #     ELLYPSE: defines the volume as an ellypse (default)
    #     RECTANGLE: defines the volume as a rectangle
    #     PROJECT: project the particles to the surface (default) (for welding, painting or scanning)
    #     NO_PROJECT: does not project the particles to the surface (for example, for 3D printing)
    #
    # volume (optional): Matrix of parameters defining the volume of the spray gun
    # geometry (optional): Matrix of vertices defining the triangles.

    tool = 0  # auto detect active tool
    obj = 0  # auto detect object in active reference frame
    if Tool_Name is not None:
        tool = RDK.Item(Tool_Name, ITEM_TYPE_TOOL)

    if Object_Name is not None:
        obj = RDK.Item(Object_Name, ITEM_TYPE_OBJECT)
    # We can specify a given tool object and/or object
    #robot = RDK.Item("ABB IRB 2600-12/1.85", ITEM_TYPE_ROBOT)
    #tools = robot.Childs()
    #if len(tools) > 0:
    #    tool = tools[0]
    #obj = RDK.Item('object', ITEM_TYPE_OBJECT)

    options_command = "ELLYPSE PROJECT PARTICLE=SPHERE(4,8,1,1,0.5) STEP=8x8 RAND=2"  # simulate
    #options_command = "PARTICLE=CUBE(10,10,2) STEP=8x8"
    #options_command = "PARTICLE=SPHERE(4,8) STEP=8x8"
    #options_command = "PARTICLE=SPHERE(4,8,1,1,0.1) STEP=8x8 RAND=3"

    # Example commands for welding:
    # options_command = "PROJECT PARTICLE=SPHERE(4,8)"
    # options_command = PARTICLE=SPHERE(4,8) STEP=1x0

    # define the ellypse volume as p0, pA, pB, colorRGBA (close and far), in mm
    # coordinates must be provided with respect to the TCP
    close_p0 = [0, 0, -200]  # xyz in mm: Center of the conical ellypse (side 1)
    close_pA = [5, 0, -200]  # xyz in mm: First vertex of the conical ellypse (side 1)
    close_pB = [0, 10, -200]  # xyz in mm: Second vertex of the conical ellypse (side 1)
    close_color = [1, 0, 0, 1]  # RGBA (0-1)

    far_p0 = [0, 0, 50]  # xyz in mm: Center of the conical ellypse (side 2)
    far_pA = [60, 0, 50]  # xyz in mm: First vertex of the conical ellypse (side 2)
    far_pB = [0, 120, 50]  # xyz in mm: Second vertex of the conical ellypse (side 2)
    far_color = [0, 0, 1, 0.2]  # RGBA (0-1)

    close_param = close_p0 + close_pA + close_pB + close_color
    far_param = far_p0 + far_pA + far_pB + far_color
    volume = Mat([close_param, far_param]).tr()
    RDK.Spray_Add(tool, obj, options_command, volume)
    RDK.Spray_SetState(SPRAY_ON)

    # Another example with a varying rectancular shape
    # define the rectangular volume as p0, pA, pB, colorRGBA (close and far)
    # close_param = [-90,-117,  0,  90,-117,0,   -90,117,  0,       0.2,0.2,1,.1]
    # far_param   = [-175,-190,200, 175,-190,200,   -175,190,200,   0.5,0,0,.9]
    # volume = Mat([close_param, far_param])
    # RDK.Spray_Add(tool, obj, "RECTANGLE PARTICLE=SPHERE(2,5) STEP=15x15 RAND=3", volume.tr())
    # RDK.Spray_SetState(SPRAY_ON)

    # Optional: define geometry as a list of triangles with normals (instead of a scaled cube or a sphere)
    # geom = Mat([[0,0,0,   0,0,1], [5,0,0,   0,0,1], [0,5,0,   0,0,1]])
    # RDK.Spray_Add(tool, obj, "STEP=8x8 RANDX=3", volume.tr(), geom.tr())
    # RDK.Spray_SetState(SPRAY_ON)
