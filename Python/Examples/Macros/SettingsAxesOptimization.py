# This example shows how to read or modify the Axes Optimization settings using the RoboDK API and a JSON string.
# You can select "Axes optimization" in a robot machining menu or the robot parameters to view the axes optimization settings.
# It is possible to update the axes optimization settings attached to a robot or a robot machining project manually or using the API.
#
# More information about the RoboDK API here:
# https://robodk.com/doc/en/RoboDK-API.html
# For more information visit:
# https://robodk.com/doc/en/PythonAPI/robolink.html

from robolink import *    # RoboDK API

# JSON tools
import json

# Start the RoboDK API
RDK = Robolink()

# Ask the user to select a robot arm (6 axis robot wich can have external axes)
robot = RDK.ItemUserPick("Select a robot arm",ITEM_TYPE_ROBOT_ARM)

# Default optimization settings test template
AxesOptimSettings = {
    # Optimization parameters:
    "Active": 1, # Use generic axes optimization: 0=Disabled or 1=Enabled
    "Algorithm": 2, # Optimization algorithm to use: 1=Nelder Mead, 2=Samples, 3=Samples+Nelder Mead
    "MaxIter": 650, # Max. number of iterations
    "Tol": 0.0016, # Tolerance to stop iterations

    # Absolute Reference joints (double):
    "AbsJnt_1": 104.17,
    "AbsJnt_2": 11.22,
    "AbsJnt_3": 15.97,
    "AbsJnt_4": -87.48,
    "AbsJnt_5": -75.36,
    "AbsJnt_6": 63.03,
    "AbsJnt_7": 174.13,
    "AbsJnt_8": 173.60,
    "AbsJnt_9": 0,

    # Using Absolute reference joints (0: No, 1: Yes):
    "AbsOn_1": 1, 
    "AbsOn_2": 1,
    "AbsOn_3": 1,
    "AbsOn_4": 1,
    "AbsOn_5": 1,
    "AbsOn_6": 1,
    "AbsOn_7": 1,
    "AbsOn_8": 1,
    "AbsOn_9": 1,

    # Weight for absolute reference joints (double):
    "AbsW_1": 100,
    "AbsW_2": 100,
    "AbsW_3": 100,
    "AbsW_4": 89,
    "AbsW_5": 90,
    "AbsW_6": 92,
    "AbsW_7": 92,
    "AbsW_8": 96,
    "AbsW_9": 50,

    # Using for relative joint motion smoothing (0: No, 1: Yes):
    "RelOn_1": 1,
    "RelOn_2": 1,
    "RelOn_3": 1,
    "RelOn_4": 1,
    "RelOn_5": 1,
    "RelOn_6": 1,
    "RelOn_7": 1,
    "RelOn_8": 1,
    "RelOn_9": 1,

    # Weight for relative joint motion (double):
    "RelW_1": 5,
    "RelW_2": 47,
    "RelW_3": 44,
    "RelW_4": 43,
    "RelW_5": 36,
    "RelW_6": 47,
    "RelW_7": 53,
    "RelW_8": 59,
    "RelW_9": 0,
}

# Update one value, for example, make it active:
ToUpdate = {}
ToUpdate["Active"] = 1
json_str = json.dumps(ToUpdate)
status = robot.setParam("OptimAxes", json_str)
print(status)

# Example to make a partial or full update
count = 1
while True:    
    for i in range(7):
        # Partial update
        ToUpdate = {}
        ToUpdate["AbsJnt_" + str(i+1)] = (count+i)*4        
        ToUpdate["AbsOn_" + str(i+1)] = count % 2
        ToUpdate["AbsW_" + str(i+1)] = (count+i)

        json_str = json.dumps(ToUpdate)
        status = robot.setParam("OptimAxes", json_str)
        print(status)
        
        # Full update
        #OptimAxes_TEST["RefJoint_" + str(i+1)] = (count+i)*4
        #OptimAxes_TEST["RefWeight_" + str(i+1)] = (count+i)
        #OptimAxes_TEST["RefOn_" + str(i+1)] = count % 2

    # Full update
    #print(robot.setParam("OptimAxes", str(AxesOptimSettings)))        
    count = count + 1

    # Read settings
    json_data = robot.setParam("OptimAxes")
    json_object = json.loads(json_data)
    print(json.dumps(json_object, indent=4))
    pause(0.2)
    

# Example to read the current axes optimization settings:
while True:
    json_data = robot.setParam("OptimAxes")
    json_object = json.loads(json_data)
    print(json.dumps(json_object, indent=4))
    pause(0.2)
