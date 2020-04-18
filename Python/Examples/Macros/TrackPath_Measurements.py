# This program tracks two objects with respect to a measurement system (6D measurement system such as the Creaform C-Track)
# The path of one object with respect to the other one is recorded as robot targets, providing a preview of the robot reaching the target.
# The first object should represent a reference frame (object) and the second tool should represent a tool
# More information about the RoboDK API here:
# https://robodk.com/doc/en/RoboDK-API.html
# More information about the RoboDK API for Python: https://robodk.com/doc/en/PythonAPI/index.html
from robolink import *    # API to communicate with RoboDK
from robodk import *      # basic matrix operations
RDK = Robolink()

MEASURE_REF = 'Measure ref'
TOOL_REF = 'Tool ref'
TRACKER_REF = 'Tracker reference'
REFRESH_RATE = 0.1
TOLERANCE_CLOSE = 5 # in mm and degrees
MIN_POINTS_REF = 3
MIN_POINTS_TCP = 3
FEEDBACK_WITH_ROBOT = True


ref_frame = RDK.Item(MEASURE_REF)
if not ref_frame.Valid():
    ref_frame = RDK.ItemUserPick('Select the reference frame', ITEM_TYPE_FRAME)
    if not ref_frame.Valid():
        quit()

ref_tool = RDK.Item(TOOL_REF)
if not ref_tool.Valid():
    ref_tool = RDK.ItemUserPick('Select the tool frame', ITEM_TYPE_FRAME)
    if not ref_tool.Valid():
        quit()

ref_tracker = RDK.Item(TRACKER_REF)
if not ref_tracker.Valid():
    ref_tracker = RDK.ItemUserPick('Select the tracker reference', ITEM_TYPE_FRAME)
    if not ref_tracker.Valid():
        quit()        

robot = RDK.ItemUserPick('Select the robot', ITEM_TYPE_ROBOT)
if not robot.Valid():
    quit()

robot.setFrame(ref_frame)
target_prev = None

while True:
    Href, Htcp, np_ref, np_tcp, time, status = RDK.StereoCamera_Measure()
    if status != 0:
        print("Problems with device. Retrying...")
        pause(2)
        continue

    if np_ref < MIN_POINTS_REF:
        print("Can't see the reference: %i/%i" % (np_ref, MIN_POINTS_REF))
        continue

    if np_tcp < MIN_POINTS_TCP:
        print("Can't see the tool: %i/%i" % (np_ref, MIN_POINTS_REF))
        continue
    
    target = invH(Href)*Htcp

    ref_tracker.setPose(invH(Href))
    ref_tool.setPose(Htcp)

    if target_prev is not None:
        target_diff = invH(target_prev)*target
        target_prev = target
        if pose_angle(target_diff) < TOLERANCE_CLOSE*pi/180 and norm(target_diff.Pos()) < TOLERANCE_CLOSE:
            print("Move the tool to record points")
            continue
    else:
        target_prev = target
    
    newtarget = RDK.AddTarget('Target %i' % time, ref_frame, robot)

    if FEEDBACK_WITH_ROBOT:
        robot.setPose(target)

    pause(REFRESH_RATE)
    
    

    

    
    

