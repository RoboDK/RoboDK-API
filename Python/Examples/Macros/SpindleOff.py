# This macro allows simulating a spray gun
# It is possible to call GunOn(1) to simulate turning the gun on or GunOff(0) to stop simulating the gun
# Calling GunOn(-1) clears all displayed data
# The macro will output spray gun statistics
import sys # allows getting the passed argument parameters
from robolink import *    # API to communicate with RoboDK
from robodk import *      # basic matrix operations
RDK = Robolink()

# quit if we are not simulating
if RDK.RunMode() != RUNMODE_SIMULATE:
    quit()

RDK.Spray_SetState(SPRAY_OFF)


