# Copyright 2015-2024 - RoboDK Inc. - https://robodk.com/
# Licensed under the Apache License, Version 2.0 (the "License")
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
"""This is a robotics toolbox to facilitate operations with the RoboDK API 
and matrix (pose) operations. This toolbox includes a simple matrix class 
for pose transformations (Mat class).

This toolbox has been inspired from Peter Corke's Robotics Toolbox:
http://petercorke.com/wordpress/toolboxes/robotics-toolbox

In this module: 
pose = transformation matrix = homogeneous matrix = 4x4 matrix = Mat class

More information about the RoboDK API for Python here:

 * https://robodk.com/doc/en/RoboDK-API.html
 * https://robodk.com/doc/en/PythonAPI/robodk.html#robomath-py
 * https://robodk.com/doc/en/Add-ins.html
"""
# --------------------------------------------
import sys
import math
import time

if sys.version_info.major >= 3 and sys.version_info.minor >= 5:
    # Python 3.5+ type hints. Type hints are stripped for <3.5
    from typing import List, Union, Tuple

#----------------------------------------------------
#--------      Generic math usage     ---------------

pi: float = math.pi  #: PI


def pause(seconds: float):
    """
    Pause the execution for a specified duration.

    :param seconds: time in seconds
    :type seconds: float
    """
    time.sleep(seconds)


def sqrt(value: float) -> float:
    """
    Computes the square root of a given value.

    :param value: Value to find the square root of.
    :type value: float
    :return: Square root of the input value.
    :rtype: float
    """
    return math.sqrt(value)


def sqrtA(value: float) -> float:
    """
    Computes the square root of a value if it's positive; returns 0 for non-positive values (differs from IEEE-754).

    :param value: Value to compute the square root of.
    :type value: float
    :return: Square root of the input value if positive, otherwise 0.
    :rtype: float
    """
    if value <= 0:
        return 0
    return sqrt(value)


def sin(value: float) -> float:
    """
    Calculates the sine of an angle given in radians.

    :param value: Angle in radians.
    :type value: float
    :return: Sine of the angle.
    :rtype: float
    """
    return math.sin(value)


def cos(value: float) -> float:
    """
    Calculates the cosine of an angle given in radians.

    :param value: Angle in radians.
    :type value: float
    :return: Cosine of the angle.
    :rtype: float
    """
    return math.cos(value)


def tan(value: float) -> float:
    """
    Calculates the tangent of an angle given in radians.

    :param value: Angle in radians.
    :type value: float
    :return: Tangent of the angle.
    :rtype: float
    """
    return math.tan(value)


def asin(value: float) -> float:
    """
    Calculates the arc sine of a value, result in radians.

    :param value: Value to compute the arc sine for.
    :type value: float
    :return: Arc sine of the input value in radians.
    :rtype: float
    """
    return math.asin(value)


def acos(value: float) -> float:
    """
    Calculates the arc cosine of a value, result in radians.

    :param value: Value to compute the arc cosine for.
    :type value: float
    :return: Arc cosine of the input value in radians.
    :rtype: float
    """
    return math.acos(value)


def atan2(y: float, x: float) -> float:
    """
    Calculates the angle of a point from the origin in the XY plane.

    :param y: Y-coordinate of the point.
    :type y: float
    :param x: X-coordinate of the point.
    :type x: float
    :return: Angle of the point in radians.
    :rtype: float
    """
    return math.atan2(y, x)


def name_2_id(str_name_id: str) -> float:
    """
    Extracts the numerical ID from a string containing a named object.
    For example: "Frame 3", "Frame3", "Fram3 3" returns 3."

    :param str_name_id: String containing the named object and its ID.
    :type str_name_id: str
    :return: Numerical ID found in the string, or -1 if none found.
    :rtype: float
    """
    import re
    numbers = re.findall(r'[0-9]+', str_name_id)
    if len(numbers) > 0:
        return float(numbers[-1])
    return -1


#----------------------------------------------------
#--------     Generic matrix usage    ---------------


def rotx(rx: float) -> 'Mat':
    r"""Returns a rotation matrix around the X axis (radians)

    .. math::

        R_x(\theta) = \begin{bmatrix} 1 & 0 & 0 & 0 \\
        0 & c_\theta & -s_\theta & 0 \\
        0 & s_\theta & c_\theta & 0 \\
        0 & 0 & 0 & 1
        \end{bmatrix}

    :param rx: rotation around X axis in radians
    :type rx: float

    :rtype: :class:`.Mat`

    .. seealso:: :func:`~robodk.robomath.transl`, :func:`~robodk.robomath.roty`, :func:`~robodk.robomath.rotz`
    """
    ct = math.cos(rx)
    st = math.sin(rx)
    return Mat([
        [1, 0, 0, 0],
        [0, ct, -st, 0],
        [0, st, ct, 0],
        [0, 0, 0, 1],
    ])


def roty(ry: float) -> 'Mat':
    r"""Returns a rotation matrix around the Y axis (radians)

    .. math::

        R_y(\theta) = \begin{bmatrix} c_\theta & 0 & s_\theta & 0 \\
        0 & 1 & 0 & 0 \\
        -s_\theta & 0 & c_\theta & 0 \\
        0 & 0 & 0 & 1
        \end{bmatrix}

    :param ry: rotation around Y axis in radians
    :type ry: float

    :rtype: :class:`.Mat`

    .. seealso:: :func:`~robodk.robomath.transl`, :func:`~robodk.robomath.rotx`, :func:`~robodk.robomath.rotz`
    """
    ct = math.cos(ry)
    st = math.sin(ry)
    return Mat([
        [ct, 0, st, 0],
        [0, 1, 0, 0],
        [-st, 0, ct, 0],
        [0, 0, 0, 1],
    ])


def rotz(rz: float) -> 'Mat':
    r"""Returns a rotation matrix around the Z axis (radians)

    .. math::

        R_x(\theta) = \begin{bmatrix} c_\theta & -s_\theta & 0 & 0 \\
        s_\theta & c_\theta & 0 & 0 \\
        0 & 0 & 1 & 0 \\
        0 & 0 & 0 & 1
        \end{bmatrix}

    :param rz: rotation around Z axis in radians
    :type rz: float

    :rtype: :class:`.Mat`

    .. seealso:: :func:`~robodk.robomath.transl`, :func:`~robodk.robomath.rotx`, :func:`~robodk.robomath.roty`
    """
    ct = math.cos(rz)
    st = math.sin(rz)
    return Mat([
        [ct, -st, 0, 0],
        [st, ct, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1],
    ])


def transl(tx: Union[float, List[float]] = 0, ty: float = 0, tz: float = 0) -> 'Mat':
    r"""Returns a translation matrix (mm) given translations in each dimension.
    Supports passing inputs as a list through the tx argument, but this ignores ty and tz.

    .. math::

        T(t_x, t_y, t_z) = \begin{bmatrix} 1 & 0 & 0 & t_x \\
        0 & 1 & 0 & t_y \\
        0 & 0 & 1 & t_z \\
        0 & 0 & 0 & 1
        \end{bmatrix}

    :param tx: translation along the X axis (mm) or list of the supported parameters (i.e. [tx, ty, tz])
    :type tx: float or list of float, optional
    :param ty: translation along the Y axis (mm), defaults to 0
    :type ty: float, optional
    :param tz: translation along the Z axis (mm)
    :type tz: float, optional

    :rtype: :class:`.Mat`

    .. seealso:: :func:`~robodk.robomath.rotx`, :func:`~robodk.robomath.roty`, :func:`~robodk.robomath.rotz`
    """
    if isinstance(tx, list):
        xx = tx[0]
        yy = tx[1]
        zz = tx[2]
    else:
        xx = tx
        yy = ty
        zz = tz
    return Mat([
        [1, 0, 0, xx],
        [0, 1, 0, yy],
        [0, 0, 1, zz],
        [0, 0, 0, 1],
    ])


def RelTool(target_pose: 'Mat', x: float, y: float, z: float, rx: float = 0, ry: float = 0, rz: float = 0) -> 'Mat':
    """Calculates a relative target with respect to the tool coordinates. This procedure has exactly the same behavior as ABB's RelTool instruction.
    X,Y,Z are in mm, RX,RY,RZ are in degrees.

    :param target_pose: Reference pose
    :type target_pose: :class:`.Mat`
    :param x: translation along the Tool X axis (mm)
    :type x: float
    :param y: translation along the Tool Y axis (mm)
    :type y: float
    :param z: translation along the Tool Z axis (mm)
    :type z: float
    :param rx: rotation around the Tool X axis (deg), optional
    :type rx: float
    :param ry: rotation around the Tool Y axis (deg), optional
    :type ry: float
    :param rz: rotation around the Tool Z axis (deg), optional
    :type rz: float

    :rtype: :class:`.Mat`

    .. seealso:: :func:`~robodk.robomath.Offset`, :func:`~robodk.robomath.transl`, :func:`~robodk.robomath.rotx`, :func:`~robodk.robomath.roty`, :func:`~robodk.robomath.rotz`
    """
    if type(target_pose) != Mat:
        target_pose = target_pose.Pose()
    new_target = target_pose * transl(x, y, z) * rotx(rx * pi / 180) * roty(ry * pi / 180) * rotz(rz * pi / 180)
    return new_target


def Offset(target_pose: 'Mat', x: float, y: float, z: float, rx: float = 0, ry: float = 0, rz: float = 0) -> 'Mat':
    """Calculates a relative target with respect to the reference frame coordinates.
    X,Y,Z are in mm, RX,RY,RZ are in degrees.

    :param target_pose: Reference pose
    :type target_pose: :class:`.Mat`
    :param x: translation along the Reference X axis (mm)
    :type x: float
    :param y: translation along the Reference Y axis (mm)
    :type y: float
    :param z: translation along the Reference Z axis (mm)
    :type z: float
    :param rx: rotation around the Reference X axis (deg), optional
    :type rx: float
    :param ry: rotation around the Reference Y axis (deg), optional
    :type ry: float
    :param rz: rotation around the Reference Z axis (deg), optional
    :type rz: float

    :rtype: :class:`.Mat`

    .. seealso:: :func:`~robodk.robomath.RelTool`, :func:`~robodk.robomath.transl`, :func:`~robodk.robomath.rotx`, :func:`~robodk.robomath.roty`, :func:`~robodk.robomath.rotz`
    """
    if type(target_pose) != Mat:
        # item object assumed:
        target_pose = target_pose.Pose()
    if not target_pose.isHomogeneous():
        raise Exception(MatrixError, "Pose matrix is not homogeneous!")
    new_target = transl(x, y, z) * rotx(rx * pi / 180.0) * roty(ry * pi / 180.0) * rotz(rz * pi / 180.0) * target_pose
    return new_target


def point_Xaxis_2_pose(point: List[float], xaxis: List[float], zaxis_hint1: List[float] = [0, 0, -1], zaxis_hint2: List[float] = [0, -1, 0]) -> 'Mat':
    """Returns a pose given the origin as a point, a X axis and a preferred orientation for the Z axis"""
    pose = eye(4)
    pose.setPos(point)
    pose.setVX(xaxis)
    zaprox = zaxis_hint1
    delta = abs(angle3(xaxis, zaprox))
    if delta < 0.03 or abs(delta - pi) < 0.03:
        zaprox = zaxis_hint2
    yaxis = normalize3(cross(zaprox, xaxis))
    zaxis = cross(xaxis, yaxis)
    pose.setVY(yaxis)
    pose.setVZ(zaxis)
    return pose


