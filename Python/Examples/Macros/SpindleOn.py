# This macro allows simulating a spray gun
# It is possible to call GunOn(1) to simulate turning the gun on or GunOff(0) to stop simulating the gun
# Calling GunOn(-1) clears all displayed data
#
# This macro creates a new "spray gun" object in RoboDK that allows simulating particle deposition
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


import sys # allows getting the passed argument parameters
from robolink import *    # API to communicate with RoboDK
from robodk import *      # basic matrix operations
RDK = Robolink()

# quit if we are not simulating
if RDK.RunMode() != RUNMODE_SIMULATE:
    quit()

# Create a new spray gun
tool = 0 #RDK.Item('Spindle') # auto detect active tool
obj = 0 #RDK.Item('Part') # auto detect object in active reference frame

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
RDK.Spray_Add(tool, obj, "PARTICLE=SPHERE(4,8) NO_PROJECT")
#RDK.Spray_Add(tool, obj, "PARTICLE=SPHERE(4,8) STEP=1x0")
#RDK.Spray_Add(tool, obj, "STEP=8x8 RANDX=3", volume.tr(), geom.tr())
RDK.Spray_SetState(SPRAY_ON)



