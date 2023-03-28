# Copyright 2015-2023 - RoboDK Inc. - https://robodk.com/
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# --------------------------------------------
# --------------- DESCRIPTION ----------------
# This file defines the following two classes:
#     Robolink()
#     Item()
# These classes are the objects used to interact with RoboDK and create macros.
# An item is an object in the RoboDK tree (it can be either a robot, an object, a tool, a frame, a program, ...).
# Items can be retrieved from the RoboDK station using the Robolink() object (such as Robolink.Item() method)
#
# More information about the RoboDK API for Python here:
#     https://robodk.com/doc/en/RoboDK-API.html
#     https://robodk.com/doc/en/PythonAPI/index.html
#
# --------------------------------------------

import struct
from robodk import robomath
import sys  # Only used to detect python version using sys.version_info
import os
import time
import threading

# Tree item types
ITEM_TYPE_STATION = 1  #: Station :class:`.Item` (.rdk files)
ITEM_TYPE_ROBOT = 2  #: Robot :class:`.Item` (.robot files)
ITEM_TYPE_FRAME = 3  #: Reference frame :class:`.Item`
ITEM_TYPE_TOOL = 4  #: Tool :class:`.Item` (.tool files or tools without geometry)
ITEM_TYPE_OBJECT = 5  #: Object :class:`.Item` (.stl, .step, .iges, ...)
ITEM_TYPE_TARGET = 6  #: Target :class:`.Item`
ITEM_TYPE_CURVE = 7  #: Curve :class:`.Item`
ITEM_TYPE_PROGRAM = 8  #: Program :class:`.Item`
ITEM_TYPE_INSTRUCTION = 9  #: Program instruction :class:`.Item`
ITEM_TYPE_PROGRAM_PYTHON = 10  #: Python program or macro :class:`.Item` (.py files)
ITEM_TYPE_MACHINING = 11  #: Machining project :class:`.Item`
ITEM_TYPE_BALLBARVALIDATION = 12  #: Ballbar validation test :class:`.Item`
ITEM_TYPE_CALIBPROJECT = 13  #: Calibration :class:`.Item`
ITEM_TYPE_VALID_ISO9283 = 14  #: ISO9283 validation test :class:`.Item`
ITEM_TYPE_FOLDER = 17  #: Folder :class:`.Item`
ITEM_TYPE_ROBOT_ARM = 18  #: Robot arm :class:`.Item` (subtype of ITEM_TYPE_ROBOT for robot arms)
ITEM_TYPE_CAMERA = 19  #: Camera :class:`.Item`
ITEM_TYPE_GENERIC = 20  #: Generic :class:`.Item`
ITEM_TYPE_ROBOT_AXES = 21  #: Robot axes :class:`.Item` (subtype of ITEM_TYPE_ROBOT for axes)
ITEM_TYPE_NOTES = 22  #: Notes :class:`.Item`

# Instruction types
INS_TYPE_INVALID = -1  #: Invalid instruction type of a :class:`.ITEM_TYPE_INSTRUCTION`
INS_TYPE_MOVE = 0  #: Move (except MoveC) instruction type of a :class:`.ITEM_TYPE_INSTRUCTION`
INS_TYPE_MOVEC = 1  #: MoveC instruction type of a :class:`.ITEM_TYPE_INSTRUCTION`
INS_TYPE_CHANGESPEED = 2  #: Set Speed instruction type of a :class:`.ITEM_TYPE_INSTRUCTION`
INS_TYPE_CHANGEFRAME = 3  #: Set Frame instruction type of a :class:`.ITEM_TYPE_INSTRUCTION`
INS_TYPE_CHANGETOOL = 4  #: Set Tool instruction type of a :class:`.ITEM_TYPE_INSTRUCTION`
INS_TYPE_CHANGEROBOT = 5  #: Set Robot instruction type of a :class:`.ITEM_TYPE_INSTRUCTION`
INS_TYPE_PAUSE = 6  #: Pause instruction type of a :class:`.ITEM_TYPE_INSTRUCTION`
INS_TYPE_EVENT = 7  #: Simulation Event instruction type of a :class:`.ITEM_TYPE_INSTRUCTION`
INS_TYPE_CODE = 8  #: Code instruction type of a :class:`.ITEM_TYPE_INSTRUCTION`
INS_TYPE_PRINT = 9  #: Show Message instruction type of a :class:`.ITEM_TYPE_INSTRUCTION`
INS_TYPE_ROUNDING = 10  #: Rounding instruction type of a :class:`.ITEM_TYPE_INSTRUCTION`

# Move types
MOVE_TYPE_INVALID = -1  #: Invalid move type of a :class:`.ITEM_TYPE_INSTRUCTION`
MOVE_TYPE_JOINT = 1  #: Joint move (MoveJ) type of a :class:`.ITEM_TYPE_INSTRUCTION`
MOVE_TYPE_LINEAR = 2  #: Linear move (MoveL) type of a :class:`.ITEM_TYPE_INSTRUCTION`
MOVE_TYPE_CIRCULAR = 3  #: Circular move (MoveC) type of a :class:`.ITEM_TYPE_INSTRUCTION`
MOVE_TYPE_LINEARSEARCH = 5  #: Linear search move (SearchL) type of a :class:`.ITEM_TYPE_INSTRUCTION`

# Station parameters request
PATH_OPENSTATION = 'PATH_OPENSTATION'  #: Full path of the current station (.rdk file) request flag
FILE_OPENSTATION = 'FILE_OPENSTATION'  #: File name of the current station (name of the .rdk file) request flag
PATH_DESKTOP = 'PATH_DESKTOP'  # Full path to the desktop folder request flag

# Script execution types
RUNMODE_SIMULATE = 1  #: Performs the simulation moving the robot (default)
RUNMODE_QUICKVALIDATE = 2  #: Performs a quick check to validate the robot movements
RUNMODE_MAKE_ROBOTPROG = 3  #: Makes the robot program
RUNMODE_MAKE_ROBOTPROG_AND_UPLOAD = 4  #: Makes the robot program and updates it to the robot
RUNMODE_MAKE_ROBOTPROG_AND_START = 5  #: Makes the robot program and starts it on the robot (independently from the PC)
RUNMODE_RUN_ROBOT = 6  #: Moves the real robot from the PC (PC is the client, the robot behaves like a server)

# Program execution type
PROGRAM_RUN_ON_SIMULATOR = 1  #: Run on the simulator program flag
PROGRAM_RUN_ON_ROBOT = 2  #: Run on the robot program flag

# Robot connection status
ROBOTCOM_PROBLEMS = -3  #: Problems connection status
ROBOTCOM_DISCONNECTED = -2  #: Disconnected connection status
ROBOTCOM_NOT_CONNECTED = -1  #: Not connected connection status
ROBOTCOM_READY = 0  #: Ready connection status
ROBOTCOM_WORKING = 1  #: Working connection status
ROBOTCOM_WAITING = 2  #: Problems connection status
ROBOTCOM_UNKNOWN = -1000  #: Problems connection status

# TCP calibration methods
CALIBRATE_TCP_BY_POINT = 0  #: Calibrate TCP by point flag
CALIBRATE_TCP_BY_PLANE = 1  #: Calibrate TCP by plane flag
CALIBRATE_TCP_BY_PLANE_SCARA = 4  #: Calibrate TCP by plane (SCARA) flag

# Reference frame calibration methods
CALIBRATE_FRAME_3P_P1_ON_X = 0  #: Calibrate frame by 3 points: [X, X+, Y+] (p1 on X axis) flag
CALIBRATE_FRAME_3P_P1_ORIGIN = 1  #: Calibrate frame by 3 points: [Origin, X+, XY+] (p1 is origin) flag
CALIBRATE_FRAME_6P = 2  #: Calibrate frame by 6 points flag
CALIBRATE_TURNTABLE = 3  #: Calibrate turntable flag
CALIBRATE_TURNTABLE_2X = 4  #: Calibrate a 2 axis turntable flag

# Projection types (for AddCurve)
PROJECTION_NONE = 0  #: No curve/point projection
PROJECTION_CLOSEST = 1  #: The projection will be the closest point on the surface
PROJECTION_ALONG_NORMAL = 2  #: The projection will be done along the normal
PROJECTION_ALONG_NORMAL_RECALC = 3  #: The projection will be done along the normal. Furthermore, the normal will be recalculated according to the surface normal
PROJECTION_CLOSEST_RECALC = 4  #: The projection will be the closest point on the surface and the normals will be recalculated
PROJECTION_RECALC = 5  #: The normals are recalculated according to the surface normal of the closest projection. The points are not changed.

# Euler type
JOINT_FORMAT = -1  #: Joints (not poses) Euler format flag
EULER_RX_RYp_RZpp = 0  #: RX:RYp:RZpp (generic) Euler format flag
EULER_RZ_RYp_RXpp = 1  #: RZ:RYp:RXpp (ABB RobotStudio) Euler format flag
EULER_RZ_RYp_RZpp = 2  #: RZ:RYp:RZpp (Kawasaki, Adept, Staubli) Euler format flag
EULER_RZ_RXp_RZpp = 3  #: RZ:RXp:RZpp (CATIA, SolidWorks) Euler format flag
EULER_RX_RY_RZ = 4  #: RX:RY:RZ (Fanuc, Kuka, Motoman, Nachi) Euler format flag
EULER_RZ_RY_RX = 5  #: RZ:RY:RX (CRS) Euler format flag
EULER_QUEATERNION = 6  #: Quaternion (ABB Rapid) Euler format flag

# State of the RoboDK window
WINDOWSTATE_HIDDEN = -1  #: Hidden RoboDK window state
WINDOWSTATE_SHOW = 0  #: Show RoboDK window state
WINDOWSTATE_MINIMIZED = 1  #: Minimized RoboDK window state
WINDOWSTATE_NORMAL = 2  #: Normal RoboDK window state
WINDOWSTATE_MAXIMIZED = 3  #: Maximized RoboDK window state
WINDOWSTATE_FULLSCREEN = 4  #: Fullscreen RoboDK window state
WINDOWSTATE_CINEMA = 5  #: Cinema RoboDK window state
WINDOWSTATE_FULLSCREEN_CINEMA = 6  #: Fullscreen and cinema RoboDK window state
WINDOWSTATE_VIDEO = 7  #: Video RoboDK window state

# Instruction program call type:
INSTRUCTION_CALL_PROGRAM = 0  #: Program call instruction type of a Program call
INSTRUCTION_INSERT_CODE = 1  #: Insert code instruction type of a Program call
INSTRUCTION_START_THREAD = 2  #: Start a new process instruction type of a Program call
INSTRUCTION_COMMENT = 3  #: Insert comment instruction type of a Program call
INSTRUCTION_SHOW_MESSAGE = 4  #: Show message instruction type of a Program call

# Object selection features
FEATURE_NONE = 0  #: None feature type flag
FEATURE_SURFACE = 1  #: Surface (under the mouse cursor) feature type flag
FEATURE_CURVE = 2  #: Curve feature type flag
FEATURE_POINT = 3  #: Point feature type flag
FEATURE_OBJECT_MESH = 7  #: Object mesh (using ID) feature type flag
FEATURE_SURFACE_PREVIEW = 8  #: Surface preview feature type flag
FEATURE_MESH = 9  #: Mesh (under the mouse cursor) feature flag
# The following do not require providing an object
FEATURE_HOVER_OBJECT_MESH = 10  #: Object mesh (under the mouse cursor) feature type flag
FEATURE_HOVER_OBJECT = 11  #: Object feature (under the mouse cursor) feature type flag

# Spray gun simulation:
SPRAY_OFF = 0  #: Spray OFF flag
SPRAY_ON = 1  #: Spray ON flag

# Collision checking state
COLLISION_OFF = 0  #: Collision OFF flag
COLLISION_ON = 1  #: Collision ON flag

# RoboDK Window Flags
FLAG_ROBODK_TREE_ACTIVE = 1  #: RoboDK tree active flag
FLAG_ROBODK_3DVIEW_ACTIVE = 2  #: RoboDK 3D view (3D mouse navigation) active flag
FLAG_ROBODK_LEFT_CLICK = 4  #: RoboDK left click active flag
FLAG_ROBODK_RIGHT_CLICK = 8  #: RoboDK right click active flag
FLAG_ROBODK_DOUBLE_CLICK = 16  #: RoboDK double clicks active flag
FLAG_ROBODK_MENU_ACTIVE = 32  #: RoboDK main menu (complete menu) active flag
FLAG_ROBODK_MENUFILE_ACTIVE = 64  #: RoboDK File menu active flag
FLAG_ROBODK_MENUEDIT_ACTIVE = 128  #: RoboDK Edit menu active flag
FLAG_ROBODK_MENUPROGRAM_ACTIVE = 256  #: RoboDK Program menu active flag
FLAG_ROBODK_MENUTOOLS_ACTIVE = 512  #: RoboDK Tools menu active flag
FLAG_ROBODK_MENUUTILITIES_ACTIVE = 1024  #: RoboDK Utilities menu active flag
FLAG_ROBODK_MENUCONNECT_ACTIVE = 2048  #: RoboDK Connect menu active flag
FLAG_ROBODK_WINDOWKEYS_ACTIVE = 4096  #: RoboDK keystrokes active flag
FLAG_ROBODK_TREE_VISIBLE = 8192  #: RoboDK tree visible flag
FLAG_ROBODK_REFERENCES_VISIBLE = 16384  #: RoboDK reference frames visible flag
FLAG_ROBODK_STATUSBAR_VISIBLE = 32768  #: RoboDK status bar visible flag
FLAG_ROBODK_NONE = 0x00  #: RoboDK disable all flag
FLAG_ROBODK_ALL = 0xFFFF  #: RoboDK enable all flag
FLAG_ROBODK_MENU_ACTIVE_ALL = FLAG_ROBODK_MENU_ACTIVE | FLAG_ROBODK_MENUFILE_ACTIVE | FLAG_ROBODK_MENUEDIT_ACTIVE | FLAG_ROBODK_MENUPROGRAM_ACTIVE | FLAG_ROBODK_MENUTOOLS_ACTIVE | FLAG_ROBODK_MENUUTILITIES_ACTIVE | FLAG_ROBODK_MENUCONNECT_ACTIVE  #: RoboDK enable menu only flag

# RoboDK Item Flags
FLAG_ITEM_SELECTABLE = 1  #: Allow selecting the item flag
FLAG_ITEM_EDITABLE = 2  #: Allow editing the item flag
FLAG_ITEM_DRAGALLOWED = 4  #: Allow dragging the item flag
FLAG_ITEM_DROPALLOWED = 8  #: Allow dropping nested items flag
FLAG_ITEM_ENABLED = 32  #: Enable this item in the tree flag
FLAG_ITEM_AUTOTRISTATE = 64
FLAG_ITEM_NOCHILDREN = 128
FLAG_ITEM_USERTRISTATE = 256
FLAG_ITEM_NONE = 0  #: Disable everything item flag
FLAG_ITEM_ALL = 64 + 32 + 8 + 4 + 2 + 1  #: Enable everything item flag

# Robot/mechanism types
MAKE_ROBOT_1R = 1  #: 1R model type flag
MAKE_ROBOT_2R = 2  #: 2R model type flag
MAKE_ROBOT_3R = 3  #: 3R model type flag
MAKE_ROBOT_1T = 4  #: 1T model type flag
MAKE_ROBOT_2T = 5  #: 2T model type flag
MAKE_ROBOT_3T = 6  #: 3T model type flag
MAKE_ROBOT_6DOF = 7  #: 6 DOF robot model type flag
MAKE_ROBOT_7DOF = 8  #: 7 DOF robot model type flag
MAKE_ROBOT_SCARA = 9  #: SCARA robot model type flag
MAKE_ROBOT_GRIPPER = 10  #: Gripper model type flag
MAKE_ROBOT_6COBOT = 11  #: 6 DOF cobot model type flag
MAKE_ROBOT_1T1R = 12  #: 1T1R model type flag
MAKE_ROBOT_5XCNC = 13  #: 5 axis CNC model type flag
MAKE_ROBOT_3T1R = 15  #: 3T1R model type flag
MAKE_ROBOT_GENERIC = 16  #: Generic model type flag

# Path Error bit mask
ERROR_KINEMATIC = 0b001  #: One or more points is not reachable path error flag
ERROR_PATH_LIMIT = 0b010  #: The path reaches the limit of joint axes path error flag
ERROR_PATH_SINGULARITY = 0b100  #: The robot reached a singularity point path error flag
ERROR_PATH_NEARSINGULARITY = 0b1000  #: The robot is too close to a singularity path error flag
ERROR_COLLISION = 0b100000  #: Collision detected path error flag

# Interactive selection option (for 3D mouse behavior and setInteractiveMode)
SELECT_RESET = -1  #: Reset selection flag
SELECT_NONE = 0  #: Reset selection flag
SELECT_RECTANGLE = 1  #: Rectangle selection flag
SELECT_ROTATE = 2  #: Rotate selection flag
SELECT_ZOOM = 3  #: Zoom selection flag
SELECT_PAN = 4  #: Pan selection flag
SELECT_MOVE = 5  #: Move selection flag
SELECT_MOVE_SHIFT = 6  #: Move Shift selection flag
SELECT_MOVE_CLEAR = 7  #: Move Clear selection flag

# Bit masks to show specific reference frames and customize the display of references (for picking references with the 3D mouse and setInteractiveMode)
DISPLAY_REF_DEFAULT = -1  #: Default reference frame visibility flag
DISPLAY_REF_NONE = 0  #: None reference frame visibility flag
DISPLAY_REF_TX = 0b001  #: TX reference frame visibility flag
DISPLAY_REF_TY = 0b010  #: TY reference frame visibility flag
DISPLAY_REF_TZ = 0b100  #: TZ reference frame visibility flag
DISPLAY_REF_RX = 0b001000  #: RX reference frame visibility flag
DISPLAY_REF_RY = 0b010000  #: RY reference frame visibility flag
DISPLAY_REF_RZ = 0b100000  #: RZ reference frame visibility flag
DISPLAY_REF_PXY = 0b001000000  #: Plane XY reference frame visibility flag
DISPLAY_REF_PXZ = 0b010000000  #: Plane XZ reference frame visibility flag
DISPLAY_REF_PYZ = 0b100000000  #: Plane YZ reference frame visibility flag

VISIBLE_REFERENCE_DEFAULT = -1  #: Default Item visibility flag
VISIBLE_REFERENCE_ON = 1  #: Visible (ON) Item visibility flag
VISIBLE_REFERENCE_OFF = 0  #: Hidden (OFF) Item visibility flag
VISIBLE_ROBOT_NONE = 0  #: None Robot visibility flag
VISIBLE_ROBOT_FLANGE = 0x01  #: Flange robot visibility flag
VISIBLE_ROBOT_AXIS_Base_3D = 0x01 << 1  #: Axis base 3D robot visibility flag
VISIBLE_ROBOT_AXIS_Base_REF = 0x01 << 2  #: Axis base reference robot visibility flag
VISIBLE_ROBOT_AXIS_1_3D = 0x01 << 3  #: Axis 1 3D robot visibility flag
VISIBLE_ROBOT_AXIS_1_REF = 0x01 << 4  #: Axis 1 reference robot visibility flag
VISIBLE_ROBOT_AXIS_2_3D = 0x01 << 5  #: Axis 2 3D robot visibility flag
VISIBLE_ROBOT_AXIS_2_REF = 0x01 << 6  #: Axis 2 reference robot visibility flag
VISIBLE_ROBOT_AXIS_3_3D = 0x01 << 7  #: Axis 3 3D robot visibility flag
VISIBLE_ROBOT_AXIS_3_REF = 0x01 << 8  #: Axis 3 reference robot visibility flag
VISIBLE_ROBOT_AXIS_4_3D = 0x01 << 9  #: Axis 4 3D robot visibility flag
VISIBLE_ROBOT_AXIS_4_REF = 0x01 << 10  #: Axis 4 reference robot visibility flag
VISIBLE_ROBOT_AXIS_5_3D = 0x01 << 11  #: Axis 5 3D robot visibility flag
VISIBLE_ROBOT_AXIS_5_REF = 0x01 << 12  #: Axis 5 reference robot visibility flag
VISIBLE_ROBOT_AXIS_6_3D = 0x01 << 13  #: Axis 6 3D robot visibility flag
VISIBLE_ROBOT_AXIS_6_REF = 0x01 << 14  #: Axis 6 reference robot visibility flag
VISIBLE_ROBOT_AXIS_7_3D = 0x01 << 15  #: Axis 7 3D robot visibility flag
VISIBLE_ROBOT_AXIS_7_REF = 0x02 << 16  #: Axis 7 reference robot visibility flag
VISIBLE_ROBOT_DEFAULT = 0x2AAAAAAB  #: Default robot visibility flag
VISIBLE_ROBOT_ALL = 0x7FFFFFFF  #: All robot visibility flag
VISIBLE_ROBOT_ALL_REFS = 0x15555555  #: All references robot visibility flag

# ShowSequence() display type flags (use as mask)
SEQUENCE_DISPLAY_DEFAULT = -1  #: Default sequence display flag
SEQUENCE_DISPLAY_TOOL_POSES = 0  #: Using tool poses (argument type) sequence display flag
SEQUENCE_DISPLAY_ROBOT_POSES = 256  #: Using robot poses (argument type) sequence display flag
SEQUENCE_DISPLAY_ROBOT_JOINTS = 2048  #: Using robot joints (argument type) sequence display flag
SEQUENCE_DISPLAY_COLOR_SELECTED = 1  #: Selected color sequence display flag
SEQUENCE_DISPLAY_COLOR_TRANSPARENT = 2  #: Transparent color sequence display flag
SEQUENCE_DISPLAY_COLOR_GOOD = 3  #: Good (green) color sequence display flag
SEQUENCE_DISPLAY_COLOR_BAD = 4  #: Bad (red) color sequence display flag
SEQUENCE_DISPLAY_OPTION_RESET = 1024  #: Reset previous sequences (force timeout) sequence display flag

if sys.version_info.major >= 3 and sys.version_info.minor >= 6:
    # To be added in the future. Requires Python 3.6 or later
    from enum import IntFlag
    from enum import IntEnum

    class InstructionListJointsFlags(IntEnum):
        """InstructionListJoints output flags"""
        Position = 1  # Only provide the joint position and XYZ values
        Speed = 2  # Calculate speed (added to position)
        SpeedAndAcceleration = 3  # Calculate speed and acceleration (added to position)
        TimeBased = 4  # Make the calculation time-based (adds a time stamp added to the previous options)
        TimeBasedFast = 5  # Make the calculation time-based and avoids calculating speeds and accelerations (adds a time stamp added to the previous options)

    class PathErrorFlags(IntFlag):
        """Error flags returned by InstructionListJoints"""
        # none of the flags is set -> No Error
        NoError = 0

        # One or more points is not reachable
        Kinematic = 0x1  # 0b0000_0000_0001

        # The robot reaches the limit of joint axes trying to make a linear movement between 2 valid points
        PathLimit = 0x2  # 0b0000_0000_0010

        # Error code reporting is inaccurate due to large axis move. Reduce the time step or the robot speed
        # This error flag is never combined with other error flags.
        # This flag will appear with time based simulations and it means the path is feasible but RoboDK is unable to calculate it with the current time step
        InnacurateDueToLargeAxisMove = 0x800  # error code 20

        # The robot reached a singularity point
        PathSingularity = 0x4  # 0b0000_0000_0100

        # The robot is close to a singularity.
        # Lower the singularity tolerance to allow the robot to continue.
        # If you get this error flag it means you may be able to go through the singularity if you lower the tolerances in Tools-Options-Motion
        PathNearSingularity = 0x8  # 0b0000_0000_1000

        # A movement can't involve an exact rotation of 180 deg around a unique axis. The rotation is ambiguous and has infinite solutions.
        PathFlipAxis = 0x10  # 0b0000_0001_0000

        # Collision detected
        Collision = 0x20  # 0b0000_0010_0000

        # The robot reached a Wrist singularity: Joint 5 is too close to 0 deg
        WristSingularity = 0x40  # 0b0000_0100_0000

        # The robot reached an Elbow singularity: Joint 3 is fully extended
        ElbowSingularity = 0x80  # 0b0000_1000_0000

        # The robot reached a Shoulder singularity: the wrist is too close to axis 1
        ShoulderSingularity = 0x100  # 0b0001_0000_0000

        # Target not reachable or invalid
        PathInvalidTarget = 0x200  # 0b0010_0000_0000

        # A circular movement is not valid because it does not define an arc. Make sure to properly separate all points and make sure they are not along one line.
        InvalidArcMove = 0x400  # 0b00100_0000_0000

    def ConvertErrorCodeToJointErrorType(evalue):
        """Convert error number returned by InstructionListJoints() to PathErrorFlags"""
        flags = PathErrorFlags.NoError
        evalue = int(evalue)
        if evalue == 0:
            return flags

        if round(evalue) == 20:
            # This error flag is never combined with other error flags.
            # This flag will appear with time based simulations and it means the path is feasible but RoboDK is unable to calculate
            return PathErrorFlags.InnacurateDueToLargeAxisMove

        if (evalue % 1000000000 > 99999999):
            # Non reachable target
            flags |= PathErrorFlags.InvalidArcMove

        if (evalue % 100000000 > 9999999):
            # Non reachable target
            flags |= PathErrorFlags.PathInvalidTarget

        if (evalue % 10000000 > 999999):
            # "The robot can't make a rotation so close to 180 deg. (the rotation axis is not properly defined
            flags |= PathErrorFlags.PathFlipAxis

        if (evalue % 1000000 > 99999):
            # Collision detected.
            flags |= PathErrorFlags.Collision

        if (evalue % 1000 > 99):
            # Joint 5 crosses 0 degrees. This is a singularity and it is not allowed for a linear move.
            flags |= PathErrorFlags.WristSingularity
            flags |= PathErrorFlags.PathSingularity

        elif (evalue % 10000 > 999):
            if (evalue % 10000 > 3999):
                # The robot is too close to the front/back singularity (wrist close to axis 1).
                flags |= PathErrorFlags.ShoulderSingularity
                flags |= PathErrorFlags.PathSingularity
                flags |= PathErrorFlags.PathNearSingularity

            elif (evalue % 10000 > 1999):
                flags |= PathErrorFlags.ElbowSingularity
                flags |= PathErrorFlags.PathSingularity
                flags |= PathErrorFlags.PathNearSingularity
                # Joint 3 is too close the elbow singularity.

            else:
                # Joint 5 is too close to a singularity (0 degrees).
                flags |= PathErrorFlags.WristSingularity
                flags |= PathErrorFlags.PathSingularity
                flags |= PathErrorFlags.PathNearSingularity

        if (evalue % 10 > 0):
            # There is no solution available to complete the path.
            flags |= PathErrorFlags.PathLimit

        if (evalue % 100 > 9):
            # The robot can't make a linear movement because of joint limits or the target is out of reach. Consider a Joint move instead.
            #flags |= PathErrorFlags.PathLimit
            flags |= PathErrorFlags.Kinematic

        return flags


class TargetReachError(Exception):
    """Unable to reach desired target or destination error."""
    pass


class StoppedError(Exception):
    """The user stopped the operation by selecting Escape key or moving the robot"""
    pass


class InputError(Exception):
    """Invalid input parameters provided to the API. Provide input as stated in the documentation."""
    pass


class LicenseError(Exception):
    """Invalid RoboDK license to use the requested feature."""
    pass


def RoboDKInstallFound():
    """Check if RoboDK is installed"""
    path_install = getPathRoboDK()
    return os.path.exists(path_install)


def getPathRoboDK():
    """RoboDK's executable/binary file"""
    from sys import platform as _platform
    if _platform == "linux" or _platform == "linux2":
        # Ubuntu, Linux or Debian
        return os.path.expanduser("~/RoboDK/bin/RoboDK")
    elif _platform == "darwin":
        # MacOS
        #self.APPLICATION_DIR = "/Applications/RoboDK.app/Contents/MacOS/RoboDK"
        path_app = os.path.expanduser("~") + "/Applications/RoboDK.app/Contents/MacOS/RoboDK"
        if os.path.exists(path_app):
            return path_app
        # default install directory
        return os.path.expanduser("~") + "/RoboDK/RoboDK.app/Contents/MacOS/RoboDK"

    else:
        # Windows assumed
        if sys.version_info[0] < 3:
            import _winreg
        else:
            import winreg as _winreg

        # Try to get the value from the Windows registry:
        try:
            #if True:
            # Open the key and return the handle object.
            try:
                hKey = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\RoboDK", 0, _winreg.KEY_READ | _winreg.KEY_WOW64_64KEY)
            except FileNotFoundError:
                hKey = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\RoboDK", 0, _winreg.KEY_READ | _winreg.KEY_WOW64_32KEY)

            # Read the value.
            result = _winreg.QueryValueEx(hKey, "INSTDIR")
            # Close the handle object.
            _winreg.CloseKey(hKey)
            # Return only the value from the resulting tuple (value, type_as_int).
            return result[0].replace("\\", "/") + "/bin/RoboDK.exe"
        except:  # FileNotFoundError:
            print("RoboDK was not installed properly. Install RoboDK from www.robodk.com/download.")

        return "C:/RoboDK/bin/RoboDK.exe"


def getPathIcon():
    iconpath = getPathRoboDK()
    if iconpath.endswith(".exe"):
        iconpath = iconpath[:-4]
    iconpath = iconpath + '.ico'
    return iconpath


def import_install(module_name, pip_name=None, rdk=None, upgrade_pip=False):
    """Import a module by first installing it if the corresponding package is not available. If the module name does not match the pip install command, provide the pip_name for install purposes.
    Optionally, you can pass the RoboDK API Robolink object to see install progress in RoboDK's status bar.

    .. code-block:: python

        # If you want to install opencv for Python and pyserial you should use:
        import_install("opencv", "opencv-python", RDK)
        import_install("serial", "pyserial", RDK)

        # If the name of the module matches the package you can just pass the name of the module.
        # Example:
        import_install("xlrd", rdk=RDK)

        # You can also use version specifiers (https://peps.python.org/pep-0440/#version-specifiers):
        import_install('numpy', 'numpy>=1.23')
        import_install('pandas', 'pandas~=1.4')

    """
    try:
        exec('import ' + module_name, globals())
        return

    except ModuleNotFoundError:
        import sys
        import subprocess
        import io

        def execute(cmd):
            print("Running command:")
            print(cmd)
            print("...")
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)  #, universal_newlines=True)
            for line in io.TextIOWrapper(proc.stdout, encoding="utf-8"):  # or another encoding
                # display line output
                line = line.strip()
                print(line)
                if rdk:
                    rdk.ShowMessage(line, False)

        if pip_name is None:
            pip_name = module_name

        msg = "Installing required module: " + module_name + " ..."
        print(msg)

        if rdk:
            rdk.ShowMessage(msg, False)

        try:
            if upgrade_pip:
                cmd = sys.executable + ' -m pip install --upgrade pip'
                execute(cmd)
            cmd = sys.executable + ' -m pip install ' + pip_name
            execute(cmd)
            exec('import ' + module_name, globals())

        except:
            msg = "Unable to load or install <strong>%s</strong>. Make sure you have internet connection and administrator privileges" % module_name
            print(msg)
            if rdk:
                rdk.ShowMessage(msg, True)

            raise ImportError(msg)


def EmbedWindow(window_name, docked_name=None, size_w=-1, size_h=-1, pid=0, area_add=1, area_allowed=15, timeout=500, port=None, args=[]):
    """Embed a window from a separate process in RoboDK as a docked window. Returns True if successful.

    :param str window_name: The name of the window currently open. Make sure the window name is unique and it is a top level window
    :param str docked_name: Name of the docked tab in RoboDK (optional, if different from the window name)
    :param int pid: Process ID (optional)
    :param int area_add: Set to 1 (right) or 2 (left) (default is 1)
    :param int area_allowed: Areas allowed (default is 15:no constrain)
    :param int timeout: Timeout to abort attempting to embed the window

    .. code-block:: python
        :caption: Example to embed a window as a docked RoboDK window

        from tkinter import *
        from robodk.robolink import *
        import threading

        # Create a new window
        window = tkinter.Tk()

        # Close the window
        def onClose():
            window.destroy()
            quit(0)

        # Trigger Select button
        # IMPORTANT: We need to run the action on a separate thread because
        # (otherwise, if we want to interact with RoboDK window it will freeze)
        def on_btnSelect():
            def thread_btnSelect():
                # Run button action (example to select an item and display its name)
                RDK = Robolink()
                item = RDK.ItemUserPick('Select an item')
                if item.Valid():
                    RDK.ShowMessage("You selected the item: " + item.Name())

            threading.Thread(target=thread_btnSelect).start()

        # Set the window title (must be unique for the docking to work, try to be creative!)
        window_title = 'RoboDK API Docked Window'
        window.title(window_title)

        # Delete the window when we close it
        window.protocol("WM_DELETE_WINDOW", onClose)

        # Add a button (Select action)
        btnSelect = Button(window, text='Trigger on_btnSelect', height=5, width=60, command=on_btnSelect)
        btnSelect.pack(fill=X)

        # Embed the window
        EmbedWindow(window_title)

        # Run the window event loop. This is like an app and will block until we close the window
        window.mainloop()

    """

    #import threading
    def t_dock(wname, dname, sz_w, sz_h, p, a_add, a_allowed, tout):
        # it is important to run this on a parallel thread to not block the main window events in Python
        rdk = Robolink(port=port, args=args)
        if rdk.EmbedWindow(wname, dname, sz_w, sz_h, p, a_add, a_allowed, tout):
            print("Window docked successfully: " + window_name)
        else:
            print("Failed to dock window: " + window_name)

    t = threading.Thread(target=t_dock, args=(window_name, docked_name, size_w, size_h, pid, area_add, area_allowed, timeout))
    t.start()


