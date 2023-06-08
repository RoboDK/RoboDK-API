# This macro can load .LIS files from Comau programs in RoboDK.
#
# Type help("robodk.robolink") or help("robodk.robomath") for more information
# Press F5 to run the script
# Visit: http://www.robodk.com/doc/PythonAPI/
# For RoboDK API documentation

from robolink import *
from robodk import *


# Function to convert XYZWPR to a pose
# Important! Specify the order of rotation
def xyzwpr_to_pose(xyzwpr):
    pose = Comau_2_Pose(xyzwpr[:6])
    return pose


def string_2_doubles(string):

    def try_float(v):
        try:
            return float(v.strip())
        except Exception:
            return None

    # Containing floats and Nones:
    doubles = [try_float(item) for item in string.split(" ")]

    # Filter out the Nones:
    doubles = [item for item in doubles if item is not None]
    return doubles


# Load .LIS data as a list of poses
def load_targets(strfile):
    targets = []
    with open(strfile, "r") as fid:
        for line in fid.readlines():
            lineinfo = line.split(";")
            if len(lineinfo) < 3:
                continue

            t = {}
            t["name"] = lineinfo[0].strip()
            print("Reading target: " + t["name"])
            t["type"] = lineinfo[1].strip()
            t["values"] = string_2_doubles(lineinfo[2].replace(",", " ").replace("<", " ").replace(">", " ").strip())
            targets.append(t)

    return targets


if __name__ == "__main__":

    # Specify file codec
    codec = 'utf-8'  #'ISO-8859-1'

    # Start communication with RoboDK
    RDK = Robolink()

    # csv_file = 'C:/Users/UserName/Desktop/Var_P.csv'
    csv_file = getOpenFileName(RDK.getParam('PATH_OPENSTATION'), defaultextension='*.LIS')
    if not csv_file:
        quit()

    # Ask the user to select the robot (ignores the popup if only one robot is available)
    ROBOT = RDK.ItemUserPick('Select a robot', ITEM_TYPE_ROBOT)

    # Check if the user selected a robot
    if not ROBOT.Valid():
        RDK.ShowMessage('Please add a robot to the station.')
        quit()

    # Automatically retrieve active reference and tool
    FRAME = ROBOT.getLink(ITEM_TYPE_FRAME)
    TOOL = ROBOT.getLink(ITEM_TYPE_TOOL)

    #FRAME = RDK.ItemUserPick('Select a reference frame', ITEM_TYPE_FRAME)
    #TOOL = RDK.ItemUserPick('Select a tool', ITEM_TYPE_TOOL)

    #if not FRAME.Valid() or not TOOL.Valid():
    #    raise Exception("Select appropriate FRAME and TOOL references")

    #ROBOT.setFrame(FRAME)
    #ROBOT.setTool(TOOL)

    RDK.Render(False)  # Faster if we turn render off

    targets = load_targets(csv_file)
    program_name = getFileName(csv_file)
    program_name = program_name.replace('-', '_').replace(' ', '_')
    program = RDK.Item(program_name, ITEM_TYPE_PROGRAM)
    if program.Valid():
        program.Delete()

    program = RDK.AddProgram(program_name, ROBOT)
    if FRAME.Valid():
        program.setFrame(FRAME)
    if TOOL.Valid():
        program.setTool(TOOL)

    # ROBOT.MoveJ(ROBOT.JointsHome())

    for t in targets:
        name = t["name"]
        target = RDK.Item(name, ITEM_TYPE_TARGET)
        if target.Valid():
            target.Delete()

        target = RDK.AddTarget(name, FRAME, ROBOT)

        if t["type"] == "JNTP":
            target.setAsJointTarget()
            target.setJoints(t["values"])
            target.setParam("Recalculate")

        else:
            target.setAsCartesianTarget()
            pose = xyzwpr_to_pose(t["values"])

            if len(t["values"]) > 6:
                # Type is XTND
                target.setJoints([0] * 6 + t["values"][6:])

            target.setPose(pose)
            target.setParam("Recalculate")

        try:
            program.MoveJ(target)
        except:
            print('Warning: %s can not be reached. It will not be added to the program' % name)