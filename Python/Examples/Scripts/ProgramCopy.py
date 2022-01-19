# This script shows how you can copy a program.
# More information here: https://robodk.com/doc/en/PythonAPI/examples.html#modify-program-instructions

# Type help("robolink") or help("robodk") for more information
# Press F5 to run the script
# Or visit: http://www.robodk.com/doc/PythonAPI/
# Note: you do not need to keep a copy of this file, your python script is saved with the station
from robolink import *    # API to communicate with RoboDK
from robodk import *      # basic matrix operations
RDK = Robolink()

# Enter the step tolerance in MM and Degrees
STEP_MM = 2
STEP_DEG = 2

#prog = RDK.Item('BallbarTest')
prog = RDK.ItemUserPick('Select a program to copy', ITEM_TYPE_PROGRAM)
if not prog.Valid():
    msg = "Create a program first"
    RDK.ShowMessage(msg)
    raise Exception(msg)

new_prog_name = "Copy of " + prog.Name()

#--------------------------------
# Method 1: Use Copy/Paste (this is the same as Ctrl+C and Ctrl+V)
if False:
    prog.Copy()
    new_prog = RDK.Paste()
    new_prog.setName(new_prog_name)
    new_prog.ShowInstructions(True)
    quit()


#--------------------------------
# Method 2: Create a new program and use setParam and copy instruction by instruction
# This is useful 
RDK.Render(False)
robot = prog.getLink(ITEM_TYPE_ROBOT)
new_prog = RDK.AddProgram(new_prog_name, robot)

nInstructions = prog.InstructionCount()
for i in range(nInstructions):
    ins_data = prog.setParam(i)
    print("Instruction: " + str(i))
    print(ins_data)
    new_prog.setParam("Add", ins_data)

RDK.Render(True)
new_prog.RunProgram()
