# Type help("robolink") or help("robodk") for more information
# Press F5 to run the script
# Documentation: https://robodk.com/doc/en/RoboDK-API.html
# Reference:     https://robodk.com/doc/en/PythonAPI/index.html
#
# Apply augmented reality using OpenCV and a ChArUco board.
# More details on ChArUco board: https://docs.opencv.org/master/df/d4a/tutorial_charuco_detection.html
# You can print this board in letter format: https://docs.opencv.org/master/charucoboard.jpg
# Camera calibration is required for pose estimation, see https://robodk.com/doc/en/PythonAPI/examples.html#camera-calibration

from robolink import *
from robodk import *
import cv2 as cv
import numpy as np

#----------------------------------------------
# If you have more than one device, change this accordingly
DEVICE_ID = 0

# You can edit these settings for your board
SQUARES_X = 5  # number of squares along the X axis
SQUARES_Y = 7  # number of squares along the Y axis
SQUARE_LENGTH = 35.0  # mm, length of one square
MARKER_LENGTH = 23.0  # mm, length of one marker

SCALE = 1  # You might want to edit this if you do not wish to have a 1:1 scale.

DICTIONNARY = cv.aruco.getPredefinedDictionary(cv.aruco.DICT_6X6_250)  # Predefined dictionary of 250 6x6 bits markers
CHARUCOBOARD = cv.aruco.CharucoBoard_create(SQUARES_X, SQUARES_Y, SQUARE_LENGTH / SCALE, MARKER_LENGTH / SCALE, DICTIONNARY)

# Camera settings
CAMERA_WIDTH = 1920  # px
CAMERA_HEIGHT = 1080  # px
CAMERA_APERTURE = 2.0  # mm

#----------------------------------------------
# Utility function to merge the RoboDK image with the input image
def merge_img(img_bg, img_fg):

    # Mask and inverse-mask of AR image
    _, mask = cv.threshold(cv.cvtColor(img_fg, cv.COLOR_BGR2GRAY), 10, 255, cv.THRESH_BINARY)
    mask_inv = cv.bitwise_not(mask)

    # Black-out AR area from environnement image
    img1_bg = cv.bitwise_and(img_bg, img_bg, mask=mask_inv)

    # Take-out AR area from AR image
    img2_fg = cv.bitwise_and(img_fg, img_fg, mask=mask)

    # Merge
    return cv.add(img1_bg, img2_fg)

#----------------------------------------------
# Link to RoboDK
RDK = Robolink()

# Get the camera
capture = cv.VideoCapture(DEVICE_ID)
if not capture.isOpened():
    RDK.ShowMessage("Selected device id [{0}] could not be opened. Ensure the camera is plugged in and that no other application is using it.".format(DEVICE_ID))
    quit()

