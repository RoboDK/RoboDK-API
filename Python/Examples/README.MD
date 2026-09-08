Examples
=========

This repository holds the RoboDK `Scripts` and `Macros` (examples). Some of these scripts are available in the install folder of RoboDK, see `RoboDK/Library/Scripts` and `RoboDK/Library/Macros`


Scripts
-----------

Any Python file (.py) in the `Scripts` folder can be run as a script within RoboDK.

To run a Python file as a script, select:

 1. `Tools`-`Run Script` (`Shift`+`S`)
 2. Select your script and select OK

Script files can be run for a specific purposes without having to make any changes to the code.


Macros
--------

Most PY files in the `Macros` folder are examples that may require adjustments to integrate with your projects. You can add these macros in your RoboDK station or run them in your Python environnement.


Index by topic
--------------

A categorized sample of representative files (not exhaustive — browse the folders directly for
the full set: 57 files in `Scripts/`, 122 in `Macros/`).

### Connecting / station basics

| File | Folder | What it shows |
|---|---|---|
| `RobotsConnect.py` | Scripts | Connects to every robot in the station and sends them home |
| `RobotsDisconnect.py` | Scripts | Disconnects all connected robots |
| `RobotsMonitor.py` | Scripts | Monitors connected-robot status |
| `ShowCommands.py` | Scripts | Lists available RoboDK command-line arguments |
| `Install_Python_Package.py` | Scripts | Installs a pip package from within RoboDK's Python env |

### Motion / offline programming

| File | Folder | What it shows |
|---|---|---|
| `SampleOfflineProgramming.py` | Macros | Canonical "draw a polygon" MoveL loop — the pattern in the top-level `Python/readme.md` example |
| `SampleOfflineProgramming_GUI.py` | Macros | Same, with a Tk GUI for parameters |
| `SampleApproachRetract.py` | Macros | Approach/retract waypoint pattern for pick/place-style moves |
| `MoveRobotRelative.py` | Macros | Relative jogging using `RelTool`/`Offset` |
| `MoveRobotThroughLine.py` | Macros | Moves a robot along a line by steps |
| `MoveAxis.py` | Macros | Moves a single external axis |
| `MovePolygon.py` / `MovePolygonGUI.py` | Scripts | Polygon motion, with and without GUI |
| `Show_All_Configurations.py` | Macros | Enumerates all IK solutions (robot configurations) for a pose |
| `Synchronize_3_Robots.py` / `SyncRobot1.py` | Macros | Multi-robot synchronized motion |
| `Jog_Robot_With_Keyboard.py` | Macros | Keyboard-driven jogging loop |

### Online programming (real robot)

| File | Folder | What it shows |
|---|---|---|
| `SampleOnlineProgramming.py` | Macros | Forces a real-robot connection and runs a program on it (`RUNMODE_RUN_ROBOT`) |
| `MoveRobotsOnline.py` | Macros | Online motion across multiple robots |
| `UR_ActivateMonitoring.py` / `UR_Monitoring_CSV.py` | Macros | Monitors a real UR robot's live position/variables |
| `UR_SendCommand.py` | Macros | Sends a raw command to a UR controller |
| `WaitForPart.py` / `LaserSensorWait.py` | Macros | Wait-for-sensor patterns before proceeding |

### Programs, targets, and post-processing

| File | Folder | What it shows |
|---|---|---|
| `ProgramAddInstructions.py` | Scripts | Programmatically adds instructions to a program |
| `ProgramCopy.py` | Scripts | Duplicates a program |
| `ProgramInvertPoses.py` | Scripts | Reverses a program's move order |
| `ProgramListCSV.py` | Scripts | Exports a program's targets to CSV |
| `ProgramReLinkTool.py` | Scripts | Re-points a program at a different tool |
| `ProgramSlider.py` / `ProgramSliderPlayback.py` | Scripts | Extracts/plays back a program's joint values, accounting for rounding |
| `ProgramSplitJoints.py` | Scripts | Splits a program by joint thresholds |
| `ProgramDisplayRobotTrace.py` | Scripts | Draws the robot's tool-path trace |
| `ScrollTo_Running_Instruction.py` | Scripts | Scrolls the tree to the currently executing instruction |
| `FilterProgram.py` / `FilterProgram2.py` / `FilterProgram3.py` | Macros | Program filtering variants (validate/convert against the active robot) |
| `ExportTargets.py` | Macros | Exports targets to a file |
| `ModifyProgramTargets.py` | Macros | Bulk-edits a program's target poses |
| `Reorganise_Prog.py` | Macros | Restructures program layout |
| `MoveC_2_MoveL.py` | Scripts/Macros (both) | Converts circular moves to a sequence of linear moves |

