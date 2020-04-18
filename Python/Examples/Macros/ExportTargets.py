# This macro exports all targets to a CSV file

# Type help("robolink") or help("robodk") for more information
# Press F5 to run the script
# Visit: http://www.robodk.com/doc/PythonAPI/
# For RoboDK API documentation
   
from robolink import *    # API to communicate with RoboDK
from robodk import *      # basic matrix operations

def getSaveFileName(path_preference="C:/RoboDK/Library/", strfile = 'file.txt', strtitle='Save file as ...', defaultextension='.txt', filetypes=[('All files', '.*'), ('Text files', '.txt')]):
    """Pop up a file dialog window to select a file to save. Returns the file path as a string."""
    options = {}
    options['initialdir'] = path_preference
    options['title'] = strtitle
    options['defaultextension'] = defaultextension #'.txt'
    options['filetypes'] = filetypes # [('all files', '.*'), ('text files', '.txt')]
    options['initialfile'] = strfile
    #options['parent'] = root
    root = tkinter.Tk()
    root.withdraw()
    root.attributes("-topmost", True)    
    file_path = filedialog.asksaveasfilename(**options)
    #same as: file_path = tkinter.filedialog.asksaveasfile(**options)
    return file_path


# Start communication with RoboDK
RDK = Robolink()

# Ask the user to select the robot (ignores the popup if only 
targets = RDK.ItemList(ITEM_TYPE_TARGET)

name_guess = "targets-" + RDK.ActiveStation().Name() + ".csv"

filepath = getSaveFileName(strfile=name_guess, defaultextension='.csv', filetypes=[('All files', '.*'), ('Text files', '.csv')])


f = open(filepath, 'w')
f.write('Name, X, Y, Z, Rx, Ry, Rz\n')

for target in targets:
    name = target.Name()
    x, y, z, rx, ry, rz = Pose_2_Staubli(target.Pose())
    f.write('%s, %.6f, %.6f, %.6f, %.6f, %.6f, %.6f\n' % (name, x, y, z, rx, ry, rz))

f.close()
    
RDK.ShowMessage("Saved %i targets" % len(targets), False)




