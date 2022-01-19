# This example shows how to modify program instructions
# See also:
# https://robodk.com/doc/en/PythonAPI/robolink.html#robolink.Robolink.AddProgram

from robodk.robolink import *    # API to communicate with RoboDK
import json

# Start the RoboDK API
RDK = Robolink()

# Ask the user to select a program:
prog = RDK.ItemUserPick("Select a Program to modify", ITEM_TYPE_PROGRAM)
if not prog.Valid():
    print("Operation cancelled or no programs available")
    quit()

# Ask the user to enter a function call that will be added after each movement:
print("Program selected: " + prog.Name())

# Iterate for all instructions (index start is 0, you can also use -1 for the last instruction)
ins_count = prog.InstructionCount()
ins_id = 0
while ins_id < ins_count:
    # Get specific data related to an instruction
    # This operation always retuns a dict (json)
    instruction_dict = prog.setParam(ins_id)

    # Print instruction data
    #indented_values = json.dumps(instruction_dict, indent=4)
    print("\n\nInstruction: " + str(ins_id))
    print(instruction_dict)

    # Note: The type is unique for each instruction and can't be changed.
    #    However, setting the Type value to -1 will delete the instruction (same as InstructionDelete())
    if instruction_dict['Type'] == INS_TYPE_CHANGESPEED:
        # Reduce speeds:
        newvalues = {'Speed': 50}
        if instruction_dict['Speed'] > 50:
            new_speed = 0.8 * instruction_dict['Speed']
            newvalues = {'Speed': new_speed}
            print("Reducing speed to: %.3f" % new_speed)

        # Update instruction data
        prog.setParam(ins_id, newvalues)
        # RoboDK may change the instruction name if you don't provide a new name

    elif instruction_dict['Type'] == INS_TYPE_CODE:
        # Select the movement instruction as a reference to add new instructions
        prog.InstructionSelect(ins_id)

        # Add a new program call
        prog.RunInstruction("Post" + instruction_dict['Code'], INSTRUCTION_CALL_PROGRAM)

        # Important: We just added a new instruction, so make sure we skip this instruction index!
        ins_id = ins_id + 1

    elif instruction_dict['Type'] == INS_TYPE_PAUSE:
        print("Deletint pause instruction")
        prog.InstructionDelete(ins_id)

        # Another way of deleting instructions:
        #delete_command = {'Type':-1}
        #prog.setParam(ins_id, delete_command)

        # Important: We just deleted an instruction, so make sure we recalculate our instruction index
        ins_id = ins_id - 1

    elif instruction_dict['Type'] == INS_TYPE_MOVE:
        print("Move instruction: use setInstruction to modify target")
        #ins_name, ins_type, move_type, isjointtarget, pose, joints = prog.Instruction(ins_id)
        #prog.setInstruction(ins_id, ins_name, ins_type, move_type, isjointtarget, pose, joints)

    ins_id = ins_id + 1

# Remove selection automatically created for new instructions
RDK.setSelection([])
