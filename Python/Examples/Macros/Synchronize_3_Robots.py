# Type help("robolink") or help("robodk") for more information
# Press F5 to run the script
# Documentation: https://robodk.com/doc/en/RoboDK-API.html
# Reference:     https://robodk.com/doc/en/PythonAPI/index.html
#
# This example shows to synchronize multiple robots at the same time

from robolink import *  # API to communicate with RoboDK for offline/online programming
from robodk import *  # Robotics toolbox for industrial robots

import threading
import queue

#----------------------------------------------
# Function definitions and global variable declarations

# Global variables used to synchronize the robot movements
# These variables are managed by SyncSet() and SynchWait()

SYNC_COUNT = 0
SYNC_TOTAL = 0
SYNC_ID = 0
lock = threading.Lock()


def SyncSet(total_sync):
    """SyncSet will set the number of total robot programs (threads) that must be synchronized togeter.
    Every time SyncSet is called SYNC_ID is increased by one."""
    global SYNC_COUNT
    global SYNC_TOTAL
    global SYNC_ID
    with lock:
        SYNC_COUNT = 0
        SYNC_TOTAL = total_sync
        SYNC_ID = SYNC_ID + 1
        #print('SyncSet')


def SyncWait():
    """SyncWait will block the robot movements for a robot when necessary, synchronizing the movements sequentially.
    Use SyncSet(nrobots) to define how many robots must be synchronized together."""
    global SYNC_COUNT
    # Save a local variable with the sync event id
    sync_id = SYNC_ID
    with lock:
        # Increase the number of threads that are synchronized
        SYNC_COUNT += 1

    # Move to the next sync event if all threads reached the SyncWait (SYNC_COUNT = SYNC_TOTAL)
    if SYNC_COUNT >= SYNC_TOTAL:
        SyncSet(SYNC_TOTAL)
        return

    # Wait for a SynchSet to move forward
    while sync_id >= SYNC_ID:
        time.sleep(0.0001)


# Main procedure to move each robot
def DoWeld(q, robotname):
    # Any interaction with RoboDK must be done through Robolink()
    # Each robot movement requires a new Robolink() object (new link of communication).
    # Two robots can't be moved by the same communication link.

    rdk = Robolink()

    # get the robot item:
    robot = rdk.Item(robotname)

    # get the home joints target
    home = robot.JointsHome()

    # get the reference welding target:
    target = rdk.Item('Target')

    # get the reference frame and set it to the robot
    reference = target.Parent()
    robot.setPoseFrame(reference)

    # get the pose of the target (4x4 matrix):
    poseref = target.Pose()
    pose_approach = poseref * transl(0, 0, -100)

    # move the robot to home, then to the center:
    robot.MoveJ(home)
    robot.MoveJ(pose_approach)
    SyncWait()
    robot.MoveL(target)

    # make an hexagon around the center:
    for i in range(7):
        ang = i * 2 * pi / 6  #angle: 0, 60, 120, ...
        posei = poseref * rotz(ang) * transl(200, 0, 0) * rotz(-ang)
        SyncWait()
        robot.MoveL(posei)

    # move back to the center, then home:
    SyncWait()
    robot.MoveL(target)
    robot.MoveL(pose_approach)
    robot.MoveJ(home)
    q.put('Robot %s finished' % robotname)


#----------------------------------------
# Python program start

# retrieve all available robots in the RoboDK station (as a list of names)
RDK = Robolink()
robots = RDK.ItemList(ITEM_TYPE_ROBOT)
print(robots)

# retrieve the number of robots to synchronize together
nrobots = len(robots)
SyncSet(nrobots)

# the queue allows sharing messages between threads
q = queue.Queue()

# Start the DoWeld program for all robots. Each robot will run on a separate thread.
threads = []
for i in range(nrobots):
    robotname = robots[i]
    t = threading.Thread(target=DoWeld, args=(q, robotname))
    t.daemon = True
    t.start()
    threads.append(t)

# wait for every thead to finish
for x in threads:
    x.join()
    print(q.get())

print('Main program finished')
