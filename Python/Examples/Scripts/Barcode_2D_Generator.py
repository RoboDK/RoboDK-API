# Type help("robolink") or help("robodk") for more information
# Press F5 to run the script
# Documentation: https://robodk.com/doc/en/RoboDK-API.html
# Reference:     https://robodk.com/doc/en/PythonAPI/index.html
#
# This script allows you to create a RoboDK object containing a QR code.

from robolink import *  # RoboDK API
from robodk import *  # Robot toolbox

import_install("qrcode")
import qrcode

#----------------------------------------------
# Settings
ASK_USER_SAVE_TO_DISK = False  # True to ask the user to save on disk. Otherwise, uses temp folder and add to RoboDK.

#----------------------------------------------
# Create the QR code
data = mbox("Enter the text to embed in your QR code", entry="robodk.com")
if data is None or data is False or type(data) is not str:
    # User cancelled
    quit()
img = qrcode.make(data)

#----------------------------------------------
# Save to file
name = "QR_" + data.replace('.', '').replace(':', '').replace('/', '')  # https://robodk.com/doc/en/PythonAPI/index.html

filename = None
if ASK_USER_SAVE_TO_DISK:
    filename = getSaveFileName(strtitle='Save QR on disk, or cancel to skip', strfile=name, defaultextension='.png', filetypes=[('PNG files', '*.png')])
if filename is None or filename == '':
    import_install("tempdir")
    import tempfile
    tempdir = tempfile.gettempdir()
    filename = tempdir + "\\" + name + ".png"

img.save(filename)

import os.path
if not os.path.exists(filename):
    quit(-1)

#----------------------------------------------
# Import in RoboDK
RDK = Robolink()
img_item = RDK.AddFile(filename)
if not img_item.Valid():
    quit(-1)