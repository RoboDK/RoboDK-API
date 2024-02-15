# Type help("robolink") or help("robodk") for more information
# Press F5 to run the script
# Documentation: https://robodk.com/doc/en/RoboDK-API.html
# Reference:     https://robodk.com/doc/en/PythonAPI/index.html
#
# Perform hand-eye calibration with recorded robot poses and 2D images from disk.
# - Requires at least 8 different poses at different orientations/distances of a chessboard or charucoboard.
# - Requires a calibrated camera (known intrinsic parameters, including distortion), which can also be performed from local images.
#
# You can find the board used in this example here:
# https://docs.opencv.org/4.x/charucoboard.png
#

from robodk import robolink  # RoboDK API
from robodk import robomath  # Robot toolbox
from robodk import robodialogs  # Dialogs

# Uncomment these lines to automatically install the dependencies using pip
# robolink.import_install('cv2', 'opencv-contrib-python==4.5.*')
# robolink.import_install('numpy')
import cv2 as cv
import numpy as np
import json
from pathlib import Path
from enum import Enum


#--------------------------------------
# This scripts supports chessboard (checkerboard) and ChAruCo board as calibration objects.
# You can add your own implementation (such as dot patterns).
class MarkerTypes(Enum):
    CHESSBOARD = 0
    CHARUCOBOARD = 1


# The camera intrinsic parameters can be performed with the same board as the Hand-eye
INTRINSIC_FOLDER = 'Hand-Eye-Data'  # Default folder to load images for the camera calibration, relative to the station folder
HANDEYE_FOLDER = 'Hand-Eye-Data'  # Default folder to load robot poses and images for the hand-eye calibration, relative to the station folder

# Camera intrinsic calibration board parameters
# You can find this chessboard here: https://docs.opencv.org/4.x/charucoboard.png
INTRINSIC_BOARD_TYPE = MarkerTypes.CHESSBOARD
INTRINSIC_CHESS_SIZE = (5, 7)  # X/Y
INTRINSIC_SQUARE_SIZE = 35  # mm
INTRINSIC_MARKER_SIZE = 21  # mm

# Hand-eye calibration board parameters
# You can find this charucoboard here: https://docs.opencv.org/4.x/charucoboard.png
HANDEYE_BOARD_TYPE = MarkerTypes.CHARUCOBOARD
HANDEYE_CHESS_SIZE = (5, 7)  # X/Y
HANDEYE_SQUARE_SIZE = 35  # mm
HANDEYE_MARKER_SIZE = 21  # mm


def pose_2_Rt(pose: robomath.Mat):
    """RoboDK pose to OpenCV pose"""
    pose_inv = pose.inv()
    R = np.array(pose_inv.Rot33())
    t = np.array(pose.Pos())
    return R, t


def Rt_2_pose(R, t):
    """OpenCV pose to RoboDK pose"""
    vx, vy, vz = R.tolist()

    cam_pose = robomath.eye(4)
    cam_pose.setPos([0, 0, 0])
    cam_pose.setVX(vx)
    cam_pose.setVY(vy)
    cam_pose.setVZ(vz)

    pose = cam_pose.inv()
    pose.setPos(t.tolist())

    return pose


def find_chessboard(img, mtx, dist, chess_size, squares_edge, refine=True, draw_img=None):
    """
    Detects a chessboard pattern in an image.
    """

    pattern = np.subtract(chess_size, (1, 1))  # number of corners

    # Prefer grayscale images
    _img = img
    if len(img.shape) > 2:
        _img = cv.cvtColor(img, cv.COLOR_RGB2GRAY)

    # Find the chessboard's corners
    success, corners = cv.findChessboardCorners(_img, pattern)
    if not success:
        raise Exception("No chessboard found")

    # Refine
    if refine:
        criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        search_size = (11, 11)
        zero_size = (-1, -1)
        corners = cv.cornerSubPix(_img, corners, search_size, zero_size, criteria)

    if draw_img is not None:
        cv.drawChessboardCorners(draw_img, pattern, corners, success)

    # Find the camera pose. Only available with the camera matrix!
    if mtx is None or dist is None:
        return corners, None, None

    cb_corners = np.zeros((pattern[0] * pattern[1], 3), np.float32)
    cb_corners[:, :2] = np.mgrid[0:pattern[0], 0:pattern[1]].T.reshape(-1, 2) * squares_edge
    success, rvec, tvec = cv.solvePnP(cb_corners, corners, mtx, dist)
    if not success:
        raise Exception("No chessboard found")

    R_target2cam = cv.Rodrigues(rvec)[0]
    t_target2cam = tvec

    return corners, R_target2cam, t_target2cam


