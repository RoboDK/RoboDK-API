# Type help("robodk.robolink") or help("robodk.robomath") for more information
# Press F5 to run the script
# Documentation: https://robodk.com/doc/en/RoboDK-API.html
# Reference:     https://robodk.com/doc/en/PythonAPI/index.html
#
# This example demonstrates some of the basic functionalities to handle 2D cameras using the RoboDK API for Python.
# It creates/reuses an existing camera, set its parameters, get the image using two different methods and display it to the user as a live stream.
# This is a great starting point for your computer vision algorithms.
#

from robodk import robolink  # RoboDK API
from robodk import robomath  # Robot toolbox
RDK = robolink.Robolink()

# OpenCV is an open source Computer Vision toolkit, which you can use to filter and analyse images
robolink.import_install('cv2', 'opencv-python', RDK)
robolink.import_install('numpy', RDK)
import numpy as np
import cv2 as cv

CAM_NAME = 'My Camera'
CAM_PARAMS = 'SIZE=640x480' # For more options, see https://robodk.com/doc/en/PythonAPI/robodk.html#robodk.robolink.Robolink.Cam2D_Add
WINDOW_NAME = 'My Camera Feed'

#----------------------------------
# Get the camera item
cam_item = RDK.Item(CAM_NAME, robolink.ITEM_TYPE_CAMERA)
if not cam_item.Valid():
    cam_item = RDK.Cam2D_Add(RDK.AddFrame(CAM_NAME + ' Frame'), CAM_PARAMS)
    cam_item.setName(CAM_NAME)
cam_item.setParam('Open', 1)

#----------------------------------
# Create a live feed
while cam_item.setParam('isOpen') == '1':

    #----------------------------------
    # Method 1: Get the camera image, by socket
    img_socket = None
    bytes_img = RDK.Cam2D_Snapshot('', cam_item)
    if isinstance(bytes_img, bytes) and bytes_img != b'':
        nparr = np.frombuffer(bytes_img, np.uint8)
        img_socket = cv.imdecode(nparr, cv.IMREAD_COLOR)
    if img_socket is None:
        break

    #----------------------------------
    # Method 2: Get the camera image, from disk
    img_png = None
    import tempfile
    with tempfile.TemporaryDirectory(prefix='robodk_') as td:
        tf = td + '/temp.png'
        if RDK.Cam2D_Snapshot(tf, cam_item) == 1:
            img_png = cv.imread(tf)
    if img_png is None:
        break

    #----------------------------------
    # Show it to the world!
    cv.imshow(WINDOW_NAME, img_socket)
    key = cv.waitKey(1)
    if key == 27:
        break  # User pressed ESC, exit
    if cv.getWindowProperty(WINDOW_NAME, cv.WND_PROP_VISIBLE) < 1:
        break  # User killed the main window, exit

# Close the preview and the camera. Ensure you call cam_item.setParam('Open', 1) before reusing a camera!
cv.destroyAllWindows()
RDK.Cam2D_Close(cam_item)