# This script generates a chart of the simulated joints calculating joint speeds and accelerations
# Tip: Use the script JointsPlayback.py to move along the recorded joints

from robodk.robolink import *    # API to communicate with RoboDK
from time import gmtime, strftime, time

# Simulation ratio: lower is more accurate
SimulationSpeed = 0.05  # A program that takes 5 seconds in real time, will be SimulationSpeed times faster in simulation (or slower if < 1)

# Sampling time: how often we want a new entry
SampleTime = 0.05

# To get better results:
# Select tools-Options-Motion
# Set Maximum path step (mm) to 0.01
# Set Maximum path step (deg) to 0.01

# Start RoboDK API
RDK = Robolink()

t_ratio = 1 / SimulationSpeed
RDK.setSimulationSpeed(SimulationSpeed)

# Ask the user to select a robot arm (mechanisms are ignored)
prog = RDK.ItemUserPick('Select a program', ITEM_TYPE_PROGRAM)
if not prog.Valid():
    raise Exception("Robot is not available")

robot = prog.getLink(ITEM_TYPE_ROBOT)
ndofs = len(robot.Joints().list())

# Generate a file in the same folder where we have the RDK file
file_path = RDK.getParam('PATH_OPENSTATION') + '/joints-' + prog.Name() + '.csv'


def joints_changed(j1, j2, tolerance=0.0001):
    """Returns True if joints 1 and joints 2 are different"""
    if j1 is None or j2 is None:
        return True

    for j1, j2 in zip(j1, j2):
        if abs(j1 - j2) > tolerance:
            return True

    return False


def diff(j1, j2, dt, dofs):
    """Returns True if joints 1 and joints 2 are different"""
    if j2 is None or dt <= 0:
        return [0] * dofs

    res = []
    for j1, j2 in zip(j1, j2):
        res.append((j1 - j2) / dt)

    return res


# Infinite loop to record robot joints
print("Recording robot joints to file: " + file_path)
with open(file_path, 'w') as fid:
    joints_header = ",".join(["Joint " + str(i + 1) for i in range(ndofs)])
    speeds_header = ",".join(["Speed " + str(i + 1) for i in range(ndofs)])
    accel_header = ",".join(["Accel " + str(i + 1) for i in range(ndofs)])
    fid.write("Time (s)," + joints_header + ",,Time (s)," + speeds_header + ",,Time (s)," + accel_header)
    fid.write("\n")
    joints_last = None
    speeds_last = None
    t_last = None
    t_start = None

    RDK.Render(True)
    prog.RunProgram()
    while prog.Busy():
        #t_now = time() # Estimate using t_ratio
        #t_now = float(RDK.Command("SimulationTime"))*0.001

        t_now = float(RDK.Command("TrajectoryTime"))  # RoboDK's internal clock for motion simulation
        joints = robot.Joints().list()
        if joints_changed(joints, joints_last):
            if t_last is None:
                t_last = t_now
                t_start = t_now

            # Calculate timings
            #t_sim = t_ratio * (t_now - t_start) # not needed if we use RoboDK's SimulationTime
            #t_delta = t_ratio * (t_now - t_last) # not needed if we use RoboDK's SimulationTime
            t_sim = t_now - t_start
            t_delta = t_now - t_last
            if t_delta < SampleTime:
                # Minimum 5 ms time for good accuracy
                continue

            # Calculate speeds
            speeds = diff(joints, joints_last, t_delta, ndofs)

            # Calcualte accelerations
            accels = diff(speeds, speeds_last, t_delta, ndofs)

            print('Time +S: %.3f s' % t_sim)
            joints_str = ",".join(["%.6f" % x for x in joints])
            speeds_str = ",".join(["%.6f" % x for x in speeds])
            accels_str = ",".join(["%.6f" % x for x in accels])

            time_str = ("%.6f," % t_sim)
            fid.write(time_str + joints_str + ",," + time_str + speeds_str + ",," + time_str + accels_str)
            fid.write("\n")
            t_last = t_now
            joints_last = joints
            speeds_last = speeds
            #pause(0.005)
