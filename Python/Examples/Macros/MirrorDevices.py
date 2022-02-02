# This Macro allows sending the state of the robots from this computer to remote computers
# More information about the RoboDK API here:
# https://robodk.com/doc/en/RoboDK-API.html
# For more information visit:
# https://robodk.com/doc/en/PythonAPI/robodk.html#robolink-py
from robodk.robolink import *  # API to communicate with RoboDK
import threading
import queue

# Tablet IP:
# 192.168.1.147
# Phone IP
# 192.168.1.171

IP_SOURCE = 'localhost'

IP_REMOTE = ['192.168.1.147', '192.168.1.171']

PROJECT = 'Offline programming - 3 robots simultaneously.rdk'


def MirrorRobots(q, ip_source, ip_destination, project_path=None):
    # Any interaction with RoboDK must be done through Robolink()
    # The source and destination devices need a Robolink() instance each
    #
    RDK_src = Robolink(ip_source)
    RDK_dest = Robolink(ip_destination)

    # check connection with source device
    if RDK_src.Connect() == 0:
        print("Cannot connect to source %s" % ip_source)
        return

    # check connection with target device
    if RDK_dest.Connect() == 0:
        print("Cannot connect to destination %s" % ip_destination)
        return

    # open the station (if specified)
    if project_path is not None:
        path_lib = RDK_dest.getParam('PATH_LIBRARY')
        RDK_dest.AddFile(path_lib + '/' + project_path)

    # get the robot item identifiers on source device:
    robots_src = RDK_src.ItemList(ITEM_TYPE_ROBOT, False)

    # get the robot items identifiers on destination device:
    robots_dest = RDK_dest.ItemList(ITEM_TYPE_ROBOT, False)

    # Loop forever to update the joints
    while True:
        robot_jointstate = RDK_src.Joints(robots_src)
        RDK_dest.setJoints(robots_dest, robot_jointstate)

    q.put('Done with %s' % ip_destination)


q = queue.Queue()

RDK = Robolink()

# Open project in source device
if PROJECT is not None:
    path_lib = RDK.getParam('PATH_LIBRARY')
    RDK.AddFile(path_lib + '/' + PROJECT)

# iterate through all devices and start a new thread
for i in range(len(IP_REMOTE)):
    ip_remote = IP_REMOTE[i]
    t = threading.Thread(target=MirrorRobots, args=(q, IP_SOURCE, ip_remote, PROJECT))
    t.daemon = True
    t.start()

print(q.get())
