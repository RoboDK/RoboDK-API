# Type help("robolink") or help("robodk") for more information
# Press F5 to run the script
# Note: you do not need to keep a copy of this file, your python script is saved with the station
# More information about the RoboDK API here:
# https://robodk.com/doc/en/RoboDK-API.html
from robolink import *  # API to communicate with RoboDK
from robodk import *  # basic matrix operations

RDK = Robolink()

# Close any open 2D camera views
RDK.Cam2D_Close()

camref = RDK.Item('Camera Reference', ITEM_TYPE_FRAME)

# set parameters in mm and degrees:
# FOV: Field of view in degrees (atan(0.5*height/distance) of the sensor divided by
# FOCAL_LENGHT: focal lenght in mm
# FAR_LENGHT: maximum working distance (in mm)
# SIZE: size of the sensor in pixels
# DEPTH: Tag as depth to show the depth image in grey
# BG_COLOR: background color (rgb color or named color: AARRGGBB)
# LIGHT_AMBIENT: ambient color (rgb color or named color: AARRGGBB)
# LIGHT_SPECULAR: specular color (rgb color or named color: AARRGGBB)
# LIGHT_DIFFUSE: diffuse color (rgb color or named color: AARRGGBB)

# cam_id = RDK.Cam2D_Add(camref, 'FOCAL_LENGHT=6 FOV=32 FAR_LENGHT=1000 SIZE=640x480 BG_COLOR=black')
# cam_id = RDK.Cam2D_Add(camref, 'FOCAL_LENGHT=6 FOV=32 FAR_LENGHT=1000 SIZE=640x480')
# cam_id = RDK.Cam2D_Add(camref, 'FOCAL_LENGHT=6 FOV=32 FAR_LENGHT=1000 SIZE=640x480 BG_COLOR=black LIGHT_AMBIENT=red LIGHT_DIFFUSE=#FF00FF00 LIGHT_SPECULAR=black')
#cam_id = RDK.Cam2D_Add(camref, 'FOCAL_LENGHT=6 FOV=32 FAR_LENGHT=1000 SIZE=640x480 DEPTH')
cam_id = RDK.Cam2D_Add(camref, 'FOCAL_LENGHT=6 FOV=32 FAR_LENGHT=1000 SIZE=640x480 BG_COLOR=black LIGHT_AMBIENT=red LIGHT_DIFFUSE=black LIGHT_SPECULAR=white')

# cam_id = RDK.Cam2D_Add(camref, 'FOCAL_LENGHT=6 FOV=32 FAR_LENGHT=1000 SIZE=640x480 LIGHT_AMBIENT=red')

# cam_id = RDK.Cam2D_Add(camref, 'POPUP')

# RDK.Cam2D_Snapshot(RDK.getParam('PATH_OPENSTATION') + "/sample_image.png", cam_id)
