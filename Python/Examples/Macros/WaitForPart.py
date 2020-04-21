# Type help("robolink") or help("robodk") for more information
# Press F5 to run the script
# Note: you do not need to keep a copy of this file, your python script is saved with the station
from robolink import *    # API to communicate with RoboDK
from robodk import *      # basic matrix operations
RDK = Robolink()

# This script allows to simulate a laser sensor
# that detect the presence of a part in a plane,
# such as a part crossing a laser sensor in a
# conveyor belt

# The script finishes once a part has been detected
# so it works like a WAIT UNTIL function.

# Use a target from the station as a reference plane:
TARGET_NAME = 'Get Conveyor'
LASER_PLANE = [0,-1,0] # normal of the plane

# Activate within this tolerance
TOLERANCE_CHECK_MM = 10

# Look for parts with the keyword "Part"
PICKABLE_OBJECTS_KEYWORD = 'Part'

# Update status every 1 ms
RECHECK_PERIOD = 0.001

# Get the target and the detection plane
target = RDK.Item(TARGET_NAME)
targetpose = target.PoseAbs()
DETECT_PLANE_POINT = targetpose.Pos()
DETECT_PLANE_VECTOR = LASER_PLANE

# Define a function to detect a target
def part_detected(pos):
    """Check if a part is in the detection area (proximity of a point to a plane)"""
    pos_proj = proj_pt_2_plane(pos, DETECT_PLANE_POINT, DETECT_PLANE_VECTOR)
    distance2plane = norm(subs3(pos,pos_proj))
    if distance2plane < TOLERANCE_CHECK_MM:
        return True
    return False

# Get all object names
all_objects = RDK.ItemList(ITEM_TYPE_OBJECT)

# Get object items in a list (faster) and filter by keyword
check_objects = []
check_objects_names = []
for i in range(len(all_objects)):
    if all_objects[i].count(PICKABLE_OBJECTS_KEYWORD) > 0:
        check_objects_names.append(all_objects[i])
        check_objects.append(RDK.Item(all_objects[i]))
        
# Make sure that there are part that we are expecting
nCheck_objects = len(check_objects)
if nCheck_objects == 0:
    raise Exception('No parts to check for. The keyword is %s.' % PICKABLE_OBJECTS_KEYWORD)

# Loop forever until a part is detected by the sensor
part_available = False;
while not part_available:
    for i in range(nCheck_objects):
        if part_detected(check_objects[i].PoseAbs().Pos()):
            print('Part detected: %s' % check_objects_names[i])
            part_available = True
            break

    # Wait some time...
    pause(RECHECK_PERIOD)

print('Procedure finished')        
        
        
