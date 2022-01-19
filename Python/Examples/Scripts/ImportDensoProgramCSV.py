# This macro can load CSV files from Denso programs in RoboDK.
# Supported types of files are:
#  1-Tool data : Tool.csv
#  2-Work object data: Work.csv
#  3-Target data: P_Var.csv (will look for Tool.csv and Work.csv in the same folder)
# This macro can also filter the P_Var.csv file for improved accuracy
#
# Type help("robolink") or help("robodk") for more information
# Press F5 to run the script
# More information about the RoboDK API here:
# https://robodk.com/doc/en/RoboDK-API.html
# Visit: https://robodk.com/doc/en/PythonAPI/index.html
# For RoboDK API documentation

from robolink import *  # API to communicate with RoboDK
from robodk import *  # basic matrix operations


# Euler angles to pose coming from CSV files
def Adept_CSV_2_Pose(xyzwpr):
    x, y, z, rx, ry, rz = xyzwpr
    return transl(x, y, z) * rotz(rz * pi / 180) * roty(ry * pi / 180) * rotx(rx * pi / 180)


# Start communication with RoboDK
RDK = Robolink()

# Select the robot
robot = RDK.ItemUserPick('Select a robot', ITEM_TYPE_ROBOT)

# Check if the user selected a robot. Quit if Cancel.
if not robot.Valid():
    quit()

# Check if the robot is named "Denso ..."
if not robot.Name().startswith('Denso'):
    raise Exception("This macro works for Denso robots only")

# Get the robot base frame
robot_base = robot.Parent()

# csv_file = 'C:/Users/Albert/Desktop/Var_P.csv'
csv_file = getOpenFile(RDK.getParam('PATH_OPENSTATION'))
if not csv_file:
    quit()

# Specify file codec
codec = 'ISO-8859-1'


# Load Work.CSV data as a list of poses
def load_refs(strfile):
    csvdata = LoadList(strfile, ',', 'ISO-8859-1')
    poses = []
    names = []
    for i in range(5, len(csvdata)):
        if csvdata[i][8] == '""':
            break
        names.append(csvdata[i][8][1:-1])
        poses.append(Adept_CSV_2_Pose(csvdata[i][1:7]))
    return poses, names


# Load Tool.CSV data as a list of poses
def load_tools(strfile):
    csvdata = LoadList(strfile, ',', codec)
    poses = []
    names = []
    for i in range(5, len(csvdata)):
        if csvdata[i][7] == '""':
            break
        names.append(csvdata[i][7][1:-1])
        poses.append(Adept_CSV_2_Pose(csvdata[i][1:7]))
    return poses, names


# Load P_Var.CSV data as a list of poses, including links to reference and tool frames
def load_targets(strfile):
    csvdata = LoadList(strfile, ',', codec)
    poses = []
    names = []
    refnames = []
    toolnames = []
    configs = []
    for i in range(5, len(csvdata)):
        if csvdata[i][8] == '""':
            break
        description = csvdata[i][8][1:-1]
        name_link = description.split(' on ')
        if len(name_link) < 2:
            raise Exception('Unexpected name for target %i: %s' % (i + 1, name_link))
        names.append(name_link[0])
        ref_tool = name_link[1].split('-')
        if len(ref_tool) < 2:
            raise Exception('Unexpected reference-tool link for target %i: %s' % (i + 1, ref_tool))

        # add the name of the reference frame to the list.
        # Important! if the name is Work0 it means it is the same robot base frame
        if ref_tool[0] == "WORK0":
            refnames.append(robot.Parent().Name())
        else:
            refnames.append(ref_tool[0])

        # Add the name of the TCP to the list
        toolnames.append(ref_tool[1])
        poses.append(Adept_CSV_2_Pose(csvdata[i][1:7]))
        configs.append(csvdata[i][7])
    return poses, names, refnames, toolnames, configs


