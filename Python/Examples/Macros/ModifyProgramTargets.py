# Example to rotate each point of a program with respect to the tool Z axis

# Start the RoboDK API
from robolink import *
from robodk import *
RDK = Robolink()

# set the rotation in radians
TOOL_RZ = 30 * pi / 180

# Ask the user to select a program
prog = RDK.ItemUserPick('Select a program to rotate targets', ITEM_TYPE_PROGRAM)
if not prog.Valid():
    # exit if the user selected cancel or no programs were available
    quit()

prog_name = prog.Name()
RDK.ShowMessage("Modifying program " + prog_name, False)

nins = prog.InstructionCount()
# Iterate through all the instructions and rotate poses of linear movements
for ins_id in range(nins):
    ins_name, ins_type, move_type, isjointtarget, pose, joints = prog.Instruction(ins_id)
    if ins_type == INS_TYPE_MOVE:
        if move_type == MOVE_TYPE_LINEAR:
            pose_rotated = pose*rotz(TOOL_RZ)
            prog.setInstruction(ins_id, ins_name, ins_type, move_type, isjointtarget, pose_rotated, joints)                
            print("Changing instruction " + ins_name)

RDK.ShowMessage("Done modifying program " + prog_name, False)