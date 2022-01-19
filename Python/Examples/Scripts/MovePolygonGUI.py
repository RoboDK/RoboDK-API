# This example shows how RoboDK and the Python GUI tkinter can display graphical user interface to customize program generation according to certain parameters
# This example is an improvement of the weld Hexagon
from robolink import *  # API to communicate with RoboDK
from robodk import *  # robodk robotics toolbox
import threading

# Set up default parameters
PROGRAM_NAME = "DoWeld"  # Name of the program
APPROACH = 300  # Approach distance
RADIUS = 200  # Radius of the polygon
SPEED_WELD = 50  # Speed in mn/s of the welding path
SPEED_MOVE = 200  # Speed in mm/s of the approach/retract movements
SIDES = 8  # Number of sides for the polygon
DRY_RUN = 1  # If 0, it will generate SprayOn/SprayOff program calls, otherwise it will not activate the tool
RUN_MODE = RUNMODE_SIMULATE  # Simulation behavior (simulate, generate program or generate the program and send it to the robot)

# use RUNMODE_SIMULATE to simulate only
# use RUNMODE_MAKE_ROBOTPROG to generate the program
# use RUNMODE_MAKE_ROBOTPROG_AND_UPLOAD to generate the program and send it to the robot


# Main program
def RunProgram():
    # Use default global variables
    global PROGRAM_NAME
    global APPROACH
    global RADIUS
    global SPEED_WELD
    global SPEED_MOVE
    global SIDES
    global DRY_RUN
    global RUN_MODE

    # Any interaction with RoboDK must be done through RDK:
    RDK = Robolink()

    # Get the robot (first robot found):
    robot = RDK.Item('', ITEM_TYPE_ROBOT)
    if not robot.Valid():
        RDK.ShowMessage("Robot is not valid or selected", False)

    # Get the reference target by name:
    #target = RDK.Item('Target 1')
    #target_pose = target.Pose()
    #robot.MoveJ(target)

    # get the robot as an item:
    robot = RDK.Item('', ITEM_TYPE_ROBOT)

    # impose the run mode
    RDK.setRunMode(RUN_MODE)
    # set the name of the generated program
    RDK.ProgramStart(PROGRAM_NAME, "", "", robot)

    # get the pose of the reference target (4x4 matrix representing position and orientation):
    poseref = robot.Pose()  # or target.Pose()

    # move the robot to home, then to an approach position
    robot.setSpeed(SPEED_MOVE)
    robot.MoveJ(transl(0, 0, APPROACH) * poseref)

    # make an polygon of n SIDES around the reference target
    for i in range(SIDES + 1):
        ang = i * 2 * pi / SIDES  #angle: 0, 60, 120, ...
        # Calculate next position
        posei = poseref * rotz(ang) * transl(RADIUS, 0, 0) * rotz(-ang)
        robot.MoveL(posei)

        # Impose weld speed only for the first point
        if i == 0:
            # Set weld speed and activate the gun after reaching the first point
            robot.setSpeed(SPEED_WELD)
            if not DRY_RUN:
                # Activate the spray right after we reached the first point
                robot.RunInstruction("SprayOn", INSTRUCTION_CALL_PROGRAM)

    # Stop the tool if we are not doing a dry run
    if not DRY_RUN:
        robot.RunInstruction("SprayOff", INSTRUCTION_CALL_PROGRAM)

    robot.setSpeed(SPEED_MOVE)

    # move back to the approach point, then home:
    robot.MoveL(transl(0, 0, APPROACH) * poseref)
    robot.MoveJ(home)

    # Provoke program generation (automatic when RDK is finished)
    RDK.Finish()


# Use tkinter to display GUI menus
#from tkinter import *
import tkinter as tk

# Generate the main window
window = tk.Tk()

# Use variables linked to the global variables
runmode = tk.IntVar()
runmode.set(RUN_MODE)  # setting up default value

dryrun = tk.IntVar()
dryrun.set(DRY_RUN)  # setting up default value

entry_name = tk.StringVar()
entry_name.set(PROGRAM_NAME)

entry_speed = tk.StringVar()
entry_speed.set(str(SPEED_WELD))


# Define feedback call
def ShowRunMode():
    print("Selected run mode: " + str(runmode.get()))


# Define a label and entry text for the program name
tk.Label(window, text="Program name").pack(fill=tk.X, expand=0)
tk.Entry(window, textvariable=entry_name).pack(fill=tk.X, expand=0)

# Define a label and entry text for the weld speed
tk.Label(window, text="Weld speed (mm/s)").pack(fill=tk.X, expand=0)
tk.Entry(window, textvariable=entry_speed).pack(fill=tk.X, expand=0)

# Define a check box to do a dry run
tk.Checkbutton(window, text="Dry run", variable=dryrun, onvalue=1, offvalue=0, height=5, width=20).pack(fill=tk.X, expand=0)

# Add a display label for the run mode
tk.Label(window, text="Run mode", justify=tk.LEFT, padx=20).pack(fill=tk.X, expand=0)

# Set up the run modes (radio buttons)
runmodes = [("Simulate", RUNMODE_SIMULATE), ("Generate program", RUNMODE_MAKE_ROBOTPROG), ("Send program to robot", RUNMODE_MAKE_ROBOTPROG_AND_START)]
for txt, val in runmodes:
    tk.Radiobutton(window, text=txt, padx=20, variable=runmode, command=ShowRunMode, value=val).pack(fill=tk.X, expand=0)


# Add a button and default action to execute the current choice of the user
def ExecuteChoice():

    def run_thread():
        global DRY_RUN
        global RUN_MODE
        global SPEED_WELD
        global PROGRAM_NAME
        DRY_RUN = dryrun.get()
        RUN_MODE = runmode.get()
        SPEED_WELD = float(entry_speed.get())
        PROGRAM_NAME = entry_name.get()
        # Run the main program once all the global variables have been set
        try:
            RunProgram()
        except Exception as e:
            RDK = Robolink()
            msg = "Unextected program error: " + str(e)
            RDK.ShowMessage(msg, False)
            print(msg)
            raise e  # raise the error (visible if we are in console mode)

    threading.Thread(target=run_thread).start()


tk.Button(window, text='Simulate/Generate', command=ExecuteChoice, height=4).pack(fill=tk.BOTH, expand=0)

# Set window name
window_title = "Move Polygon Program"
window.title(window_title)

# We can embed the window into RoboDK as a docked window
# Make sure the window title is unique
EmbedWindow(window_title)

# Important to display the graphical user interface
window.mainloop()
