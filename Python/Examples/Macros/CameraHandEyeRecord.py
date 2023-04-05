# Type help("robolink") or help("robodk") for more information
# Press F5 to run the script
# Documentation: https://robodk.com/doc/en/RoboDK-API.html
# Reference:     https://robodk.com/doc/en/PythonAPI/index.html
#
# Utility script to perform hand-eye calibration on a 2D camera.
# This script can be use for eye-in-hand or eye-to-hand calibrations.
# Dynamically record the robot pose and save the camera image on disk for later processing.
# This script is running in a separate thread and a main program request punctual recordings through an handshake.

from robodk import robolink  # RoboDK API
from robodk import robomath  # Robot toolbox

# Uncomment these lines to automatically install the dependencies using pip
# robolink.import_install('cv2', 'opencv-contrib-python==4.5.*')
# robolink.import_install('numpy')
import cv2 as cv
import numpy as np
from pathlib import Path
import json
from enum import Enum
import time


#--------------------------------------
# This script supports RoboDK virtual/simulated cameras, and USB devices (as supported by OpenCV)
# You can add your own implementation to retrieve images from any camera, such as a Cognex Insight, SICK, etc.
class CameraTypes(Enum):
    ROBODK_SIMULATED = 0
    OPENCV_USB = 1


RECORD_ROBOT = True  # Record the robot pose on disk
RECORD_CAMERA = True  # Record the camera image on disk
RECORD_FOLDER = 'Hand-Eye-Data'  # Default folder to save recordings, relative to the station folder

CAMERA_TYPE = CameraTypes.ROBODK_SIMULATED  # Camera type to be used
CAMERA_ROBODK_NAME = ''  # [Optional] Default name to use for the RoboDK camera
ROBOT_NAME = ''  # [Optional] Default name to use for the robot

# Station variables shared with the main program to interact with this script
RECORD_READY = 'RECORD_READY'  # Set this true in the main program when the robot is in position and the the script is allowed to record the robot and the image
RECORD_ACKNOWLEDGE = 'RECORD_ACKNOWLEDGE'  # Set this true in this script when the record is complete
RECORD_STOP = 'RECORD_STOP'  # Request to stop the script by the main program


#--------------------------------------
def get_robot(RDK: robolink.Robolink, robot_name: str):

    # Retrieve the robot
    robot_item = None
    if robot_name:
        robot_item = RDK.Item(robot_name, robolink.ITEM_TYPE_ROBOT)
        if not robot_item.Valid():
            robot_name = ''

    if not robot_name:
        robot_item = RDK.ItemUserPick("Select the robot for hand-eye", robolink.ITEM_TYPE_ROBOT)
        if not robot_item.Valid():
            raise

    return robot_item


def get_camera_handle(camera_type: CameraTypes, camera_name: str, RDK: robolink.Robolink):

    if camera_type == CameraTypes.ROBODK_SIMULATED:

        # Retrieve the RoboDK camera by name
        camera_item = None
        if camera_name:
            camera_item = RDK.Item(camera_name, robolink.ITEM_TYPE_CAMERA)
            if not camera_item.Valid():
                camera_name = ''

        if not camera_name:
            camera_item = RDK.ItemUserPick("Select the camera for hand-eye", robolink.ITEM_TYPE_CAMERA)
            if not camera_item.Valid():
                raise

        # Ensure the preview window in RoboDK is open
        if camera_item.setParam('Open') != '1':
            camera_item.setParam('Open', 1)
            robomath.pause(0.1)

        return camera_item

    elif camera_type == CameraTypes.OPENCV_USB:
        return cv.VideoCapture(0, cv.CAP_ANY)  # More information on supported devices here: https://docs.opencv.org/4.x/d8/dfe/classcv_1_1VideoCapture.html#aabce0d83aa0da9af802455e8cf5fd181

    return None


def record_camera(camera_type: CameraTypes, camera_handle, filename: str):
    if camera_type == CameraTypes.ROBODK_SIMULATED:
        record_robodk_camera(filename, camera_handle)

    elif camera_type == CameraTypes.OPENCV_USB:
        record_opencv_camera(filename, camera_handle)


def record_robodk_camera(filename: str, camera_item: robolink.Item):

    # Retrieve the image by socket
    bytes_img = camera_item.RDK().Cam2D_Snapshot('', camera_item)
    nparr = np.frombuffer(bytes_img, np.uint8)
    img = cv.imdecode(nparr, cv.IMREAD_COLOR)

    # Save the image on disk as a grayscale image
    cv.imwrite(filename, cv.cvtColor(img, cv.COLOR_RGB2GRAY))


def record_opencv_camera(filename: str, capture: cv.VideoCapture):

    # Retrieve image
    success, img = capture.read()
    if not success:
        raise

    # Save the image on disk as a grayscale image
    cv.imwrite(filename, cv.cvtColor(img, cv.COLOR_RGB2GRAY))


def record_robot(robot_item: robolink.Item, filename: str):

    # Retrieve the required information for hand-eye
    robot_data = {}
    robot_data['joints'] = robot_item.Joints().tolist()
    robot_data['pose_flange'] = robomath.Pose_2_TxyzRxyz(robot_item.SolveFK(robot_item.Joints()))

    # Save it on disk as a JSON
    # You can also provide another format, like YAML
    with open(filename, 'w') as f:
        json.dump(robot_data, f, indent=2)


def runmain():

    RDK = robolink.Robolink()

    # Retrieve the camera and robot
    camera_handle = get_camera_handle(CAMERA_TYPE, CAMERA_ROBODK_NAME, RDK)
    robot_item = get_robot(RDK, ROBOT_NAME)

    # Retrieve the folder to save the data
    record_folder = Path(RDK.getParam(robolink.PATH_OPENSTATION)) / RECORD_FOLDER
    record_folder.mkdir(exist_ok=True, parents=True)

    # This script does not delete the previous run if the folder is not empty
    # If the folder is not empty, retrieve the next ID
    id = 0
    ids = sorted([int(x.stem) for x in record_folder.glob('*.png') if x.stem.isdigit()])
    if ids:
        id = ids[-1] + 1

    # Start the main loop, and wait for requests
    RDK.setParam(RECORD_READY, 0)

    while True:
        time.sleep(0.01)

        # Read the requests set by the main program
        ready = int(RDK.getParam(RECORD_READY)) == 1
        stop = int(RDK.getParam(RECORD_STOP)) == 1
        if stop:
            break

        if not ready:
            continue

        # Process the requests
        if RECORD_CAMERA:
            img_filename = Path(f'{record_folder.as_posix()}/{id}.png')
            record_camera(CAMERA_TYPE, camera_handle, img_filename.as_posix())

        if RECORD_ROBOT:
            robot_filename = Path(f'{record_folder.as_posix()}/{id}.json')
            record_robot(robot_item, robot_filename.as_posix())

        id += 1

        # Inform the main program that we have completed the request
        RDK.setParam(RECORD_ACKNOWLEDGE, 1)
        RDK.setParam(RECORD_READY, 0)


if __name__ == '__main__':
    runmain()