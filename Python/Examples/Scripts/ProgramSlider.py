# This macro provides an example to extract the joints of a program. 
# The joints extracted take into account the rounding effect.
from robolink import *    # API to communicate with RoboDK
from robodk import *      # basic matrix operations
import sys

# Start the RoboDK API:
RDK = Robolink()

# Get the robot and the program available in the open station:
robot = RDK.Item('', ITEM_TYPE_ROBOT_ARM)


# First, check if we are getting a list of joints through the command line:
if len(sys.argv) >= 2:
    joint_list = Mat(LoadList(sys.argv[1]))

#elif True:
#    joint_list = Mat(LoadList(r'joints.csv'))
    
else:
    # Option one, retrieve joint list as a matrix (not through a file):
    prog = RDK.ItemUserPick('Select a Program', ITEM_TYPE_PROGRAM)
    
    # Define the way we want to output the list of joints
    Position = 1        # Only provide the joint position and XYZ values
    Speed = 2           # Calculate speed (added to position)
    SpeedAndAcceleration = 3 # Calculate speed and acceleration (added to position)
    TimeBased = 4       # Make the calculation time-based (adds a time stamp added to the previous options)
    TimeBasedFast = 5   # Make the calculation time-based and avoids calculating speeds and accelerations (adds a time stamp added to the previous options)
    
    STEP_MM = 1
    STEP_DEG = 1
    FLAGS = TimeBasedFast
    #FLAGS = TimeBased
    TIME_STEP = 0.025 # time step in seconds
    status_msg, joint_list, status_code = prog.InstructionListJoints(STEP_MM, STEP_DEG, flags=FLAGS, time_step=TIME_STEP)

    # Option two, write the joint list to a file (recommended if step is very small)
    #STEP_MM = 0.5
    #STEP_DEG = 0.5
    #status_msg, joint_list, status_code = prog.InstructionListJoints(STEP_MM, STEP_DEG, 'C:/Users/user/Desktop/InstructionListJoints' + prog.Name() + '.csv', flags=FLAGS, time_step=TIME_STEP)
    #quit(0)
    
    # Status code is negative if there are errors in the program
    print(joint_list.tr())    
    print("Size: " + str(len(joint_list)))
    print("Status code:" + str(status_code))
    print("Status message: " + status_msg)
    


# Show as a sequence
if False:
    # detect if joint_list is a file or a list
    if type(joint_list) is str:
        print('Program saved to %s' % joint_list)
    else:
        print('Showing joint sequencence in RoboDK')
        robot.ShowSequence(joint_list[:6,:])
    quit()



import tkinter as tk
import threading 

# Number of points
np = len(joint_list)

# Nuber of degrees of freedom (robot)
global njoints
njoints = len(robot.Joints().list())

# Create a new window
window = tk.Tk()

# Slider variable
var = tk.DoubleVar()

# Lock to prevent using the RoboDK API from 2 different threads
lock = threading.Lock()


def SliderUpdated(obj):
    """Slider moved: run the program on a separate thread. Otherwise, the UI will be blocked"""
    def thread_btnSelect():
        global njoints

        # We need to lock this section of code to make sure we dont access the RoboDK API from 2 different trheads, otherwise we would have to create a second instance of Robolink
        lock.acquire()
        idjoints = int(var.get())
        jointinfo = joint_list[:,idjoints].list()
        robot.setJoints(jointinfo[:njoints])
        e_flags = jointinfo[njoints]
        step_mm = jointinfo[njoints+1]
        step_deg = jointinfo[njoints+2]
        move_id = jointinfo[njoints+3]
        step_sec = jointinfo[njoints+4]
        extra_info = "MoveID=%.0f     Step=%.1f mm | %.1f deg | %.3f sec" % (move_id, step_mm, step_deg, step_sec)
        if abs(e_flags) > 0.001:
            extra_info += ("      *** ErrorFlags=%.0f ***" % e_flags)
            
        RDK.ShowMessage(("Index %i ->    " % (idjoints)) + extra_info, False)
        lock.release()

    threading.Thread(target=thread_btnSelect).start()

# Add a slider widget
w2 = tk.Scale(window, from_=0, to=np-1, tickinterval=np/10, orient=tk.HORIZONTAL, variable=var, command=SliderUpdated)
# Set the value of 0
w2.set(0)
w2.pack(fill=tk.BOTH, expand=1)

#Button(window_title, text='Show', command=show_values).pack()

# Embed the window at the bottom
window_title = 'Program Slider'
window.title(window_title)
EmbedWindow(window_title, area_add=8)

# Run the UI loop
tk.mainloop()
