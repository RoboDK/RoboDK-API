# This is an example to add geometry to a RoboDK station or a robot given triangle vertices
# Vertex normals can also be added

# Two triangles with normals:
# SHAPE = [[0,-50,0,0,0,1],[0,500,0,0,0,1],[500,0,0,0,0,1],[0,0,100,0,0,1],[500,0,100,0,0,1],[0,500,100,0,0,1]]
#
# More information about the RoboDK API here:
# https://robodk.com/doc/en/RoboDK-API.html

# Octahedron vertices 
A = [ 0.17770898,  0.72315927,  0.66742804]
B = [-0.65327074, -0.4196453 ,  0.63018661]
C = [ 0.65382635,  0.42081934, -0.62882604]
D = [-0.17907021, -0.72084723, -0.66956189]
E = [-0.73452809,  0.5495376 , -0.39809158]
F = [ 0.73451554, -0.55094017,  0.39617148]

# Octadron faces by groups of vertices
SHAPE = [E, B, A,
        E, D, B,
        E, C, D,
        E, A, C,
        F, A, B,
        F, B, D,
        F, D, C,
        F, C, A,
]

##### Add the shape as an object in RoboDK
from robolink import *    # API to communicate with RoboDK
from robodk import *      # basic matrix operations
RDK = Robolink() # Initialize the RoboDK API
new_object = RDK.AddShape(SHAPE)
new_object.Scale(500) # scale by a factor of 500

##### Alternatively, we could also do:
#old_object = RDK.Item('',ITEM_TYPE_OBJECT)
#new_object = RDK.AddShape(OCTO, old_object)
#or
#old_object.AddShape(OCTO)

# Add the shape to a robot link
robot = RDK.ItemUserPick('Select a robot to add geometry', ITEM_TYPE_ROBOT)
if not robot.Valid():
    raise Exception('No robot selected. Add a robot to attach this geometry to a link')
value = mbox('Enter the joint to attach an object',entry='3')
link_id = int(value)
link = robot.ObjectLink(link_id)
link.AddShape(tr(Mat(SHAPE))*200)# scale vertices with a factor of 100


