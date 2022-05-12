# This macro shows how you can add a new camera from a simulation event
#
from robodk.robolink import *  # API to communicate with RoboDK

RDK = Robolink()

# Close any open 2D camera views
RDK.Cam2D_Close()

camref = RDK.ItemUserPick('Select the Camera location (reference, tool or object)')
#camref = RDK.Item('Frame 7',ITEM_TYPE_FRAME)

# Set parameters in mm and degrees:
# (more information here: https://robodk.com/doc/en/PythonAPI/robodk.html#robodk.robolink.Robolink.Cam2D_Snapshot)
#
#  FOV: Field of view in degrees (atan(0.5*height/distance) of the sensor
#  FOCAL_LENGTH: focal length in mm
#  FAR_LENGTH: maximum working distance (in mm)
#  SIZE: size of the window in pixels (fixed) (width x height)
#  SNAPSHOT: size of the snapshot image in pixels (width x height)
#  BG_COLOR: background color (rgb color or named color: AARRGGBB)
#  LIGHT_AMBIENT: ambient color (rgb color or named color: AARRGGBB)
#  LIGHT_SPECULAR: specular color (rgb color or named color: AARRGGBB)
#  LIGHT_DIFFUSE: diffuse color (rgb color or named color: AARRGGBB)
#  DEPTH: Add this flag to create a 32 bit depth map (white=close, black=far)
#  NO_TASKBAR: Don't add the window to the task bar
#  MINIMIZED: Show the window minimized
#  ALWAYS_VISIBLE: Keep the window on top of all other windows
#  SHADER_VERTEX: File to a vertex shader (GLSL file)
#  SHADER_FRAGMENT: File to a fragment shader (GLSL file)

# Examples to call Camd2D_Add:

# Camera without a fixed window size and 1000 mm length
cam_id = RDK.Cam2D_Add(camref, 'FOCAL_LENGTH=6 FOV=32 FAR_LENGTH=1000')

# Stop script execution
quit()

# Camera with a fixed window size and 1000 mm length
cam_id = RDK.Cam2D_Add(camref, 'FOCAL_LENGTH=6 FOV=32 FAR_LENGTH=1000 SIZE=640x480')

# Camera with a black background
cam_id = RDK.Cam2D_Add(camref, 'FOCAL_LENGTH=6 FOV=32 FAR_LENGTH=1000 SIZE=640x480 BG_COLOR=black')

# Camera without a fixed window size and high resolution snapshot
cam_id = RDK.Cam2D_Add(camref, 'FOCAL_LENGTH=6 FOV=32 FAR_LENGTH=1000 SIZE=640x480')

# Depth view: 32 bit depth map (white=close, black=far)
cam_id = RDK.Cam2D_Add(camref, 'FOCAL_LENGTH=6 FOV=32 FAR_LENGTH=1000 SIZE=640x480 DEPTH')

# Minimized camera
cam_id = RDK.Cam2D_Add(camref, 'FOCAL_LENGTH=6 FOV=32 FAR_LENGTH=1000 SIZE=640x480 MINIMIZED')

# Do not show the camera window in the taskbar
cam_id = RDK.Cam2D_Add(camref, 'FOCAL_LENGTH=6 FOV=32 FAR_LENGTH=1000 SIZE=640x480 NO_TASKBAR')

# Customize the light
cam_id = RDK.Cam2D_Add(camref, 'FOCAL_LENGTH=6 FOV=32 FAR_LENGTH=1000 SIZE=640x480 BG_COLOR=black LIGHT_AMBIENT=red LIGHT_DIFFUSE=#FF00FF00 LIGHT_SPECULAR=black')
cam_id = RDK.Cam2D_Add(camref, 'FOCAL_LENGTH=6 FOV=32 FAR_LENGTH=600 SIZE=640x480 BG_COLOR=black LIGHT_AMBIENT=red LIGHT_DIFFUSE=black LIGHT_SPECULAR=white')
cam_id = RDK.Cam2D_Add(camref, 'FOCAL_LENGTH=6 FOV=32 FAR_LENGTH=1000 SIZE=640x480 LIGHT_AMBIENT=red')

# Provoke a popup and allow the user to enter some parameters
cam_id = RDK.Cam2D_Add(camref, 'POPUP')

# Example to take a snapshot from the camera
RDK.Cam2D_Snapshot(RDK.getParam('PATH_OPENSTATION') + "/sample_image.png", cam_id)

# Special command to retrieve the window ID:
win_id = RDK.Command("CamWinID", str(cam_id))
print(str(win_id))

#-----------------------------------------------------------------------------------
# Example to use a customized shader to customize the effect of light
# Tip: Use the example: C:/RoboDK/Library/Example-Shader-Customized-Light.rdk
# Tip: If you need a fixed light source update the variable light_Position in the shader_fragment.glsl file

# Get the path to the RoboDK library (usually in C:/RoboDK/Library/)
path_library = RDK.getParam("PATH_LIBRARY")
file_shader_fragment = path_library + '/Macros/Camera-Shaders/shader_fragment.glsl'
file_shader_vertex = path_library + '/Macros/Camera-Shaders/shader_vertex.glsl'
cam_id = RDK.Cam2D_Add(camref, 'FOCAL_LENGTH=6 FOV=32 FAR_LENGTH=2500 SHADER_FRAGMENT=' + file_shader_fragment + ' SHADER_VERTEX=' + file_shader_vertex)
