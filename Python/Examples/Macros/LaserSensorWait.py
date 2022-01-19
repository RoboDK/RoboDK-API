# More information about the RoboDK API here:
# https://robodk.com/doc/en/RoboDK-API.html
# Type help("robodk.robolink") or help("robodk.robomath") for more information
# Press F5 to run the script
# Note: you do not need to keep a copy of this file, your python script is saved with the station
from robodk.robolink import *    # API to communicate with RoboDK
from robodk.robomath import *    # basic matrix operations

RDK = Robolink()

# This script allows to simulate a laser sensor
# that detect the presence of a part in a plane,
# such as a part crossing a laser sensor in a
# conveyor belt

# Use a target from the station as a reference plane:
SENSOR_NAME = 'Sensor SICK WL4S'
SENSOR_VARIABLE = 'SENSOR'

# Look for parts with the keyword "Part"
PART_KEYWORD = 'Part '

# Update status every 1 ms
RECHECK_PERIOD = 0.001

# Get the sensor and the detection plane
SENSOR = RDK.Item(SENSOR_NAME, ITEM_TYPE_OBJECT)

# retrieve all objects
all_objects = RDK.ItemList(ITEM_TYPE_OBJECT, False)
part_objects = []
for obj in all_objects:
    if obj.Name().count(PART_KEYWORD) > 0:
        part_objects.append(obj)

# Loop forever to detect parts
detected_status = -1
while True:
    detected = 0
    for obj in part_objects:
        # check if an object has the part keyword and is detected by the laser
        if SENSOR.Collision(obj) > 0:
            detected = 1
            break

    # update the current status of the sensor
    if detected_status != detected:
        detected_status = detected
        RDK.setParam(SENSOR_VARIABLE, detected_status)
        print('Object detected status --> %i' % detected_status)

    # Wait some time...
    pause(RECHECK_PERIOD)
