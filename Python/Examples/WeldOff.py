# This macro allows simulating a weld gun
# This is an old version of the ArcStart / ArcEnd macro. Use these macros instead for higher flexibility.
# 
# This macro creates a new "spray gun" object in RoboDK that allows simulating particle deposition
# It is possible to call GunOn(1) to simulate turning the gun on or GunOff(0) to stop simulating the gun
# Calling GunOn(-1) clears all displayed data
# The macro will output spray gun statistics
# More information about the RoboDK API here:
# https://robodk.com/doc/en/RoboDK-API.html
import sys # allows getting the passed argument parameters
from robolink import *    # API to communicate with RoboDK
from robodk import *      # basic matrix operations
RDK = Robolink()

# quit if we are not simulating
if RDK.RunMode() != RUNMODE_SIMULATE:
    quit()

RDK.Spray_SetState(SPRAY_OFF)


