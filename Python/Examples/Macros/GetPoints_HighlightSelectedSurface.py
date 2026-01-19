# This example shows how to get a custom geometry selection by the user. It uses GetPoints and creates a new surfaces that highlights the selected object.
# You can also use best fitting algorithms provided by RoboDK to know what type of geometry was selected.

# Start the RoboDK API
from robodk import robolink    # RoboDK API
from robodk import robomath    # Robot toolbox
import time
RDK = robolink.Robolink()

# Use an empty and hidden object to hold selected geometry
obj_highlight = RDK.AddFile("")
obj_highlight.setName("API Object to highlight selection")
obj_highlight.setParam("Tree", "Hide") # Hide the object from the user (this won't be seen in the tree or saved)
obj_highlight.setParam("Clear", "SurfPointCurve") # Example to clear the object container items, including everything (surfaces, curves, points)

def FitGeometry(mesh):
    geo_types = ['Unknown', 'Plane', 'Cylinder', 'Sphere', 'Line', 'Point']
    
    # Convert the triangle mesh to a Mat object and trigger the best fitting algorithm provided by RoboDK API
    points_mat = robomath.Mat(mesh)[:, :3].tr()
    geometry = RDK.Command("FitGeometry", points_mat)
    
    # Retrieve the result
    g_data_list = geometry[0].list()
    if len(g_data_list) == 0:
        return None

    if len(g_data_list) < 9:
        return None

    g_data = {}
    g_data["type"] = geo_types[int(g_data_list[0])]
    g_data["point"] = tuple(g_data_list[1:4])  # Point on plane or point on cylinder axis (typically center point)    
    g_data["axis"] = tuple(g_data_list[4:7])  # Plane normal or cylinder axis
    if True:
        # It should be normalized already, but just in case
        g_data["axis"] = robomath.normalize3(g_data["axis"])
        
    g_data["mean_err"] = float(g_data_list[7])
    g_data["max_err"] = float(g_data_list[8])
    if len(g_data_list) > 9:
        g_data["radius"] = float(g_data_list[9])

    return g_data

# Infinite loop to print the item under the mouse cursor
while True:
    #obj, feature_type, feature_id, feature_name, points = RDK.GetPoints(FEATURE_HOVER_OBJECT) # Faster if you don't need the mesh
    obj, feature_type, feature_id, feature_name, points = RDK.GetPoints(robolink.FEATURE_HOVER_OBJECT_MESH)
    
    if obj.Valid():
        print("Mouse on: " + obj.Name() + ": " + feature_name + " Type/id=" + str(feature_type) + "/" + str(feature_id) + ". Click a surface to highlight and get more info")
        
        if feature_type != robolink.FEATURE_SURFACE:
            continue
                    
        if obj in RDK.Selection():
            print("OBject selected!")
            # RDK.Selection() # returns the current selection
            RDK.setSelection([]) # Clear selection
            
            # Reset the geometry of the object to highlight
            obj_highlight.setParam("Clear", "SurfPointCurve") # Example to clear the object geometry
            
            # Add the points to the highlighted object
            obj_highlight.AddShape(points)

            # Attach it to the same coordinate system
            obj_highlight.setParent(obj)
            # idx = int(obj_highlight.setParam("Count", "Surf"))
            idx = 1
            # print("Number of surfaces: " + str(idx)) # Should be one if we only used AddShape once
            
            if True:
                # Best fit the selected geometry to a type of geometry (plane, cylinder, sphere, etc)
                geometry = FitGeometry(points)
                print("Current geometry selected")
                print(geometry)
            
            # Color is defined as AARRGGBB (Alpha-Red-Green-Blue)
            # Pro trick: set the alpha to less than 50% to have some transparency for the following reasons:
            #   1. RoboDK renders transparent objects first.
            #   2. We can not click through objects with less than 50% of transparency, this allows us to click the objects of the cell and not our highlighted objects
            color = "#7e00ff00"
            print("Setting color of selected surface to: " + color)
            result = obj_highlight.setParam("Color", color + " " + str(idx-1))            

    else:
        print("Nothing under the mouse cursor")

    time.sleep(0.1)