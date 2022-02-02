# Type help("robolink") or help("robodk") for more information
# Press F5 to run the script
# Documentation: https://robodk.com/doc/en/RoboDK-API.html
# Reference:     https://robodk.com/doc/en/PythonAPI/index.html
#
# This example shows how to detect blobs in a camera feed using OpenCV.
# It uses a simulated camera, but it can easily be modified to use an input camera.
#
# You can find more information in the OpenCV Contours tutorials:
# https://docs.opencv.org/master/d3/d05/tutorial_py_table_of_contents_contours.html

from robodk.robolink import *  # RoboDK API

import_install('cv2', 'opencv-python')
import cv2 as cv
import numpy as np

#----------------------------------
# Settings
PROCESS_COUNT = -1  # How many frames to process before exiting. -1 means indefinitely.

CAM_NAME = "Camera"

DISPLAY_SETTINGS = True
WDW_NAME_PARAMS = 'RoboDK - Blob detection parameters'

DISPLAY_RESULT = True
WDW_NAME_RESULTS = 'RoboDK - Blob detections'

#----------------------------------
# Get the simulated camera from RoboDK
RDK = Robolink()

cam_item = RDK.Item(CAM_NAME, ITEM_TYPE_CAMERA)
if not cam_item.Valid():
    raise Exception("Camera not found! %s" % CAM_NAME)
cam_item.setParam('Open', 1)  # Force the camera view to open

#----------------------------------------------
# Set up the detector with default parameters.
# Default parameters extract dark circular blobs.
global params
params = cv.SimpleBlobDetector_Params()
global detector
detector = cv.SimpleBlobDetector_create(params)

#----------------------------------------------
# Set up sliders for parameters, using OpenCV's trackbars
if DISPLAY_SETTINGS:

    cv.namedWindow(WDW_NAME_PARAMS, cv.WINDOW_FREERATIO | cv.WINDOW_GUI_EXPANDED)

    def minDistBetweenBlobs(value):
        """Minimum distance between two blobs, in pixels."""
        global params
        global detector
        params.minDistBetweenBlobs = value
        detector = cv.SimpleBlobDetector_create(params)

    # Image thresholds
    def minThreshold(value):
        """Minimum intensity threshold, in uint8."""
        global params
        global detector
        params.minThreshold = value
        detector = cv.SimpleBlobDetector_create(params)

    def maxThreshold(value):
        """Maximum intensity threshold, in uint8."""
        global params
        global detector
        params.maxThreshold = value
        detector = cv.SimpleBlobDetector_create(params)

    def thresholdStep(value):
        """Intensity threshold steps between min and max thresholds, in uint8."""
        global params
        global detector
        params.thresholdStep = max(1, value)
        detector = cv.SimpleBlobDetector_create(params)

    def minRepeatability(value):
        """Minimum number of detections of a blob throughout the thresholding steps."""
        global params
        global detector
        params.minRepeatability = max(1, value)
        detector = cv.SimpleBlobDetector_create(params)

    # Filter by Area
    def filterByArea(value):
        """Enable filtering by blob area."""
        global params
        global detector
        params.filterByArea = value != 0
        detector = cv.SimpleBlobDetector_create(params)

    def minArea(value):
        """Minimum blob area, in pixel^2."""
        global params
        global detector
        params.minArea = value
        detector = cv.SimpleBlobDetector_create(params)

    def maxArea(value):
        """Maximum blob area, in pixel^2."""
        global params
        global detector
        params.maxArea = value
        detector = cv.SimpleBlobDetector_create(params)

    # Filter by Circularity (4*pi*area / perimeter^2)
    def filterByCircularity(value):
        """Enable filtering by blob circularity."""
        global params
        global detector
        params.filterByCircularity = value != 0
        detector = cv.SimpleBlobDetector_create(params)

    def minCircularity(value):
        """Minimum blob circularity, in %."""
        global params
        global detector
        params.minCircularity = value / 100
        detector = cv.SimpleBlobDetector_create(params)

    def maxCircularity(value):
        """Maximum blob circularity, in %."""
        global params
        global detector
        params.maxCircularity = value / 100
        detector = cv.SimpleBlobDetector_create(params)

    # Filter by Convexity (area / area of blob convex hull)
    def filterByConvexity(value):
        """Enable filtering by blob convexity."""
        global params
        global detector
        params.filterByConvexity = value != 0
        detector = cv.SimpleBlobDetector_create(params)

    def minConvexity(value):
        """Minimum blob convexity, in %."""
        global params
        global detector
        params.minConvexity = value / 100
        detector = cv.SimpleBlobDetector_create(params)

    def maxConvexity(value):
        """Maximum blob convexity, in %."""
        global params
        global detector
        params.maxConvexity = value / 100
        detector = cv.SimpleBlobDetector_create(params)

    # Filter by Color (light vs. dark)
    def filterByColor(value):
        """Enable filtering by blob color."""
        global params
        global detector
        params.filterByColor = value != 0
        detector = cv.SimpleBlobDetector_create(params)

    def blobColor(value):
        """Color of the blob, in uint8."""
        global params
        global detector
        params.blobColor = value  # [0 (dark), 255 (light)]
        detector = cv.SimpleBlobDetector_create(params)

    # Filter by Inertia (elongation)
    def filterByInertia(value):
        """Enable filtering by blob inertia."""
        global params
        global detector
        params.filterByInertia = value != 0
        detector = cv.SimpleBlobDetector_create(params)

    def minInertiaRatio(value):
        """Minimum blob inertia, in %."""
        global params
        global detector
        params.minInertiaRatio = value / 100  # [0, 1]
        detector = cv.SimpleBlobDetector_create(params)

    def maxInertiaRatio(value):
        """Maximum blob inertia, in %."""
        global params
        global detector
        params.maxInertiaRatio = value / 100  # [0, 1]
        detector = cv.SimpleBlobDetector_create(params)

    # All ranges are from 0 to 'count', initialized at the default value.
    cv.createTrackbar('Dist\nMin', WDW_NAME_PARAMS, int(params.minDistBetweenBlobs), 999, minDistBetweenBlobs)
    cv.createTrackbar('Thresh\nMin', WDW_NAME_PARAMS, int(params.minThreshold), 255, minThreshold)
    cv.createTrackbar('Thresh\nMax', WDW_NAME_PARAMS, int(params.maxThreshold), 255, maxThreshold)
    cv.createTrackbar('Thresh\nStp', WDW_NAME_PARAMS, int(params.thresholdStep), 255, thresholdStep)
    cv.createTrackbar('Thresh\nRep', WDW_NAME_PARAMS, int(params.minRepeatability), 100, minRepeatability)
    cv.createTrackbar('Area\nON', WDW_NAME_PARAMS, bool(params.filterByArea), 1, filterByArea)
    cv.createTrackbar('Area\nMin', WDW_NAME_PARAMS, int(params.minArea), 500, minArea)
    cv.createTrackbar('Area\nMax', WDW_NAME_PARAMS, int(params.maxArea), 5000, maxArea)
    cv.createTrackbar('Circ\nON', WDW_NAME_PARAMS, bool(params.filterByCircularity), 1, filterByCircularity)
    cv.createTrackbar('Circ\nMin', WDW_NAME_PARAMS, int(params.minCircularity * 100), 500, minCircularity)
    cv.createTrackbar('Circ\nMax', WDW_NAME_PARAMS, int(min(500, params.maxCircularity * 100)), 500, maxCircularity)
    cv.createTrackbar('Conv\nON', WDW_NAME_PARAMS, bool(params.filterByConvexity), 1, filterByConvexity)
    cv.createTrackbar('Conv\nMin', WDW_NAME_PARAMS, int(params.minConvexity * 100), 500, minConvexity)
    cv.createTrackbar('Conv\nMax', WDW_NAME_PARAMS, int(min(500, params.maxConvexity * 100)), 500, maxConvexity)
    cv.createTrackbar('Color\nON', WDW_NAME_PARAMS, bool(params.filterByColor), 1, filterByColor)
    cv.createTrackbar('Color', WDW_NAME_PARAMS, int(params.blobColor), 255, blobColor)
    cv.createTrackbar('Inert\nON', WDW_NAME_PARAMS, bool(params.filterByInertia), 1, filterByInertia)
    cv.createTrackbar('Inert\nMin', WDW_NAME_PARAMS, int(params.minInertiaRatio * 100), 100, minInertiaRatio)
    cv.createTrackbar('Inert\nMax', WDW_NAME_PARAMS, int(min(100, params.maxInertiaRatio * 100)), 100, maxInertiaRatio)