# Load and display reference frames from Work.CSV in RoboDK
def load_refs_station(strfile):
    poses, names = load_refs(strfile)
    for pose, name in zip(poses, names):
        frame = RDK.Item(name, ITEM_TYPE_FRAME)
        if not frame.Valid():
            frame = RDK.AddFrame(name, robot_base)
        frame.setPose(pose)


# Load and display tool frames from Tool.CSV in RoboDK
def load_tools_station(strfile):
    poses, names = load_tools(strfile)
    for pose, name in zip(poses, names):
        tool = RDK.Item(name, ITEM_TYPE_TOOL)
        if tool.Valid():
            tool.setPoseTool(pose)
        else:
            tool = robot.AddTool(pose, name)


# ---------------------------------------------------------------------------
# Calculate the joint data given the information about the target configuration
def target_joints(pose_target, pose_ref, pose_tool, str_config, name):
    # str_config = 17 - Lefty | Above | Flip | J6Single | J4Double | J1Single
    config_RLF = [0, 0, 0]
    if str_config.index('Lefty') < 0:
        config_RLF[0] = 1
    if str_config.index('Above') < 0:
        config_RLF[1] = 1
    if str_config.index('NonFlip') < 0:
        config_RLF[2] = 1
    joint_solutions = robot.SolveIK_All(pose_ref * pose_target * invH(pose_tool))
    nsol = joint_solutions.size(1)
    joints = False
    for i in range(0, nsol):
        ji = joint_solutions[0:7, i]
        ji_config = robot.JointsConfig(ji).tolist()
        if ji_config[0] == config_RLF[0] and ji_config[1] == config_RLF[1] and ji_config[2] == config_RLF[2]:
            joints = ji
            break
    if nsol <= 0:
        joints = [0, 0, 0, 0, 90, 0]
        print('WARNING! Target %s is not reachable!!' % name)
    elif joints is False:
        joints = [0, 0, 0, 0, 90, 0]
        print('Warning! it is not possible to match desired configuration for target %s' % name)
    return joints


# Load and display Targets from P_Var.CSV in RoboDK
def load_targets_station(strfile):
    poses, names, refnames, toolnames, configs = load_targets(strfile)
    jointlist = []
    program_name = getFileName(strfile)
    program = RDK.Item(program_name, ITEM_TYPE_PROGRAM)
    if program.Valid():
        program.Delete()
    program = RDK.AddProgram(program_name, robot)
    refname_active = 'unknown'
    toolname_active = 'unknown'

    for pose, name, refname, toolname, config_str in zip(poses, names, refnames, toolnames, configs):
        target = RDK.Item(name, ITEM_TYPE_TARGET)
        if target.Valid():
            target.Delete()
        frame = None
        tool = None
        frame = RDK.Item(refname, ITEM_TYPE_FRAME)
        if toolname == "TOOL0":
            tool = RDK.Item("TOOL0", ITEM_TYPE_TOOL)
            if not tool.Valid():
                tool = robot.AddTool(eye(4), "TOOL0")
        else:
            tool = RDK.Item(toolname, ITEM_TYPE_TOOL)

        if not frame.Valid():
            raise Exception("Reference %s for target %s not found" % (refname, name))
        if not tool.Valid():
            raise Exception("Tool %s for target %s not found" % (toolname, name))
        target = RDK.AddTarget(name, frame, robot)
        target.setPose(pose)
        joints = target_joints(pose, frame.Pose(), tool.PoseTool(), config_str, name)
        target.setJoints(joints)
        jointlist.append(joints)

        # Add instruction to program
        if refname_active != refname:
            refname_active = refname
            program.setFrame(frame)
            robot.setFrame(frame)
        if toolname_active != toolname:
            toolname_active = toolname
            program.setTool(tool)
            robot.setTool(tool)
        try:
            program.MoveJ(target)
        except:
            print('Warning: %s can not be reached. It will not be added to the program' % name)

    return poses, jointlist, names, refnames, toolnames, configs