### Import / export (CSV, DXF, CAD)

| File | Folder | What it shows |
|---|---|---|
| `ImportCSV_XYZ.py` / `ImportCSV_XYZWPR.py` | Scripts | Import target lists from CSV (position-only vs. full pose) |
| `Example-Import-CSV-XYZWPR.csv` | Scripts | Sample CSV matching the importer above |
| `ImportDensoProgramCSV.py` | Scripts | Imports a Denso-formatted CSV as a program |
| `Import_DXF.py` | Scripts | Imports 2D DXF geometry as curves/points |
| `Import_KUKA_SRC_Program.py` | Scripts | Parses a KUKA `.src` file back into a RoboDK program |
| `Import_Mecademic_Script.py` | Scripts | Imports a Mecademic robot script |
| `Comau_LIS_Import.py` | Scripts | Imports Comau `.lis` program format |
| `load_dxf_codec.py` | Macros | DXF codec helper used by curve-import macros |

### Curves, surfaces, and geometry

| File | Folder | What it shows |
|---|---|---|
| `Curve_Change_Normals.py` | Scripts | Edits curve normal vectors |
| `Curve_Filter_AverageNormals.py` | Scripts | Smooths normals by local averaging |
| `Curve_Offset_CollisionFree.py` | Scripts | Offsets a curve while checking for collisions |
| `Curve_Project_2_Surface.py` / `ProjectCurve2SurfaceGUI.py` | Scripts | Projects a curve onto a surface |
| `Add_Curve_by_Points.py` | Macros | Builds a curve item from raw points |
| `Add_Shape_by_Triangles.py` | Macros | Builds a mesh shape from triangle data |
| `Mesh_Filter.py` | Scripts | Mesh simplification/filtering |
| `APT_Split.py` / `APT_Calculate_Radial_Normals.py` | Macros | APT (CAM) file utilities |
| `GetPoints_HighlightSelectedSurface.py` | Macros | Reads picked-surface points, highlights the selection |

### Calibration and measurement

| File | Folder | What it shows |
|---|---|---|
| `CalibrationExtractPoseMeasurements.py` | Scripts | Extracts measured poses for a calibration project |
| `CalculateErrorsDistances.py` / `CalculateErrorsPoses.py` | Macros | Post-calibration error validation (distance-only vs. full pose) |
| `Create_measurements_Grid.py` | Macros | Generates a measurement grid for calibration |
| `Create_repeatability_test.py` | Macros | ISO9283-style repeatability test setup |
| `TrackerCalibrateReference.py` | Macros | Laser-tracker reference-frame calibration |
| `Tracker_CreatePoints.py` / `Move_Robot_and_Measure.py` | Macros | Tracker point capture and measurement loop |
| `TCP_Set_Relative.py` / `TCP_Set_Relative_All_Len.py` | Macros | TCP-relative offset utilities |
| `TCP_2_axis_projection.py` | Macros | Projects the TCP onto a mechanism axis |

### Cameras and vision (OpenCV / Open3D)

| File | Folder | What it shows |
|---|---|---|
| `CameraAdd.py` / `CameraAddFov.py` / `SetupCamera2D.py` | Macros | Adds a simulated 2D camera to the station |
| `CameraSnapshot.py` / `CameraLiveStream.py` | Macros | Captures/streams simulated camera frames |
| `CameraHandEyeRecord.py` / `CameraHandEyeApply.py` | Macros | Hand-eye calibration record/apply workflow |
| `Depth_Camera.py` / `Open3D_Depth_Camera.py` / `Open3D_RGBD_Camera.py` | Macros | Depth-camera simulation via Open3D |
| `OpenCV_Camera_Calibration.py` / `OpenCV_Camera_Pose.py` | Macros | OpenCV-based camera calibration and pose estimation |
| `OpenCV_Augmented_Reality.py` | Macros | AR overlay demo |
| `OpenCV_Barcode_Reader.py` / `Barcode_1D_Generator.py` / `Barcode_2D_Generator.py` | Scripts/Macros | Barcode generation and reading |
| `OpenCV_Blobs.py` / `OpenCV_Part_Pose_SIFT.py` / `OpenCV_Parts_Orientation.py` | Macros | Blob detection, SIFT-based part pose, orientation estimation |

