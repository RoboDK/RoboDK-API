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
# REMOVE BELOW after the adoption period
from . import robolink, robomath, robodialogs, robofileio
from .robomath import *
from .robodialogs import *
from .robofileio import *

# Inform our users of the changes
# Note: "from robodk import robomath" will trigger a warning while being perfectly valid.
#       PendingDeprecationWarning is ignored by the default filter (add the -Wd argument to Python to show all warnings).
s = '"from robodk import *" behavior has changed. You can instead use: "from robodk.robomath import *" or "from robodk import robomath, robodialogs, robofileio"'

from warnings import warn, simplefilter
#simplefilter('default') # Uncommenting this will force the warning to stderr.
warn(s, PendingDeprecationWarning)
#==================================

#==================================
# UNCOMMENT BELOW after the adoption period
#__all__ = ['robolink', 'robomath', 'robodialogs', 'robofileio']
#==================================