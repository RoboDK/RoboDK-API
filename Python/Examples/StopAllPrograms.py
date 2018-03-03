# This macro stops all running programs
# More information about the RoboDK API here:
# https://robodk.com/doc/en/RoboDK-API.html
from robolink import *    # API to communicate with RoboDK
from robodk import *      # basic matrix operations
RDK = Robolink()

# Get the list of all GUI programs:
proglist = RDK.ItemList(ITEM_TYPE_PROGRAM, False)

# Add to the list of all Python programs:
# proglist = proglist + RDK.ItemList(ITEM_TYPE_PROGRAM_PYTHON, False)


for prog in proglist:
    prog_name = prog.Name()
    
    # Skip stopping a specific program
    if prog_name.lower().startswith('main'):
        continue
    
    print("Stopping Program: " + progname)
    prog.Stop()