### Cell / process simulation

| File | Folder | What it shows |
|---|---|---|
| `Pick_And_Place.py` | Macros | Full pick-and-place application on a Fanuc M-710iC/50 (RoboDK library Example 2) |
| `PickObject.py` / `SimulateGripper.py` | Macros | Object pick and gripper open/close simulation |
| `RunConveyor.py` | Macros | Conveyor motion simulation |
| `Extruder.py` | Macros | 3D-printing/extrusion process simulation |
| `WeldOn.py` / `WeldOff.py` / `Weld_Path_Embedded.py` / `DoWeld_Remote.py` / `DoPointWeld.py` | Macros | Welding process on/off and path patterns |
| `SprayOn.py` / `SprayOff.py` | Macros | Paint-spray process on/off (`Spray_*` API) |
| `SetIO.py` / `WaitDI.py` | Macros | Digital I/O set/wait patterns |
| `Machining.py` / `RobotMachiningSettings.py` / `Edit_Machining_Settings.py` | Macros | Machining project setup and parameter editing |
| `MirrorDevices.py` / `Mirror_Robots.py` / `MirrorRealRobot.py` | Macros | Mirroring simulated motion onto a second device or the real robot |

### Cycle time / diagnostics

| File | Folder | What it shows |
|---|---|---|
| `CycleTimeDisplay.py` / `CycleTimeDisplay2.py` / `CycleTimeDisplayAll.py` | Scripts | Program cycle-time calculation, single and all-programs variants |
| `CycleTimeStudy.py` | Scripts | Deeper cycle-time breakdown |
| `Check_Orientation_Reachability.py` | Scripts | Visualizes reachable orientations around the current robot pose |
| `Monitor_TCP_Speed.py` / `MonitorJoints.py` / `MonitorJointsReal.py` | Macros | Live TCP speed / joint monitoring, sim and real |
| `JointSpeedsAccel.py` | Macros | Joint speed/acceleration inspection |
| `CheckCollisions.py` | Macros | Collision-check sweep over a program |

### UI, dialogs, and embedding

| File | Folder | What it shows |
|---|---|---|
| `MovePolygonGUI.py` / `SampleOfflineProgramming_GUI.py` | Scripts/Macros | Tk-based parameter GUIs |
| `Embed_PySide6.py` / `EmbedWindow_DockExample.py` | Macros | Embedding a Qt/PySide window inside RoboDK (`RDK.EmbedWindow`) |
| `Event_Loop.py` / `Event_Loop_ProgramSlider.py` | Macros | RoboDK event-loop consumption patterns |
| `viewport_demonstration.py` | Macros | Camera/viewport manipulation |
| `TakeSnapshot.py` / `TakeSnapshotHighRes.py` | Scripts | Station screenshot capture |

### Robot-vendor specific

| File | Folder | What it shows |
|---|---|---|
| `KUKA_Driver_Auto_Configuration.py` | Scripts | Auto-configures the KUKA driver |
| `FilterKukaCamrob.py` | Scripts | KUKA CamRob-specific program filtering |
| `JAKA_LoadControllerKinematics.py` / `UR_LoadControllerKinematics.py` | Scripts | Loads real-controller kinematics for comparison against simulation |
| `Fanuc_RetrieveRobotJoints.py` | Macros | Reads live joints from a Fanuc controller |
| `Gcode_Recalculate.py` | Macros | Recomputes G-code-derived motion |

`Python/tests/` is a separate `unittest`-based suite (needs a live RoboDK instance with a
matching `.rdk` station loaded — see the `.cmd` files there), not example code to copy from
directly.
