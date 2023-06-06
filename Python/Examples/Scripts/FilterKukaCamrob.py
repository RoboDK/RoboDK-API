from robodk import robolink, robomath, robodialogs, robofileio
import os

csv_path = robodialogs.getOpenFileName(defaultextension='.csv')
if not csv_path:
    quit()

RDK = robolink.Robolink()

robot = RDK.ItemUserPick('Select robot arm', robolink.ITEM_TYPE_ROBOT_ARM)

# IMPORTANT!
# You need to edit this according to your setup.
# The TOOL currently active in RoboDK while running this script must be the same as the active tool in the CSV.
# The reference FRAME currently active in RoboDK while running this script must be the same as the active tool in the CSV.
joints = robot.JointsHome().tolist()  # reference joints, this is the configuration used to filter the targets
robot.setPoseTool(robot.PoseTool())  # find the current active tool in your source program, as it must be THE SAME in RoboDK!
robot.setPoseFrame(robot.PoseFrame())  # find the current active reference frame in your source program, as it must be THE SAME in RoboDK!

rows = []

for i, row in enumerate(robofileio.LoadList(csv_path, ';')):
    if not row:
        continue

    xyzwpr = row[1:7]
    speed = row[8]
    tool_id = int(row[13])
    e01 = row[14]
    e02 = row[15]

    # Assuming you have two synchronize axes
    if len(joints) > 6:
        joints[6] = e01

    if len(joints) > 7:
        joints[7] = e02

    pose = robomath.KUKA_2_Pose(xyzwpr)

    # Preview the pose to ensure everything is OK
    # Comment to save time
    robot.setJoints(joints)
    robot.setPose(pose)

    try:
        pose_filtered, joints_filtered = robot.FilterTarget(pose)#, joints)

        # Modify current row with filtered data
        # Ensure we follow expected format
        row[1:7] = robomath.Pose_2_KUKA(pose_filtered)
        if len(joints) > 6:
            row[14] = joints_filtered.tolist()[6]
        if len(joints) > 7:
            row[15] = joints_filtered.tolist()[7]
    except:
        print('Unable to reach point. Ensure your frame and tool are properly defined.')
        print(xyzwpr)

    rows.append(row)

# Save to CSV
csv_out_path = robodialogs.getSaveFileName(os.path.dirname(csv_path), os.path.basename(csv_path), defaultextension='.csv')
if not csv_out_path:
    quit()

with open(csv_out_path, 'w') as fo:
    for r in rows:
        newline = '%i;%.4f;%.4f;%.4f;%.4f;%.4f;%.4f;%i;%.7f;%i;%i;%i;%i;%i;%.4f;%.4f;%i;%i;%i;%i;%i;\n' % (r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10], r[11], r[12], r[13], r[14], r[15], r[16], r[17], r[18], r[19], r[20])
        fo.write(newline)

print('Done')