# Set the camera resolution. If the resolution is not found, it will default to the next available resolution.
capture.set(cv.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
capture.set(cv.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
width, height = int(capture.get(cv.CAP_PROP_FRAME_WIDTH)), int(capture.get(cv.CAP_PROP_FRAME_HEIGHT))
print('Camera resolution: {0}, {1}'.format(width, height))

#----------------------------------------------
# Get the camera calibration parameters
file = getOpenFileName(strfile='RoboDK-Camera-Settings.yaml', strtitle='Open calibration settings file..', defaultextension='.yaml', filetypes=[('YAML files', '.yaml')])
cv_file = cv.FileStorage(file, cv.FILE_STORAGE_READ)
if not cv_file.isOpened():
    RDK.ShowMessage("Failed to process calibration file")
    quit()
CAMERA_MTX = cv_file.getNode("camera_matrix").mat()
DIST_COEFFS = cv_file.getNode("dist_coeff").mat()
CALIB_SIZE = cv_file.getNode("camera_size").mat().astype(int)
cv_file.release()

# If the calibrated camera resolution and the current resolution differs, approximate the camera matrix
c_width, c_height = CALIB_SIZE
if (width, height) != (c_width, c_height):
    RDK.ShowMessage("The calibrated resolution and the current resolution differs. Approximated calibration matrix will be used.")
    CAMERA_MTX[0][0] = (width / c_width) * CAMERA_MTX[0][0]  # fx' = (dimx' / dimx) * fx
    CAMERA_MTX[1][1] = (height / c_height) * CAMERA_MTX[1][1]  # fy' = (dimy' / dimy) * fy

# Assuming an aperture of 2 mm, update if needed
fovx, fovy, focal_length, p_point, ratio = cv.calibrationMatrixValues(CAMERA_MTX, (width, height), CAMERA_APERTURE, CAMERA_APERTURE)

#----------------------------------------------
# Close camera windows, if any
RDK.Cam2D_Close(0)

# Create the charuco frame for the pose estimation
board_frame_name = 'ChArUco Frame'
board_ref = RDK.Item(board_frame_name, ITEM_TYPE_FRAME)
if not board_ref.Valid():
    board_ref = RDK.AddFrame(board_frame_name)

# Create a frame on which to attach the camera
cam_frame_name = 'Camera Frame'
cam_ref = RDK.Item(cam_frame_name, ITEM_TYPE_FRAME)
if not cam_ref.Valid():
    cam_ref = RDK.AddFrame(cam_frame_name)
cam_ref.setParent(board_ref)

# Simulated camera
cam_name = 'Camera'
cam_id = RDK.Item(cam_name, ITEM_TYPE_CAMERA)
if cam_id.Valid():
    cam_id.Delete()  # Reusing the same camera doesn't apply the settings correctly
camera_settings = 'FOCAL_LENGHT={0:0.0f} FOV={1:0.0f} BG_COLOR=black FAR_LENGTH=5000 SNAPSHOT={2:0.0f}x{3:0.0f} SIZE={2:0.0f}x{3:0.0f}'.format(focal_length, fovy, width, height)
cam_id = RDK.Cam2D_Add(cam_ref, camera_settings)
cam_id.setName(cam_name)
cam_id.setParent(cam_ref.Parent())

# Create an output window
preview_window = 'Camera Window'
cv.namedWindow(preview_window, cv.WINDOW_KEEPRATIO)
cv.resizeWindow(preview_window, width, height)

#----------------------------------------------
# Find the camera pose
while capture.isOpened():

    # Get the image from the camera
    success, image = capture.read()
    if not success or image is None:
        continue

    # Find the board markers
    mcorners, mids, _ = cv.aruco.detectMarkers(image, DICTIONNARY, None, None, None, None, CAMERA_MTX, DIST_COEFFS)
    if mids is not None and len(mids) > 0:

        # Interpolate the charuco corners from the markers
        count, corners, ids = cv.aruco.interpolateCornersCharuco(mcorners, mids, image, CHARUCOBOARD, None, None, CAMERA_MTX, DIST_COEFFS, 2)
        if count > 0 and len(ids) > 0:
            print('Detected Corners: %i, Ids: %i' % (len(corners), len(ids)))

            # Draw corners on the image
            cv.aruco.drawDetectedCornersCharuco(image, corners, ids)

            # Estimate the charuco board pose
            success, rvec, tvec = cv.aruco.estimatePoseCharucoBoard(corners, ids, CHARUCOBOARD, CAMERA_MTX, DIST_COEFFS, None, None, False)
            if success:
                # Draw axis on image
                image = cv.aruco.drawAxis(image, CAMERA_MTX, DIST_COEFFS, rvec, tvec, 100.)

                # You can filter how much marker needs to be found in order to update the pose as follow
                board_size = CHARUCOBOARD.getChessboardSize()
                min_corners = int((board_size[0] - 1) * (board_size[1] - 1) * 0.8)  # as a % of the total
                if corners.shape[0] >= min_corners and ids.size >= min_corners:

                    # Find the camera pose
                    rmat = cv.Rodrigues(rvec)[0]
                    camera_position = -np.matrix(rmat).T * np.matrix(tvec)
                    cam_xyz = camera_position.T.tolist()[0]
                    vx, vy, vz = rmat.tolist()

                    # Build the camera pose for RoboDK
                    pose = eye(4)
                    pose.setPos(cam_xyz)
                    pose.setVX(vx)
                    pose.setVY(vy)
                    pose.setVZ(vz)

                    # Update the pose in RoboDK
                    cam_ref.setPose(pose)

    #----------------------------------------------
    # Get the RDK camera image
    image_rdk = None
    bytes_img = RDK.Cam2D_Snapshot("", cam_id)
    nparr = np.frombuffer(bytes_img, np.uint8)
    image_rdk = cv.imdecode(nparr, cv.IMREAD_COLOR)

    # Apply AR
    image = merge_img(image, image_rdk)

    #----------------------------------------------
    # Display the charuco board
    cv.imshow(preview_window, image)
    key = cv.waitKey(1)
    if key == 27:
        break  # User pressed ESC, exit
    if cv.getWindowProperty(preview_window, cv.WND_PROP_VISIBLE) < 1:
        break  # User killed the main window, exit

# Release the device
capture.release()
cv.destroyAllWindows()