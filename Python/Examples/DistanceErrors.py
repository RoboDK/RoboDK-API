# This macro shows an example to customize the validation of distance measurements after robot calibration
# More information about the RoboDK API here:
# https://robodk.com/doc/en/RoboDK-API.html
# For more information visit:
# https://robodk.com/doc/en/PythonAPI/robolink.html

from robolink import *    # API to communicate with RoboDK
from robodk import *      # basic matrix operations

# Start RoboDK API
RDK = Robolink()

# Select the robot
robot = RDK.ItemUserPick('Select a robot', ITEM_TYPE_ROBOT)

# Use the CSV file exported after validation measurements are completed
VALID_FILE = 'validation-80-full-workspace.csv'
csvdata = LoadList(RDK.getParam('PATH_OPENSTATION') + '/' + VALID_FILE)

# Retrieve the TCP
xyzwpr_tcp = csvdata[1][12:18]
x,y,z,w,p,r = xyzwpr_tcp
#[-135.22663, -53.15329,  71.31105,  -3.13948*180.0/pi,   0.00114*180.0/pi,  -1.15271*180.0/pi]
xyzwpr_tcp = [x,y,z,w*180.0/pi,p*180.0/pi,r*180.0/pi]
htcp = UR_2_Pose(xyzwpr_tcp)

# Iterate between consecutive points and check distances
print('p1\tp2\terror nominal\terror accurate')
num_points = len(csvdata)-1
for i in range(1,num_points):

    # TCP point i measured by the tracker
    pi_ref = csvdata[i][6:9]

    # Joints for point i
    ji = csvdata[i][0:6]

    # Calculate TCP using nominal kinematics (pi_nom)
    robot.setAccuracyActive(False)
    hi_nom = robot.SolveFK(ji)*htcp
    pi_nom = hi_nom.Pos()

    # Calculate TCP using accurate kinematics (pi_acc)
    robot.setAccuracyActive(True)
    hi_acc = robot.SolveFK(ji)*htcp
    pi_acc = hi_acc.Pos()

    for j in range(i+1, i+2):#,numdata+1):

        # Same calculation for point j
        pj_ref = csvdata[j][6:9]
        
        jj = csvdata[j][0:6]
        
        robot.setAccuracyActive(False)
        hj_nom = robot.SolveFK(jj)*htcp
        pj_nom = hj_nom.Pos()
        robot.setAccuracyActive(True)
        hj_acc = robot.SolveFK(jj)*htcp
        pj_acc = hj_acc.Pos()

        # Calculate the distances seen by the tracker, by the nominal kinematics and by the accurate kinematics:
        dist_ref = distance(pi_ref, pj_ref)
        dist_nom = distance(pi_nom, pj_nom)
        dist_acc = distance(pi_acc, pj_acc)

        # Calculate the robot errors compared to the tracker errors
        error_nom = abs(dist_nom - dist_ref)
        error_acc = abs(dist_acc - dist_ref)

        # Display the data
        print('%i\t%i\t%.3f\t%.3f' % (i,j,error_nom, error_acc))
  
        