def point_Yaxis_2_pose(point: List[float], yaxis: List[float], zaxis_hint1: List[float] = [0, 0, -1], zaxis_hint2: List[float] = [-1, 0, 0]) -> 'Mat':
    """Returns a pose given the origin as a point, a Y axis and a preferred orientation for the Z axis"""
    pose = eye(4)
    pose.setPos(point)
    pose.setVY(yaxis)
    zaprox = zaxis_hint1
    delta = abs(angle3(yaxis, zaprox))
    if delta < 0.03 or abs(delta - pi) < 0.03:
        zaprox = zaxis_hint2
    xaxis = normalize3(cross(yaxis, zaprox))
    zaxis = cross(xaxis, yaxis)
    pose.setVX(xaxis)
    pose.setVZ(zaxis)
    return pose


def point_Zaxis_2_pose(point: List[float], zaxis: List[float], yaxis_hint1: List[float] = [0, 0, 1], yaxis_hint2: List[float] = [0, 1, 1]) -> 'Mat':
    """Returns a pose given the origin as a point, a Z axis and a preferred orientation for the Y axis"""
    pose = eye(4)
    pose.setPos(point)
    pose.setVZ(zaxis)
    yaprox = yaxis_hint1
    delta = abs(angle3(zaxis, yaprox))
    if delta < 0.03 or abs(delta - pi) < 0.03:
        yaprox = yaxis_hint2
    xaxis = normalize3(cross(yaprox, zaxis))
    yaxis = cross(zaxis, xaxis)
    pose.setVX(xaxis)
    pose.setVY(yaxis)
    return pose


def eye(size: int = 4) -> 'Mat':
    r"""Returns the identity matrix

    .. math::

        T(t_x, t_y, t_z) = \begin{bmatrix} 1 & 0 & 0 & 0 \\
        0 & 1 & 0 & 0 \\
        0 & 0 & 1 & 0 \\
        0 & 0 & 0 & 1
        \end{bmatrix}

    :param size: square matrix size (4x4 Identity matrix by default, otherwise it is initialized to 0)
    :type size: int

    .. seealso:: :func:`~robodk.robomath.transl`, :func:`~robodk.robomath.rotx`, :func:`~robodk.robomath.roty`, :func:`~robodk.robomath.rotz`
    """
    if size == 4:
        return Mat([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1],
        ])
    else:
        newmat = Mat(size, size)
        for i in range(size):
            newmat[i, i] = 1
        return newmat


def size(matrix: 'Mat', dim: int = None) -> Union[Tuple[int, int], int]:
    """Returns the size of a matrix (m,n).
    Dim can be set to 0 to return m (rows) or 1 to return n (columns)

    :param matrix: pose
    :type matrix: :class:`.Mat`
    :param dim: dimension
    :type dim: int
    """
    return matrix.size(dim)


def tr(matrix: 'Mat') -> 'Mat':
    """Returns the transpose of the matrix

    :param matrix: pose
    :type matrix: :class:`.Mat`"""
    return matrix.tr()


def invH(matrix: 'Mat') -> 'Mat':
    """Returns the inverse of a homogeneous matrix

    :param matrix: pose
    :type matrix: :class:`.Mat`

    .. seealso:: :func:`~robodk.robomath.transl`, :func:`~robodk.robomath.rotx`, :func:`~robodk.robomath.roty`, :func:`~robodk.robomath.rotz`
    """
    return matrix.invH()


def catV(mat1: 'Mat', mat2: 'Mat') -> 'Mat':
    """Concatenate 2 matrices (vertical concatenation)"""
    return mat1.catV(mat2)


def catH(mat1: 'Mat', mat2: 'Mat') -> 'Mat':
    """Concatenate 2 matrices (horizontal concatenation)"""
    return mat1.catH(mat2)


def tic():
    """Start a stopwatch timer"""
    import time
    global TICTOC_START_TIME
    TICTOC_START_TIME = time.time()


def toc():
    """Read the stopwatch timer"""
    import time
    if 'TICTOC_START_TIME' in globals():
        elapsed = time.time() - TICTOC_START_TIME
        #print("Elapsed time is " + str(elapsed) + " seconds.")
        return elapsed
    else:
        print("Toc: start time not set")
        return -1


#----------------------------------------------------
#------ Pose to xyzrpw and xyzrpw to pose------------
def PosePP(x: float, y: float, z: float, r: float, p: float, w: float) -> 'Mat':
    """Create a pose from XYZRPW coordinates. The pose format is the one used by KUKA (XYZABC coordinates). This is function is the same as KUKA_2_Pose (with the difference that the input values are not a list). This function is used as "p" by the intermediate file when generating a robot program.

    .. seealso:: :func:`~robodk.robomath.KUKA_2_Pose`, :class:`.Mat`, :func:`~robodk.robomath.TxyzRxyz_2_Pose`, :func:`~robodk.robomath.Pose_2_TxyzRxyz`, :func:`~robodk.robomath.Pose_2_ABB`, :func:`~robodk.robomath.Pose_2_Adept`, :func:`~robodk.robomath.Pose_2_Comau`, :func:`~robodk.robomath.Pose_2_Fanuc`, :func:`~robodk.robomath.Pose_2_KUKA`, :func:`~robodk.robomath.Pose_2_Motoman`, :func:`~robodk.robomath.Pose_2_Nachi`, :func:`~robodk.robomath.Pose_2_Staubli`, :func:`~robodk.robomath.Pose_2_UR`, :func:`~robodk.robomath.quaternion_2_pose`
    """
    a = r * math.pi / 180.0
    b = p * math.pi / 180.0
    c = w * math.pi / 180.0
    ca = math.cos(a)
    sa = math.sin(a)
    cb = math.cos(b)
    sb = math.sin(b)
    cc = math.cos(c)
    sc = math.sin(c)
    return Mat([
        [cb * ca, ca * sc * sb - cc * sa, sc * sa + cc * ca * sb, x],
        [cb * sa, cc * ca + sc * sb * sa, cc * sb * sa - ca * sc, y],
        [-sb, cb * sc, cc * cb, z],
        [0.0, 0.0, 0.0, 1.0],
    ])


def pose_2_xyzrpw(H: 'Mat') -> List[float]:
    """Calculates the equivalent position (mm) and Euler angles (deg) as an [x,y,z,r,p,w] array, given a pose.
    It returns the values that correspond to the following operation:
    transl(x,y,z)*rotz(w*pi/180)*roty(p*pi/180)*rotx(r*pi/180)

    :param H: pose
    :type H: :class:`.Mat`
    :return: [x,y,z,r,p,w] in mm and deg

    .. seealso:: :class:`.Mat`, :func:`~robodk.robomath.TxyzRxyz_2_Pose`, :func:`~robodk.robomath.Pose_2_TxyzRxyz`, :func:`~robodk.robomath.Pose_2_ABB`, :func:`~robodk.robomath.Pose_2_Adept`, :func:`~robodk.robomath.Pose_2_Comau`, :func:`~robodk.robomath.Pose_2_Fanuc`, :func:`~robodk.robomath.Pose_2_KUKA`, :func:`~robodk.robomath.Pose_2_Motoman`, :func:`~robodk.robomath.Pose_2_Nachi`, :func:`~robodk.robomath.Pose_2_Staubli`, :func:`~robodk.robomath.Pose_2_UR`, :func:`~robodk.robomath.quaternion_2_pose`
    """
    x = H[0, 3]
    y = H[1, 3]
    z = H[2, 3]
    if (H[2, 0] > (1.0 - 1e-10)):
        p = -pi / 2
        r = 0
        w = math.atan2(-H[1, 2], H[1, 1])
    elif H[2, 0] < -1.0 + 1e-10:
        p = pi / 2
        r = 0
        w = math.atan2(H[1, 2], H[1, 1])
    else:
        p = math.atan2(-H[2, 0], sqrt(H[0, 0] * H[0, 0] + H[1, 0] * H[1, 0]))
        w = math.atan2(H[1, 0], H[0, 0])
        r = math.atan2(H[2, 1], H[2, 2])
    return [x, y, z, r * 180 / pi, p * 180 / pi, w * 180 / pi]


def xyzrpw_2_pose(xyzrpw: List[float]) -> 'Mat':
    """Calculates the pose from the position (mm) and Euler angles (deg), given a [x,y,z,r,p,w] array.
    The result is the same as calling: H = transl(x,y,z)*rotz(w*pi/180)*roty(p*pi/180)*rotx(r*pi/180)

    .. seealso:: :class:`.Mat`, :func:`~robodk.robomath.TxyzRxyz_2_Pose`, :func:`~robodk.robomath.Pose_2_TxyzRxyz`, :func:`~robodk.robomath.Pose_2_ABB`, :func:`~robodk.robomath.Pose_2_Adept`, :func:`~robodk.robomath.Pose_2_Comau`, :func:`~robodk.robomath.Pose_2_Fanuc`, :func:`~robodk.robomath.Pose_2_KUKA`, :func:`~robodk.robomath.Pose_2_Motoman`, :func:`~robodk.robomath.Pose_2_Nachi`, :func:`~robodk.robomath.Pose_2_Staubli`, :func:`~robodk.robomath.Pose_2_UR`, :func:`~robodk.robomath.quaternion_2_pose`
    """
    [x, y, z, r, p, w] = xyzrpw
    a = r * pi / 180
    b = p * pi / 180
    c = w * pi / 180
    ca = math.cos(a)
    sa = math.sin(a)
    cb = math.cos(b)
    sb = math.sin(b)
    cc = math.cos(c)
    sc = math.sin(c)
    H = Mat([
        [cb * cc, cc * sa * sb - ca * sc, sa * sc + ca * cc * sb, x],
        [cb * sc, ca * cc + sa * sb * sc, ca * sb * sc - cc * sa, y],
        [-sb, cb * sa, ca * cb, z],
        [0, 0, 0, 1],
    ])
    return H


def Pose(x: float, y: float, z: float, rxd: float, ryd: float, rzd: float) -> 'Mat':
    """Returns the pose (:class:`.Mat`) given the position (mm) and Euler angles (deg) as an array [x,y,z,rx,ry,rz].
    The result is the same as calling: H = transl(x,y,z)*rotx(rx*pi/180)*roty(ry*pi/180)*rotz(rz*pi/180)
    This pose format is printed for homogeneous poses automatically. This Pose is the same representation used by Mecademic or Staubli robot controllers.

    :param tx: position (X coordinate)
    :type tx: float
    :param ty: position (Y coordinate)
    :type ty: float
    :param tz: position (Z coordinate)
    :type tz: float
    :param rxd: first rotation in deg (X coordinate)
    :type rxd: float
    :param ryd: first rotation in deg (Y coordinate)
    :type ryd: float
    :param rzd: first rotation in deg (Z coordinate)
    :type rzd: float

    .. seealso:: :class:`.Mat`, :func:`~robodk.robomath.TxyzRxyz_2_Pose`, :func:`~robodk.robomath.Pose_2_TxyzRxyz`
    """
    rx = rxd * pi / 180
    ry = ryd * pi / 180
    rz = rzd * pi / 180
    srx = math.sin(rx)
    crx = math.cos(rx)
    sry = math.sin(ry)
    cry = math.cos(ry)
    srz = math.sin(rz)
    crz = math.cos(rz)
    return Mat([
        [cry * crz, -cry * srz, sry, x],
        [crx * srz + crz * srx * sry, crx * crz - srx * sry * srz, -cry * srx, y],
        [srx * srz - crx * crz * sry, crz * srx + crx * sry * srz, crx * cry, z],
        [0, 0, 0, 1],
    ])


