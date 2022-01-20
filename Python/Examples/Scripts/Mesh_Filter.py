# This script removes small components of an object such as small shapes or small/invalid triangles
# Among other things, running this script can improve the speed and the numerical stability of collision checking

# Documentation: https://robodk.com/doc/en/RoboDK-API.html
# Reference:     https://robodk.com/doc/en/PythonAPI/index.html
# Note: It is not required to keep a copy of this file, your python script is saved with the station
from robodk.robolink import *  # RoboDK API

RDK = Robolink()

# Program example:
obj = RDK.ItemUserPick("Select an object to simplify its geometry")
result = obj.setParam("FilterMesh")
# Optionally provide the size threshold to delete elements as [shape radius (mm), triangle area (mm^2), angle (deg)]
#result = obj.setParam("FilterMesh", "1,1,1")
print(result)
RDK.ShowMessage(obj.Name() + ": " + result, False)

# Recalculate collisions:
#RDK.Collisions()