def find_charucoboard(img, mtx, dist, chess_size, squares_edge, markers_edge, predefined_dict=cv.aruco.DICT_6X6_100, draw_img=None):
    """
    Detects a charuco board pattern in an image.
    """

    # Note that for chessboards, the pattern size is the number of "inner corners", while charucoboards are the number of chessboard squares

    # Charuco board and dictionary
    charuco_board = cv.aruco.CharucoBoard_create(chess_size[0], chess_size[1], squares_edge, markers_edge, cv.aruco.getPredefinedDictionary(predefined_dict))
    charuco_dict = charuco_board.dictionary

    # Find the markers first
    marker_corners, marker_ids, _ = cv.aruco.detectMarkers(img, charuco_dict, None, None, None, None)
    if marker_ids is None or len(marker_ids) < 1:
        raise Exception("No charucoboard found")

    # Then the charuco
    count, corners, ids = cv.aruco.interpolateCornersCharuco(marker_corners, marker_ids, img, charuco_board, None, None, mtx, dist, 2)  # mtx and dist are optional here
    if count < 1 or len(ids) < 1:
        raise Exception("No charucoboard found")

    if draw_img is not None:
        cv.aruco.drawDetectedCornersCharuco(draw_img, corners, ids)

    # Find the camera pose. Only available with the camera matrix!
    if mtx is None or dist is None:
        return corners, None, None

    success, rot_vec, trans_vec = cv.aruco.estimatePoseCharucoBoard(corners, ids, charuco_board, mtx, dist, None, None, False)  # mtx and dist are mandatory here
    if not success:
        raise Exception("Charucoboard pose not found")

    if draw_img is not None:
        cv.drawFrameAxes(draw_img, mtx, dist, rot_vec, trans_vec, max(1.5 * squares_edge, 5))

    R_target2cam = cv.Rodrigues(rot_vec)[0]

    return corners, R_target2cam, trans_vec


def calibrate_static(chessboard_images, board_type: MarkerTypes, chess_size, squares_edge: float, markers_edge: float, min_detect: int = -1, show_images=False):
    """
    Calibrate a camera with a chessboard or charucoboard pattern.
    """
    # Chessboard parameters
    pattern = np.subtract(chess_size, (1, 1))  # number of corners
    img_size = None

    # Find the chessboard corners
    img_corners = []

    if show_images:
        WDW_NAME = 'Chessboard'
        MAX_W, MAX_H = 640, 480
        cv.namedWindow(WDW_NAME, cv.WINDOW_NORMAL)

    for file, img in chessboard_images.items():
        # Ensure the image size is consistent
        if img_size is None:
            img_size = img.shape[:2]
        else:
            if img.shape[:2] != img_size:
                raise Exception('Camera resolution is not consistent across images!')

        # Find the chessboard corners
        draw_img = None
        if show_images:
            draw_img = cv.cvtColor(img, cv.COLOR_GRAY2RGB)
        try:
            if board_type == MarkerTypes.CHESSBOARD:
                corners, _, _ = find_chessboard(img, mtx=None, dist=None, chess_size=chess_size, squares_edge=squares_edge, draw_img=draw_img)
            else:
                corners, _, _ = find_charucoboard(img, mtx=None, dist=None, chess_size=chess_size, squares_edge=squares_edge, markers_edge=markers_edge, draw_img=draw_img)
        except:
            print(f'Unable to find chessboard in {file}!')
            continue

        if show_images:
            cv.imshow(WDW_NAME, draw_img)
            cv.resizeWindow(WDW_NAME, MAX_W, MAX_H)
            cv.waitKey(500)
        img_corners.append(corners)

        # Check if we processed enough images
        if min_detect > 0 and len(img_corners) >= min_detect:
            break

    if show_images:
        cv.destroyAllWindows()

    if len(img_corners) < 3 or min_detect > 0 and len(img_corners) < min_detect:
        raise Exception('Not enough detections!')

    # Calibrate the camera
    # Create a flat chessboard representation of the corners
    cb_corners = np.zeros((pattern[0] * pattern[1], 3), np.float32)
    cb_corners[:, :2] = np.mgrid[0:pattern[0], 0:pattern[1]].T.reshape(-1, 2) * squares_edge

    h, w = img_size
    rms_err, mtx, dist, rot_vecs, trans_vecs = cv.calibrateCamera([cb_corners for i in range(len(img_corners))], img_corners, (w, h), None, None)
    return mtx, dist, (w, h)


