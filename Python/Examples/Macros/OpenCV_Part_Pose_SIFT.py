# Type help("robolink") or help("robodk") for more information
# Press F5 to run the script
# Documentation: https://robodk.com/doc/en/RoboDK-API.html
# Reference:     https://robodk.com/doc/en/PythonAPI/index.html
#
# This example shows how to match an input image (source object) with a camera feed to determine it's 2D pose using a SIFT algorithm.
# It uses a simulated camera, but it can easily be modified to use an input camera.
# Warning: This only calculates the rotation along the Z axis, and the X/Y offsets. It is not meant for 3D positioning.
#
# You can find more information in the OpenCV homography tutorials:
# https://docs.opencv.org/master/d7/dff/tutorial_feature_homography.html
# https://docs.opencv.org/master/d9/dab/tutorial_homography.html

from robodk.robolink import *  # RoboDK API
from robodk.robomath import *  # Robot toolbox
from robodk.robodialogs import *

import_install('cv2', 'opencv-contrib-python')
import cv2 as cv
import numpy as np
import tempfile
import math

#----------------------------------
# Settings
PROCESS_COUNT = -1  # How many frames to process before exiting. -1 means indefinitely.

# Camera
CAM_NAME = "Camera"
CAMERA_SIZE_X = 1280.0  # pixel
CAMERA_SIZE_Y = 720.0  # pixel
PIXEL_SIZE_X = (100.0 / 175.0)  # mm/pixel, found experimentally
PIXEL_SIZE_Y = (100.0 / 175.0)  # mm/pixel
Z_OFFSET = 715.0  # mm, distance between the camera and the part surface

# Calculated frame and targets
OBJ_NAME = "RoboDK Box"
CALC_FRAME_NAME = "%s Calc Frame" % OBJ_NAME
CALC_TARGET_NAME = "%s Pick" % OBJ_NAME
CALC_TARGET_APPROACH_NAME = "%s Approach" % CALC_TARGET_NAME
APPROACH_DIST = 100  # mm

# Detection
MATCH_DIST_THRESH = 0.75  # Lowe's ratio threshold
MIN_MATCH = 15  # Minimum SIFT matches to consider the detection valid
OBJ_IMG_PATH = ""  # Absolute path to your source image. Leave empty to open a file dialog.

# Draw results
DISPLAY_RESULT = True  # Opens a window with the SIFT matches
DRAW_AXIS_LENGTH = 50  # pixel
DRAW_LINE_WEIGHT = 1  # pixel
DRAW_LINE_COLOR = (0, 255, 0)  # RGB

#----------------------------------
# Get the source image for recognition
img_path = OBJ_IMG_PATH
if img_path == "":
    img_path = getOpenFileName(strtitle='Select source object image', defaultextension='.png', filetypes=[('PNG', '.png'), ('JPEG', '.jpg')])
img_object = cv.imread(img_path, cv.IMREAD_GRAYSCALE)
if img_object is None or np.shape(img_object) == ():
    raise Exception("Unable to retrieve the source image for recognition!")

#----------------------------------
# Get the part to recognize
RDK = Robolink()

part = RDK.Item(OBJ_NAME, ITEM_TYPE_OBJECT)
if not part.Valid():
    raise Exception("Part not found! %s" % OBJ_NAME)
part_frame = part.Parent()
if not part_frame.Valid() or part_frame.Type() != ITEM_TYPE_FRAME:
    raise Exception("Part parent is invalid, make sur it's a frame!")

#----------------------------------
# Get the simulated camera from RoboDK
cam_item = RDK.Item(CAM_NAME, ITEM_TYPE_CAMERA)
if not cam_item.Valid():
    raise Exception("Camera not found! %s" % CAM_NAME)
cam_tool = cam_item.Parent()
if not cam_tool.Valid() or cam_tool.Type() != ITEM_TYPE_TOOL:
    raise Exception("Camera parent is invalid, make sur it's a tool!")

#----------------------------------
# Get or create the calculated object pose frame
calc_frame = RDK.Item(CALC_FRAME_NAME, ITEM_TYPE_FRAME)
if not calc_frame.Valid():
    calc_frame = RDK.AddFrame(CALC_FRAME_NAME, part_frame.Parent())

calc_pick = RDK.Item(CALC_TARGET_NAME, ITEM_TYPE_TARGET)
if not calc_pick.Valid():
    calc_pick = RDK.AddTarget(CALC_TARGET_NAME, calc_frame)

calc_pick_approach = RDK.Item(CALC_TARGET_APPROACH_NAME, ITEM_TYPE_TARGET)
if not calc_pick_approach.Valid():
    calc_pick_approach = RDK.AddTarget(CALC_TARGET_APPROACH_NAME, calc_frame)

