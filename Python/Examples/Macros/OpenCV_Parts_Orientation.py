# Type help("robolink") or help("robodk") for more information
# Press F5 to run the script
# Documentation: https://robodk.com/doc/en/RoboDK-API.html
# Reference:     https://robodk.com/doc/en/PythonAPI/index.html
#
# This example shows how to detect the orientation of elongated parts in a camera feed using OpenCV.
# It uses a simulated camera, but it can easily be modified to use an input camera.
# Warning: best results are observe with elongated parts that are symmetrical.
#
# You can find more information in the OpenCV Contours tutorials:
# https://docs.opencv.org/master/d3/d05/tutorial_py_table_of_contents_contours.html

from robolink import *  # RoboDK API
from robodk import *  # Robot toolbox

import_install('cv2', 'opencv-contrib-python')
import cv2 as cv
import numpy as np

#----------------------------------
# Settings
PROCESS_COUNT = -1  # How many frames to process before exiting. -1 means indefinitely.

CAM_NAME = "Camera"

DISPLAY_SETTINGS = True
WDW_NAME_PARAMS = 'RoboDK - Part orientation parameters'

DISPLAY_RESULT = True
WDW_NAME_RESULTS = 'RoboDK - Part orientation'

DRAW_AXIS_LENGTH = 30

THRESH_MIN = 50
THRESH_MAX = 255
LENGTH_MIN = 100
LENGTH_MAX = 400
AREA_MIN = 400
AREA_MAX = 1000

#----------------------------------
# Get the simulated camera from RoboDK
RDK = Robolink()

cam_item = RDK.Item(CAM_NAME, ITEM_TYPE_CAMERA)
if not cam_item.Valid():
    raise Exception("Camera not found! %s" % CAM_NAME)
cam_item.setParam('Open', 1)  # Force the camera view to open

#----------------------------------------------
# Start a camera feed.
# If you are using a connected device, use cv.VideoCapture to get the livefeed.
# https://docs.opencv.org/master/d8/dfe/classcv_1_1VideoCapture.html
#
# capture = cv.VideoCapture(0)
# retval, image = capture.read()

#----------------------------------------------
# Create an resizable result window with sliders for parameters
if DISPLAY_RESULT:
    cv.namedWindow(WDW_NAME_RESULTS)

if DISPLAY_SETTINGS:

    def nothing(val):
        pass

    cv.namedWindow(WDW_NAME_PARAMS)
    cv.createTrackbar('Thresh\nMin', WDW_NAME_PARAMS, THRESH_MIN, 255, nothing)
    cv.createTrackbar('Thresh\nMax', WDW_NAME_PARAMS, THRESH_MAX, 255, nothing)
    cv.createTrackbar('Length\nMin', WDW_NAME_PARAMS, LENGTH_MIN, 1000, nothing)
    cv.createTrackbar('Length\nMax', WDW_NAME_PARAMS, LENGTH_MAX, 2500, nothing)
    cv.createTrackbar('Area\nMin', WDW_NAME_PARAMS, AREA_MIN, 1000, nothing)
    cv.createTrackbar('Area\nMax', WDW_NAME_PARAMS, AREA_MAX, 2500, nothing)