class Robolink:
    """
    The Robolink class is the link to RoboDK and allows creating macros for Robodk, simulate applications and generate programs offline.
    Any interaction is made through \"items\" (Item() objects). An item is an object in the robodk tree (it can be either a robot, an object, a tool, a frame, a program, ...).

    :param str robodk_ip: IP of the RoboDK API server (default='localhost')
    :param int port: Port of the RoboDK API server (default=None, it will use the default value)
    :param list args: Command line arguments to pass to RoboDK on startup (for example: '/NOSPLASH /NOSHOW' should be passed as args=['/NOSPLASH','/NOSHOW'] to not display RoboDK). Arguments have no effect if RoboDK is already running.\n
        For more information: `RoboDK list of arguments on startup <https://robodk.com/doc/en/RoboDK-API.html#CommandLine>`_.
    :param str robodk_path: RoboDK installation path. It defaults to RoboDK's default path (C:/RoboDK/bin/RoboDK.exe on Windows or /Applications/RoboDK.app/Contents/MacOS/RoboDK on Mac)
    :param bool close_std_out: Close RoboDK standard output path. No RoboDK console output will be shown.
    :param bool quit_on_close: Close RoboDK when this instance of Robolink disconnect. It has no effect if RoboDK is already running.
    :param com_object: Custom communication class (allows using WebSockets or other custom implementations). It defaults to socket communication.
    :param bool skipstatus: Skip the status flag for operations that only wait for the command response status and do not return anything (assumes the command always completes successfully).


    .. code-block:: python
        :caption: Example of a RoboDK API initialization

        from robodk.robolink import *

        # Connect to the RoboDK API
        RDK = Robolink()

        # Retrieve all items and print their names
        list_items = RDK.ItemList()
        for item in list_items:
            print(item.Name())

    .. code-block:: python
        :caption: Force starting a new RoboDK hidden instance and output debug information

        from robodk.robolink import *

        # Connect to the RoboDK API
        RDK = Robolink(args=["-NEWINSTANCE", "-NOUI", "-SKIPINI", "-EXIT_LAST_COM"])

        # Add a reference frame
        RDK.AddFrame("My reference frame")
        RDK.setPose(transl(100,200,300) * rotz(pi/2))

        # Retrieve all items and print their names (just a reference frame)
        list_items = RDK.ItemList()
        for item in list_items:
            print(item.Name())

        # Close RoboDK
        RDK.CloseRoboDK()

        # Example command line arguments:
        # -NEWINSTANCE: Forces using a new instance
        # -NOUI: Run RoboDK behind the scenes (without OpenGL context)
        # -SKIPINI: Skip using RoboDK's INI settings (global settings), this provides a faster startup
        # -EXIT_LAST_COM: Exit RoboDK when the last API client connected closes
        # -DEBUG: Run in debug mode (outputs information in the console)
        #
        # Follow these steps to see an extended list of command line arguments:
        # 1- Select Tools-Run Script
        # 2- Select ShowCommands
        #
        # More information here:
        #    https://robodk.com/doc/en/RoboDK-API.html#CommandLine

    .. seealso:: :func:`~robodk.robolink.Robolink.Item`, :func:`~robodk.robolink.Item.Name`, :func:`~robodk.robolink.Item.setPose`, :func:`~robodk.robolink.Robolink.CloseRoboDK`

    .. seealso:: :func:`~robodk.robolink.Robolink.AddFile`, :func:`~robodk.robolink.Robolink.AddFrame`, :func:`~robodk.robolink.Robolink.AddTarget`, :func:`~robodk.robolink.Robolink.AddProgram`

    """

    # checks that provided items exist in memory and poses are homogeneous
    SAFE_MODE = 1

    # if AUTO_UPDATE is 1, updating and rendering objects the 3D the scene will be delayed until 100 ms after the last call (this value can be changed in Tools-Options-Other-API Render delay, or also using the RoboDK.Command('AutoRenderDelay', value) and RoboDK.Command('AutoRenderDelayMax', value)
    AUTO_UPDATE = 0

    # If _SkipStatus flag is True, we are skipping the status flag for operations that only wait for the status and do not return anything
    # We assume the command always completes successfully
    _SkipStatus = False

    # IP address of the simulator (localhost if it is the same computer), otherwise, use RL = Robolink('yourip') to set to a different IP
    IP = 'localhost'

    # port to start looking for the RoboDK API connection (Tools-Options-Other-RoboDK API)
    PORT_START = 20500

    # port to stop looking for the RoboDK API connection
    PORT_END = 20500

    # timeout for communication, in seconds
    TIMEOUT = 10

    # Add Cameras as items (added option to use cameras as items at version v5.0.0)
    CAMERA_AS_ITEM = True

    # activate nodelay option (faster, requires more resources)
    NODELAY = False

    # file path to the robodk program (executable). As an example, on Windows it should be: C:/RoboDK/bin/RoboDK.exe
    APPLICATION_DIR = ''

    DEBUG = False  # Debug output through console
    COM = None  # tcpip com
    _lock = None
    ARGUMENTS = []  # Command line arguments to RoboDK, such as /NOSPLASH /NOSHOW to not display RoboDK. It has no effect if RoboDK is already running.
    CLOSE_STD_OUT = False  # Close standard output for roboDK (RoboDK console output will no longer be visible)
    PORT = -1  # current port
    BUILD = 0  # This variable holds the build id and is used for version checking

    NEW_INSTANCE = None  # If not None, a new RoboDK instance was spawned when initiating connection
    QUIT_ON_CLOSE = False  # If true, new instances of RoboDK will be closed when this object is deleted

    # Remember last status message
    LAST_STATUS_MESSAGE = ''

    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    def _setTimeout(self, timeout_sec=30):
        """Set the communication timeout (in seconds)."""
        # Change the default timeout here, in seconds:
        with self._lock:
            self.TIMEOUT = timeout_sec  # in seconds
            self.COM.settimeout(self.TIMEOUT)

    def _is_connected(self):
        """Returns 1 if connection is valid, returns 0 if connection is invalid"""
        if not self.COM:
            return 0
        connected = 1
        #try:
        #    self.COM.settimeout(0)
        #    check = self.COM.recv(1)
        #except:
        #    connected = 0
        #
        #self.COM.settimeout(self.TIMEOUT)
        return connected

    def _check_connection(self):
        """If we are not connected it will attempt a connection, if it fails, it will throw an error"""
        if not self._is_connected() and self.Connect() < 1:
            raise Exception('Unable to connect')
        #To do: Clear input buffer.

    def _check_status(self):
        """This procedure checks the status of the connection"""
        status = self._rec_int()
        if status == 0:
            # everything is OK
            self.LAST_STATUS_MESSAGE = ''

        elif status > 0 and status < 10:
            self.LAST_STATUS_MESSAGE = 'Unknown error'
            if status == 1:
                self.LAST_STATUS_MESSAGE = 'Invalid item provided: The item identifier provided is not valid or it does not exist.'
            elif status == 2:  # output warning
                self.LAST_STATUS_MESSAGE = self._rec_line()
                print('WARNING: ' + self.LAST_STATUS_MESSAGE)
                return 0
            elif status == 3:  # output error
                self.LAST_STATUS_MESSAGE = self._rec_line()
                raise Exception(self.LAST_STATUS_MESSAGE)
            elif status == 9:
                self.LAST_STATUS_MESSAGE = 'Invalid license. Purchase a license online (www.robodk.com) or contact us at info@robodk.com.'
            print(self.LAST_STATUS_MESSAGE)
            raise Exception(self.LAST_STATUS_MESSAGE)

        elif status < 100:
            # Since RoboDK 4.0 we raise dedicated errors
            self.LAST_STATUS_MESSAGE = self._rec_line()
            if status == 10:
                raise TargetReachError(self.LAST_STATUS_MESSAGE)

            elif status == 11:
                raise StoppedError(self.LAST_STATUS_MESSAGE)

            elif status == 12:
                raise InputError(self.LAST_STATUS_MESSAGE)

            elif status == 13:
                raise LicenseError(self.LAST_STATUS_MESSAGE)

            else:
                # Generic error exception
                raise Exception(self.LAST_STATUS_MESSAGE)

        else:
            self.LAST_STATUS_MESSAGE = 'Problems running function'
            raise Exception(self.LAST_STATUS_MESSAGE)

        return status

    def _check_color(self, color):
        """Formats the color in a vector of size 4x1 and ranges [0,1]"""
        if not isinstance(color, list) or len(color) < 3 or len(color) > 4:
            raise Exception('The color vector must be a list of 3 or 4 values')
        if len(color) == 3:
            color.append(1)
        if max(color) > 1 or min(color) < -1:
            print("WARNING: Color provided is not in the range [0,1] ([r,g,b,a])")
        return color

    def _send_line(self, string=None):
        """Sends a string of characters with a \\n"""
        string = string.replace('\n', '<br>')
        if sys.version_info[0] < 3:
            self.COM.send(bytes(string + '\n'))  # Python 2.x only
        else:
            self.COM.send(bytes(string + '\n', 'utf-8'))  # Python 3.x only

    def _rec_line(self):
        """Receives a string. It reads until if finds LF (\\n)"""
        bytes_list = []  # this method is significantly faster than a byte string
        chari = self.COM.recv(1)
        while chari != b'\n':  # read until LF
            bytes_list.append(chari)
            chari = self.COM.recv(1)
        return str(b''.join(bytes_list).decode('utf-8'))  # python 2 and python 3 compatible

    def _send_item(self, item):
        """Sends an item pointer"""
        if isinstance(item, Item):
            self.COM.send(struct.pack('>Q', item.item))  #q=unsigned long long (64 bits), d=float64
            return
        if item is None:
            item = 0
        self.COM.send(struct.pack('>Q', item))  #q=unsigned long long (64 bits), d=float64

    def _rec_item(self):
        """Receives an item pointer"""
        buffer = self.COM.recv(8)
        item = struct.unpack('>Q', buffer)  #q=unsigned long long (64 bits), d=float64
        buffer2 = self.COM.recv(4)
        itemtype = struct.unpack('>i', buffer2)
        return Item(self, item[0], itemtype[0])

    def _send_bytes(self, data):
        """Sends a byte array"""
        if isinstance(data, str):
            data = bytes(data, 'utf-8')
        if not isinstance(data, bytes):
            data = bytes(data)

        self.COM.send(struct.pack('>I', len(data)))  #q=unsigned long long (64 bits), d=float64
        self.COM.send(data)

    def _rec_bytes(self):
        """Receives a byte array"""
        buffer = self.COM.recv(4)
        bytes_len = struct.unpack('>I', buffer)[0]  #q=unsigned long long (64 bits), d=float64
        bytes_list = []  # this method is significantly faster than a byte string
        bytes_count = 0
        bytes_remaining = bytes_len
        while bytes_remaining > 0:
            data = self.COM.recv(bytes_remaining)
            bytes_list.append(data)
            bytes_count += len(data)
            bytes_remaining = bytes_len - bytes_count
        return b''.join(bytes_list)

    def _send_ptr(self, ptr_h):
        """Sends a generic pointer"""
        self.COM.send(struct.pack('>Q', ptr_h))  #q=unsigned long long (64 bits), d=float64

    def _rec_ptr(self):
        """Receives a generic pointer"""
        buffer = self.COM.recv(8)
        ptr_h = struct.unpack('>Q', buffer)  #q=unsigned long long (64 bits), d=float64
        return ptr_h[0]  #return ptr_h

    def _send_pose(self, pose):
        """Sends a pose (4x4 matrix)"""
        #if not pose.isHomogeneous(): # this check is expansive!
        #    print("Warning: pose is not homogeneous!")
        #    print(pose)
        posebytes = b''
        for j in range(4):
            for i in range(4):
                posebytes = posebytes + struct.pack('>d', pose[i, j])
        self.COM.send(posebytes)

    def _rec_pose(self):
        """Receives a pose (4x4 matrix)"""
        posebytes = self.COM.recv(16 * 8)
        posenums = struct.unpack('>16d', posebytes)
        pose = robomath.Mat(4, 4)
        cnt = 0
        for j in range(4):
            for i in range(4):
                pose[i, j] = posenums[cnt]
                cnt = cnt + 1
        return pose

    def _send_xyz(self, pos):
        """Sends an xyz vector"""
        posbytes = b''
        for i in range(3):
            posbytes = posbytes + struct.pack('>d', pos[i])
        self.COM.send(posbytes)

    def _rec_xyz(self):
        """Receives an xyz vector"""
        posbytes = self.COM.recv(3 * 8)
        posnums = struct.unpack('>3d', posbytes)
        pos = [0, 0, 0]
        for i in range(3):
            pos[i] = posnums[i]
        return pos

    def _send_int(self, num):
        """Sends an int (32 bits)"""
        if isinstance(num, float):
            num = round(num)
        elif not isinstance(num, int):
            num = num[0]
        self.COM.send(struct.pack('>i', num))

    def _rec_int(self):
        """Receives an int (32 bits)"""
        buffer = self.COM.recv(4)
        num = struct.unpack('>i', buffer)
        return num[0]

    def _send_array(self, values):
        """Sends an array of doubles"""
        if not isinstance(values, list):  #if it is a Mat() with joints
            values = (values.tr()).rows[0]
        nval = len(values)
        self._send_int(nval)
        if nval > 0:
            buffer = b''
            for i in range(nval):
                buffer = buffer + struct.pack('>d', values[i])
            self.COM.send(buffer)

    def _rec_array(self):
        """Receives an array of doubles"""
        nvalues = self._rec_int()
        if nvalues > 0:
            buffer = self.COM.recv(8 * nvalues)
            values = list(struct.unpack('>' + str(nvalues) + 'd', buffer))
            #values = fread(self.COM, nvalues, 'double')
        else:
            values = [0]
        return robomath.Mat(values)

    def _send_matrix(self, mat):
        """Sends a 2 dimensional matrix (nxm)"""
        if mat is None:
            self._send_int(0)
            self._send_int(0)
            return
        if type(mat) == list:
            mat = robomath.Mat(mat).tr()
        size = mat.size()
        self._send_int(size[0])
        self._send_int(size[1])
        for j in range(size[1]):
            matbytes = b''
            for i in range(size[0]):
                matbytes = matbytes + struct.pack('>d', mat[i, j])
            self.COM.send(matbytes)

    def _rec_matrix(self):
        """Receives a 2 dimensional matrix (nxm)"""
        size1 = self._rec_int()
        size2 = self._rec_int()
        recvsize = size1 * size2 * 8
        BUFFER_SIZE = 512
        if recvsize > 0:
            bytes_list = []  # this method is significantly faster than a byte string
            bytes_count = 0
            bytes_remaining = min(recvsize, BUFFER_SIZE)
            while bytes_remaining > 0:
                data = self.COM.recv(bytes_remaining)
                bytes_list.append(data)
                bytes_count += len(data)
                bytes_remaining = min(recvsize - bytes_count, BUFFER_SIZE)
            matnums = struct.unpack('>' + str(size1 * size2) + 'd', b''.join(bytes_list))
            mat = robomath.Mat(size1, size2)
            cnt = 0
            for j in range(size2):
                for i in range(size1):
                    mat.rows[i][j] = matnums[cnt]
                    cnt = cnt + 1
        else:
            mat = robomath.Mat(0, 0)
        return mat

    def _moveX(self, target, itemrobot, movetype, blocking=True):
        """Performs a linear or joint movement. Use MoveJ or MoveL instead."""
        with self._lock:
            #self._check_connection();
            itemrobot.WaitMove()  # checks connection
            if blocking:
                command = 'MoveXb'
            else:
                command = 'MoveX'

            self._send_line(command)
            self._send_int(movetype)
            if isinstance(target, Item):  # target is an item
                self._send_int(3)
                self._send_array([])
                self._send_item(target)
            elif isinstance(target, list) or target.size() != (4, 4):  # target are joints
                self._send_int(1)
                self._send_array(target)
                self._send_item(0)
            elif target.size() == (4, 4):  # target is a pose
                self._send_int(2)
                mattr = target.tr()
                self._send_array(mattr.rows[0] + mattr.rows[1] + mattr.rows[2] + mattr.rows[3])
                self._send_item(0)
            else:
                raise Exception('Invalid input values')
            self._send_item(itemrobot)
            self._check_status()
            if blocking:
                #itemrobot.WaitMove()
                self.COM.settimeout(360000)
                self._check_status()  #will wait here
                self.COM.settimeout(self.TIMEOUT)

    def MoveC(self, target1, target2, itemrobot, blocking=True):
        """Performs a circular movement. Use robot.MoveC instead."""
        with self._lock:
            #self._check_connection();
            itemrobot.WaitMove()  # checks connection
            if blocking:
                command = 'MoveCb'
            else:
                command = 'MoveC'

            self._send_line(command)
            self._send_int(MOVE_TYPE_CIRCULAR)
            if isinstance(target1, Item):  # target1 is an item
                self._send_int(3)
                self._send_array([])
                self._send_item(target1)
            elif isinstance(target1, list) or target1.size() != (4, 4):  # target1 are joints
                self._send_int(1)
                self._send_array(target1)
                self._send_item(0)
            elif target1.size() == (4, 4):  # target1 is a pose
                self._send_int(2)
                mattr = target1.tr()
                self._send_array(mattr.rows[0] + mattr.rows[1] + mattr.rows[2] + mattr.rows[3])
                self._send_item(0)
            else:
                raise Exception('Invalid input value for target 1')
            if isinstance(target2, Item):  # target1 is an item
                self._send_int(3)
                self._send_array([])
                self._send_item(target2)
            elif isinstance(target2, list) or target2.size() != (4, 4):  # target2 are joints
                self._send_int(1)
                self._send_array(target2)
                self._send_item(0)
            elif target2.size() == (4, 4):  # target2 is a pose
                self._send_int(2)
                mattr = target2.tr()
                self._send_array(mattr.rows[0] + mattr.rows[1] + mattr.rows[2] + mattr.rows[3])
                self._send_item(0)
            else:
                raise Exception('Invalid input value for target 2')
            self._send_item(itemrobot)
            self._check_status()
            if blocking:
                #itemrobot.WaitMove()
                self.COM.settimeout(360000)
                self._check_status()  #will wait here
                self.COM.settimeout(self.TIMEOUT)

    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    def __init__(self, robodk_ip='localhost', port=None, args=[], robodk_path=None, close_std_out=False, quit_on_close=False, com_object=None, skipstatus=False):
        """A connection is attempted upon creation of the object
        In  1 (optional) : robodk_ip -> IP of the RoboDK API server (default='localhost')
        In  2 (optional) : port -> Port of the RoboDK API server (default=None)
        In  3 (optional) : args -> Command line arguments, as a list, to pass to RoboDK on startup (such as ['/NOSPLASH','/NOSHOW']), to not display RoboDK. It has no effect if RoboDK is already running.
        In  4 (optional) : robodk_path -> RoboDK path. Leave it to the default None for the default path (C:/RoboDK/bin/RoboDK.exe).
        In  5 (optional) : close_std_out -> Close RoboDK standard output path. No RoboDK console output will be shown.
        In  6 (optional) : quit_on_close -> Close RoboDK when this instance of Robolink disconnect. It has no effect if RoboDK is already running.
        In  7 (optional) : com_object -> Custom communication class (allows using WebSockets or other custom implementations).
        In  8 (optional) : skipstatus -> Skip the status flag for operations that only wait for the command response status and do not return anything (assumes the command always completes successfully).
        """
        self._SkipStatus = skipstatus
        self._customCOM = com_object
        self._lock = threading.Lock()
        with self._lock:
            if type(args) is str:
                if args != "":
                    args = [args]
                else:
                    args = []

            self.IP = robodk_ip
            self.ARGUMENTS = args
            self.CLOSE_STD_OUT = close_std_out
            self.QUIT_ON_CLOSE = quit_on_close

            if robodk_path is not None:
                self.APPLICATION_DIR = robodk_path
            else:
                self.APPLICATION_DIR = getPathRoboDK()

            if ('/API_NODELAY' in self.ARGUMENTS or '-API_NODELAY' in self.ARGUMENTS):
                self.NODELAY = True

            if port is not None:
                self.PORT_START = port
                self.PORT_END = port
                self.ARGUMENTS.append("-PORT=%i" % port)

            elif "ROBODK_API_PORT" in os.environ:
                port = int(os.environ["ROBODK_API_PORT"])
                self.PORT_START = port
                self.PORT_END = port
                self.ARGUMENTS.append("-PORT=%i" % port)

            elif ('/NEWINSTANCE' in self.ARGUMENTS or '-NEWINSTANCE' in self.ARGUMENTS):
                from socket import socket
                if sys.version_info.major >= 3:
                    with socket() as s:
                        s.bind(('', 0))
                        port = s.getsockname()[1]
                        print("Using available port %i" % port)
                        self.PORT_START = port
                        self.PORT_END = port
                        self.ARGUMENTS.append("-PORT=%i" % port)
                else:
                    sock = socket()
                    sock.bind(('', 0))
                    port = sock.getsockname()[1]
                    print("Using available port %i" % port)
                    self.PORT_START = port
                    self.PORT_END = port
                    self.ARGUMENTS.append("-PORT=%i" % port)
                    sock.close()

            if "-DEBUG" in self.ARGUMENTS or "/DEBUG" in self.ARGUMENTS:
                self.DEBUG = True
            elif self.DEBUG:
                self.ARGUMENTS.append("-DEBUG")

        # This is already locked
        self.Connect()

    def __del__(self):
        self.Disconnect()

    def _verify_connection(self):
        """Verify that we are connected to the RoboDK API server"""
        # Imortant! this should not thread locked
        use_new_version = True
        if self._SkipStatus:
            # Todo: Remove on future versions when RoboDK for Web supports it
            use_new_version = False

        if use_new_version:
            self._send_line('RDK_API')
            self._send_array([self.SAFE_MODE, self.AUTO_UPDATE, 1.0 if self._SkipStatus else 0])

            # still used for new version, do not uncomment these next 3 lines
            #if self._SkipStatus:
            #    self.COM.flush()
            #    return True

            response = self._rec_line()
            ver_api = self._rec_int()
            self.BUILD = self._rec_int()

            self._check_status()
            return response == 'RDK_API'

        else:
            self._send_line('CMD_START')
            if not self._SkipStatus:
                self._send_line(str(self.SAFE_MODE) + ' ' + str(self.AUTO_UPDATE))
            else:
                self._send_line(str(self.SAFE_MODE) + ' ' + str(self.AUTO_UPDATE) + " 1")

            #fprintf(self.COM, sprintf('%i %i'), self.SAFE_MODE, self.AUTO_UPDATE))# appends LF
            if self._SkipStatus:
                self.COM.flush()
                return True

            response = self._rec_line()
            if response == 'READY':
                ok = 1
            else:
                ok = 0
            return ok

    def _require_build(self, build_required):
        if self.BUILD == 0:
            # unknown build number. Use new API hello command
            return True

        if self.BUILD < build_required:
            raise Exception("This function is unavailable. Update RoboDK to use this API feature: https://robodk.com/download")
        return True

    def Disconnect(self):
        """Stops the communication with RoboDK. If setRunMode is set to RUNMODE_MAKE_ROBOTPROG for offline programming, any programs pending will be generated."""
        if self.QUIT_ON_CLOSE and self.NEW_INSTANCE is not None:
            print('Stopping %s\n' % self.APPLICATION_DIR)
            self.CloseRoboDK()
            with self._lock:
                self.NEW_INSTANCE.wait()
                self.NEW_INSTANCE = None

        with self._lock:
            if self.COM:
                self.COM.close()

    def Finish(self):
        """Stops the communication with RoboDK. If setRunMode is set to RUNMODE_MAKE_ROBOTPROG for offline programming, any programs pending will be generated.

        .. seealso:: :func:`~robodk.robolink.Robolink.setRunMode`, :func:`~robodk.robolink.Robolink.AddProgram`, :func:`~robodk.robolink.Robolink.ProgramStart`"""
        self.Disconnect()

    def NewLink(self):
        """Reconnect the API using a different communication link."""
        try:
            #if True:
            with self._lock:
                import socket
                #self.COM.close()
                if self._customCOM:
                    self.COM = self._customCOM()
                else:
                    self.COM = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                if self.NODELAY:
                    self.COM.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

                self.COM.connect((self.IP, self.PORT))
                connected = self._is_connected()
                if not (connected > 0):
                    print("Failed to reconnect (1)")
                    return

                # Validate the connection
                self._verify_connection()
                self.COM.settimeout(self.TIMEOUT)

        except:
            print("Failed to reconnect (2)")

    def isNewInstance(self):
        return self.NEW_INSTANCE is not None

    def Connect(self):
        """Establish a connection with RoboDK. If RoboDK is not running it will attempt to start RoboDK from the default installation path (otherwise APPLICATION_DIR must be set properly).
        If the connection succeeds it returns 1, otherwise it returns 0"""

        def start_robodk(command):
            print('Starting %s\n' % self.APPLICATION_DIR)
            import subprocess

            #import time
            #tstart = time.time()

            def output_reader(proc):
                for line in iter(proc.stdout.readline, b''):
                    ln = str(line.decode("utf-8")).strip()
                    if ln:
                        print(ln)

            from sys import platform as _platform
            if self.NEW_INSTANCE is not None:
                print('Warning: A new instance of RoboDK is being created.')
            self.NEW_INSTANCE = None
            if (_platform == "linux" or _platform == "linux2") and os.path.splitext(command[0])[1] == ".sh":
                self.NEW_INSTANCE = subprocess.Popen(command, shell=True, executable='/bin/bash', stdout=subprocess.PIPE)
            elif _platform == "darwin":
                # Popen does not work sometimes (such as running from fusion)
                #startapp = ["/usr/bin/open", command[0].split("/Content")[0]]
                try:
                    #self.NEW_INSTANCE = subprocess.Popen(command,stdout=subprocess.PIPE)
                    self.NEW_INSTANCE = subprocess.Popen(command, stdout=subprocess.PIPE)
                except Exception as e:
                    print(str(e))
                    return False

                #self.NEW_INSTANCE = subprocess.call(startapp)
            else:
                self.NEW_INSTANCE = subprocess.Popen(command, stdout=subprocess.PIPE)

            emptyln = 0
            if self.NEW_INSTANCE:
                while True:
                    lineb = self.NEW_INSTANCE.stdout.readline()
                    line = str(lineb.decode("utf-8")).strip()
                    if len(lineb) > 0:
                        print(line)
                        emptyln = 0
                    else:
                        emptyln += 1

                    if emptyln > 10:
                        print("RoboDK Application not properly started. Command:")
                        print(str(command))
                        break

                    if 'running' in line.lower():
                        #telapsed = time.time() - tstart
                        #print("RoboDK startup time: %.3f" % telapsed)
                        break

                #if self.DEBUG:
                # Important! Make sure we consume stdout (at least in Debug mode)
                if self.CLOSE_STD_OUT:
                    self.NEW_INSTANCE.stdout.close()
                else:
                    #import threading
                    t = threading.Thread(target=output_reader, args=(self.NEW_INSTANCE,))
                    t.start()

            return True

            #with subprocess.Popen(command, stdout=subprocess.PIPE, bufsize=1, universal_newlines=True) as self.NEW_INSTANCE:
            #    self._ProcessID = self.NEW_INSTANCE.pid
            #    for line in self.NEW_INSTANCE.stdout:
            #        line_ok = line.strip()
            #        print(line_ok)
            #        if 'running' in line_ok.lower():
            #            print("RoboDK is running")
            #            return #does not return!!

        connected = 0
        with self._lock:
            import socket
            for i in range(2):
                for port in range(self.PORT_START, self.PORT_END + 1):
                    # Prevent warning message by closing the previous socket
                    if self.COM:
                        self.COM.close()

                    if self._customCOM:
                        self.COM = self._customCOM()
                    else:
                        self.COM = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                    if self.NODELAY:
                        self.COM.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

                    self.COM.settimeout(1)
                    try:
                        self.COM.connect((self.IP, port))
                        connected = self._is_connected()
                        if connected > 0:
                            self.COM.settimeout(self.TIMEOUT)
                            break

                    except:
                        connected = connected

                if connected > 0:  # if status is closed, try to open application
                    self.PORT = port
                    break

                elif i == 0:
                    if self.IP != 'localhost':
                        break

                    try:
                        if self.APPLICATION_DIR == '':
                            if self.COM:
                                self.COM = None
                            connected = 0
                            return connected
                        command = [self.APPLICATION_DIR]
                        if self.ARGUMENTS:
                            command += self.ARGUMENTS

                        if not start_robodk(command):
                            if self.COM:
                                self.COM = None
                            connected = 0
                            return connected
                        #import time
                        #time.sleep(5) # wait for RoboDK to start and check network license.
                    except Exception as e:
                        print(str(e))
                        raise Exception('Application path is not correct or could not start: ' + self.APPLICATION_DIR)

            if connected > 0 and not self._verify_connection():
                connected = 0

        return connected

    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # public methods
    def Item(self, name, itemtype=None):
        """Returns an item by its name. If there is no exact match it will return the last closest match.
        Specify what type of item you are looking for with itemtype. This is useful if 2 items have the same name but different type.
        (check variables ITEM_TYPE_*)

        :param str name: name of the item (name of the item shown in the RoboDK station tree)
        :param int itemtype: type of the item to be retrieved (avoids confusion if there are similar name matches). Use ITEM_TYPE_*.

        .. code-block:: python
            :caption: Available Item types

            ITEM_TYPE_STATION=1             # station item (.rdk files)
            ITEM_TYPE_ROBOT=2               # robot item (.robot files)
            ITEM_TYPE_FRAME=3               # reference frame item
            ITEM_TYPE_TOOL=4                # tool item (.tool files or tools without geometry)
            ITEM_TYPE_OBJECT=5              # object item (.stl, .step, .iges, ...)
            ITEM_TYPE_TARGET=6              # target item
            ITEM_TYPE_PROGRAM=8             # program item (made using the GUI)
            ITEM_TYPE_PROGRAM_PYTHON=10     # Python program or macro

        .. seealso:: :func:`~robodk.robolink.Robolink.ItemList`, :func:`~robodk.robolink.Robolink.ItemUserPick`

        .. seealso:: :func:`~robodk.robolink.Item.Name`, :func:`~robodk.robolink.Item.Pose`, :func:`~robodk.robolink.Item.setPose`, :func:`~robodk.robolink.Item.setParent`, :func:`~robodk.robolink.Item.setJoints`, :func:`~robodk.robolink.Item.MoveJ`, :func:`~robodk.robolink.Item.MoveL`

        Example:

        .. code-block:: python

            from robodk.robolink import *           # import the robolink library
            RDK = Robolink()                        # connect to the RoboDK API (RoboDK starts if it has not started
            tool  = RDK.Item('Tool')                # Retrieve an item named tool
            robot = RDK.Item('', ITEM_TYPE_ROBOT)   # the first available robot

        """
        with self._lock:
            if type(name) is not str:
                raise Exception("Invalid name: provide a name as a string. Item names are visible in the RoboDK tree.")

            self._check_connection()
            if itemtype is None:
                command = 'G_Item'
                self._send_line(command)
                self._send_line(name)
            else:
                command = 'G_Item2'
                self._send_line(command)
                self._send_line(name)
                self._send_int(itemtype)
            item = self._rec_item()  #     item = fread(com, 2, 'ulong');% ulong is 32 bits!!!
            self._check_status()
            return item

    def ItemList(self, filter=None, list_names=False):
        """Returns a list of items (list of name or pointers) of all available items in the currently open station of RoboDK.

        :param int filter: (optional) Filter the list by a specific item type (ITEM_TYPE_*). For example: RDK.ItemList(filter = ITEM_TYPE_ROBOT)
        :param int list_names: (optional) Set to True to return a list of names instead of a list of :class:`.Item`

        .. seealso:: :func:`~robodk.robolink.Robolink.Item`, :func:`~robodk.robolink.Robolink.ItemUserPick`
        """
        with self._lock:
            self._check_connection()
            retlist = []
            if list_names:
                if filter is None:
                    command = 'G_List_Items'
                    self._send_line(command)
                else:
                    command = 'G_List_Items_Type'
                    self._send_line(command)
                    self._send_int(filter)
                count = self._rec_int()
                for i in range(count):
                    namei = self._rec_line()
                    retlist.append(namei)
            else:
                if filter is None:
                    command = 'G_List_Items_ptr'
                    self._send_line(command)
                else:
                    command = 'G_List_Items_Type_ptr'
                    self._send_line(command)
                    self._send_int(filter)
                count = self._rec_int()
                for i in range(count):
                    itemi = self._rec_item()
                    retlist.append(itemi)
            self._check_status()
            return retlist

    def ItemUserPick(self, message="Pick one item", itemtype_or_list=None):
        """Shows a RoboDK popup to select one Item from the open station.
        An item type (ITEM_TYPE_*) can be specified to filter desired items. If no type is specified, all items are selectable.

        Note: If only one Item is available, the Item is selected and return without prompting the user.
        If a candidate Item is currently selected in the RoboDK tree, the Item is selected and return without prompting the user.

        Example:

        .. code-block:: python

            RDK.ItemUserPick("Pick a robot", ITEM_TYPE_ROBOT)
            RDK.ItemUserPick("Pick a from a list", [item1, item2, item3])

        :param str message: message to display
        :param int itemtype_or_list: filter choices by a specific item type (ITEM_TYPE_*) or provide a list of items to choose from

        .. seealso:: :func:`~robodk.robolink.Robolink.Item`, :func:`~robodk.robolink.Robolink.ItemList`
        """

        with self._lock:
            if itemtype_or_list is None:
                itemtype_or_list = -1

            if type(itemtype_or_list) is int:
                self._check_connection()
                command = 'PickItem'
                self._send_line(command)
                self._send_line(message)
                self._send_int(itemtype_or_list)

            else:
                self._check_connection()
                command = 'PickItemList'
                self._send_line(command)
                self._send_line(message)
                self._send_int(len(itemtype_or_list))
                for itm in itemtype_or_list:
                    self._send_item(itm)

            self.COM.settimeout(3600)  # wait up to 1 hour for user input
            item = self._rec_item()
            self.COM.settimeout(self.TIMEOUT)
            self._check_status()
            return item

    def ShowRoboDK(self):
        """Show or raise the RoboDK window

        .. seealso:: :func:`~robodk.robolink.Robolink.setWindowState`"""
        with self._lock:
            self._check_connection()
            command = 'RAISE'
            self._send_line(command)
            self._check_status()

    def HideRoboDK(self):
        """Hide the RoboDK window. RoboDK will keep running as a process

        .. seealso:: :func:`~robodk.robolink.Robolink.setWindowState`"""
        with self._lock:
            self._check_connection()
            command = 'HIDE'
            self._send_line(command)
            self._check_status()

    def CloseRoboDK(self):
        """Close RoboDK window and finish RoboDK's execution."""
        with self._lock:
            self._check_connection()
            command = 'QUIT'
            self._send_line(command)
            self._check_status()

    def Version(self):
        """Return RoboDK's version as a string"""
        with self._lock:
            self._check_connection()
            command = 'Version'
            self._send_line(command)
            app_name = self._rec_line()
            bit_arch = self._rec_int()
            ver4 = self._rec_line()
            date_build = self._rec_line()
            self._check_status()
            return ver4

    def setWindowState(self, windowstate=WINDOWSTATE_NORMAL):
        """Set the state of the RoboDK window

        :param int windowstate: state of the window (WINDOWSTATE_*)

        .. code-block:: python
            :caption: Allowed window states

            WINDOWSTATE_HIDDEN      = -1        # Hidden
            WINDOWSTATE_SHOW        = 0         # Visible
            WINDOWSTATE_MINIMIZED   = 1         # Minimize window
            WINDOWSTATE_NORMAL      = 2         # Show normal window (last known state)
            WINDOWSTATE_MAXIMIZED   = 3         # Show maximized window
            WINDOWSTATE_FULLSCREEN  = 4         # Show fulscreen window
            WINDOWSTATE_CINEMA      = 5         # Show maximized window without the toolbar and without the menu
            WINDOWSTATE_FULLSCREEN_CINEMA= 6    # Show fulscreen window without the toolbar and without the menu

        .. seealso:: :func:`~robodk.robolink.Robolink.setFlagsRoboDK`
        """
        with self._lock:
            self._check_connection()
            command = 'S_WindowState'
            self._send_line(command)
            self._send_int(windowstate)
            self._check_status()

    def setFlagsRoboDK(self, flags=FLAG_ROBODK_ALL):
        """Update the RoboDK flags. RoboDK flags allow defining how much access the user has to RoboDK features. Use a FLAG_ROBODK_* variables to set one or more flags.

        :param int flags: state of the window (FLAG_ROBODK_*)

        .. code-block:: python
            :caption: Allowed RoboDK flags

            FLAG_ROBODK_TREE_ACTIVE = 1                 # Enable the tree
            FLAG_ROBODK_3DVIEW_ACTIVE = 2               # Enable the 3D view (3D mouse navigation)
            FLAG_ROBODK_LEFT_CLICK = 4                  # Enable left clicks
            FLAG_ROBODK_RIGHT_CLICK = 8                 # Enable right clicks
            FLAG_ROBODK_DOUBLE_CLICK = 16               # Enable double clicks
            FLAG_ROBODK_MENU_ACTIVE = 32                # Enable the main menu (complete menu)
            FLAG_ROBODK_MENUFILE_ACTIVE = 64            # Enable the File menu
            FLAG_ROBODK_MENUEDIT_ACTIVE = 128           # Enable the Edit menu
            FLAG_ROBODK_MENUPROGRAM_ACTIVE = 256        # Enable the Program menu
            FLAG_ROBODK_MENUTOOLS_ACTIVE = 512          # Enable the Tools menu
            FLAG_ROBODK_MENUUTILITIES_ACTIVE = 1024     # Enable the Utilities menu
            FLAG_ROBODK_MENUCONNECT_ACTIVE = 2048       # Enable the Connect menu
            FLAG_ROBODK_WINDOWKEYS_ACTIVE = 4096        # Enable the keyboard
            FLAG_ROBODK_TREE_VISIBLE = 8192             # Make the station tree visible
            FLAG_ROBODK_REFERENCES_VISIBLE = 16384      # Make the reference frames visible
            FLAG_ROBODK_STATUSBAR_VISIBLE = 32768       # Make the status bar visible
            FLAG_ROBODK_NONE = 0                        # Disable everything
            FLAG_ROBODK_ALL = 0xFFFF                    # Enable everything
            FLAG_ROBODK_MENU_ACTIVE_ALL                 # Enable the menu only

        .. seealso:: :func:`~robodk.robolink.Robolink.setFlagsItem`, :func:`~robodk.robolink.Robolink.setWindowState`
        """
        with self._lock:
            self._check_connection()
            command = 'S_RoboDK_Rights'
            self._send_line(command)
            self._send_int(flags)
            self._check_status()

    def setFlagsItem(self, item, flags=FLAG_ITEM_ALL):
        """Update item flags. Item flags allow defining how much access the user has to item-specific features. Use FLAG_ITEM_* flags to set one or more flags.

        :param item: item to set (set to 0 to apply to all items)
        :type item: :class:`.Item`
        :param flags: set the item flags (FLAG_ITEM_*)
        :type flags: int

        .. seealso:: :func:`~robodk.robolink.Robolink.getFlagsItem`, :func:`~robodk.robolink.Robolink.setFlagsRoboDK`, :func:`~robodk.robolink.Robolink.setWindowState`"""
        with self._lock:
            self._check_connection()
            command = 'S_Item_Rights'
            self._send_line(command)
            self._send_item(item)
            self._send_int(flags)
            self._check_status()

    def getFlagsItem(self, item):
        """Retrieve current item flags. Item flags allow defining how much access the user has to item-specific features. Use FLAG_ITEM_* flags to set one or more flags.

        :param item: item to get flags
        :type item: :class:`.Item`

        .. code-block:: python
            :caption: Allowed RoboDK flags

            FLAG_ITEM_SELECTABLE = 1        # Allow selecting the item
            FLAG_ITEM_EDITABLE = 2          # Allow editing the item
            FLAG_ITEM_DRAGALLOWED = 4       # Allow dragging the item
            FLAG_ITEM_DROPALLOWED = 8       # Allow dropping nested items
            FLAG_ITEM_ENABLED = 32          # Enable this item in the tree
            FLAG_ITEM_NONE = 0              # Disable everything
            FLAG_ITEM_ALL = 64+32+8+4+2+1   # Enable everything

        .. seealso:: :func:`~robodk.robolink.Robolink.setFlagsItem`, :func:`~robodk.robolink.Robolink.setFlagsRoboDK`, :func:`~robodk.robolink.Robolink.setWindowState`
        """
        with self._lock:
            self._check_connection()
            command = 'G_Item_Rights'
            self._send_line(command)
            self._send_item(item)
            flags = self._rec_int()
            self._check_status()
            return flags

    def ShowMessage(self, message, popup=True):
        """Show a message from the RoboDK window. By default, the message will be a blocking popup. Alternatively, it can be a message displayed at the bottom of RoboDK's main window.

        :param str message: message to display
        :param bool popup: Set to False to display the message in the RoboDK's status bar (not blocking)
        """
        with self._lock:
            print(message)
            self._check_connection()
            if popup:
                command = 'ShowMessage'
                self._send_line(command)
                self._send_line(message)
                self.COM.settimeout(3600)  # wait up to 1 hour user to hit OK
                self._check_status()
                self.COM.settimeout(self.TIMEOUT)
            else:
                command = 'ShowMessageStatus'
                self._send_line(command)
                self._send_line(message)
                self._check_status()

    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    def Copy(self, item, copy_childs=True):
        """Makes a copy of an item (same as Ctrl+C), which can be pasted (Ctrl+V) using Paste().

        :param item: Item to copy to the clipboard
        :type item: :class:`.Item`

        .. seealso:: :func:`~robodk.robolink.Robolink.Paste`, :func:`Item.Copy() <~robodk.robolink.Item.Copy>`

        Example:

        .. code-block:: python

            RDK = Robolink()
            object = RDK.Item('My Object')
            object.Copy()               # same as RDK.Copy(object) also works
            object_copy1 = RDK.Paste()
            object_copy1.setName('My Object (copy 1)')
            object_copy2 = RDK.Paste()
            object_copy2.setName('My Object (copy 2)')

        """
        with self._lock:
            self._check_connection()
            command = 'Copy2'
            self._send_line(command)
            self._send_item(item)
            self._send_int(1 if copy_childs else 0)
            if self._SkipStatus:
                self.COM.flush()
                return

            self._check_status()

    def Paste(self, paste_to=0, paste_times=1):
        """Paste the copied item as a dependency of another item (same as Ctrl+V). Paste should be used after Copy(). It returns the newly created item.

        :param paste_to: Item to attach the copied item (optional)
        :type paste_to: :class:`.Item`
        :param int paste_times: number of times to paste the item (returns a list if greater than 1)
        :return: New item created
        :rtype: :class:`.Item`

        .. seealso:: :func:`~robodk.robolink.Robolink.Copy`

        """
        with self._lock:
            if paste_times > 1:
                self._require_build(10500)
                self._check_connection()
                command = 'PastN'
                self._send_line(command)
                self._send_item(paste_to)
                self._send_int(paste_times)
                ntimes = self._rec_int()
                list_items = []
                for i in range(ntimes):
                    newitem = self._rec_item()
                    list_items.append(newitem)

                self._check_status()
                return list_items

            else:
                self._check_connection()
                command = 'Paste'
                self._send_line(command)
                self._send_item(paste_to)
                newitem = self._rec_item()
                self._check_status()
                return newitem

    def AddFile(self, filename, parent=0):
        """Load a file and attach it to parent (if provided). The call returns the newly added :class:`.Item`. If the new file is an object and it is attached to a robot it will be automatically converted to a tool.

        :param str filename: any file to load, supported by RoboDK. Supported formats include STL, STEP, IGES, ROBOT, TOOL, RDK,... It is also possible to load supported robot programs, such as SRC (KUKA), SCRIPT (Universal Robots), LS (Fanuc), JBI (Motoman), MOD (ABB), PRG (ABB), ...
        :param parent: item to attach the newly added object (optional)
        :type parent: :class:`.Item`

        Example:

        .. code-block:: python

            RDK = Robolink()
            item = RDK.AddFile(r'C:\\Users\\Name\\Desktop\\object.step')
            item.setPose(transl(100,50,500))

            # Add a tool to an existing robot:
            tool = RDK.AddFile(r'C:\\Users\\Name\\Desktop\\robot-tool.stl', robot)
            tool.setPoseTool(transl(100,50,500))

            # Add a reference frame, move it and add an object to that reference frame (locally):
            frame = AddFrame('Reference A')
            frame.setPose(transl(100,200,300))
            new_object = RDK.Addfile('path-to-object.stl', frame)

        .. seealso:: :func:`~robodk.robolink.Robolink.Save`, :func:`~robodk.robolink.Robolink.AddFrame`, :func:`~robodk.robolink.Item.AddTool`, :func:`~robodk.robolink.Robolink.Copy`, :func:`~robodk.robolink.Robolink.Paste`

        """
        with self._lock:
            self._check_connection()
            command = 'Add'
            self._send_line(command)
            self._send_line(filename)
            self._send_item(parent)
            self.COM.settimeout(60)  # 60 seconds timeout to add a file
            newitem = self._rec_item()
            self.COM.settimeout(self.TIMEOUT)
            self._check_status()
            return newitem

    def AddShape(self, triangle_points, add_to=0, override_shapes=False):
        """Adds a shape provided triangle coordinates. Triangles must be provided as a list of vertices. A vertex normal can be provided optionally.

        :param triangle_points: List of vertices grouped by triangles.
        :type triangle_points: :class:`~robodk.robomath.Mat` (3xN or 6xN matrix, N must be multiple of 3 because vertices must be stacked by groups of 3)
        :param parent: item to attach the newly added geometry (optional)
        :type parent: :class:`.Item`
        :param override_shapes: Set to True to fill the object with a new shape
        :type override_shapes: bool
        :return: added object/shape (0 if failed)
        :rtype: :class:`.Item`

        .. seealso:: :func:`~robodk.robolink.Robolink.AddCurve`, :func:`~robodk.robolink.Robolink.AddPoints`
        """
        with self._lock:
            if isinstance(triangle_points, list):
                triangle_points = robomath.tr(robomath.Mat(triangle_points))
            elif not isinstance(triangle_points, robomath.Mat):
                raise Exception("triangle_points must be a 3xN or 6xN list or matrix")
            self._check_connection()
            command = 'AddShape2'
            self._send_line(command)
            self._send_matrix(triangle_points)
            self._send_item(add_to)
            self._send_int(1 if override_shapes else 0)
            newitem = self._rec_item()
            self._check_status()
            return newitem

    def AddCurve(self, curve_points, reference_object=0, add_to_ref=False, projection_type=PROJECTION_ALONG_NORMAL_RECALC):
        """Adds a curve provided point coordinates. The provided points must be a list of vertices. A vertex normal can be provided optionally.

        :param curve_points: List of points defining the curve
        :type curve_points: :class:`~robodk.robomath.Mat` (3xN matrix, or 6xN to provide curve normals as ijk vectors)
        :param reference_object: item to attach the newly added geometry (optional)
        :type reference_object: :class:`.Item`
        :param bool add_to_ref: If True, the curve will be added as part of the object in the RoboDK item tree (a reference object must be provided)
        :param int projection_type: type of projection. Use the PROJECTION_* flags.
        :return: added object/shape (0 if failed)
        :rtype: :class:`.Item`

        .. code-block:: python
            :caption: Available projection types

            PROJECTION_NONE                = 0 # No projection
            PROJECTION_CLOSEST             = 1 # The projection will be the closest point on the surface
            PROJECTION_ALONG_NORMAL        = 2 # The projection will be done along the normal.
            PROJECTION_ALONG_NORMAL_RECALC = 3 # The projection will be done along the normal. Furthermore, the normal will be recalculated according to the surface normal.
            PROJECTION_CLOSEST_RECALC      = 4 # The projection will be the closest point on the surface and the normals will be recalculated
            PROJECTION_RECALC              = 5 # The normals are recalculated according to the surface normal of the closest projection. The points are not changed.

        .. seealso:: :func:`~robodk.robolink.Robolink.AddShape`, :func:`~robodk.robolink.Robolink.AddPoints`
        """
        with self._lock:
            if isinstance(curve_points, list):
                curve_points = robomath.Mat(curve_points).tr()
            elif not isinstance(curve_points, robomath.Mat):
                raise Exception("curve_points must be a 3xN or 6xN list or matrix")
            self._check_connection()
            command = 'AddWire'
            self._send_line(command)
            self._send_matrix(curve_points)
            self._send_item(reference_object)
            self._send_int(1 if add_to_ref else 0)
            self._send_int(projection_type)
            newitem = self._rec_item()
            self._check_status()
            return newitem

    def AddPoints(self, points, reference_object=0, add_to_ref=False, projection_type=PROJECTION_ALONG_NORMAL_RECALC):
        """Adds a list of points to an object. The provided points must be a list of vertices. A vertex normal can be provided optionally.

        :param points: list of points or matrix
        :type points: :class:`~robodk.robomath.Mat` (3xN matrix, or 6xN to provide point normals as ijk vectors)
        :param reference_object: item to attach the newly added geometry (optional)
        :type reference_object: :class:`.Item`
        :param bool add_to_ref: If True, the points will be added as part of the object in the RoboDK item tree (a reference object must be provided)
        :param int projection_type: type of projection. Use the PROJECTION_* flags.
        :return: added object/shape (0 if failed)
        :rtype: :class:`.Item`

        .. seealso:: :func:`~robodk.robolink.Robolink.ProjectPoints`, :func:`~robodk.robolink.Robolink.AddShape`, :func:`~robodk.robolink.Robolink.AddCurve`

        The difference between ProjectPoints and AddPoints is that ProjectPoints does not add the points to the RoboDK station.
        """
        with self._lock:
            if isinstance(points, list):
                points = robomath.Mat(points).tr()

            elif not isinstance(points, robomath.Mat):
                raise Exception("points must be a 3xN or 6xN list or matrix")
            self._check_connection()
            command = 'AddPoints'
            self._send_line(command)
            self._send_matrix(points)
            self._send_item(reference_object)
            self._send_int(1 if add_to_ref else 0)
            self._send_int(projection_type)
            newitem = self._rec_item()
            self._check_status()
            return newitem

    def ProjectPoints(self, points, object_project, projection_type=PROJECTION_ALONG_NORMAL_RECALC, timeout=30):
        """Project a point or a list of points given its coordinates.
        The provided points must be a list of [XYZ] coordinates. Optionally, a vertex normal can be provided [XYZijk].
        It returns the projected points as a list of points (empty matrix if failed).

        :param points: list of points to project
        :type points: list of points (XYZ or XYZijk list of floats), or :class:`~robodk.robomath.Mat` (3xN matrix, or 6xN to provide point normals as ijk vectors)
        :param object_project: object to project the points
        :type object_project: :class:`.Item`
        :param projection_type: Type of projection. For example: PROJECTION_ALONG_NORMAL_RECALC will project along the point normal and recalculate the normal vector on the surface projected.
        :type projection_type: int
        :param timeout: Max timeout to wait for a reply in seconds (30 seconds by default).
        :type timeout: int

        The difference between ProjectPoints and AddPoints is that ProjectPoints does not add the points to the RoboDK station.
        """
        with self._lock:
            islist = False
            if isinstance(points, list):
                islist = True
                points = robomath.Mat(points).tr()
                # Safety check for backwards compatibility
                if points.size(0) != 6 and points.size(1) == 6:
                    points = points.tr()

            elif not isinstance(points, robomath.Mat):
                raise Exception("points must be a 3xN or 6xN list or matrix")
            self._check_connection()
            command = 'ProjectPoints'
            self._send_line(command)
            self._send_matrix(points)
            self._send_item(object_project)
            self._send_int(projection_type)
            self.COM.settimeout(timeout)  # 30 seconds timeout
            projected_points = self._rec_matrix()  # will wait here
            self.COM.settimeout(self.TIMEOUT)
            self._check_status()
            if islist:
                projected_points = list(projected_points)
            return projected_points

    def CloseStation(self):
        """Closes the current RoboDK station without suggesting to save"""
        with self._lock:
            self._require_build(12938)
            self._check_connection()
            self._send_line('RemoveStn')
            if self._SkipStatus:
                self.COM.flush()
                return

            self._check_status()

    def Delete(self, item_list):
        """Remove a list of items.

        .. seealso:: :func:`~robodk.robolink.Item.Delete`, :func:`~robodk.robolink.Robolink.CloseStation`
        """
        with self._lock:
            self._require_build(14560)
            if type(item_list) is not list:
                item_list = [item_list]

            self._check_connection()
            command = 'RemoveLst'
            self._send_line(command)
            self._send_int(len(item_list))
            for itm in item_list:
                self._send_item(itm)
                itm.item = 0

            self._check_status()

    def Save(self, filename, itemsave=0):
        """Save an item or a station to a file (formats supported include RDK, STL, ROBOT, TOOL, ...). If no item is provided, the open station is saved.

        :param str filename: File path to save
        :param itemsave: Item to save (leave at 0 to save the current RoboDK station as an RDK file
        :type itemsave: :class:`.Item`

        .. seealso:: :func:`~robodk.robolink.Robolink.AddFile`
        """
        with self._lock:
            self._check_connection()
            command = 'Save'
            self._send_line(command)
            self._send_line(filename)
            self._send_item(itemsave)
            self.COM.settimeout(60)
            self._check_status()
            self.COM.settimeout(self.TIMEOUT)

    def AddStation(self, name='New Station'):
        """Add a new empty station. It returns the station :class:`.Item` created.

        :param str name: name of the station

        .. seealso:: :func:`~robodk.robolink.Robolink.AddFile`
        """
        with self._lock:
            self._check_connection()
            command = 'NewStation'
            self._send_line(command)
            self._send_line(name)
            newitem = self._rec_item()
            self._check_status()
            return newitem

    def AddTarget(self, name, itemparent=0, itemrobot=0):
        """Add a new target that can be reached with a robot.

        :param str name: Target name
        :param itemparent: Reference frame to attach the target
        :type itemparent: :class:`.Item`
        :param itemrobot: Robot that will be used to go to self target (optional)
        :type itemrobot: :class:`.Item`
        :return: New target item created
        :rtype: :class:`.Item`

        .. seealso:: :func:`~robodk.robolink.Robolink.AddFrame`
        """
        with self._lock:
            self._check_connection()
            command = 'Add_TARGET'
            self._send_line(command)
            self._send_line(name)
            self._send_item(itemparent)
            self._send_item(itemrobot)
            newitem = self._rec_item()
            self._check_status()
            return newitem

    def AddFrame(self, name, itemparent=0):
        """Adds a new reference Frame. It returns the new :class:`.Item` created.

        :param str name: name of the new reference frame
        :param itemparent: Item to attach the new reference frame (such as another reference frame)
        :type itemparent: :class:`.Item`

        .. seealso:: :func:`~robodk.robolink.Robolink.AddTarget`"""
        with self._lock:
            self._check_connection()
            command = 'Add_FRAME'
            self._send_line(command)
            self._send_line(name)
            self._send_item(itemparent)
            newitem = self._rec_item()
            self._check_status()
            return newitem

    def AddProgram(self, name, itemrobot=0):
        """Add a new program to the RoboDK station. Programs can be used to simulate a specific sequence, to generate vendor specific programs (Offline Programming) or to run programs on the robot (Online Programming).
        It returns the new :class:`.Item` created.
        Tip: Use the MoveRobotThroughLine.py macro to create programs in the RoboDK station (Option 2).

        :param name: Name of the program
        :type name: str
        :param itemrobot: Robot that will be used for this program. It is not required to specify the robot if the station has only one robot or mechanism.
        :type itemrobot: :class:`.Item`
        :return: New program item
        :rtype: :class:`.Item`

        .. seealso:: :func:`~robodk.robolink.Robolink.AddTarget`, :func:`~robodk.robolink.Item.MoveJ`, :func:`~robodk.robolink.Item.MoveL`, :func:`~robodk.robolink.Item.setDO`, :func:`~robodk.robolink.Item.waitDI`, :func:`~robodk.robolink.Item.Pause`, :func:`~robodk.robolink.Item.RunCodeCustom`, :func:`~robodk.robolink.Item.RunInstruction`, :func:`~robodk.robolink.Item.ShowInstructions`, :func:`~robodk.robolink.Item.ShowTargets`, :func:`~robodk.robolink.Item.Update`


        Example 1 - Generic program with movements:

        .. code-block:: python

            # Turn off rendering (faster)
            RDK.Render(False)
            prog = RDK.AddProgram('AutoProgram')

            # Hide program instructions (optional, but faster)
            prog.ShowInstructions(False)

            # Retrieve the current robot position:
            pose_ref = robot.Pose()

            # Iterate through a number of points
            for i in range(len(POINTS)):
                # add a new target
                ti = RDK.AddTarget('Auto Target %i' % (i+1))

                # use the reference pose and update the XYZ position
                pose_ref.setPos(POINTS[i])
                ti.setPose(pose_ref)

                # force to use the target as a Cartesian target (default)
                ti.setAsCartesianTarget()

                # Add the target as a Linear/Joint move in the new program
                prog.MoveL(ti)

            # Hide the target items from the tree: it each movement still keeps its own target.
            # Right click the movement instruction and select "Select Target" to see the target in the tree
            program.ShowTargets(False)

            # Turn rendering ON before starting the simulation (automatic if we are done)
            RDK.Render(True)

            #--------------------------------------
            # Update the program path to display the yellow path in RoboDK.
            # Set collision checking ON or OFF
            check_collisions = COLLISION_OFF
            # Update the path (can take some time if collision checking is active)
            update_result = program.Update(check_collisions)
            # Retrieve the result
            n_insok = update_result[0]
            time = update_result[1]
            distance = update_result[2]
            percent_ok = update_result[3]*100
            str_problems = update_result[4]
            if percent_ok < 100.0:
                msg_str = "WARNING! Problems with <strong>%s</strong> (%.1f):<br>%s" % (program_name, percent_ok, str_problems)
            else:
                msg_str = "No problems found for program %s" % program_name

            # Notify the user:
            print(msg_str)
            RDK.ShowMessage(msg_str)

        Example 2 - Program flow, manage inputs/outputs and program calls:

        .. code-block:: python

            # Add a pause (in miliseconds)
            program.Pause(1000) # pause motion 1 second

            # Stop the program so that it can be resumed
            # It provokes a STOP (pause until the operator desires to resume)
            program.Pause()

            # Add a program call or specific code in the program:
            program.RunInstruction('ChangeTool(2)',INSTRUCTION_CALL_PROGRAM)
            program.RunInstruction('ChangeTool(2);',INSTRUCTION_INSERT_CODE)

            # Set a digital output
            program.setDO('DO_NAME', 1)
            # Wait for a digital input:
            program.waitDI('DI_NAME', 1)

        Example 3 - Add movements with external axes:

        .. code-block:: python

            # Add a new movement involving external axes:

            # First: create a new target
            target = RDK.AddTarget("T1", reference)

            # Set the target as Cartesian (default)
            target.setAsCartesianTarget()

            # Specify the position of the external axes:
            external_axes = [10, 20]
            # The robot joints are calculated to reach the target
            # given the position of the external axes
            target.setJoints([0,0,0,0,0,0] + external_axes)

            # Specify the pose (position with respect to the reference frame):
            target.setPose(KUKA_2_Pose([x,y,z,w,p,r]))

            # Add a new movement instruction linked to that target:
            program.MoveJ(target)

        Example 4 - Add a program call after each movement instruction inside a program:

        .. code-block:: python

            from robodk.robolink import *       # API to communicate with RoboDK
            from robodk.robodialogs import *    # User prompts
            RDK = Robolink()

            # Ask the user to select a program:
            prog = RDK.ItemUserPick("Select a Program to modify", ITEM_TYPE_PROGRAM)
            if not prog.Valid():
                print("Operation cancelled or no programs available")
                quit()

            # Ask the user to enter a function call that will be added after each movement:
            print("Program selected: " + prog.Name())
            ins_call = mbox("Enter a program call to add after each movement", entry="SynchRobot")
            if not ins_call:
                print("Operation cancelled")
                quit()

            # Iterate through all the instructions in a program:
            ins_id = 0
            ins_count = prog.InstructionCount()
            while ins_id < ins_count:
                # Retrieve instruction
                ins_nom, ins_type, move_type, isjointtarget, pose, joints = prog.Instruction(ins_id)
                if ins_type == INS_TYPE_MOVE:
                    # Select the movement instruction as a reference
                    prog.InstructionSelect(ins_id)
                    # Add a new program call
                    prog.RunInstruction(ins_call, INSTRUCTION_CALL_PROGRAM)
                    # Advance one additional instruction as we just added another instruction
                    ins_id = ins_id + 1
                    ins_count = ins_count + 1

                ins_id = ins_id + 1

        More examples to generate programs directly from your script or move the robot directly from your program here:
        :ref:`lbl-move-through-points`. or the macro available in RoboDK/Library/Macros/MoveRobotThroughLine.py
        """
        with self._lock:
            self._check_connection()
            command = 'Add_PROG'
            self._send_line(command)
            self._send_line(name)
            self._send_item(itemrobot)
            newitem = self._rec_item()
            self._check_status()
            return newitem

    def AddMillingProject(self, name='Milling settings', itemrobot=0):
        """
        .. deprecated:: 4.0
            Obsolete. Use :func:`~robodk.robolink.Robolink.AddMachiningProject` instead.
        """
        return self.AddMachiningProject(name, itemrobot)

    def AddMachiningProject(self, name='Milling settings', itemrobot=0):
        """Add a new robot machining project. Machining projects can also be used for 3D printing, following curves and following points.
        It returns the newly created :class:`.Item` containing the project settings.
        Tip: Use the MoveRobotThroughLine.py macro to see an example that creates a new "curve follow project" given a list of points to follow (Option 4).

        :param str name: Name of the project settings
        :param itemrobot: Robot to use for the project settings (optional). It is not required to specify the robot if only one robot or mechanism is available in the RoboDK station.
        :type itemrobot: :class:`.Item`

        .. seealso:: :func:`~robodk.robolink.Item.setMachiningParameters`"""
        with self._lock:
            self._check_connection()
            command = 'Add_MACHINING'
            self._send_line(command)
            self._send_line(name)
            self._send_item(itemrobot)
            newitem = self._rec_item()
            self._check_status()
            return newitem

    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    def RunProgram(self, fcn_param, wait_for_finished=False):
        """Run a program (start a program). If the program exists in the RoboDK station it has the same behavior as right clicking a and selecting Run (or Run Python script for Python programs).
        When generating a program offline (Offline Programming), the program call will be generated in the program output (RoboDK will handle the syntax when the code is generated for a specific robot using the post processor).

        :param fcn_param: program name and parameters. Parameters can be provided for Python programs available in the RoboDK station as well.
        :type fcn_param: str
        :param bool wait_for_finished: Set to True to block execution during a simulation until the program finishes (skipped if the program does not exist or when the program is generated)

        .. seealso:: :func:`~robodk.robolink.Robolink.Item`, :func:`~robodk.robolink.Robolink.AddProgram`, :func:`~robodk.robolink.Item.Busy`
        """
        if wait_for_finished:
            prog_item = self.Item(fcn_param, ITEM_TYPE_PROGRAM)
            if not prog_item.Valid():
                raise Exception('Invalid program %s' % fcn_param)
            prog_status = prog_item.RunProgram()
            prog_item.WaitFinished()
        else:
            prog_status = self.RunCode(fcn_param, True)
        return prog_status

    def RunCode(self, code, code_is_fcn_call=False):
        """Generate a program call or a customized instruction output in a program.
        If code_is_fcn_call is set to True it has the same behavior as RDK.RunProgram(). In this case, when generating a program offline (offline programming), a function/procedure call will be generated in the program output (RoboDK will handle the syntax when the code is generated for a specific robot using the post processor).
        If the program exists it will also run the program in simulate mode.

        :param code: program name or code to generate
        :type code: str
        :param code_is_fcn_call: Set to True if the provided code corresponds to a function call (same as RunProgram()), if so, RoboDK will handle the syntax when the code is generated for a specific robot.
        :type code_is_fcn_call: bool

        Example to run an existing program in the RoboDK station:

        .. code-block:: python

            from robodk.robolink import *           # import the robolink library
            RDK = Robolink()                        # connect to the RoboDK API (RoboDK starts if it has not started
            RDK.RunCode("Prog1", True)              # Run a program named Prog1 available in the RoboDK station

        """
        with self._lock:
            self._check_connection()
            command = 'RunCode'
            self._send_line(command)
            self._send_int(code_is_fcn_call)
            self._send_line(code.replace('\r\n', '<<br>>').replace('\n', '<<br>>'))
            prog_status = self._rec_int()
            self._check_status()
            return prog_status

    def RunMessage(self, message, message_is_comment=False):
        """Show a message or a comment in the program generated offline (program generation). The message (or code) is displayed on the teach pendant of the robot.

        :param str message: message or comment to display.
        :param bool message_is_comment: Set to True to generate a comment in the generated code instead of displaying a message on the teach pendant of the robot.

        """
        print('Message: ' + message)
        with self._lock:
            self._check_connection()
            command = 'RunMessage'
            self._send_line(command)
            self._send_int(message_is_comment)
            self._send_line(message.replace('\r\n', '<<br>>').replace('\n', '<<br>>'))
            self._check_status()

    def Render(self, always_render=False):
        """Display/render the scene: update the display. This function turns default rendering (rendering after any modification of the station unless always_render is set to true).
        Use Update to update the internal links of the complete station without rendering (when a robot or item has been moved).

        :param bool always_render: Set to True to update the screen every time the station is modified (default behavior when Render() is not used).

        .. seealso:: :func:`~robodk.robolink.Robolink.Update`
        """
        auto_render = None
        if always_render is True:
            auto_render = 0
        elif always_render is False:
            auto_render = 1
        elif always_render == 2:
            auto_render = 2

        if auto_render is None:
            return

        with self._lock:
            self._check_connection()
            command = 'Render'
            self._send_line(command)
            self._send_int(auto_render)
            self._check_status()

    def Update(self):
        """Update the screen. This updates the position of all robots and internal links according to previously set values.
        This function is useful when Render is turned off (Example: "RDK.Render(False)"). Otherwise, by default RoboDK will update all links after any modification of the station (when robots or items are moved).

        .. seealso:: :func:`~robodk.robolink.Robolink.Render`"""
        with self._lock:
            self._check_connection()
            command = 'Refresh'
            self._send_line(command)
            self._send_int(0)
            self._check_status()

    def IsInside(self, object_inside, object):
        """Return 1 (True) if object_inside is inside the object, otherwise, it returns 0 (False). Both objects must be of type :class:`.Item`"""
        with self._lock:
            self._check_connection()
            self._send_line('IsInside')
            self._send_item(object_inside)
            self._send_item(object)
            inside = self._rec_int()
            self._check_status()
            return inside

    def setCollisionActive(self, check_state=COLLISION_ON):
        """Set global collision checking ON or OFF (COLLISION_ON/COLLISION_OFF).

        .. seealso:: :func:`~robodk.robolink.Robolink.setCollisionActivePair`, :func:`~robodk.robolink.Item.Visible`
        """
        with self._lock:
            self._check_connection()
            command = 'Collision_SetState'
            self._send_line(command)
            self._send_int(check_state)
            ncollisions = self._rec_int()
            self._check_status()
            return ncollisions

    def setCollisionActivePair(self, check_state, item1, item2, id1=0, id2=0):
        """Set collision checking ON or OFF (COLLISION_ON/COLLISION_OFF) for a specific pair of objects (:class:`.Item`).
        This allows altering the collision map for Collision checking.
        Specify the link id for robots or moving mechanisms (id 0 is the base)
        Returns 1 if succeeded. Returns 0 if setting the pair failed (wrong id is provided)

        .. seealso:: :func:`~robodk.robolink.Robolink.setCollisionActive`, :func:`~robodk.robolink.Robolink.Collisions`, :func:`~robodk.robolink.Item.Visible`
        """
        with self._lock:
            self._check_connection()
            command = 'Collision_SetPair'
            self._send_line(command)
            self._send_item(item1)
            self._send_item(item2)
            self._send_int(id1)
            self._send_int(id2)
            self._send_int(check_state)
            success = self._rec_int()
            self._check_status()
            return success

    def setCollisionActivePairList(self, list_check_state, list_item1, list_item2, list_id1=None, list_id2=None):
        """Set collision checking ON or OFF (COLLISION_ON/COLLISION_OFF) for a specific list of pairs of objects. This allows altering the collision map for Collision checking.
        Specify the link id for robots or moving mechanisms (id 0 is the base).

        .. seealso:: :func:`~robodk.robolink.Robolink.setCollisionActive`, :func:`~robodk.robolink.Robolink.Collisions`, :func:`~robodk.robolink.Robolink.setCollisionActivePair`
        """
        with self._lock:
            npairs = min(len(list_check_state), min(len(list_item1), len(list_item2)))
            self._check_connection()
            self._send_line("Collision_SetPairList")
            self._send_int(npairs)
            for i in range(npairs):
                self._send_item(list_item1[i])
                self._send_item(list_item2[i])
                id1 = 0
                id2 = 0
                if list_id1 is not None and len(list_id1) > i:
                    id1 = list_id1[i]

                if list_id2 is not None and len(list_id2) > i:
                    id2 = list_id2[i]

                self._send_int(id1)
                self._send_int(id2)
                self._send_int(list_check_state[i])

            success = self._rec_int()
            self._check_status()
            return success

    def Collisions(self):
        """Return the number of pairs of objects that are currently in a collision state.

        .. seealso:: :func:`~robodk.robolink.Robolink.setCollisionActive`, :func:`~robodk.robolink.Robolink.Collisions`, :func:`~robodk.robolink.Robolink.CollisionItems`, :func:`~robodk.robolink.Item.Visible`
        """
        with self._lock:
            self._check_connection()
            command = 'Collisions'
            self._send_line(command)
            ncollisions = self._rec_int()
            self._check_status()
            return ncollisions

    def Collision(self, item1, item2):
        """Returns 1 if item1 and item2 collided. Otherwise returns 0.

        .. seealso:: :func:`~robodk.robolink.Robolink.Collisions`, :func:`~robodk.robolink.Robolink.CollisionItems`, :func:`~robodk.robolink.Item.Visible`
        """
        with self._lock:
            self._check_connection()
            command = 'Collided'
            self._send_line(command)
            self._send_item(item1)
            self._send_item(item2)
            ncollisions = self._rec_int()
            self._check_status()
            return ncollisions

    def CollisionItems(self):
        """Return the list of items that are in a collision state. This function can be used after calling Collisions() to retrieve the items that are in a collision state.

        .. seealso:: :func:`~robodk.robolink.Robolink.Collisions`, :func:`~robodk.robolink.Item.Visible`
        """
        with self._lock:
            self._check_connection()
            command = 'Collision_Items'
            self._send_line(command)
            nitems = self._rec_int()
            item_list = []
            for i in range(nitems):
                item_list.append(self._rec_item())
                link_id = self._rec_int()  # link id for robot items (ignored)
                collision_times = self._rec_int()  # number of objects it is in collisions with

            self._check_status()
            return item_list

    def CollisionPairs(self):
        """Return the list of pairs of items that are in a collision state.

        .. seealso:: :func:`~robodk.robolink.Robolink.Collisions`, :func:`~robodk.robolink.Item.Visible`
        """
        with self._lock:
            self._check_connection()
            command = 'Collision_Pairs'
            self._send_line(command)
            nitems = self._rec_int()
            item_list = []
            for i in range(nitems):
                item_1 = self._rec_item()
                id_1 = self._rec_int()
                item_2 = self._rec_item()
                id_2 = self._rec_int()
                item_list.append([item_1, item_2, id_1, id_2])

            self._check_status()
            return item_list

    def setSimulationSpeed(self, speed):
        """Set the simulation speed.
        A simulation speed of 5 (default) means that 1 second of simulation time equals to 5 seconds in a real application.
        The slowest speed ratio allowed is 0.001. Set a large simmulation ratio (>100) for fast simulation results.

        :param speed: simulation ratio
        :type speed: float

        .. seealso:: :func:`~robodk.robolink.Robolink.SimulationSpeed`, :func:`~robodk.robolink.Robolink.SimulationTime`
        """
        with self._lock:
            self._check_connection()
            command = 'SimulateSpeed'
            self._send_line(command)
            self._send_int(speed * 1000)
            self._check_status()

    def SimulationSpeed(self):
        """Return the simulation speed. A simulation speed of 1 means real-time simulation.
        A simulation speed of 5 (default) means that 1 second of simulation time equals to 5 seconds in a real application.

        .. seealso:: :func:`~robodk.robolink.Robolink.setSimulationSpeed`
        """
        with self._lock:
            self._check_connection()
            command = 'GetSimulateSpeed'
            self._send_line(command)
            speed = self._rec_int() / 1000.0
            self._check_status()
            return speed

    def SimulationTime(self):
        """Retrieve the simulation time (in seconds). Time of 0 seconds starts with the first time this function is called.
        The simulation time changes depending on the simulation speed. The simulation time is usually faster than the real time (5 times by default).

        .. seealso:: :func:`~robodk.robolink.Robolink.setSimulationSpeed`, :func:`~robodk.robolink.Robolink.SimulationSpeed`
        """
        with self._lock:
            self._check_connection()
            command = 'GetSimTime'
            self._send_line(command)
            speed = self._rec_int() / 1000.0
            self._check_status()
            return speed

    def setRunMode(self, run_mode=1):
        """Set the run mode (behavior) of the script, for either simulation, offline programming or online programming.
        By default, robodk shows the path simulation for movement instructions (run_mode=RUNMODE_SIMULATE).

        .. code-block:: python
            :caption: Available run modes

            RUNMODE_SIMULATE=1                      # performs the simulation moving the robot (default)
            RUNMODE_QUICKVALIDATE=2                 # performs a quick check to validate the robot movements
            RUNMODE_MAKE_ROBOTPROG=3                # makes the robot program
            RUNMODE_MAKE_ROBOTPROG_AND_UPLOAD=4     # makes the robot program and updates it to the robot
            RUNMODE_MAKE_ROBOTPROG_AND_START=5      # makes the robot program and starts it on the robot (independently from the PC)
            RUNMODE_RUN_ROBOT=6                     # moves the real robot from the PC (PC is the client, the robot behaves like a server)

        The following calls will alter the current run mode:

        1- :func:`~robodk.robolink.Item.Connect` automatically sets RUNMODE_RUN_ROBOT. So it will use the robot driver together with the simulation.

        2- :func:`~robodk.robolink.Robolink.ProgramStart` automatically sets the mode to RUNMODE_MAKE_ROBOTPROG. So it will generate the program

        .. seealso:: :func:`~robodk.robolink.Robolink.RunMode`
        """
        with self._lock:
            self._check_connection()
            command = 'S_RunMode'
            self._send_line(command)
            self._send_int(run_mode)
            self._check_status()

    def RunMode(self):
        """Return the current run mode (behavior) of the script.
        By default, robodk simulates any movements requested from the API (such as prog.MoveL) simulation for movement instructions (run_mode=RUNMODE_SIMULATE).

        .. seealso:: :func:`~robodk.robolink.Robolink.setRunMode`
        """
        with self._lock:
            self._check_connection()
            command = 'G_RunMode'
            self._send_line(command)
            runmode = self._rec_int()
            self._check_status()
            return runmode

    def getParams(self):
        """Get all the user parameters from the open RoboDK station.
        Station parameters can also be modified manually by right clicking the station item and selecting "Station parameters"
        :return: list of pairs of strings
        :rtype: list of str

        .. seealso:: :func:`Robolink.getParam() <robodk.robolink.Robolink.getParam>`, :func:`Robolink.setParam() <robodk.robolink.Robolink.setParam>`
        """
        with self._lock:
            self._check_connection()
            command = 'G_Params'
            self._send_line(command)
            nparam = self._rec_int()
            params = []
            for i in range(nparam):
                param = self._rec_line()
                value = self._rec_line()
                if value.replace('.', '', 1).isnumeric():
                    value = float(value)  # automatically convert int, long and float

                params.append([param, value])
            self._check_status()
            return params

    def getParam(self, param='PATH_OPENSTATION', str_type=True):
        """Get a global or a station parameter from the open RoboDK station.
        Station parameters can also be modified manually by right clicking the station item and selecting "Station parameters"

        :param str param: name of the parameter
        :param bool str_type: True to retrieve a string parameter (False for binary/bytes type)
        :return: value of the parameter.
        :rtype: str, float or None if the parameter is unknown

        .. code-block:: python
            :caption: Available global parameters

            PATH_OPENSTATION       # Full path of the current station (.rdk file)
            FILE_OPENSTATION       # File name of the current station (name of the .rdk file)
            PATH_DESKTOP           # Full path to the desktop folder

        .. seealso:: :func:`Robolink.setParam() <robodk.robolink.Robolink.setParam>`, :func:`Robolink.getParams() <robodk.robolink.Robolink.getParams>`
        """
        with self._lock:
            self._check_connection()
            if str_type:
                command = 'G_Param'
                self._send_line(command)
                self._send_line(param)
                value = self._rec_line()
                self._check_status()
                if value.startswith('UNKNOWN '):
                    return None

                if value.replace('.', '', 1).isnumeric():
                    value = float(value)  # automatically convert int, long and float

                return value

            else:
                command = 'G_DataParam'
                self._send_line(command)
                self._send_line(param)
                value = self._rec_bytes()
                self._check_status()
                return value

    def setParam(self, param, value):
        """Set a station parameter. If the parameters exists, it will be updated. Otherwise, it will be added to the station.

        :param str param: name of the parameter
        :param str value: value of the parameter (value type can be str or bytes)

        .. seealso:: :func:`~robodk.robolink.Robolink.getParam`
        """
        with self._lock:
            if isinstance(value, Item):
                value = str(value.item)
            self._check_connection()
            if isinstance(value, bytes):
                command = 'S_DataParam'
                self._send_line(command)
                self._send_line(str(param))
                self._send_bytes(value)
            else:
                command = 'S_Param'
                self._send_line(command)
                self._send_line(str(param))
                self._send_line(str(value).replace('\n', ' '))

            self._check_status()

    def Command(self, cmd, value='', skip_result=False):
        """Send a special command. These commands are meant to have a specific effect in RoboDK, such as changing a specific setting or provoke specific events.

        :param str command: Command Name, such as Trace, Threads or Window.
        :param str value: Comand value (optional, not all commands require a value)

        Select **Tools-Run Script-Show Commands** to see all available commands.

        .. image:: Commands.png

        .. code-block:: python
            :caption: Example commands

            from robodk.robolink import *
            RDK = Robolink()      # Start the RoboDK API

            # How to change the number of threads using by the RoboDK application:
            RDK.Command("Threads", "4")

            # How to change the default behavior of 3D view using the mouse:
            RDK.Command("MouseClick_Left", "Select")   # Set the left mouse click to select
            RDK.Command("MouseClick_Mid", "Pan")       # Set the mid mouse click to Pan the 3D view
            RDK.Command("MouseClick_Right", "Rotate")  # Set the right mouse click to Rotate the 3D view

            RDK.Command("MouseClick", "Default")       # Set the default mouse 3D navigation settings

            # Provoke a resize event
            RDK.Command("Window", "Resize")

            # Reset the trace
            RDK.Command("Trace", "Reset")


        You can also pass commands through command line when starting RoboDK or when RoboDK is already running (add '-' to the command name).
        More information about command line options available in the documentation: https://robodk.com/doc/en/RoboDK-API.html#CommandLine

        .. code-block:: python
            :caption: Example to start RoboDK in Chinese and white background using 6 threads and load a RoboDK project file

            RoboDK -Lang=zh -ColorBgBottom=white -ColorBgTop=white -Threads=6 "path-to-file.rdk"


        .. seealso:: :func:`Item.setParam() <robodk.robolink.Item.setParam>`, :func:`Robolink.setParam() <robodk.robolink.Robolink.setParam>`
        """
        with self._lock:
            if type(value) == dict:
                # return dict if we provided a dict
                import json
                value = json.dumps(value)

            elif type(value) == robomath.Mat:
                # Special 2D matrix write/read
                self._check_connection()
                command = 'G_Gen_Mat'
                self._send_line(command)
                self._send_item(None)
                self._send_line(str(cmd))
                self._send_matrix(value)
                self.COM.settimeout(3600)
                nmats = self._rec_int()
                self.COM.settimeout(self.TIMEOUT)
                mat2d_list = []
                for i in range(nmats):
                    mat2d_list.append(self._rec_matrix())

                self._check_status()
                return mat2d_list

            elif isinstance(value, Item):
                value = str(value.item)

            else:
                value = str(value)

            value = value.replace('\n', '<br>')

            self._check_connection()
            # Skipstatus flag has no effect here
            # skip_result = self._SkipStatus
            if skip_result:
                command = 'BlindSCMD'
                self._send_line(command)
                self._send_line(str(cmd))
                self._send_line(value)
                self.COM.flush()
                return None

            else:
                command = 'SCMD'
                self._send_line(command)
                self._send_line(str(cmd))
                self._send_line(value)
                self.COM.settimeout(3600)
                line = self._rec_line()
                self.COM.settimeout(self.TIMEOUT)
                self._check_status()
                return line

    def getOpenStations(self):
        """Returns the list of open stations in RoboDK

        .. seealso:: :func:`~robodk.robolink.Robolink.setActiveStation`, :func:`~robodk.robolink.Robolink.getParam`, :func:`~robodk.robolink.Item.Childs`, :func:`~robodk.robolink.Item.Save`, :func:`~robodk.robolink.Robolink.AddStation`
        """
        with self._lock:
            self._check_connection()
            command = 'G_AllStn'
            self._send_line(command)
            nstn = self._rec_int()
            list_stn = []
            for i in range(nstn):
                list_stn.append(self._rec_item())
            self._check_status()
            return list_stn

    def ActiveStation(self):
        """Returns the active station item (station currently visible)

        .. seealso:: :func:`~robodk.robolink.Robolink.setActiveStation`, :func:`~robodk.robolink.Robolink.getParam`, :func:`~robodk.robolink.Item.Childs`, :func:`~robodk.robolink.Item.Save`, :func:`~robodk.robolink.Robolink.AddStation`
        """
        with self._lock:
            self._check_connection()
            command = 'G_ActiveStn'
            self._send_line(command)
            stn = self._rec_item()
            self._check_status()
            return stn

    def setActiveStation(self, stn):
        """Set the active station (project currently visible)

        :param stn: station item, it can be previously loaded as an RDK file
        :type stn: :class:`.Item`

        .. seealso:: :func:`~robodk.robolink.Robolink.ActiveStation`, :func:`~robodk.robolink.Robolink.getOpenStations`, :func:`~robodk.robolink.Robolink.getParam`, :func:`~robodk.robolink.Item.Childs`, :func:`~robodk.robolink.Robolink.AddFile`, :func:`~robodk.robolink.Robolink.AddStation`
        """
        with self._lock:
            self._check_connection()
            command = 'S_ActiveStn'
            self._send_line(command)
            self._send_item(stn)
            self._check_status()

    def ShowSequence(self, matrix, display_type=SEQUENCE_DISPLAY_DEFAULT, timeout=-1):
        """Displays a sequence of joints or poses in RoboDK.

        :param matrix: list of joints as a matrix or as a list of joint arrays, a list of poses, or a sequence of instructions (same sequence that was supported with RoKiSim).
        :type matrix: list of list of float, a matrix of joints as a :class:`~robodk.robomath.Mat` or a list of poses as :class:`~robodk.robomath.Mat`
        :param display_type: display options (SEQUENCE_DISPLAY_*). Use -1 to use default.
        :type display_type: int, optional
        :param timeout: display timeout, in milliseconds. Use -1 to use default.
        :type timeout: int, optional

        Tip: use :func:`~robodk.robolink.Item.InstructionList` to retrieve the instruction list in RoKiSim format.

        .. seealso:: :func:`Item.ShowSequence() <robodk.robolink.Item.ShowSequence>`
        """
        Item(self, 0).ShowSequence(matrix, display_type, timeout)

    def LaserTracker_Measure(self, estimate=[0, 0, 0], search=False):
        """Takes a measurement using the laser tracker with respect to the tracker reference frame. If an estimate point is provided, the laser tracker will first move to those coordinates. If search is True, the tracker will search for a target.
        Returns the XYZ coordinates of target if it was found. Othewise it retuns None. For trackers that support a 6D measurement, the returned value with be an array of 6 values (list) to include the Euler angles."""
        with self._lock:
            self._check_connection()
            command = 'MeasLT2'
            self._send_line(command)
            self._send_xyz(estimate)
            self._send_int(1 if search else 0)
            xyz = self._rec_array().list()
            self._check_status()
            if len(xyz) < 3:
                return None

            # Old versions require checking against 0 mm
            if xyz[0] * xyz[0] + xyz[1] * xyz[1] + xyz[2] * xyz[2] < 0.0001:
                return None

            return xyz

    def MeasurePose(self, target=-1, time_avg_ms=0, tip_xyz=None):
        """Takes a measurement with a 6D measurement device. It returns two poses, the base reference frame and the measured object reference frame. Status is negative if the measurement failed. extra data is [error_avg, error_max] in mm, if we are averaging a pose.

        :param time_avg: Take the measurement for a period of time and average the result.
        :param tip_xyz: Offet the measurement to the tip.
        """
        with self._lock:
            array_send = [target, time_avg_ms]
            if tip_xyz is not None:
                array_send += tip_xyz[:3]
            else:
                array_send += [0, 0, 0]

            self._check_connection()
            command = 'MeasPose4'
            self._send_line(command)
            self._send_array(array_send)
            pose1 = self._rec_pose()
            data = self._rec_array().list()
            self._check_status()
            return pose1, data

    def Collision_Line(self, p1, p2, ref=robomath.eye(4)):
        """Checks the collision between a line and any objects in the station. The line is defined by 2 points.

        :param p1: start point of the line
        :type p1: list of float [x,y,z]
        :param p2: end point of the line
        :type p2: list of float [x,y,z]
        :param ref: Reference of the two points with respect to the absolute station reference.
        :type ref: :class:`~robodk.robomath.Mat`
        :return: [collision (True or False), item (collided), point (point of collision with respect to the station)]
        :rtype: [bool, :class:`.Item`, list of float as xyz]
        """
        with self._lock:
            p1abs = ref * p1
            p2abs = ref * p2
            self._check_connection()
            command = 'CollisionLine'
            self._send_line(command)
            self._send_xyz(p1abs)
            self._send_xyz(p2abs)
            itempicked = self._rec_item()
            xyz = self._rec_xyz()
            self._check_status()

            # Avoid a deadlock
            self._lock.release()
            collision = itempicked.Valid()
            self._lock.acquire()

            return collision, itempicked, xyz

    def setPoses(self, items, poses):
        """Sets the relative positions (poses) of a list of items with respect to their parent. For example, the position of an object/frame/target with respect to its parent.
        Use this function instead of setPose() for faster speed.

        .. seealso:: :func:`Item.setPose() <robodk.robolink.Item.setPose>`, :func:`Item.Pose() <robodk.robolink.Item.Pose>`, :func:`~robodk.robolink.Robolink.setPosesAbs`
        """
        with self._lock:
            if len(items) != len(poses):
                raise Exception('The number of items must match the number of poses')

            if len(items) == 0:
                return

            self._check_connection()
            command = 'S_Hlocals'
            self._send_line(command)
            self._send_int(len(items))
            for i in range(len(items)):
                self._send_item(items[i])
                self._send_pose(poses[i])
            self._check_status()

    def setPosesAbs(self, items, poses):
        """Set the absolute positions (poses) of a list of items with respect to the station reference. For example, the position of an object/frame/target with respect to its parent.
        Use this function instead of setPose() for faster speed.

        .. seealso:: :func:`Item.setPoseAbs() <robodk.robolink.Item.setPoseAbs>`, :func:`Item.PoseAbs() <robodk.robolink.Item.PoseAbs>`, :func:`~robodk.robolink.Robolink.setPoses`
        """
        with self._lock:
            if len(items) != len(poses):
                raise Exception('The number of items must match the number of poses')

            if len(items) == 0:
                return

            self._check_connection()
            command = 'S_Hlocal_AbsS'
            self._send_line(command)
            self._send_int(len(items))
            for i in range(len(items)):
                self._send_item(items[i])
                self._send_pose(poses[i])
            self._check_status()

    def Joints(self, robot_item_list):
        """Return the current joints of a list of robots.

        .. seealso:: :func:`Item.setJoints() <robodk.robolink.Item.setJoints>`, :func:`Item.Joints() ~robodk.robolink.Item.Joints`, :func:`~robodk.robolink.Robolink.setJoints`
        """
        with self._lock:
            self._check_connection()
            command = 'G_ThetasList'
            self._send_line(command)
            nrobs = len(robot_item_list)
            self._send_int(nrobs)
            joints_list = []
            for i in range(nrobs):
                self._send_item(robot_item_list[i])
                joints_i = self._rec_array()
                joints_list.append(joints_i)
            self._check_status()
            return joints_list

    def setJoints(self, robot_item_list, joints_list):
        """Sets the current robot joints for a list of robot items and a list joints.

        .. seealso:: :func:`Item.setJoints() <robodk.robolink.Item.setJoints>`, :func:`Item.Joints <robodk.robolink.Item.Joints>`, :func:`~robodk.robolink.Robolink.Joints`
        """
        with self._lock:
            nrobs = len(robot_item_list)
            if nrobs != len(joints_list):
                raise Exception('The size of the robot list does not match the size of the joints list')

            self._check_connection()
            command = 'S_ThetasList'
            self._send_line(command)
            self._send_int(nrobs)
            for i in range(nrobs):
                self._send_item(robot_item_list[i])
                self._send_array(joints_list[i])

            self._check_status()

    def CalibrateTool(self, poses_xyzwpr, input_format=EULER_RX_RY_RZ, algorithm=CALIBRATE_TCP_BY_POINT, robot=None, tool=None):
        """Calibrate a TCP given a list of poses/joints and following a specific algorithm/method.
        Tip: Provide the list of joints instead of poses to maximize accuracy for calibrated robots.

        :param poses_xyzwpr: List of points or a list of robot joints (matrix 3xN or nDOFsxN)
        :type poses_xyzwpr: :class:`~robodk.robomath.Mat` or a list of list of float
        :param int input_format: Euler format. Optionally, use JOINT_FORMAT and provide the robot.
        :param int algorithm: method/algorithm to use to calculate the new TCP. Tip: use CALIBRATE_TCP ...
        :param robot: the robot must be provided to calculate the reference frame by joints
        :type robot: :class:`.Item`
        :param tool: provide a tool item to store the calibration data with that tool (the TCP is not updated, only the calibration joints)
        :type tool: :class:`.Item`
        :return: \n
            [TCP, stats, errors]\n
            Out 1 (TCP) - The TCP as a list [x,y,z] with respect to the robot flange\n
            Out 2 (stats) - Statistics as [mean, standard deviation, max] - error stats summary\n
            Out 3 (errors) - List of errors for each pose (array 1xN)\n

        .. code-block:: python
            :caption: Available Tool Calibration Algorithms

            CALIBRATE_TCP_BY_POINT      # Take the same point using different orientations
            CALIBRATE_TCP_BY_PLANE      # Take the same point on a plane

        .. seealso:: :func:`~robodk.robolink.Robolink.CalibrateReference`
        """
        with self._lock:
            if type(poses_xyzwpr) == list and len(poses_xyzwpr) > 0 and type(poses_xyzwpr[0]) == robomath.Mat:
                nposes = len(poses_xyzwpr)
                if len(poses_xyzwpr) > 0:
                    input_format = EULER_RX_RYp_RZpp
                    matrix = []
                    for i in range(nposes):
                        matrix.append(robomath.Pose_2_Staubli(poses_xyzwpr[i]))

                    poses_xyzwpr = matrix

            self._check_connection()
            command = 'CalibTCP3'
            self._send_line(command)
            self._send_matrix(poses_xyzwpr)
            self._send_int(input_format)
            if type(algorithm) != list:
                algorithm = [algorithm]

            self._send_array(algorithm)
            self._send_item(robot)
            self._send_item(tool)
            self.COM.settimeout(3600)
            TCPxyz = self._rec_array()
            self.COM.settimeout(self.TIMEOUT)
            errorstats = self._rec_array()
            errors = self._rec_matrix()
            self._check_status()
            if errors.size(1) > 0:
                errors = errors[:, 1].list()
            else:
                errors = []
            return TCPxyz.list(), errorstats.list(), errors

    def CalibrateReference(self, joints_points, method=CALIBRATE_FRAME_3P_P1_ON_X, use_joints=False, robot=None):
        """Calibrate a reference frame given a number of points and following a specific algorithm/method.
        Important: Provide the list of joints to maximize accuracy for calibrated robots.

        :param joints_points: List of points or a list of robot joints (matrix 3xN or nDOFsxN)
        :type joints_points: :class:`~robodk.robomath.Mat` or a list of list of float
        :param int method: method/algorithm to use to calculate the new TCP. Tip: use CALIBRATE_FRAME ...
        :param bool use_joints: use points or joint values (bool): Set to True if joints_points is a list of joints
        :param robot: the robot must be provided to calculate the reference frame by joints
        :type robot: :class:`.Item`
        :return: The pose of the reference frame with respect to the robot base frame
        :rtype: :class:`~robodk.robomath.Mat`

        .. code-block:: python
            :caption: Available Reference Frame Calibration Algorithms

            CALIBRATE_FRAME_3P_P1_ON_X = 0      # Calibrate by 3 points: [X, X+, Y+] (p1 on X axis)
            CALIBRATE_FRAME_3P_P1_ORIGIN = 1    # Calibrate by 3 points: [Origin, X+, XY+] (p1 is origin)
            CALIBRATE_FRAME_6P = 2              # Calibrate by 6 points
            CALIBRATE_TURNTABLE = 3             # Calibrate turntable
            CALIBRATE_TURNTABLE = 4             # Calibrate 2-axis turntable

        .. seealso:: :func:`~robodk.robolink.Robolink.CalibrateTool`
        """
        with self._lock:
            self._check_connection()
            command = 'CalibFrame'
            self._send_line(command)
            self._send_matrix(joints_points)
            self._send_int(-1 if use_joints else 0)
            self._send_int(method)
            self._send_item(robot)
            reference_pose = self._rec_pose()
            stats_data = self._rec_array()
            self._check_status()

            stats_data = stats_data.list()
            # We'll receive addditional information when calibrating a 1 axis or 2 axis turntable
            if len(stats_data) > 3:
                return reference_pose, stats_data

            return reference_pose

    def ProgramStart(self, programname, folder='', postprocessor='', robot=None):
        """Defines the name of the program when the program is generated (offline programming).
        It is also possible to specify the name of the post processor as well as the folder to save the program.
        This method must be called before any program output is generated (before any robot movement or other instruction).

        :param str progname: Name of the program
        :param str folder: Folder to save the program, leave empty to use the default program folder (usually Desktop)
        :param str postprocessor: Name of the post processor. For example, to select the post processor C:/RoboDK/Posts/Fanuc_RJ3.py, specify "Fanuc_RJ3.py" or simply "Fanuc_RJ3".
        :param robot: Robot used for program generation
        :type robot: :class:`.Item`

        Example:

        .. code-block:: python

            from robodk.robolink import *            # import the robolink library
            RDK = Robolink()                         # connect to the RoboDK API (RoboDK starts if it has not started
            robot = RDK.Item('', ITEM_TYPE_ROBOT)    # use the first available robot
            RDK.ProgramStart('Prog1','C:/MyProgramFolder/', "ABB_RAPID_IRC5", robot)  # specify the program name for program generation
            # RDK.setRunMode(RUNMODE_MAKE_ROBOTPROG) # redundant
            robot.MoveJ(target)                      # make a simulation
            ...
            RDK.Finish()                             # Provokes the program generation (disconnects the API)

        .. seealso:: :func:`~robodk.robolink.Robolink.setRunMode`, :func:`~robodk.robolink.Robolink.AddProgram`, :func:`~robodk.robolink.Robolink.Finish`
        """
        with self._lock:
            self._check_connection()
            command = 'ProgramStart'
            self._send_line(command)
            self._send_line(programname)
            self._send_line(folder)
            self._send_line(postprocessor)
            if robot is None:
                self._send_item(Item(None))
            else:
                self._send_item(robot)
            errors = self._rec_int()
            self._check_status()
            return errors

    def setViewPose(self, pose):
        """Set the pose of the world reference frame with respect to the view (camera/screen)

        :param pose: pose of the item with respect to its parent
        :type pose: :class:`~robodk.robomath.Mat`
        """
        with self._lock:
            self._check_connection()
            command = 'S_ViewPose'
            self._send_line(command)
            self._send_pose(pose)
            self._check_status()

    def ViewPose(self):
        """Get the pose of the world reference frame with respect to the view (camera/screen)"""
        with self._lock:
            self._check_connection()
            command = 'G_ViewPose'
            self._send_line(command)
            pose = self._rec_pose()
            self._check_status()
            return pose

    def BuildMechanism(self, type, list_obj, parameters, joints_build, joints_home, joints_senses, joints_lim_low, joints_lim_high, base=robomath.eye(4), tool=robomath.eye(4), name="New robot", robot=None):
        """Create a new robot or mechanism.

        :param int type: Type of the mechanism
        :param list list_obj: list of object items that build the robot
        :param list parameters: robot parameters in the same order as shown in the RoboDK menu: Utilities-Build Mechanism or robot
        :param list_joints_build: current state of the robot (joint axes) to build the robot
        :param list joints_home: joints for the home position (it can be changed later)
        :param robot: existing robot in the station to replace it (optional)
        :type robot: :class:`.Item`
        :param str name: robot name

        Example:

        .. code-block:: python

            # Start the RoboDK API
            from robodk.robolink import *
            from robodk.robomath import *
            RDK = Robolink()

            # Define your new robot or mechanism
            # Example to create a Fanuc LR Mate 200iD robot
            robot_name = 'Fanuc LR Mate 200iD'
            DOFs       = 6

            # Define the joints of the robot/mechanism
            joints_build = [0, 0, 0, 0, 0, 0]

            # Define the home position of the robot/mechanism (default position when you build the mechanism)
            # This is also the position the robot goes to if you select "Home"
            joints_home   = [0, 0, 0, 0, 0, 0]

            # Define the robot parameters. The parameters must be provided in the same order they appear
            #     in the menu Utilities-Model Mechanism or robot
            # Some basic mechanisms such as 1 or 2 axis translation/rotation axes don't need any parameters
            #     (translation/rotation will happen around the Z axis)
            #parameters = []
            parameters = [330, 50, 0, 330, 35, 335, 80, 0, -90, 0, 0, 0, 0]

            # Define the joint sense (set to +1 or -1 for each axis (+1 is used as a reference for the ABB IRB120 robot)
            joints_senses   = [+1, +1, -1,  -1, -1, -1] # add -1 as 7th index to account for axis 2 and axis 3 coupling

            # Joint limits (lower limits for each axis)
            lower_limits  = [-170, -100, -67, -190, -125, -360]

            # Joint limits (upper limits for each axis)
            upper_limits  = [ 170,  145, 213,  190,  125,  360]

            # Base frame pose (offset the model by applying a base frame transformation)
            #base_pose   = xyzrpw_2_pose([0, 0, 0, 0, 0, 0])
            # Fanuc and Motoman robots have the base frame at the intersection of axes 1 and 2
            base_pose   = xyzrpw_2_pose([0, 0, -330, 0, 0, 0])

            # Tool frame pose (offset the tool flange by applying a tool frame transformation)
            tool_pose   = xyzrpw_2_pose([0, 0, 0, 0, 0, 0])

            # Retrieve all your items from RoboDK (they should be previously loaded manually or using the API's command RDK.AddFile())
            list_objects   = []
            for i in range(DOFs + 1):
               if i == 0:
                   itm = RDK.Item(robot_name + ' Base', ITEM_TYPE_OBJECT)
               else:
                   itm = RDK.Item(robot_name + ' ' + str(i), ITEM_TYPE_OBJECT)

               list_objects.append(itm)

            # Create the robot/mechanism
            new_robot = RDK.BuildMechanism(MAKE_ROBOT_6DOF, list_objects, parameters, joints_build, joints_home, joints_senses, lower_limits, upper_limits, base_pose, tool_pose, robot_name)
            if not new_robot.Valid():
                print("Failed to create the robot. Check input values.")
            else:
                print("Robot/mechanism created: " + new_robot.Name())

        """

        # calculate the number of degrees of freedom
        with self._lock:
            ndofs = len(list_obj) - 1
            self._check_connection()
            command = 'BuildMechanism'
            self._send_line(command)
            self._send_item(robot)
            self._send_line(name)
            self._send_int(type)
            self._send_int(ndofs)
            for i in range(ndofs + 1):
                self._send_item(list_obj[i])
            self._send_pose(base)
            self._send_pose(tool)
            self._send_array(parameters)
            if len(joints_build) < 12:
                joints_build += [0] * (12 - len(joints_build))
            joints_data = robomath.Mat([joints_build, joints_home, joints_senses, joints_lim_low, joints_lim_high]).tr()
            self._send_matrix(joints_data)
            robot = self._rec_item()
            self._check_status()
            return robot

    #------------------------------------------------------------------
    #----------------------- CAMERA VIEWS ----------------------------
    def Cam2D_Add(self, item_object=None, cam_params="", camera_item=None):
        """Open a simulated 2D camera view. Returns a handle pointer that can be used in case more than one simulated view is used.

        :param item_object: object to attach the camera
        :type item_object: :class:`.Item`
        :param str cam_params: Camera parameters as a string. Add one or more commands as shown in the following example.
        :param camera_item: Use an existing camera item to modify settings and open the view (supported on RoboDK v5.0 and later)
        :type camera_item: :class:`.Item`


        Example:

        .. code-block:: python

            from robodk.robolink import *    # API to communicate with RoboDK
            RDK = Robolink()

            # Close any open 2D camera views
            RDK.Cam2D_Close()

            camref = RDK.ItemUserPick('Select the Camera location (reference, tool or object)')
            #camref = RDK.Item('Frame 7',ITEM_TYPE_FRAME)

            # Set parameters in mm and degrees:
            #  FOV: Field of view in degrees (2*atan(0.5*height/distance) of the sensor
            #  FOCAL_LENGTH: focal length in mm
            #  FAR_LENGTH: maximum working distance (in mm)
            #  PIXELSIZE: Size of the pixel in micro meters (square size assumed)
            #  SIZE: size of the window in pixels (fixed) (width x height)
            #    WINDOWFIXED: If we specify the Size, make the size of the window exactly the same size
            #    WINDOWRESIZE: Even if we specify the size
            #  SNAPSHOT: size of the snapshot image in pixels if it should be different from the normal size (width x height). Size can be larger than 4k, depending on graphics card support.
            #  BG_COLOR: background color (rgb color or named color: AARRGGBB)
            #  LIGHT_AMBIENT: ambient color (rgb color or named color: AARRGGBB)
            #  LIGHT_SPECULAR: specular color (rgb color or named color: AARRGGBB)
            #  LIGHT_DIFFUSE: diffuse color (rgb color or named color: AARRGGBB)
            #  DEPTH: Add this flag to create a 32 bit depth map (white=close, black=far)
            #  GRAYSCALE: Add this flag to create a grayscale image
            #  NO_TASKBAR: Don't add the window to the task bar
            #  MINIMIZED: Show the window minimized
            #  ALWAYS_VISIBLE: Keep the window on top of all other windows
            #  DOCKED: Show the view as a docked window (not a separate window)
            #  SHADER_VERTEX: File to a vertex shader (GLSL file)
            #  SHADER_FRAGMENT: File to a fragment shader (GLSL file)

            # Examples to call Camd2D_Add:

            # Camera without a fixed window size and 1000 mm length
            cam_id = RDK.Cam2D_Add(camref, 'FOCAL_LENGTH=6 FOV=32 FAR_LENGTH=1000')

            # Camera with a fixed window size and 1000 mm length
            cam_id = RDK.Cam2D_Add(camref, 'FOCAL_LENGTH=6 FOV=32 FAR_LENGTH=1000 SIZE=640x480')

            # Camera with a black background
            cam_id = RDK.Cam2D_Add(camref, 'FOCAL_LENGTH=6 FOV=32 FAR_LENGTH=1000 SIZE=640x480 BG_COLOR=black')

            # Camera without a fixed window size and high resolution snapshot
            cam_id = RDK.Cam2D_Add(camref, 'FOCAL_LENGTH=6 FOV=32 FAR_LENGTH=1000 SIZE=640x480')

            # Depth view: 32 bit depth map (white=close, black=far)
            cam_id = RDK.Cam2D_Add(camref, 'FOCAL_LENGTH=6 FOV=32 FAR_LENGTH=1000 SIZE=640x480 DEPTH')

            # Minimized camera
            cam_id = RDK.Cam2D_Add(camref, 'FOCAL_LENGTH=6 FOV=32 FAR_LENGTH=1000 SIZE=640x480 MINIMIZED')

            # Do not show the camera window in the taskbar
            cam_id = RDK.Cam2D_Add(camref, 'FOCAL_LENGTH=6 FOV=32 FAR_LENGTH=1000 SIZE=640x480 NO_TASKBAR')

            # Customize the light
            cam_id = RDK.Cam2D_Add(camref, 'FOCAL_LENGTH=6 FOV=32 FAR_LENGTH=1000 SIZE=640x480 BG_COLOR=black LIGHT_AMBIENT=red LIGHT_DIFFUSE=#FF00FF00 LIGHT_SPECULAR=black')
            cam_id = RDK.Cam2D_Add(camref, 'FOCAL_LENGTH=6 FOV=32 FAR_LENGTH=600 SIZE=640x480 BG_COLOR=black LIGHT_AMBIENT=red LIGHT_DIFFUSE=black LIGHT_SPECULAR=white')
            cam_id = RDK.Cam2D_Add(camref, 'FOCAL_LENGTH=6 FOV=32 FAR_LENGTH=1000 SIZE=640x480 LIGHT_AMBIENT=red')

            # Provoke a popup and allow the user to enter some parameters
            cam_id = RDK.Cam2D_Add(camref, 'POPUP')

            # Example to take a snapshot from the camera
            RDK.Cam2D_Snapshot(RDK.getParam('PATH_OPENSTATION') + "/sample_image.png", cam_id)

            # Special command to retrieve the window ID:
            win_id = RDK.Command("CamWinID", str(cam_id))
            # print(str(win_id))

            #-----------------------------------------------------------------------------------
            # Example to use a customized shader to customize the effect of light
            # Tip: Use the example: C:/RoboDK/Library/Example-Shader-Customized-Light.rdk
            # Tip: If you need a fixed light source update the variable light_Position in the shader_fragment.glsl file

            # Get the path to the RoboDK library (usually in C:/RoboDK/Library/)
            path_library = RDK.getParam("PATH_LIBRARY")
            file_shader_fragment = path_library + '/Macros/Camera-Shaders/shader_fragment.glsl'
            file_shader_vertex = path_library + '/Macros/Camera-Shaders/shader_vertex.glsl'
            cam_id = RDK.Cam2D_Add(camref, 'FOCAL_LENGTH=6 FOV=32 FAR_LENGTH=2500 SHADER_FRAGMENT=' + file_shader_fragment + ' SHADER_VERTEX=' + file_shader_vertex)


        .. seealso:: :func:`~robodk.robolink.Robolink.Cam2D_Snapshot`, :func:`~robodk.robolink.Robolink.Cam2D_Close`, :func:`~robodk.robolink.Robolink.Cam2D_SetParams`
        """
        with self._lock:
            self._check_connection()
            if self.CAMERA_AS_ITEM:
                self._require_build(17779)
                command = 'Cam2D_PtrAdd'
                self._send_line(command)
                self._send_item(item_object)
                self._send_item(camera_item)
                self._send_line(cam_params)
                cam_handle = self._rec_item()

            else:
                command = 'Cam2D_Add'
                self._send_line(command)
                self._send_item(item_object)
                self._send_line(cam_params)
                cam_handle = self._rec_ptr()
            self._check_status()
            return cam_handle

    def Cam2D_Snapshot(self, file_save_img="", cam_handle=0, params=""):
        """Take a snapshot from a simulated camera view and save it to a file. Returns 1 if success, 0 otherwise.

        :param str file_save_img: file path to save. Formats supported include PNG, JPEG, TIFF, ...
        :param int cam_handle: camera handle (item returned by Cam2D_Add). If the camera handle is set to None it will take a snapshot of the full 3D views.
        :param str params: additional options (use, "Grayscale", "Depth" or "Color" to modify the camera snapshot)

        .. seealso:: :func:`~robodk.robolink.Robolink.Cam2D_Add`, :func:`~robodk.robolink.Robolink.Cam2D_Close`
        """
        with self._lock:
            if type(file_save_img) is not str:
                raise Exception("The first argument must be a valid file name (str)")

            self._check_connection()
            if type(cam_handle) is int:
                command = 'Cam2D_Snapshot'
                self._send_line(command)
                self._send_ptr(int(cam_handle))
                self._send_line(file_save_img)
                success = self._rec_int()

            else:
                # Camera is an item
                self._require_build(17779)
                command = 'Cam2D_PtrSnapshot'
                self._send_line(command)
                self._send_item(cam_handle)
                self._send_line(file_save_img)
                self._send_line(params)
                self.COM.settimeout(3600)
                if len(file_save_img) == 0:
                    # If the file name is empty we are expecting a byte array as PNG file
                    success = self._rec_bytes()
                else:
                    success = self._rec_int()
                self.COM.settimeout(self.TIMEOUT)

            self._check_status()
            return success

    def Cam2D_Close(self, cam_handle=0):
        """Closes all camera windows or one specific camera if the camera handle is provided. Returns True if success, False otherwise.

        :param cam_handle: camera handle (pointer returned by Cam2D_Add). Leave to 0 to close all simulated views.
        :type cam_handle: int

        .. seealso:: :func:`~robodk.robolink.Robolink.Cam2D_Add`, :func:`~robodk.robolink.Robolink.Cam2D_Snapshot`"""
        with self._lock:
            self._check_connection()
            if type(cam_handle) is int:
                if cam_handle == 0:
                    command = 'Cam2D_CloseAll'
                    self._send_line(command)
                else:
                    command = 'Cam2D_Close'
                    self._send_line(command)
                    self._send_ptr(cam_handle)
            else:
                self._require_build(17779)
                command = 'Cam2D_PtrClose'
                self._send_line(command)
                self._send_item(cam_handle)

            success = self._rec_int() > 0
            self._check_status()
            return success

    def Cam2D_SetParams(self, params, cam_handle=0):
        """Set the parameters of the simulated camera.
        Returns 1 if success, 0 otherwise.

        :param str params: parameter settings according to the parameters supported by Cam2D_Add

        .. seealso:: :func:`~robodk.robolink.Robolink.Cam2D_Add`
        """
        with self._lock:
            self._check_connection()
            if type(cam_handle) is int:
                command = 'Cam2D_SetParams'
                self._send_line(command)
                self._send_ptr(int(cam_handle))
                self._send_line(params)
                success = self._rec_int()
            else:
                command = 'Cam2D_PtrSetParams'
                self._send_line(command)
                self._send_item(cam_handle)
                self._send_line(params)
                success = self._rec_int()

            self._check_status()
            return success

    #------------------------------------------------------------------
    #----------------------- SPRAY GUN SIMULATION ----------------------------
    def Spray_Add(self, item_tool=0, item_object=0, params="", points=None, geometry=None):
        """Add a simulated spray gun that allows projecting particles to a part. This is useful to simulate applications such as:
        arc welding, spot welding, 3D printing, painting, inspection or robot machining to verify the trace.

        The scripts ArcStart, ArcEnd and WeldOn and SpindleOn behave in a similar way, the only difference is the default behavior
        This behavior simmulates Fanuc Arc Welding and triggers appropriate output when using the customized post processor.

        Select ESC to clear the trace manually.

        Example scripts that use Spray_Add in **Library/Macros**:

        * SpindleOn / SpindleOff: Turn trace On/Off
        * ArcOn / ArcOff: Turn trace On/Off
        * SprayOn / SprayOff: Simulate a spray given a workspace volume (for painting)
        * WeldOn / WeldOff: Support for multiple weld guns

        Examples:

        * SpindleOn(2): Show the trace in blue
        * SpindleOn(red): Show the trace in red
        * SpindleOff: Turn off the trace
        * SpindleOn(green,2.5): Green trace with a sphere of radius 2.5 mm

        .. image:: TraceOn.png

        :param str params: A string specifying the behavior of the simulated particles. The string can contain one or more of the following commands (separated by a space). See the allowed parameter options.
        :param points: provide the volume as a list of points as described in the sample macro SprayOn.py
        :type points: :class:`~robodk.robomath.Mat`
        :param geometry: (optional) provide a list of points describing triangles to define a specific particle geometry. Use this option instead of the PARTICLE command.
        :type geometry: :class:`~robodk.robomath.Mat`

        .. code-block:: python
            :caption: Allowed parameter options

            STEP=AxB: Defines the grid to be projected 1x1 means only one line of particle projection (for example, for welding)
            PARTICLE: Defines the shape and size of particle (sphere or particle), unless a specific geometry is provided:
                a- SPHERE(radius, facets)
                b- SPHERE(radius, facets, scalex, scaley, scalez)
                b- CUBE(sizex, sizey, sizez)
            RAND=factor: Defines a random factor factor 0 means that the particles are not deposited randomly
            ELLYPSE: defines the volume as an ellypse (default)
            RECTANGLE: defines the volume as a rectangle
            PROJECT: project the particles to the surface (default) (for welding, painting or scanning)
            NO_PROJECT: does not project the particles to the surface (for example, for 3D printing)

        .. seealso:: :func:`~robodk.robolink.Robolink.Spray_SetState`, :func:`~robodk.robolink.Robolink.Spray_GetStats`, :func:`~robodk.robolink.Robolink.Spray_Clear`

        Example:

        .. code-block:: python

            tool = 0    # auto detect active tool
            obj = 0     # auto detect object in active reference frame

            options_command = "ELLYPSE PROJECT PARTICLE=SPHERE(4,8,1,1,0.5) STEP=8x8 RAND=2"

            # define the ellypse volume as p0, pA, pB, colorRGBA (close and far), in mm
            # coordinates must be provided with respect to the TCP
            close_p0 = [   0,   0, -200] # xyz in mm: Center of the conical ellypse (side 1)
            close_pA = [   5,   0, -200] # xyz in mm: First vertex of the conical ellypse (side 1)
            close_pB = [   0,  10, -200] # xyz in mm: Second vertex of the conical ellypse (side 1)
            close_color = [ 1, 0, 0, 1]  # RGBA (0-1)

            far_p0   = [   0,   0,  50] # xyz in mm: Center of the conical ellypse (side 2)
            far_pA   = [  60,   0,  50] # xyz in mm: First vertex of the conical ellypse (side 2)
            far_pB   = [   0, 120,  50] # xyz in mm: Second vertex of the conical ellypse (side 2)
            far_color   = [ 0, 0, 1, 0.2]  # RGBA (0-1)

            close_param = close_p0 + close_pA + close_pB + close_color
            far_param = far_p0 + far_pA + far_pB + far_color
            volume = robomath.Mat([close_param, far_param]).tr()
            RDK.Spray_Add(tool, obj, options_command, volume)
            RDK.Spray_SetState(SPRAY_ON)

        """
        with self._lock:
            self._check_connection()
            command = 'Gun_Add'
            self._send_line(command)
            self._send_item(item_tool)
            self._send_item(item_object)
            self._send_line(params)
            self._send_matrix(points)
            self._send_matrix(geometry)
            id_spray = self._rec_int()
            self._check_status()
            return id_spray

    def Spray_SetState(self, state=SPRAY_ON, id_spray=-1):
        """Sets the state of a simulated spray gun (ON or OFF)

        :param int state: Set to ON or OFF. Use the defined constants: SPRAY_*
        :param int id_spray: spray handle (pointer returned by Spray_Add). Leave to -1 to apply to all simulated sprays.

        .. seealso:: :func:`~robodk.robolink.Robolink.Spray_Add`, :func:`~robodk.robolink.Robolink.Spray_GetStats`, :func:`~robodk.robolink.Robolink.Spray_Clear`
        """
        with self._lock:
            self._check_connection()
            command = 'Gun_SetState'
            self._send_line(command)
            self._send_int(id_spray)
            self._send_int(state)
            success = self._rec_int()
            self._check_status()
            return success

    def Spray_GetStats(self, id_spray=-1):
        """Gets statistics from all simulated spray guns or a specific spray gun.

        :param int id_spray: spray handle (pointer returned by Spray_Add). Leave to -1 to apply to all simulated sprays.

        .. seealso:: :func:`~robodk.robolink.Robolink.Spray_Add`, :func:`~robodk.robolink.Robolink.Spray_SetState`, :func:`~robodk.robolink.Robolink.Spray_Clear`
        """
        with self._lock:
            self._check_connection()
            command = 'Gun_Stats'
            self._send_line(command)
            self._send_int(id_spray)
            info = self._rec_line().replace('<br>', '\t')
            data = self._rec_matrix()
            self._check_status()
            return info, data

    def Spray_Clear(self, id_spray=-1):
        """Stops simulating a spray gun. This will clear the simulated particles.

        :param int id_spray: spray handle (pointer returned by Spray_Add). Leave the default -1 to apply to all simulated sprays.

        .. seealso:: :func:`~robodk.robolink.Robolink.Spray_Add`, :func:`~robodk.robolink.Robolink.Spray_SetState`, :func:`~robodk.robolink.Robolink.Spray_GetStats`
        """
        with self._lock:
            self._check_connection()
            command = 'Gun_Clear'
            self._send_line(command)
            self._send_int(id_spray)
            success = self._rec_int()
            self._check_status()
            return success

    def License(self):
        """Get the license string"""
        with self._lock:
            self._check_connection()
            command = 'G_License2'
            self._send_line(command)
            lic_name = self._rec_line()
            lic_cid = self._rec_line()
            self._check_status()
            return lic_name, lic_cid

    def Selection(self):
        """Return the list of currently selected items

        :return: List of items
        :rtype: list of :class:`.Item`"""
        with self._lock:
            self._check_connection()
            command = 'G_Selection'
            self._send_line(command)
            nitems = self._rec_int()
            item_list = []
            for i in range(nitems):
                item_list.append(self._rec_item())
            self._check_status()
            return item_list

    def setSelection(self, list_items=[]):
        """Set the selection in the tree

        :param list list_items: List of items to set as selected"""
        with self._lock:
            self._require_build(8896)
            self._check_connection()
            command = 'S_Selection'
            self._send_line(command)
            self._send_int(len(list_items))
            for itm in list_items:
                self._send_item(itm)

            if self._SkipStatus:
                self.COM.flush()
                return self

            self._check_status()

    def MergeItems(self, list_items=[]):
        """Merge multiple object items as one. Source objects are not deleted and a new object is created.

        :param list list_items: List of items to set as selected
        :return: New object created
        :rtype: :class:`.Item`"""
        with self._lock:
            self._require_build(8896)
            self._check_connection()
            command = 'MergeItems'
            self._send_line(command)
            self._send_int(len(list_items))
            for itm in list_items:
                self._send_item(itm)
            newitem = self._rec_item()
            self._check_status()
            return newitem

    def Popup_ISO9283_CubeProgram(self, robot=0):
        """Popup the menu to create the ISO9283 cube program (Utilities-Create Cube ISO)

        :return: Created program. The program is invalid.
        :rtype: :class:`.Item`"""
        with self._lock:
            self._require_build(5177)
            self._check_connection()
            command = 'Popup_ProgISO9283'
            self._send_line(command)
            self._send_item(robot)
            self.COM.settimeout(3600)
            iso_program = self._rec_item()
            self.COM.settimeout(self.TIMEOUT)
            self._check_status()
            return iso_program

    def setInteractiveMode(self, mode_type=SELECT_MOVE, default_ref_flags=DISPLAY_REF_DEFAULT, custom_objects=None, custom_ref_flags=None):
        """Set the interactive mode to define the behavior when navigating and selecting items in RoboDK's 3D view.

        :param int mode_type: The mode type defines what accion occurs when the 3D view is selected (Select object, Pan, Rotate, Zoom, Move Objects, ...)
        :param int default_ref_flags: When a movement is specified, we can provide what motion we allow by default with respect to the coordinate system (set apropriate flags)
        :param list custom_objects: Provide a list of optional items to customize the move behavior for these specific items (important: the length of custom_ref_flags must match)
        :param list custom_ref_flags: Provide a matching list of flags to customize the movement behavior for specific items
        """
        with self._lock:
            self._check_connection()
            command = 'S_InteractiveMode'
            self._send_line(command)
            self._send_int(mode_type)
            self._send_int(default_ref_flags)
            if custom_objects is None or custom_ref_flags is None:
                self._send_int(-1)
            else:
                nitems = min(len(custom_objects), len(custom_ref_flags))
                self._send_int(nitems)
                for i in range(nitems):
                    self._send_item(custom_objects[i])
                    self._send_int(custom_ref_flags[i])

            self._check_status()

    def CursorXYZ(self, x_coord=-1, y_coord=-1):
        """Returns the position of the cursor as XYZ coordinates (by default), or the 3D position of a given set of 2D coordinates of the window (x & y coordinates in pixels from the top left corner)
        The XYZ coordinates returned are given with respect to the RoboDK station (absolute reference).
        If no coordinates are provided, the current position of the cursor is retrieved.

        :param int x_coord: X coordinate in pixels
        :param int y_coord: Y coordinate in pixels

        .. code-block:: python
            :caption: Example to retrieve the 3D point under the mouse cursor

            RDK = Robolink()
            while True:
                xyz, item = RDK.CursorXYZ()
                print(str(item) + " " + str(xyz))

        """
        with self._lock:
            self._check_connection()
            command = 'Proj2d3d'
            self._send_line(command)
            self._send_int(x_coord)
            self._send_int(y_coord)
            selection = self._rec_int()
            item = self._rec_item()
            xyz = self._rec_xyz()
            self._check_status()
            return xyz, item

    def GetPoints(self, feature_type=FEATURE_HOVER_OBJECT_MESH):
        """Retrieves the object under the mouse cursor.

        :param int feature_type: set to FEATURE_HOVER_OBJECT_MESH to retrieve object under the mouse cursor, the selected feature and mesh, or FEATURE_HOVER_OBJECT if you don't need the mesh (faster).

        :return: Object under the mouse cursor, selected feature, feature id, list of points and description

        .. code-block:: python

            # Infinite loop to print the item under the mouse cursor
            while True:
                object, feature_type, feature_id, feature_name, points = RDK.GetPoints(FEATURE_HOVER_OBJECT) # Faster if you don't need the mesh
                #object, feature_type, feature_id, feature_name, points = RDK.GetPoints(FEATURE_HOVER_OBJECT_MESH)

                if object.Valid():
                    print("Mouse on: " + object.Name() + ": " + feature_name + " Type/id=" + str(feature_type) + "/" + str(feature_id))
                    # print(points)
                    # RDK.Selection() # returns selection
                    if object in RDK.Selection():
                        print("Object is selected!")
                        #RDK.setSelection([]) # Clear selection

                else:
                    print("Nothing under the mouse cursor")

                pause(0.1)

        .. seealso:: :func:`~robodk.robolink.Item.SelectedFeature`
        """
        if feature_type < FEATURE_HOVER_OBJECT_MESH:
            raise Exception("Invalid feature type, use FEATURE_HOVER_OBJECT_MESH, FEATURE_HOVER_OBJECT or equivalent")

        with self._lock:
            self._check_connection()
            command = 'G_ObjPoint'
            self._send_line(command)
            self._send_item(None)
            self._send_int(feature_type)
            feature_id = 0  #not used here
            self._send_int(feature_id)
            points = None
            if feature_type == FEATURE_HOVER_OBJECT_MESH:
                points = self._rec_matrix()
                points = list(points)

            object = self._rec_item()
            is_frame = self._rec_int() > 0
            feature_type = self._rec_int()
            feature_id = self._rec_int()
            feature_name = self._rec_line()
            self._check_status()
            return object, feature_type, feature_id, feature_name, points

    def PluginLoad(self, plugin_name="", load=1):
        """Load or unload the specified plugin (path to DLL, dylib or SO file). If the plugin is already loaded it will unload the plugin and reload it. Pass an empty plugin_name to reload all plugins.

        :param str plugin_name: name of the plugin or path (if it is not in the default directory.
        :param int load: load the plugin (1/default) or unload (0)

        .. code-block:: python
            :caption: Example to load a plugin

            RDK = Robolink()
            RDK.PluginLoad("C:/RoboDK/bin/plugin/yourplugin.dll")
            # or if the Add-in is located in the default folder you can simply do:
            RDK.PluginLoad("yourplugin")

            # You can also load the library in RoboDK as you would open any other file:
            RDK.AddFile("C:/RoboDK/bin/plugin/yourplugin.dll")

        """
        result = ""
        if load:
            if load >= 2:
                #result = self.Command("PluginReload", plugin_name) # crash?
                result = self.Command("PluginUnload", plugin_name)
                result = self.Command("PluginLoad", plugin_name)
            else:
                result = self.Command("PluginLoad", plugin_name)
        else:
            result = self.Command("PluginUnload", plugin_name)

        success = result == "OK"
        return success

        # Old version:
        #with self._lock:
        #    self._check_connection()
        #    command = 'PluginLoad'
        #    self._send_line(command)
        #    self._send_line(plugin_name)
        #    self._send_int(load)
        #    self._check_status()

    def PluginCommand(self, plugin_name, plugin_command="", value=""):
        """Send a specific command to a RoboDK plugin. The command and value (optional) must be handled by your plugin. It returns the result as a string.

        :param str plugin_name: The plugin name must match the PluginName() implementation in the RoboDK plugin.
        :param str command: Specific command handled by your plugin
        :param str value: Specific value (optional) handled by your plugin
        """
        with self._lock:
            self._check_connection()
            command = 'PluginCommand'
            self._send_line(command)
            self._send_line(plugin_name)
            self._send_line(plugin_command)
            self._send_line(str(value))
            self.COM.settimeout(3600 * 24 * 7)
            result = self._rec_line()
            self.COM.settimeout(self.TIMEOUT)
            self._check_status()
            return result

    def EmbedWindow(self, window_name, docked_name=None, size_w=-1, size_h=-1, pid=0, area_add=1, area_allowed=15, timeout=500):
        """Embed a window from a separate process in RoboDK as a docked window. Returns True if successful.

        Note: This function should be called on a seperate thread. Use the static function: :func:`~robodk.robolink.EmbedWindow` instead.

        :param str window_name: The name of the window currently open. Make sure the window name is unique and it is a top level window
        :param str docked_name: Name of the docked tab in RoboDK (optional, if different from the window name)
        :param int pid: Process ID (optional)
        :param int area_add: Set to 1 (right) or 2 (left) (default is 1)
        :param int area_allowed: Areas allowed (default is 15:no constrain)
        :param int timeout: Timeout to abort attempting to embed the window

        .. seealso:: :func:`~robodk.robolink.EmbedWindow`

        """
        with self._lock:
            if not docked_name:
                docked_name = window_name

            self._check_connection()
            command = 'WinProcDock'
            self._send_line(command)
            self._send_line(docked_name)
            self._send_line(window_name)
            self._send_array([size_w, size_h])
            self._send_line(str(pid))
            self._send_int(area_allowed)
            self._send_int(area_add)
            self._send_int(timeout)
            result = self._rec_int()
            self._check_status()
            return result > 0


