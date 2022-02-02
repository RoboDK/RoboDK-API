# This macro will override the first joint move in each program and set it as a linear move
# WARNING! The configuration might not be set as desired and the robot may move in an undesired way (different from the simulated movements)
from robodk.robolink import *  # API to communicate with RoboDK

RDK = Robolink()

progs = []
progs_all = RDK.ItemList(ITEM_TYPE_PROGRAM, False)

for prog in progs_all:
    # Example to filter programs by name
    #prog_name = prog.Name()
    #if prog_name.endswith('-2'):
    #    print('Programme %s selected automatically' % prog_name)
    #    progs.append(prog)
    progs.append(prog)

if len(progs) == 0:
    print('No programs found')
    prog = RDK.ItemUserPick('Select a program to impose a linear move as first movement', ITEM_TYPE_PROGRAM)
    if not prog.Valid():
        quit()
    progs.append(prog)

for prog in progs:
    prog_name = prog.Name()
    nins = prog.InstructionCount()
    for ins_id in range(nins):
        ins_name, ins_type, move_type, isjointtarget, pose, joints = prog.Instruction(ins_id)
        if ins_type == INS_TYPE_MOVE:
            if move_type == MOVE_TYPE_JOINT:
                prog.setInstruction(ins_id, '*MoveL', ins_type, MOVE_TYPE_LINEAR, False, pose, joints)
                RDK.ShowMessage('Program %s modified Successfully' % prog_name, False)

            else:
                RDK.ShowMessage('The first movements for %s is already linear' % prog_name, False)

            break
