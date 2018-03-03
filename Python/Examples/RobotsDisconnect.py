# This macro disconnects all robots so that programs can be run in simulation mode only
#
# More information about the RoboDK API here:
# https://robodk.com/doc/en/RoboDK-API.html
# For more information visit:
# https://robodk.com/doc/en/PythonAPI/robolink.html

from robolink import *    # API to communicate with RoboDK
from robodk import *      # basic matrix operations

# Start RoboDK API
RDK = Robolink()

# Iterate through all programs and set them to "Run on robot" if they match a specific rule
# Rule = Program name must start with "Curve"
programs = RDK.ItemList(ITEM_TYPE_PROGRAM, False)
for prog in programs:
    if prog.Name().startswith("Curve"):        
        prog.setRunType(PROGRAM_RUN_ON_SIMULATOR)
