# Type help("robolink") or help("robodk") for more information
# Press F5 to run the script
# Documentation: https://robodk.com/doc/en/RoboDK-API.html
# Reference:     https://robodk.com/doc/en/PythonAPI/index.html
#
# This script allows you to create a RoboDK object containing a EAN13 bar code (European).

from robodk.robolink import *  # RoboDK API
from robodk.robodialogs import *

import_install("barcode", "python-barcode")
import barcode

#----------------------------------------------
# Settings
ASK_USER_SAVE_TO_DISK = False  # True to ask the user to save on disk. Otherwise, uses temp folder and add to RoboDK.

#----------------------------------------------
# Create the bar code
data = mbox("Enter your bar code (EAN 13 digits)", entry='5701234567899')
if data is None or data is False or type(data) is not str:
    # User cancelled
    quit()
if not data.isdecimal() or len(data) != 13:
    # Invalid input
    quit()
img = barcode.EAN13(data, writer=barcode.writer.ImageWriter())

# You can easily copy this script to generate other bar codes type, such as UPC-A
#img = barcode.UPCA(data, writer=barcode.writer.ImageWriter())

#----------------------------------------------
# Save to file
name = "EAN13_" + data.replace('.', '').replace(':', '').replace('/', '')

filename = None
if ASK_USER_SAVE_TO_DISK:
    filename = getSaveFileName(strtitle='Save bar code on disk, or cancel to skip', strfile=name, defaultextension='.png', filetypes=[('PNG files', '*.png')])
if filename is None or filename == '':
    import_install("tempdir")
    import tempfile
    tempdir = tempfile.gettempdir()
    filename = tempdir + "\\" + name

img.save(filename)

filename += '.png'  # barcode .save adds the .png
import os.path
if not os.path.exists(filename):
    quit(-1)

#----------------------------------------------
# Import in RoboDK
RDK = Robolink()
img_item = RDK.AddFile(filename)
if not img_item.Valid():
    quit(-1)