def TxyzRxyz_2_Pose(xyzrpw: List[float]) -> 'Mat':
    """Returns the pose given the position (mm) and Euler angles (rad) as an array [x,y,z,rx,ry,rz].
    The result is the same as calling: H = transl(x,y,z)*rotx(rx)*roty(ry)*rotz(rz)

    :param xyzrpw: [x,y,z,rx,ry,rz] in mm and radians
    :type xyzrpw: list of float

    .. seealso:: :class:`.Mat`, :func:`~robodk.robomath.TxyzRxyz_2_Pose`, :func:`~robodk.robomath.Pose_2_TxyzRxyz`, :func:`~robodk.robomath.Pose_2_ABB`, :func:`~robodk.robomath.Pose_2_Adept`, :func:`~robodk.robomath.Pose_2_Comau`, :func:`~robodk.robomath.Pose_2_Fanuc`, :func:`~robodk.robomath.Pose_2_KUKA`, :func:`~robodk.robomath.Pose_2_Motoman`, :func:`~robodk.robomath.Pose_2_Nachi`, :func:`~robodk.robomath.Pose_2_Staubli`, :func:`~robodk.robomath.Pose_2_UR`, :func:`~robodk.robomath.quaternion_2_pose`
    """
    [x, y, z, rx, ry, rz] = xyzrpw
    srx = math.sin(rx)
    crx = math.cos(rx)
    sry = math.sin(ry)
    cry = math.cos(ry)
    srz = math.sin(rz)
    crz = math.cos(rz)
    H = Mat([
        [cry * crz, -cry * srz, sry, x],
        [crx * srz + crz * srx * sry, crx * crz - srx * sry * srz, -cry * srx, y],
        [srx * srz - crx * crz * sry, crz * srx + crx * sry * srz, crx * cry, z],
        [0, 0, 0, 1],
    ])
    return H


def Pose_2_TxyzRxyz(H: 'Mat') -> List[float]:
    """Retrieve the position (mm) and Euler angles (rad) as an array [x,y,z,rx,ry,rz] given a pose.
    It returns the values that correspond to the following operation:
    H = transl(x,y,z)*rotx(rx)*roty(ry)*rotz(rz).

    :param H: pose
    :type H: :class:`.Mat`

    .. seealso:: :class:`.Mat`, :func:`~robodk.robomath.TxyzRxyz_2_Pose`, :func:`~robodk.robomath.Pose_2_TxyzRxyz`, :func:`~robodk.robomath.Pose_2_ABB`, :func:`~robodk.robomath.Pose_2_Adept`, :func:`~robodk.robomath.Pose_2_Comau`, :func:`~robodk.robomath.Pose_2_Fanuc`, :func:`~robodk.robomath.Pose_2_KUKA`, :func:`~robodk.robomath.Pose_2_Motoman`, :func:`~robodk.robomath.Pose_2_Nachi`, :func:`~robodk.robomath.Pose_2_Staubli`, :func:`~robodk.robomath.Pose_2_UR`, :func:`~robodk.robomath.quaternion_2_pose`
    """
    x = H[0, 3]
    y = H[1, 3]
    z = H[2, 3]
    a = H[0, 0]
    b = H[0, 1]
    c = H[0, 2]
    d = H[1, 2]
    e = H[2, 2]
    if c > (1.0 - 1e-10):
        ry1 = pi / 2
        rx1 = 0
        rz1 = atan2(H[1, 0], H[1, 1])
    elif c < (-1.0 + 1e-10):
        ry1 = -pi / 2
        rx1 = 0
        rz1 = atan2(H[1, 0], H[1, 1])
    else:
        sy = c
        cy1 = +sqrt(1 - sy * sy)
        sx1 = -d / cy1
        cx1 = e / cy1
        sz1 = -b / cy1
        cz1 = a / cy1
        rx1 = atan2(sx1, cx1)
        ry1 = atan2(sy, cy1)
        rz1 = atan2(sz1, cz1)
    return [x, y, z, rx1, ry1, rz1]


def Pose_2_Staubli(H: 'Mat') -> List[float]:
    """Converts a pose (4x4 matrix) to a Staubli XYZWPR target

    :param H: pose
    :type H: :class:`.Mat`

    .. seealso:: :class:`.Mat`, :func:`~robodk.robomath.TxyzRxyz_2_Pose`, :func:`~robodk.robomath.Pose_2_TxyzRxyz`, :func:`~robodk.robomath.Pose_2_ABB`, :func:`~robodk.robomath.Pose_2_Adept`, :func:`~robodk.robomath.Pose_2_Comau`, :func:`~robodk.robomath.Pose_2_Fanuc`, :func:`~robodk.robomath.Pose_2_KUKA`, :func:`~robodk.robomath.Pose_2_Motoman`, :func:`~robodk.robomath.Pose_2_Nachi`, :func:`~robodk.robomath.Staubli_2_Pose`, :func:`~robodk.robomath.Pose_2_UR`, :func:`~robodk.robomath.quaternion_2_pose`
    """
    xyzwpr = Pose_2_TxyzRxyz(H)
    xyzwpr[3] = xyzwpr[3] * 180.0 / pi
    xyzwpr[4] = xyzwpr[4] * 180.0 / pi
    xyzwpr[5] = xyzwpr[5] * 180.0 / pi
    return xyzwpr


def Staubli_2_Pose(xyzwpr: List[float]) -> 'Mat':
    """Converts a Staubli XYZWPR target to a pose (4x4 matrix)

    :param H: pose
    :type H: :class:`.Mat`

    .. seealso:: :class:`.Mat`, :func:`~robodk.robomath.TxyzRxyz_2_Pose`, :func:`~robodk.robomath.Pose_2_TxyzRxyz`, :func:`~robodk.robomath.Pose_2_ABB`, :func:`~robodk.robomath.Pose_2_Adept`, :func:`~robodk.robomath.Pose_2_Comau`, :func:`~robodk.robomath.Pose_2_Fanuc`, :func:`~robodk.robomath.Pose_2_KUKA`, :func:`~robodk.robomath.Pose_2_Motoman`, :func:`~robodk.robomath.Pose_2_Nachi`, :func:`~robodk.robomath.Pose_2_Staubli`, :func:`~robodk.robomath.Pose_2_UR`, :func:`~robodk.robomath.quaternion_2_pose`
    """
    xyzwpr[3] = xyzwpr[3] * pi / 180.0
    xyzwpr[4] = xyzwpr[4] * pi / 180.0
    xyzwpr[5] = xyzwpr[5] * pi / 180.0
    return TxyzRxyz_2_Pose(xyzwpr)


def Pose_2_Motoman(H: 'Mat') -> List[float]:
    """Converts a pose (4x4 matrix) to a Motoman XYZWPR target (mm and deg)

    :param H: pose
    :type H: :class:`.Mat`

    .. seealso:: :class:`.Mat`, :func:`~robodk.robomath.TxyzRxyz_2_Pose`, :func:`~robodk.robomath.Pose_2_TxyzRxyz`, :func:`~robodk.robomath.Pose_2_ABB`, :func:`~robodk.robomath.Pose_2_Adept`, :func:`~robodk.robomath.Pose_2_Comau`, :func:`~robodk.robomath.Pose_2_Fanuc`, :func:`~robodk.robomath.Pose_2_KUKA`, :func:`~robodk.robomath.Pose_2_Motoman`, :func:`~robodk.robomath.Pose_2_Nachi`, :func:`~robodk.robomath.Pose_2_Staubli`, :func:`~robodk.robomath.Pose_2_UR`, :func:`~robodk.robomath.quaternion_2_pose`
    """
    xyzwpr = pose_2_xyzrpw(H)
    return xyzwpr


def Pose_2_Fanuc(H: 'Mat') -> List[float]:
    """Converts a pose (4x4 matrix) to a Fanuc XYZWPR target (mm and deg)

    :param H: pose
    :type H: :class:`.Mat`

    .. seealso:: :class:`.Mat`, :func:`~robodk.robomath.TxyzRxyz_2_Pose`, :func:`~robodk.robomath.Pose_2_TxyzRxyz`, :func:`~robodk.robomath.Pose_2_ABB`, :func:`~robodk.robomath.Pose_2_Adept`, :func:`~robodk.robomath.Pose_2_Comau`, :func:`~robodk.robomath.Pose_2_Fanuc`, :func:`~robodk.robomath.Pose_2_KUKA`, :func:`~robodk.robomath.Pose_2_Motoman`, :func:`~robodk.robomath.Pose_2_Nachi`, :func:`~robodk.robomath.Pose_2_Staubli`, :func:`~robodk.robomath.Pose_2_UR`, :func:`~robodk.robomath.quaternion_2_pose`
    """
    xyzwpr = pose_2_xyzrpw(H)
    return xyzwpr


def Pose_2_Techman(H: 'Mat') -> List[float]:
    """Converts a pose (4x4 matrix) to a Techman XYZWPR target (mm and deg)

    :param H: pose
    :type H: :class:`.Mat`

    .. seealso:: :class:`.Mat`, :func:`~robodk.robomath.TxyzRxyz_2_Pose`, :func:`~robodk.robomath.Pose_2_TxyzRxyz`, :func:`~robodk.robomath.Pose_2_ABB`, :func:`~robodk.robomath.Pose_2_Adept`, :func:`~robodk.robomath.Pose_2_Comau`, :func:`~robodk.robomath.Pose_2_Fanuc`, :func:`~robodk.robomath.Pose_2_KUKA`, :func:`~robodk.robomath.Pose_2_Motoman`, :func:`~robodk.robomath.Pose_2_Nachi`, :func:`~robodk.robomath.Pose_2_Staubli`, :func:`~robodk.robomath.Pose_2_UR`, :func:`~robodk.robomath.quaternion_2_pose`
    """
    xyzwpr = pose_2_xyzrpw(H)
    return xyzwpr


def Motoman_2_Pose(xyzwpr: List[float]) -> 'Mat':
    """Converts a Motoman target to a pose (4x4 matrix)

    .. seealso:: :class:`.Mat`, :func:`~robodk.robomath.TxyzRxyz_2_Pose`, :func:`~robodk.robomath.Pose_2_TxyzRxyz`, :func:`~robodk.robomath.Pose_2_ABB`, :func:`~robodk.robomath.Pose_2_Adept`, :func:`~robodk.robomath.Pose_2_Comau`, :func:`~robodk.robomath.Pose_2_Fanuc`, :func:`~robodk.robomath.Pose_2_KUKA`, :func:`~robodk.robomath.Pose_2_Motoman`, :func:`~robodk.robomath.Pose_2_Nachi`, :func:`~robodk.robomath.Pose_2_Staubli`, :func:`~robodk.robomath.Pose_2_UR`, :func:`~robodk.robomath.quaternion_2_pose`
    """
    return xyzrpw_2_pose(xyzwpr)


def Fanuc_2_Pose(xyzwpr: List[float]) -> 'Mat':
    """Converts a Fanuc target to a pose (4x4 matrix)

    .. seealso:: :class:`.Mat`, :func:`~robodk.robomath.TxyzRxyz_2_Pose`, :func:`~robodk.robomath.Pose_2_TxyzRxyz`, :func:`~robodk.robomath.Pose_2_ABB`, :func:`~robodk.robomath.Pose_2_Adept`, :func:`~robodk.robomath.Pose_2_Comau`, :func:`~robodk.robomath.Pose_2_Fanuc`, :func:`~robodk.robomath.Pose_2_KUKA`, :func:`~robodk.robomath.Pose_2_Motoman`, :func:`~robodk.robomath.Pose_2_Nachi`, :func:`~robodk.robomath.Pose_2_Staubli`, :func:`~robodk.robomath.Pose_2_UR`, :func:`~robodk.robomath.quaternion_2_pose`
    """
    return xyzrpw_2_pose(xyzwpr)


