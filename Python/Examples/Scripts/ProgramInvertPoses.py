# This macro allows adding a program call after each movement instruction in a program
# This macro shows an example to use prog.InstructionSelect()
# This macro is useful if we want to synchronize motion between 2 robots for a calibration task
from robolink import *  # API to communicate with RoboDK
from robodk import *  # basic matrix operations

RDK = Robolink()

# Ask the user to select a program:
prog = RDK.ItemUserPick("Select a Program to invert the poses (useful if you have a Remote TCP setup)", ITEM_TYPE_PROGRAM)
if not prog.Valid():
    print("Operation cancelled or no programs available")
    quit()

# Iterate through all the instructions in a program:
ins_id = 0
ins_count = prog.InstructionCount()
RDK.ShowMessage("Inverting poses for program: " + prog.Name(), False)
RDK.Render(False)
while ins_id < ins_count:
    # Retrieve instruction
    ins_name, ins_type, move_type, isjointtarget, pose, joints = prog.Instruction(ins_id)
    if ins_type == INS_TYPE_MOVE:
        # Invert the pose:
        pose = invH(pose)
        prog.setInstruction(ins_id, ins_name, ins_type, move_type, isjointtarget, pose, joints)

    ins_id += 1

RDK.ShowMessage("Done", False)