##########################################
# This procedure shows how the filterim mechanism works behind the scenes
# This procedure is equivalent to FilterTarget() and does not need to be used
def FilterTarget(target, ref, tcp, japrox):
    """Target: pose of the TCP (tcp) with respect to the reference frame (ref)
    jnts_ref: preferred joints for inverse kinematics calculation"""
    # First: we need to calculate the accurate inverse kinematics to calculate the accurate joint data for the desired target
    # Note: SolveIK and SolveFK take the robot into account (from the robot base frame to the robot flange)
    robot.setAccuracyActive(True)
    pose_rob = ref * target * invH(tcp)
    robot_joints = robot.SolveIK(pose_rob, japrox)
    if len(robot_joints.tolist()) < 6:
        raise Exception("Target not reachable")
    # Second: Calculate the nominal forward kinematics as this is the calculation that the robot performs
    robot.setAccuracyActive(False)
    pose_rob_fixed = robot.SolveFK(robot_joints)
    target_filtered = invH(ref) * pose_rob_fixed * tcp
    return target_filtered


# -----------------------------------------------
# -----------------------------------------------
# -----------------------------------------------
# -----------------------------------------------
# Load selected file
if csv_file.endswith("Tool.csv"):
    load_tools_station(csv_file)

elif csv_file.endswith("Work.csv"):
    load_refs_station(csv_file)

else:
    # Load everything
    csv_file_tools = getFileDir(csv_file) + '/Tool.csv'
    csv_file_refs = getFileDir(csv_file) + '/Work.csv'
    load_tools_station(csv_file_tools)
    load_refs_station(csv_file_refs)

    poses, jointlist, names, refnames, toolnames, configs = load_targets_station(csv_file)

    do_filter = mbox('Do you want to filter the target file?', 'Yes', 'No')

    #do_filter = True
    if do_filter:
        print('Filtering targets...')

        # -------------------------
        # Read CSV data
        import csv
        import codecs
        csvdata = []
        show_warning = ''
        with codecs.open(csv_file, "r", codec) as fid:
            csvread = csv.reader(fid, delimiter=',', quotechar="^")
            for row in csvread:
                row_nums = [i for i in row]
                csvdata.append(row_nums)

        # -------------------------
        # Manipulate data
        i_target = 0
        for i in range(5, len(csvdata)):
            name = csvdata[i][8]
            if name == '""':
                break
            frame = RDK.Item(refnames[i_target], ITEM_TYPE_FRAME)
            tool = RDK.Item(toolnames[i_target], ITEM_TYPE_TOOL)
            try:
                #robot.setFrame(frame)
                #robot.setTool(tool)
                #pose_filtered = robot.FilterTarget(poses[i_target], jointlist[i_target])
                pose_filtered = FilterTarget(poses[i_target], frame.Pose(), tool.PoseTool(), jointlist[i_target])
                name = name.replace(' on ', '-F on ')
            except:
                msg = 'Warning! Can not filter target %i: %s' % (i_target, name)
                print(msg)
                show_warning = show_warning + msg + '<br>'
                pose_filtered = poses[i_target]

            x, y, z, w, p, r = Pose_2_Adept(pose_filtered)
            csvdata[i][1] = '%.5f' % x
            csvdata[i][2] = '%.5f' % y
            csvdata[i][3] = '%.5f' % z
            csvdata[i][4] = '%.5f' % w
            csvdata[i][5] = '%.5f' % p
            csvdata[i][6] = '%.5f' % r
            csvdata[i][8] = name
            i_target = i_target + 1

        # -------------------------
        # Write CSV data
        with codecs.open(csv_file[:-4] + '-F.CSV', 'wb', 'ISO-8859-1') as fid:
            writter = csv.writer(fid, delimiter=',', quotechar="^")
            for line in csvdata:
                writter.writerow(line)
        if len(show_warning) > 0:
            RDK.ShowMessage(show_warning)
