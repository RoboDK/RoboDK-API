# This macro shows how to convert any program to only linear movements.
# Circular movements will be replaced by small linear movements given a step tolerance.
# Type help("robolink") or help("robodk") for more information
# Press F5 to run the script
# Or visit: http://www.robodk.com/doc/PythonAPI/
# Note: you do not need to keep a copy of this file, your python script is saved with the station
from robolink import *  # API to communicate with RoboDK
from robodk import *  # basic matrix operations

RDK = Robolink()

STEP_MM = 1
STEP_DEG = 1

prog = RDK.Item('BallbarTest')
if not prog.Valid():
    raise Exception("Create a BallbarTest program first!")

robot = RDK.Item('', ITEM_TYPE_ROBOT)
if not robot.Valid():
    raise Exception("No robot available!")

reference = robot.Parent()
pose_tool = robot.Childs()[0].PoseTool()

status_joint_list = prog.InstructionListJoints(STEP_MM, STEP_DEG)
joint_list = status_joint_list[1]

njoints = joint_list.size(1)

targets = RDK.ItemList(ITEM_TYPE_TARGET, False)
RDK.Render(False)
for target in targets:
    if target.Name().startswith('Mov'):
        target.Delete()

if njoints < 2:
    raise Exception('Invalid program!')

new_prog = RDK.AddProgram('BallbarTestLin')

new_prog.setTool(robot.Childs()[0])
target = RDK.AddTarget('MovJ 1', reference, robot)
target.setJoints(joint_list[:6, 0].tolist())
new_prog.MoveJ(target)

for i in range(1, njoints):
    targeti = RDK.AddTarget('MovL %i' % (i + 1), reference, robot)
    joints_i = joint_list[:6, i].tolist()
    targeti.setJoints(joints_i)
    targeti.setPose(robot.SolveFK(joints_i) * pose_tool)
    new_prog.MoveL(targeti)

RDK.Render(True)
new_prog.RunProgram()
