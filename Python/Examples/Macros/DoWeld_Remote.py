# This macro moves robots on remote devices.
# The movement is done with many robots simultaneously. Each robot movement has a new thread
# The device running the script decides where to move the robots (in this case, an hexagonal path is followed with respect to a reference target)
# The target device must have its API active
# Recommended: run after the project "MirrorDevices.py"
# Python needs to be installed only on the device running the script
# More information about the RoboDK API here:
# https://robodk.com/doc/en/RoboDK-API.html
from robodk.robolink import *    # API to communicate with RoboDK
from robodk.robomath import *    # basic matrix operations
import threading
import queue

# Tablet IP:
# 192.168.1.147
# Phone IP
# 192.168.1.171
IP_REMOTE_ADDRESS = '192.168.1.147'


def DoWeld(q, robotname, ipaddress):
    # Any interaction with RoboDK must be done through Robolink()
    # Each robot movement requires a new Robolink() object (new socket communication).
    # Two robots can't be moved by the same communication thread.

    RDK = Robolink(ipaddress)
    if RDK.Connect() == 0:
        print("Cant connect for robot %s" % robotname)
        return

    # get the robot item:
    robot = RDK.Item(robotname)

    # get the home joints target
    home = robot.JointsHome()

    # get the reference welding target:
    target = RDK.Item('Target')

    # get the reference frame and set it to the robot
    reference = target.Parent()
    robot.setFrame(reference)

    # get the pose of the target (4x4 matrix):
    poseref = target.Pose()
    pose_approach = poseref * transl(0, 0, -100)

    # move the robot to home, then to the center:
    robot.MoveJ(home)
    robot.MoveJ(pose_approach)
    robot.MoveL(target)

    # make an hexagon around the center:
    for i in range(7):
        ang = i * 2 * pi / 6  #angle: 0, 60, 120, ...
        posei = poseref * rotz(ang) * transl(200, 0, 0) * rotz(-ang)
        robot.MoveL(posei)

    # move back to the center, then home:
    robot.MoveL(target)
    robot.MoveL(pose_approach)
    robot.MoveJ(home)
    status = 'Done with %s' % robotname
    print(status)
    q.put(status)


# define the Queue thread
q = queue.Queue()

RDK = Robolink(IP_REMOTE_ADDRESS)
status = RDK.Connect()
print('Connection status (1 = ok, 0 = problems):')
print(status)
print('Robots to move:')
robots = RDK.ItemList(ITEM_TYPE_ROBOT, True)
print(robots)

# iterate through all robots and do welding
for i in range(len(robots)):
    robotname = robots[i]
    t = threading.Thread(target=DoWeld, args=(q, robotname, IP_REMOTE_ADDRESS))
    t.daemon = True
    t.start()

#print(q.get())
