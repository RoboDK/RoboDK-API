# This script allows you to take screen captures with high resolution


# Set the image size in pixels
# Larger sizes may depend on your graphic card
IMAGE_WIDTH  = 8000
IMAGE_HEIGHT = 6000

from robodk import *
from robolink import *
import datetime

from tkinter import *
from tkinter import filedialog

RDK = Robolink()

date_str = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
path_rdk = RDK.getParam('PATH_OPENSTATION')
file_name = "RoboDK-Screenshot-HQ-" + date_str + ".png"

root = Tk()
root.withdraw()
types = (("PNG files","*.png"),("JPEG files","*.jpg"),("All files","*.*"))
file_path = filedialog.asksaveasfilename(title = "Select image file to save", defaultextension = types, filetypes = types, initialdir=path_rdk, initialfile=file_name)
if not file_path:
    print("Operation cancelled")
    quit()


#RDK.Render(False) # prevent flickering

# Add a new reference frame at the camera view location
ref_cam = RDK.AddFrame("Camera Position")
ref_cam.setVisible(False)
ref_cam.setPose(RDK.ViewPose().inv()*rotx(pi))

# Turn auto render back on (otherwise we get a black view)
#RDK.Render(True)

# Create a new 2D camera view with high snapshot resolution, take a snapshot and close
# More information here: https://robodk.com/doc/en/PythonAPI/robolink.html#robolink.Robolink.Cam2D_Snapshot
cam_id = RDK.Cam2D_Add(ref_cam, "SNAPSHOT=%ix%i NO_TASKBAR" % (IMAGE_WIDTH, IMAGE_HEIGHT))
#cam_id = RDK.Cam2D_Add(ref_cam, "NEAR_LENGTH=5 FAR_LENGTH=100000 FOV=30 SNAPSHOT=%ix%i NO_TASKBAR BG_COLOR=black" % (IMAGE_WIDTH, IMAGE_HEIGHT))
RDK.Cam2D_Snapshot(file_path, cam_id)
RDK.Cam2D_Close(cam_id)

# Delete the temporary reference added
ref_cam.Delete()

print("Done")
RDK.ShowMessage("High resolution snapshot saved: " + file_path, False)