class Item:
    """The Item class represents an item in RoboDK station. An item can be a robot, a frame, a tool, an object, a target, ... any item visible in the station tree.
    An item can also be seen as a node where other items can be attached to (child items).
    Every item has one parent item/node and can have one or more child items/nodes.

    RoboDK Items are automatically created and retrieved by generated by :class:`.Robolink` methods such as :func:`~robodk.robolink.Robolink.Item` and :func:`~robodk.robolink.Robolink.ItemUserPick`

    .. seealso:: :func:`~robodk.robolink.Robolink.Item`, :func:`~robodk.robolink.Robolink.ItemUserPick`

    .. code-block:: python

            from robodk.robolink import *   # Import the robolink library
            RDK = Robolink()                # Connect to the RoboDK API (RoboDK starts if it has not started
            tool  = RDK.Item('Tool')                         # Get an item named Tool (name in the RoboDK station tree)
            robot = RDK.Item('', ITEM_TYPE_ROBOT)            # Get the first available robot
            target = RDK.Item('Target 1', ITEM_TYPE_TARGET)  # Get a target called "Target 1"
            frame = RDK.ItemUserPick('Select a reference frame', ITEM_TYPE_FRAME)  # Prompt the user to select a reference frame

            robot.setPoseFrame(frame)
            robot.setPoseTool(tool)
            robot.MoveJ(target)             # Move the robot to the target using the selected reference frame
    """

    def __init__(self, link, ptr_item=0, itemtype=-1):

        self.link = link  # it is recommended to keep the link as a reference and not a duplicate (otherwise it will establish a new connection at every call)
        self.type = itemtype
        if type(ptr_item) is str:
            self.item = int(ptr_item)
            if self.type == -1:
                self.type = self.Type()  # request type
        else:
            self.item = ptr_item

    def __repr__(self):
        if self.Valid():
            return ("RoboDK item (%i) of type %i" % (self.item, int(self.type)))
        else:
            return "RoboDK item (INVALID)"

    def __hash__(self):
        return int(self.item)

    def __eq__(self, other):
        if other is None:
            return False
        return self.item == other.item

    def __ne__(self, other):
        if other is None:
            return True
        return self.item != other.item

    def equals(self, item2):
        """Returns True if an item is the same as this item :class:`.Item`

        :param item2: item to compare
        :type item2: :class:`.Item`
        """
        return self.item == item2.item

    def RDK(self):
        """Returns the RoboDK link Robolink(). It is important to have different links (Robolink) for multithreaded applications.

        .. seealso:: :func:`~robodk.robolink.Robolink.Finish`
        """
        return self.link

    #"""Generic item calls"""
    def Type(self):
        """Return the type of the item (robot, object, tool, frame, ...).
        Tip: Compare the returned value against ITEM_TYPE_* variables

        .. seealso:: :func:`~robodk.robolink.Robolink.Item`
        """
        with self.link._lock:
            self.link._check_connection()
            command = 'G_Item_Type'
            self.link._send_line(command)
            self.link._send_item(self)
            itemtype = self.link._rec_int()
            self.link._check_status()
            return itemtype

    def Copy(self, copy_children=True):
        """Copy the item to the clipboard (same as Ctrl+C). Use together with Paste() to duplicate items.

        :param bool copy_children: Set to false to prevent copying all items attached to this item.

        .. seealso:: :func:`~robodk.robolink.Robolink.Copy`, :func:`~robodk.robolink.Item.Paste`
        """
        self.link.Copy(self.item, copy_children)

    def Paste(self):
        """Paste the copied :class:`.Item` from the clipboard as a child of this item (same as Ctrl+V)
        Returns the new item created (pasted)

        .. seealso:: :func:`~robodk.robolink.Robolink.Copy`, :func:`~robodk.robolink.Item.Copy`, :func:`~robodk.robolink.Item.Paste`
        """
        return self.link.Paste(self.item)

    def AddFile(self, filename):
        """Adds an object attached to this object

        :param str filename: file path

        .. seealso:: :func:`~robodk.robolink.Robolink.AddFile`, :func:`~robodk.robolink.Item.Save`
        """
        return self.link.AddFile(filename, self.item)

    def Save(self, filename):
        """Save a station or object to a file

        :param str filename: file to save. Use \\*.rdk name for RoboDK stations, \\*.stl file for objects, \\*.robot file for robots, etc.

        .. seealso:: :func:`~robodk.robolink.Robolink.AddFile`, :func:`~robodk.robolink.Item.AddFile`
        """
        self.link.Save(filename, self.item)

    def Collision(self, item_check):
        """Returns True if this item is in a collision state with another :class:`.Item`, otherwise it returns False.

        :param item_check: item to check for collisions
        :type item_check: :class:`.Item`

        .. seealso:: :func:`~robodk.robolink.Robolink.Collision`
        """
        return self.link.Collision(self.item, item_check)

    def IsInside(self, object):
        """Return True if the object is inside the provided object

        :param object: object to check
        :type object: :class:`.Item`

        .. seealso:: :func:`~robodk.robolink.Robolink.IsInside`
        """
        return self.link.IsInside(self.item, object)

    def AddGeometry(self, fromitem, pose):
        """Makes a copy of the geometry fromitem adding it at a given position (pose), relative to this item."""
        with self.link._lock:
            self.link._check_connection()
            command = 'CopyFaces'
            self.link._send_line(command)
            self.link._send_item(fromitem)
            self.link._send_item(self)
            self.link._send_pose(pose)
            self.link._check_status()

    def Delete(self):
        """Remove this item and all its children from the station.

        .. seealso:: :func:`~robodk.robolink.Robolink.AddFile`, :func:`~robodk.robolink.Robolink.Item`
        """
        with self.link._lock:
            if self.item == 0:
                raise InputError("Item is not valid or was already deleted")

            self.link._check_connection()
            command = 'Remove'
            self.link._send_line(command)
            self.link._send_item(self)
            self.item = 0
            if self.link._SkipStatus:
                self.link.COM.flush()
                return

            self.link._check_status()

    def Valid(self, check_deleted=False):
        """Checks if the item is valid.
        Returns True if the item is valid or False if the item is not valid.
        An invalid item will be returned by an unsuccessful function call (wrong name or because an item was deleted)

        :param bool check_deleted: Check if the item was deleted in RoboDK.

        .. seealso:: :func:`~robodk.robolink.Robolink.Item`

        Example:

        .. code-block:: python

            from robodk.robolink import *           # import the robolink library
            RDK = Robolink()                        # connect to the RoboDK API (RoboDK starts if it has not started
            tool  = RDK.Item('Tool')                # Retrieve an item named tool
            if not tool.Valid():
                print("The tool item does not exist!")
                quit()
        """
        if self.item == 0:
            return False
        if check_deleted:
            return self.Type() >= 0
        return True

    def setParent(self, parent):
        """Attaches the item to a new parent while maintaining the relative position with its parent.
        The absolute position is changed.

        :param parent: parent to attach the item
        :type parent: :class:`.Item`

        .. seealso:: :func:`~robodk.robolink.Item.setParentStatic`
        """
        with self.link._lock:
            self.link._check_connection()
            command = 'S_Parent'
            self.link._send_line(command)
            self.link._send_item(self)
            self.link._send_item(parent)
            if self.link._SkipStatus:
                self.link.COM.flush()
                return self

            self.link._check_status()
            return self

    def setParentStatic(self, parent):
        """Attaches the item to another parent while maintaining the current absolute position in the station.
        The relationship between this item and its parent is changed to maintain the abosolute position.

        :param parent: parent to attach the item
        :type parent: :class:`.Item`

        .. seealso:: :func:`~robodk.robolink.Item.setParent`
        """
        with self.link._lock:
            self.link._check_connection()
            command = 'S_Parent_Static'
            self.link._send_line(command)
            self.link._send_item(self)
            self.link._send_item(parent)
            if self.link._SkipStatus:
                self.link.COM.flush()
                return self

            self.link._check_status()
            return self

    def AttachClosest(self, keyword='', tolerance_mm=-1, list_objects=[]):
        """Attach the closest object to the tool.
        Returns the item that was attached. Use item.Valid() to check if an object was attached to the tool.

        :param str keyword: Keyword needed for an object to be grabbable (leave empty to consider all objects)
        :param float tolerance_mm: Distance tolerance to use (at most) to consider grabbing objects. The closest object will be attached. In Tools-Options-General tab you can choose to check object distance between TCP and object shape (instead of the default TCP vs. Object position).
        :param list list_objects: List of candidate objects to consider to grab (providing a keyword constrains the choices even more)

        .. seealso:: :func:`~robodk.robolink.Item.setParentStatic`
        """
        with self.link._lock:
            self.link._check_connection()
            command = 'Attach_Closest2'
            self.link._send_line(command)
            self.link._send_item(self)
            self.link._send_line(keyword)
            self.link._send_array([tolerance_mm])
            self.link._send_int(len(list_objects))
            for obji in list_objects:
                self.link._send_item(obji)

            item_attached = self.link._rec_item()
            self.link._check_status()
            return item_attached

    def DetachClosest(self, parent=0):
        """Detach the closest object attached to the tool (see also: setParentStatic).

        :param parent: New parent item to attach, such as a reference frame (optional). If not provided, the items held by the tool will be placed at the station root.
        :type parent: :class:`.Item`

        .. seealso:: :func:`~robodk.robolink.Item.setParentStatic`
        """
        with self.link._lock:
            self.link._check_connection()
            command = 'Detach_Closest'
            self.link._send_line(command)
            self.link._send_item(self)
            self.link._send_item(parent)
            item_detached = self.link._rec_item()
            self.link._check_status()
            return item_detached

    def DetachAll(self, parent=0):
        """Detaches any object attached to a tool.

        :param parent: New parent item to attach, such as a reference frame (optional). If not provided, the items held by the tool will be placed at the station root.
        :type parent: :class:`.Item`

        .. seealso:: :func:`~robodk.robolink.Item.setParentStatic`
        """
        with self.link._lock:
            self.link._check_connection()
            command = 'Detach_All'
            self.link._send_line(command)
            self.link._send_item(self)
            self.link._send_item(parent)
            self.link._check_status()

    def Parent(self):
        """Return the parent item of this item (:class:`.Item`)

        .. seealso:: :func:`~robodk.robolink.Item.Childs`
        """
        with self.link._lock:
            self.link._check_connection()
            command = 'G_Parent'
            self.link._send_line(command)
            self.link._send_item(self)
            parent = self.link._rec_item()
            self.link._check_status()
            return parent

    def Childs(self):
        """Return a list of the childs items (list of :class:`.Item`) that are attached to this item.
        Exceptionally, if Childs is called on a program it will return the list of subprograms called by this program.

        .. seealso:: :func:`~robodk.robolink.Item.Parent`
        """
        with self.link._lock:
            self.link._check_connection()
            command = 'G_Childs'
            self.link._send_line(command)
            self.link._send_item(self)
            nitems = self.link._rec_int()
            itemlist = []
            for i in range(nitems):
                itemlist.append(self.link._rec_item())
            self.link._check_status()
            return itemlist

    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    def Visible(self):
        """Returns 1 if the item is visible, otherwise it returns 0.

        .. seealso:: :func:`~robodk.robolink.Item.setVisible`
        """
        with self.link._lock:
            self.link._check_connection()
            command = 'G_Visible'
            self.link._send_line(command)
            self.link._send_item(self)
            visible = self.link._rec_int()
            self.link._check_status()
            return visible

    def setVisible(self, visible, visible_frame=None):
        """Sets the item visiblity.

        :param bool visible: Set the object as visible (1/True) or invisible (0/False)
        :param bool visible_frame: Set the object reference frame as visible (1/True) or invisible (0/False). It is also possible to provide flags to control the visibility of each robot link (only for robot items). When the item is a robot, this variable can specify robot visibility using suitable flags (as shown in the example).

        Note: Use setVisible on a programs to set the \"Display path\" setting.

        Example:

        .. code-block:: python
            :caption: Change robot visibility

            # Retrieve the robot (first robot available)
            robot = RDK.Item('', ITEM_TYPE_ROBOT)

            # Show the robot with default settings:
            robot.setVisible(True, VISIBLE_ROBOT_DEFAULT)

            # Show the robot and hide all references:
            robot.setVisible(1, VISIBLE_ROBOT_DEFAULT and not VISIBLE_ROBOT_ALL_REFS)

            # Show only references (hide the robot):
            robot.setVisible(1, VISIBLE_ROBOT_ALL_REFS)

        .. code-block:: python
            :caption: Available Frame flags

            # Default values for objects
            VISIBLE_REFERENCE_DEFAULT = -1
            VISIBLE_REFERENCE_ON = 1     # For objects and reference frames only
            VISIBLE_REFERENCE_OFF = 0    # For objects and reference frames only

            # Available flags to set robot visiblity
            VISIBLE_ROBOT_NONE = 0
            VISIBLE_ROBOT_FLANGE = 0x01
            VISIBLE_ROBOT_AXIS_Base_3D = 0x01 << 1
            VISIBLE_ROBOT_AXIS_Base_REF = 0x01 << 2
            VISIBLE_ROBOT_AXIS_1_3D = 0x01 << 3
            VISIBLE_ROBOT_AXIS_1_REF = 0x01 << 4
            VISIBLE_ROBOT_AXIS_2_3D = 0x01 << 5
            VISIBLE_ROBOT_AXIS_2_REF = 0x01 << 6
            VISIBLE_ROBOT_AXIS_3_3D = 0x01 << 7
            VISIBLE_ROBOT_AXIS_3_REF = 0x01 << 8
            VISIBLE_ROBOT_AXIS_4_3D = 0x01 << 9
            VISIBLE_ROBOT_AXIS_4_REF = 0x01 << 10
            VISIBLE_ROBOT_AXIS_5_3D = 0x01 << 11
            VISIBLE_ROBOT_AXIS_5_REF = 0x01 << 12
            VISIBLE_ROBOT_AXIS_6_3D = 0x01 << 13
            VISIBLE_ROBOT_AXIS_6_REF = 0x01 << 14
            VISIBLE_ROBOT_AXIS_7_3D = 0x01 << 15
            VISIBLE_ROBOT_AXIS_7_REF = 0x02 << 16
            VISIBLE_ROBOT_DEFAULT = 0x2AAAAAAB
            VISIBLE_ROBOT_ALL = 0x7FFFFFFF
            VISIBLE_ROBOT_ALL_REFS = 0x15555555

        .. seealso:: :func:`~robodk.robolink.Item.Visible`

        """
        if visible_frame is None:
            visible_frame = -1
        elif visible_frame is False:
            visible_frame = -2
        elif visible_frame is True:
            visible_frame = -3

        with self.link._lock:
            self.link._check_connection()
            command = 'S_Visible'
            self.link._send_line(command)
            self.link._send_item(self)
            self.link._send_int(visible)
            self.link._send_int(visible_frame)
            if self.link._SkipStatus:
                self.link.COM.flush()
                return self

            self.link._check_status()
            return self

    def Name(self):
        """Returns the item name. The name of the item is always displayed in the RoboDK station tree.
        Returns the name as a string (str)

        :return: New item name
        :rtype: str

        .. seealso:: :func:`~robodk.robolink.Item.setName`
        """
        with self.link._lock:
            self.link._check_connection()
            command = 'G_Name'
            self.link._send_line(command)
            self.link._send_item(self)
            name = self.link._rec_line()
            self.link._check_status()
            return name

    def setName(self, name):
        """Set the name of the item. The name of the item will be displayed in the station tree.

        :param str name: New item name

        .. seealso:: :func:`~robodk.robolink.Item.Name`
        """
        with self.link._lock:
            self.link._check_connection()
            command = 'S_Name'
            self.link._send_line(command)
            self.link._send_item(self)
            self.link._send_line(name)
            if self.link._SkipStatus:
                self.link.COM.flush()
                return self

            self.link._check_status()
            return self

    def setValue(self, varname, value=None):
        """Set a specific property name to a given value. This is reserved for internal purposes and future compatibility.

        :param str varname: property name
        :param str value: property value

        .. seealso:: :func:`~robodk.robolink.Robolink.Command`, :func:`~robodk.robolink.Item.setParam`

        """
        with self.link._lock:
            self.link._check_connection()
            if value is None:
                value = robomath.Mat(0, 0)

            if isinstance(value, robomath.Mat):
                self.link._require_build(22340)
                command = 'S_ValueMat'
                self.link._send_line(command)
                self.link._send_item(self)
                self.link._send_line(varname)
                self.link._send_matrix(value)
                mat2d = self.link._rec_matrix()
                self.link._check_status()
                return mat2d

            # elif isinstance(value, robomath.Mat):
            #     command = 'S_Gen_Mat'
            #     self.link._send_line(command)
            #     self.link._send_item(self)
            #     self.link._send_line(varname)
            #     self.link._send_matrix(value)

            elif isinstance(value, str):
                command = 'S_Gen_Str'
                self.link._send_line(command)
                self.link._send_item(self)
                self.link._send_line(varname)
                self.link._send_line(value)
            else:
                raise Exception("Unsupported value type")
            self.link._check_status()

    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    def setPose(self, pose):
        """Set the position (pose) of the item with respect to its parent (item it is attached to), for example, the position of an object, frame or target with respect to its parent reference frame.

        For robot items, setPose will move the robot joints to reach the pose target using the active tool with respect to the active reference. setPose has no effect on tool items, however, it will modify the pose of the related object with respect to its parent (this is only visible when the tool is converted to an object).

        :param pose: pose of the item with respect to its parent
        :type pose: :class:`~robodk.robomath.Mat`

        .. seealso:: :func:`~robodk.robolink.Item.Pose`, :func:`~robodk.robolink.Item.PoseAbs`, :func:`~robodk.robolink.Item.setPoseAbs`, :func:`~robodk.robolink.Item.setPoseTool`, :func:`~robodk.robolink.Item.setPoseFrame`, :func:`~robodk.robolink.Robolink.Item`
        """
        with self.link._lock:
            self.link._check_connection()
            command = 'S_Hlocal'
            self.link._send_line(command)
            self.link._send_item(self)
            self.link._send_pose(pose)
            if self.link._SkipStatus:
                self.link.COM.flush()
                return self

            self.link._check_status()
            return self

    def Pose(self):
        """Returns the relative pose of an object, target or reference frame. For example, the position of an object, target or reference frame with respect to its parent (the item it is attached to in the tree).
        For robot items, this function returns the pose of the active tool with respect to the active reference frame.

        It returns the pose as :class:`~robodk.robomath.Mat`.

        Tip: Use a Pose_2_* function from the robodk module (such as :class:`robomath.Pose_2_KUKA`) to convert the pose to XYZABC (XYZ position in mm and ABC orientation in degrees), specific to a robot brand.

        Example: :ref:`weldexample`

        .. seealso:: :func:`~robodk.robolink.Item.Pose`, :func:`~robodk.robolink.Item.setPose`, :func:`~robodk.robolink.Item.PoseAbs`, :func:`~robodk.robolink.Item.PoseTool`, :func:`~robodk.robolink.Item.PoseFrame`, :func:`~robodk.robolink.Robolink.Item`
        """
        with self.link._lock:
            self.link._check_connection()
            command = 'G_Hlocal'
            self.link._send_line(command)
            self.link._send_item(self)
            pose = self.link._rec_pose()
            self.link._check_status()
            return pose

    def PoseWrt(self, item):
        """Returns the relative pose of this Item with respect to an another Item.

        :param item: The other Item
        :type item: :class:`.Item`

        :return: The pose from the source Item to the second Item
        :rtype: :class:`~robodk.robomath.Mat`

        .. seealso:: :func:`~robodk.robolink.Item.Pose`, :func:`~robodk.robolink.Item.PoseAbs`
        """
        from robodk import robolinkutils
        return robolinkutils.getPoseWrt(self, item)

    def setGeometryPose(self, pose, apply=False):
        """Set the position (pose) the object geometry with respect to its own reference frame. This can be applied to tools and objects.
        The pose must be a :class:`~robodk.robomath.Mat`"""
        with self.link._lock:
            self.link._check_connection()
            command = 'S_Hgeo2'
            self.link._send_line(command)
            self.link._send_item(self)
            self.link._send_pose(pose)
            self.link._send_int(1 if apply else 0)
            self.link._check_status()

    def GeometryPose(self):
        """Returns the position (pose as :class:`~robodk.robomath.Mat`) the object geometry with respect to its own reference frame. This procedure works for tools and objects.
        """
        self.link._check_connection()
        command = 'G_Hgeom'
        self.link._send_line(command)
        self.link._send_item(self)
        pose = self.link._rec_pose()
        self.link._check_status()
        return pose

    def setPoseAbs(self, pose):
        """Set the pose (:class:`~robodk.robomath.Mat`) of this item with respect to the absolute reference frame (also know as the station reference or world coordinate system -WCS-). For example, the position of an object/frame/target with respect to the origin of the station. If the item is a tool, the joints of the associated robot will be updated to match the absolute pose with the tool (the TCP is not changed). setPoseAbs has no effect on robots.

        :param pose: pose of the item with respect to the station reference
        :type pose: :class:`~robodk.robomath.Mat`

        .. seealso:: :func:`~robodk.robolink.Item.PoseAbs`, :func:`~robodk.robolink.Item.setPose`, :func:`~robodk.robolink.Item.Pose`
        """
        with self.link._lock:
            self.link._check_connection()
            command = 'S_Hlocal_Abs'
            self.link._send_line(command)
            self.link._send_item(self)
            self.link._send_pose(pose)
            if self.link._SkipStatus:
                self.link.COM.flush()
                return self

            self.link._check_status()
            return self

    def PoseAbs(self):
        """Return the pose (:class:`~robodk.robomath.Mat`) of this item with respect to the absolute reference frame (also know as the station reference or world coordinate system -WCS-).
        For example, the position of an object/frame/target with respect to the origin of the station.

        For robot items, this returns the pose of the robot base with respect to the origin of the station.

        Example:

        .. code-block:: python

            # Calculate the pose of any object with respect to any reference in RoboDK
            def CalculatePoseFrame2Object(frame, part):
                # Get both poses with respect to the station reference (wrt-world coordinate system)
                framePoseAbs = frame.PoseAbs()
                partPoseAbs = part.PoseAbs()

                # Calculate the pose of the object relative to the reference
                pose = framePoseAbs.inv() * partPoseAbs
                return pose

            # Take the object
            obj = RDK.Item('Sphere')

            # Retrieve the reference
            frame = RDK.Item('Frame 2')

            # Calculate the relationship
            pose =  CalculatePoseFrame2Object(frame,obj)

            # Display the result
            print(pose)
            RDK.ShowMessage("The relative pose is: " + str(pose))

        .. seealso:: :func:`~robodk.robolink.Item.setPoseAbs`, :func:`~robodk.robolink.Item.Pose`, :func:`~robodk.robolink.Item.setPose`
        """
        with self.link._lock:
            self.link._check_connection()
            command = 'G_Hlocal_Abs'
            self.link._send_line(command)
            self.link._send_item(self)
            pose = self.link._rec_pose()
            self.link._check_status()
            return pose

    def Recolor(self, tocolor, fromcolor=None, tolerance=None):
        """Changes the color of an :class:`.Item` (object, tool or robot).
        Colors must in the format COLOR=[R,G,B,(A=1)] where all values range from 0 to 1.
        Alpha (A) defaults to 1 (100% opaque). Set A to 0 to make an object transparent.

        :param tocolor: color to set
        :type tocolor: list of float
        :param fromcolor: color to change
        :type fromcolor: list of float
        :param tolerance: tolerance to replace colors (set to 0 for exact match)
        :type tolerance: float (defaults to 0.1)

        .. seealso:: :func:`~robodk.robolink.Item.setColor`
        """
        with self.link._lock:
            self.link._check_connection()
            if not fromcolor:
                fromcolor = [0, 0, 0, 0]
                tolerance = 2
            elif not tolerance:
                tolerance = 0.1
            if not (isinstance(tolerance, int) or isinstance(tolerance, float)):
                raise Exception("tolerance must be a scalar")

            tocolor = self.link._check_color(tocolor)
            fromcolor = self.link._check_color(fromcolor)
            command = 'Recolor'
            self.link._send_line(command)
            self.link._send_item(self)
            self.link._send_array([tolerance] + fromcolor + tocolor)
            self.link._check_status()

    def setColor(self, tocolor):
        """Set the color of an object, tool or robot.
        A color must in the format COLOR=[R,G,B,(A=1)] where all values range from 0 to 1.

        :param tocolor: color to set
        :type tocolor: list of float

        .. seealso:: :func:`~robodk.robolink.Item.Color`, :func:`~robodk.robolink.Item.Recolor`
        """
        with self.link._lock:
            self.link._check_connection()
            tocolor = self.link._check_color(tocolor)
            command = 'S_Color'
            self.link._send_line(command)
            self.link._send_item(self)
            self.link._send_array(tocolor)
            self.link._check_status()

    def setColorShape(self, tocolor, shape_id):
        """Set the color of an object shape. It can also be used for tools.
        A color must in the format COLOR=[R,G,B,(A=1)] where all values range from 0 to 1.

        :param tocolor: color to set
        :type tocolor: list of float
        :param int shape_id: ID of the shape: the ID is the order in which the shape was added using AddShape()

        .. seealso:: :func:`~robodk.robolink.Item.Color`, :func:`~robodk.robolink.Item.Recolor`
        """
        with self.link._lock:
            self.link._check_connection()
            tocolor = self.link._check_color(tocolor)
            command = 'S_ShapeColor'
            self.link._send_line(command)
            self.link._send_item(self)
            self.link._send_int(shape_id)
            self.link._send_array(tocolor)
            self.link._check_status()

    def setColorCurve(self, tocolor, curve_id=-1):
        """Set the color of a curve object. It can also be used for tools.
        A color must in the format COLOR=[R,G,B,(A=1)] where all values range from 0 to 1.

        :param tocolor: color to set
        :type tocolor: list of float
        :param int curve_id: ID of the curve: the ID is the order in which the shape was added using AddCurve()

        .. seealso:: :func:`~robodk.robolink.Item.Color`, :func:`~robodk.robolink.Item.Recolor`
        """
        with self.link._lock:
            self.link._check_connection()
            tocolor = self.link._check_color(tocolor)
            command = 'S_CurveColor'
            self.link._send_line(command)
            self.link._send_item(self)
            self.link._send_int(curve_id)
            self.link._send_array(tocolor)
            self.link._check_status()

    def Color(self):
        """Return the color of an :class:`.Item` (object, tool or robot). If the item has multiple colors it returns the first color available).
        A color is in the format COLOR=[R,G,B,(A=1)] where all values range from 0 to 1.

        .. seealso:: :func:`~robodk.robolink.Item.setColor`, :func:`~robodk.robolink.Item.Recolor`
        """
        with self.link._lock:
            self.link._check_connection()
            command = 'G_Color'
            self.link._send_line(command)
            self.link._send_item(self)
            color = self.link._rec_array()
            self.link._check_status()
            return color.tolist()

    def Scale(self, scale, pre_mult=None, post_mult=None):
        """Apply a scale to an object to make it bigger or smaller.
        The scale can be uniform (if scale is a float value) or per axis (if scale is an array/list [scale_x, scale_y, scale_z]).

        :param scale: scale parameter (1 means no change)
        :type scale: float or list of 3 float [scale_x, scale_y, scale_z]
        :param pre_mult: pre multiplication to apply before the scaling(optional)
        :param post_mult: post multiplication to apply after the scaling (optional)"""
        with self.link._lock:
            if pre_mult is not None or post_mult is not None:
                if pre_mult is None:
                    pre_mult = robomath.eye(4)
                if post_mult is None:
                    post_mult = robomath.invH(pre_mult)

                self.link._check_connection()
                if isinstance(scale, float) or isinstance(scale, int):
                    scale = [scale, scale, scale]
                elif len(scale) > 3:
                    scale = scale[:3]
                elif len(scale) < 3:
                    raise Exception("scale must be a single value or a 3-vector value")

                command = 'TrScale'
                self.link._send_line(command)
                self.link._send_item(self)
                self.link._send_array(scale)
                self.link._send_pose(pre_mult)
                self.link._send_pose(post_mult)
                status = self.link._rec_int()
                self.link._check_status()
                return status > 0

            else:
                self.link._check_connection()
                if isinstance(scale, float) or isinstance(scale, int):
                    scale = [scale, scale, scale]
                elif len(scale) > 3:
                    scale = scale[:3]
                elif len(scale) < 3:
                    raise Exception("scale must be a single value or a 3-vector value")
                command = 'Scale'
                self.link._send_line(command)
                self.link._send_item(self)
                self.link._send_array(scale)
                self.link._check_status()
                return None

    #"""Object specific calls"""
    def AddShape(self, triangle_points):
        """Adds a shape to the object provided some triangle coordinates. Triangles must be provided as a list of vertices. A vertex normal can be optionally provided.

        .. seealso:: :func:`~robodk.robolink.Robolink.AddShape`
        """
        return self.link.AddShape(triangle_points, self)

    def AddCurve(self, curve_points, add_to_ref=False, projection_type=PROJECTION_ALONG_NORMAL_RECALC):
        """Adds a curve provided point coordinates. The provided points must be a list of vertices. A vertex normal can be provided optionally.

        .. seealso:: :func:`~robodk.robolink.Robolink.AddCurve`
        """
        return self.link.AddCurve(curve_points, self, add_to_ref, projection_type)

    def AddPoints(self, points, add_to_ref=False, projection_type=PROJECTION_ALONG_NORMAL_RECALC):
        """Adds a list of points to an object. The provided points must be a list of vertices. A vertex normal can be provided optionally.

        .. seealso:: :func:`~robodk.robolink.Robolink.AddPoints`
        """
        return self.link.AddPoints(points, self, add_to_ref, projection_type)

    def ProjectPoints(self, points, projection_type=PROJECTION_ALONG_NORMAL_RECALC):
        """Projects a point or a list of points to the object given its coordinates. The provided points must be a list of [XYZ] coordinates. Optionally, a vertex normal can be provided [XYZijk].

        .. seealso:: :func:`~robodk.robolink.Robolink.ProjectPoints`
        """
        return self.link.ProjectPoints(points, self, projection_type)

    def SelectedFeature(self):
        """Retrieve the currently selected feature for this object.

        .. seealso:: :func:`~robodk.robolink.Robolink.GetPoints`

        Example:

        .. code-block:: python

            # Show the point selected
            object = RDK.Item('Object', ITEM_TYPE_OBJECT)
            is_selected, feature_type, feature_id = OBJECT.SelectedFeature()

            points, name_selected = object.GetPoints(feature_type, feature_id)
            point = None
            if len(points) > 1:
                point = points[feature_id]
            else:
                point = points[0]

            RDK.ShowMessage("Selected Point: %s = [%.3f, %.3f, %.3f]" % (name_selected, point[0], point[1], point[2]))

        """
        with self.link._lock:
            self.link._check_connection()
            command = 'G_ObjSelection'
            self.link._send_line(command)
            self.link._send_item(self)
            is_selected = self.link._rec_int()
            feature_type = self.link._rec_int()
            feature_id = self.link._rec_int()
            self.link._check_status()
            return is_selected, feature_type, feature_id

    def GetPoints(self, feature_type=FEATURE_SURFACE, feature_id=0):
        """Retrieves the point under the mouse cursor, a curve or the 3D points of an object. The points are provided in [XYZijk] format in relative coordinates. The XYZ are the local point coordinate and ijk is the normal of the surface.

        :param int feature_type: set to FEATURE_SURFACE to retrieve the point under the mouse cursor, FEATURE_CURVE to retrieve the list of points for that wire, or FEATURE_POINT to retrieve the list of points.
        :param int feature_id:  used only if FEATURE_CURVE is specified, it allows retrieving the appropriate curve id of an object

        :return: List of points


        Example 1 - Display the XYZ position of a selected object

        .. code-block:: python

            from robodk.robolink import *    # Import the RoboDK API
            RDK = Robolink()          # Start RoboDK API

            # Ask the user to select an object
            OBJECT = RDK.ItemUserPick("Select an object", ITEM_TYPE_OBJECT)

            while True:
                is_selected, feature_type, feature_id = OBJECT.SelectedFeature()

                if is_selected and feature_type == FEATURE_SURFACE:
                    point_mouse, name_feature = OBJECT.GetPoints(FEATURE_SURFACE)
                    print("Selected %i (%i): %s  %s" % (feature_id, feature_type, str(point_mouse), name_feature))

                else:
                    print("Object Not Selected. Select a point in the object surface...")

                robomath.pause(0.1)


        Example 2 - Display the mesh of a selected object surface

        .. code-block:: python

            from robolink import *    # Import the RoboDK API
            import time
            RDK = Robolink()          # Start RoboDK API

            while True:
                # Check if we have an object under the mouse cursor
                object, feature_type, feature_id, feature_name, points = RDK.GetPoints(FEATURE_HOVER_OBJECT)
                if object.Valid() and (object.type == ITEM_TYPE_OBJECT or object.type == ITEM_TYPE_TOOL):

                    # Retrieve the selected feature on the object
                    is_selected, feature_type, feature_id = object.SelectedFeature()

                    if is_selected and feature_type == FEATURE_SURFACE:
                        # Retrieve the mesh related to the surface ID
                        point_mesh, name_feature = object.GetPoints(FEATURE_OBJECT_MESH, feature_id)
                        print("Selected %i (%i):  %s" % (feature_id, feature_type, name_feature))
                        print("Mesh points:")
                        for xyzijk in point_mesh:
                            print(xyzijk)

                        # Clear selection or manipulate as necessary
                        RDK.setSelection([])

                    else:
                        print("Click the surface to see the mesh")
                        time.sleep(0.1)
                        continue

                else:
                    print("Object Not Selected. The surface of an object or a tool")

                time.sleep(0.1)


        .. seealso:: :func:`~robodk.robolink.Item.SelectedFeature`
        """
        if feature_type >= FEATURE_HOVER_OBJECT_MESH:
            raise Exception("Invalid feature type. Use FEATURE_SURFACE, FEATURE_MESH or equivalent.")

        with self.link._lock:
            self.link._check_connection()
            command = 'G_ObjPoint'
            self.link._send_line(command)
            self.link._send_item(self)
            self.link._send_int(feature_type)
            self.link._send_int(feature_id)
            points = self.link._rec_matrix()
            feature_name = self.link._rec_line()
            self.link._check_status()
            return list(points), feature_name

    def setMillingParameters(self, ncfile='', part=0, params=''):
        """
        .. deprecated:: 4.0
            Obsolete. Use :func:`~robodk.robolink.Item.setMachiningParameters` instead.
        """
        newprog, status = self.setMachiningParameters(ncfile, part, params)
        return newprog, status

    def setMachiningParameters(self, ncfile='', part=0, params=''):
        """Update the robot milling path input and parameters. Parameter input can be an NC file (G-code or APT file) or an object item in RoboDK. A curve or a point follow project will be automatically set up for a robot manufacturing project.
        Tip: Use getLink(), setPoseTool(), setPoseFrame() to get/set the robot tool, reference frame, robot and program linked to the project.
        Tip: Use setPose() and setJoints() to update the path to tool orientation or the preferred start joints.

        :param str ncfile: path to the NC file (G-code or APT) to be loaded (optional)
        :param part: object holding curves or points to automatically set up a curve/point follow project (optional)
        :type part: :class:`.Item`
        :param params: Additional options

        .. seealso:: :func:`~robodk.robolink.Robolink.AddMachiningProject`, :func:`~robodk.robolink.Item.Joints`, :func:`~robodk.robolink.Item.getLink`, :func:`~robodk.robolink.Item.setJoints`, :func:`~robodk.robolink.Item.setPoseTool`, :func:`~robodk.robolink.Item.setPoseFrame`

        Example:

        .. code-block:: python

            object_curve = RDK.AddCurve(POINTS)
            object_curve.setName('AutoPoints n%i' % NUM_POINTS)
            path_settings = RDK.AddMillingProject("AutoCurveFollow settings")
            prog, status = path_settings.setMillingParameters(part=object_curve)

        """
        with self.link._lock:
            self.link._check_connection()
            command = 'S_MachiningParams'
            self.link._send_line(command)
            self.link._send_item(self)
            self.link._send_line(ncfile)
            self.link._send_item(part)
            self.link._send_line(params)
            self.link.COM.settimeout(3600)
            newprog = self.link._rec_item()
            self.link.COM.settimeout(self.link.TIMEOUT)
            status = self.link._rec_int() / 1000.0
            self.link._check_status()
            return newprog, status

    #"""Target item calls"""
    def setAsCartesianTarget(self):
        """Sets a target as a cartesian target. A cartesian target moves to cartesian coordinates.

        .. seealso:: :func:`~robodk.robolink.Robolink.AddTarget`, :func:`~robodk.robolink.Item.setPose`, :func:`~robodk.robolink.Item.setAsJointTarget`
        """
        with self.link._lock:
            self.link._check_connection()
            command = 'S_Target_As_RT'
            self.link._send_line(command)
            self.link._send_item(self)
            if self.link._SkipStatus:
                self.link.COM.flush()
                return self

            self.link._check_status()
            return self

    def setAsJointTarget(self):
        """Sets a target as a joint target. A joint target moves to the joint position without taking into account the cartesian coordinates.

        .. seealso:: :func:`~robodk.robolink.Robolink.AddTarget`, :func:`~robodk.robolink.Item.setPose`, :func:`~robodk.robolink.Item.setAsCartesianTarget`
        """
        with self.link._lock:
            self.link._check_connection()
            command = 'S_Target_As_JT'
            self.link._send_line(command)
            self.link._send_item(self)
            if self.link._SkipStatus:
                self.link.COM.flush()
                return self

            self.link._check_status()
            return self

    def isJointTarget(self):
        """Returns True if a target is a joint target. A joint target moves to the joint position without taking into account the cartesian coordinates.

        .. seealso:: :func:`~robodk.robolink.Robolink.AddTarget`, :func:`~robodk.robolink.Item.setPose`, :func:`~robodk.robolink.Item.setAsCartesianTarget`, :func:`~robodk.robolink.Item.setAsJointTarget`
        """
        with self.link._lock:
            self.link._check_connection()
            command = 'Target_Is_JT'
            self.link._send_line(command)
            self.link._send_item(self)
            isjt = self.link._rec_int()
            self.link._check_status()
            return isjt > 0

    #"""Robot item calls"""
    def Joints(self):
        """Return the current joint position as a :class:`~robodk.robomath.Mat` of a robot or the joints of a target.
        If the item is a cartesian target, it returns the preferred joints (configuration) to go to that cartesian position.

        .. seealso:: :func:`~robodk.robolink.Item.setJoints`, :func:`~robodk.robolink.Item.MoveJ`

        Example:

        .. code-block:: python

            from robodk.robolink import *           # import the robolink library
            RDK = Robolink()                        # connect to the RoboDK API (RoboDK starts if it has not started)
            tool  = RDK.Item('', ITEM_TYPE_ROBOT)   # Retrieve the robot
            joints = robot.Joints().list()          # retrieve the current robot joints as a list
            joints[5] = 0                           # set joint 6 to 0 deg
            robot.MoveJ(joints)                     # move the robot to the new joint position

        """
        with self.link._lock:
            self.link._check_connection()
            command = 'G_Thetas'
            self.link._send_line(command)
            self.link._send_item(self)
            joints = self.link._rec_array()
            self.link._check_status()
            return joints

    def SimulatorJoints(self):
        """Return the current joint position of a robot (only from the simulator, never from the real robot).
        This should be used only when RoboDK is connected to the real robot and only the simulated robot needs to be retrieved (for example, if we want to move the robot using a spacemouse).

        Note: Use robot.Joints() instead to retrieve the simulated and real robot position when connected.

        .. seealso:: :func:`~robodk.robolink.Item.Joints`
        """
        with self.link._lock:
            self.link._check_connection()
            command = 'G_Thetas_Sim'
            self.link._send_line(command)
            self.link._send_item(self)
            joints = self.link._rec_array()
            self.link._check_status()
            return joints.list()

    def JointPoses(self, joints=None):
        """Returns the positions of the joint links for a provided robot configuration (joints). If no joints are provided it will return the poses for the current robot position.
        Out 1 : 4x4 x n -> array of 4x4 homogeneous matrices. Index 0 is the base frame reference (it never moves when the joints move).
        """
        with self.link._lock:
            self.link._check_connection()
            command = 'G_LinkPoses'
            self.link._send_line(command)
            self.link._send_item(self)
            if joints is None:
                self.link._send_array([])
            else:
                self.link._send_array(joints)

            nlinks = self.link._rec_int()
            poses = []
            for i in range(nlinks):
                poses.append(self.link._rec_pose())

            self.link._check_status()
            return poses

    def JointsHome(self):
        """Return the home joints of a robot.
        The home joints can be manually set in the robot "Parameters" menu of the robot panel in RoboDK, then select "Set home position".

        .. seealso:: :func:`~robodk.robolink.Item.Joints`
        """
        with self.link._lock:
            self.link._check_connection()
            command = 'G_Home'
            self.link._send_line(command)
            self.link._send_item(self)
            joints = self.link._rec_array()
            self.link._check_status()
            return joints

    def setJointsHome(self, joints):
        """Set the home position of the robot in the joint space.

        :param joints: robot joints
        :type joints: list of float or :class:`~robodk.robomath.Mat`

        .. seealso:: :func:`~robodk.robolink.Item.setJoints`
        """
        with self.link._lock:
            self.link._check_connection()
            command = 'S_Home'
            self.link._send_line(command)
            self.link._send_array(joints)
            self.link._send_item(self)
            self.link._check_status()
            return self

    def ObjectLink(self, link_id=0):
        """Returns an item pointer (:class:`.Item`) to a robot link. This is useful to show/hide certain robot links or alter their geometry.

        :param int link_id: link index (0 for the robot base, 1 for the first link, ...)
        """
        with self.link._lock:
            self.link._check_connection()
            command = 'G_LinkObjId'
            self.link._send_line(command)
            self.link._send_item(self)
            self.link._send_int(link_id)
            item = self.link._rec_item()
            self.link._check_status()
            return item

    def getLink(self, type_linked=ITEM_TYPE_ROBOT):
        """
        Returns an item pointer (:class:`.Item`) to a robot, object, tool or program that is linked to this item.
        This is useful to retrieve the relationship between programs, robots, tools and other specific projects.
        This returns the first link found.

        :param int type_linked: type of the linked item to retrieve (ITEM_TYPE_*)
        :return: An item that is invalid if no link is found, else the item
        :rtype: :class:`.Item`

        Example:

        .. code-block:: python

            prog = machining_proj.getLink(ITEM_TYPE_PROGRAM)  # Get the generated program of a machining project
            robot = prog.getLink(ITEM_TYPE_ROBOT)  # Get the robot associated with the program
            frame = robot.getLink(ITEM_TYPE_FRAME)  # Get the active reference frame

        .. seealso:: :func:`~robodk.robolink.Item.setLink`, :func:`~robodk.robolink.Item.getLinks`
        """
        with self.link._lock:
            self.link._check_connection()
            command = 'G_LinkType'
            self.link._send_line(command)
            self.link._send_item(self)
            self.link._send_int(type_linked)
            item = self.link._rec_item()
            self.link._check_status()
            return item

    def getLinks(self, type_linked=ITEM_TYPE_ROBOT):
        """
        Get all the items of a specific type for which `~robodk.robolink.Item.getLink` returns this item.

        :param int type_linked: type of the items to check for a link (ITEM_TYPE_*). None means any type.
        :return: A list of items for which `~robodk.robolink.Item.getLink` return the specified item
        :rtype: list of :class:`.Item`

        .. seealso:: :func:`~robodk.robolink.Item.getLink`, :func:`~robodk.robolink.Item.setLink`
        """
        from robodk import robolinkutils
        return robolinkutils.getLinks(self, type_linked)

    def setLink(self, item):
        """
        Sets a link between this item and the specified item.
        This is useful to set the relationship between programs, robots, tools and other specific projects.

        :param item: item to link
        :type item: :class:`.Item`

        .. seealso:: :func:`~robodk.robolink.Item.getLink`, :func:`~robodk.robolink.Item.getLinks`, :func:`~robodk.robolink.Item.setRobot`
        """
        if item is None:
            item = Item(self.link)

        with self.link._lock:
            self.link._check_connection()
            command = 'S_Link_ptr'
            self.link._send_line(command)
            self.link._send_item(item)
            self.link._send_item(self)
            self.link._check_status()
            return self

    def setJoints(self, joints):
        """Set the current joints of a robot or a target. If robot joints are set, the robot position will be updated on the screen.

        :param joints: robot joints
        :type joints: list of float or :class:`~robodk.robomath.Mat`

        .. seealso:: :func:`~robodk.robolink.Item.Joints`
        """
        with self.link._lock:
            self.link._check_connection()
            command = 'S_Thetas'
            self.link._send_line(command)
            self.link._send_array(joints)
            self.link._send_item(self)
            if self.link._SkipStatus:
                self.link.COM.flush()
                return self

            self.link._check_status()
            return self

    def JointLimits(self):
        """Retrieve the joint limits of a robot. Returns (lower limits, upper limits, joint type).

        .. seealso:: :func:`~robodk.robolink.Item.setJointLimits`
        """
        with self.link._lock:
            self.link._check_connection()
            command = 'G_RobLimits'
            self.link._send_line(command)
            self.link._send_item(self)
            lim_inf = self.link._rec_array()
            lim_sup = self.link._rec_array()
            joints_type = self.link._rec_int() / 1000.0
            self.link._check_status()
            return lim_inf, lim_sup, joints_type

    def setJointLimits(self, lower_limit, upper_limit):
        """Update the robot joint limits

        :param lower_limit: lower joint limits
        :type lower_limit: list of float
        :param upper_limit: upper joint limits
        :type upper_limit: list of float

        .. seealso:: :func:`~robodk.robolink.Item.JointLimits`
        """
        with self.link._lock:
            self.link._check_connection()
            command = 'S_RobLimits'
            self.link._send_line(command)
            self.link._send_item(self)
            self.link._send_array(lower_limit)
            self.link._send_array(upper_limit)
            self.link._check_status()

    def setRobot(self, robot=None):
        """Assigns a specific robot to a program, target or robot machining project.

        :param robot: robot to link
        :type robot: :class:`.Item`
        """
        if self.link.BUILD > 22916:
            self.setLink(robot)
            return self

        else:
            # To be removed in 2024
            with self.link._lock:
                if robot is None:
                    robot = Item(self.link)

                self.link._check_connection()
                command = 'S_Robot'
                self.link._send_line(command)
                self.link._send_item(self)
                self.link._send_item(robot)
                self.link._check_status()
                return self

    def setPoseFrame(self, frame):
        """Sets the reference frame of a robot (user frame). The frame can be an item or a 4x4 Matrix

        :param frame: robot reference frame as an item, or a pose
        :type frame: :class:`~robodk.robomath.Mat` or :class:`.Item`

        .. seealso:: :func:`~robodk.robolink.Item.PoseFrame`, :func:`~robodk.robolink.Item.setPose`, :func:`~robodk.robolink.Item.setPoseTool`
        """
        with self.link._lock:
            self.link._check_connection()
            if isinstance(frame, Item):
                command = 'S_Link_ptr'
                self.link._send_line(command)
                self.link._send_item(frame)
            else:
                command = 'S_Frame'
                self.link._send_line(command)
                self.link._send_pose(frame)
            self.link._send_item(self)
            self.link._check_status()
            return self

    def setPoseTool(self, tool):
        """Set the robot tool pose (TCP) with respect to the robot flange. The tool pose can be an item or a 4x4 Matrix

        :param tool: robot tool as an item, or a pose
        :type tool: :class:`~robodk.robomath.Mat` or :class:`.Item`

        .. seealso:: :func:`~robodk.robolink.Item.PoseTool`, :func:`~robodk.robolink.Item.setPose`, :func:`~robodk.robolink.Item.setPoseFrame`"""
        with self.link._lock:
            self.link._check_connection()
            if isinstance(tool, Item):
                command = 'S_Tool_ptr'
                self.link._send_line(command)
                self.link._send_item(tool)
            else:
                command = 'S_Tool'
                self.link._send_line(command)
                self.link._send_pose(tool)
            self.link._send_item(self)
            self.link._check_status()
            return self

    def PoseTool(self):
        """Returns the pose (:class:`~robodk.robomath.Mat`) of the robot tool (TCP) with respect to the robot flange

        .. seealso:: :func:`~robodk.robolink.Item.setPoseTool`, :func:`~robodk.robolink.Item.Pose`, :func:`~robodk.robolink.Item.PoseFrame`
        """
        with self.link._lock:
            self.link._check_connection()
            command = 'G_Tool'
            self.link._send_line(command)
            self.link._send_item(self)
            pose = self.link._rec_pose()
            self.link._check_status()
            return pose

    def PoseFrame(self):
        """Returns the pose (:class:`~robodk.robomath.Mat`) of the robot reference frame with respect to the robot base

        .. seealso:: :func:`~robodk.robolink.Item.setPoseFrame`, :func:`~robodk.robolink.Item.Pose`, :func:`~robodk.robolink.Item.PoseTool`
        """
        with self.link._lock:
            self.link._check_connection()
            command = 'G_Frame'
            self.link._send_line(command)
            self.link._send_item(self)
            pose = self.link._rec_pose()
            self.link._check_status()
            return pose

    # Obsolete methods -----------------------
    def Htool(self):
        """
        .. deprecated:: 4.0
            Obsolete. Use :func:`~robodk.robolink.Item.PoseTool` instead.

        Returns the pose (:class:`~robodk.robomath.Mat`) of the robot tool (TCP) with respect to the robot flange
        """
        return self.PoseTool()

    def Tool(self):
        """
        .. deprecated:: 4.0
            Obsolete. Use :func:`~robodk.robolink.Item.PoseTool` instead.

        Returns the pose (:class:`~robodk.robomath.Mat`) of the robot tool (TCP) with respect to the robot flange
        """
        return self.PoseTool()

    def Frame(self):
        """
        .. deprecated:: 4.0
            Obsolete. Use :func:`~robodk.robolink.Item.PoseFrame` instead.

        Returns the pose (:class:`~robodk.robomath.Mat`) of the robot reference frame with respect to the robot base
        """
        return self.PoseFrame()

    def setHtool(self, tool):
        """
        .. deprecated:: 4.0
            Obsolete. :func:`~robodk.robolink.Item.setPoseTool` instead.

        Sets the robot tool pose (TCP) with respect to the robot flange. The tool pose can be an item or a 4x4 Matrix
        """
        self.setPoseTool(tool)

    def setTool(self, tool):
        """
        .. deprecated:: 4.0
            Obsolete. Use :func:`~robodk.robolink.Item.setPoseTool` instead.

        Sets the robot tool pose (TCP) with respect to the robot flange. The tool pose can be an item or a 4x4 Matrix
        """
        self.setPoseTool(tool)

    def setFrame(self, frame):
        """
        .. deprecated:: 4.0
            Obsolete. Use :func:`~robodk.robolink.Item.setPoseFrame` instead.

        Sets the reference frame of a robot (user frame). The frame can be an item or a 4x4 Matrix
        """
        self.setPoseFrame(frame)

    # -----------------------

    def AddTool(self, tool_pose, tool_name='New TCP'):
        """Add a tool to a robot given the tool pose and the tool name. It returns the tool as an :class:`.Item`.

        :param tool_pose: Tool pose (TCP) of the tool with respect to the robot flange
        :type tool_pose: :class:`~robodk.robomath.Mat`
        :param str tool_name: name of the tool

        .. seealso:: :func:`~robodk.robolink.Robolink.AddFrame`, :func:`~robodk.robolink.Item.PoseTool`, :func:`~robodk.robolink.Item.setPoseTool`, :func:`~robodk.robolink.Robolink.AddFile`
        """
        with self.link._lock:
            self.link._check_connection()
            command = 'AddToolEmpty'
            self.link._send_line(command)
            self.link._send_item(self)
            self.link._send_pose(tool_pose)
            self.link._send_line(tool_name)
            newtool = self.link._rec_item()
            self.link._check_status()
            return newtool

    def SolveFK(self, joints, tool=None, reference=None):
        """Calculate the forward kinematics of the robot for the provided joints.
        Returns the pose of the robot flange with respect to the robot base reference (:class:`~robodk.robomath.Mat`).

        :param joints: robot joints
        :type joints: list of float or :class:`~robodk.robomath.Mat`
        :param tool: Optionally provide the tool used to calculate the forward kinematics. If this parameter is ignored it will use the robot flange.
        :type tool: :class:`~robodk.robomath.Mat`
        :param reference: Optionally provide the reference frame used to calculate the forward kinematics. If this parameter is ignored it will use the robot base frame.
        :type reference: :class:`~robodk.robomath.Mat`

        .. seealso:: :func:`~robodk.robolink.Item.SolveIK`, :func:`~robodk.robolink.Item.SolveIK_All`, :func:`~robodk.robolink.Item.JointsConfig`

        Example:

        .. code-block:: python

            from robodk.robolink import *           # import the robolink library
            RDK = Robolink()                        # connect to the RoboDK API (RoboDK starts if it has not started
            robot  = RDK.Item('', ITEM_TYPE_ROBOT)  # Retrieve the robot

            # get the current robot joints
            robot_joints = robot.Joints()

            # get the robot position from the joints (calculate forward kinematics)
            robot_position = robot.SolveFK(robot_joints)

            # get the robot configuration (robot joint state)
            robot_config = robot.JointsConfig(robot_joints)

            # calculate the new robot position
            new_robot_position = transl([x_move,y_move,z_move])*robot_position

            # calculate the new robot joints
            new_robot_joints = robot.SolveIK(new_robot_position)
            if len(new_robot_joints.tolist()) < 6:
                print("No robot solution!! The new position is too far, out of reach or close to a singularity")
                continue

            # calculate the robot configuration for the new joints
            new_robot_config = robot.JointsConfig(new_robot_joints)

            if robot_config[0] != new_robot_config[0] or robot_config[1] != new_robot_config[1] or robot_config[2] != new_robot_config[2]:
                print("Warning! Robot configuration changed: this may lead to unextected movements!")
                print(robot_config)
                print(new_robot_config)

            # move the robot to the new position
            robot.MoveJ(new_robot_joints)
            #robot.MoveL(new_robot_joints)
        """
        with self.link._lock:
            self.link._check_connection()
            command = 'G_FK'
            self.link._send_line(command)
            self.link._send_array(joints)
            self.link._send_item(self)
            pose = self.link._rec_pose()
            self.link._check_status()
            if tool is not None:
                pose = pose * tool
            if reference is not None:
                pose = robomath.invH(reference) * pose
            return pose

    def JointsConfig(self, joints):
        """Returns the robot configuration state for a set of robot joints.
        The configuration state is defined as: [REAR, LOWERARM, FLIP, turns]. The turns are reserved for future use.

        Example:

        .. code-block:: python

            # Retrieve all solutions for a given pose:
            all_solutions = robot.SolveIK_All(pose, toolpose, framepose)
            joints = []

            # Iterate through each solution
            for j in all_solutions:
                # Retrieve flags as a list for each solution
                conf_RLF = robot.JointsConfig(j).list()

                # Breakdown of flags:
                rear  = conf_RLF[0] # 1 if Rear , 0 if Front
                lower = conf_RLF[1] # 1 if Lower, 0 if Upper (elbow)
                flip  = conf_RLF[2] # 1 if Flip , 0 if Non flip (Flip is usually when Joint 5 is negative)

                # Look for a solution with Front and Elbow up configuration
                #if conf_RLF[0:2] == [0,0]:
                if rear == 0 and lower == 0:
                    print("Solution found!")
                    joints = j
                    break


        :param joints: robot joints
        :type joints: list of float

        .. seealso:: :func:`~robodk.robolink.Item.SolveFK`, :func:`~robodk.robolink.Item.SolveIK`
        """
        with self.link._lock:
            self.link._check_connection()
            command = 'G_Thetas_Config'
            self.link._send_line(command)
            self.link._send_array(joints)
            self.link._send_item(self)
            config = self.link._rec_array()
            self.link._check_status()
            return config

    def SolveIK(self, pose, joints_approx=None, tool=None, reference=None):
        """Calculates the inverse kinematics for a given specified pose. The pose must be robot flange with respect to the robot base unless you provide the tool and/or reference.
        SolveIK returns the joints solution as a Mat object (size 1xnDOFs). Use list() on a Mat to convert to a list. If there is no solution it returns an array of size 0.
        If there is no solution it returns an empty matrix.

        Note: For some 6-axis robots, SolveIK returns 2 additional values that can be ignored.

        :param pose: pose of the robot flange with respect to the robot base frame
        :type pose: :class:`~robodk.robomath.Mat`
        :param joints_approx: Preferred joint solution. Leave blank to return the closest match to the current robot position.
        :type joints_approx: list of float
        :param tool: Tool pose with respect to the robot flange (TCP)
        :type tool: :class:`~robodk.robomath.Mat`
        :param reference: Reference pose (reference frame with respect to the robot base)
        :type reference: :class:`~robodk.robomath.Mat`

        .. seealso:: :func:`~robodk.robolink.Item.SolveFK`, :func:`~robodk.robolink.Item.SolveIK_All`, :func:`~robodk.robolink.Item.JointsConfig`
        """
        with self.link._lock:
            if tool is not None:
                pose = pose * robomath.invH(tool)
            if reference is not None:
                pose = reference * pose

            self.link._check_connection()
            if joints_approx is None:
                command = 'G_IK'
                self.link._send_line(command)
                self.link._send_pose(pose)
                self.link._send_item(self)
                joints = self.link._rec_array()
            else:
                command = 'G_IK_jnts'
                self.link._send_line(command)
                self.link._send_pose(pose)
                self.link._send_array(joints_approx)
                self.link._send_item(self)
                joints = self.link._rec_array()
            self.link._check_status()
            return joints

    def SolveIK_All(self, pose, tool=None, reference=None):
        """Calculates the inverse kinematics for the specified robot and pose. The function returns all available joint solutions as a 2D matrix.
        Returns a list of joints as a 2D matrix [N x M], where N is the number of degrees of freedom (robot joints) and M is the number of solutions. For some 6-axis robots, SolveIK returns 2 additional values that can be ignored.

        :param pose: pose of the robot flange with respect to the robot base frame
        :type pose: :class:`~robodk.robomath.Mat`

        .. seealso:: :func:`~robodk.robolink.Item.SolveFK`, :func:`~robodk.robolink.Item.SolveIK`, :func:`~robodk.robolink.Item.JointsConfig`"""
        with self.link._lock:
            if tool is not None:
                pose = pose * robomath.invH(tool)
            if reference is not None:
                pose = reference * pose

            self.link._check_connection()
            command = 'G_IK_cmpl'
            self.link._send_line(command)
            self.link._send_pose(pose)
            self.link._send_item(self)
            joints_list = self.link._rec_matrix()
            self.link._check_status()
            return joints_list

    def FilterTarget(self, pose, joints_approx=None):
        """Filters a target to improve accuracy. This option requires a calibrated robot.
        :param pose: pose of the robot TCP with respect to the robot reference frame
        :type pose: :class:`~robodk.robomath.Mat`
        :param joints_approx: approximated desired joints to define the preferred configuration
        :type joints_approx: list of float or :class:`~robodk.robomath.Mat`"""
        with self.link._lock:
            self.link._check_connection()
            command = 'FilterTarget'
            self.link._send_line(command)
            self.link._send_pose(pose)
            if joints_approx is None:
                joints_approx = [0, 0, 0, 0, 0, 0]
            self.link._send_array(joints_approx)
            self.link._send_item(self)
            pose_filtered = self.link._rec_pose()
            joints_filtered = self.link._rec_array()
            self.link._check_status()
            return pose_filtered, joints_filtered

    def Connect(self, robot_ip='', blocking=True):
        """Connect to a real robot and wait for a connection to succeed. Returns 1 if connection succeeded, or 0 if it failed.

        :param robot_ip: Robot IP. Leave blank to use the IP selected in the connection panel of the robot.
        :type robot_ip: str

        .. seealso:: :func:`~robodk.robolink.Item.ConnectSafe`, :func:`~robodk.robolink.Item.ConnectedState`, :func:`~robodk.robolink.Item.Disconnect`, :func:`~robodk.robolink.Robolink.setRunMode`
        """
        with self.link._lock:
            self.link._check_connection()
            command = 'Connect2'
            self.link._send_line(command)
            self.link._send_item(self)
            self.link._send_line(robot_ip)
            self.link._send_int(1 if blocking else 0)
            status = self.link._rec_int()
            self.link._check_status()
            return status

    def ConnectSafe(self, robot_ip='', max_attempts=5, wait_connection=4, callback_abort=None):
        """Connect to a real robot and wait for a connection to succeed. Returns the connected state returned by ConnectedState() (0 if connection succeeded and the robot is ready).

        :param robot_ip: Robot IP. Leave blank to use the IP selected in the connection panel of the robot.
        :type robot_ip: str
        :param max_attempts: maximum connection attemps before reporting an unsuccessful connection
        :type max_attempts: int
        :param wait_connection: time to wait in seconds between connection attempts
        :type wait_connection: float
        :param callback_abort: function pointer that returns true if we should abort the connection operation
        :type callback_abort: function

        .. seealso:: :func:`~robodk.robolink.Item.Connect`, :func:`~robodk.robolink.Item.ConnectedState`, :func:`~robodk.robolink.Robolink.setRunMode`
        """
        # Never attempt to reconnect if we are already connected
        con_status, status_msg = self.ConnectedState()
        print(status_msg)
        if con_status == ROBOTCOM_READY:
            return con_status

        trycount = 0
        refresh_rate = 0.2
        self.Connect(blocking=False)
        robomath.tic()
        timer1 = robomath.toc()
        robomath.pause(refresh_rate)
        while True:
            # Wait up to 2 seconds to see the connected state
            for i in range(10):
                con_status, status_msg = self.ConnectedState()
                print(status_msg)
                if con_status == ROBOTCOM_READY:
                    return con_status

                if callback_abort is not None and callback_abort():
                    return con_status

                robomath.pause(refresh_rate)

            if con_status < 0:
                print('Trying to reconnect...')
                self.Disconnect()
            if callback_abort is not None and callback_abort():
                return con_status

            time.sleep(refresh_rate)
            self.Connect()

            if robomath.toc() - timer1 > wait_connection:
                timer1 = robomath.toc()
                trycount = trycount + 1
                if trycount >= max_attempts:
                    print('Failed to connect: Timed out')
                    break

            if callback_abort is not None and callback_abort():
                return con_status

            time.sleep(refresh_rate)

        return con_status

    def ConnectionParams(self):
        """Returns the robot connection parameters
        :return: [robotIP (str), port (int), remote_path (str), FTP_user (str), FTP_pass (str)]

        .. seealso:: :func:`~robodk.robolink.Item.setConnectionParams`, :func:`~robodk.robolink.Item.Connect`, :func:`~robodk.robolink.Item.ConnectSafe`
        """
        with self.link._lock:
            self.link._check_connection()
            command = 'ConnectParams'
            self.link._send_line(command)
            self.link._send_item(self)
            robot_ip = self.link._rec_line()
            port = self.link._rec_int()
            remote_path = self.link._rec_line()
            ftp_user = self.link._rec_line()
            ftp_pass = self.link._rec_line()
            self.link._check_status()
            return robot_ip, port, remote_path, ftp_user, ftp_pass

    def setConnectionParams(self, robot_ip, port, remote_path, ftp_user, ftp_pass):
        """Set the robot connection parameters

        :param robot_ip: robot IP
        :type robot_ip: str
        :param port: robot communication port
        :type port: int
        :param remote_path: path to transfer files on the robot controller
        :type remote_path: str
        :param ftp_user: user name for the FTP connection
        :type ftp_user: str
        :param ftp_pass: password credential for the FTP connection
        :type ftp_pass: str

        .. seealso:: :func:`~robodk.robolink.Item.ConnectionParams`, :func:`~robodk.robolink.Item.Connect`, :func:`~robodk.robolink.Item.ConnectSafe`
        """
        with self.link._lock:
            self.link._check_connection()
            command = 'setConnectParams'
            self.link._send_line(command)
            self.link._send_item(self)
            self.link._send_line(robot_ip)
            self.link._send_int(port)
            self.link._send_line(remote_path)
            self.link._send_line(ftp_user)
            self.link._send_line(ftp_pass)
            self.link._check_status()
            return self

    def ConnectedState(self):
        """Check connection status with a real robobt
        Out 1 : status code -> (int) ROBOTCOM_READY if the robot is ready to move, otherwise, status message will provide more information about the issue
        Out 2 : status message -> Message description of the robot status

        .. seealso:: :func:`~robodk.robolink.Item.ConnectionParams`, :func:`~robodk.robolink.Item.Connect`, :func:`~robodk.robolink.Item.ConnectSafe`

        Example:

        .. code-block:: python

            from robodk.robolink import *           # import the robolink library
            robot = RDK.Item('', ITEM_TYPE_ROBOT)   # Get the first robot available
            state = robot.Connect()
            print(state)

            # Check the connection status and message
            state, msg = robot.ConnectedState()
            print(state)
            print(msg)
            if state != ROBOTCOM_READY:
                print('Problems connecting: ' + robot.Name() + ': ' + msg)
                quit()

            # Move the robot (real robot if we are connected)
            robot.MoveJ(jnts, False)

        """
        with self.link._lock:
            self.link._check_connection()
            command = 'ConnectedState'
            self.link._send_line(command)
            self.link._send_item(self)
            robotcom_status = self.link._rec_int()
            status_msg = self.link._rec_line()
            self.link._check_status()
            return robotcom_status, status_msg

    def Disconnect(self):
        """Disconnect from a real robot (when the robot driver is used)
        Returns 1 if it disconnected successfully, 0 if it failed. It can fail if it was previously disconnected manually for example.

        .. seealso:: :func:`~robodk.robolink.Item.Connect`, :func:`~robodk.robolink.Item.ConnectedState`
        """
        with self.link._lock:
            self.link._check_connection()
            command = 'Disconnect'
            self.link._send_line(command)
            self.link._send_item(self)
            status = self.link._rec_int()
            self.link._check_status()
            return status

    def MoveJ(self, target, blocking=True):
        """Move a robot to a specific target ("Move Joint" mode). This function waits (blocks) until the robot finishes its movements.
        If this is used with a program item, a new joint movement instruction will be added to the program.
        Important note when adding new movement instructions to programs: only target items supported, not poses.

        :param target: Target to move to. It can be the robot joints (Nx1 or 1xN), the pose (4x4) or a target (item pointer)
        :type target: :class:`~robodk.robomath.Mat`, list of joints or :class:`.Item`
        :param blocking: Set to True to wait until the robot finished the movement (default=True). Set to false to make it a non blocking call. Tip: If set to False, use robot.Busy() to check if the robot is still moving.
        :type blocking: bool

        .. seealso:: :func:`~robodk.robolink.Item.MoveL`, :func:`~robodk.robolink.Item.MoveC`, :func:`~robodk.robolink.Item.SearchL`, :func:`~robodk.robolink.Robolink.AddTarget`
        """
        if self.type == ITEM_TYPE_PROGRAM:
            blocking = False
            if type(target) == Item:
                self.addMoveJ(target)
                return

        self.link._moveX(target, self, MOVE_TYPE_JOINT, blocking)

    def MoveL(self, target, blocking=True):
        """Moves a robot to a specific target ("Move Linear" mode). This function waits (blocks) until the robot finishes its movements. This function can also be called on Programs and a new movement instruction will be added at the end of the program.
        If this is used with a program item, a new linear movement instruction will be added to the program.
        Important note when adding new movement instructions to programs: only target items supported, not poses.

        :param target: Target to move to. It can be the robot joints (Nx1 or 1xN), the pose (4x4) or a target (item pointer)
        :type target: :class:`~robodk.robomath.Mat`, list of joints or :class:`.Item`
        :param blocking: Set to True to wait until the robot finished the movement (default=True). Set to false to make it a non blocking call. Tip: If set to False, use robot.Busy() to check if the robot is still moving.
        :type blocking: bool

        .. seealso:: :func:`~robodk.robolink.Item.MoveJ`, :func:`~robodk.robolink.Item.MoveC`, :func:`~robodk.robolink.Item.SearchL`, :func:`~robodk.robolink.Robolink.AddTarget`
        """
        if self.type == ITEM_TYPE_PROGRAM:
            blocking = False
            if type(target) == Item:
                self.addMoveL(target)
                return

        self.link._moveX(target, self, MOVE_TYPE_LINEAR, blocking)

    def SearchL(self, target, blocking=True):
        """Moves a robot to a specific target and stops when a specific input switch is detected ("Search Linear" mode). This function waits (blocks) until the robot finishes its movements.

        :param target: Target to move to. It can be the robot joints (Nx1 or 1xN), the pose (4x4) or a target (item pointer)
        :type target: :class:`~robodk.robomath.Mat`, list of joints or :class:`.Item`
        :param blocking: Set to True to wait until the robot finished the movement (default=True). Set to false to make it a non blocking call. Tip: If set to False, use robot.Busy() to check if the robot is still moving.
        :type blocking: bool

        .. seealso:: :func:`~robodk.robolink.Item.MoveJ`, :func:`~robodk.robolink.Item.MoveL`, :func:`~robodk.robolink.Item.MoveC`, :func:`~robodk.robolink.Robolink.AddTarget`


        Example:

        .. code-block:: python

            from robodk.robolink import *      # import the robolink library
            RDK = Robolink()                   # Connect to the RoboDK API
            r = RDK.Item('', ITEM_TYPE_ROBOT)
            r.MoveJ(pose_from)                 # Move to the approach point
            r.SearchL(pose_to)                 # Move towards the search location

            # Retrieve the contact point as joints and pose:
            targetJoints = r.Joints().list()
            targetPose = r.Pose()

            status = r.setParam("Driver", "Status")
            # Status is "1" a contact was found or "0" if not found (empty string means the driver does not support it)

            if len(status) > 0:
                # Important! Not all robot drivers support this "Driver Status" flag
                # This works in simulation
                if "1" in status:
                    # Contact found! We already have the robot joints and pose as targetJoints and targetPose respectively
                    pass
                else:
                    # Nothing found!
                    targetJoints = None
                    targetPose = None

            else:
                # When the driver does not support the Driver Status flag, we can use this workaround to check if we found an interference
                # Check if we are near the end point (for drivers that don't support the first option)
                if pose_is_similar(r.Pose(), pose_to, 0.1):
                    # The robot was not able to detect any interference
                    targetJoints = None
                    targetPose = None


        """
        if self.type == ITEM_TYPE_PROGRAM:
            self.link._moveX(target, self, MOVE_TYPE_LINEARSEARCH, False)
            return None

        self.link._moveX(target, self, MOVE_TYPE_LINEARSEARCH, blocking)
        return self.SimulatorJoints()

    def MoveC(self, target1, target2, blocking=True):
        """Move a robot to a specific target ("Move Circular" mode). By default, this procedure waits (blocks) until the robot finishes the movement.

        :param target1: pose along the cicle movement
        :type target1: :class:`~robodk.robomath.Mat`, list of joints or :class:`.Item`
        :param target2: final circle target
        :type target2: :class:`~robodk.robomath.Mat`, list of joints or :class:`.Item`
        :param blocking: True if the instruction should wait until the robot finished the movement (default=True)
        :type blocking: bool

        .. seealso:: :func:`~robodk.robolink.Item.MoveL`, :func:`~robodk.robolink.Item.MoveC`, :func:`~robodk.robolink.Item.SearchL`, :func:`~robodk.robolink.Robolink.AddTarget`
        """
        if self.type == ITEM_TYPE_PROGRAM:
            if type(target1) != Item or type(target2) != Item:
                raise Exception("Adding a movement instruction to a program given joints or a pose is not supported. Use a target item instead, for example, add a target as with RDK.AddTarget(...) and set the pose or joints.")
            self.addMoveC(target1, target2)

        else:
            self.link.MoveC(target1, target2, self, blocking)

    def MoveJ_Test(self, j1, j2, minstep_deg=-1):
        """Checks if a joint movement is feasible and free of collisions (if collision checking is activated). The robot will moved to the collision point if a collision is detected (use Joints to collect the collision joints) or it will be placed at the destination joints if a collision is not detected.

        :param j1: start joints
        :type j1: list of float
        :param j2: end joints
        :type j2: list of float
        :param float minstep_deg: joint step in degrees
        :return: returns 0 if the movement is free of collision or any other issues. Otherwise it returns the number of pairs of objects that collided if there was a collision.
        :rtype: int

        .. seealso:: :func:`~robodk.robolink.Item.MoveL_Test`, :func:`~robodk.robolink.Robolink.setCollisionActive`, :func:`~robodk.robolink.Item.MoveJ`, :func:`~robodk.robolink.Robolink.AddTarget`
        """
        with self.link._lock:
            self.link._check_connection()
            command = 'CollisionMove'
            self.link._send_line(command)
            self.link._send_item(self)
            self.link._send_array(j1)
            self.link._send_array(j2)
            self.link._send_int(minstep_deg * 1000)
            self.link.COM.settimeout(3600)  # wait up to 1 hour
            collision = self.link._rec_int()
            self.link.COM.settimeout(self.link.TIMEOUT)
            self.link._check_status()
            return collision

    def MoveJ_Test_Blend(self, j1, j2, j3, blend_deg=5, minstep_deg=-1):
        """Checks if a joint movement with blending is feasible and free of collisions (if collision checking is activated). The robot will move to the collision point if a collision is detected (use Joints to collect the collision joints) or it will be placed at the destination joints if a collision is not detected.

        :param j1: start joints
        :type j1: list of float
        :param j2: joints via
        :type j2: list of float
        :param j3: joints final destination
        :type j3: list of float
        :param blend_deg: blend in degrees
        :type blend_deg: float
        :param minstep_deg: maximum joint step in degrees
        :type minstep_deg: float
        :return: returns 0 if the movement is free of collision or any other issues. Otherwise it returns the number of pairs of objects that collided if there was a collision.
        :rtype: int

        .. seealso:: :func:`~robodk.robolink.Item.MoveJ_Test`, :func:`~robodk.robolink.Robolink.setCollisionActive`, :func:`~robodk.robolink.Item.MoveJ`, :func:`~robodk.robolink.Robolink.AddTarget`
        """
        with self.link._lock:
            self.link._require_build(7206)
            self.link._check_connection()
            self.link._send_line("CollisionMoveBlend")
            self.link._send_item(self)
            self.link._send_array(j1)
            self.link._send_array(j2)
            self.link._send_array(j3)
            self.link._send_int(minstep_deg * 1000.0)
            self.link._send_int(blend_deg * 1000.0)
            self.link.COM.settimeout(3600)
            collision = self.link._rec_int()
            self.link.COM.settimeout(self.link.TIMEOUT)
            self.link._check_status()
            return collision

    def MoveL_Test(self, j1, pose, minstep_mm=-1):
        """Checks if a linear movement is feasible and free of collisions (if collision checking is activated). The robot will moved to the collision point if a collision is detected (use Joints to collect the collision joints) or it will be placed at the destination pose if a collision is not detected.

        :param j1: start joints
        :type j1: list of float
        :param pose: end pose (position of the active tool with respect to the active reference frame)
        :type pose: :class:`~robodk.robomath.Mat`
        :param float minstep_mm: linear step in mm
        :return: returns 0 if the movement is free of collision or any other issues.
        :rtype: int

        If the robot can not reach the target pose it returns -2. If the robot can reach the target but it can not make a linear movement it returns -1.

        .. seealso:: :func:`~robodk.robolink.Item.MoveJ_Test`, :func:`~robodk.robolink.Item.setPoseFrame`, :func:`~robodk.robolink.Item.setPoseTool`, :func:`~robodk.robolink.Robolink.setCollisionActive`, :func:`~robodk.robolink.Item.MoveL`, :func:`~robodk.robolink.Robolink.AddTarget`
        """
        with self.link._lock:
            self.link._check_connection()
            command = 'CollisionMoveL'
            self.link._send_line(command)
            self.link._send_item(self)
            self.link._send_array(j1)
            self.link._send_pose(pose)
            self.link._send_int(minstep_mm * 1000)
            self.link.COM.settimeout(3600)  # wait up to 1 hour
            collision = self.link._rec_int()
            self.link.COM.settimeout(self.link.TIMEOUT)
            self.link._check_status()
            return collision

    def setSpeed(self, speed_linear, speed_joints=-1, accel_linear=-1, accel_joints=-1):
        """Sets the linear speed of a robot. Additional arguments can be provided to set linear acceleration or joint speed and acceleration.

        :param float speed_linear: linear speed -> speed in mm/s (-1 = no change)
        :param float speed_joints: joint speed (optional) -> speed in deg/s (-1 = no change)
        :param float accel_linear: linear acceleration (optional) -> acceleration in mm/s^2 (-1 = no change)
        :param float accel_joints: joint acceleration (optional) -> acceleration in deg/s^2 (-1 = no change)

        .. seealso:: :func:`~robodk.robolink.Item.setAcceleration`, :func:`~robodk.robolink.Item.setSpeedJoints`, :func:`~robodk.robolink.Item.setAccelerationJoints`
        """
        with self.link._lock:
            self.link._check_connection()
            command = 'S_Speed4'
            self.link._send_line(command)
            self.link._send_item(self)
            self.link._send_array([float(speed_linear), float(speed_joints), float(accel_linear), float(accel_joints)])
            self.link._check_status()
            return self

    def setAcceleration(self, accel_linear):
        """Sets the linear acceleration of a robot in mm/s2

        :param float accel_linear: acceleration in mm/s2

        .. seealso:: :func:`~robodk.robolink.Item.setSpeed`, :func:`~robodk.robolink.Item.setSpeedJoints`, :func:`~robodk.robolink.Item.setAccelerationJoints`
        """
        self.setSpeed(-1, -1, accel_linear, -1)
        return self

    def setSpeedJoints(self, speed_joints):
        """Sets the joint speed of a robot in deg/s for rotary joints and mm/s for linear joints

        :param float speed_joints: speed in deg/s for rotary joints and mm/s for linear joints

        .. seealso:: :func:`~robodk.robolink.Item.setSpeed`, :func:`~robodk.robolink.Item.setAcceleration`, :func:`~robodk.robolink.Item.setAccelerationJoints`
        """
        self.setSpeed(-1, speed_joints, -1, -1)
        return self

    def setAccelerationJoints(self, accel_joints):
        """Sets the joint acceleration of a robot

        :param float accel_joints: acceleration in deg/s2 for rotary joints and mm/s2 for linear joints

        .. seealso:: :func:`~robodk.robolink.Item.setSpeed`, :func:`~robodk.robolink.Item.setAcceleration`, :func:`~robodk.robolink.Item.setSpeedJoints`
        """
        self.setSpeed(-1, -1, -1, accel_joints)
        return self

    def setRounding(self, rounding_mm):
        """Sets the rounding accuracy to smooth the edges of corners. In general, it is recommended to allow a small approximation near the corners to maintain a constant speed.
        Setting a rounding values greater than 0 helps avoiding jerky movements caused by constant acceleration and decelerations.

        :param float rounding_mm: rounding accuracy in mm. Set to -1 (default) for best accuracy and to have point to point movements (might have a jerky behavior)

        This rounding parameter is also known as ZoneData (ABB), CNT (Fanuc), C_DIS/ADVANCE (KUKA), cornering (Mecademic) or blending (Universal Robots)

        .. seealso:: :func:`~robodk.robolink.Item.setSpeed`
        """
        with self.link._lock:
            self.link._check_connection()
            command = 'S_ZoneData'
            self.link._send_line(command)
            self.link._send_int(rounding_mm * 1000)
            self.link._send_item(self)
            self.link._check_status()
            return self

    def setZoneData(self, zonedata):
        """
        .. deprecated:: 4.0
            Obsolete. Use :func:`~robodk.robolink.Item.setRounding` instead.
        """
        return self.setRounding(zonedata)

    def ShowSequence(self, matrix, display_type=SEQUENCE_DISPLAY_DEFAULT, timeout=-1):
        """Displays a sequence of joints or poses in RoboDK.

        :param matrix: list of joints as a matrix or as a list of joint arrays, a list of poses, or a sequence of instructions (same sequence that was supported with RoKiSim).
        :type matrix: list of list of float, a matrix of joints as a :class:`~robodk.robomath.Mat` or a list of poses as :class:`~robodk.robomath.Mat`
        :param display_type: display options (SEQUENCE_DISPLAY_*). Use -1 to use default.
        :type display_type: int, optional
        :param timeout: display timeout, in milliseconds. Use -1 to use default.
        :type timeout: int, optional

        Tip: use :func:`~robodk.robolink.Item.InstructionList` to retrieve the instruction list in RoKiSim format.

        Example:

        .. code-block:: python

            from robolink import *
            from robodk import *
            RDK = Robolink()

            prog = RDK.ItemUserPick('Select a Program', ITEM_TYPE_PROGRAM)
            if not prog.Valid():
                quit()

            robot = prog.getLink(ITEM_TYPE_ROBOT)
            if not robot.Valid():
                quit()

            # Calculate delta time to display robots
            prog_stats = prog.Update()
            time_estimate = prog_stats[1]
            TIME_STEP = max(1, time_estimate / 100)

            # Define the way we want to output the list of joints
            status_msg, joint_list, status_code = prog.InstructionListJoints(1, 1, flags=5, time_step=TIME_STEP)

            # Status code is negative if there are errors in the program
            print("Status code:" + str(status_code))
            print("Status message: " + status_msg)
            print(joint_list.tr())
            print("Size: " + str(len(joint_list)))

            # Show as ghost robot
            joints = []
            for j in joint_list:
                joints.append(j)

            # Display "ghost" robots in RoboDK
            robot.ShowSequence(joints, SEQUENCE_DISPLAY_OPTION_RESET | SEQUENCE_DISPLAY_ROBOT_JOINTS | SEQUENCE_DISPLAY_TRANSPARENT, 3600*1000)

        """

        display_ghost_joints = display_type & SEQUENCE_DISPLAY_ROBOT_JOINTS if display_type > 0 else False
        with self.link._lock:
            if type(matrix) == list and (len(matrix) == 0 or type(matrix[0]) == robomath.Mat or display_ghost_joints):
                # poses assumed
                self.link._check_connection()
                command = 'Show_SeqPoses'
                self.link._send_line(command)
                self.link._send_item(self)
                self.link._send_array([display_type, timeout])
                self.link._send_int(len(matrix))
                if display_ghost_joints:
                    for jnts in matrix:
                        self.link._send_array(jnts)

                else:
                    for pose in matrix:
                        self.link._send_pose(pose)

                self.link._check_status()

            else:
                # list of joints as a Mat assumed
                self.link._check_connection()
                command = 'Show_Seq'
                self.link._send_line(command)
                self.link._send_matrix(matrix)
                self.link._send_item(self)
                self.link._check_status()

    def Busy(self):
        """Checks if a robot or program is currently running (busy or moving).
        Returns a busy status (1=moving, 0=stopped)

        .. seealso:: :func:`~robodk.robolink.Item.WaitMove`, :func:`~robodk.robolink.Item.RunProgram`, :func:`~robodk.robolink.Item.RunCodeCustom`, :func:`~robodk.robolink.Item.RunInstruction`

        Example:

        .. code-block:: python

            from robodk.robolink import *      # import the robolink library
            from robodk.robomath import *
            RDK = Robolink()                   # Connect to the RoboDK API
            prog = RDK.Item('MainProgram', ITEM_TYPE_PROGRAM)
            prog.RunProgram()
            while prog.Busy():
                pause(0.1)

            print("Program done")

        """
        with self.link._lock:
            self.link._check_connection()
            command = 'IsBusy'
            self.link._send_line(command)
            self.link._send_item(self)
            busy = self.link._rec_int()
            self.link._check_status()
            return busy

    def Stop(self):
        """Stop a program or a robot

        .. seealso:: :func:`~robodk.robolink.Item.RunProgram`, :func:`~robodk.robolink.Item.MoveJ`
        """
        with self.link._lock:
            self.link._check_connection()
            command = 'Stop'
            self.link._send_line(command)
            self.link._send_item(self)
            self.link._check_status()

    def WaitMove(self, timeout=360000):
        """Waits (blocks) until the robot finishes its movement.

        :param float timeout: Maximum time to wait for robot to finish its movement (in seconds)

        .. seealso:: :func:`~robodk.robolink.Item.Busy`, :func:`~robodk.robolink.Item.MoveJ`
        """
        self.link._check_connection()
        command = 'WaitMove'
        self.link._send_line(command)
        self.link._send_item(self)
        self.link._check_status()
        self.link.COM.settimeout(timeout)
        self.link._check_status()  #will wait here
        self.link.COM.settimeout(self.link.TIMEOUT)
        #busy = self.link.Is_Busy(self.item)
        #while busy:
        #    busy = self.link.Is_Busy(self.item)

    def WaitFinished(self):
        """Wait until a program finishes or a robot completes its movement

        .. seealso:: :func:`~robodk.robolink.Item.Busy`
        """
        while self.Busy():
            time.sleep(0.05)

    def ProgramStart(self, programname, folder='', postprocessor=''):
        """Defines the name of the program when a program must be generated.
        It is possible to specify the name of the post processor as well as the folder to save the program.
        This method must be called before any program output is generated (before any robot movement or other program instructions).

        :param str progname: name of the program
        :param str folder: folder to save the program, leave empty to use the default program folder
        :param str postprocessor: name of the post processor (for a post processor in C:/RoboDK/Posts/Fanuc_post.py it is possible to provide "Fanuc_post.py" or simply "Fanuc_post")

        .. seealso:: :func:`~robodk.robolink.Robolink.setRunMode`
        """
        return self.link.ProgramStart(programname, folder, postprocessor, self)

    def setAccuracyActive(self, accurate=1):
        """Sets the accuracy of the robot active or inactive. A robot must have been calibrated to properly use this option.

        :param int accurate: set to 1 to use the accurate model or 0 to use the nominal model

        .. seealso:: :func:`~robodk.robolink.Item.AccuracyActive`
        """
        with self.link._lock:
            self.link._check_connection()
            command = 'S_AbsAccOn'
            self.link._send_line(command)
            self.link._send_item(self)
            self.link._send_int(accurate)
            self.link._check_status()

    def AccuracyActive(self):
        """Returns True if the accurate kinematics are being used. Accurate kinematics are available after a robot calibration.

        .. seealso:: :func:`~robodk.robolink.Item.setAccuracyActive`
        """
        with self.link._lock:
            self.link._check_connection()
            command = 'G_AbsAccOn'
            self.link._send_line(command)
            self.link._send_item(self)
            isaccurate = self.link._rec_int()
            self.link._check_status()
            return isaccurate > 0

    def setParamRobotTool(self, tool_mass=5, tool_cog=None):
        """Sets the tool mass and center of gravity. This is only used with accurate robots to improve accuracy.

        :param float tool_mass: tool weigth in Kg
        :param list tool_cog: tool center of gravity as [x,y,z] with respect to the robot flange

        """
        with self.link._lock:
            self.link._check_connection()
            command = 'S_ParamCalibTool'
            self.link._send_line(command)
            self.link._send_item(self)
            values = []
            values.append(tool_mass)
            if tool_cog is not None:
                values += tool_cog
            self.link._send_array(values)
            self.link._check_status()

    def FilterProgram(self, filestr):
        """Filter a program file to improve accuracy for a specific robot. The robot must have been previously calibrated.
        It returns 0 if the filter succeeded, or a negative value if there are filtering problems. It also returns a summary of the filtering.

        :param str filestr: File path of the program. Formats supported include: JBI (Motoman), SRC (KUKA), MOD (ABB), PRG (ABB), LS (FANUC).
        """
        with self.link._lock:
            self.link._check_connection()
            command = 'FilterProg2'
            self.link._send_line(command)
            self.link._send_item(self)
            self.link._send_line(filestr)
            filter_status = self.link._rec_int()
            filter_msg = self.link._rec_line()
            self.link._check_status()
            return filter_status, filter_msg

    #"""Program item calls"""
    def MakeProgram(self, folder_path='', run_mode=RUNMODE_MAKE_ROBOTPROG):
        """Generate the program file. Returns True if the program was successfully generated.

        :param str pathstr: Folder to save the program (not including the file name and extension). Make sure the folder ends with a slash. You can use backslashes or forward slashes to define the path. In most cases, the file name is defined by the program name (visible in the RoboDK tree) and the extension is defined by the Post Processor (the file extension must match the extension supported by your robot controller). It can be left empty to use the default action (save to the default programs location)
        :param run_mode: RUNMODE_MAKE_ROBOTPROG to generate the program file. Alternatively, Use RUNMODE_MAKE_ROBOTPROG_AND_UPLOAD or RUNMODE_MAKE_ROBOTPROG_AND_START to transfer the program through FTP and execute the program.
        :return: [success (True or False), log (str), transfer_succeeded (True/False)]

        Transfer succeeded is True if there was a successful program transfer (if RUNMODE_MAKE_ROBOTPROG_AND_UPLOAD or RUNMODE_MAKE_ROBOTPROG_AND_START are used)

        .. seealso:: :func:`~robodk.robolink.Robolink.setRunMode`
        """
        if len(folder_path) > 0 and not (folder_path.endswith("/") or folder_path.endswith("\\")):
            folder_path = folder_path + "/"

        with self.link._lock:
            self.link._check_connection()
            command = 'MakeProg2'
            self.link._send_line(command)
            self.link._send_item(self)
            self.link._send_line(folder_path)
            self.link._send_int(run_mode)
            self.link.COM.settimeout(300)  # wait up to 5 minutes for the program to generate
            prog_status = self.link._rec_int()
            self.link.COM.settimeout(self.link.TIMEOUT)
            prog_log_str = self.link._rec_line()
            transfer_status = self.link._rec_int()
            self.link._check_status()
            success = False
            if prog_status > 0:
                success = True
            transfer_ok = False
            if transfer_status > 0:
                transfer_ok = True

            return success, prog_log_str, transfer_ok

    def setRunType(self, program_run_type):
        """Set the Run Type of a program to specify if a program made using the GUI will be run in simulation mode or on the real robot ("Run on robot" option).

        :param int program_run_type: Use "PROGRAM_RUN_ON_SIMULATOR" to set the program to run on the simulator only or "PROGRAM_RUN_ON_ROBOT" to force the program to run on the robot

        .. seealso:: :func:`~robodk.robolink.Robolink.setRunMode` :func:`~robodk.robolink.Item.RunType`
        """
        with self.link._lock:
            self.link._check_connection()
            command = 'S_ProgRunType'
            self.link._send_line(command)
            self.link._send_item(self)
            self.link._send_int(program_run_type)
            self.link._check_status()

    def RunType(self):
        """Get the Run Type of a program to specify if a program made using the GUI will be run in simulation mode or on the real robot ("Run on robot" option).

        .. seealso:: :func:`~robodk.robolink.Robolink.setRunMode` :func:`~robodk.robolink.Item.setRunType`
        """
        with self.link._lock:
            self.link._check_connection()
            command = 'G_ProgRunType'
            self.link._send_line(command)
            self.link._send_item(self)
            program_run_type = self.link._rec_int()
            self.link._check_status()
            return program_run_type

    def RunProgram(self, prog_parameters=None):
        """
        .. deprecated:: 4.0
            Obsolete. Use :func:`~robodk.robolink.Item.RunCode` instead. RunProgram is available for backwards compatibility.
        """
        return self.RunCode(prog_parameters)

    def RunCode(self, prog_parameters=None):
        """Run a program. It returns the number of instructions that can be executed successfully (a quick program check is performed before the program starts)
        This is a non-blocking call. Use program.Busy() to check if the program execution finished, or program.WaitFinished() to wait until the program finishes.

        :param prog_parameters: Program parameters can be provided for Python programs as a string
        :type prog_parameters: list of str

        .. seealso:: :func:`~robodk.robolink.Item.RunCodeCustom`, :func:`~robodk.robolink.Item.Busy`, :func:`~robodk.robolink.Robolink.AddProgram`

        If setRunMode(RUNMODE_SIMULATE) is used: the program will be simulated (default run mode)

        If setRunMode(RUNMODE_RUN_ROBOT) is used: the program will run on the robot (default when RUNMODE_RUN_ROBOT is used)

        If setRunMode(RUNMODE_RUN_ROBOT) is used together with program.setRunType(PROGRAM_RUN_ON_ROBOT) -> the program will run sequentially on the robot the same way as if we right clicked the program and selected "Run on robot" in the RoboDK GUI

        """
        with self.link._lock:
            self.link._check_connection()
            if type(prog_parameters) == list:
                command = 'RunProgParam'
                self.link._send_line(command)
                self.link._send_item(self)
                parameters = ''
                if type(prog_parameters) is list:
                    parameters = '<br>'.join(str(param_i) for param_i in prog_parameters)
                else:
                    parameters = str(prog_parameters)
                self.link._send_line(parameters)
            else:
                command = 'RunProg'
                self.link._send_line(command)
                self.link._send_item(self)
            prog_status = self.link._rec_int()
            self.link._check_status()
            return prog_status

    def RunCodeCustom(self, code, run_type=INSTRUCTION_CALL_PROGRAM):
        """
        .. deprecated:: 4.0
            Obsolete, use RunInstruction instead.

        Adds a program call, code, message or comment to the program. Returns 0 if succeeded.

        .. seealso:: :func:`~robodk.robolink.Item.RunInstruction`
        """
        return self.RunInstruction(code, run_type)

    def RunInstruction(self, code, run_type=INSTRUCTION_CALL_PROGRAM):
        """Adds a program call, code, message or comment to the program. Returns 0 if succeeded.

        :param str code: The code to insert, program to run, or comment to add.
        :param int run_type: Use INSTRUCTION_* variable to specify if the code is a program call or just a raw code insert. For example, to add a line of customized code use:

        .. code-block:: python
            :caption: Available Instruction Types

            INSTRUCTION_CALL_PROGRAM = 0        # Program call
            INSTRUCTION_INSERT_CODE = 1         # Insert raw code in the generated program
            INSTRUCTION_START_THREAD = 2        # Start a new process
            INSTRUCTION_COMMENT = 3             # Add a comment in the code
            INSTRUCTION_SHOW_MESSAGE = 4        # Add a message

        .. seealso:: :func:`~robodk.robolink.Item.RunCode`, :func:`~robodk.robolink.Robolink.AddProgram`

        Example:

        .. code-block:: python

            program.RunInstruction('Setting the spindle speed', INSTRUCTION_COMMENT)
            program.RunInstruction('SetRPM(25000)', INSTRUCTION_INSERT_CODE)
            program.RunInstruction('Done setting the spindle speed. Ready to start!', INSTRUCTION_SHOW_MESSAGE)
            program.RunInstruction('Program1', INSTRUCTION_CALL_PROGRAM)

        """
        with self.link._lock:
            self.link._check_connection()
            command = 'RunCode2'
            self.link._send_line(command)
            self.link._send_item(self)
            self.link._send_line(code.replace('\r\n', '<<br>>').replace('\n', '<<br>>'))
            self.link._send_int(run_type)
            prog_status = self.link._rec_int()
            self.link._check_status()
            return prog_status

    def Pause(self, time_ms=-1):
        """Pause instruction for a robot or insert a pause instruction to a program (when generating code offline -offline programming- or when connected to the robot -online programming-).

        :param float time_ms: time in miliseconds. Do not provide a value (leave the default -1) to pause until the user desires to resume the execution of a program.

        .. seealso:: :func:`~robodk.robolink.Robolink.AddProgram`
        """
        with self.link._lock:
            self.link._check_connection()
            command = 'RunPause'
            self.link._send_line(command)
            self.link._send_item(self)
            self.link._send_int(time_ms * 1000.0)
            self.link._check_status()

    def setDO(self, io_var, io_value):
        """Set a Digital Output (DO). This command can also be used to set any generic variables to a desired value.

        :param io_var: Digital Output (string or number)
        :type io_var: str or int
        :param io_value: value
        :type io_value: str, int or float

        .. seealso:: :func:`~robodk.robolink.Robolink.AddProgram`, :func:`~robodk.robolink.Item.setAO`, :func:`~robodk.robolink.Item.getDI`, :func:`~robodk.robolink.Item.getAI`
        """
        with self.link._lock:
            self.link._check_connection()
            command = 'setDO'
            self.link._send_line(command)
            self.link._send_item(self)
            self.link._send_line(str(io_var))
            self.link._send_line(str(io_value))
            self.link._check_status()

    def setAO(self, io_var, io_value):
        """Set an Analog Output (AO).

        :param io_var: Analog Output (string or number)
        :type io_var: str or int
        :param io_value: value
        :type io_value: str, int or float

        .. seealso:: :func:`~robodk.robolink.Robolink.AddProgram`, :func:`~robodk.robolink.Item.setDO`, :func:`~robodk.robolink.Item.getDI`, :func:`~robodk.robolink.Item.getAI`
        """
        with self.link._lock:
            self.link._check_connection()
            command = 'setAO'
            self.link._send_line(command)
            self.link._send_item(self)
            self.link._send_line(str(io_var))
            self.link._send_line(str(io_value))
            self.link._check_status()

    def getDI(self, io_var):
        """Get a Digital Input (DI). This function is only useful when connected to a real robot using the robot driver. It returns a string related to the state of the Digital Input (1=True, 0=False). This function returns an empty string if the script is not executed on the robot.

        :param io_var: Digital Input (string or number)
        :type io_var: str or int

        .. seealso:: :func:`~robodk.robolink.Robolink.AddProgram`, :func:`~robodk.robolink.Item.getAI`, :func:`~robodk.robolink.Item.setDO`, :func:`~robodk.robolink.Item.setAO`
        """
        with self.link._lock:
            self.link._check_connection()
            command = 'getDI'
            self.link._send_line(command)
            self.link._send_item(self)
            self.link._send_line(str(io_var))
            io_value = self.link._rec_line()
            self.link._check_status()
            return io_value

    def getAI(self, io_var):
        """Get an Analog Input (AI). This function is only useful when connected to a real robot using the robot driver. It returns a string related to the state of the Digital Input (0-1 or other range depending on the robot driver). This function returns an empty string if the script is not executed on the robot.

        :param io_var: Analog Input (string or number)
        :type io_var: str or int

        .. seealso:: :func:`~robodk.robolink.Robolink.AddProgram`, :func:`~robodk.robolink.Item.getDI`, :func:`~robodk.robolink.Item.setDO`, :func:`~robodk.robolink.Item.setAO`
        """
        with self.link._lock:
            self.link._check_connection()
            command = 'getAI'
            self.link._send_line(command)
            self.link._send_item(self)
            self.link._send_line(str(io_var))
            io_value = self.link._rec_line()
            self.link._check_status()
            return io_value

    def waitDI(self, io_var, io_value, timeout_ms=-1):
        """Wait for an digital input io_var to attain a given value io_value. Optionally, a timeout can be provided.

        :param io_var: digital input (string or number)
        :type io_var: str or int
        :param io_value: value
        :type io_value: str, int or float
        :param timeout_ms: timeout in milliseconds
        :type timeout_ms: int or float

        .. seealso:: :func:`~robodk.robolink.Robolink.AddProgram`
        """
        with self.link._lock:
            self.link._check_connection()
            command = 'waitDI'
            self.link._send_line(command)
            self.link._send_item(self)
            self.link._send_line(str(io_var))
            self.link._send_line(str(io_value))
            self.link._send_int(timeout_ms * 1000)
            self.link.COM.settimeout(3600 * 24 * 7)  # wait up to 1 week
            self.link._check_status()
            self.link.COM.settimeout(self.link.TIMEOUT)

    def customInstruction(self, name, path_run, path_icon="", blocking=1, cmd_run_on_robot=""):
        """Add a custom instruction. This instruction will execute a Python file or an executable file.

        :param name: Name of the instruction
        :type name: str or int
        :param path_run: path of the executable or Python script to run (relative to RoboDK/bin/ folder or absolute path)
        :type path_run: str
        :param path_icon: instruction image/icon path (relative to RoboDK/bin/ folder or absolute path)
        :type path_icon: str
        :param blocking: 1 if blocking, 0 if it is a non blocking executable trigger
        :type blocking: int
        :param cmd_run_on_robot: Command to send to the driver when connected to the robot
        :type cmd_run_on_robot: str

        .. seealso:: :func:`~robodk.robolink.Robolink.AddProgram`
        """
        with self.link._lock:
            self.link._check_connection()
            command = 'InsCustom2'
            self.link._send_line(command)
            self.link._send_item(self)
            self.link._send_line(name)
            self.link._send_line(path_run)
            self.link._send_line(path_icon)
            self.link._send_line(cmd_run_on_robot)
            self.link._send_int(blocking)
            self.link._check_status()

    def addMoveJ(self, itemtarget):
        """
        .. deprecated:: 4.0
            Obsolete. Use :func:`~robodk.robolink.Item.MoveJ` instead.

        Adds a new robot joint move instruction to a program.

        :param itemtarget: target item to move to
        :type itemtarget: :class:`.Item`

        .. seealso:: :func:`~robodk.robolink.Robolink.AddProgram`, :func:`~robodk.robolink.Item.MoveJ`
        """
        with self.link._lock:
            self.link._check_connection()
            command = 'Add_INSMOVE'
            self.link._send_line(command)
            self.link._send_item(itemtarget)
            self.link._send_item(self)
            self.link._send_int(1)
            self.link._check_status()

    def addMoveL(self, itemtarget):
        """
        .. deprecated:: 4.0
            Obsolete. Use :func:`~robodk.robolink.Item.MoveL` instead.

        Adds a new linear move instruction to a program.

        :param itemtarget: target item to move to
        :type itemtarget: :class:`.Item`

        .. seealso:: :func:`~robodk.robolink.Robolink.AddProgram`, :func:`~robodk.robolink.Item.MoveL`
        """
        with self.link._lock:
            self.link._check_connection()
            command = 'Add_INSMOVE'
            self.link._send_line(command)
            self.link._send_item(itemtarget)
            self.link._send_item(self)
            self.link._send_int(2)
            self.link._check_status()

    def addMoveSearch(self, itemtarget):
        """
        .. deprecated:: 4.0
            Obsolete. Use :func:`~robodk.robolink.Item.SearchL` instead.

        Adds a new linear search move instruction to a program.

        :param itemtarget: target item to move to
        :type itemtarget: :class:`.Item`

        .. seealso:: :func:`~robodk.robolink.Robolink.AddProgram`, :func:`~robodk.robolink.Item.SearchL`
        """
        with self.link._lock:
            self.link._check_connection()
            command = 'Add_INSMOVE'
            self.link._send_line(command)
            self.link._send_item(itemtarget)
            self.link._send_item(self)
            self.link._send_int(5)
            self.link._check_status()

    def addMoveC(self, itemtarget1, itemtarget2):
        """
        .. deprecated:: 4.0
            Obsolete. Use :func:`~robodk.robolink.Item.MoveC` instead.

        Adds a new circular move instruction to a program.

        :param itemtarget: target item to move to
        :type itemtarget: :class:`.Item`

        .. seealso:: :func:`~robodk.robolink.Robolink.AddProgram`, :func:`~robodk.robolink.Item.MoveL`, :func:`~robodk.robolink.Item.MoveC`
        """
        with self.link._lock:
            self.link._check_connection()
            command = 'Add_INSMOVEC'
            self.link._send_line(command)
            self.link._send_item(itemtarget1)
            self.link._send_item(itemtarget2)
            self.link._send_item(self)
            self.link._check_status()

    def ShowInstructions(self, show=True):
        """Show or hide instruction items of a program in the RoboDK tree

        :param show: Set to True to show the instruction nodes, otherwise, set to False
        :type show: bool

        .. seealso:: :func:`~robodk.robolink.Robolink.AddProgram`, :func:`~robodk.robolink.Item.ShowTargets`
        """
        with self.link._lock:
            self.link._check_connection()
            command = 'Prog_ShowIns'
            self.link._send_line(command)
            self.link._send_item(self)
            self.link._send_int(1 if show else 0)
            self.link._check_status()

    def ShowTargets(self, show=True):
        """Show or hide targets of a program in the RoboDK tree

        :param show: Set to False to remove the target item (the target is not deleted as it remains inside the program), otherwise, set to True to show the targets
        :type show: bool

        .. seealso:: :func:`~robodk.robolink.Robolink.AddProgram`, :func:`~robodk.robolink.Item.ShowInstructions`
        """
        with self.link._lock:
            self.link._check_connection()
            command = 'Prog_ShowTargets'
            self.link._send_line(command)
            self.link._send_item(self)
            self.link._send_int(1 if show else 0)
            self.link._check_status()

    def InstructionCount(self):
        """Return the number of instructions of a program.

        .. seealso:: :func:`~robodk.robolink.Robolink.AddProgram`
        """
        with self.link._lock:
            self.link._check_connection()
            command = 'Prog_Nins'
            self.link._send_line(command)
            self.link._send_item(self)
            nins = self.link._rec_int()
            self.link._check_status()
            return nins

    def InstructionSelect(self, ins_id=-1):
        """Select an instruction in the program as a reference to add new instructions. New instructions will be added after the selected instruction.
        If no instruction ID is specified, the active instruction will be selected and returned (if the program is running), otherwise it returns -1.

        .. seealso:: :func:`~robodk.robolink.Robolink.AddProgram`
        """
        with self.link._lock:
            self.link._check_connection()
            command = 'Prog_SelIns'
            self.link._send_line(command)
            self.link._send_item(self)
            self.link._send_int(ins_id)
            ins_id = self.link._rec_int()
            self.link._check_status()
            return ins_id

    def InstructionDelete(self, ins_id=0):
        """Delete an instruction of a program

        .. seealso:: :func:`~robodk.robolink.Robolink.AddProgram`
        """
        with self.link._lock:
            self.link._check_connection()
            command = 'Prog_DelIns'
            self.link._send_line(command)
            self.link._send_item(self)
            self.link._send_int(ins_id)
            success = self.link._rec_int() > 0
            self.link._check_status()
            return success

    def Instruction(self, ins_id=-1):
        """Return the current program instruction or the instruction given the instruction id (if provided).
        It returns the following information about an instruction:

        * name: name of the instruction (displayed in the RoboDK tree)
        * instype: instruction type (INS_TYPE_*). For example, INS_TYPE_MOVE for a movement instruction.
        * movetype: type of movement for INS_TYPE_MOVE instructions: MOVE_TYPE_JOINT for joint moves, or MOVE_TYPE_LINEAR for linear moves
        * isjointtarget: 1 if the target is specified in the joint space, otherwise, the target is specified in the cartesian space (by the pose)
        * target: pose of the target as :class:`.Item`
        * joints: robot joints for that target

        :param ins_id: instruction id to return
        :type ins_id: int

        .. seealso:: :func:`~robodk.robolink.Robolink.AddProgram`, :func:`~robodk.robolink.Item.setInstruction`, :func:`~robodk.robolink.Item.InstructionDelete`
        """
        with self.link._lock:
            self.link._check_connection()
            command = 'Prog_GIns'
            self.link._send_line(command)
            self.link._send_item(self)
            self.link._send_int(ins_id)
            name = self.link._rec_line()
            instype = self.link._rec_int()
            movetype = None
            isjointtarget = None
            target = None
            joints = None
            if instype == INS_TYPE_MOVE:
                movetype = self.link._rec_int()
                isjointtarget = self.link._rec_int()
                target = self.link._rec_pose()
                joints = self.link._rec_array()
            self.link._check_status()
            return name, instype, movetype, isjointtarget, target, joints

    def setInstruction(self, ins_id, name, instype, movetype, isjointtarget, target, joints):
        """Update a program instruction.

        :param ins_id: index of the instruction (0 for the first instruction, 1 for the second, and so on)
        :type ins_id: int
        :param name: Name of the instruction (displayed in the RoboDK tree)
        :type name: str
        :param instype: Type of instruction. INS_TYPE_*
        :type instype: int
        :param movetype: Type of movement if the instruction is a movement (MOVE_TYPE_JOINT or MOVE_TYPE_LINEAR)
        :type movetype: int
        :param isjointtarget: 1 if the target is defined in the joint space, otherwise it means it is defined in the cartesian space (by the pose)
        :type isjointtarget: int
        :param target: target pose
        :type target: :class:`~robodk.robomath.Mat`
        :param joints: robot joints for the target
        :type joints: list of float

        .. seealso:: :func:`~robodk.robolink.Robolink.AddProgram`, :func:`~robodk.robolink.Item.Instruction`
        """
        with self.link._lock:
            self.link._check_connection()
            command = 'Prog_SIns'
            self.link._send_line(command)
            self.link._send_item(self)
            self.link._send_int(ins_id)
            self.link._send_line(name)
            self.link._send_int(instype)
            if instype == INS_TYPE_MOVE:
                self.link._send_int(movetype)
                self.link._send_int(isjointtarget)
                self.link._send_pose(target)
                self.link._send_array(joints)
            self.link._check_status()

    def Update(self, check_collisions=COLLISION_OFF, timeout_sec=3600, mm_step=-1, deg_step=-1):
        """Updates a program and returns the estimated time and the number of valid instructions.
        An update can also be applied to a robot machining project. The update is performed on the generated program.

        :param int check_collisions: Check collisions (COLLISION_ON -yes- or COLLISION_OFF -no-)
        :param int timeout_sec: Maximum time to wait for the update to complete (in seconds)
        :param float mm_step: Step in mm to split the program (-1 means default, as specified in Tools-Options-Motion)
        :param float deg_step: Step in deg to split the program (-1 means default, as specified in Tools-Options-Motion)

        :return: [valid_instructions, program_time, program_distance, valid_ratio, readable_msg]

        valid_instructions: The number of valid instructions

        program_time: Estimated cycle time (in seconds)

        program_distance: Estimated distance that the robot TCP will travel (in mm)

        valid_ratio: This is a ratio from [0.00 to 1.00] showing if the path can be fully completed without any problems (1.0 means the path 100% feasible) or
        valid_ratio is <1.0 if there were problems along the path.

        valid_ratio will be < 0 if Update is called on a machining project and the machining project can't be achieved successfully.

        readable_msg: a readable message as a string

        .. seealso:: :func:`~robodk.robolink.Robolink.AddProgram`
        """
        with self.link._lock:
            self.link._check_connection()
            command = 'Update2'
            self.link._send_line(command)
            self.link._send_item(self)
            self.link._send_array([check_collisions, mm_step, deg_step])
            self.link.COM.settimeout(timeout_sec)  # wait up to 1 hour user to hit OK
            values = self.link._rec_array().tolist()
            self.link.COM.settimeout(self.link.TIMEOUT)
            readable_msg = self.link._rec_line()
            self.link._check_status()
            valid_instructions = values[0]
            program_time = values[1]
            program_distance = values[2]
            valid_ratio = values[3]
            return valid_instructions, program_time, program_distance, valid_ratio, readable_msg

    def InstructionList(self):
        """Returns the list of program instructions as an MxN matrix, where N is the number of instructions and M equals to 1 plus the number of robot axes. This is the equivalent sequence that used to be supported by RoKiSim.
        Tip: Use RDK.ShowSequence(matrix) to dipslay a joint list or a RoKiSim sequence of instructions.

        Out 1: Returns the matrix

        Out 2: Returns 0 if the program has no issues

        .. seealso:: :func:`~robodk.robolink.Item.ShowSequence`, :func:`~robodk.robolink.Item.InstructionListJoints`
        """
        with self.link._lock:
            self.link._check_connection()
            command = 'G_ProgInsList'
            self.link._send_line(command)
            self.link._send_item(self)
            insmat = self.link._rec_matrix()
            errors = self.link._rec_int()
            self.link._check_status()
            return insmat, errors

    def InstructionListJoints(self, mm_step=10, deg_step=5, save_to_file=None, collision_check=COLLISION_OFF, flags=0, time_step=0.1):
        """Returns a list of joints an MxN matrix, where M is the number of robot axes plus 4 columns. Linear moves are rounded according to the smoothing parameter set inside the program.

        :param float mm_step: step in mm to split the linear movements
        :param float deg_step: step in deg to split the joint movements
        :param str save_to_file: (optional) save the result to a file as Comma Separated Values (CSV). If the file name is not provided it will return the matrix. If step values are very small, the returned matrix can be very large.
        :param int collision_check: (optional) check for collisions
        :param int flags: (optional) set to 1 to include the timings between movements, set to 2 to also include the joint speeds (deg/s), set to 3 to also include the accelerations, set to 4 to include all previous information and make the splitting time-based.
        :param float time_step: (optional) set the time step in seconds for time based calculation
        :return: [message (str), joint_list (:class:`~robodk.robomath.Mat`), status (int)]

        Outputs:

        * message (str): Returns a human readable error message (if any).
        * joint_list (:class:`~robodk.robomath.Mat`): 2D matrix with all the joint information and corresponding information such as step, time stamp and speeds. Each entry is one column.
        * status (int): Status is negative if there are program issues (singularity, axis limit, targets not properly defined or collision if activated). Otherwise it returns the number of instructions that can be successfully executed.

        It also returns the list of joints as [J1, J2, ..., Jn, ERROR, MM_STEP, DEG_STEP, MOVE_ID, TIME, X,Y,Z] or the file name if a file path is provided to save the result. Default units are MM and DEG.
        Use list(:class:`~robodk.robomath.Mat`) to extract each column in a list. The ERROR is returned as an int but it needs to be interpreted as a binary number.

        .. code-block:: python
            :caption: Error bit masks

            # If error is not 0, check the binary error using the following bit masks
            error_bin = int(str(ERROR),2)
            ERROR_KINEMATIC = 0b001             # One or more points in the path is not reachable
            ERROR_PATH_LIMIT = 0b010            # The path reached a joint axis limit
            ERROR_PATH_NEARSINGULARITY = 0b1000 # The robot is too close to a wrist singularity (J5). Lower the singularity tolerance to allow the robot to continue.
            ERROR_PATH_SINGULARITY = 0b100      # The robot reached a singularity point
            ERROR_COLLISION = 0b100000          # Collision detected

        .. seealso:: :func:`~robodk.robolink.Item.ShowSequence`
        """
        with self.link._lock:
            self.link._check_connection()
            command = 'G_ProgJointList'
            self.link._send_line(command)
            self.link._send_item(self)
            self.link._send_array([mm_step, deg_step, float(collision_check), float(flags), float(time_step)])
            joint_list = save_to_file
            self.link.COM.settimeout(3600)
            if save_to_file is None:
                self.link._send_line('')
                joint_list = self.link._rec_matrix()
            else:
                self.link._send_line(save_to_file)

            error_code = self.link._rec_int()
            self.link.COM.settimeout(self.link.TIMEOUT)
            error_msg = self.link._rec_line()
            self.link._check_status()
            return error_msg, joint_list, error_code

    def getParam(self, param):
        """Get custom binary data from this item. Use setParam to set the data.

        :param str param: Parameter name

        .. seealso:: :func:`~robodk.robolink.Item.setParam`
        """
        # Setting custom binary data
        with self.link._lock:
            self.link._check_connection()
            command = 'G_ItmDataParam'
            self.link._send_line(command)
            self.link._send_item(self)
            self.link._send_line(str(param))
            data = self.link._rec_bytes()
            self.link._check_status()
            return data

    def setParam(self, param, value='', skip_result=False):
        """Set a specific item parameter.

        Select **Tools-Run Script-Show Commands** to see all available commands for items and the station.

        Note: For parameters (commands) that require a JSON string value you can also provide a dict.

        :param str param: Parameter/command name
        :param str value: Parameter value (optional, not all commands require a value). If value is bytes it will store customized data to an item given the param name.

        .. code-block:: python
            :caption: Example to expand or collapse an item in the tree

            from robodk.robolink import *
            import time
            RDK = Robolink()      # Start the RoboDK API

            # How to expand or collapse an item in the tree
            item = RDK.ItemUserPick("Select an item")

            item.setParam("Tree", "Expand")
            time.sleep(2)
            item.setParam("Tree", "Collapse")


        .. code-block:: python
            :caption: Example to change the post processor

            robot = RDK.ItemUserPick("Select a robot", ITEM_TYPE_ROBOT)

            # Set the robot post processor (name of the py file in the posts folder)
            robot.setParam("PostProcessor", "Fanuc_RJ3")


        .. code-block:: python
            :caption: Example to change display style

            # How to change the display style of an object (color as AARRGGBB):
            obj = RDK.ItemUserPick('Select an object to change the style', ITEM_TYPE_OBJECT)

            # Display points as simple dots given a certain size (suitable for fast rendering or large point clouds)
            # Color is defined as AARRGGBB
            obj.setValue('Display', 'POINTSIZE=4 COLOR=#FF771111')

            # Display each point as a cube of a given size in mm
            obj.setValue('Display','PARTICLE=CUBE(0.2,0.2,0.2) COLOR=#FF771111')

            # Another way to change display style of points to display as a sphere (size,rings):
            obj.setValue('Display','PARTICLE=SPHERE(4,8) COLOR=red')

            # Example to change the size of displayed curves:
            obj.setValue('Display','LINEW=4')

            # More examples to change the appearance of points and curves available here:
            https://github.com/RoboDK/Plug-In-Interface/tree/master/PluginAppLoader/Apps/SetStyle


        .. seealso:: :func:`~robodk.robolink.Item.getParam`, :func:`robodk.robolink.Robolink.Command`, :func:`Robolink.setParam() <robodk.robolink.Robolink.setParam>`
        """
        with self.link._lock:
            import json

            if isinstance(value, dict):
                # return dict if we provided a dict
                value = json.dumps(value)
            elif isinstance(value, bytes) and sys.version_info[0] >= 3:
                # Setting custom binary data
                self.link._check_connection()
                command = 'S_ItmDataParam'
                self.link._send_line(command)
                self.link._send_item(self)
                self.link._send_line(str(param))
                self.link._send_bytes(value)
                self.link._check_status()
                return True

            elif isinstance(value, Item):
                value = str(value.item)

            elif isinstance(value, bool):
                value = '1' if value else '0'

            elif isinstance(value, robomath.Mat):
                # Special 2D matrix write/read
                self.link._check_connection()
                command = 'G_Gen_Mat'
                self.link._send_line(command)
                self.link._send_item(self)
                self.link._send_line(str(param))
                self.link._send_matrix(value)
                self.link.COM.settimeout(3600)
                nmats = self.link._rec_int()
                self.link.COM.settimeout(self.link.TIMEOUT)
                mat2d_list = []
                if nmats == 1:
                    mat2d_list = self.link._rec_matrix()
                elif nmats == 0:
                    mat2d_list = None
                else:
                    for i in range(nmats):
                        mat2d_list.append(self.link._rec_matrix())

                self.link._check_status()
                return mat2d_list

            else:
                value = str(value)
            value = value.replace('\n', '<br>')

            self.link._check_connection()

            # Skipstatus flag has no effect here
            #skip_result = self._SkipStatus
            if skip_result:
                command = 'BlindICMD'
                self.link._send_line(command)
                self.link._send_item(self)
                self.link._send_line(str(param))
                self.link._send_line(value)
                self.link.COM.flush()
                return None

            else:
                command = 'ICMD'
                self.link._send_line(command)
                self.link._send_item(self)
                self.link._send_line(str(param))
                self.link._send_line(value)

                self.link.COM.settimeout(3600)
                line = self.link._rec_line()
                self.link.COM.settimeout(self.link.TIMEOUT)

                self.link._check_status()
                if len(value) == 0 and line.startswith("{"):
                    line = json.loads(line)

                return line


if __name__ == "__main__":

    def RoboDKInfo():
        print('=======================================')
        print('|        RoboDK API for Python        |')
        print('=======================================')
        RDK = Robolink(quit_on_close=True)
        print('')
        print('RoboDK Version: ' + RDK.Command("Version"))
        print('RoboDK License: ' + RDK.License()[0])
        print('')

    pass  # RoboDKInfo()
