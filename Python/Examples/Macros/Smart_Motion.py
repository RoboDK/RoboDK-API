# This example shows how to use the Smart Motion Add-in's API commands for collision-free path generation
# General format of the Smart Motion Add-in's commands: RDK.PluginCommand("Smart Motion", "CommandName", "ValueString")
#
# Every command returns a string: setters return the value that was applied (after clamping),
# getters return the current value and the motion commands return the generation result
# (for example "Final path generated in 2.5 seconds" or "No path found").
# While a command runs, the Add-in does not show message boxes: always check the returned string.
#
# Smart Motion Documentation: https://robodk.com/doc/en/Smart-Motion.html

from robodk.robolink import *  # API to communicate with RoboDK for simulation and offline/online programming

# Any interaction with RoboDK must be done through RDK:
RDK = Robolink()

# Launch and dock the Smart Motion side panel in the RoboDK interface
RDK.PluginCommand("Smart Motion", "openForm", "")

# Display the RoboDK collision checking map
RDK.PluginCommand("Smart Motion", "showCollisionMap", "")

# Select the active robot (the robot in the station which will execute the path planning commands) by name
# Use an empty string "" to select the robot automatically when the station has only one robot,
# or to open the robot selector window when it has several
result = RDK.PluginCommand("Smart Motion", "selectRobot", "Comau Smart5 NJ 130-2.6")
print("Select robot:", result)  # robot name, or "No robot selected"

# Get the name of the currently active robot ("" if none is selected)
active_robot = RDK.PluginCommand("Smart Motion", "getRobot")
print("Active Robot:", active_robot)

# Seed the planner's random number generator (positive integer) to get reproducible paths
# This only takes effect when called before the first path is generated in the RoboDK session
RDK.PluginCommand("Smart Motion", "setSeed", "12345")

# Set the planner quality effort on a scale from 1 (coarse) to 10 (fine); out-of-range values are clamped
# This determines how much computing time is spent increasing the safety and smoothness of a trajectory
RDK.PluginCommand("Smart Motion", "setQuality", "5")

# Retrieve the current path quality level
current_quality = RDK.PluginCommand("Smart Motion", "getQuality")
print("Quality Level:", current_quality)

# Also write the rough, pre-simplified draft of the trajectory to an extra "RRT Plan initial" program (debugging aid)
# Use "true", "1" or "on" to enable this setting and anything else to disable it
RDK.PluginCommand("Smart Motion", "setShowInitialPath", "false")

# Check if the pre-simplified path output is enabled ("true" or "false")
show_initial = RDK.PluginCommand("Smart Motion", "getShowInitialPath")
print("Show Initial Path:", show_initial)

# Force joint-space planning for navigating narrow and cluttered spaces which are heavily constrained
# Use "true", "1" or "on" to enable this setting and anything else to disable it
# Activating Constrained Space automatically turns off Lock TCP, and vice versa
RDK.PluginCommand("Smart Motion", "setConstrainedSpace", "true")

# Check whether constrained space mode is active ("true" or "false")
constrained_mode = RDK.PluginCommand("Smart Motion", "getConstrainedSpace")
print("Constrained Space:", constrained_mode)

# Constrain the tool orientation (degrees, range -1 to 180, out-of-range values are clamped)
# -1 leaves the tool orientation completely free
# Any value from 0 locks the rotations around X and Y and allows up to +/- that many degrees around the tool Z axis
# (0 locks the orientation completely)
# Activating Lock TCP (value greater than -1) automatically turns off Constrained Space, and vice versa
RDK.PluginCommand("Smart Motion", "setLockTcp", "45.0")

# Display the current TCP rotation lock angle
lock_tcp_val = RDK.PluginCommand("Smart Motion", "getLockTcp")
print("Lock TCP Angle:", lock_tcp_val)

# Select the destination program for the NEXT path generation (created if it does not exist)
# The selection applies to one generation only: call selectProgram again before each motion command.
# Without a selection, the Add-in creates a new "Smart Motion path N" program
# (or asks which program to use when the station already contains more than one program).
# Passing "" clears the selection.
RDK.PluginCommand("Smart Motion", "selectProgram", "SmartMotion_Targets")

# Verify the name of the destination program
current_prog = RDK.PluginCommand("Smart Motion", "getProgram")
print("Selected Program:", current_prog)

# Calculate a collision-free trajectory through a series of existing targets (at least two names)
# Multiple values separated by the pipe character (|)
result = RDK.PluginCommand("Smart Motion", "moveTarget", "Home|AppFront|Weld_Target_1|Home")
print("moveTarget:", result)  # "Final path generated in N seconds", "No path found", "Invalid target: ...", ...

# Re-run the path generation with the current parameters on the same targets
# (the targets of the last moveTarget call, or the ones chosen in the target selector window)
RDK.PluginCommand("Smart Motion", "selectProgram", "SmartMotion_Targets_Fine")
RDK.PluginCommand("Smart Motion", "setQuality", "10")
result = RDK.PluginCommand("Smart Motion", "generatePath", "")
print("generatePath:", result)

# Calculate a collision-free path through joint poses (comma-separated joint values, at least two poses)
# Add the keyword "Approach" after a pose to flag the move into that pose as an approach move,
# which keeps that segment unsimplified.
# The poses are created as temporary targets that are removed when the command returns,
# so the target list is empty afterwards (generatePath would report "No target selected").
RDK.PluginCommand("Smart Motion", "selectProgram", "SmartMotion_Joints")
result = RDK.PluginCommand("Smart Motion", "moveJoint", "0,0,0,0,0,0|15,-20,10,0,30,0|Approach|30,0,0,0,0,0")
print("moveJoint:", result)

# Open the interactive target selector window to pick targets manually, then use generatePath
RDK.PluginCommand("Smart Motion", "openTargetSelector", "")