def Techman_2_Pose(xyzwpr: List[float]) -> 'Mat':
    """Converts a Techman target to a pose (4x4 matrix)

    .. seealso:: :class:`.Mat`, :func:`~robodk.robomath.TxyzRxyz_2_Pose`, :func:`~robodk.robomath.Pose_2_TxyzRxyz`, :func:`~robodk.robomath.Pose_2_ABB`, :func:`~robodk.robomath.Pose_2_Adept`, :func:`~robodk.robomath.Pose_2_Comau`, :func:`~robodk.robomath.Pose_2_Fanuc`, :func:`~robodk.robomath.Pose_2_KUKA`, :func:`~robodk.robomath.Pose_2_Motoman`, :func:`~robodk.robomath.Pose_2_Nachi`, :func:`~robodk.robomath.Pose_2_Staubli`, :func:`~robodk.robomath.Pose_2_UR`, :func:`~robodk.robomath.quaternion_2_pose`
    """
    return xyzrpw_2_pose(xyzwpr)


def Pose_2_KUKA(H: 'Mat') -> List[float]:
    """Converts a pose (4x4 matrix) to an XYZABC KUKA target (Euler angles), required by KUKA KRC controllers.

    :param H: pose
    :type H: :class:`.Mat`

    .. seealso:: :class:`.Mat`, :func:`~robodk.robomath.TxyzRxyz_2_Pose`, :func:`~robodk.robomath.Pose_2_TxyzRxyz`, :func:`~robodk.robomath.Pose_2_ABB`, :func:`~robodk.robomath.Pose_2_Adept`, :func:`~robodk.robomath.Pose_2_Comau`, :func:`~robodk.robomath.Pose_2_Fanuc`, :func:`~robodk.robomath.Pose_2_KUKA`, :func:`~robodk.robomath.Pose_2_Motoman`, :func:`~robodk.robomath.Pose_2_Nachi`, :func:`~robodk.robomath.Pose_2_Staubli`, :func:`~robodk.robomath.Pose_2_UR`, :func:`~robodk.robomath.quaternion_2_pose`
    """
    x = H[0, 3]
    y = H[1, 3]
    z = H[2, 3]
    if (H[2, 0]) > (1.0 - 1e-10):
        p = -pi / 2
        r = 0
        w = atan2(-H[1, 2], H[1, 1])
    elif (H[2, 0]) < (-1.0 + 1e-10):
        p = pi / 2
        r = 0
        w = atan2(H[1, 2], H[1, 1])
    else:
        p = atan2(-H[2, 0], sqrt(H[0, 0] * H[0, 0] + H[1, 0] * H[1, 0]))
        w = atan2(H[1, 0], H[0, 0])
        r = atan2(H[2, 1], H[2, 2])
    return [x, y, z, w * 180 / pi, p * 180 / pi, r * 180 / pi]


def KUKA_2_Pose(xyzrpw: List[float]) -> 'Mat':
    """Converts a KUKA XYZABC target to a pose (4x4 matrix), required by KUKA KRC controllers.

    .. seealso:: :class:`.Mat`, :func:`~robodk.robomath.TxyzRxyz_2_Pose`, :func:`~robodk.robomath.Pose_2_TxyzRxyz`, :func:`~robodk.robomath.Pose_2_ABB`, :func:`~robodk.robomath.Pose_2_Adept`, :func:`~robodk.robomath.Pose_2_Comau`, :func:`~robodk.robomath.Pose_2_Fanuc`, :func:`~robodk.robomath.Pose_2_KUKA`, :func:`~robodk.robomath.Pose_2_Motoman`, :func:`~robodk.robomath.Pose_2_Nachi`, :func:`~robodk.robomath.Pose_2_Staubli`, :func:`~robodk.robomath.Pose_2_UR`, :func:`~robodk.robomath.quaternion_2_pose`
    """
    [x, y, z, r, p, w] = xyzrpw
    a = r * math.pi / 180.0
    b = p * math.pi / 180.0
    c = w * math.pi / 180.0
    ca = math.cos(a)
    sa = math.sin(a)
    cb = math.cos(b)
    sb = math.sin(b)
    cc = math.cos(c)
    sc = math.sin(c)
    return Mat([
        [cb * ca, ca * sc * sb - cc * sa, sc * sa + cc * ca * sb, x],
        [cb * sa, cc * ca + sc * sb * sa, cc * sb * sa - ca * sc, y],
        [-sb, cb * sc, cc * cb, z],
        [0.0, 0.0, 0.0, 1.0],
    ])


def Adept_2_Pose(xyzrpw: List[float]) -> 'Mat':
    """Converts an Adept XYZRPW target to a pose (4x4 matrix)

    .. seealso:: :class:`.Mat`, :func:`~robodk.robomath.TxyzRxyz_2_Pose`, :func:`~robodk.robomath.Pose_2_TxyzRxyz`, :func:`~robodk.robomath.Pose_2_ABB`, :func:`~robodk.robomath.Pose_2_Adept`, :func:`~robodk.robomath.Pose_2_Comau`, :func:`~robodk.robomath.Pose_2_Fanuc`, :func:`~robodk.robomath.Pose_2_KUKA`, :func:`~robodk.robomath.Pose_2_Motoman`, :func:`~robodk.robomath.Pose_2_Nachi`, :func:`~robodk.robomath.Pose_2_Staubli`, :func:`~robodk.robomath.Pose_2_UR`, :func:`~robodk.robomath.quaternion_2_pose`
    """
    [x, y, z, r, p, w] = xyzrpw
    a = r * math.pi / 180.0
    b = p * math.pi / 180.0
    c = w * math.pi / 180.0
    ca = math.cos(a)
    sa = math.sin(a)
    cb = math.cos(b)
    sb = math.sin(b)
    cc = math.cos(c)
    sc = math.sin(c)
    return Mat([
        [ca * cb * cc - sa * sc, -cc * sa - ca * cb * sc, ca * sb, x],
        [ca * sc + cb * cc * sa, ca * cc - cb * sa * sc, sa * sb, y],
        [-cc * sb, sb * sc, cb, z],
        [0.0, 0.0, 0.0, 1.0],
    ])


def Pose_2_Adept(H: 'Mat') -> List[float]:
    """Converts a pose to an Adept target

    :param H: pose
    :type H: :class:`.Mat`

    .. seealso:: :class:`.Mat`, :func:`~robodk.robomath.TxyzRxyz_2_Pose`, :func:`~robodk.robomath.Pose_2_TxyzRxyz`, :func:`~robodk.robomath.Pose_2_ABB`, :func:`~robodk.robomath.Pose_2_Adept`, :func:`~robodk.robomath.Pose_2_Comau`, :func:`~robodk.robomath.Pose_2_Fanuc`, :func:`~robodk.robomath.Pose_2_KUKA`, :func:`~robodk.robomath.Pose_2_Motoman`, :func:`~robodk.robomath.Pose_2_Nachi`, :func:`~robodk.robomath.Pose_2_Staubli`, :func:`~robodk.robomath.Pose_2_UR`, :func:`~robodk.robomath.quaternion_2_pose`
    """
    x = H[0, 3]
    y = H[1, 3]
    z = H[2, 3]
    if H[2, 2] > (1.0 - 1e-10):
        r = 0
        p = 0
        w = atan2(H[1, 0], H[0, 0])
    elif H[2, 2] < (-1.0 + 1e-10):
        r = 0
        p = pi
        w = atan2(H[1, 0], H[1, 1])
    else:
        cb = H[2, 2]
        sb = +sqrt(1 - cb * cb)
        sc = H[2, 1] / sb
        cc = -H[2, 0] / sb
        sa = H[1, 2] / sb
        ca = H[0, 2] / sb
        r = atan2(sa, ca)
        p = atan2(sb, cb)
        w = atan2(sc, cc)
    return [x, y, z, r * 180 / pi, p * 180 / pi, w * 180 / pi]


def Pose_2_Catia(H: 'Mat') -> List[float]:
    """Converts a pose to Catia or Solidworks format, in mm and deg. It returns the values that correspond to the following operation:
    H = transl(x,y,z)*rotz(a)*rotx(b)*rotz(c).

    :param H: pose
    :type H: :class:`.Mat`

    .. seealso:: :class:`.Mat`, :func:`~robodk.robomath.TxyzRxyz_2_Pose`, :func:`~robodk.robomath.Pose_2_TxyzRxyz`, :func:`~robodk.robomath.Pose_2_ABB`, :func:`~robodk.robomath.Pose_2_Adept`, :func:`~robodk.robomath.Pose_2_Comau`, :func:`~robodk.robomath.Pose_2_Fanuc`, :func:`~robodk.robomath.Pose_2_KUKA`, :func:`~robodk.robomath.Pose_2_Motoman`, :func:`~robodk.robomath.Pose_2_Nachi`, :func:`~robodk.robomath.Pose_2_Staubli`, :func:`~robodk.robomath.Pose_2_UR`, :func:`~robodk.robomath.quaternion_2_pose`
    """
    x = H[0, 3]
    y = H[1, 3]
    z = H[2, 3]
    if H[2, 2] > (1.0 - 1e-10):
        r = 0
        p = 0
        w = atan2(H[1, 0], H[0, 0])
    elif H[2, 2] < (-1.0 + 1e-10):
        r = 0
        p = pi
        w = atan2(H[1, 0], H[0, 0])
    else:
        r = atan2(H[0, 2], -H[1, 2])
        p = atan2(sqrt(H[0, 2] * H[0, 2] + H[1, 2] * H[1, 2]), H[2, 2])
        w = atan2(H[2, 0], H[2, 1])

    return [x, y, z, r * 180 / pi, p * 180 / pi, w * 180 / pi]


def Comau_2_Pose(xyzrpw: List[float]) -> 'Mat':
    """Converts a Comau XYZRPW target to a pose (4x4 matrix), the same representation required by PDL Comau programs.

    .. seealso:: :class:`.Mat`, :func:`~robodk.robomath.TxyzRxyz_2_Pose`, :func:`~robodk.robomath.Pose_2_TxyzRxyz`, :func:`~robodk.robomath.Pose_2_ABB`, :func:`~robodk.robomath.Pose_2_Adept`, :func:`~robodk.robomath.Pose_2_Comau`, :func:`~robodk.robomath.Pose_2_Fanuc`, :func:`~robodk.robomath.Pose_2_KUKA`, :func:`~robodk.robomath.Pose_2_Motoman`, :func:`~robodk.robomath.Pose_2_Nachi`, :func:`~robodk.robomath.Pose_2_Staubli`, :func:`~robodk.robomath.Pose_2_UR`, :func:`~robodk.robomath.quaternion_2_pose`
    """
    return Adept_2_Pose(xyzrpw)


def Pose_2_Comau(H: 'Mat') -> List[float]:
    """Converts a pose to a Comau target, the same representation required by PDL Comau programs.

    :param H: pose
    :type H: :class:`.Mat`

    .. seealso:: :class:`.Mat`, :func:`~robodk.robomath.TxyzRxyz_2_Pose`, :func:`~robodk.robomath.Pose_2_TxyzRxyz`, :func:`~robodk.robomath.Pose_2_ABB`, :func:`~robodk.robomath.Pose_2_Adept`, :func:`~robodk.robomath.Pose_2_Comau`, :func:`~robodk.robomath.Pose_2_Fanuc`, :func:`~robodk.robomath.Pose_2_KUKA`, :func:`~robodk.robomath.Pose_2_Motoman`, :func:`~robodk.robomath.Pose_2_Nachi`, :func:`~robodk.robomath.Pose_2_Staubli`, :func:`~robodk.robomath.Pose_2_UR`, :func:`~robodk.robomath.quaternion_2_pose`"""
    return Pose_2_Adept(H)


