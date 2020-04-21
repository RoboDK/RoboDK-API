# This macro allows a user to teach a reference frame using a laser tracker
# The macro guides the used to take 3 measurements (X, X+ and Y+)
# Important: The robot needs to be calibrated first to accurately measure the reference frame
from robolink import *    # API to communicate with RoboDK
from robodk import *      # basic matrix operations
RDK = Robolink()

# Manually enter the target compensation
COMPENSATION_X = 0 # -1.5*25.4/2.0
COMPENSATION_Y = 0 # -1.5*25.4/2.0
COMPENSATION_Z = 0 # -1.5*25.4/2.0

# Measurements reference:
REFERENCE_MEASUREMENTS = "Measurements Reference"

#p1 = [10,10,1]
#p2 = [100, 12, 1]
#p3 = [0, 100, 1]


#COMPENSATION = transl(-1.5*25.4/2.0, -1.5*25.4/2.0, 0)
POSE_COMPENSATION = transl(COMPENSATION_X, COMPENSATION_Y, COMPENSATION_Z)

# Select the robot
robot = RDK.ItemUserPick('Select a robot', ITEM_TYPE_ROBOT)
if not robot.Valid():
    raise Exception("Robot not selected or available")

print("Using robot %s" % robot.Name())

# Select the reference frame to calibrate
frame = RDK.ItemUserPick("Select a reference frame to calibrate", ITEM_TYPE_FRAME)
if not frame.Valid():
    raise Exception("Reference frame not selected or available")
    
print("Calibrating reference frame %s" % frame.Name())

# Select the robot base frame automatically from the robot item
robot_base = robot.Parent()
if not frame.Parent().equals(robot_base):
    raise Exception("The selected reference frame to calibrate (%s) must be directly attached to the robot" % frame.Name())
    
# Select the measurements reference:
ref_measurements = RDK.Item(REFERENCE_MEASUREMENTS, ITEM_TYPE_FRAME)
if not ref_measurements.Valid():
    ref_measurements = RDK.ItemUserPick("Select the measurements reference", ITEM_TYPE_FRAME)
    if not ref_measurements.Valid():
        raise Exception("The measurements reference is not selected or available")

if ref_measurements.equals(frame):
    raise Exception("The measurement reference can not calibrate itself! Select another reference to calibrate")
        
# Retrieve the transformation from the robot base to the measurements reference
#params = RDK.SignatureRobot(robot)
#Hbase2measref = invH(params[0])
Hbase2measref = invH(robot_base.PoseAbs())*ref_measurements.PoseAbs()

# Measure the first point:
answer = mbox('Measure point on X and select OK')
if not answer:
    print('Operation cancelled')
    quit()
    
p1 = RDK.LaserTracker_Measure()
while p1 is None:
    if not mbox("The laser tracker is not ready. Select OK to try again."):
        quit()
        
    p1 = RDK.LaserTracker_Measure()
    #raise Exception('The laser tracker is not ready')

print("p1= %s" % str(p1))

# Measure the second point:    
answer = mbox('Measure point on X+ and select OK')
if not answer:
    print('Operation cancelled')
    quit()
p2 = RDK.LaserTracker_Measure()
while p2 is None:
    if not mbox("The laser tracker is not ready. Select OK to try again."):
        quit()
        
    p2 = RDK.LaserTracker_Measure()
    #raise Exception('The laser tracker is not ready')
    
print("p2= %s" % str(p2))

# Measure the third point:    
answer = mbox('Measure point on Y+ and select OK')
if not answer:
    print('Operation cancelled')
    quit()
p3 = RDK.LaserTracker_Measure()
while p3 is None:
    if not mbox("The laser tracker is not ready. Select OK to try again."):
        quit()
        
    p3 = RDK.LaserTracker_Measure()
    #raise Exception('The laser tracker is not ready')

print("p3= %s" % str(p3))

# Calculate the reference frame
pose_p123 = RDK.CalibrateReference([p1,p2,p3])
pose_frame = Hbase2measref * pose_p123 * POSE_COMPENSATION
pose_frame_old = frame.Pose()

mm_error = distance(pose_frame.Pos(), pose_frame_old.Pos())
angle_error = pose_angle_between(pose_frame, pose_frame_old)*180.0/pi

msg = 'Teaching reference %s\n' % frame.Name()
msg += 'Found errors: %.3f mm , %.3f deg\n' % (mm_error, angle_error)
msg += 'Using compensation: [%.3f, %.3f, %.3f] mm\n' % (COMPENSATION_X, COMPENSATION_Y, COMPENSATION_Z)
msg += '\nOld value: %s\n' % (str(Pose_2_Fanuc(pose_frame_old)))
msg += '\nNew value: %s\n' % (str(Pose_2_Fanuc(pose_frame)))
msg += '\nUpdate reference?'

print(msg)

isok = mbox(msg)

if not isok:
    print("Reference frame update cancelled")
    quit()
    #raise Exception("Operation cancelled by user")

frame.setPose(pose_frame)


