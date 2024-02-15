# Type help("robolink") or help("robodk") for more information
# Press F5 to run the script
# Documentation: https://robodk.com/doc/en/RoboDK-API.html
# Reference:     https://robodk.com/doc/en/PythonAPI/index.html
#
# This script process a camera frame to extract QR and bar codes.
# It currently uses a RoboDK camera, but it can be easily adapted to use a physical device.

from robodk.robolink import *  # RoboDK API
from robodk.robomath import *  # Robot toolbox

import_install("cv2", "opencv-contrib-python")  # The contrib version adds the barcode support
import cv2 as cv
import tempfile

#----------------------------------------------
# Settings
PROCESS_COUNT = -1  # How many frames to process before exiting. -1 means indefinitely.
DETECT_COLOR = (0, 0, 255)

#----------------------------------------------
# Start a camera feed.
# If you are using a connected device, use cv.VideoCapture to get the livefeed.
# https://docs.opencv.org/master/d8/dfe/classcv_1_1VideoCapture.html
#
# capture = cv.VideoCapture(0)
# retval, image = capture.read()

#----------------------------------------------
# Get the camera from RoboDK
RDK = Robolink()
cam_item = RDK.ItemUserPick("Select the camera", ITEM_TYPE_CAMERA)
if not cam_item.Valid():
    quit()

#----------------------------------------------
# Initialize the QR and barcode detectors
qr_detector = cv.QRCodeDetector()  # https://docs.opencv.org/master/de/dc3/classcv_1_1QRCodeDetector.html
barcode_detector = cv.barcode_BarcodeDetector()  # https://docs.opencv.org/master/d2/dea/group__barcode.html

#----------------------------------------------
# For now, we need to save RDK snapshots on disk.
# A new update is coming which will return the image, like: img = RDK.Cam2D_Snapshot('', cam_item)
tempdir = tempfile.gettempdir()
snapshot_file = tempdir + "\\code_reader_temp.png"

#----------------------------------------------
# Process camera frames
count = 0
while count < PROCESS_COUNT or PROCESS_COUNT < 0:
    count += 1

    #----------------------------------------------
    # Save and get the image from RoboDK
    if RDK.Cam2D_Snapshot(snapshot_file, cam_item):
        img = cv.imread(snapshot_file)

        #----------------------------------------------
        # Check for QR codes
        retval, decoded_info_list, points_list, straight_qrcode_list = qr_detector.detectAndDecodeMulti(img)
        if retval:
            points_list = points_list.astype(int)
            n_qr = len(decoded_info_list)
            for i in range(n_qr):
                print("Found QR code: " + decoded_info_list[i])

                # Draw the contour
                points = points_list[i]
                n_lines = len(points)
                for j in range(n_lines):
                    point1 = points[j]
                    point2 = points[(j + 1) % n_lines]
                    cv.line(img, point1, point2, color=DETECT_COLOR, thickness=2)

                # Print the QR content
                cv.putText(img, decoded_info_list[i], points[0], cv.FONT_HERSHEY_SIMPLEX, 1, DETECT_COLOR, 2, cv.LINE_AA)

        #----------------------------------------------
        # Check for bar codes
        retval, decoded_info_list, decoded_type_list, points_list = barcode_detector.detectAndDecode(img)
        if retval:
            points_list = points_list.astype(int)
            n_bar = len(decoded_info_list)
            for i in range(n_bar):

                def barcodeType(decoded_type: int):
                    if decoded_type == cv.barcode.EAN_8:
                        return "EAN8"
                    elif decoded_type == cv.barcode.EAN_13:
                        return "EAN13"
                    elif decoded_type == cv.barcode.UPC_A:
                        return "UPC-A"
                    elif decoded_type == cv.barcode.UPC_E:
                        return "UPC-E"
                    elif decoded_type == cv.barcode.UPC_EAN_EXTENSION:
                        return "UPC-EAN"
                    else:
                        return "None"

                barcode_type = barcodeType(decoded_type_list[i])
                print("Found Bar code: " + decoded_info_list[i] + ", [%s]" % barcode_type)

                # Draw the contour
                points = points_list[i]
                n_lines = len(points)
                for j in range(n_lines):
                    point1 = points[j]
                    point2 = points[(j + 1) % n_lines]
                    cv.line(img, point1, point2, color=DETECT_COLOR, thickness=2)

                # Print the barcode content
                cv.putText(img, decoded_info_list[i], points[1], cv.FONT_HERSHEY_SIMPLEX, 1, DETECT_COLOR, 2, cv.LINE_AA)

        #----------------------------------------------
        # Display on screen
        cv.imshow("QR and Barcode reader", img)
        cv.waitKey(1)

        #----------------------------------------------
        # At this point, you can process the items.
        # For instance, request the robot to place the item on a specific conveyor, bin, etc.
        pause(1)

cv.destroyAllWindows()