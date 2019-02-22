# This macro shows how you can add a new camera from a simulation event
#
from robolink import *    # API to communicate with RoboDK
from robodk import *      # library for basic matrix operations
RDK = Robolink()

# Close any open 2D camera views
RDK.Cam2D_Close()

#camref = RDK.Item('Camera Reference',ITEM_TYPE_FRAME)
camref = RDK.ItemUserPick('Select the Camera location (reference, tool or object')

# set parameters in mm and degrees:
# FOV: Field of view in degrees (atan(0.5*height/distance) of the sensor
# FOCAL_LENGHT: focal lenght in mm
# FAR_LENGHT: maximum working distance (in mm)
# SIZE: size of the sensor in pixels
# BG_COLOR: background color (rgb color or named color: AARRGGBB)
# LIGHT_AMBIENT: ambient color (rgb color or named color: AARRGGBB)
# LIGHT_SPECULAR: specular color (rgb color or named color: AARRGGBB)
# LIGHT_DIFFUSE: diffuse color (rgb color or named color: AARRGGBB)
# DEPTH: Add this flag to create a 32 bit depth map


# cam_id = RDK.Cam2D_Add(camref, 'FOCAL_LENGHT=6 FOV=32 FAR_LENGHT=1000 SIZE=640x480 BG_COLOR=black')
# cam_id = RDK.Cam2D_Add(camref, 'FOCAL_LENGHT=6 FOV=32 FAR_LENGHT=1000 SIZE=640x480')
# cam_id = RDK.Cam2D_Add(camref, 'FOCAL_LENGHT=6 FOV=32 FAR_LENGHT=1000 SIZE=640x480 BG_COLOR=black LIGHT_AMBIENT=red LIGHT_DIFFUSE=#FF00FF00 LIGHT_SPECULAR=black')
# cam_id = RDK.Cam2D_Add(camref, 'FOCAL_LENGHT=6 FOV=32 FAR_LENGHT=1000 SIZE=640x480 DEPTH')
cam_id = RDK.Cam2D_Add(camref, 'FOCAL_LENGHT=6 FOV=32 FAR_LENGHT=600 SIZE=640x480 BG_COLOR=black LIGHT_AMBIENT=red LIGHT_DIFFUSE=black LIGHT_SPECULAR=white')


# cam_id = RDK.Cam2D_Add(camref, 'FOCAL_LENGHT=6 FOV=32 FAR_LENGHT=1000 SIZE=640x480 LIGHT_AMBIENT=red')

# Provoke a popup and allow the user to enter some parameters
# cam_id = RDK.Cam2D_Add(camref, 'POPUP')

# Example to take a snapshot from the camera
# RDK.Cam2D_Snapshot(RDK.getParam('PATH_OPENSTATION') + "/sample_image.png", cam_id)