def calibrate_handeye(robot_poses, chessboard_images, camera_matrix, camera_distortion, board_type: MarkerTypes, chess_size, squares_edge: float, markers_edge: float, show_images=False):
    """
    Calibrate a camera mounted on a robot arm using a list of robot poses and a list of images for each pose.
    The robot pose should be at the flange (remove .PoseTool) unless you have a calibrated tool.
    """
    # https://docs.opencv.org/4.x/d9/d0c/group__calib3d.html#gaebfc1c9f7434196a374c382abf43439b

    # Rotation part extracted from the homogeneous matrix that transforms a point expressed in the gripper frame to the robot base frame (bTg).
    # This is a vector (vector<Mat>) that contains the rotation, (3x3) rotation matrices or (3x1) rotation vectors, for all the transformations from gripper frame to robot base frame.
    R_gripper2base_list = []

    # Translation part extracted from the homogeneous matrix that transforms a point expressed in the gripper frame to the robot base frame (bTg).
    # This is a vector (vector<Mat>) that contains the (3x1) translation vectors for all the transformations from gripper frame to robot base frame.
    t_gripper2base_list = []

    # Rotation part extracted from the homogeneous matrix that transforms a point expressed in the target frame to the camera frame (cTt).
    # This is a vector (vector<Mat>) that contains the rotation, (3x3) rotation matrices or (3x1) rotation vectors, for all the transformations from calibration target frame to camera frame.
    R_target2cam_list = []

    # Rotation part extracted from the homogeneous matrix that transforms a point expressed in the target frame to the camera frame (cTt).
    # This is a vector (vector<Mat>) that contains the (3x1) translation vectors for all the transformations from calibration target frame to camera frame.
    t_target2cam_list = []

    if show_images:
        WDW_NAME = 'Charucoboard'
        MAX_W, MAX_H = 640, 480
        cv.namedWindow(WDW_NAME, cv.WINDOW_NORMAL)

    for i in chessboard_images.keys():
        robot_pose = robot_poses[i]
        image = chessboard_images[i]
        draw_img = None
        if show_images:
            draw_img = cv.cvtColor(image, cv.COLOR_GRAY2RGB)
        try:
            if board_type == MarkerTypes.CHESSBOARD:
                _, R_target2cam, t_target2cam = find_chessboard(image, camera_matrix, camera_distortion, chess_size, squares_edge, draw_img=draw_img)
            else:
                _, R_target2cam, t_target2cam = find_charucoboard(image, camera_matrix, camera_distortion, chess_size, squares_edge, markers_edge, draw_img=draw_img)
        except:
            print(f'Unable to find chessboard in {i}!')
            continue

        if show_images:
            cv.imshow(WDW_NAME, draw_img)
            cv.resizeWindow(WDW_NAME, MAX_W, MAX_H)
            cv.waitKey(500)

        R_target2cam_list.append(R_target2cam)
        t_target2cam_list.append(t_target2cam)

        R_gripper2base, t_gripper2base = pose_2_Rt(robot_pose)
        R_gripper2base_list.append(R_gripper2base)
        t_gripper2base_list.append(t_gripper2base)

    if show_images:
        cv.destroyAllWindows()

    R_cam2gripper, t_cam2gripper = cv.calibrateHandEye(R_gripper2base_list, t_gripper2base_list, R_target2cam_list, t_target2cam_list)
    return Rt_2_pose(R_cam2gripper, t_cam2gripper)


