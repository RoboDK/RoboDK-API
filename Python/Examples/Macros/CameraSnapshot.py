# This macro provokes taking a snapshot from a simulated 2D camera
#
from robolink import *  # API to communicate with RoboDK
from robodk import *  # basic matrix operations

RDK = Robolink()

import datetime

date_str = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

file_name = RDK.getParam('PATH_OPENSTATION') + "/Image_" + date_str + ".png"

print("Saving camera snapshot to the file:" + file_name)

RDK.Cam2D_Snapshot(file_name)