def Pose_2_Nachi(pose: 'Mat') -> List[float]:
    """Converts a pose to a Nachi XYZRPW target

    :param pose: pose
    :type pose: :class:`.Mat`

    .. seealso:: :class:`.Mat`, :func:`~robodk.robomath.TxyzRxyz_2_Pose`, :func:`~robodk.robomath.Pose_2_TxyzRxyz`, :func:`~robodk.robomath.Pose_2_ABB`, :func:`~robodk.robomath.Pose_2_Adept`, :func:`~robodk.robomath.Pose_2_Comau`, :func:`~robodk.robomath.Pose_2_Fanuc`, :func:`~robodk.robomath.Pose_2_KUKA`, :func:`~robodk.robomath.Pose_2_Motoman`, :func:`~robodk.robomath.Pose_2_Nachi`, :func:`~robodk.robomath.Pose_2_Staubli`, :func:`~robodk.robomath.Pose_2_UR`, :func:`~robodk.robomath.quaternion_2_pose`
    """
    [x, y, z, r, p, w] = pose_2_xyzrpw(pose)
    return [x, y, z, w, p, r]


def Nachi_2_Pose(xyzwpr: List[float]) -> 'Mat':
    """Converts a Nachi XYZRPW target to a pose (4x4 matrix)

    .. seealso:: :class:`.Mat`, :func:`~robodk.robomath.TxyzRxyz_2_Pose`, :func:`~robodk.robomath.Pose_2_TxyzRxyz`, :func:`~robodk.robomath.Pose_2_ABB`, :func:`~robodk.robomath.Pose_2_Adept`, :func:`~robodk.robomath.Pose_2_Comau`, :func:`~robodk.robomath.Pose_2_Fanuc`, :func:`~robodk.robomath.Pose_2_KUKA`, :func:`~robodk.robomath.Pose_2_Motoman`, :func:`~robodk.robomath.Pose_2_Nachi`, :func:`~robodk.robomath.Pose_2_Staubli`, :func:`~robodk.robomath.Pose_2_UR`, :func:`~robodk.robomath.quaternion_2_pose`
    """
    return xyzrpw_2_pose(xyzwpr)


def pose_2_quaternion(Ti: 'Mat') -> List[float]:
    """Returns the quaternion orientation vector of a pose (4x4 matrix)

    :param Ti: pose
    :type Ti: :class:`.Mat`

    .. seealso:: :class:`.Mat`, :func:`~robodk.robomath.TxyzRxyz_2_Pose`, :func:`~robodk.robomath.Pose_2_TxyzRxyz`, :func:`~robodk.robomath.Pose_2_ABB`, :func:`~robodk.robomath.Pose_2_Adept`, :func:`~robodk.robomath.Pose_2_Comau`, :func:`~robodk.robomath.Pose_2_Fanuc`, :func:`~robodk.robomath.Pose_2_KUKA`, :func:`~robodk.robomath.Pose_2_Motoman`, :func:`~robodk.robomath.Pose_2_Nachi`, :func:`~robodk.robomath.Pose_2_Staubli`, :func:`~robodk.robomath.Pose_2_UR`, :func:`~robodk.robomath.quaternion_2_pose`
    """
    TOLERANCE_0 = 1e-9
    TOLERANCE_180 = 1e-7

    cosangle = min(max(((Ti[0, 0] + Ti[1, 1] + Ti[2, 2] - 1.0) * 0.5), -1.0), 1.0)  # Calculate the rotation angle
    if cosangle > 1.0 - TOLERANCE_0:
        # Identity matrix
        q1 = 1.0
        q2 = 0.0
        q3 = 0.0
        q4 = 0.0

    elif cosangle < -1.0 + TOLERANCE_180:
        # 180 rotation around an axis
        diag = [Ti[0, 0], Ti[1, 1], Ti[2, 2]]
        k = diag.index(max(diag))
        col = [Ti[0, k], Ti[1, k], Ti[2, k]]
        col[k] = col[k] + 1.0
        rotvector = [n / sqrtA(2.0 * (1.0 + diag[k])) for n in col]

        q1 = 0.0
        q2 = rotvector[0]
        q3 = rotvector[1]
        q4 = rotvector[2]

    else:
        # No edge case, normal calculation
        a = Ti[0, 0]
        b = Ti[1, 1]
        c = Ti[2, 2]
        sign2 = 1.0
        sign3 = 1.0
        sign4 = 1.0
        if Ti[2, 1] - Ti[1, 2] < 0.0:
            sign2 = -1.0
        if Ti[0, 2] - Ti[2, 0] < 0.0:
            sign3 = -1.0
        if Ti[1, 0] - Ti[0, 1] < 0.0:
            sign4 = -1.0
        q1 = sqrt(max(a + b + c + 1.0, 0.0)) / 2.0
        q2 = sign2 * sqrt(max(a - b - c + 1.0, 0.0)) / 2.0
        q3 = sign3 * sqrt(max(-a + b - c + 1.0, 0.0)) / 2.0
        q4 = sign4 * sqrt(max(-a - b + c + 1.0, 0.0)) / 2.0

    return [q1, q2, q3, q4]


def Pose_Split(pose1: 'Mat', pose2: 'Mat', delta_mm: float = 1.0) -> 'Mat':
    """Create a sequence of poses that transitions from pose1 to pose2 by steps of delta_mm in mm (the first and last pose are not included in the list)"""
    pose_delta = invH(pose1) * pose2
    distance = norm(pose_delta.Pos())
    if distance <= delta_mm:
        return [pose2]

    pose_list = []

    x, y, z, w, p, r = Pose_2_UR(pose_delta)

    steps = max(1, int(distance / delta_mm))

    xd = x / steps
    yd = y / steps
    zd = z / steps
    wd = w / steps
    pd = p / steps
    rd = r / steps
    for i in range(steps - 1):
        factor = i + 1
        pose_list.append(pose1 * UR_2_Pose([xd * factor, yd * factor, zd * factor, wd * factor, pd * factor, rd * factor]))

    return pose_list


def quaternion_2_pose(qin: List[float]) -> 'Mat':
    """Returns the pose orientation matrix (4x4 matrix) given a quaternion orientation vector

    :param qin: quaternions as 4 float values
    :type qin: list

    .. seealso:: :class:`.Mat`, :func:`~robodk.robomath.TxyzRxyz_2_Pose`, :func:`~robodk.robomath.Pose_2_TxyzRxyz`, :func:`~robodk.robomath.Pose_2_ABB`, :func:`~robodk.robomath.Pose_2_Adept`, :func:`~robodk.robomath.Pose_2_Comau`, :func:`~robodk.robomath.Pose_2_Fanuc`, :func:`~robodk.robomath.Pose_2_KUKA`, :func:`~robodk.robomath.Pose_2_Motoman`, :func:`~robodk.robomath.Pose_2_Nachi`, :func:`~robodk.robomath.Pose_2_Staubli`, :func:`~robodk.robomath.Pose_2_UR`, :func:`~robodk.robomath.quaternion_2_pose`
    """
    qnorm = sqrt(qin[0] * qin[0] + qin[1] * qin[1] + qin[2] * qin[2] + qin[3] * qin[3])
    q = qin
    q[0] = q[0] / qnorm
    q[1] = q[1] / qnorm
    q[2] = q[2] / qnorm
    q[3] = q[3] / qnorm
    pose = Mat([
        [1 - 2 * q[2] * q[2] - 2 * q[3] * q[3], 2 * q[1] * q[2] - 2 * q[3] * q[0], 2 * q[1] * q[3] + 2 * q[2] * q[0], 0],
        [2 * q[1] * q[2] + 2 * q[3] * q[0], 1 - 2 * q[1] * q[1] - 2 * q[3] * q[3], 2 * q[2] * q[3] - 2 * q[1] * q[0], 0],
        [2 * q[1] * q[3] - 2 * q[2] * q[0], 2 * q[2] * q[3] + 2 * q[1] * q[0], 1 - 2 * q[1] * q[1] - 2 * q[2] * q[2], 0],
        [0, 0, 0, 1],
    ])
    return pose


def Pose_2_ABB(H: 'Mat') -> List[float]:
    """Converts a pose to an ABB target (using quaternion representation).

    :param H: pose
    :type H: :class:`.Mat`

    .. seealso:: :class:`.Mat`, :func:`~robodk.robomath.TxyzRxyz_2_Pose`, :func:`~robodk.robomath.Pose_2_TxyzRxyz`, :func:`~robodk.robomath.Pose_2_ABB`, :func:`~robodk.robomath.Pose_2_Adept`, :func:`~robodk.robomath.Pose_2_Comau`, :func:`~robodk.robomath.Pose_2_Fanuc`, :func:`~robodk.robomath.Pose_2_KUKA`, :func:`~robodk.robomath.Pose_2_Motoman`, :func:`~robodk.robomath.Pose_2_Nachi`, :func:`~robodk.robomath.Pose_2_Staubli`, :func:`~robodk.robomath.Pose_2_UR`, :func:`~robodk.robomath.quaternion_2_pose`
    """
    q = pose_2_quaternion(H)
    return [H[0, 3], H[1, 3], H[2, 3], q[0], q[1], q[2], q[3]]


def print_pose_ABB(pose: 'Mat'):
    """Displays an ABB RAPID target (the same way it is displayed in IRC5 controllers).

    :param pose: pose
    :type pose: :class:`.Mat`

    .. seealso:: :class:`.Mat`, :func:`~robodk.robomath.TxyzRxyz_2_Pose`, :func:`~robodk.robomath.Pose_2_TxyzRxyz`, :func:`~robodk.robomath.Pose_2_ABB`, :func:`~robodk.robomath.Pose_2_Adept`, :func:`~robodk.robomath.Pose_2_Comau`, :func:`~robodk.robomath.Pose_2_Fanuc`, :func:`~robodk.robomath.Pose_2_KUKA`, :func:`~robodk.robomath.Pose_2_Motoman`, :func:`~robodk.robomath.Pose_2_Nachi`, :func:`~robodk.robomath.Pose_2_Staubli`, :func:`~robodk.robomath.Pose_2_UR`, :func:`~robodk.robomath.quaternion_2_pose`
    """
    q = pose_2_quaternion(pose)
    print('[[%.3f,%.3f,%.3f],[%.6f,%.6f,%.6f,%.6f]]' % (pose[0, 3], pose[1, 3], pose[2, 3], q[0], q[1], q[2], q[3]))


def Pose_2_UR(pose: 'Mat') -> List[float]:
    """Calculate the p[x,y,z,u,v,w] position with rotation vector for a pose target. This is the same format required by Universal Robot controllers.

    .. seealso:: :class:`.Mat`, :func:`~robodk.robomath.TxyzRxyz_2_Pose`, :func:`~robodk.robomath.Pose_2_TxyzRxyz`, :func:`~robodk.robomath.Pose_2_ABB`, :func:`~robodk.robomath.Pose_2_Adept`, :func:`~robodk.robomath.Pose_2_Comau`, :func:`~robodk.robomath.Pose_2_Fanuc`, :func:`~robodk.robomath.Pose_2_KUKA`, :func:`~robodk.robomath.Pose_2_Motoman`, :func:`~robodk.robomath.Pose_2_Nachi`, :func:`~robodk.robomath.Pose_2_Staubli`, :func:`~robodk.robomath.Pose_2_UR`, :func:`~robodk.robomath.quaternion_2_pose`
    """
    NUMERIC_TOLERANCE = 1e-8

    def saturate_1(value: float) -> float:
        return min(max(value, -1.0), 1.0)

    angle = acos(saturate_1((pose[0, 0] + pose[1, 1] + pose[2, 2] - 1) * 0.5))
    rxyz = [pose[2, 1] - pose[1, 2], pose[0, 2] - pose[2, 0], pose[1, 0] - pose[0, 1]]
    if angle < NUMERIC_TOLERANCE:
        rxyz = [0, 0, 0]
    else:
        sin_angle = sin(angle)
        if abs(sin_angle) < NUMERIC_TOLERANCE or norm(rxyz) < NUMERIC_TOLERANCE:
            d3 = [pose[0, 0], pose[1, 1], pose[2, 2]]
            mx = max(d3)
            mx_id = d3.index(mx)
            if mx_id == 0:
                rxyz = [pose[0, 0] + 1, pose[1, 0], pose[2, 0]]
            elif mx_id == 1:
                rxyz = [pose[0, 1], pose[1, 1] + 1, pose[2, 1]]
            else:
                rxyz = [pose[0, 2], pose[1, 2], pose[2, 2] + 1]

            rxyz = mult3(rxyz, angle / (sqrt(max(0, 2 * (1 + mx)))))
        else:
            rxyz = normalize3(rxyz)
            rxyz = mult3(rxyz, angle)
    return [pose[0, 3], pose[1, 3], pose[2, 3], rxyz[0], rxyz[1], rxyz[2]]


