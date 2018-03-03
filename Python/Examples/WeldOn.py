# This macro allows simulating a weld gun
# It creates a new "spray gun" object in RoboDK that allows simulating particle deposition
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
# More information about the RoboDK API here:
# https://robodk.com/doc/en/RoboDK-API.html
import sys # allows getting the passed argument parameters
from robolink import *    # API to communicate with RoboDK
from robodk import *      # basic matrix operations
RDK = Robolink()

# quit if we are not simulating
if RDK.RunMode() != RUNMODE_SIMULATE:
    quit()

tool = 0    # auto detect active tool
obj = 0     # auto detect object in active reference frame
    
# Create a new type of spray simulation
#RDK.Spray_Add(tool, obj, "PARTICLE=CUBE(10,10,2) STEP=8x8")
#RDK.Spray_Add(tool, obj, "PARTICLE=SPHERE(4,8) STEP=8x8")
#RDK.Spray_Add(tool, obj, "PARTICLE=SPHERE(4,8,1,1,0.1) STEP=8x8 RANDX=3")
RDK.Spray_Add(tool, obj, "PARTICLE=SPHERE(4,8)")
#RDK.Spray_Add(tool, obj, "PARTICLE=SPHERE(10,20) STEP=1x0")
#RDK.Spray_Add(tool, obj, "STEP=8x8 RANDX=3", volume.tr(), geom.tr())


# Activate the spray
RDK.Spray_SetState(SPRAY_ON)



