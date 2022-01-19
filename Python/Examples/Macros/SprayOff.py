# This macro allows simulating a weld gun
# This is an old version of the ArcStart / ArcEnd macro. Use these macros instead for higher flexibility.
#
# This macro creates a new "spray gun" object in RoboDK that allows simulating particle deposition
# It is possible to call GunOn(1) to simulate turning the gun on or GunOff(0) to stop simulating the gun
# Calling GunOn(-1) clears all displayed data
# The macro will output spray gun statistics

#-----------------------------------------------------------------
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
import sys  # allows getting the passed argument parameters
from robodk.robolink import *    # API to communicate with RoboDK

RDK = Robolink()

# quit if we are not simulating
if RDK.RunMode() != RUNMODE_SIMULATE:
    quit()

RDK.Spray_SetState(SPRAY_OFF)