#----------------------------------------------
# Process camera frames
count = 0
while count < PROCESS_COUNT or PROCESS_COUNT < 0:
    count += 1

    #----------------------------------------------
    # Get the image from RoboDK (since 5.3.0)
    bytes_img = RDK.Cam2D_Snapshot("", cam_item)
    if bytes_img == b'':
        raise
    # Image from RoboDK are BGR, uchar, (h,w,3)
    nparr = np.frombuffer(bytes_img, np.uint8)
    img = cv.imdecode(nparr, cv.IMREAD_UNCHANGED)
    if img is None or img.shape == ():
        raise

    #----------------------------------------------
    # Retrieve the slider values for this iteration
    if DISPLAY_SETTINGS:
        THRESH_MIN = cv.getTrackbarPos('Thresh\nMin', WDW_NAME_PARAMS)
        THRESH_MAX = cv.getTrackbarPos('Thresh\nMax', WDW_NAME_PARAMS)
        LENGTH_MIN = cv.getTrackbarPos('Length\nMin', WDW_NAME_PARAMS)
        LENGTH_MAX = cv.getTrackbarPos('Length\nMax', WDW_NAME_PARAMS)
        AREA_MIN = cv.getTrackbarPos('Area\nMin', WDW_NAME_PARAMS)
        AREA_MAX = cv.getTrackbarPos('Area\nMax', WDW_NAME_PARAMS)

    #----------------------------------------------
    # The easiest way to extract features is to threshold their intensity with regards to their background
    # Optimal results with light parts on dark background, and vice-versa
    _, img_bw = cv.threshold(cv.cvtColor(img, cv.COLOR_BGR2GRAY), THRESH_MIN, THRESH_MAX, cv.THRESH_BINARY | cv.THRESH_OTSU)

    #----------------------------------------------
    # Find and parse all the contours in the binary image
    contours, _ = cv.findContours(img_bw, cv.RETR_LIST, cv.CHAIN_APPROX_NONE)
    for i, c in enumerate(contours):
        reject = False

        # Calculate contour's length (only works with CHAIN_APPROX_NONE)
        length = len(c)
        if length < LENGTH_MIN or length > LENGTH_MAX:
            reject = True

        # Calculate the contour's area
        area = cv.contourArea(c)
        if area < AREA_MIN or area > AREA_MAX:
            reject = True

        #----------------------------------------------
        # Create a bounding box of the contour
        rect = cv.minAreaRect(c)
        center = (rect[0][0], rect[0][1])
        width = rect[1][0]
        height = rect[1][1]
        angle = np.radians(rect[2])
        # Angle is [0, 90], and from the horizontal to the bottom left and bottom right edge of the box
        if width < height:
            angle += pi / 2.0
        if angle > pi:
            angle -= pi

        #----------------------------------------------
        # You can also bestfit an ellipse and use it's angle
        #if length > 4:
        #    ell = cv.fitEllipse(c)
        #    center = (ell[0][0], ell[0][1])
        #    width = ell[1][0]
        #    height = ell[1][1]
        #    angle = np.radians(ell[2])
        #    if width < height2:
        #        angle += pi / 2.0
        #    if angle2 > pi:
        #        angle -= pi

        #----------------------------------------------
        # Do something with your detections!
        # Here's a few examples:
        # - Reject a part if it's orientation is different than expected
        # - Reject a part if it's area is too small
        # - Calculate the robot's rotation angle to pick a part

        #----------------------------------------------
        # Display the detection to the user (reference image and camera image side by side, with detection results)
        if DISPLAY_RESULT:
            color = (0, 255, 0)
            if reject:
                color = (0, 0, 255)

            # Draw the bounding box
            box = cv.boxPoints(rect)
            box = np.int0(box)
            cv.drawContours(img, [box], 0, color, 1)

            # Draw the contour
            cv.drawContours(img, contours, i, color, 1)

            if not reject:

                def rotate(origin, point, angle):
                    """Rotate a point counterclockwise by a given angle (radians) around a given origin."""
                    ox, oy = origin
                    px, py = point
                    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
                    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
                    return qx, qy

                # Construct the Axis parameters
                center_pt = center
                x_axis = (center_pt[0] + DRAW_AXIS_LENGTH, center_pt[1])
                x_axis = rotate(center_pt, x_axis, angle)
                y_axis = rotate(center_pt, x_axis, pi / 2.0)

                center_pt = (int(center_pt[0]), int(center_pt[1]))
                x_axis = (int(x_axis[0]), int(x_axis[1]))
                y_axis = (int(y_axis[0]), int(y_axis[1]))

                # Draw the orientation vector
                cv.circle(img, center_pt, 2, (255, 0, 0), -1)
                cv.arrowedLine(img, center_pt, x_axis, (0, 0, 255), 2, cv.LINE_AA)
                cv.arrowedLine(img, center_pt, y_axis, (0, 255, 0), 2, cv.LINE_AA)

                # Draw the angle
                label = '%0.1f' % np.degrees(angle)
                cv.putText(img, label, (center_pt[0] + 30, center_pt[1]), cv.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1, cv.LINE_AA)

    cv.imshow(WDW_NAME_RESULTS, img)
    key = cv.waitKey(1)
    if key == 27:
        break  # User pressed ESC, exit
    if cv.getWindowProperty(WDW_NAME_RESULTS, cv.WND_PROP_VISIBLE) < 1:
        break  # User killed the main window, exit

cv.destroyAllWindows()