#----------------------------------------------
# Create an resizable result window
if DISPLAY_RESULT:
    cv.namedWindow(WDW_NAME_RESULTS)  #, cv.WINDOW_NORMAL)

#----------------------------------------------
# Start a camera feed.
# If you are using a connected device, use cv.VideoCapture to get the livefeed.
# https://docs.opencv.org/master/d8/dfe/classcv_1_1VideoCapture.html
#
# capture = cv.VideoCapture(0)
# retval, image = capture.read()

#----------------------------------------------
# Process camera frames
count = 0
while count < PROCESS_COUNT or PROCESS_COUNT < 0:
    print("=============================================")
    print("Processing image %i" % count)
    count += 1

    #----------------------------------------------
    # Get the image from RoboDK
    bytes_img = RDK.Cam2D_Snapshot("", cam_item)
    if bytes_img == b'':
        raise
    # Image from RoboDK are BGR, uchar, (h,w,3)
    nparr = np.frombuffer(bytes_img, np.uint8)
    img = cv.imdecode(nparr, cv.IMREAD_UNCHANGED)
    if img is None or img.shape == ():
        raise

    #----------------------------------------------
    # Detect blobs
    keypoints = detector.detect(img)
    i = 0
    for keypoint in keypoints:
        print("id:%i  coord=(%0.0f, %0.0f)" % (i, keypoint.pt[0], keypoint.pt[1]))
        i += 1

    #----------------------------------------------
    # Do something with your detections!
    # Here's a few examples:
    # - Reject a part if the number of keypoints (screw holes) is different than 3
    # - Calculate the world coordinate of each keypoints to move the robot

    #----------------------------------------------
    # Display the detection to the user (reference image and camera image side by side, with detection results)
    if DISPLAY_RESULT:

        # Draw detected blobs and their id
        img_matches = cv.drawKeypoints(img, keypoints, None, (0, 255, 0), cv.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        i = 0
        for keypoint in keypoints:
            x, y = keypoint.pt
            cv.putText(img_matches, str(i), (int(x), int(y)), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 1, cv.LINE_AA)
            i += 1

        # Resize the image, so that it fits your screen
        img_matches = cv.resize(img_matches, (int(img_matches.shape[1] * .75), int(img_matches.shape[0] * .75)))

        cv.imshow(WDW_NAME_RESULTS, img_matches)
        key = cv.waitKey(500)
        if key == 27:
            break  # User pressed ESC, exit
        if cv.getWindowProperty(WDW_NAME_RESULTS, cv.WND_PROP_VISIBLE) < 1:
            break  # User killed the window, exit

cv.destroyAllWindows()
