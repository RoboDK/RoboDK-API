# This example will convert an object containing points and normals as lines to a new object with points and normals.
# Importat: Each point must have a line describing the normal coming from the point (or arriving to)
# The first and last points are used to calculate the normal
# The tolerance to match a point with a line is 0.001 mm
#
# Set to True to invert the normals (flip the normals)
FlipNormals = True

from robolink import *  # RoboDK API
from robodk import *  # Robot toolbox

RDK = Robolink()

# Ask the user to provide the object with the geometry (points and curves)
object_original = RDK.ItemUserPick("Select object with points and lines", ITEM_TYPE_OBJECT)
if not object_original.Valid():
    quit()

# Turn Off rendering (faster)
RDK.Render(False)

# Collect all curves
CurveList = []
curve_id = 0
while True:
    # Retrieve the curve points
    curve_points, name_feature = object_original.GetPoints(FEATURE_CURVE, curve_id)
    print(name_feature)
    curve_id = curve_id + 1
    npoints = len(curve_points)
    if npoints == 0:
        break

    print("Using curve %s with %i points" % (name_feature, npoints))
    CurveList.append(curve_points)

# Collect all points
PointList, name_feature = object_original.GetPoints(FEATURE_POINT)
npoints = len(PointList)
print("Using %i points" % npoints)

# For each point, calculate IJK
point_xyzijk_list = []
tolerance = 0.001
for pt in PointList:
    x, y, z = pt[:3]
    ijk = None
    for curve in CurveList:
        pCurveFirst = curve[0]
        pCurveLast = curve[-1]
        if norm(subs3(pt, pCurveFirst)) < tolerance:
            ijk = normalize3(subs3(pCurveLast, pCurveFirst))
            break
        elif norm(subs3(pt, pCurveLast)) < tolerance:
            ijk = normalize3(subs3(pCurveFirst, pCurveLast))
            break

    if ijk is None:
        RDK.ShowMessage("Warning: Point %s does not have a normal line" % str(pt), False)
        continue

    # Add xyzijk coordinates to point
    if FlipNormals:
        ijk = mult3(ijk, -1)
    i, j, k = ijk
    point_xyzijk_list.append([x, y, z, i, j, k])

if len(point_xyzijk_list) == 0:
    RDK.ShowMessage("No points found")
    quit(0)

# Create new object in the RoboDK tree attached to the same coordinate system
object_points = RDK.AddPoints(point_xyzijk_list, None, True, PROJECTION_NONE)
object_points.setName(object_original.Name() + "-PointNormals")
object_points.setParent(object_original.Parent())

# Set the curve width
#object_points.setValue('DISPLAY','LINEW=2') # for lines
object_points.setValue('DISPLAY', 'Particle=Sphere(5,12) Color=#22999955')
# Set the curve color
#object_points.setColorCurve([0.0,0.5,0.5])

object_original.setVisible(False)

# Turn On rendering (Optional)
RDK.Render(True)
print("Done")