def runmain():
    #------------------------------------------------------
    # Calibrate the camera intrinsic parameters
    # 1. Print a chessboard, measure it using a caliper
    # 2. Mount the camera statically, take a series of images of the chessboard at different distance, orientation, offset, etc.
    # 3. Calibrate the camera using the images (can be done offline)
    #
    #
    # Calibrate the camera location (hand-eye)
    # 4. Create a robot program in RoboDK that moves the robot around a static chessboard at different distance, orientation, offset, etc.
    # 5. At each position, record the robot pose (robot.Pose(), or robot.Joints() even) and take a screenshot with the camera
    # 6. Use the robot poses and the images to calibrate the camera location
    #
    #
    # Good to know
    # - You can retrieve the camera image live with OpenCV using cv.VideoCapture(0, cv.CAP_DSHOW)
    # - You can load/save images with OpenCV using cv.imread(filename) and cv.imwrite(filename, img)
    # - You can save your calibrated camera parameters with JSON, i.e. print(json.dumps({"mtx":mtx, "dist":dist}))
    #
    #------------------------------------------------------

    RDK = robolink.Robolink()

    #------------------------------------------------------
    # Calibrate a camera using local images of chessboards, retrieves the camera intrinsic parameters
    # Get the input folder
    intrinsic_folder = Path(RDK.getParam(robolink.PATH_OPENSTATION)) / INTRINSIC_FOLDER
    if not intrinsic_folder.exists():
        intrinsic_folder = robodialogs.getSaveFolder(intrinsic_folder.as_posix(), 'Select the directory containing the images (.png) for the camera intrinsic calibration')
        if not intrinsic_folder:
            raise
        intrinsic_folder = Path(intrinsic_folder)

    # Retrieve the images
    image_files = sorted(intrinsic_folder.glob('*.png'))
    images = {int(image_file.stem): cv.imread(image_file.as_posix(), cv.IMREAD_GRAYSCALE) for image_file in image_files}

    # Perform the image calibration
    mtx, dist, size = calibrate_static(images, INTRINSIC_BOARD_TYPE, INTRINSIC_CHESS_SIZE, INTRINSIC_SQUARE_SIZE, INTRINSIC_MARKER_SIZE, min_detect=-1)
    print(f'Camera matrix:\n{mtx}\n')
    print(f'Distortion coefficient:\n{dist}\n')
    print(f'Camera resolution:\n{size}\n')

    #------------------------------------------------------
    # Load images and robot poses to calibrate hand-eye camera
    # Get the input folder
    handeye_folder = Path(RDK.getParam(robolink.PATH_OPENSTATION)) / HANDEYE_FOLDER
    if not handeye_folder.exists():
        handeye_folder = robodialogs.getSaveFolder('Select the directory of the images (.png) and robot poses (.json) for hand-eye calibration')
        if not handeye_folder:
            raise
        handeye_folder = Path(handeye_folder)

    # Retrieve the images and robot poses
    image_files = sorted(handeye_folder.glob('*.png'))
    robot_files = sorted(handeye_folder.glob('*.json'))

    images, poses, joints = {}, {}, {}
    for image_file, robot_file in zip(image_files, robot_files):
        if int(image_file.stem) != int(robot_file.stem):
            raise

        id = int(image_file.stem)

        image = cv.imread(image_file.as_posix(), cv.IMREAD_GRAYSCALE)
        images[id] = image

        with open(robot_file.as_posix(), 'r') as f:
            robot_data = json.load(f)
            joints[id] = robot_data['joints']
            poses[id] = robomath.TxyzRxyz_2_Pose(robot_data['pose_flange'])

    # Perform hand-eye calibration
    camera_pose = calibrate_handeye(poses, images, mtx, dist, HANDEYE_BOARD_TYPE, HANDEYE_CHESS_SIZE, HANDEYE_SQUARE_SIZE, HANDEYE_MARKER_SIZE)
    print(f'Camera pose (wrt to the robot flange):\n{camera_pose}')

    RDK.ShowMessage('Hand-Eye location:\n' + str(camera_pose))

    #------------------------------------------------------
    # In RoboDK, set the camera location wrt to the robot flange at that calibrated hand-eye location (use a .tool)
    tool = RDK.ItemUserPick('Select the "eye" tool to calibrate', RDK.ItemList(robolink.ITEM_TYPE_TOOL))
    if tool.Valid():
        tool.setPoseTool(camera_pose)


if __name__ == '__main__':
    runmain()