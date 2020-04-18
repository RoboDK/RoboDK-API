# This script allows you to take snapshots

from robodk import *
from robolink import *
import datetime

from tkinter import *
from tkinter import filedialog


RDK = Robolink()

date_str = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
path_rdk = RDK.getParam('PATH_OPENSTATION')
file_name = "ScreenShot_" + date_str + ".png"

root = Tk()
root.withdraw()
types = (("PNG files","*.png"),("All files","*.*"))
fname = filedialog.asksaveasfile(title = "Select file to save", defaultextension = types, filetypes = types, initialdir=path_rdk, initialfile=file_name)
if fname is None:
    quit()
    
file_path = fname.name

print("Saving image to: " + file_path)

cmd = "Snapshot"
#cmd = "SnapshotWhite" # Snapshot with white background
#cmd = "SnapshotWhiteNoTextNoFrames" # Snapshot with white background, no text or coordinate systems


returned = RDK.Command(cmd, file_path)
print(returned)
RDK.ShowMessage("Snapshot saved: " + file_path, False)




