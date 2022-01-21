# Below is to support the legacy robodk/robolink modules importation:
#
# from robolink import *
# from robodk import *
# 
# is now any of:
#
# Option #1
# from robodk import robolink, robomath
# RDK = robolink.Robolink()
# pose = robomath.eye()
#
# Option #2
# from robodk.robolink import Robolink
# from robodk.robomath import eye
# RDK = Robolink()
# pose = eye()
#
# Option #3
# from robodk.robolink import *
# from robodk.robomath import *
# RDK = Robolink()
# pose = eye()

#==================================
# REMOVE THIS ENTIRE FOLDER after the adoption period
import sys
from robodk import robolink
sys.modules['robolink'] = robolink

# Inform our users of the changes
# Note: All calls using robolink are deprecated.
#       For that reason, we use UserWarning over PendingDeprecationWarning so that it always prints (add the -Wd argument to Python to show all warnings).
s = '"from robolink import *" is deprecated. You can instead use: "from robodk.robolink import *" or "from robodk import robolink"'

from warnings import warn, simplefilter
#simplefilter('default') # Uncommenting this will force the warning to stderr.
warn(s, UserWarning)
#==================================