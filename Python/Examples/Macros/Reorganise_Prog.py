# Type help("robodk.robolink") or help("robodk.robomath") for more information
# Press F5 to run the script
# Documentation: https://robodk.com/doc/en/RoboDK-API.html
# Reference:     https://robodk.com/doc/en/PythonAPI/index.html
# Note: It is not required to keep a copy of this file, your Python script is saved with your RDK project
from robodk import robolink    # RoboDK API
from robodk import robomath    # Robot toolbox
from robolink import *

# The goal of this macro is to find the first 2 program calls of a machining program and bring them as the first instructions of the program
# This would mainly bring "SetTool" and "SetRPM" up front.
RDK = robolink.Robolink()

# Ask the User to pick a program 
prog = RDK.ItemUserPick('Select an item',ITEM_TYPE_PROGRAM)

if not prog.Valid():
    print("Select a valid program.")
    quit()

insert_position = 0

for instruction in range(0,prog.InstructionCount()):
    instruction_dict = prog.setParam(instruction)

    # If the instruction is a Program Call
    if instruction_dict['Type']==INS_TYPE_CODE:        
        # Choose if you want to reorder before or after
        reorder_cmd = "ReorderBefore"
        #reorder_cmd = "ReorderAfter"

        # Warning: This can crash if id's are not valid
        prog.setParam(reorder_cmd, str(instruction) + "|" + str(insert_position) + "|" + str(prog.item))

        # Increment insert position 
        insert_position += 1
        # Do this for the first 2 Prog Call
        if insert_position == 2:
            break

path_progs = RDK.Command("PATH_PROGRAMS")
prog.MakeProgram(path_progs)