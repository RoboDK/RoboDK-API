# This script allows adding a trace or a spray deposition
#
# Note: Select Esc key or close the RDK project to clear any trace added using this method
# Note: You can pass an ID as first agurment to specify the trace color
#
# Example: 
#    SpindleOn(2)           show the trace in blue
#    SpindleOn(red)         show the trace in red
#    SpindleOff             turn off the trace
#
# Note: You can pass the radius of the trace as a second argument
#    SpindleOn(2,2.5)       show the trace in blue with a sphere of radius 2.5 mm
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
# Set the tool name as shown in the RoboDK tree (set to None to automatically detect)
TOOL_NAME = None
# TOOL_NAME = "Spindle"

# Set the part name as shown in the RoboDK tree (set to None to automatically detect)
PART_NAME = None
# PART_NAME = "Object"

# Radius of the sphere
SPHERE_RADIUS = 5

# Set the particle color as a named color or as AARRGGBB (alpha channel goes first!)
COLOR = "white"
#COLOR = "green"
#COLOR = "#ffff55bb" # pink-red

# Color list to use if we provide an argument
# Example: 
#    SpindleOn(2) will show blue
#    SpindleOn(red) will show red
COLOR_LIST = [COLOR, "red", "green", "blue", "cyan", "magenta", "#ffff55bb"]

#------------------------------------------------------------------
import sys # allows getting the passed argument parameters
from robolink import *    # API to communicate with RoboDK
from robodk import *      # basic matrix operations

# If an arguments from the object events are provided, retrieve the argument
# (index 0 is the file name)
# Use argument index 1 as color index or named color
if len(sys.argv) >= 2:
    # Use argument 1 as color ID if it is numeric
    arg_1 = sys.argv[1]   
    if arg_1.isnumeric():
        color_id = int(arg_1)
        if color_id >= 0:            
            color_id = color_id % len(COLOR_LIST)
            COLOR = COLOR_LIST[color_id]
    else:
        # Use the named color (or # color)
        COLOR = arg_1
        
# Use argument index 2 to set the radius
if len(sys.argv) >= 3:
    # Use argument 1 as color ID if it is numeric
    arg_2 = sys.argv[2]   
    try:
        SPHERE_RADIUS = float(arg_2)
    except:
        print("Unable to read paramter 2 as radius");

#------------------------------------------------------------------

# Start the RoboDK API
RDK = Robolink()

# Stop if we are not simulating
if RDK.RunMode() != RUNMODE_SIMULATE:
    quit()
    
# Create a new spray gun
tool = 0  # auto detect active tool
object = 0 # auto detect object to attach particles

# Use specific tool and part if we provided it
if TOOL_NAME is not None:    
    tool = RDK.Item(TOOL_NAME, ITEM_TYPE_TOOL)
    
if PART_NAME is not None:    
    object = RDK.Item(PART_NAME, ITEM_TYPE_OBJECT) 

    
# Create a new object with a spray gun
RDK.Spray_Add(tool, object, "PARTICLE=SPHERE(%.2f) NO_PROJECT COLOR=%s" % (SPHERE_RADIUS, COLOR)) # Do not project
# RDK.Spray_Add(tool, object, "PARTICLE=SPHERE(4) PROJECT") # Project to part
RDK.Spray_SetState(SPRAY_ON)


# Option to use a spread
# coordinates must be provided with respect to the TCP
#close_p0 = [   0,   0, -200] # xyz in mm: Center of the conical ellypse (side 1)
#close_pA = [   5,   0, -200] # xyz in mm: First vertex of the conical ellypse (side 1)
#close_pB = [   0,  10, -200] # xyz in mm: Second vertex of the conical ellypse (side 1)
#close_color = [ 1, 1, 1, 1]  # RGBA (0-1)

#far_p0   = [   0,   0,  50] # xyz in mm: Center of the conical ellypse (side 2)
#far_pA   = [  60,   0,  50] # xyz in mm: First vertex of the conical ellypse (side 2)
#far_pB   = [   0, 120,  50] # xyz in mm: Second vertex of the conical ellypse (side 2)
#far_color   = [ 1, 1, 1, 1]  # RGBA (0-1)

#RDK.Spray_Add(tool, obj, "PARTICLE=CUBE(10,10,2) STEP=8x8")
#RDK.Spray_Add(tool, obj, "PARTICLE=SPHERE(4,8) STEP=8x8")
#RDK.Spray_Add(tool, obj, "PARTICLE=SPHERE(4,8,1,1,0.1) STEP=8x8 RANDX=3")
#RDK.Spray_Add(tool, obj, "PARTICLE=SPHERE(4,8) NO_PROJECT")
#RDK.Spray_Add(tool, obj, "PARTICLE=SPHERE(4,8) STEP=1x0")
#RDK.Spray_Add(tool, obj, "STEP=8x8 RANDX=3", volume.tr(), geom.tr())
#RDK.Spray_SetState(SPRAY_ON)


# Available options:
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