def UR_2_Pose(xyzwpr: List[float]) -> 'Mat':
    """Calculate the pose target given a p[x,y,z,u,v,w] cartesian target with rotation vector. This is the same format required by Universal Robot controllers.

    .. seealso:: :class:`.Mat`, :func:`~robodk.robomath.TxyzRxyz_2_Pose`
    """
    x, y, z, w, p, r = xyzwpr
    wpr = [w, p, r]
    angle = norm(wpr)
    cosang = cos(0.5 * angle)

    if angle == 0.0:
        q234 = [0.0, 0.0, 0.0]
    else:
        ratio = sin(0.5 * angle) / angle
        q234 = mult3(wpr, ratio)

    q1234 = [cosang, q234[0], q234[1], q234[2]]
    pose = quaternion_2_pose(q1234)
    pose.setPos([x, y, z])
    return pose


#----------------------------------------------------
#-------- ROBOT MODEL (D-H and D-H M) ---------------


def dh(rz: float, tx: float = None, tz: float = None, rx: float = None) -> 'Mat':
    """Returns the Denavit-Hartenberg 4x4 matrix for a robot link.
    calling dh(rz,tx,tz,rx) is the same as using rotz(rz)*transl(tx,0,tz)*rotx(rx)
    calling dh(rz,tx,tz,rx) is the same as calling dh([rz,tx,tz,rx])
    """
    if tx is None:
        [rz, tx, tz, rx] = rz

    crx = math.cos(rx)
    srx = math.sin(rx)
    crz = math.cos(rz)
    srz = math.sin(rz)
    return Mat([
        [crz, -srz * crx, srz * srx, tx * crz],
        [srz, crz * crx, -crz * srx, tx * srz],
        [0, srx, crx, tz],
        [0, 0, 0, 1],
    ])


def dhm(rx: float, tx: float = None, tz: float = None, rz: float = None) -> 'Mat':
    """Returns the Denavit-Hartenberg Modified 4x4 matrix for a robot link (Craig 1986).

    calling dhm(rx,tx,tz,rz) is the same as using rotx(rx)*transl(tx,0,tz)*rotz(rz)

    calling dhm(rx,tx,tz,rz) is the same as calling dhm([rx,tx,tz,rz])
    """
    if tx is None:
        [rx, tx, tz, rz] = rx

    crx = math.cos(rx)
    srx = math.sin(rx)
    crz = math.cos(rz)
    srz = math.sin(rz)
    return Mat([
        [crz, -srz, 0, tx],
        [crx * srz, crx * crz, -srx, -tz * srx],
        [srx * srz, crz * srx, crx, tz * crx],
        [0, 0, 0, 1],
    ])


def joints_2_angles(jin: List[float], type: int) -> List[float]:
    """Converts the robot encoders into angles between links depending on the type of the robot."""
    jout = jin
    if type == 2:
        jout[2] = -jin[1] - jin[2]
        jout[3] = -jin[3]
        jout[4] = -jin[4]
        jout[5] = -jin[5]
    elif type == 3:
        jout[2] = -jin[2]
        jout[3] = -jin[3]
        jout[4] = -jin[4]
        jout[5] = -jin[5]
    elif type == 4:
        jout[2] = +jin[1] + jin[2]
    elif type == 11:
        jout[2] = -jin[1] - jin[2]
        jout[0] = -jin[0]
        jout[3] = -jin[3]
        jout[5] = -jin[5]
    return jout


def angles_2_joints(jin: List[float], type: int) -> List[float]:
    """Converts the angles between links into the robot motor space depending on the type of the robot."""
    jout = jin
    if type == 2:
        jout[2] = -jin[1] - jin[2]
        jout[3] = -jin[3]
        jout[4] = -jin[4]
        jout[5] = -jin[5]
    elif type == 3:
        jout[2] = -jin[2]
        jout[3] = -jin[3]
        jout[4] = -jin[4]
        jout[5] = -jin[5]
    elif type == 11:
        jout[2] = -jin[1] - jin[2]
        jout[0] = -jin[0]
        jout[3] = -jin[3]
        jout[5] = -jin[5]
    return jout


#----------------------------------------------------
#-------- Useful geometric tools ---------------


def norm(p: List[float]) -> float:
    """Returns the norm of a 3D vector"""
    return sqrt(p[0] * p[0] + p[1] * p[1] + p[2] * p[2])


def normalize3(a: List[float]) -> List[float]:
    """Returns the unitary vector"""
    norminv = 1.0 / norm(a)
    return [a[0] * norminv, a[1] * norminv, a[2] * norminv]


def cross(a: List[float], b: List[float]) -> List[float]:
    """Returns the cross product of two 3D vectors"""
    c = [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]
    return c


def dot(a: List[float], b: List[float]) -> List[float]:
    """Returns the dot product of two 3D vectors"""
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def angle3(a: List[float], b: List[float]) -> float:
    """Returns the angle in radians of two 3D vectors"""
    cos_angle = dot(normalize3(a), normalize3(b))
    cos_angle = min(1.0, max(-1.0, cos_angle))
    return acos(cos_angle)


def pose_angle(pose: 'Mat') -> float:
    """Returns the angle in radians of a 4x4 matrix pose

    :param pose: pose
    :type pose: :class:`.Mat`"""
    cos_ang = (pose[0, 0] + pose[1, 1] + pose[2, 2] - 1) / 2
    cos_ang = min(max(cos_ang, -1), 1)
    return acos(cos_ang)


def pose_angle_between(pose1: 'Mat', pose2: 'Mat') -> float:
    """Returns the angle in radians between two poses (4x4 matrix pose)"""
    return pose_angle(invH(pose1) * pose2)


def mult3(v: List[float], d: List[float]) -> List[float]:
    """Multiplies a 3D vector to a scalar"""
    return [v[0] * d, v[1] * d, v[2] * d]


def subs3(a: List[float], b: List[float]) -> List[float]:
    """Subtracts two 3D vectors c=a-b"""
    return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]


def add3(a: List[float], b: List[float]) -> List[float]:
    """Adds two 3D vectors c=a+b"""
    return [a[0] + b[0], a[1] + b[1], a[2] + b[2]]


def distance(a: List[float], b: List[float]) -> float:
    """Calculates the distance between two points"""
    return norm(subs3(a, b))


def pose_is_similar(a: List[float], b: List[float], tolerance: float = 0.1) -> bool:
    """Check if the pose is similar. Returns True if both poses are less than 0.1 mm or 0.1 deg appart. Optionally provide the tolerance in mm+deg"""
    if distance(a.Pos(), b.Pos()) + pose_angle_between(a, b) * 180 / pi < tolerance:
        return True
    return False


def intersect_line_2_plane(pline: List[float], vline: List[float], pplane: List[float], vplane: List[float]) -> List[float]:
    """Calculates the intersection betweeen a line and a plane"""
    D = -dot(vplane, pplane)
    k = -(D + dot(vplane, pline)) / dot(vplane, vline)
    p = add3(pline, mult3(vline, k))
    return p


def proj_pt_2_plane(point: List[float], planepoint: List[float], planeABC: List[float]) -> List[float]:
    """Projects a point to a plane"""
    return intersect_line_2_plane(point, planeABC, planepoint, planeABC)


def proj_pt_2_line(point: List[float], paxe: List[float], vaxe: List[float]) -> List[float]:
    """Projects a point to a line"""
    vpaxe2point = subs3(point, paxe)
    dist = dot(vaxe, vpaxe2point) / dot(vaxe, vaxe)
    return add3(paxe, mult3(vaxe, dist))


def fitPlane(points: List[List[float]]) -> Tuple[List[float], List[float]]:
    """Returns the equation and normal for a best fit plane to a cloud of points.

    Uses singular value decomposition to produce a least squares fit to a plane. Points must have centroid at [0, 0, 0]. Must provide at least 4 points.

    :param points: a 3xN array of points. Each column represents one point.
    :type points: array-like
    :type array_like:

    :return: pplane: the equation of the best-fit plane, in the form b(1)*X + b(2)*Y +b(3)*Z + b(4) = 0.
    :rtype: array_like
    :return: vplane: the normal vector of the best-fit plane.
    :rtype: list of floats
    """
    import numpy as np
    XYZ = np.array(points)
    [rows, cols] = XYZ.shape
    # Set up constraint equations of the form  AB = 0,
    # where B is a column vector of the plane coefficients
    # in the form b(1)*X + b(2)*Y +b(3)*Z + b(4) = 0.
    p = (np.ones((rows, 1)))
    AB = np.hstack([XYZ, p])
    [u, d, v] = np.linalg.svd(AB, 0)
    B = v[3, :]  # Solution is last column of v.
    nn = np.linalg.norm(B[0:3])
    B = B / nn
    #pplane = [0, 0, -(B[3] / B[2])]
    pplane = np.average(XYZ, 0)
    vplane = B[0:3].tolist()
    return pplane, vplane


#----------------------------------------------------
#--------       Mat matrix class      ---------------


class MatrixError(Exception):
    """ An exception class for Matrix """
    pass


