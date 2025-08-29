# This example shows how to estimate the execution time of a program with a variable speed
#
# Important notes and tips for accurate cycle time calculation:
# https://robodk.com/doc/en/General.html#CycleTime

# Start the RoboDK API
from robodk.robolink import *  # API to communicate with RoboDK
from robodk.robomath import *  # Robot toolbox

RDK = Robolink()
# Ask the user to select a program
prog = RDK.ItemUserPick('Select a Program', ITEM_TYPE_PROGRAM)

# Retrieve the robot linked to the selected program
robot = prog.getLink(ITEM_TYPE_ROBOT)

# Assume that the default robot speed is 1000 mm/s
cur_spd = 1000

# Create a map of speeds for the program
spd_map = []

ins_count = prog.InstructionCount()
ins_id = 0

while ins_id < ins_count:

    instruction_dict = prog.setParam(ins_id)

    if instruction_dict['Type'] == INS_TYPE_CHANGESPEED:
        cur_spd = instruction_dict['Speed']

    elif instruction_dict['Type'] == INS_TYPE_MOVE:
        spd_map.append(cur_spd)

    ins_id = ins_id + 1

# Get a list of joints that contains motion ids
STEP_MM = 1
STEP_DEG = 1
FLAGS = 1

status_msg, joint_list, status_code = prog.InstructionListJoints(STEP_MM, STEP_DEG, flags=FLAGS)

# Calculate the motion time and actual distance for each step and sum these times
cycle_time = 0.0
motion_ins_id = 0

njoints = len(robot.Joints().list())

jointinfo = joint_list[:, 0].list()

x = jointinfo[njoints + 5]
y = jointinfo[njoints + 6]
z = jointinfo[njoints + 7]

prt_old = [x, y, z]

for jointinfo in joint_list:

    x = jointinfo[njoints + 5]
    y = jointinfo[njoints + 6]
    z = jointinfo[njoints + 7]

    prt_new = [x, y, z]

    d = distance(prt_old, prt_new)

    prt_old = prt_new

    motion_ins_id = int(jointinfo[njoints + 3])
    cycle_time += d / spd_map[motion_ins_id - 1]

# Output the linear speed, joint speed and time (separated by tabs)
writeline = "Program name\tProgram status (100%=OK)\tTravel length\tCycle Time"
print(writeline)
# Prepare an HTML message we can show to the user through the RoboDK API:
msg_html = "<table border=1><tr><td>" + writeline.replace('\t', '</td><td>') + "</td></tr>"

# Check the program status
prog_stats = prog.Update()
travel = prog_stats[2]
ok = prog_stats[3]

# Print the information
newline = "%s\t%.0f %%\t%.1f mm\t%.1f s" % (prog.Name(), ok * 100, travel, cycle_time)
print(newline)
msg_html = msg_html + '<tr><td>' + newline.replace('\t', '</td><td>') + '</td></tr>'

msg_html = msg_html + '</table>'

RDK.ShowMessage(msg_html)
