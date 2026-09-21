# This example shows how to use Smart Motion Add-in's API commands for effective colision-free path generation
# General format of Smart Motion Add-in's commands: rdk.PluginCommand("Smart Motion", "CommandName", "ValueString")

# Smart Motion Documentation: https://robodk.com/doc/en/Smart-Motion.html

from robodk.robolink import *  # API to communicate with RoboDK for simulation and offline/online programming

# Any interaction with RoboDK must be done through RDK:
RDK = Robolink()

# Launch and dock the Smart Motion side panel in the RoboDK interface
RDK.PluginCommand("Smart Motion", "openForm", "")

# Display the RoboDK collision checking map
RDK.PluginCommand("Smart Motion", "showCollisionMap", "")

# Open the interactive target selector window
RDK.PluginCommand("Smart Motion", "openTargetSelector", "")

# Select the active robot (the robot in the station which will execute the path planning commands) by name in the station
# Use an empty text string "" instead of specifying the active robot to open the robot selector window
RDK.PluginCommand("Smart Motion", "selectRobot", "Comau Smart5 NJ 130-2.6")

# Get the name of the currently active robot
active_robot = RDK.PluginCommand("Smart Motion", "getRobot")
print("Active Robot:", active_robot)

# Set the planner quality effort on a scale from 1 (coarse) to 10 (fine)
# This determines how much computing time is spent increasing the safety and smoothness of a trajectory
RDK.PluginCommand("Smart Motion", "setQuality", "5")

# Retrieve the current path quality level
current_quality = RDK.PluginCommand("Smart Motion", "getQuality")
print("Quality Level:", current_quality)

# Display the rough, pre-simplified initial draft of the trajectory
# Use "true", "1", or "on" to enable this setting and anything else to disable
RDK.PluginCommand("Smart Motion", "setShowInitialPath", "true")

# Check if pre-simplified path display is enabled
show_initial = RDK.PluginCommand("Smart Motion", "getShowInitialPath")
print("Show Initial Path:", show_initial)

# Enable joint-space planning for navigating narrow and cluttered spaces which are heavily constrained
# Use "true", "1", or "on" to enable this setting and anything else to disable
# Activating Constrained Space automatically turns off Lock TCP, and vice-versa
RDK.PluginCommand("Smart Motion", "setConstrainedSpace", "true")

# Check whether constrained space mode is active
constrained_mode = RDK.PluginCommand("Smart Motion", "getConstrainedSpace")
print("Constrained Space:", constrained_mode)

# Manage tool rotation allowance around Z (deg, data type: double, range: -1 to 180) and auto-disable constrained space
# Setting the value to -1 leaves the tool rotation completely free and unlocked
# Out-of-range value is clamped to either -1.0 or 180.0 depending on the closest one
# Activating Lock TCP (value greater than -1) automatically turns off Constrained Space, and vice-versa
RDK.PluginCommand("Smart Motion", "setLockTcp", "45.0")

# Display the current TCP rotation lock angle
lock_tcp_val = RDK.PluginCommand("Smart Motion", "getLockTcp")
print("Lock TCP Angle:", lock_tcp_val)

# Pre-select an existing program or create a new destination program for generated motion
# If the program specified in the ValueString of this command does not exist, a new program with the name is created
# Leaving this blank or passing "" clears the selection and opens the program selector window after the path is calculated
RDK.PluginCommand("Smart Motion", "selectProgram", "SmartMotion_Program")

# Verify the name of the destination program
current_prog = RDK.PluginCommand("Smart Motion", "getProgram")
print("Selected Program:", current_prog)

# Calculate a collision-free trajectory across a series of consecutive waypoints from existing targets
# Multiple values separated by the pipe character (|)
RDK.PluginCommand("Smart Motion", "moveTarget", "Home|AppFront|Weld_Target_1|Home")

# Calculate a collision-free path directly between two specific joint poses
RDK.PluginCommand("Smart Motion", "moveJoint", "0,0,0,0,0,0|15,-20,10,0,30,0")

# Re-run path generation using the current target list and parameters
RDK.PluginCommand("Smart Motion", "generatePath", "")