#----------------------------------------------
# Start a camera feed.
# If you are using a connected device, use cv.VideoCapture to get the livefeed.
# https://docs.opencv.org/master/d8/dfe/classcv_1_1VideoCapture.html
#
# capture = cv.VideoCapture(0)
# retval, image = capture.read()

#----------------------------------------------
# For now, we need to save RDK snapshots on disk.
# A new update is coming which will return the image, like: img = RDK.Cam2D_Snapshot('', cam_item)
tempdir = tempfile.gettempdir()
snapshot_file = tempdir + "\\sift_temp.png"

#----------------------------------------------
# Process camera frames
count = 0
while count < PROCESS_COUNT or PROCESS_COUNT < 0:
    count += 1

    #----------------------------------------------
    # Save and get the image from RoboDK
    if RDK.Cam2D_Snapshot(snapshot_file, cam_item):
        img_scene = cv.imread(snapshot_file, cv.IMREAD_GRAYSCALE)

        #----------------------------------------------
        # Detect the keypoints using SIFT Detector, compute the descriptors
        detector = cv.SIFT_create()
        keypoints_obj, descriptors_obj = detector.detectAndCompute(img_object, None)
        keypoints_scene, descriptors_scene = detector.detectAndCompute(img_scene, None)
        if descriptors_obj is None or descriptors_scene is None or keypoints_obj == [] or keypoints_scene == []:
            print("Unable to detect keypoints")
            continue

        # Match descriptor vectors
        matcher = cv.DescriptorMatcher_create(cv.DescriptorMatcher_FLANNBASED)
        knn_matches = matcher.knnMatch(descriptors_obj, descriptors_scene, 2)

        # Filter matches using the Lowe's ratio test
        good_matches = []
        for m, n in knn_matches:
            if m.distance < MATCH_DIST_THRESH * n.distance:
                good_matches.append(m)

        # Draw matches
        img_matches = np.empty((max(img_object.shape[0], img_scene.shape[0]), img_object.shape[1] + img_scene.shape[1], 3), dtype=np.uint8)
        cv.drawMatches(img_object, keypoints_obj, img_scene, keypoints_scene, good_matches, img_matches, flags=cv.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)

        # Stop processing on low match count
        if len(good_matches) < MIN_MATCH:
            print("No enough matches")
            continue

        #----------------------------------------------
        # Localize the object
        obj = np.empty((len(good_matches), 2), dtype=np.float32)
        scene = np.empty((len(good_matches), 2), dtype=np.float32)
        for i in range(len(good_matches)):
            # Get the keypoints from the good matches
            obj[i, 0] = keypoints_obj[good_matches[i].queryIdx].pt[0]
            obj[i, 1] = keypoints_obj[good_matches[i].queryIdx].pt[1]
            scene[i, 0] = keypoints_scene[good_matches[i].trainIdx].pt[0]
            scene[i, 1] = keypoints_scene[good_matches[i].trainIdx].pt[1]

        # Calculate the perspective transformation, or Homography matrix
        H, _ = cv.findHomography(obj, scene, cv.RANSAC)
        if H is None or np.shape(H) == ():
            print("No transformation possible")
            continue

        # We can extract the rotation angle from H directly
        theta = -math.atan2(H[0, 1], H[0, 0])

        #----------------------------------------------
        # There are many ways to calculate the pose.
        #
        # 1. Using a camera matrix
        #    If you you have a calibrated camera (simulated or hardware), you can decompose H and get the rotation and translation solutions (up to four solutions).
        #    See our examples on how to calibrate a camera:
        #    - https://robodk.com/doc/en/PythonAPI/examples.html#camera-calibration
        #
        # cam_mtx = np.array([[1.3362190822261939e+04, 0., 8.4795067509033629e+02], [0., 1.3361819220999134e+04, 1.6875586379396785e+02], [0., 0., 1.]])  # Sample camera matrix from a 1280x720 simulated camera
        # n_solution, rot, trans, normals = cv.decomposeHomographyMat(H, cam_mtx)
        # for i in range(n_solution):
        #     vx, vy, vz = rot[i].tolist()
        #     tx, ty, tz = trans[i].tolist()

        #----------------------------------------------
        # 2. Using moments
        #    This method does not take into account the camera matrix, small errors are expected.
        #    For more information, visit:
        #    - https://en.wikipedia.org/wiki/Image_moment
        #    - https://docs.opencv.org/master/d8/d23/classcv_1_1Moments.html

        # Get the corners from the object image
        obj_corners = np.zeros((4, 1, 2), dtype=np.float32)  # corder id, x, y
        obj_corners[1, 0, 0] = img_object.shape[1]
        obj_corners[2, 0, 0] = img_object.shape[1]
        obj_corners[2, 0, 1] = img_object.shape[0]
        obj_corners[3, 0, 1] = img_object.shape[0]

        # Transform the object corners to the camera image
        scene_corners = cv.perspectiveTransform(obj_corners, H)

        # Get the image moments, and extract the center
        moments = cv.moments(scene_corners)
        cx = moments['m10'] / moments['m00']
        cy = moments['m01'] / moments['m00']

        #----------------------------------------------
        # Calculate X and Y relative to the camera frame
        rel_x = (cx - CAMERA_SIZE_X / 2.0) * PIXEL_SIZE_X
        rel_y = (cy - CAMERA_SIZE_Y / 2.0) * PIXEL_SIZE_Y
        rel_theta = float(theta)

        # Centered tolerance
        if abs(rel_x) < 1:
            rel_x = 0.0
        if abs(rel_y) < 1:
            rel_y = 0.0
        if abs(rel_theta) < 0.0005:
            rel_theta = 0.0

        # Precision tolerance
        rel_x = round(rel_x, 4)
        rel_y = round(rel_y, 4)
        rel_theta = round(rel_theta, 4)

        # Calculate the pose wrt to the camera
        calc_frame_pose = cam_tool.Pose()
        calc_frame_pose.setPos([rel_x, rel_y, Z_OFFSET])
        calc_frame_pose = calc_frame_pose * rotz(rel_theta)

        # Lazy way of calculating a set of relative poses is to static move them around!
        calc_frame.setParent(cam_tool)
        calc_frame.setPose(calc_frame_pose)
        calc_pick.setPose(eye(4))
        calc_pick_approach.setPose(calc_pick.Pose() * transl(0, 0, -APPROACH_DIST))
        calc_frame.setParentStatic(part_frame)

        #----------------------------------------------
        # Display the detection to the user (reference image and camera image side by side, with detection results)
        if DISPLAY_RESULT:

            def rotate(origin, point, angle):
                """Rotate a point counterclockwise by a given angle (radians) around a given origin."""
                ox, oy = origin
                px, py = point
                qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
                qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
                return qx, qy

            # Construct the drawing parameters
            cx_off = img_object.shape[1]
            center_pt = (cx + cx_off, cy)
            x_axis = (center_pt[0] + DRAW_AXIS_LENGTH, center_pt[1])
            x_axis = rotate(center_pt, x_axis, theta)
            y_axis = rotate(center_pt, x_axis, pi / 2.0)

            center_pt = (int(center_pt[0]), int(center_pt[1]))
            x_axis = (int(x_axis[0]), int(x_axis[1]))
            y_axis = (int(y_axis[0]), int(y_axis[1]))

            # Draw the orientation vector of the detected object
            cv.circle(img_matches, center_pt, 3, (0, 255, 255), -1)
            cv.arrowedLine(img_matches, center_pt, x_axis, (0, 0, 255), 2, cv.LINE_AA)  # X
            cv.arrowedLine(img_matches, center_pt, y_axis, (0, 255, 0), 2, cv.LINE_AA)  # Y

            # Draw lines between the corners of the detected object
            cv.line(img_matches, (int(scene_corners[0,0,0] + img_object.shape[1]), int(scene_corners[0,0,1])),\
                (int(scene_corners[1,0,0] + img_object.shape[1]), int(scene_corners[1,0,1])), DRAW_LINE_COLOR, DRAW_LINE_WEIGHT)
            cv.line(img_matches, (int(scene_corners[1,0,0] + img_object.shape[1]), int(scene_corners[1,0,1])),\
                (int(scene_corners[2,0,0] + img_object.shape[1]), int(scene_corners[2,0,1])), DRAW_LINE_COLOR, DRAW_LINE_WEIGHT)
            cv.line(img_matches, (int(scene_corners[2,0,0] + img_object.shape[1]), int(scene_corners[2,0,1])),\
                (int(scene_corners[3,0,0] + img_object.shape[1]), int(scene_corners[3,0,1])), DRAW_LINE_COLOR, DRAW_LINE_WEIGHT)
            cv.line(img_matches, (int(scene_corners[3,0,0] + img_object.shape[1]), int(scene_corners[3,0,1])),\
                (int(scene_corners[0,0,0] + img_object.shape[1]), int(scene_corners[0,0,1])), DRAW_LINE_COLOR, DRAW_LINE_WEIGHT)

            # Show detected matches
            wdw_name = 'RoboDK - Matches and detected object'
            cv.imshow(wdw_name, img_matches)
            key = cv.waitKey(1)
            if key == 27:
                break  # User pressed ESC, exit
            if cv.getWindowProperty(wdw_name, cv.WND_PROP_VISIBLE) < 1:
                break  # User killed the main window, exit

cv.destroyAllWindows()
