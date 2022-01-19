# This script allows adding a trace or a spray deposition
# More information here:
# https://robodk.com/doc/en/PythonAPI/robolink.html#robolink.Robolink.Spray_Add
#
# Example scripts that use Spray_Add:
#     SpindleOn / SpindleOff    -> Turn trace On/Off
#     ArcOn / ArcOff            -> Turn trace On/Off
#     SprayOn / SprayOff        -> Simulate a spray given a workspace volume (for painting)
#     WeldOn / WeldOff          -> Support for multiple weld guns
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
# ---------------------------------------------------------------
#
import sys  # allows getting the passed argument parameters
from robodk.robolink import *    # API to communicate with RoboDK

RDK = Robolink()

# quit if we are not simulating
if RDK.RunMode() != RUNMODE_SIMULATE:
    quit()

# Stop the trace
RDK.Spray_SetState(SPRAY_OFF)
