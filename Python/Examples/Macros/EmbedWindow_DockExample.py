from tkinter import *
from robolink import *
import threading    

# Create a new window
window = tkinter.Tk()

# Close the window
def onClose():
    window.destroy()
    quit(0)

# Trigger Select button
# IMPORTANT: We need to run the action on a separate thread because
# (otherwise, if we want to interact with RoboDK window it will freeze)
def on_btnSelect():
    def thread_btnSelect():
        # Run button action (example to select an item and display its name)
        RDK = Robolink()
        item = RDK.ItemUserPick('Select an item')
        if item.Valid():
            RDK.ShowMessage("You selected the item: " + item.Name())
        
    threading.Thread(target=thread_btnSelect).start()

# Set the window title (must be unique for the docking to work, try to be creative)
window_title = 'RoboDK API Docked Window'
window.title(window_title)

# Delete the window when we close it
window.protocol("WM_DELETE_WINDOW", onClose)

# Add a button (Select action)
btnSelect = Button(window, text='Trigger on_btnSelect', height=5, width=60, command=on_btnSelect)
btnSelect.pack(fill=X)

# Embed the window
EmbedWindow(window_title)

# Run the window event loop. This is like an app and will block until we close the window
window.mainloop()