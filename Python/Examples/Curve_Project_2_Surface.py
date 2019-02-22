# This example takes 2 objects:
# 1 - Object with features (curves and/or points)
# 2 - Object with surface (additional features are ignored)
# This example projects the features (points/curves) to the reference surface and calculates the normals to the surface

from robolink import *    # RoboDK API
from robodk import *      # Robot toolbox
RDK = Robolink()

# Set to True to invert the normals (flip the normals)
FlipNormals = False

# Set the type of projection
ProjectionType = PROJECTION_RECALC
# Available values include:
#PROJECTION_NONE                = 0 # No curve projection
#PROJECTION_CLOSEST             = 1 # The projection will be the closest point on the surface
#PROJECTION_ALONG_NORMAL        = 2 # The projection will be done along the normal.
#PROJECTION_ALONG_NORMAL_RECALC = 3 # The projection will be done along the normal. Furthermore, the normal will be recalculated according to the surface normal.
#PROJECTION_CLOSEST_RECALC      = 4 # The projection will be the closest point on the surface and the normals will be recalculated
#PROJECTION_RECALC              = 5 # The normals are recalculated according to the surface normal of the closest projection

#-------------------------------------------------------------
# Ask the user to provide the object with the features
object_features = RDK.ItemUserPick("Select object with the features to project (curves and/or points)", ITEM_TYPE_OBJECT)
if not object_features.Valid():
    quit()

# Ask the user to provide the object with the surface used as a reference
object_surface = RDK.ItemUserPick("Select Surface Object to project features", ITEM_TYPE_OBJECT)
if not object_surface.Valid():
    quit()

# Create a duplicate copy of the surface object
object_surface.Copy()
new_object = RDK.Paste(object_surface.Parent())
new_object.setName("Recalculated Normals")
new_object.setVisible(True)

# Hide the objects used to build the new object with the desired curves
object_features.setVisible(False)
object_surface.setVisible(False)

# Turn Off rendering (faster)
RDK.Render(False)

# Add all curves, projected as desired (iterate through all curves until no more curves are found)
curve_id = 0
while True:
    # Retrieve the curve points
    curve_points, name_feature = object_features.GetPoints(FEATURE_CURVE, curve_id)
    print(name_feature)
    curve_id = curve_id + 1
    npoints = len(curve_points)
    if npoints == 0:
        break

    print("Adding curve %s with %i points" % (name_feature, npoints))
    curve_points_proj = RDK.ProjectPoints(curve_points, object_surface, ProjectionType)

    # Optionally flip the normals (ijk vector)
    if FlipNormals:
        for ci in range(len(curve_points_proj)):
            x,y,z,i,j,k = curve_points_proj[ci]
            curve_points_proj[ci] = [x,y,z,-i,-j,-k]

    RDK.AddCurve(curve_points_proj, new_object, True, PROJECTION_NONE)

# Add all points, projected as desired
point_list, name_feature = object_features.GetPoints(FEATURE_POINT, curve_id)
npoints = len(curve_points)
print("Adding %i points" % npoints)
if npoints > 0:    
    #RDK.AddPoints(point_list, new_object, True, PROJECTION_ALONG_NORMAL_RECALC)
    curve_points = RDK.ProjectPoints(curve_points, object_surface, ProjectionType)
    RDK.AddCurve(curve_points, new_object, True, PROJECTION_NONE)

# Set the curve width
new_object.setValue('DISPLAY','LINEW=2')
# Set the curve color
new_object.setColorCurve([0.0,0.5,0.5])

# Turn On rendering (Optional)
RDK.Render(True)
print("Done")
