# This example shows how to create a small UI window embedded in RoboDK

# Type help("robolink") or help("robodk") for more information
# Press F5 to run the script
# Documentation: https://robodk.com/doc/en/RoboDK-API.html
# Reference:     https://robodk.com/doc/en/PythonAPI/index.html
# Note: It is not required to keep a copy of this file, your python script is saved with the station
from robolink import *    # RoboDK API
from robodk import *      # Robot toolbox
from tkinter import *

NUM_SIDES = 7
LENGTH = 200

RDK = Robolink()

robot = RDK.Item('', ITEM_TYPE_ROBOT)
# get the home target and the welding targets:
home = RDK.Item('Home')
if not home.Valid():
    raise Exception("Home target not defined")

target = RDK.Item('Target Reference')
if not target.Valid():
    raise Exception("Target Reference not available")

def RunProgram():
    global NUM_SIDES
    global LENGTH
    target_pose = target.Pose()
    target_xyz = target_pose.Pos()
    # Move the robot to the reference point:
    robot.MoveJ(home)
    robot.MoveJ(target)
    for i in range((NUM_SIDES) + 1):
        angle = i*2*pi/NUM_SIDES
        posei = target_pose * rotz(angle) * transl(LENGTH,0,0) * rotz(-angle)
        robot.MoveL(posei)
    robot.MoveL(target)
    robot.MoveJ(home)
    #RDK.Finish()
    
# Create option window
root = Tk()
num_sides = StringVar()
num_sides.set(str(NUM_SIDES))
length = StringVar()
length.set(str(LENGTH))
Label(root,text = "Enter the number of sides for polygon").pack()
Entry(root,textvariable = num_sides).pack()

Label(root,text = "Enter the radius").pack()
Entry(root,textvariable = length).pack()

import threading
rdk_lock = threading.Lock()

def ExecuteChoice():
    def thread_ExecuteChoice():
        """We need to run on a separate thread to make sure we don't block the main loop, otherwise, RoboDK will freeze"""
        global NUM_SIDES
        global LENGTH
        NUM_SIDES = int(num_sides.get())
        LENGTH = float(length.get())
        # We need to make sure we don't run the program twice at the same time
        if rdk_lock.locked():
            print("Operation ignored. Waiting to complete previous movement...")
            return

        rdk_lock.acquire()
        RunProgram()
        rdk_lock.release()

    threading.Thread(target=thread_ExecuteChoice).start()

Button(root,text = "Start",command = ExecuteChoice).pack()

# Embed the window in RoboDK
window_title = "Weld path"
root.title(window_title)
EmbedWindow(window_title)

root.mainloop()