class Mat(object):
    """Mat is a matrix object. The main purpose of this object is to represent a pose in the 3D space (position and orientation).

    A pose is a 4x4 matrix that represents the position and orientation of one reference frame with respect to another one, in the 3D space.

    Poses are commonly used in robotics to place objects, reference frames and targets with respect to each other.

    .. seealso:: :func:`~robodk.robomath.TxyzRxyz_2_Pose`, :func:`~robodk.robomath.Pose_2_TxyzRxyz`, :func:`~robodk.robomath.Pose_2_ABB`, :func:`~robodk.robomath.Pose_2_Adept`, :func:`~robodk.robomath.Adept_2_Pose`, :func:`~robodk.robomath.Pose_2_Comau`, :func:`~robodk.robomath.Pose_2_Fanuc`, :func:`~robodk.robomath.Pose_2_KUKA`, :func:`~robodk.robomath.KUKA_2_Pose`, :func:`~robodk.robomath.Pose_2_Motoman`, :func:`~robodk.robomath.Pose_2_Nachi`, :func:`~robodk.robomath.Pose_2_Staubli`, :func:`~robodk.robomath.Pose_2_UR`, :func:`~robodk.robomath.quaternion_2_pose`

    Example:

        .. code-block:: python

            from robodk.robolink import *           # import the robolink library
            from robodk.robomath import *           # import the robomath library

            RDK = Robolink()                        # connect to the RoboDK API
            robot  = RDK.Item('', ITEM_TYPE_ROBOT)  # Retrieve a robot available in RoboDK
            #target  = RDK.Item('Target 1')         # Retrieve a target (example)


            pose = robot.Pose()                     # retrieve the current robot position as a pose (position of the active tool with respect to the active reference frame)
            # target = target.Pose()                # the same can be applied to targets (taught position)

            # Read the 4x4 pose matrix as [X,Y,Z , A,B,C] Euler representation (mm and deg): same representation as KUKA robots
            XYZABC = Pose_2_KUKA(pose)
            print(XYZABC)

            # Read the 4x4 pose matrix as [X,Y,Z, q1,q2,q3,q4] quaternion representation (position in mm and orientation in quaternion): same representation as ABB robots (RAPID programming)
            xyzq1234 = Pose_2_ABB(pose)
            print(xyzq1234)

            # Read the 4x4 pose matrix as [X,Y,Z, u,v,w] representation (position in mm and orientation vector in radians): same representation as Universal Robots
            xyzuvw = Pose_2_UR(pose)
            print(xyzuvw)

            x,y,z,a,b,c = XYZABC                    # Use the KUKA representation (for example) and calculate a new pose based on the previous pose
            XYZABC2 = [x,y,z+50,a,b,c+45]
            pose2 = KUKA_2_Pose(XYZABC2)            # Convert the XYZABC array to a pose (4x4 matrix)

            robot.MoveJ(pose2)                      # Make a joint move to the new position
            # target.setPose(pose2)                  # We can also update the pose to targets, tools, reference frames, objects, ...
    """

    def __init__(self, rows: Union[int, List[List[float]], 'Mat'] = None, ncols: int = None):
        """
        Initializes a new instance of the Mat class.

        :param rows: Number of rows, a 2D list representing the matrix, or another Mat instance to clone.
        :type rows: int or List[List[float]] or Mat
        :param ncols: Number of columns (required if rows is an integer).
        :type ncols: int
        """
        if ncols is None:
            if rows is None:
                m = 4
                n = 4
                self.rows = [[0] * n for x in range(m)]
            else:
                if isinstance(rows, Mat):
                    rows = rows.copy().rows
                m = len(rows)
                transpose = 0
                if isinstance(rows, list) and len(rows) == 0:
                    # Check empty matrix
                    self.rows = [[]]
                    n = 0
                    return

                if not isinstance(rows[0], list):
                    rows = [rows]
                    transpose = 1

                n = len(rows[0])
                if any([len(row) != n for row in rows[1:]]):  # Validity check
                    #raise Exception(MatrixError, "inconsistent row length")
                    # make the size uniform (fill blanks with zeros)
                    n = max([len(i) for i in rows])
                    for row in rows:
                        row += [0] * (n - len(row))

                self.rows = rows
                if transpose:
                    self.rows = [list(item) for item in zip(*self.rows)]
        else:
            m = max(rows, 0)
            n = max(ncols, 0)
            if m == 0:
                m = 1
                n = 0

            self.rows = [[0] * n for x in range(m)]

    def __iter__(self):
        if self.size(0) == 0 or self.size(1) == 0:
            return iter([])
        return iter(self.tr().rows)

    def copy(self) -> 'Mat':
        """
        Creates a deep copy of the matrix.

        :return: A new instance of Mat that is a copy of this instance.
        :rtype: Mat
        """
        sz = self.size()
        newmat = Mat(sz[0], sz[1])
        for i in range(sz[0]):
            for j in range(sz[1]):
                newmat[i, j] = self[i, j]
        return newmat

    def fromNumpy(ndarray) -> 'Mat':
        """Convert a numpy array to a Mat matrix"""
        return Mat(ndarray.tolist())

    def toNumpy(self):
        """Return a copy of the Mat matrix as a numpy array"""
        import numpy
        return numpy.asarray(self.rows, float)

    def __len__(self) -> int:
        """Return the number of columns"""
        return len(self.rows[0])

    def ColsCount(self) -> int:
        """Return the number of coumns. Same as len().

        .. seealso:: :func:`~Mat.Cols`, :func:`~Mat.Rows`, :func:`~Mat.RowsCount`
        """
        return len(self.rows[0])

    def RowsCount(self) -> int:
        """Return the number of rows

        .. seealso:: :func:`~Mat.Cols`, :func:`~Mat.Rows`, :func:`~Mat.ColsCount`

        """
        return len(self.rows)

    def Cols(self) -> List[List[float]]:
        """Retrieve the matrix as a list of columns (list of list of float).

        .. seealso:: :func:`~Mat.Rows`, :func:`~Mat.ColsCount`, :func:`~Mat.RowsCount`

        Example:

            .. code-block:: python

                >>> transl(10,20,30).Rows()
                [[1, 0, 0, 10], [0, 1, 0, 20], [0, 0, 1, 30], [0, 0, 0, 1]]

                >>> transl(10,20,30).Cols()
                [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [10, 20, 30, 1]]
        """
        return self.tr().rows

    def Rows(self) -> List[List[float]]:
        """Get the matrix as a list of lists

        .. seealso:: :func:`~Mat.Cols`, :func:`~Mat.ColsCount`, :func:`~Mat.RowsCount`
        """
        return self.rows

    def Col(self, n: int) -> List[float]:
        """"Get the Column n from the matrix"""
        return self.tr().rows[n]

    def Row(self, n: int) -> List[float]:
        """"Get the Row n from the matrix"""
        return self.rows[n]

    def __getitem__(self, idx: Union[int, slice, Tuple[slice, slice]]) -> 'Mat':
        if isinstance(idx, int):  #integer A[1]
            return tr(Mat(self.rows[idx]))
        elif isinstance(idx, slice):  #one slice: A[1:3]
            return Mat(self.rows[idx])
        else:  #two slices: A[1:3,1:3]
            idx1 = idx[0]
            idx2 = idx[1]
            if isinstance(idx1, int) and isinstance(idx2, int):
                return self.rows[idx1][idx2]
            matsize = self.size()
            if isinstance(idx1, slice):
                indices1 = idx1.indices(matsize[0])
                rg1 = range(*indices1)
            else:  #is int
                rg1 = range(idx1, idx1 + 1)
            if isinstance(idx2, slice):
                indices2 = idx2.indices(matsize[1])
                rg2 = range(*indices2)
            else:  #is int
                rg2 = range(idx2, idx2 + 1)
            #newm = int(abs((rg1.stop-rg1.start)/rg1.step))
            #newn = int(abs((rg2.stop-rg2.start)/rg2.step))
            newm = rg1
            newn = rg2
            newmat = Mat(len(newm), len(newn))
            cm = 0
            for i in rg1:
                cn = 0
                for j in rg2:
                    newmat.rows[cm][cn] = self.rows[i][j]
                    cn = cn + 1
                cm = cm + 1
            return newmat

    def __setitem__(self, idx, item):
        if isinstance(item, float) or isinstance(item, int):
            item = Mat([[item]])
        elif isinstance(item, list):
            item = Mat(item)

        matsize = self.size()
        if isinstance(idx, int):  #integer A[1]
            idx1 = idx
            idx2 = 0
            #raise Exception(MatrixError, "Cannot set item. Use [i,:] instead.")
            #self.rows[idx] = item
        elif isinstance(idx, slice):  #one slice: A[1:3]
            # raise Exception(MatrixError, "Cannot set item. Use [a:b,:] instead.")
            idx1 = idx
            idx2 = 0
        else:
            idx1 = idx[0]
            idx2 = idx[1]

        # at this point we have two slices: example A[1:3,1:3]
        if isinstance(idx1, slice):
            indices1 = idx1.indices(matsize[0])
            rg1 = range(*indices1)
        else:  #is int
            rg1 = range(idx1, idx1 + 1)
        if isinstance(idx2, slice):
            indices2 = idx2.indices(matsize[1])
            rg2 = range(*indices2)
        else:  #is int
            rg2 = range(idx2, idx2 + 1)
        #newm = int(abs((rg1.stop-rg1.start)/rg1.step))
        #newn = int(abs((rg2.stop-rg2.start)/rg2.step))
        newm = rg1
        newn = rg2
        itmsz = item.size()
        if len(newm) != itmsz[0] or len(newn) != itmsz[1]:
            raise Exception(MatrixError, "Submatrix indices does not match the new matrix sizes", itmsz[0], "x", itmsz[1], "<-", newm, "x", newn)
        #newmat = Mat(newm,newn)
        cm = 0
        for i in rg1:
            cn = 0
            for j in rg2:
                self.rows[i][j] = item.rows[cm][cn]
                cn = cn + 1
            cm = cm + 1

    def __str__(self) -> str:
        #s='\n [ '.join([(', '.join([str(item) for item in row])+' ],') for row in self.rows])
        str_add = ''
        if self.isHomogeneous():
            x, y, z, rx, ry, rz = Pose_2_TxyzRxyz(self)
            str_add = 'Pose(%.3f, %.3f, %.3f,  %.3f, %.3f, %.3f):\n' % (x, y, z, rx * 180 / pi, ry * 180 / pi, rz * 180 / pi)

        s = '\n [ '.join([(', '.join([('%.3f' % item if type(item) == float else str(item)) for item in row]) + ' ],') for row in self.rows])
        return str_add + '[[ ' + s[:-1] + ']\n'

    def __repr__(self) -> str:
        s = str(self)
        rank = str(self.size())
        rep = "Matrix: %s\n%s" % (rank, s)
        return rep

    def tr(self) -> 'Mat':
        """Returns the transpose of the matrix"""
        if len(self.rows) == 0 or len(self.rows[0]) == 0:
            return Mat(0, 0)
        # mat = Mat([list(item) for item in zip(*self.rows)])
        mat = Mat(list(map(list, zip(*self.rows))))
        return mat

    def size(self, dim: int = None) -> Union[int, Tuple[int, int]]:
        """
        Returns the size of the matrix.

        :param dim: Optional. If specified, returns the size of the specified dimension (0 for rows, 1 for columns).
        :type dim: int
        :return: The size of the matrix as a tuple (rows, columns), or the size of the specified dimension.
        """
        m = len(self.rows)
        if m > 0:
            n = len(self.rows[0])
        else:
            n = 0

        if dim is None:
            return (m, n)
        elif dim == 0:
            return m
        elif dim == 1:
            return n
        else:
            raise Exception(MatrixError, "Invalid dimension!")

    def catV(self, mat2: 'Mat') -> 'Mat':
        """Concatenate with another matrix (vertical concatenation)"""
        if not isinstance(mat2, Mat):
            #raise Exception(MatrixError, "Concatenation must be performed with 2 matrices")
            return self.catH(Mat(mat2).tr())

        sz1 = self.size()
        sz2 = mat2.size()
        if sz1[1] != sz2[1]:
            raise Exception(MatrixError, "Horizontal size of matrices does not match")

        newmat = Mat(sz1[0] + sz2[0], sz1[1])
        newmat[0:sz1[0], :] = self
        newmat[sz1[0]:, :] = mat2
        return newmat

    def catH(self, mat2: 'Mat') -> 'Mat':
        """Concatenate with another matrix (horizontal concatenation)"""
        if not isinstance(mat2, Mat):
            #raise Exception(MatrixError, "Concatenation must be performed with 2 matrices")
            return self.catH(Mat(mat2))

        sz1 = self.size()
        sz2 = mat2.size()
        if sz1[0] != sz2[0]:
            raise Exception(MatrixError, "Horizontal size of matrices does not match")

        newmat = Mat(sz1[0], sz1[1] + sz2[1])
        newmat[:, :sz1[1]] = self
        newmat[:, sz1[1]:] = mat2
        return newmat

    def __eq__(self, other: 'Mat') -> bool:
        """Test equality"""
        if other is None:
            return False
        #return (other.rows == self.rows)
        return pose_is_similar(other, self)

    def __ne__(self, other: 'Mat') -> bool:
        return not (self == other)

    def __add__(self, mat: 'Mat') -> 'Mat':
        """Add a matrix to this matrix and
        return the new matrix. It doesn't modify
        the current matrix"""
        if isinstance(mat, int) or isinstance(mat, float):
            m, n = self.size()
            result = Mat(m, n)
            for x in range(m):
                for y in range(n):
                    result.rows[x][y] = self.rows[x][y] + mat
            return result
        sz = self.size()
        m = sz[0]
        n = sz[1]
        ret = Mat(m, n)
        if sz != mat.size():
            raise Exception(MatrixError, "Can not add matrices of sifferent sizes!")
        for x in range(m):
            row = [sum(item) for item in zip(self.rows[x], mat.rows[x])]
            ret.rows[x] = row
        return ret

    def __sub__(self, mat: 'Mat') -> 'Mat':
        """Subtract a matrix from this matrix and
        return the new matrix. It doesn't modify
        the current matrix"""
        if isinstance(mat, int) or isinstance(mat, float):
            m, n = self.size()
            result = Mat(m, n)
            for x in range(m):
                for y in range(n):
                    result.rows[x][y] = self.rows[x][y] - mat
            return result
        sz = self.size()
        m = sz[0]
        n = sz[1]
        ret = Mat(m, n)
        if sz != mat.size():
            raise Exception(MatrixError, "Can not subtract matrices of sifferent sizes!")
        for x in range(m):
            row = [item[0] - item[1] for item in zip(self.rows[x], mat.rows[x])]
            ret.rows[x] = row
        return ret

    def __mul__(self, mat: 'Mat') -> 'Mat':
        """Multiply a matrix with this matrix and
        return the new matrix. It doesn't modify
        the current matrix"""
        if isinstance(mat, int) or isinstance(mat, float):
            m, n = self.size()
            mulmat = Mat(m, n)
            for x in range(m):
                for y in range(n):
                    mulmat.rows[x][y] = self.rows[x][y] * mat
            return mulmat
        if isinstance(mat, list):  #case of a matrix times a vector
            szvect = len(mat)
            m = self.size(0)
            matvect = Mat(mat)
            if szvect + 1 == m:
                vectok = catV(matvect, Mat([[1]]))
                result = self * vectok
                return (result[:-1, :]).tr().rows[0]
            elif szvect == m:
                result = self * Mat(matvect)
                return result.tr().rows[0]
            else:
                raise Exception(MatrixError, "Invalid product")
        else:
            matm, matn = mat.size()
            m, n = self.size()
            if (n != matm):
                raise Exception(MatrixError, "Matrices cannot be multipled (unexpected size)!")
            mat_t = mat.tr()
            mulmat = Mat(m, matn)
            for x in range(m):
                for y in range(mat_t.size(0)):
                    mulmat.rows[x][y] = sum([item[0] * item[1] for item in zip(self.rows[x], mat_t.rows[y])])
            return mulmat

    def eye(self, m: int = 4) -> 'Mat':
        """Make identity matrix of size (mxm)"""
        rows = [[0] * m for x in range(m)]
        idx = 0
        for row in rows:
            row[idx] = 1
            idx += 1
        return Mat(rows)

    def isHomogeneous(self) -> bool:
        """
        Checks if the matrix is a homogeneous transformation matrix (4x4).

        :return: True if the matrix is homogeneous, False otherwise.
        :rtype: bool
        """
        m, n = self.size()
        if m != 4 or n != 4:
            return False
        #if self[3,:] != Mat([[0.0,0.0,0.0,1.0]]):
        #    return False
        test = self[0:3, 0:3]
        test = test * test.tr()
        test[0, 0] = test[0, 0] - 1.0
        test[1, 1] = test[1, 1] - 1.0
        test[2, 2] = test[2, 2] - 1.0
        zero = 0.0
        for x in range(3):
            for y in range(3):
                zero = zero + abs(test[x, y])
        if zero > 1e-4:
            return False
        return True

    def RelTool(self, x: float, y: float, z: float, rx: float = 0, ry: float = 0, rz: float = 0) -> 'Mat':
        """Calculates a relative target with respect to the tool coordinates. This procedure has exactly the same behavior as ABB's RelTool instruction.
        X,Y,Z are in mm, RX,RY,RZ are in degrees.

        :param x: translation along the Tool X axis (mm)
        :type x: float
        :param y: translation along the Tool Y axis (mm)
        :type y: float
        :param z: translation along the Tool Z axis (mm)
        :type z: float
        :param rx: rotation around the Tool X axis (deg) (optional)
        :type rx: float
        :param ry: rotation around the Tool Y axis (deg) (optional)
        :type ry: float
        :param rz: rotation around the Tool Z axis (deg) (optional)
        :type rz: float

        .. seealso:: :func:`~Mat.Offset`
        """
        return RelTool(self, x, y, z, rx, ry, rz)

    def Offset(self, x: float, y: float, z: float, rx: float = 0, ry: float = 0, rz: float = 0) -> 'Mat':
        """Calculates a relative target with respect to this pose.
        X,Y,Z are in mm, RX,RY,RZ are in degrees.

        :param x: translation along the Reference X axis (mm)
        :type x: float
        :param y: translation along the Reference Y axis (mm)
        :type y: float
        :param z: translation along the Reference Z axis (mm)
        :type z: float
        :param rx: rotation around the Reference X axis (deg) (optional)
        :type rx: float
        :param ry: rotation around the Reference Y axis (deg) (optional)
        :type ry: float
        :param rz: rotation around the Reference Z axis (deg) (optional)
        :type rz: float

        .. seealso:: :func:`~Mat.RelTool`
        """
        return Offset(self, x, y, z, rx, ry, rz)

    def invH(self) -> 'Mat':
        """
        Returns the inverse of the matrix. Assumes the matrix is homogeneous.

        :return: The inverse of the matrix.
        :rtype: Mat
        :raises MatrixError: If the matrix is not homogeneous.
        """
        if not self.isHomogeneous():
            raise Exception(MatrixError, "Pose matrix is not homogeneous. invH() can only compute the inverse of a homogeneous matrix")
        Hout = self.tr()
        Hout[3, 0:3] = Mat([[0, 0, 0]])
        Hout[0:3, 3] = (Hout[0:3, 0:3] * self[0:3, 3]) * (-1)
        return Hout

    def inv(self) -> 'Mat':
        """
        Returns the inverse of the matrix. Assumes the matrix is homogeneous.

        :return: The inverse of the matrix.
        :rtype: Mat
        """
        return self.invH()

    def tolist(self) -> List[float]:
        """Returns the first column of the matrix as a list"""
        return self.tr().rows[0]

    def list(self) -> List[float]:
        """Returns the first column of the matrix as a list"""
        return self.tr().rows[0]

    def list2(self) -> list:
        """Returns the matrix as list of lists (one list per column)"""
        return self.tr().rows

    def Pos(self) -> List[float]:
        """
        Extracts the translation part of a homogeneous transformation matrix.

        :return: The translation vector [X, Y, Z].
        :rtype: List[float]
        """
        # return self[0:3, 3].tolist()
        return [self.rows[0][3], self.rows[1][3], self.rows[2][3]]

    def VX(self) -> List[float]:
        """
        Extracts the X-axis vector from a homogeneous transformation matrix.

        :return: The X-axis vector [Xx, Xy, Xz].
        :rtype: List[float]
        """
        # return self[0:3, 0].tolist()
        return [self.rows[0][0], self.rows[1][0], self.rows[2][0]]

    def VY(self) -> List[float]:
        """
        Extracts the Y-axis vector from a homogeneous transformation matrix.

        :return: The Y-axis vector [Yx, Yy, Yz].
        :rtype: List[float]
        """
        # return self[0:3, 1].tolist()
        return [self.rows[0][1], self.rows[1][1], self.rows[2][1]]

    def VZ(self) -> List[float]:
        """
        Extracts the Z-axis vector from a homogeneous transformation matrix.

        :return: The Z-axis vector [Zx, Zy, Zz].
        :rtype: List[float]
        """
        # return self[0:3, 2].tolist()
        return [self.rows[0][2], self.rows[1][2], self.rows[2][2]]

    def Rot33(self):
        """Returns the sub 3x3 rotation matrix"""
        return self[0:3, 0:3]

    def setPos(self, newpos: Union[List[float], 'Mat']) -> 'Mat':
        """
        Sets the translation part of a homogeneous transformation matrix.

        :param newpos: The new translation vector [X, Y, Z].
        :type newpos: List[float] or Mat
        :return: The matrix after setting the new position.
        :rtype: Mat
        """
        if type(newpos) == Mat:
            newpos = list(newpos)[0]

        self.rows[0][3] = newpos[0]
        self.rows[1][3] = newpos[1]
        self.rows[2][3] = newpos[2]
        return self

    def setVX(self, v_xyz: Union[List[float], 'Mat']) -> 'Mat':
        """
        Sets the X-axis vector of a homogeneous transformation matrix.

        :param v_xyz: The new X-axis vector [Xx, Xy, Xz].
        :type v_xyz: List[float] or Mat
        :return: The matrix after setting the new X-axis vector.
        :rtype: Mat
        """
        if type(v_xyz) == Mat:
            v_xyz = list(v_xyz)[0]

        v_xyz = normalize3(v_xyz)
        self.rows[0][0] = v_xyz[0]
        self.rows[1][0] = v_xyz[1]
        self.rows[2][0] = v_xyz[2]
        return self

    def setVY(self, v_xyz: Union[List[float], 'Mat']) -> 'Mat':
        """
        Sets the Y-axis vector of a homogeneous transformation matrix.

        :param v_xyz: The new Y-axis vector [Yx, Yy, Yz].
        :type v_xyz: List[float] or Mat
        :return: The matrix after setting the new Y-axis vector.
        :rtype: Mat
        """
        if type(v_xyz) == Mat:
            v_xyz = list(v_xyz)[0]

        v_xyz = normalize3(v_xyz)
        self.rows[0][1] = v_xyz[0]
        self.rows[1][1] = v_xyz[1]
        self.rows[2][1] = v_xyz[2]
        return self

    def setVZ(self, v_xyz: Union[List[float], 'Mat']) -> 'Mat':
        """
        Sets the Z-axis vector of a homogeneous transformation matrix.

        :param v_xyz: The new Z-axis vector [Zx, Zy, Zz].
        :type v_xyz: List[float] or Mat
        :return: The matrix after setting the new Z-axis vector.
        :rtype: Mat
        """
        if type(v_xyz) == Mat:
            v_xyz = list(v_xyz)[0]

        v_xyz = normalize3(v_xyz)
        self.rows[0][2] = v_xyz[0]
        self.rows[1][2] = v_xyz[1]
        self.rows[2][2] = v_xyz[2]
        return self

    def translationPose(self) -> 'Mat':
        """Return the translation pose of this matrix. The rotation returned is set to identity (assumes that a 4x4 homogeneous matrix is being used)"""
        return transl(self.Pos())

    def rotationPose(self) -> 'Mat':
        """Return the rotation pose of this matrix. The position returned is set to [0,0,0] (assumes that a 4x4 homogeneous matrix is being used)"""
        mat_rotation = Mat(self)
        mat_rotation.setPos([0, 0, 0])
        return mat_rotation

    def SaveCSV(self, strfile: str):
        """Save the :class:`.Mat` Matrix to a CSV (Comma Separated Values) file. The file can be easily opened as a spreadsheet such as Excel.

        .. seealso:: :func:`~Mat.SaveMat`, :func:`~robodk.robomath.SaveList`, :func:`~robodk.robomath.LoadList`, :func:`~robodk.robomath.LoadMat`
        """
        self.tr().SaveMat(strfile)

    def SaveMat(self, strfile: str, separator: str = ','):
        """Save the :class:`.Mat` Matrix to a CSV or TXT file

        .. seealso:: :func:`~Mat.SaveCSV`, :func:`~robodk.robomath.SaveList`, :func:`~robodk.robomath.LoadList`, :func:`~robodk.robomath.LoadMat`
        """
        sz = self.size()
        m = sz[0]
        n = sz[1]
        file = open(strfile, 'w')
        for j in range(n):
            for i in range(m):
                file.write(('%.6f' + separator) % self.rows[i][j])
            file.write('\n')
        file.close()


if __name__ == "__main__":
    pass
