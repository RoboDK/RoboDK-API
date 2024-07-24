# This example shows how to use GetPoints by creating new surfaces as we select the features of an existing object

# Start the RoboDK API
from robodk import robolink    # RoboDK API
from robodk import robomath    # Robot toolbox
import os
RDK = robolink.Robolink()

# Forward and backwards compatible use of the RoboDK API:
# Remove these 2 lines to follow python programming guidelines
from robodk import *      # RoboDK API
from robolink import *    # Robot toolbox
# Link to RoboDK
# RDK = Robolink()

# Use an empty object to hold 
obj_highlight = None
obj_highlight = RDK.AddFile("")
obj_highlight.setName("API Object to highlight selection")
# obj_highlight.setParam("Tree", "Hide") # Hide the object from the user
obj_highlight.setParam("Clear", "SurfPointCurve") # Example to clear the object container items, including everything (surfaces, curves, points)

# Infinite loop to print the item under the mouse cursor
while True:
    #obj, feature_type, feature_id, feature_name, points = RDK.GetPoints(FEATURE_HOVER_OBJECT) # Faster if you don't need the mesh
    obj, feature_type, feature_id, feature_name, points = RDK.GetPoints(FEATURE_HOVER_OBJECT_MESH)
    
    if obj.Valid():
        print("Mouse on: " + obj.Name() + ": " + feature_name + " Type/id=" + str(feature_type) + "/" + str(feature_id))
        
        if feature_type != FEATURE_SURFACE:
            continue
                    
        if obj in RDK.Selection():
            print("Object surface is selected!")
            # RDK.Selection() # returns the current selection
            RDK.setSelection([]) # Clear selection
            
            # obj_highlight.setParam("Clear", "SurfPointCurve") # Example to clear the object geometry
            # Add the points to the highlighted object
            obj_highlight.AddShape(points)
            
            # Trick to use the same coordinate system
            obj_highlight.setParent(obj)
            idx = int(obj_highlight.setParam("Count", "Surf"))
            print("Number of surfaces: " + str(idx))
            
            # Color is defined as AARRGGBB (Alpha-Red-Green-Blue)
            # Important trick! Set the alpha to less than 50% to have some transparency for the following reasons:
            #   1. RoboDK renders transparent objects first.
            #   2. We can not click through objects with less than 50% of transparency, this allows us to click the objects of the cell and not our highlighted objects
            color = "#7e00ff00"
            print("Setting color of selected surface to: " + color)
            result = obj_highlight.setParam("Color", color + " " + str(idx-1))            

    else:
        print("Nothing under the mouse cursor")

    pause(0.1)