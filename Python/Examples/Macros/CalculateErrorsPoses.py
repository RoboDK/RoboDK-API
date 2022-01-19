# This macro shows an example to implement the validation of distance measurements after robot calibration including orientation errors
# Update CSV_FILE variable to the appropriate CSV file with the measurement data.
#
# More information about the RoboDK API here:
# https://robodk.com/doc/en/RoboDK-API.html
# For more information visit:
# https://robodk.com/doc/en/PythonAPI/robolink.html

from robolink import *  # API to communicate with RoboDK
from robodk import *  # basic matrix operations

# Start RoboDK API
RDK = Robolink()

# Select the robot
robot = RDK.ItemUserPick('Select a robot', ITEM_TYPE_ROBOT)

# Use the CSV file exported after validation measurements are completed
CSV_FILE = 'Measurements Validation.csv'
csvdata = LoadList(RDK.getParam('PATH_OPENSTATION') + '/' + CSV_FILE)

# Retrieve the TCP (for 6DOF measurements it should be the same TCP that applies to all measurements)
xyzwpr_tcp = csvdata[1][12:18]
#x,y,z,w,p,r = xyzwpr_tcp  #[-135.22663, -53.15329,  71.31105,  -3.13948*180.0/pi,   0.00114*180.0/pi,  -1.15271*180.0/pi]
#xyzwpr_tcp = [x,y,z,w,p,r]

htcp = TxyzRxyz_2_Pose(xyzwpr_tcp)

# Force to shift the TCP a specific value. For example, to check accuracy at the origin of the tool.
shift_tcp = invH(htcp)
#shift_tcp = eye(4)

htcp = htcp * shift_tcp

RDK.Render(False)

# Iterate between consecutive points and check distances
print('p1\tp2\tposition error nominal (mm)\tposition error accurate (mm)\tangle error nominal (deg)\tangle error accurate (deg)')
num_points = len(csvdata) - 1
for i in range(1, num_points):
    # TCP pose (i) measured by the tracker
    hi_ref = TxyzRxyz_2_Pose(csvdata[i][6:12]) * shift_tcp

    # Robot joints for point i
    ji = csvdata[i][0:6]

    # Calculate the pose (homogeneous matrix) of the TCP using nominal kinematics (hi_nom)
    robot.setAccuracyActive(False)
    hi_nom = robot.SolveFK(ji) * htcp

    # Calculate TCP using accurate kinematics (hi_acc)
    robot.setAccuracyActive(True)
    hi_acc = robot.SolveFK(ji) * htcp

    # Iterate through pairs of points
    for j in range(i + 1, num_points + 1):
        # Same pose calculations for pose j
        hj_ref = TxyzRxyz_2_Pose(csvdata[j][6:12]) * shift_tcp
        jj = csvdata[j][0:6]
        robot.setAccuracyActive(False)
        hj_nom = robot.SolveFK(jj) * htcp
        robot.setAccuracyActive(True)
        hj_acc = robot.SolveFK(jj) * htcp

        # Calculate the distances seen by the tracker, by the nominal kinematics and by the accurate kinematics:
        d_ref = norm(subs3(hi_ref.Pos(), hj_ref.Pos()))
        d_nom = norm(subs3(hi_nom.Pos(), hj_nom.Pos()))
        d_acc = norm(subs3(hi_acc.Pos(), hj_acc.Pos()))

        # Calculate distance errors
        dist_error_nom = abs(d_nom - d_ref)
        dist_error_acc = abs(d_acc - d_ref)

        if dist_error_nom > 20:
            # This is an ivalid measurement, skip.
            continue

        # Calculate the pose shifts (to calculate orientation errors)
        Href = invH(hi_ref) * hj_ref
        Hnom = invH(hi_nom) * hj_nom
        Hacc = invH(hi_acc) * hj_acc

        # Calculate angle errors
        Hnom_error = invH(Href) * Hnom
        Hacc_error = invH(Href) * Hacc
        ang_error_nom = pose_angle(Hnom_error) * 180.0 / pi
        ang_error_acc = pose_angle(Hacc_error) * 180.0 / pi

        # Display the data
        print('%i\t%i\t%.3f\t%.3f\t%.3f\t%.3f' % (i, j, dist_error_nom, dist_error_acc, ang_error_nom, ang_error_acc))
