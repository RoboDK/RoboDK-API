# This macro shows how we can take a group of laser tracker measurements
# from a laser tracker and save it to a file

CREATE_MEASUREMENTS = False

# Set the name of the reference frame to add measurements attached to id
REFERENCE_NAME = "Tracker Reference"
#REFERENCE_NAME = None

MEASUREMENT_RATE_S = 50

MEASUREMENT_PAUSE_S = 1/MEASUREMENT_RATE_S

# Start the RoboDK API
from robolink import *    
from robodk import *
RDK = Robolink()

# Get the reference frame if available
if REFERENCE_NAME is None:
    reference = None
else:
    reference = RDK.Item(REFERENCE_NAME, ITEM_TYPE_FRAME)
    if not reference.Valid():
        #reference = None
        reference = RDK.AddFrame(REFERENCE_NAME)

# Start the counter
tic()
count = 0

path_file = RDK.getParam('PATH_OPENSTATION') or RDK.getParam('PATH_DESKTOP')

is_lasertracker = True

# Open a csv file in the same folder as the RDK file to store the data
with open(path_file + '/tracker_point_test.csv', 'w') as csvfile:
    # Infinite loop until we decide to stop
    while True:
        count = count + 1
        
        data = "Invalid measurement"
        measurement = None
        
        if is_lasertracker:
            measurement = RDK.LaserTracker_Measure()
        
        if measurement is not None:
            # Block rendering (faster)
            RDK.Render(False)

            if len(measurement) >= 6:
                # We have a pose measurement (eg Leica 6 DOF T-Mac)
                x, y, z, w, p, r = measurement
                data = '%.3f, %.6f, %.6f, %.6f, %.6f, %.6f, %.6f' % (toc(), x, y, z, w, p, r)
                RDK.ShowMessage("Measured XYZWPR: " + data, False)

                # Convert position and orientation Euler angles to poses (rot functions are in radians)
                pose_tool_wrt_tracker = transl(x,y,z) * rotx(w*pi/180) * roty(p*pi/180) * rotz(r*pi/180)

                # Add the object as a reference (easier to copy/paste coordinates):
                if CREATE_MEASUREMENTS:
                    item = RDK.AddFrame('Pose %i' % count)
                    item.setPose(pose_tool_wrt_tracker)

                    # Set the reference relative to the tracker reference if available
                    if reference is not None:
                        item.setParent(reference)
                            
            else:
                # We have an XYZ tracker measurement
                x,y,z = measurement

                # Display the data as [time, x,y,z]
                data = '%.3f, %.6f, %.6f, %.6f' % (toc(), x, y, z)
                RDK.ShowMessage("Measured XYZ: " + data, False)

                # Add the object as a point object
                #item = RDK.AddPoints([[x,y,z]])
                #item.setName('Point %i' % count)

                # Add the object as a reference (easier to copy/paste coordinates):
                #item = RDK.AddFrame('Point %i' % count)
                #item.setPose(transl(x,y,z))

                #if reference is not None:
                #    item.setParent(reference)  
                                
        else:
            # Stop trying to use the laser tracker
            is_lasertracker = False
            #RDK.ShowMessage("Unable to measure with a laser tracker. Trying with pose input", False)
            #pause(2)
            #continue
            
            # Take the measurement (make sure we are connected from the RoboDK API
            pose1, pose2, np1, np2, time, aux = RDK.StereoCamera_Measure()
            if np1 == 0:
                print("Unable to see the tracker")
            
            else:
                #print(pose1)
                #print(pose2)
                station_2_tracker = pose1
                
                if reference is not None:
                    reference.setPoseAbs(station_2_tracker)
                
                x,y,z,a,b,c = Pose_2_KUKA(station_2_tracker)
                data = '%.3f, %.6f, %.6f, %.6f, %.6f, %.6f, %.6f' % (toc(), x, y, z, a, b, c)
            
        # Save the data to the CSV file
        print(data)
        csvfile.write(data + '\n')

        # Set default rendering back
        RDK.Render(True)

        # Take a break, if desired:
        pause(MEASUREMENT_PAUSE_S)
