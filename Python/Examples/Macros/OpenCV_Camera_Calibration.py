# Type help("robolink") or help("robodk") for more information
# Press F5 to run the script
# Documentation: https://robodk.com/doc/en/RoboDK-API.html
# Reference:     https://robodk.com/doc/en/PythonAPI/index.html
#
# Find a camera intrinsic and extrinsic properties using a chessboard and a series of images.
# More details on camera calibration: https://docs.opencv.org/master/dc/dbb/tutorial_py_calibration.html
# You can print this board in letter format: https://github.com/opencv/opencv/blob/master/doc/pattern.png

from robodk.robolink import *
from robodk.robodialogs import *
import cv2 as cv
import numpy as np
import glob

#----------------------------------------------
# You can edit these settings for your board
SQUARES_X = 10  # number of squares along the X axis
SQUARES_Y = 7  # number of squares along the Y axis
PATTERN = (SQUARES_X - 1, SQUARES_Y - 1)
SQUARE_LENGTH = 23.0  # mm, length of one square

#----------------------------------------------
# Get the images
images_dir = getSaveFolder(popup_msg='Select the directory of the images')
images = glob.glob('%s/*.png' % images_dir) + glob.glob('%s/*.jpg' % images_dir)

#----------------------------------------------
# Parse the images
frame_size = None
obj_points = []  # 3D points in real world space
img_points = []  # 2D points in image plane.
objp = np.zeros((PATTERN[0] * PATTERN[1], 3), np.float32)  # object points (0,0,0), (1,0,0), (2,0,0) ....,(8,5,0)
objp[:, :2] = np.mgrid[0:PATTERN[0], 0:PATTERN[1]].T.reshape(-1, 2) * SQUARE_LENGTH

for image in images:
    # Read the image as grayscale
    img = cv.imread(image)
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    frame_size = gray.shape[::-1]

    # Find the chessboard corners
    ret, corners = cv.findChessboardCorners(gray, PATTERN, None)

    # If found, add object points, image points (after refining them)
    if ret == True:
        rcorners = cv.cornerSubPix(gray, corners, (11, 11), (-1, -1), (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001))
        img_points.append(rcorners)
        obj_points.append(objp)

        # Draw and display the corners
        cv.drawChessboardCorners(img, PATTERN, rcorners, ret)
        cv.imshow('Original image', img)
        cv.waitKey(250)

cv.destroyAllWindows()

#----------------------------------------------
# Get the calibrated camera parameters
rms_err, calib_mtx, dist_coeffs, rvecs, tvecs = cv.calibrateCamera(obj_points, img_points, frame_size, None, None)
print('Overall RMS re-projection error: %0.3f' % rms_err)

#----------------------------------------------
# Save the parameters
file = getSaveFileName(strfile='RoboDK-Camera-Settings.yaml', defaultextension='.yaml', filetypes=[('YAML files', '.yaml')])
cv_file = cv.FileStorage(file, cv.FILE_STORAGE_WRITE)
if not cv_file.isOpened():
    raise Exception('Failed to save calibration file')
cv_file.write("camera_matrix", calib_mtx)
cv_file.write("dist_coeff", dist_coeffs)
cv_file.write("camera_size", frame_size)
cv_file.release()