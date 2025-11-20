# This example shows how to create and update a custom mechanism built from an array of objects using one API call
# You can quickly update an array of objects in one shot without penalizing simulation performance
import time
import math
from robodk import *    # RoboDK API
from robolink import *    # Robot toolbox

# Start the RoboDK API
RDK = Robolink()

# Number of elements
x_count = 20
y_count = 20

# Spacing between elements
x_spacing = 40
y_spacing = 40

# Length along X axis
x_lenth = x_count * x_spacing

# Retrieve the reference box (100x100x100 mm, centered)
box_ref = RDK.Item("Reference Box", ITEM_TYPE_OBJECT)

# Delete the previous array
frame_old = RDK.Item("Mechanism Array", ITEM_TYPE_FRAME)
if frame_old.Valid():
    frame_old.Delete()

# Frame to place the mechanism
frame_ref = RDK.AddFrame("Mechanism Array")

# Show as collapsed (less cluttered tree, faster rendering)
frame_ref.setParam("Tree", "Collapse")

# Create the array of objects based on the model object
RDK.Render(False)
box_ref.Copy()
# Create the objects and scale them
obj_array = RDK.Paste(frame_ref, x_count * y_count)
idx = 0
for i in range(x_count):
    for j in range(y_count):
        obj_array[idx].Scale([0.05, 0.05, 2])
        obj_array[idx].setName("piston " + str(idx))
        obj_array[idx].setVisible(True)
        idx = idx + 1

RDK.Render(True)

# Random function to calculate a Z position based on X,Y and time
def z_func(x,y, t):
    """x and y are the coordinates on X and Y of the parent frame, in mm. t is time in seconds."""
    z = 100 * math.sin(2 * math.pi * math.sqrt(x*x + y*y) * (1/x_lenth)  + t/6 )
    return z

def update_mechanism(t):
    """Update the mechanism for the time t in seconds"""
    obj_poses = []
    for i in range(x_count):
        x = i*x_spacing
        for j in range(y_count):            
            y = j*y_spacing
            z = z_func(x, y, t)
            pose = robomath.transl(x,y,z)
            obj_poses.append(pose)

    RDK.setPoses(obj_array, obj_poses)

# Infinite loop to update the mechanism
while True:
    # Retrieve RoboDK simulation time:
    t = RDK.SimulationTime()

    # Update the mechanism
    print("Updating mechanism at time frame: " + str(t))
    update_mechanism(t)

    # Wait a bit before running the next frame
    time.sleep(0.05)

