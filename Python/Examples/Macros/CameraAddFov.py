# Type help("robolink") or help("robodk") for more information
# Press F5 to run the script
# Documentation: https://robodk.com/doc/en/RoboDK-API.html
# Reference:     https://robodk.com/doc/en/PythonAPI/index.html
#
# This example shows how to create a RoboDK Shape to represent a camera's FoV
# and verify if an object is within that shape.
from robodk.robolink import Robolink, ITEM_TYPE_CAMERA, ITEM_TYPE_OBJECT
from robodk import robomath

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

# Retrieve cam settings to be used in FoV Shape Creation
w, h = cam_settings['SIZE']
focal_length = cam_settings['FOCAL_LENGTH']
pixel_size = cam_settings['PIXELSIZE']
camera_range = cam_settings['FAR_LENGTH']

# Creates cam FoV Shape using cam settings
HFOV = 2 * robomath.atan2((w * pixel_size / 1000.0), (2 * focal_length))
VFOV = 2 * robomath.atan2((h * pixel_size / 1000.0), (2 * focal_length))
fov_items = []
fov_items.append(RDK.AddShape([[0, 0, 0], [camera_range * robomath.tan(HFOV / 2), camera_range * robomath.tan(VFOV / 2), camera_range], [-camera_range * robomath.tan(HFOV / 2), camera_range * robomath.tan(VFOV / 2), camera_range]]))
fov_items.append(RDK.AddShape([[0, 0, 0], [-camera_range * robomath.tan(HFOV / 2), camera_range * robomath.tan(VFOV / 2), camera_range], [-camera_range * robomath.tan(HFOV / 2), -camera_range * robomath.tan(VFOV / 2), camera_range]]))
fov_items.append(RDK.AddShape([[0, 0, 0], [camera_range * robomath.tan(HFOV / 2), -camera_range * robomath.tan(VFOV / 2), camera_range], [camera_range * robomath.tan(HFOV / 2), camera_range * robomath.tan(VFOV / 2), camera_range]]))
fov_items.append(RDK.AddShape([[0, 0, 0], [-camera_range * robomath.tan(HFOV / 2), -camera_range * robomath.tan(VFOV / 2), camera_range], [camera_range * robomath.tan(HFOV / 2), -camera_range * robomath.tan(VFOV / 2), camera_range]]))
fov_items.append(RDK.AddShape([[-camera_range * robomath.tan(HFOV / 2), -camera_range * robomath.tan(VFOV / 2), camera_range], [camera_range * robomath.tan(HFOV / 2), -camera_range * robomath.tan(VFOV / 2), camera_range], [-camera_range * robomath.tan(HFOV / 2), camera_range * robomath.tan(VFOV / 2), camera_range]]))
fov_items.append(RDK.AddShape([[camera_range * robomath.tan(HFOV / 2), camera_range * robomath.tan(VFOV / 2), camera_range], [camera_range * robomath.tan(HFOV / 2), -camera_range * robomath.tan(VFOV / 2), camera_range], [-camera_range * robomath.tan(HFOV / 2), camera_range * robomath.tan(VFOV / 2), camera_range]]))

# Merges all created items into 1 shape
fov = RDK.MergeItems(fov_items)
fov.setName("Camera FoV")
fov.setParent(cam_item)
fov.setVisible(False)

# Select an existing object and verifies if the object is seen by the camera
obj_item = RDK.ItemUserPick(itemtype_or_list=ITEM_TYPE_OBJECT)
if not obj_item.Valid():
    obj_item = None

if obj_item is not None:
    obj_item.IsInside(fov)
