# This script scrolls the tree to the last running instruction

from robodk import *      # RoboDK API
from robolink import *    # Robot toolbox
import time

# Start the RoboDK API
RDK = Robolink()

# Retrieve all programs
progs = RDK.ItemList(ITEM_TYPE_PROGRAM)

# Start looking for running programs from the bottom
progs.reverse()

# Infinite loop to look for running programs
while True:
    for p in progs:
        if p.Busy():
            # Get the running instruction id
            ins = p.setParam("CurrentInstruction")

            # Scroll the tree to the running program
            p.setParam("Scroll", ins)
            break
        
    time.sleep(0.05)
