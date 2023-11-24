# Offset the curve of an object along the normal by iteratively checking collisions against another object until no collisions are found.
# For example: if we are going to perform a sanding operation we can model the sander as a round disk to check collisions against the part and iteratively offset each curve point
# When running this script you should select:
# 1 - Object with features (curves and/or points)
# 2 - Object with the collision surface

from robodk import robolink, robomath  

# Set to True to invert the normals (flip the normals)
FLIP_NORMALS = False

# delta offset in mm
DELTAZ_OFFSET = 1

# MAximum offset to apply to a point of the curve (in mm)
MAX_DELTAZ_OFFSET = 500

# Display each step of the iterative search
# (set to True to visualize the iterative search for non colliding state for each point)
# Obtain faster results by setting it to False
RENDER_ITERATIONS = True

#--------------------------------
# Start the RoboDK API
RDK = robolink.Robolink()
RDK.setSelection([])

OFFSET_DIR = +1.0
if FLIP_NORMALS:
    OFFSET_DIR = -1.0

#-------------------------------------------------------------
# Ask the user to provide the object with the features
object_features = RDK.ItemUserPick("Select object with the curves to offset ", robolink.ITEM_TYPE_OBJECT)
if not object_features.Valid():
    quit()

# Ask the user to provide the object with the surface used as a reference
object_collision = RDK.ItemUserPick("Select the object used for collision checking", robolink.ITEM_TYPE_OBJECT)
if not object_collision.Valid():
    quit()

object_collision.setVisible(True)

# Create a clean duplicate copy of the object with curves
object_features.Copy()
new_object = RDK.Paste(object_features.Parent())
new_object.setName(object_features.Name() + " Offset")
new_object.setVisible(True)
new_object.setParam("Clear", "Curve,Point")

# Hide the objects used to build the new object with the desired curves
object_features.setVisible(False)

# Turn Off rendering (faster)
RDK.Render(False)

# Iterate through each curve
curve_id = 0
while True:
    # Retrieve the curve points
    curve_points, name_feature = object_features.GetPoints(robolink.FEATURE_CURVE, curve_id)
    curve_id = curve_id + 1
    npoints = len(curve_points)
    if npoints == 0:
        break

    print("Processing curve %s with %i points" % (name_feature, npoints))
    curve_points_new = []
    for ci, xyzijk in enumerate(curve_points):
        x, y, z, i, j, k = xyzijk
        point = [x,y,z]
        point_orig = point
        Zaxis = [i,j,k]
        i = 0
        while True:
            offset = DELTAZ_OFFSET * i
            if offset > MAX_DELTAZ_OFFSET:
                from robodk import robodialogs
                robodialogs.ShowMessage("Offset larger than tolerance for point %i-%i ignoring this point" % (curve_id, ci))
                break

            point = robomath.add3( point_orig, robomath.mult3(Zaxis, OFFSET_DIR * offset) )
            pose = robomath.point_Zaxis_2_pose(point, Zaxis)
            object_collision.setPose(pose)
            if RENDER_ITERATIONS:
                RDK.Render()
            else:
                RDK.Update()

            if RDK.Collision(new_object, object_collision) == 0:
                break

            print("Increasing height of point %i-%i (current offset=%.1f mm)" % (curve_id, ci, offset))
            i = i + 1

        x,y,z = point
        i,j,k = Zaxis
        curve_points_new.append([x, y, z, i, j, k])

    RDK.AddCurve(curve_points_new, new_object, True, robolink.PROJECTION_NONE)

# Set the curve width and collor
new_object.setValue('DISPLAY', 'LINEW=2')
new_object.setColorCurve([0.0, 0.5, 0.5])

# Hide the object used for collisions
object_collision.setVisible(False)

# Auto update curve follow projects:
#for milling in RDK.ItemList(robolink.ITEM_TYPE_MACHINING):
#    if milling.getLink(robolink.ITEM_TYPE_OBJECT) == object_features:
#        milling.setLink(new_object)

print("Done")
