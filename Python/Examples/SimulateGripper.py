# This file allows simulating the opening and closing of grippers.
# Two models of the gripper per robot are required: one opened and one closed.
# The opened model of the gripper should have the keyword "Opened"
# The closed model of the gripper should have the keyword "Closed"
# Simply place this file in the station and leave it running to
# make it work
#
# More information about the RoboDK API here:
# https://robodk.com/doc/en/RoboDK-API.html
# For more information visit:
# https://robodk.com/doc/en/PythonAPI/robolink.html
# Press F5 to run the script
# Note: you do not need to keep a copy of this file, your python script is saved with the station
from robolink import *    # API to communicate with RoboDK
from robodk import *      # basic matrix operations
RDK = Robolink()


OPENED_KEYWORD = 'Opened'
CLOSED_KEYWORD = 'Closed'
UPDATE_FREQUENCY = 0.01   

# Loop forever
print('Starting infinite loop to simulate open/close of tools')
while True:
    # First step: get a list of tool pairs (open, closed) per robot
    Tool_Pairs = []
    # get all the robot names (strings)
    all_robots = RDK.ItemList(ITEM_TYPE_ROBOT, True)
    for i in range(len(all_robots)):
        roboti = RDK.Item(all_robots[i])
        roboti_name = roboti.Name()
        # get the tools of each robot
        roboti_tools = roboti.Childs()
        opened = None
        closed = None
        # store the opened model and closed model of each gripper
        for t in range(len(roboti_tools)):
            tnamei = roboti_tools[t].Name()
            if not isinstance(opened,Item) and tnamei.count(OPENED_KEYWORD) > 0:
                opened = roboti_tools[t]
                print('Using %s from robot %s as gripper opened' % (tnamei, roboti_name))
            elif not isinstance(closed,Item) and tnamei.count(CLOSED_KEYWORD) > 0:
                closed = roboti_tools[t]
                print('Using %s from robot %s as gripper closed' % (tnamei, roboti_name))

            if isinstance(opened, Item) and isinstance(closed, Item):
                # Stop if we have an open state and a closed state per robot
                break;
        Tool_Pairs.append([opened, closed])

    # We may find as many pairs of tools as robots are available in the station        
    nTool_Pairs = len(Tool_Pairs)
    while True:
        #try:
            # Iterate through all tool pairs and detect the presence of objects
            for i in range(nTool_Pairs):
                opened = Tool_Pairs[i][0]
                closed = Tool_Pairs[i][1]
                open_valid = isinstance(opened,Item)
                close_valid = isinstance(closed,Item)
                tool_is_open = True

                # Check if the tool holds one or more objects:
                if (open_valid and len(opened.Childs()) > 0) or (close_valid and len(closed.Childs()) > 0):
                    tool_is_open = False

                # Update the visibility of the tools
                if open_valid:
                    opened.setVisible(tool_is_open)
                if close_valid:
                    closed.setVisible(not tool_is_open)                  

            # Take a pause...
            pause(UPDATE_FREQUENCY)

        #except:            
            #print('An item was deleted. Remaking tool list')
            #break


            
