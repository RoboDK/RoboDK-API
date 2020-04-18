# This macro shows how we can take a group of laser tracker measurements
# from a laser tracker and save it to a file

# Start the RoboDK API
from robolink import *    
RDK = Robolink()

# Start the counter
tic()
count = 0

# Open a csv file in the same folder as the RDK file to store the data
with open(RDK.getParam('PATH_OPENSTATION') + '/tracker_point_test.csv', 'a') as csvfile:
    # Infinite loop until we decide to stop
    while True:
        count = count + 1
        # Take the measurement (make sure we are connected from the RoboDK API
        xyz = RDK.LaserTracker_Measure()
        if xyz is None:
            print("Unable to measure")
            continue
        
        x,y,z = xyz

        # Display the data as [time, x,y,z]
        data = '%.3f, %.6f, %.6f, %.6f' % (toc(), x, y, z)
        print(data)

        # Add the object as a point object
        #item = RDK.AddPoints([[x,y,z]])
        #item.setName('Point %i' % count)

        # Add the object as a reference (easier to copy/paste coordinates):
        #item = RDK.AddFrame('Point %i' % count)
        #item.setPose(transl(x,y,z))
        
        # Save the data to the file
        csvfile.write(data + '\n')

        # Take a break, if desired:
        #pause(1)
