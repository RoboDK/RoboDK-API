# This macro shows how to change the approach/retract settings for a robot machining project
from robolink import *
from robodk import *

# Ask the user to select a robot machining project
RDK = Robolink()
m = RDK.ItemUserPick('Select a robot machining project to change approach/retract', ITEM_TYPE_MACHINING)
if not m.Valid():
    raise Exception("Add a robot machining project, curve follow or point follow")

# Units are in mm and degrees

# Apply a tangency approach (mm)
m.setParam("Approach", "Tangent 100")
m.setParam("Retract", "Tangent 100")
m.setParam("UpdatePath")

pause(1)

# Apply a normal approach (mm)
m.setParam("Approach", "Normal 100")
m.setParam("UpdatePath")

pause(1)

# Apply a normal approach/retract of 100 mm
m.setParam("ApproachRetract", "Normal 250")
m.setParam("UpdatePath")

pause(1)

# Apply a side approach (mm)
m.setParam("Retract", "Side 100")
m.setParam("UpdatePath")

pause(1)

# Apply an XYZ approach tangency approach
m.setParam("Approach", "XYZ 50 60 70")
m.setParam("UpdatePath")

pause(1)

# Apply an NTS approach tangency approach
m.setParam("Approach", "NTS 50 60 70")
m.setParam("UpdatePath")

pause(1)

# Apply a normal arc approach (diameter in mm and arc in deg)
m.setParam("ApproachRetract", "ArcN 50 100")
m.setParam("UpdatePath")

pause(1)

# Apply a side arc approach (diameter in mm and arc in deg)
m.setParam("Approach", "ArcS 50 100")
m.setParam("UpdatePath")
