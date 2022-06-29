# Type help("robolink") or help("robodk") for more information
# Press F5 to run the script
# Documentation: https://robodk.com/doc/en/RoboDK-API.html
# Reference:     https://robodk.com/doc/en/PythonAPI/index.html
#
# This example shows how to retrieve both the RGB and Depth images to vizualize colorized point cloud in 3D using a simulated camera.
# It uses Open3D for converting the depth map to a point cloud and for vizualisation.
# Left-click the view to move the mesh in the viewer.

from robodk.robolink import *
import numpy as np
import open3d as o3d
import cv2 as cv

#----------------------------------
# You might need to play arround these settings depending on the object/setup
CAMERA_NAME = 'RGB-D Camera'
ANIMATE_OBJECT = True

#----------------------------------
# Get the simulated camera from RoboDK
RDK = Robolink()

cam_item = RDK.Item(CAMERA_NAME, ITEM_TYPE_CAMERA)
if not cam_item.Valid():
    cam_item = RDK.Cam2D_Add(RDK.ActiveStation())  # Do not set the DEPTH option here, as we are retrieving both RGB and DEPTH images
    cam_item.setName(CAMERA_NAME)
cam_item.setParam('Open', 1)

#----------------------------------
# Get the scanned object, to rotate it arround
obj_item = RDK.ItemUserPick(itemtype_or_list=ITEM_TYPE_OBJECT)
if not obj_item.Valid():
    obj_item = None


#----------------------------------
# Retrieve camera settings / camera matrix
def settings_to_dict(settings):
    if not settings:
        return {}

    settings_dict = {}
    settings_list = [setting.split('=') for setting in settings.strip().split(' ')]
    for setting in settings_list:
        key = setting[0].upper()
        val = setting[-1]

        if key in ['FOV', 'PIXELSIZE', 'FOCAL_LENGTH', 'FAR_LENGTH']:
            val = float(val)
        elif key in ['SIZE', 'ACTUALSIZE', 'SNAPSHOT']:
            w, h = val.split('x')
            val = (int(w), int(h))
        elif key == val.upper():
            val = True  # Flag

        settings_dict[key] = val

    return settings_dict


cam_settings = settings_to_dict(cam_item.setParam('Settings'))
w, h = cam_settings['SIZE']
fy = h / (2 * np.tan(np.radians(cam_settings['FOV']) / 2))

cam_params = o3d.camera.PinholeCameraParameters()
cam_params.intrinsic = o3d.camera.PinholeCameraIntrinsic(width=w, height=h, fx=fy, fy=fy, cx=w / 2, cy=h / 2)

#----------------------------------
# Initialize a non-blocking 3D viewer
vis = o3d.visualization.Visualizer()
vis.create_window("RoboDK RGB-D Viewer")
source = None

i = 0
while True:

    #----------------------------------------------
    # Get the RDB+D image from RoboDK

    # Get the RGB image
    rgb = None
    bytes_img = RDK.Cam2D_Snapshot("", cam_item)
    if not isinstance(bytes_img, bytes) or bytes_img == b'':
        continue
    nparr = np.frombuffer(bytes_img, np.uint8)
    rgb = cv.imdecode(nparr, cv.IMREAD_ANYCOLOR)
    rgb = cv.cvtColor(rgb, cv.COLOR_RGB2BGR)

    # Get the Depth image
    depth32 = None
    bytes_img = RDK.Cam2D_Snapshot("", cam_item, 'DEPTH')
    if not isinstance(bytes_img, bytes) or bytes_img == b'':
        continue
    depth32 = np.frombuffer(bytes_img, dtype='>u4')
    w, h = depth32[:2]
    depth32 = np.flipud(np.reshape(depth32[2:], (h, w))).astype(np.uint32)
    depth = (depth32 / np.iinfo(np.uint32).max) * cam_settings['FAR_LENGTH']
    depth = depth.astype(np.float32)

    rgbd_image = o3d.geometry.RGBDImage.create_from_color_and_depth(o3d.geometry.Image(rgb), o3d.geometry.Image(depth), convert_rgb_to_intensity=False)

    #----------------------------------------------
    # Convert to point cloud
    pcd = o3d.geometry.PointCloud.create_from_rgbd_image(rgbd_image, cam_params.intrinsic)
    pcd.transform([[1, 0, 0, 0], [0, -1, 0, 0], [0, 0, -1, 0], [0, 0, 0, 1]])

    #----------------------------------------------
    # Update the viewer
    if source is None:
        source = pcd
    else:
        source.points = pcd.points
        source.colors = pcd.colors

    if i == 0:
        vis.add_geometry(source, reset_bounding_box=True)
    else:
        vis.update_geometry(source)
        if not vis.poll_events():
            break
        vis.update_renderer()

    #----------------------------------------------
    # Rainbow color cycle and rotate the object
    if ANIMATE_OBJECT and obj_item:
        obj_item.setPose(obj_item.Pose() * robomath.rotz(0.05))

        import colorsys
        r, g, b = colorsys.hsv_to_rgb(i % 100 / 100, 1, 1)
        obj_item.setColor([r, g, b, 1])

    i += 1
