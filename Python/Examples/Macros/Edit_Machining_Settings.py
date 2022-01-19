# Type help("robolink") or help("robodk") for more information
# Press F5 to run the script
# Documentation: https://robodk.com/doc/en/RoboDK-API.html
# Reference:     https://robodk.com/doc/en/PythonAPI/index.html
#
# This example shows how to modify settings related to robot machining and program events using the RoboDK API

from robolink import *    # RoboDK API

# JSON tools
import json

# Ask the user to select a robot machining project
RDK = Robolink()
m = RDK.ItemUserPick('Select a robot machining project to change approach/retract', ITEM_TYPE_MACHINING)
if not m.Valid():
    raise Exception("Add a robot machining project, curve follow or point follow")

# Get the robot used by this robot machining project:
robot = m.getLink(ITEM_TYPE_ROBOT)
if not robot.Valid():
    print("Robot not selected: select a robot for this robot machining project")
    quit()
 
#--------------------------------------------
# Get or set preferred start joints:
joints = m.Joints()
joints = robot.JointsHome()
print("Preferred start joints:")
print(joints.list())
m.setJoints(joints)

# Get or set the path to tool pose:
path2tool = m.Pose()
print("Path to tool pose:")
print(path2tool)
m.setPose(path2tool)

# Get or set the tool / reference frame:
tool = m.getLink(ITEM_TYPE_TOOL)
print("Using tool: " + tool.Name())
frame = m.getLink(ITEM_TYPE_FRAME)
print("Using reference: " + frame.Name())
#m.setPoseFrame(frame)
#m.setPoseTool(tool)



#--------------------------------------------
# Get or set robot machining parameters
# Read Program Events settings for selected machining project
machiningsettings = m.setParam("Machining")
print("Robot machining settings:")
print(json.dumps(machiningsettings, indent=4))

    
#--------------------------------------------
# Read Program Events settings for selected machining project
progevents = m.setParam("ProgEvents")
print("Program events:")
print(json.dumps(progevents, indent=4))

# Read Program Events settings used by default
#station = RDK.ActiveStation()
#json_data = station.setParam("ProgEvents")
#json_object = json.loads(json_data)
#print(json.dumps(json_object, indent=4))
  
# Sample dict for robot machining settings
MachiningSettings = {
    "Algorithm": 0, # 0: minimum tool orientation change, 1: tool orientation follows path
    "ApproachRetractAll": 1,
    "AutoUpdate": 0,
    "AvoidCollisions": 0,
    "FollowAngle": 45,
    "FollowAngleOn": 1,
    "FollowRealign": 10,
    "FollowRealignOn": 0,
    "FollowStep": 90,
    "FollowStepOn": 0,
    "JoinCurvesTol": 0.5,
    "OrientXaxis2_X": -2,
    "OrientXaxis2_Y": 0,
    "OrientXaxis2_Z": 2,
    "OrientXaxis_X": 0,
    "OrientXaxis_Y": 0,
    "OrientXaxis_Z": 1,
    "PointApproach": 20,
    "RapidApproachRetract": 1,
    "RotZ_Range": 180,
    "RotZ_Step": 20,
    "SpeedOperation": 50,
    "SpeedRapid": 1000,
    "TrackActive": 0,
    "TrackOffset": 0,
    "TrackVector_X": -2,
    "TrackVector_Y": -2,
    "TrackVector_Z": -2,
    "TurntableActive": 1,
    "TurntableOffset": 0,
    "TurntableRZcomp": 1,
    "VisibleNormals": 0
}

# Sample dict for program events
MachiningProgEvents = {
    "CallAction": "onPoint",
    "CallActionOn": 0,
    "CallApproach": "onApproach",
    "CallApproachOn": 0,
    "CallPathFinish": "SpindleOff",
    "CallPathFinishOn": 1,
    "CallPathStart": "SpindleOn",
    "CallPathStartOn": 1,
    "CallProgFinish": "onFinish",
    "CallProgFinishOn": 0,
    "CallProgStart": "ChangeTool(%TOOL%)",
    "CallProgStartOn": 1,
    "CallRetract": "onRetract",
    "CallRetractOn": 0,
    "Extruder": "Extruder(%1)",
    "IO_Off": "default",
    "IO_OffMotion": "OutOffMov(%1)",
    "IO_On": "default",
    "IO_OnMotion": "OutOnMov(%1)",
    "Mcode": "M_RunCode(%1)",
    "RapidSpeed": 1000, # rapid speed to move to/from the path
    "Rounding": 1, # blending radius
    "RoundingOn": 0,
    "SpindleCCW": "",
    "SpindleCW": "",
    "SpindleRPM": "SetRPM(%1)",
    "ToolChange": "SetTool(%1)"
}

# Update one value, for example, make the normals not visible
MachiningUpdate = {}
MachiningUpdate["VisibleNormals"] = 0
MachiningUpdate["AutoUpdate"] = 0
MachiningUpdate["RotZ_Range"] = 0
print("Updating robot machining settings")
status = m.setParam("Machining", MachiningUpdate)
print(status)

# Update some values, for example, set custom tool change and set arc start and arc end commands
ProgEventsUpdate = {}
ProgEventsUpdate["ToolChange"] = "ChangeTool(%1)"
ProgEventsUpdate["CallPathStart"] = "ArcStart(1)"
ProgEventsUpdate["CallPathStartOn"] = 1
ProgEventsUpdate["CallPathFinish"] = "ArcEnd()"
ProgEventsUpdate["CallPathFinishOn"] = 1
print("Updating program events")
status = m.setParam("ProgEvents", ProgEventsUpdate)
print(status)


#---------------------------------------------------------------------------
# This section shows how to change the approach/retract settings for a robot machining project
# Units are in mm and degrees
# More examples here: C:/RoboDK/Library/Macros/SampleApproachRetract.py

# Apply a tangency approach and retract (in mm)
m.setParam("ApproachRetract", "Tangent 50")
#m.setParam("Approach", "Tangent 50")
#m.setParam("Retract", "Tangent 50")
#m.setParam("Retract", "Side 100") # side approach
#m.setParam("Approach", "XYZ 50 60 70") # XYZ offset
#m.setParam("Approach", "NTS 50 60 70") #Normal/Tangent/Side Coordinates
#m.setParam("ApproachRetract", "ArcN 50 100") # Normal arc (diameter/angle)
m.setParam("UpdatePath") # recalculate toolpath

# Update machining project (validates robot feasibility)
status = m.Update() 

# Get the generated robot program
prog = m.getLink(ITEM_TYPE_PROGRAM)

# Run the program simulation
prog.RunProgram()

# Save program file to specific folder
#program.MakeProgram("""C:/Path-to-Folder/""")

