' 25/09/2017 (Frederic De Oliveira - www.rpc3d.com)
' Converted from C# to VB.Net
' Wrapped some methods from python API (RoboDK v3.2.6) // python code on non-wrapped method is commented for future conversion


' The RoboDK class allows interacting with RoboDK
' This library includes a robotics toolbox for C#, inspired from Peter Corke's Robotics Toolbox:
' http://petercorke.com/Robotics_Toolbox.html
'
' In this library: pose = transformation matrix = homogeneous matrix = 4x4 matrix
' Visit: http://www.j3d.org/matrix_faq/matrfaq_latest.html
' to better understand homogeneous matrix operations
'
' This library includes the mathematics to operate with homogeneous matrices for robotics.

Imports System.Collections.Generic
Imports System.Linq
Imports System.Text
Imports System.Threading.Tasks
Imports System.Net.Sockets ' for Socket
Imports Microsoft.Win32 ' for registry key

''' <summary>
''' Matrix class for robotics. 
''' </summary>
Public Class Mat ' simple matrix class for homogeneous operations
    Public rows As Integer
    Public cols As Integer
    Private _mat As Double(,)

    '  Class used for Matrix exceptions
    Public Class MatException
        Inherits Exception
        Public Sub New(Message As String)
            MyBase.New(Message)
        End Sub
    End Class

    ''' <summary>
    ''' Matrix class constructor for any size matrix
    ''' </summary>
    ''' <param name="Rows__1">dimension 1 size (rows)</param>
    ''' <param name="Cols__2">dimension 2 size (columns)</param>
    Public Sub New(Rows__1 As Integer, Cols__2 As Integer)
        ' Matrix Class constructor
        rows = Rows__1
        cols = Cols__2
        _mat = New Double(rows - 1, cols - 1) {}
    End Sub

    ''' <summary>
    ''' Matrix class constructor for a 4x4 homogeneous matrix
    ''' </summary>
    ''' <param name="nx">Position [0,0]</param>
    ''' <param name="ox">Position [0,1]</param>
    ''' <param name="ax">Position [0,2]</param>
    ''' <param name="tx">Position [0,3]</param>
    ''' <param name="ny">Position [1,0]</param>
    ''' <param name="oy">Position [1,1]</param>
    ''' <param name="ay">Position [1,2]</param>
    ''' <param name="ty">Position [1,3]</param>
    ''' <param name="nz">Position [2,0]</param>
    ''' <param name="oz">Position [2,1]</param>
    ''' <param name="az">Position [2,2]</param>
    ''' <param name="tz">Position [2,3]</param>
    Public Sub New(nx As Double, ox As Double, ax As Double, tx As Double, ny As Double, oy As Double, _
     ay As Double, ty As Double, nz As Double, oz As Double, az As Double, tz As Double)
        ' Matrix Class constructor
        rows = 4
        cols = 4
        _mat = New Double(rows - 1, cols - 1) {}
        _mat(0, 0) = nx
        _mat(1, 0) = ny
        _mat(2, 0) = nz
        _mat(0, 1) = ox
        _mat(1, 1) = oy
        _mat(2, 1) = oz
        _mat(0, 2) = ax
        _mat(1, 2) = ay
        _mat(2, 2) = az
        _mat(0, 3) = tx
        _mat(1, 3) = ty
        _mat(2, 3) = tz
        _mat(3, 0) = 0.0
        _mat(3, 1) = 0.0
        _mat(3, 2) = 0.0
        _mat(3, 3) = 1.0
    End Sub

    ''' <summary>
    ''' Matrix class constructor for a 4x4 homogeneous matrix as a copy from another matrix
    ''' </summary>
    Public Sub New(pose As Mat)
        rows = pose.rows
        cols = pose.cols
        _mat = New Double(rows - 1, cols - 1) {}
        For i As Integer = 0 To rows - 1
            For j As Integer = 0 To cols - 1
                _mat(i, j) = pose(i, j)
            Next
        Next
    End Sub

    ''' <summary>
    ''' Matrix class constructor for a 4x1 vector [x,y,z,1]
    ''' </summary>
    ''' <param name="x">x coordinate</param>
    ''' <param name="y">y coordinate</param>
    ''' <param name="z">z coordinate</param>
    Public Sub New(x As Double, y As Double, z As Double)
        rows = 4
        cols = 1
        _mat = New Double(rows - 1, cols - 1) {}
        _mat(0, 0) = x
        _mat(1, 0) = y
        _mat(2, 0) = z
        _mat(3, 0) = 1.0
    End Sub

    '----------------------------------------------------
    '--------     Generic matrix usage    ---------------
    ''' <summary>
    ''' Return a translation matrix
    '''                 |  1   0   0   X |
    ''' transl(X,Y,Z) = |  0   1   0   Y |
    '''                 |  0   0   1   Z |
    '''                 |  0   0   0   1 |
    ''' </summary>
    ''' <param name="x">translation along X (mm)</param>
    ''' <param name="y">translation along Y (mm)</param>
    ''' <param name="z">translation along Z (mm)</param>
    ''' <returns></returns>
    Public Shared Function transl(x As Double, y As Double, z As Double) As Mat
        Dim mat__1 As Mat = Mat.IdentityMatrix(4, 4)
        mat__1.setPos(x, y, z)
        Return mat__1
    End Function

    ''' <summary>
    ''' Return a X-axis rotation matrix
    '''            |  1  0        0        0 |
    ''' rotx(rx) = |  0  cos(rx) -sin(rx)  0 |
    '''            |  0  sin(rx)  cos(rx)  0 |
    '''            |  0  0        0        1 |
    ''' </summary>
    ''' <param name="rx">rotation around X axis (in radians)</param>
    ''' <returns></returns>
    Public Shared Function rotx(rx As Double) As Mat
        Dim cx As Double = Math.Cos(rx)
        Dim sx As Double = Math.Sin(rx)
        Return New Mat(1, 0, 0, 0, 0, cx, _
         -sx, 0, 0, sx, cx, 0)
    End Function

    ''' <summary>
    ''' Return a Y-axis rotation matrix
    '''            |  cos(ry)  0   sin(ry)  0 |
    ''' roty(ry) = |  0        1   0        0 |
    '''            | -sin(ry)  0   cos(ry)  0 |
    '''            |  0        0   0        1 |
    ''' </summary>
    ''' <param name="ry">rotation around Y axis (in radians)</param>
    ''' <returns></returns>
    Public Shared Function roty(ry As Double) As Mat
        Dim cy As Double = Math.Cos(ry)
        Dim sy As Double = Math.Sin(ry)
        Return New Mat(cy, 0, sy, 0, 0, 1, _
         0, 0, -sy, 0, cy, 0)
    End Function

    ''' <summary>
    ''' Return a Z-axis rotation matrix
    '''            |  cos(rz)  -sin(rz)   0   0 |
    ''' rotz(rx) = |  sin(rz)   cos(rz)   0   0 |
    '''            |  0         0         1   0 |
    '''            |  0         0         0   1 |
    ''' </summary>
    ''' <param name="rz">rotation around Z axis (in radians)</param>
    ''' <returns></returns>
    Public Shared Function rotz(rz As Double) As Mat
        Dim cz As Double = Math.Cos(rz)
        Dim sz As Double = Math.Sin(rz)
        Return New Mat(cz, -sz, 0, 0, sz, cz, _
         0, 0, 0, 0, 1, 0)
    End Function


    '----------------------------------------------------
    '------ Pose to xyzrpw and xyzrpw to pose------------
    ''' <summary>
    ''' Calculates the equivalent position and euler angles ([x,y,z,r,p,w] vector) of the given pose 
    ''' Note: transl(x,y,z)*rotz(w*pi/180)*roty(p*pi/180)*rotx(r*pi/180)
    ''' See also: FromXYZRPW()
    ''' </summary>
    ''' <returns>XYZWPR translation and rotation in mm and degrees</returns>
    Public Function ToXYZRPW() As Double()
        Dim xyzwpr As Double() = New Double(5) {}
        Dim x As Double = _mat(0, 3)
        Dim y As Double = _mat(1, 3)
        Dim z As Double = _mat(2, 3)
        Dim w As Double, p As Double, r As Double
        If _mat(2, 0) > (1.0 - 0.000001) Then
            p = -Math.PI * 0.5
            r = 0
            w = Math.Atan2(-_mat(1, 2), _mat(1, 1))
        ElseIf _mat(2, 0) < -1.0 + 0.000001 Then
            p = 0.5 * Math.PI
            r = 0
            w = Math.Atan2(_mat(1, 2), _mat(1, 1))
        Else
            p = Math.Atan2(-_mat(2, 0), Math.Sqrt(_mat(0, 0) * _mat(0, 0) + _mat(1, 0) * _mat(1, 0)))
            w = Math.Atan2(_mat(1, 0), _mat(0, 0))
            r = Math.Atan2(_mat(2, 1), _mat(2, 2))
        End If
        xyzwpr(0) = x
        xyzwpr(1) = y
        xyzwpr(2) = z
        xyzwpr(3) = r * 180.0 / Math.PI
        xyzwpr(4) = p * 180.0 / Math.PI
        xyzwpr(5) = w * 180.0 / Math.PI
        Return xyzwpr
    End Function

    ''' <summary>
    ''' Calculates the pose from the position and euler angles ([x,y,z,r,p,w] vector)
    ''' The result is the same as calling: H = transl(x,y,z)*rotz(w*pi/180)*roty(p*pi/180)*rotx(r*pi/180)
    ''' </summary>
    ''' <param name="x"></param>
    ''' <param name="y"></param>
    ''' <param name="z"></param>
    ''' <param name="w"></param>
    ''' <param name="p"></param>
    ''' <param name="r"></param>
    ''' <returns>Homogeneous matrix (4x4)</returns>
    Public Shared Function FromXYZRPW(x As Double, y As Double, z As Double, w As Double, p As Double, r As Double) As Mat
        Dim a As Double = r * Math.PI / 180.0
        Dim b As Double = p * Math.PI / 180.0
        Dim c As Double = w * Math.PI / 180.0
        Dim ca As Double = Math.Cos(a)
        Dim sa As Double = Math.Sin(a)
        Dim cb As Double = Math.Cos(b)
        Dim sb As Double = Math.Sin(b)
        Dim cc As Double = Math.Cos(c)
        Dim sc As Double = Math.Sin(c)
        Return New Mat(cb * cc, cc * sa * sb - ca * sc, sa * sc + ca * cc * sb, x, cb * sc, ca * cc + sa * sb * sc, _
         ca * sb * sc - cc * sa, y, -sb, cb * sa, ca * cb, z)
    End Function

    ''' <summary>
    ''' Calculates the pose from the position and euler angles ([x,y,z,r,p,w] vector)
    '''  The result is the same as calling: H = transl(x,y,z)*rotz(w*pi/180)*roty(p*pi/180)*rotx(r*pi/180)
    ''' </summary>
    ''' <param name="xyzwpr"></param>
    ''' <returns>Homogeneous matrix (4x4)</returns>
    Public Shared Function FromXYZRPW(xyzwpr As Double()) As Mat
        If xyzwpr.Length < 6 Then
            Return Nothing
        End If
        Return FromXYZRPW(xyzwpr(0), xyzwpr(1), xyzwpr(2), xyzwpr(3), xyzwpr(4), xyzwpr(5))
    End Function

    ''' <summary>
    ''' Calculates the pose from the position and euler angles ([x,y,z,rx,ry,rz] array)
    ''' The result is the same as calling: H = transl(x,y,z)*rotx(rx*pi/180)*roty(ry*pi/180)*rotz(rz*pi/180)
    ''' </summary>
    ''' <param name="x"></param>
    ''' <param name="y"></param>
    ''' <param name="z"></param>
    ''' <param name="rx"></param>
    ''' <param name="ry"></param>
    ''' <param name="rz"></param>
    ''' <returns>Homogeneous matrix (4x4)</returns>
    Public Shared Function FromTxyzRxyz(x As Double, y As Double, z As Double, rx As Double, ry As Double, rz As Double) As Mat
        Dim a As Double = rx * Math.PI / 180.0
        Dim b As Double = ry * Math.PI / 180.0
        Dim c As Double = rz * Math.PI / 180.0
        Dim crx As Double = Math.Cos(a)
        Dim srx As Double = Math.Sin(a)
        Dim cry As Double = Math.Cos(b)
        Dim sry As Double = Math.Sin(b)
        Dim crz As Double = Math.Cos(c)
        Dim srz As Double = Math.Sin(c)
        Return New Mat(cry * crz, -cry * srz, sry, x, crx * srz + crz * srx * sry, crx * crz - srx * sry * srz, _
         -cry * srx, y, srx * srz - crx * crz * sry, crz * srx + crx * sry * srz, crx * cry, z)
    End Function

    ''' <summary>
    ''' Calculates the pose from the position and euler angles ([x,y,z,rx,ry,rz] array)
    ''' The result is the same as calling: H = transl(x,y,z)*rotx(rx*pi/180)*roty(ry*pi/180)*rotz(rz*pi/180)
    ''' </summary>
    ''' <returns>Homogeneous matrix (4x4)</returns>
    Public Shared Function FromTxyzRxyz(xyzwpr As Double()) As Mat
        If xyzwpr.Length < 6 Then
            Return Nothing
        End If
        Return FromTxyzRxyz(xyzwpr(0), xyzwpr(1), xyzwpr(2), xyzwpr(3), xyzwpr(4), xyzwpr(5))
    End Function

    ''' <summary>
    ''' Calculates the equivalent position and euler angles ([x,y,z,rx,ry,rz] array) of a pose 
    ''' Note: Pose = transl(x,y,z)*rotx(rx*pi/180)*roty(ry*pi/180)*rotz(rz*pi/180)
    ''' See also: FromTxyzRxyz()
    ''' </summary>
    ''' <returns>XYZWPR translation and rotation in mm and degrees</returns>
    Public Function ToTxyzRxyz() As Double()
        Dim xyzwpr As Double() = New Double(5) {}
        Dim x As Double = _mat(0, 3)
        Dim y As Double = _mat(1, 3)
        Dim z As Double = _mat(2, 3)
        Dim rx1 As Double = 0
        Dim ry1 As Double = 0
        Dim rz1 As Double = 0


        Dim a As Double = _mat(0, 0)
        Dim b As Double = _mat(0, 1)
        Dim c As Double = _mat(0, 2)
        Dim d As Double = _mat(1, 2)
        Dim e As Double = _mat(2, 2)

        If c = 1 Then
            ry1 = 0.5 * Math.PI
            rx1 = 0
            rz1 = Math.Atan2(_mat(1, 0), _mat(1, 1))
        ElseIf c = -1 Then
            ry1 = -Math.PI / 2
            rx1 = 0
            rz1 = Math.Atan2(_mat(1, 0), _mat(1, 1))
        Else
            Dim sy As Double = c
            Dim cy1 As Double = +Math.Sqrt(1 - sy * sy)

            Dim sx1 As Double = -d / cy1
            Dim cx1 As Double = e / cy1

            Dim sz1 As Double = -b / cy1
            Dim cz1 As Double = a / cy1

            rx1 = Math.Atan2(sx1, cx1)
            ry1 = Math.Atan2(sy, cy1)
            rz1 = Math.Atan2(sz1, cz1)
        End If

        xyzwpr(0) = x
        xyzwpr(1) = y
        xyzwpr(2) = z
        xyzwpr(3) = rx1 * 180.0 / Math.PI
        xyzwpr(4) = ry1 * 180.0 / Math.PI
        xyzwpr(5) = rz1 * 180.0 / Math.PI
        Return xyzwpr
    End Function

    ''' <summary>
    ''' Converts a pose (4x4 matrix) to a Staubli XYZWPR target
    ''' </summary>
    ''' <returns>XYZWPR translation and rotation in mm and degrees</returns>
    Public Function ToStaubli() As Double()
        'Converts a pose (4x4 matrix) to a Staubli XYZWPR target
        Dim xyzwpr As Double() = ToTxyzRxyz() 'already in degrees and mm
        'xyzwpr(3) *= 180.0 / Math.PI
        'xyzwpr(4) *= 180.0 / Math.PI
        'xyzwpr(5) *= 180.0 / Math.PI
        Return xyzwpr
    End Function

    'def ToMotoman(H):
    '    """Converts a pose (4x4 matrix) to a Motoman XYZWPR target

    '    :param H: pose
    '    :type H: :class:`.Mat`"""
    '    xyzwpr = pose_2_xyzrpw(H)
    '    return xyzwpr

    'def Pose_2_Fanuc(H):
    '    """Converts a pose (4x4 matrix) to a Fanuc XYZWPR target

    '    :param H: pose
    '    :type H: :class:`.Mat`"""
    '    xyzwpr = pose_2_xyzrpw(H)
    '    return xyzwpr

    'def Motoman_2_Pose(xyzwpr):
    '    """Converts a Motoman target to a pose (4x4 matrix)"""
    '    return xyzrpw_2_pose(xyzwpr)

    'def Pose_2_KUKA(H):
    '    """Converts a pose (4x4 matrix) to a Kuka target

    '    :param H: pose
    '    :type H: :class:`.Mat`"""
    '    x = H[0,3]
    '    y = H[1,3]
    '    z = H[2,3]
    '    if (H[2,0]) > (1.0 - 1e-6):
    '        p = -pi/2
    '        r = 0
    '        w = atan2(-H[1,2],H[1,1])
    '    elif (H[2,0]) < (-1.0 + 1e-6):
    '        p = pi/2
    '        r = 0
    '        w = atan2(H[1,2],H[1,1])
    '    else:
    '        p = atan2(-H[2,0],sqrt(H[0,0]*H[0,0]+H[1,0]*H[1,0]))
    '        w = atan2(H[1,0],H[0,0])
    '        r = atan2(H[2,1],H[2,2])
    '    return [x, y, z, w*180/pi, p*180/pi, r*180/pi]

    'def KUKA_2_Pose(xyzrpw):
    '    """Converts a KUKA XYZABC target to a pose (4x4 matrix)"""
    '    [x,y,z,r,p,w] = xyzrpw
    '    a = r*math.pi/180.0
    '    b = p*math.pi/180.0
    '    c = w*math.pi/180.0
    '    ca = math.cos(a)
    '    sa = math.sin(a)
    '    cb = math.cos(b)
    '    sb = math.sin(b)
    '    cc = math.cos(c)
    '    sc = math.sin(c)
    '    return Mat([[cb*ca, ca*sc*sb - cc*sa, sc*sa + cc*ca*sb, x],[cb*sa, cc*ca + sc*sb*sa, cc*sb*sa - ca*sc, y],[-sb, cb*sc, cc*cb, z],[0.0,0.0,0.0,1.0]])

    'def Adept_2_Pose(xyzrpw):
    '    """Converts an Adept XYZRPW target to a pose (4x4 matrix)"""
    '    [x,y,z,r,p,w] = xyzrpw
    '    a = r*math.pi/180.0
    '    b = p*math.pi/180.0
    '    c = w*math.pi/180.0
    '    ca = math.cos(a)
    '    sa = math.sin(a)
    '    cb = math.cos(b)
    '    sb = math.sin(b)
    '    cc = math.cos(c)
    '    sc = math.sin(c)
    '    return Mat([[ca*cb*cc - sa*sc, - cc*sa - ca*cb*sc, ca*sb, x],[ca*sc + cb*cc*sa, ca*cc - cb*sa*sc, sa*sb, y],[-cc*sb, sb*sc, cb, z],[0.0,0.0,0.0,1.0]])

    'def Pose_2_Adept(H):
    '    """Converts a pose to an Adept target    

    '    :param H: pose
    '    :type H: :class:`.Mat`"""
    '    x = H[0,3]
    '    y = H[1,3]
    '    z = H[2,3]
    '    if H[2,2] > (1.0 - 1e-6):
    '        r = 0
    '        p = 0
    '        w = atan2(H[1,0],H[0,0])
    '    elif H[2,2] < (-1.0 + 1e-6):
    '        r = 0
    '        p = pi
    '        w = atan2(H[1,0],H[1,1])
    '    else:
    '        cb=H[2,2]
    '        sb=+sqrt(1-cb*cb)
    '        sc=H[2,1]/sb
    '        cc=-H[2,0]/sb        
    '        sa=H[1,2]/sb
    '        ca=H[0,2]/sb        
    '        r = atan2(sa,ca)
    '        p = atan2(sb,cb)
    '        w = atan2(sc,cc)
    '    return [x, y, z, r*180/pi, p*180/pi, w*180/pi]

    'def Comau_2_Pose(xyzrpw):
    '    """Converts a Comau XYZRPW target to a pose (4x4 matrix)"""
    '    return Adept_2_Pose(xyzrpw)

    'def Pose_2_Comau(H):
    '    """Converts a pose to a Comau target

    '    :param H: pose
    '    :type H: :class:`.Mat`"""
    '    return Pose_2_Adept(H)

    'def Pose_2_Nachi(pose):
    '    """Converts a pose to a Nachi XYZRPW target    

    '    :param pose: pose
    '    :type pose: :class:`.Mat`"""
    '    [x,y,z,r,p,w] = pose_2_xyzrpw(pose)
    '    return [x,y,z,w,p,r]

    'def Nachi_2_Pose(xyzwpr):
    '    """Converts a Nachi XYZRPW target to a pose (4x4 matrix)"""
    '    return Fanuc_2_Pose(xyzwpr)



    ''' <summary>
    ''' Returns the quaternion of a pose (4x4 matrix)
    ''' </summary>
    ''' <param name="Ti"></param>
    ''' <returns></returns>
    Private Shared Function PoseToQuaternion(Ti As Mat) As Double()
        Dim q As Double() = New Double(3) {}
        Dim a As Double = (Ti(0, 0))
        Dim b As Double = (Ti(1, 1))
        Dim c As Double = (Ti(2, 2))
        Dim sign2 As Double = 1.0
        Dim sign3 As Double = 1.0
        Dim sign4 As Double = 1.0
        If (Ti(2, 1) - Ti(1, 2)) < 0 Then
            sign2 = -1
        End If
        If (Ti(0, 2) - Ti(2, 0)) < 0 Then
            sign3 = -1
        End If
        If (Ti(1, 0) - Ti(0, 1)) < 0 Then
            sign4 = -1
        End If
        q(0) = 0.5 * Math.Sqrt(Math.Max(a + b + c + 1, 0))
        q(1) = 0.5 * sign2 * Math.Sqrt(Math.Max(a - b - c + 1, 0))
        q(2) = 0.5 * sign3 * Math.Sqrt(Math.Max(-a + b - c + 1, 0))
        q(3) = 0.5 * sign4 * Math.Sqrt(Math.Max(-a - b + c + 1, 0))
        Return q
    End Function

    ''' <summary>
    ''' Returns the pose (4x4 matrix) from quaternion data
    ''' </summary>
    ''' <param name="qin"></param>
    ''' <returns></returns>
    Private Shared Function QuaternionToPose(qin As Double()) As Mat
        Dim qnorm As Double = Math.Sqrt(qin(0) * qin(0) + qin(1) * qin(1) + qin(2) * qin(2) + qin(3) * qin(3))
        Dim q As Double() = New Double(3) {}
        q(0) = qin(0) / qnorm
        q(1) = qin(1) / qnorm
        q(2) = qin(2) / qnorm
        q(3) = qin(3) / qnorm
        Dim pose As New Mat(1 - 2 * q(2) * q(2) - 2 * q(3) * q(3), 2 * q(1) * q(2) - 2 * q(3) * q(0), 2 * q(1) * q(3) + 2 * q(2) * q(0), 0, 2 * q(1) * q(2) + 2 * q(3) * q(0), 1 - 2 * q(1) * q(1) - 2 * q(3) * q(3), _
         2 * q(2) * q(3) - 2 * q(1) * q(0), 0, 2 * q(1) * q(3) - 2 * q(2) * q(0), 2 * q(2) * q(3) + 2 * q(1) * q(0), 1 - 2 * q(1) * q(1) - 2 * q(2) * q(2), 0)
        Return pose
    End Function

    ''' <summary>
    ''' Converts a pose to an ABB target
    ''' </summary>
    ''' <param name="H"></param>
    ''' <returns></returns>
    Private Shared Function PoseToABB(H As Mat) As Double()
        Dim q As Double() = PoseToQuaternion(H)
        Dim xyzq1234 As Double() = {H(0, 3), H(1, 3), H(2, 3), q(0), q(1), q(2), _
         q(3)}
        Return xyzq1234
    End Function

    ''' <summary>
    ''' Calculates the equivalent position and euler angles ([x,y,z,r,p,w] vector) of the given pose in Universal Robots format
    ''' Note: The difference between ToUR and ToXYZWPR is that the first one uses radians for the orientation and the second one uses degres
    ''' Note: transl(x,y,z)*rotx(rx*pi/180)*roty(ry*pi/180)*rotz(rz*pi/180)
    ''' See also: FromXYZRPW()
    ''' </summary>
    ''' <returns>XYZWPR translation and rotation in mm and radians</returns>
    Public Function PoseToUR() As Double()
        Dim xyzwpr As Double() = New Double(5) {}
        Dim x As Double = _mat(0, 3)
        Dim y As Double = _mat(1, 3)
        Dim z As Double = _mat(2, 3)
        Dim angle As Double = Math.Acos(Math.Min(Math.Max((_mat(0, 0) + _mat(1, 1) + _mat(2, 2) - 1) / 2, -1), 1))
        Dim rx As Double = _mat(2, 1) - _mat(1, 2)
        Dim ry As Double = _mat(0, 2) - _mat(2, 0)
        Dim rz As Double = _mat(1, 0) - _mat(0, 1)
        If angle = 0 Then
            rx = 0
            ry = 0
            rz = 0
        Else
            rx = rx * angle / (2 * Math.Sin(angle))
            ry = ry * angle / (2 * Math.Sin(angle))
            rz = rz * angle / (2 * Math.Sin(angle))
        End If
        xyzwpr(0) = x
        xyzwpr(1) = y
        xyzwpr(2) = z
        xyzwpr(3) = rx
        xyzwpr(4) = ry
        xyzwpr(5) = rz
        Return xyzwpr
    End Function

    ''' <summary>
    ''' Calculates the pose from the position and euler angles ([x,y,z,r,p,w] vector)
    ''' Note: The difference between FromUR and FromXYZWPR is that the first one uses radians for the orientation and the second one uses degres
    ''' The result is the same as calling: H = transl(x,y,z)*rotx(rx)*roty(ry)*rotz(rz)
    ''' </summary>
    ''' <param name="xyzwpr">The position and euler angles array</param>
    ''' <returns>Homogeneous matrix (4x4)</returns>
    Public Shared Function URToPose(xyzwpr As Double()) As Mat
        Dim x As Double = xyzwpr(0)
        Dim y As Double = xyzwpr(1)
        Dim z As Double = xyzwpr(2)
        Dim w As Double = xyzwpr(3)
        Dim p As Double = xyzwpr(4)
        Dim r As Double = xyzwpr(5)
        Dim angle As Double = Math.Sqrt(w * w + p * p + r * r)
        If angle < 0.000001 Then
            Return Identity4x4()
        End If
        Dim c As Double = Math.Cos(angle)
        Dim s As Double = Math.Sin(angle)
        Dim ux As Double = w / angle
        Dim uy As Double = p / angle
        Dim uz As Double = r / angle
        Return New Mat(ux * ux + c * (1 - ux * ux), ux * uy * (1 - c) - uz * s, ux * uz * (1 - c) + uy * s, x, ux * uy * (1 - c) + uz * s, uy * uy + (1 - uy * uy) * c, _
         uy * uz * (1 - c) - ux * s, y, ux * uz * (1 - c) - uy * s, uy * uz * (1 - c) + ux * s, uz * uz + (1 - uz * uz) * c, z)
    End Function

    ''' <summary>
    ''' Converts a matrix into a one-dimensional array of doubles
    ''' </summary>
    ''' <returns>one-dimensional array</returns>
    Public Function ToDoubles() As Double()
        Dim cnt As Integer = 0
        Dim array As Double() = New Double(rows * cols - 1) {}
        For j As Integer = 0 To cols - 1
            For i As Integer = 0 To rows - 1
                array(cnt) = _mat(i, j)
                cnt = cnt + 1
            Next
        Next
        Return array
    End Function

    ''' <summary>
    ''' Check if the matrix is square
    ''' </summary>
    Public Function IsSquare() As [Boolean]
        Return (rows = cols)
    End Function

    Public Function Is4x4() As [Boolean]
        If cols <> 4 OrElse rows <> 4 Then
            Return False
        End If
        Return True
    End Function

    ''' <summary>
    ''' Check if the matrix is homogeneous (4x4)
    ''' </summary>
    Public Function IsHomogeneous() As [Boolean]
        If Not Is4x4() Then
            Return False
        End If
        Return True
        '
        '        test = self[0:3,0:3];
        '        test = test*test.tr()
        '        test[0,0] = test[0,0] - 1.0
        '        test[1,1] = test[1,1] - 1.0
        '        test[2,2] = test[2,2] - 1.0
        '        zero = 0.0
        '        for x in range(3):
        '            for y in range(3):
        '                zero = zero + abs(test[x,y])
        '        if zero > 1e-4:
        '            return False
        '        return True
        '        

    End Function

    ''' <summary>
    ''' Returns the inverse of a homogeneous matrix (4x4 matrix)
    ''' </summary>
    ''' <returns>Homogeneous matrix (4x4)</returns>
    Public Function inv() As Mat
        If Not IsHomogeneous() Then
            Throw New MatException("Can't invert a non-homogeneous matrix")
        End If
        Dim xyz As Double() = Me.Pos()
        Dim mat_xyz As New Mat(xyz(0), xyz(1), xyz(2))
        Dim hinv As Mat = Me.Duplicate()
        hinv.setPos(0, 0, 0)
        hinv = hinv.Transpose()
        Dim new_pos As Mat = rotate(hinv, mat_xyz)
        hinv(0, 3) = -new_pos(0, 0)
        hinv(1, 3) = -new_pos(1, 0)
        hinv(2, 3) = -new_pos(2, 0)
        Return hinv
    End Function

    ''' <summary>
    ''' Rotate a vector given a matrix (rotation matrix or homogeneous matrix)
    ''' </summary>
    ''' <param name="pose">4x4 homogeneous matrix or 3x3 rotation matrix</param>
    ''' <param name="vector">4x1 or 3x1 vector</param>
    ''' <returns></returns>
    Public Shared Function rotate(pose As Mat, vector As Mat) As Mat
        If pose.cols < 3 OrElse pose.rows < 3 OrElse vector.rows < 3 Then
            Throw New MatException("Invalid matrix size")
        End If
        Dim pose3x3 As Mat = pose.Duplicate()
        Dim vector3 As Mat = vector.Duplicate()
        pose3x3.rows = 3
        pose3x3.cols = 3
        vector3.rows = 3
        Return pose3x3 * vector3
    End Function

    ''' <summary>
    ''' Returns the XYZ position of the Homogeneous matrix
    ''' </summary>
    ''' <returns>XYZ position</returns>
    Public Function Pos() As Double()
        If Not Is4x4() Then
            Return Nothing
        End If
        Dim xyz As Double() = New Double(2) {}
        xyz(0) = _mat(0, 3)
        xyz(1) = _mat(1, 3)
        xyz(2) = _mat(2, 3)
        Return xyz
    End Function

    ''' <summary>
    ''' Sets the 4x4 position of the Homogeneous matrix
    ''' </summary>
    ''' <param name="xyz">XYZ position</param>
    Public Sub setPos(xyz As Double())
        If Not Is4x4() OrElse xyz.Length < 3 Then
            Return
        End If
        _mat(0, 3) = xyz(0)
        _mat(1, 3) = xyz(1)
        _mat(2, 3) = xyz(2)
    End Sub

    ''' <summary>
    ''' Sets the 4x4 position of the Homogeneous matrix
    ''' </summary>
    ''' <param name="x">X position</param>
    ''' <param name="y">Y position</param>
    ''' <param name="z">Z position</param>
    Public Sub setPos(x As Double, y As Double, z As Double)
        If Not Is4x4() Then
            Return
        End If
        _mat(0, 3) = x
        _mat(1, 3) = y
        _mat(2, 3) = z
    End Sub


    Default Public Property Item(iRow As Integer, iCol As Integer) As Double
        ' Access this matrix as a 2D array
        Get
            Return _mat(iRow, iCol)
        End Get
        Set(value As Double)
            _mat(iRow, iCol) = value
        End Set
    End Property

    Public Function GetCol(k As Integer) As Mat
        Dim m As New Mat(rows, 1)
        For i As Integer = 0 To rows - 1
            m(i, 0) = _mat(i, k)
        Next
        Return m
    End Function

    Public Sub SetCol(v As Mat, k As Integer)
        For i As Integer = 0 To rows - 1
            _mat(i, k) = v(i, 0)
        Next
    End Sub

    Public Function Duplicate() As Mat
        ' Function returns the copy of this matrix
        Dim matrix As New Mat(rows, cols)
        For i As Integer = 0 To rows - 1
            For j As Integer = 0 To cols - 1
                matrix(i, j) = matrix(i, j)
            Next
        Next
        Return matrix
    End Function

    Public Shared Function ZeroMatrix(iRows As Integer, iCols As Integer) As Mat
        ' Function generates the zero matrix
        Dim matrix As New Mat(iRows, iCols)
        For i As Integer = 0 To iRows - 1
            For j As Integer = 0 To iCols - 1
                matrix(i, j) = 0
            Next
        Next
        Return matrix
    End Function

    Public Shared Function IdentityMatrix(iRows As Integer, iCols As Integer) As Mat
        ' Function generates the identity matrix
        Dim matrix As Mat = ZeroMatrix(iRows, iCols)
        For i As Integer = 0 To Math.Min(iRows, iCols) - 1
            matrix(i, i) = 1
        Next
        Return matrix
    End Function

    ''' <summary>
    ''' Returns an identity 4x4 matrix (homogeneous matrix)
    ''' </summary>
    ''' <returns></returns>
    Public Shared Function Identity4x4() As Mat
        Return Mat.IdentityMatrix(4, 4)
    End Function

    '
    '    public static Mat Parse(string ps)                        // Function parses the matrix from string
    '    {
    '        string s = NormalizeMatrixString(ps);
    '        string[] rows = Regex.Split(s, "\r\n");
    '        string[] nums = rows[0].Split(' ');
    '        Mat matrix = new Mat(rows.Length, nums.Length);
    '        try
    '        {
    '            for (int i = 0; i < rows.Length; i++)
    '            {
    '                nums = rows[i].Split(' ');
    '                for (int j = 0; j < nums.Length; j++) matrix[i, j] = double.Parse(nums[j]);
    '            }
    '        }
    '        catch (FormatException exc) { throw new MatException("Wrong input format!"); }
    '        return matrix;
    '    }


    Public Overrides Function ToString() As String
        ' Function returns matrix as a string
        Dim s As String = ""
        For i As Integer = 0 To rows - 1
            For j As Integer = 0 To cols - 1
                s += [String].Format("{0,5:0.00}", _mat(i, j)) + " "
            Next
            s += vbCr & vbLf
        Next
        Return s
    End Function

    ''' <summary>
    ''' Transpose a matrix
    ''' </summary>
    ''' <returns></returns>
    Public Function Transpose() As Mat
        Return Transpose(Me)
    End Function
    Public Shared Function Transpose(m As Mat) As Mat
        ' Matrix transpose, for any rectangular matrix
        Dim t As New Mat(m.cols, m.rows)
        For i As Integer = 0 To m.rows - 1
            For j As Integer = 0 To m.cols - 1
                t(j, i) = m(i, j)
            Next
        Next
        Return t
    End Function

    Private Shared Sub SafeAplusBintoC(A As Mat, xa As Integer, ya As Integer, B As Mat, xb As Integer, yb As Integer, _
     C As Mat, size As Integer)
        For i As Integer = 0 To size - 1
            ' rows
            For j As Integer = 0 To size - 1
                ' cols
                C(i, j) = 0
                If xa + j < A.cols AndAlso ya + i < A.rows Then
                    C(i, j) += A(ya + i, xa + j)
                End If
                If xb + j < B.cols AndAlso yb + i < B.rows Then
                    C(i, j) += B(yb + i, xb + j)
                End If
            Next
        Next
    End Sub

    Private Shared Sub SafeAminusBintoC(A As Mat, xa As Integer, ya As Integer, B As Mat, xb As Integer, yb As Integer, _
     C As Mat, size As Integer)
        For i As Integer = 0 To size - 1
            ' rows
            For j As Integer = 0 To size - 1
                ' cols
                C(i, j) = 0
                If xa + j < A.cols AndAlso ya + i < A.rows Then
                    C(i, j) += A(ya + i, xa + j)
                End If
                If xb + j < B.cols AndAlso yb + i < B.rows Then
                    C(i, j) -= B(yb + i, xb + j)
                End If
            Next
        Next
    End Sub

    Private Shared Sub SafeACopytoC(A As Mat, xa As Integer, ya As Integer, C As Mat, size As Integer)
        For i As Integer = 0 To size - 1
            ' rows
            For j As Integer = 0 To size - 1
                ' cols
                C(i, j) = 0
                If xa + j < A.cols AndAlso ya + i < A.rows Then
                    C(i, j) += A(ya + i, xa + j)
                End If
            Next
        Next
    End Sub

    Private Shared Sub AplusBintoC(A As Mat, xa As Integer, ya As Integer, B As Mat, xb As Integer, yb As Integer, _
     C As Mat, size As Integer)
        For i As Integer = 0 To size - 1
            ' rows
            For j As Integer = 0 To size - 1
                C(i, j) = A(ya + i, xa + j) + B(yb + i, xb + j)
            Next
        Next
    End Sub

    Private Shared Sub AminusBintoC(A As Mat, xa As Integer, ya As Integer, B As Mat, xb As Integer, yb As Integer, _
     C As Mat, size As Integer)
        For i As Integer = 0 To size - 1
            ' rows
            For j As Integer = 0 To size - 1
                C(i, j) = A(ya + i, xa + j) - B(yb + i, xb + j)
            Next
        Next
    End Sub

    Private Shared Sub ACopytoC(A As Mat, xa As Integer, ya As Integer, C As Mat, size As Integer)
        For i As Integer = 0 To size - 1
            ' rows
            For j As Integer = 0 To size - 1
                C(i, j) = A(ya + i, xa + j)
            Next
        Next
    End Sub

    Private Shared Function StrassenMultiply(A As Mat, B As Mat) As Mat
        ' Smart matrix multiplication
        If A.cols <> B.rows Then
            Throw New MatException("Wrong dimension of matrix!")
        End If

        Dim R As Mat

        Dim msize As Integer = Math.Max(Math.Max(A.rows, A.cols), Math.Max(B.rows, B.cols))

        If msize < 32 Then
            R = ZeroMatrix(A.rows, B.cols)
            For i As Integer = 0 To R.rows - 1
                For j As Integer = 0 To R.cols - 1
                    For k As Integer = 0 To A.cols - 1
                        R(i, j) += A(i, k) * B(k, j)
                    Next
                Next
            Next
            Return R
        End If

        Dim size As Integer = 1
        Dim n As Integer = 0
        While msize > size
            size *= 2
            n += 1
        End While


        Dim h As Integer = size / 2


        Dim mField As Mat(,) = New Mat(n - 1, 8) {}

        '
        '         *  8x8, 8x8, 8x8, ...
        '         *  4x4, 4x4, 4x4, ...
        '         *  2x2, 2x2, 2x2, ...
        '         *  . . .
        '         


        Dim z As Integer
        For i As Integer = 0 To n - 5
            ' rows
            z = CInt(Math.Pow(2, n - i - 1))
            For j As Integer = 0 To 8
                mField(i, j) = New Mat(z, z)
            Next
        Next

        SafeAplusBintoC(A, 0, 0, A, h, h, _
         mField(0, 0), h)
        SafeAplusBintoC(B, 0, 0, B, h, h, _
         mField(0, 1), h)
        StrassenMultiplyRun(mField(0, 0), mField(0, 1), mField(0, 1 + 1), 1, mField)
        ' (A11 + A22) * (B11 + B22);
        SafeAplusBintoC(A, 0, h, A, h, h, _
         mField(0, 0), h)
        SafeACopytoC(B, 0, 0, mField(0, 1), h)
        StrassenMultiplyRun(mField(0, 0), mField(0, 1), mField(0, 1 + 2), 1, mField)
        ' (A21 + A22) * B11;
        SafeACopytoC(A, 0, 0, mField(0, 0), h)
        SafeAminusBintoC(B, h, 0, B, h, h, _
         mField(0, 1), h)
        StrassenMultiplyRun(mField(0, 0), mField(0, 1), mField(0, 1 + 3), 1, mField)
        'A11 * (B12 - B22);
        SafeACopytoC(A, h, h, mField(0, 0), h)
        SafeAminusBintoC(B, 0, h, B, 0, 0, _
         mField(0, 1), h)
        StrassenMultiplyRun(mField(0, 0), mField(0, 1), mField(0, 1 + 4), 1, mField)
        'A22 * (B21 - B11);
        SafeAplusBintoC(A, 0, 0, A, h, 0, _
         mField(0, 0), h)
        SafeACopytoC(B, h, h, mField(0, 1), h)
        StrassenMultiplyRun(mField(0, 0), mField(0, 1), mField(0, 1 + 5), 1, mField)
        '(A11 + A12) * B22;
        SafeAminusBintoC(A, 0, h, A, 0, 0, _
         mField(0, 0), h)
        SafeAplusBintoC(B, 0, 0, B, h, 0, _
         mField(0, 1), h)
        StrassenMultiplyRun(mField(0, 0), mField(0, 1), mField(0, 1 + 6), 1, mField)
        '(A21 - A11) * (B11 + B12);
        SafeAminusBintoC(A, h, 0, A, h, h, _
         mField(0, 0), h)
        SafeAplusBintoC(B, 0, h, B, h, h, _
         mField(0, 1), h)
        StrassenMultiplyRun(mField(0, 0), mField(0, 1), mField(0, 1 + 7), 1, mField)
        ' (A12 - A22) * (B21 + B22);
        R = New Mat(A.rows, B.cols)
        ' result
        ' C11
        For i As Integer = 0 To Math.Min(h, R.rows) - 1
            ' rows
            For j As Integer = 0 To Math.Min(h, R.cols) - 1
                ' cols
                R(i, j) = mField(0, 1 + 1)(i, j) + mField(0, 1 + 4)(i, j) - mField(0, 1 + 5)(i, j) + mField(0, 1 + 7)(i, j)
            Next
        Next

        ' C12
        For i As Integer = 0 To Math.Min(h, R.rows) - 1
            ' rows
            For j As Integer = h To Math.Min(2 * h, R.cols) - 1
                ' cols
                R(i, j) = mField(0, 1 + 3)(i, j - h) + mField(0, 1 + 5)(i, j - h)
            Next
        Next

        ' C21
        For i As Integer = h To Math.Min(2 * h, R.rows) - 1
            ' rows
            For j As Integer = 0 To Math.Min(h, R.cols) - 1
                ' cols
                R(i, j) = mField(0, 1 + 2)(i - h, j) + mField(0, 1 + 4)(i - h, j)
            Next
        Next

        ' C22
        For i As Integer = h To Math.Min(2 * h, R.rows) - 1
            ' rows
            For j As Integer = h To Math.Min(2 * h, R.cols) - 1
                ' cols
                R(i, j) = mField(0, 1 + 1)(i - h, j - h) - mField(0, 1 + 2)(i - h, j - h) + mField(0, 1 + 3)(i - h, j - h) + mField(0, 1 + 6)(i - h, j - h)
            Next
        Next

        Return R
    End Function

    ' function for square matrix 2^N x 2^N

    Private Shared Sub StrassenMultiplyRun(A As Mat, B As Mat, C As Mat, l As Integer, f As Mat(,))
        ' A * B into C, level of recursion, matrix field
        Dim size As Integer = A.rows
        Dim h As Integer = size / 2

        If size < 32 Then
            For i As Integer = 0 To C.rows - 1
                For j As Integer = 0 To C.cols - 1
                    C(i, j) = 0
                    For k As Integer = 0 To A.cols - 1
                        C(i, j) += A(i, k) * B(k, j)
                    Next
                Next
            Next
            Return
        End If

        AplusBintoC(A, 0, 0, A, h, h, _
         f(l, 0), h)
        AplusBintoC(B, 0, 0, B, h, h, _
         f(l, 1), h)
        StrassenMultiplyRun(f(l, 0), f(l, 1), f(l, 1 + 1), l + 1, f)
        ' (A11 + A22) * (B11 + B22);
        AplusBintoC(A, 0, h, A, h, h, _
         f(l, 0), h)
        ACopytoC(B, 0, 0, f(l, 1), h)
        StrassenMultiplyRun(f(l, 0), f(l, 1), f(l, 1 + 2), l + 1, f)
        ' (A21 + A22) * B11;
        ACopytoC(A, 0, 0, f(l, 0), h)
        AminusBintoC(B, h, 0, B, h, h, _
         f(l, 1), h)
        StrassenMultiplyRun(f(l, 0), f(l, 1), f(l, 1 + 3), l + 1, f)
        'A11 * (B12 - B22);
        ACopytoC(A, h, h, f(l, 0), h)
        AminusBintoC(B, 0, h, B, 0, 0, _
         f(l, 1), h)
        StrassenMultiplyRun(f(l, 0), f(l, 1), f(l, 1 + 4), l + 1, f)
        'A22 * (B21 - B11);
        AplusBintoC(A, 0, 0, A, h, 0, _
         f(l, 0), h)
        ACopytoC(B, h, h, f(l, 1), h)
        StrassenMultiplyRun(f(l, 0), f(l, 1), f(l, 1 + 5), l + 1, f)
        '(A11 + A12) * B22;
        AminusBintoC(A, 0, h, A, 0, 0, _
         f(l, 0), h)
        AplusBintoC(B, 0, 0, B, h, 0, _
         f(l, 1), h)
        StrassenMultiplyRun(f(l, 0), f(l, 1), f(l, 1 + 6), l + 1, f)
        '(A21 - A11) * (B11 + B12);
        AminusBintoC(A, h, 0, A, h, h, _
         f(l, 0), h)
        AplusBintoC(B, 0, h, B, h, h, _
         f(l, 1), h)
        StrassenMultiplyRun(f(l, 0), f(l, 1), f(l, 1 + 7), l + 1, f)
        ' (A12 - A22) * (B21 + B22);
        ' C11
        For i As Integer = 0 To h - 1
            ' rows
            For j As Integer = 0 To h - 1
                ' cols
                C(i, j) = f(l, 1 + 1)(i, j) + f(l, 1 + 4)(i, j) - f(l, 1 + 5)(i, j) + f(l, 1 + 7)(i, j)
            Next
        Next

        ' C12
        For i As Integer = 0 To h - 1
            ' rows
            For j As Integer = h To size - 1
                ' cols
                C(i, j) = f(l, 1 + 3)(i, j - h) + f(l, 1 + 5)(i, j - h)
            Next
        Next

        ' C21
        For i As Integer = h To size - 1
            ' rows
            For j As Integer = 0 To h - 1
                ' cols
                C(i, j) = f(l, 1 + 2)(i - h, j) + f(l, 1 + 4)(i - h, j)
            Next
        Next

        ' C22
        For i As Integer = h To size - 1
            ' rows
            For j As Integer = h To size - 1
                ' cols
                C(i, j) = f(l, 1 + 1)(i - h, j - h) - f(l, 1 + 2)(i - h, j - h) + f(l, 1 + 3)(i - h, j - h) + f(l, 1 + 6)(i - h, j - h)
            Next
        Next
    End Sub

    Public Shared Function StupidMultiply(m1 As Mat, m2 As Mat) As Mat
        ' Stupid matrix multiplication
        If m1.cols <> m2.rows Then
            Throw New MatException("Wrong dimensions of matrix!")
        End If

        Dim result As Mat = ZeroMatrix(m1.rows, m2.cols)
        For i As Integer = 0 To result.rows - 1
            For j As Integer = 0 To result.cols - 1
                For k As Integer = 0 To m1.cols - 1
                    result(i, j) += m1(i, k) * m2(k, j)
                Next
            Next
        Next
        Return result
    End Function
    Private Shared Function Multiply(n As Double, m As Mat) As Mat
        ' Multiplication by constant n
        Dim r As New Mat(m.rows, m.cols)
        For i As Integer = 0 To m.rows - 1
            For j As Integer = 0 To m.cols - 1
                r(i, j) = m(i, j) * n
            Next
        Next
        Return r
    End Function
    Private Shared Function Add(m1 As Mat, m2 As Mat) As Mat
        ' Add matrix
        If m1.rows <> m2.rows OrElse m1.cols <> m2.cols Then
            Throw New MatException("Matrices must have the same dimensions!")
        End If
        Dim r As New Mat(m1.rows, m1.cols)
        For i As Integer = 0 To r.rows - 1
            For j As Integer = 0 To r.cols - 1
                r(i, j) = m1(i, j) + m2(i, j)
            Next
        Next
        Return r
    End Function

    Public Shared Function NormalizeMatrixString(matStr As String) As String
        ' From Andy - thank you! :)
        ' Remove any multiple spaces
        While matStr.IndexOf("  ") <> -1
            matStr = matStr.Replace("  ", " ")
        End While

        ' Remove any spaces before or after newlines
        matStr = matStr.Replace(" " & vbCr & vbLf, vbCr & vbLf)
        matStr = matStr.Replace(vbCr & vbLf & " ", vbCr & vbLf)

        ' If the data ends in a newline, remove the trailing newline.
        ' Make it easier by first replacing \r\n’s with |’s then
        ' restore the |’s with \r\n’s
        matStr = matStr.Replace(vbCr & vbLf, "|")
        While matStr.LastIndexOf("|") = (matStr.Length - 1)
            matStr = matStr.Substring(0, matStr.Length - 1)
        End While

        matStr = matStr.Replace("|", vbCr & vbLf)
        Return matStr.Trim()
    End Function


    ' Operators
    Public Shared Operator -(m As Mat) As Mat
        Return Mat.Multiply(-1, m)
    End Operator

    Public Shared Operator +(m1 As Mat, m2 As Mat) As Mat
        Return Mat.Add(m1, m2)
    End Operator

    Public Shared Operator -(m1 As Mat, m2 As Mat) As Mat
        Return Mat.Add(m1, -m2)
    End Operator

    Public Shared Operator *(m1 As Mat, m2 As Mat) As Mat
        Return Mat.StrassenMultiply(m1, m2)
    End Operator

    Public Shared Operator *(n As Double, m As Mat) As Mat
        Return Mat.Multiply(n, m)
    End Operator
End Class


    ''' <summary>
    ''' This class is the link to allows to create macros and automate Robodk.
    ''' Any interaction is made through \"items\" (Item() objects). An item is an object in the
    ''' robodk tree (it can be either a robot, an object, a tool, a frame, a program, ...).
    ''' </summary>
Public Class RoboDK
    ''' <summary>
    ''' Class used for RoboDK exceptions
    ''' </summary>  
    Public Class RDKException
        Inherits Exception
        Public Sub New(Message As String)
            MyBase.New(Message)
        End Sub
    End Class

    ' Tree item types
    Public Const ITEM_TYPE_ANY As Integer = -1
    Public Const ITEM_TYPE_STATION As Integer = 1
    Public Const ITEM_TYPE_ROBOT As Integer = 2
    Public Const ITEM_TYPE_FRAME As Integer = 3
    Public Const ITEM_TYPE_TOOL As Integer = 4
    Public Const ITEM_TYPE_OBJECT As Integer = 5
    Public Const ITEM_TYPE_TARGET As Integer = 6
    Public Const ITEM_TYPE_PROGRAM As Integer = 8
    Public Const ITEM_TYPE_INSTRUCTION As Integer = 9
    Public Const ITEM_TYPE_PROGRAM_PYTHON As Integer = 10
    Public Const ITEM_TYPE_MACHINING As Integer = 11
    Public Const ITEM_TYPE_BALLBARVALIDATION As Integer = 12
    Public Const ITEM_TYPE_CALIBPROJECT As Integer = 13
    Public Const ITEM_TYPE_VALID_ISO9283 As Integer = 14

    ' Instruction types
    Public Const INS_TYPE_INVALID As Integer = -1
    Public Const INS_TYPE_MOVE As Integer = 0
    Public Const INS_TYPE_MOVEC As Integer = 1
    Public Const INS_TYPE_CHANGESPEED As Integer = 2
    Public Const INS_TYPE_CHANGEFRAME As Integer = 3
    Public Const INS_TYPE_CHANGETOOL As Integer = 4
    Public Const INS_TYPE_CHANGEROBOT As Integer = 5
    Public Const INS_TYPE_PAUSE As Integer = 6
    Public Const INS_TYPE_EVENT As Integer = 7
    Public Const INS_TYPE_CODE As Integer = 8
    Public Const INS_TYPE_PRINT As Integer = 9

    ' Move types
    Public Const MOVE_TYPE_INVALID As Integer = -1
    Public Const MOVE_TYPE_JOINT As Integer = 1
    Public Const MOVE_TYPE_LINEAR As Integer = 2
    Public Const MOVE_TYPE_CIRCULAR As Integer = 3

    ' Station parameters request
    Public Const PATH_OPENSTATION As String = "PATH_OPENSTATION"
    Public Const FILE_OPENSTATION As String = "FILE_OPENSTATION"
    Public Const PATH_DESKTOP As String = "PATH_DESKTOP"

    ' Script execution types
    Public Const RUNMODE_SIMULATE As Integer = 1 ' performs the simulation moving the robot (default)
    Public Const RUNMODE_QUICKVALIDATE As Integer = 2 ' performs a quick check to validate the robot movements
    Public Const RUNMODE_MAKE_ROBOTPROG As Integer = 3 ' makes the robot program
    Public Const RUNMODE_MAKE_ROBOTPROG_AND_UPLOAD As Integer = 4 ' makes the robot program and updates it to the robot
    Public Const RUNMODE_MAKE_ROBOTPROG_AND_START As Integer = 5 ' makes the robot program and starts it on the robot (independently from the PC)
    Public Const RUNMODE_RUN_ROBOT As Integer = 6 ' moves the real robot from the PC (PC is the client, the robot behaves like a server)

    ' Program execution type
    Public Const PROGRAM_RUN_ON_SIMULATOR As Integer = 1 ' Set the program to run on the simulator
    Public Const PROGRAM_RUN_ON_ROBOT As Integer = 2 ' Set the program to run on the robot


    ' Robot connection status
    Public Const ROBOTCOM_PROBLEMS As Integer = -3
    Public Const ROBOTCOM_DISCONNECTED As Integer = -2
    Public Const ROBOTCOM_NOT_CONNECTED As Integer = -1
    Public Const ROBOTCOM_READY As Integer = 0
    Public Const ROBOTCOM_WORKING As Integer = 1
    Public Const ROBOTCOM_WAITING As Integer = 2
    Public Const ROBOTCOM_UNKNOWN As Integer = -1000

    ' TCP calibration types
    Public Const CALIBRATE_TCP_BY_POINT As Integer = 0
    Public Const CALIBRATE_TCP_BY_PLANE As Integer = 1

    ' Reference frame calibration types
    Public Const CALIBRATE_FRAME_3P_P1_ON_X As Integer = 0 'Calibrate by 3 points: [X, X+, Y+] (p1 on X axis)
    Public Const CALIBRATE_FRAME_3P_P1_ORIGIN As Integer = 1 'Calibrate by 3 points: [Origin, X+, XY+] (p1 is origin)
    Public Const CALIBRATE_FRAME_6P As Integer = 2 'Calibrate by 6 points
    Public Const CALIBRATE_TURNTABLE As Integer = 3 'Calibrate turntable

    ' projection types (for AddCurve)
    Public Const PROJECTION_NONE As Integer = 0 ' No curve projection
    Public Const PROJECTION_CLOSEST As Integer = 1 ' The projection will the closest point on the surface
    Public Const PROJECTION_ALONG_NORMAL As Integer = 2 ' The projection will be done along the normal.
    Public Const PROJECTION_ALONG_NORMAL_RECALC As Integer = 3 ' The projection will be done along the normal. Furthermore, the normal will be recalculated according to the surface normal.

    ' Euler type
    Public Const JOINT_FORMAT = -1 ' Using joints (not poses)
    Public Const EULER_RX_RYp_RZpp As Integer = 0 ' generic
    Public Const EULER_RZ_RYp_RXpp As Integer = 1 ' ABB RobotStudio
    Public Const EULER_RZ_RYp_RZpp As Integer = 2 ' Kawasaki, Adept, Staubli
    Public Const EULER_RZ_RXp_RZpp As Integer = 3 ' CATIA, SolidWorks
    Public Const EULER_RX_RY_RZ As Integer = 4 ' Fanuc, Kuka, Motoman, Nachi
    Public Const EULER_RZ_RY_RX As Integer = 5 ' CRS
    Public Const EULER_QUEATERNION As Integer = 6 ' ABB Rapid

    ' State of the RoboDK window
    Public Const WINDOWSTATE_HIDDEN As Integer = -1
    Public Const WINDOWSTATE_SHOW As Integer = 0
    Public Const WINDOWSTATE_MINIMIZED As Integer = 1
    Public Const WINDOWSTATE_NORMAL As Integer = 2
    Public Const WINDOWSTATE_MAXIMIZED As Integer = 3
    Public Const WINDOWSTATE_FULLSCREEN As Integer = 4
    Public Const WINDOWSTATE_CINEMA As Integer = 5
    Public Const WINDOWSTATE_FULLSCREEN_CINEMA As Integer = 6

    ' Instruction program call type:
    Public Const INSTRUCTION_CALL_PROGRAM As Integer = 0
    Public Const INSTRUCTION_INSERT_CODE As Integer = 1
    Public Const INSTRUCTION_START_THREAD As Integer = 2
    Public Const INSTRUCTION_COMMENT As Integer = 3

    ' Object selection features:
    Public Const FEATURE_NONE As Integer = 0
    Public Const FEATURE_SURFACE As Integer = 1
    Public Const FEATURE_CURVE As Integer = 2
    Public Const FEATURE_POINT As Integer = 3

    ' Spray gun simulation:
    Public Const SPRAY_OFF As Integer = 0
    Public Const SPRAY_ON As Integer = 1

    ' Collision checking state
    Public Const COLLISION_OFF As Integer = 0
    Public Const COLLISION_ON As Integer = 1

    ' NC program result
    Public Const NC_POSITIONS_NOT_REACHABLE As Integer = -2
    Public Const NC_OK As Integer = 1


    Public PROCESS As System.Diagnostics.Process = Nothing ' pointer to the process

    Private APPLICATION_DIR As String = "" ' file path to the robodk program (executable), typically C:/RoboDK/bin/RoboDK.exe. Leave empty to use the registry key: HKEY_LOCAL_MACHINE\SOFTWARE\RoboDK
    Private ARGUMENTS As String = "" ' arguments to provide to RoboDK on startup
    Private SAFE_MODE As Integer = 1 ' checks that provided items exist in memory
    Private AUTO_UPDATE As Integer = 0 ' if AUTO_UPDATE is zero, the scene is rendered after every function call  
    Private TIMEOUT As Integer = 10 * 1000 ' timeout for communication, in seconds
    Private COM As Socket ' tcpip com
    Private IP As String = "localhost" ' IP address of the simulator (localhost if it is the same computer), otherwise, use RL = Robolink('yourip') to set to a different IP
    Private PORT_START As Integer = 20500 ' port to start looking for app connection
    Private PORT_END As Integer = 20500 ' port to stop looking for app connection
    Private START_HIDDEN As Boolean = False ' forces to start hidden. ShowRoboDK must be used to show the window
    Private PORT As Integer = -1 ' port where connection succeeded
    Private PORT_FORCED As Integer = -1 ' port to force RoboDK to start listening

    'Returns 1 if connection is valid, returns 0 if connection is invalid
    Private Function _is_connected() As Boolean
        Return COM.Connected
    End Function

    ''' <summary>
    ''' Checks if the object is currently linked to RoboDK
    ''' </summary>
    ''' <returns></returns>
    Public Function Connected() As Boolean
        'return COM.Connected;//does not work well
        Dim part1 As Boolean = COM.Poll(1000, SelectMode.SelectRead)
        Dim part2 As Boolean = COM.Available = 0
        If part1 AndAlso part2 Then
            Return False
        Else
            Return True
        End If
    End Function

    'If we are not connected it will attempt a connection, if it fails, it will throw an error
    Private Sub _check_connection()
        If Not _is_connected() AndAlso Not Connect() Then
            Throw New RDKException("Can't connect to RoboDK library")
        End If
    End Sub

    ' checks the status of the connection
    Private Function _check_status() As Integer
        Dim status As Integer = _rec_int()
        If status > 0 AndAlso status < 10 Then
            Dim strproblems As String
            strproblems = "Unknown error"
            If status = 1 Then
                strproblems = "Invalid item provided: The item identifier provided is not valid or it does not exist."
            ElseIf status = 2 Then
                'output warning
                strproblems = _rec_line()
                'print("WARNING: " + strproblems);
                '#warn(strproblems)# does not show where is the problem...
                Return 0
            ElseIf status = 3 Then
                ' output error
                strproblems = _rec_line()
                Throw New RDKException(strproblems)
            ElseIf status = 9 Then
                strproblems = "Invalid license. Contact us at: info@robodk.com"
            End If
            'print(strproblems);
            'raise Exception(strproblems)
            Throw New RDKException(strproblems)
            ' everything is OK
            'status = status
        ElseIf status = 0 Then
        Else
            'raise Exception('Problems running function');
            Throw New RDKException("Problems running function")
        End If
        Return status
    End Function

    'Formats the color in a vector of size 4x1 and ranges [0,1]
    Private Function _check_color(color As Double()) As Boolean
        If color.Length < 4 Then
            Throw New RDKException("Invalid color. A color must be a 4-size double array [r,g,b,a]")
            'raise Exception('Problems running function');
            Return False
        End If
        Return True
    End Function

    'Sends a string of characters with a \\n
    Private Sub _send_line(line As String)
        line.Replace(ControlChars.Lf, " "c)
        ' one new line at the end only!
        Dim data As Byte() = System.Text.Encoding.UTF8.GetBytes(line & Convert.ToString(vbLf))
        COM.Send(data)
    End Sub

    Private Function _rec_line() As String
        'Receives a string. It reads until if finds LF (\\n)
        Dim buffer As Byte() = New Byte(0) {}
        Dim bytesread As Integer = COM.Receive(buffer, 1, SocketFlags.None)
        Dim line As String = ""
        While bytesread > 0 AndAlso buffer(0) <> Convert.ToByte(ControlChars.Lf)
            line = line & System.Text.Encoding.UTF8.GetString(buffer)
            bytesread = COM.Receive(buffer, 1, SocketFlags.None)
        End While
        Return line
    End Function

    'Sends an item pointer
    Private Sub _send_item(item As Item)
        Dim bytes As Byte()
        If item Is Nothing Then
            Dim zero As UInt64 = 0
            bytes = BitConverter.GetBytes(zero)
        Else
            bytes = BitConverter.GetBytes(item.ID)
        End If
        If bytes.Length <> 8 Then
            Throw New RDKException("API error")
        End If
        Array.Reverse(bytes)
        COM.Send(bytes)
    End Sub

    'Receives an item pointer
    Private Function _rec_item() As Item
        Dim buffer1 As Byte() = New Byte(7) {}
        Dim buffer2 As Byte() = New Byte(3) {}
        Dim read1 As Integer = COM.Receive(buffer1, 8, SocketFlags.None)
        Dim read2 As Integer = COM.Receive(buffer2, 4, SocketFlags.None)
        If read1 <> 8 OrElse read2 <> 4 Then
            Return Nothing
        End If
        Array.Reverse(buffer1)
        Array.Reverse(buffer2)
        Dim item As UInt64 = BitConverter.ToUInt64(buffer1, 0)
        'Console.WriteLine("Received item: " + item.ToString());
        Dim type As Int32 = BitConverter.ToInt32(buffer2, 0)
        Return New Item(Me, item, type)
    End Function

    Private Sub _send_pose(pose As Mat)
        If Not pose.IsHomogeneous() Then
            ' warning!!
            Return
        End If
        Const nvalues As Integer = 16
        Dim bytesarray As Byte() = New Byte(8 * nvalues - 1) {}
        Dim cnt As Integer = 0
        For j As Integer = 0 To pose.cols - 1
            For i As Integer = 0 To pose.rows - 1
                Dim onedouble As Byte() = BitConverter.GetBytes(CDbl(pose(i, j)))
                Array.Reverse(onedouble)
                Array.Copy(onedouble, 0, bytesarray, cnt * 8, 8)
                cnt = cnt + 1
            Next
        Next
        COM.Send(bytesarray, 8 * nvalues, SocketFlags.None)
    End Sub

    Private Function _rec_pose() As Mat
        Dim pose As New Mat(4, 4)
        Dim bytes As Byte() = New Byte(16 * 8 - 1) {}
        Dim nbytes As Integer = COM.Receive(bytes, 16 * 8, SocketFlags.None)
        If nbytes <> 16 * 8 Then
            'raise Exception('Problems running function');
            Throw New RDKException("Invalid pose sent")
        End If
        Dim cnt As Integer = 0
        For j As Integer = 0 To pose.cols - 1
            For i As Integer = 0 To pose.rows - 1
                Dim onedouble As Byte() = New Byte(7) {}
                Array.Copy(bytes, cnt, onedouble, 0, 8)
                Array.Reverse(onedouble)
                pose(i, j) = BitConverter.ToDouble(onedouble, 0)
                cnt = cnt + 8
            Next
        Next
        Return pose
    End Function

    Private Sub _send_xyz(xyzpos As Double())
        For i As Integer = 0 To 2
            Dim bytes As Byte() = BitConverter.GetBytes(CDbl(xyzpos(i)))
            Array.Reverse(bytes)
            COM.Send(bytes, 8, SocketFlags.None)
        Next
    End Sub
    Private Sub _rec_xyz(xyzpos As Double())
        Dim bytes As Byte() = New Byte(3 * 8 - 1) {}
        Dim nbytes As Integer = COM.Receive(bytes, 3 * 8, SocketFlags.None)
        If nbytes <> 3 * 8 Then
            'raise Exception('Problems running function');
            Throw New RDKException("Invalid pose sent")
        End If
        For i As Integer = 0 To 2
            Dim onedouble As Byte() = New Byte(7) {}
            Array.Copy(bytes, i * 8, onedouble, 0, 8)
            Array.Reverse(onedouble)
            xyzpos(i) = BitConverter.ToDouble(onedouble, 0)
        Next
    End Sub

    Private Sub _send_int(number As Int32)
        Dim bytes As Byte() = BitConverter.GetBytes(number)
        Array.Reverse(bytes)
        ' convert from big endian to little endian
        COM.Send(bytes)
    End Sub

    Private Function _rec_int() As Int32
        Dim bytes As Byte() = New Byte(3) {}
        Dim read As Integer = COM.Receive(bytes, 4, SocketFlags.None)
        If read < 4 Then
            Return 0
        End If
        Array.Reverse(bytes)
        ' convert from little endian to big endian
        Return BitConverter.ToInt32(bytes, 0)
    End Function

    ' Sends an array of doubles
    Private Sub _send_array(values As Double())
        If values Is Nothing Then
            _send_int(0)
            Return
        End If
        Dim nvalues As Integer = values.Length
        _send_int(nvalues)
        Dim bytesarray As Byte() = New Byte(8 * nvalues - 1) {}
        For i As Integer = 0 To nvalues - 1
            Dim onedouble As Byte() = BitConverter.GetBytes(values(i))
            Array.Reverse(onedouble)
            Array.Copy(onedouble, 0, bytesarray, i * 8, 8)
        Next
        COM.Send(bytesarray, 8 * nvalues, SocketFlags.None)
    End Sub

    ' Receives an array of doubles
    Private Function _rec_array() As Double()
        Dim nvalues As Integer = _rec_int()
        If nvalues > 0 Then
            Dim values As Double() = New Double(nvalues - 1) {}
            Dim bytes As Byte() = New Byte(nvalues * 8 - 1) {}
            Dim read As Integer = COM.Receive(bytes, nvalues * 8, SocketFlags.None)
            For i As Integer = 0 To nvalues - 1
                Dim onedouble As Byte() = New Byte(7) {}
                Array.Copy(bytes, i * 8, onedouble, 0, 8)
                Array.Reverse(onedouble)
                values(i) = BitConverter.ToDouble(onedouble, 0)
            Next
            Return values
        End If
        Return Nothing
    End Function

    ' sends a 2 dimensional matrix
    Private Sub _send_matrix(mat As Mat)
        _send_int(mat.rows)
        _send_int(mat.cols)
        For j As Integer = 0 To mat.cols - 1
            For i As Integer = 0 To mat.rows - 1
                Dim bytes As Byte() = BitConverter.GetBytes(CDbl(mat(i, j)))
                Array.Reverse(bytes)
                COM.Send(bytes, 8, SocketFlags.None)
            Next
        Next

    End Sub

    ' receives a 2 dimensional matrix (nxm)
    Private Function _rec_matrix() As Mat
        Dim size1 As Integer = _rec_int()
        Dim size2 As Integer = _rec_int()
        Dim recvsize As Integer = size1 * size2 * 8
        Dim bytes As Byte() = New Byte(recvsize - 1) {}
        Dim mat As New Mat(size1, size2)
        Dim BUFFER_SIZE As Integer = 256
        Dim received As Integer = 0
        If recvsize > 0 Then
            Dim to_receive As Integer = Math.Min(recvsize, BUFFER_SIZE)
            While to_receive > 0
                Dim nbytesok As Integer = COM.Receive(bytes, received, to_receive, SocketFlags.None)
                If nbytesok <= 0 Then
                    'raise Exception('Problems running function');
                    Throw New RDKException("Can't receive matrix properly")
                End If
                received = received + nbytesok
                to_receive = Math.Min(recvsize - received, BUFFER_SIZE)
            End While
        End If
        Dim cnt As Integer = 0
        For j As Integer = 0 To mat.cols - 1
            For i As Integer = 0 To mat.rows - 1
                Dim onedouble As Byte() = New Byte(7) {}
                Array.Copy(bytes, cnt, onedouble, 0, 8)
                Array.Reverse(onedouble)
                mat(i, j) = BitConverter.ToDouble(onedouble, 0)
                cnt = cnt + 8
            Next
        Next
        Return mat
    End Function

    ' private move type, to be used by public methods (MoveJ  and MoveL)
    Private Sub _moveX(target As Item, joints As Double(), mat_target As Mat, itemrobot As Item, movetype As Integer, Optional blocking As Boolean = True)
        itemrobot.WaitMove()
        Dim command As String = "MoveX"
        _send_line(command)
        _send_int(movetype)
        If target IsNot Nothing Then
            _send_int(3)
            _send_array(Nothing)
            _send_item(target)
        ElseIf joints IsNot Nothing Then
            _send_int(1)
            _send_array(joints)
            _send_item(Nothing)
        ElseIf mat_target IsNot Nothing AndAlso mat_target.IsHomogeneous() Then
            _send_int(2)
            _send_array(mat_target.ToDoubles())
            _send_item(Nothing)
        Else
            'raise Exception('Problems running function');
            Throw New RDKException("Invalid target type")
        End If
        _send_item(itemrobot)
        _check_status()
        If blocking Then
            itemrobot.WaitMove()
        End If
    End Sub
    ' private move type, to be used by public methods (MoveJ  and MoveL)
    Private Sub _moveC_private(target1 As Item, joints1 As Double(), mat_target1 As Mat, target2 As Item, joints2 As Double(), mat_target2 As Mat, _
     itemrobot As Item, Optional blocking As Boolean = True)
        itemrobot.WaitMove()
        Dim command As String = "MoveC"
        _send_line(command)
        _send_int(3)
        If target1 IsNot Nothing Then
            _send_int(3)
            _send_array(Nothing)
            _send_item(target1)
        ElseIf joints1 IsNot Nothing Then
            _send_int(1)
            _send_array(joints1)
            _send_item(Nothing)
        ElseIf mat_target1 IsNot Nothing AndAlso mat_target1.IsHomogeneous() Then
            _send_int(2)
            _send_array(mat_target1.ToDoubles())
            _send_item(Nothing)
        Else
            Throw New RDKException("Invalid type of target 1")
        End If
        '//////////////////////////////////
        If target2 IsNot Nothing Then
            _send_int(3)
            _send_array(Nothing)
            _send_item(target2)
        ElseIf joints2 IsNot Nothing Then
            _send_int(1)
            _send_array(joints2)
            _send_item(Nothing)
        ElseIf mat_target2 IsNot Nothing AndAlso mat_target2.IsHomogeneous() Then
            _send_int(2)
            _send_array(mat_target2.ToDoubles())
            _send_item(Nothing)
        Else
            Throw New RDKException("Invalid type of target 2")
        End If
        '//////////////////////////////////
        _send_item(itemrobot)
        _check_status()
        If blocking Then
            itemrobot.WaitMove()
        End If
    End Sub

    '%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%   

    ''' <summary>
    ''' Creates a link with RoboDK
    ''' </summary>
    ''' <param name="robodk_ip"></param>
    ''' <param name="start_hidden__1"></param>
    ''' <param name="com_port"></param>
    Public Sub New(Optional robodk_ip As String = "localhost", Optional start_hidden__1 As Boolean = False, Optional com_port As Integer = -1, Optional args As String = "", Optional path As String = "")
        'A connection is attempted upon creation of the object"""
        If robodk_ip <> "" Then
            IP = robodk_ip
        End If
        START_HIDDEN = start_hidden__1
        If com_port > 0 Then
            PORT_FORCED = com_port
            PORT_START = com_port
            PORT_END = com_port
        End If
        If path <> "" Then
            APPLICATION_DIR = path
        End If
        If args <> "" Then
            ARGUMENTS = args
        End If
        Connect()
    End Sub

    ''' <summary>
    ''' Disconnect from the RoboDK API. This flushes any pending program generation.
    ''' </summary>
    ''' <returns></returns>
    Public Function Disconnect() As Boolean
        If COM.Connected Then
            COM.Disconnect(False)
        End If
        Return True
    End Function

    ''' <summary>
    ''' Disconnect from the RoboDK API. This flushes any pending program generation.
    ''' </summary>
    ''' <returns></returns>
    Public Function Finish() As Boolean
        Return Disconnect()
    End Function

    Private Function _Set_connection_params(Optional safe_mode__1 As Integer = 1, Optional auto_update__2 As Integer = 0, Optional timeout__3 As Integer = -1) As Boolean
        'Sets some behavior parameters: SAFE_MODE, AUTO_UPDATE and TIMEOUT.
        SAFE_MODE = safe_mode__1
        AUTO_UPDATE = auto_update__2
        If timeout__3 >= 0 Then
            TIMEOUT = timeout__3
        End If
        _send_line("CMD_START")
        _send_line(Convert.ToString(SAFE_MODE) + " " + Convert.ToString(AUTO_UPDATE))
        Dim response As String = _rec_line()
        If response = "READY" Then
            Return True
        End If
        Return False
    End Function

    ''' <summary>
    ''' Starts the link with RoboDK (automatic upon creation of the object)
    ''' </summary>
    ''' <returns></returns>
    Public Function Connect() As Boolean
        'Establishes a connection with robodk. robodk must be running, otherwise, the variable APPLICATION_DIR must be set properly.
        Dim connected As Boolean = False
        Dim _port As Integer
        For i As Integer = 0 To 1
            For _port = PORT_START To PORT_END
                COM = New Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.IP)
                'COM = new Socket(SocketType.Stream, ProtocolType.IPv4);
                COM.SendTimeout = 1000
                COM.ReceiveTimeout = 1000
                Try
                    COM.Connect(IP, _port)
                    connected = _is_connected()
                    If connected Then
                        COM.SendTimeout = TIMEOUT
                        COM.ReceiveTimeout = TIMEOUT
                        Exit Try
                    End If
                Catch e As Exception
                    'connected = false;
                End Try
            Next
            If connected Then
                PORT = _port
                Exit For
            Else
                If IP <> "localhost" Then
                    Exit For
                End If
                Dim _arguments As String = ""
                If PORT_FORCED > 0 Then
                    _arguments = (_arguments & Convert.ToString("/PORT=")) + PORT_FORCED.ToString() + " "
                End If
                If START_HIDDEN Then
                    _arguments = _arguments & Convert.ToString("/NOSPLASH /NOSHOW /HIDDEN ")
                End If
                If ARGUMENTS <> "" Then
                    _arguments = _arguments & ARGUMENTS
                End If
                If APPLICATION_DIR = "" Then

                    Dim install_path As String = Nothing

                    ' retrieve install path from the registry:
                    Dim localKey As RegistryKey = RegistryKey.OpenBaseKey(Microsoft.Win32.RegistryHive.LocalMachine, RegistryView.Registry64)
                    localKey = localKey.OpenSubKey("SOFTWARE\RoboDK")
                    If localKey IsNot Nothing Then
                        install_path = localKey.GetValue("INSTDIR").ToString()
                        If install_path IsNot Nothing Then
                            APPLICATION_DIR = install_path & "\bin\RoboDK.exe"
                        End If
                    End If
                End If
                If APPLICATION_DIR = "" Then
                    APPLICATION_DIR = "C:/RoboDK/bin/RoboDK.exe"
                End If
                PROCESS = System.Diagnostics.Process.Start(APPLICATION_DIR, _arguments)
                System.Threading.Thread.Sleep(2000)
            End If
        Next
        If connected AndAlso Not _Set_connection_params() Then
            connected = False
            PROCESS = Nothing
        End If
        Return connected
    End Function


    ' %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    ' public methods
    ''' <summary>
    ''' Returns an item by its name. If there is no exact match it will return the last closest match.
    ''' </summary>
    ''' <param name="name">Item name</param>
    ''' <param name="itemtype">Filter by item type RoboDK.ITEM_TYPE_...</param>
    ''' <returns></returns>
    Public Function getItem(name As String, Optional itemtype As Integer = -1) As Item
        _check_connection()
        Dim command As String
        If itemtype < 0 Then
            command = "G_Item"
            _send_line(command)
            _send_line(name)
        Else
            command = "G_Item2"
            _send_line(command)
            _send_line(name)
            _send_int(itemtype)
        End If
        Dim item As Item = _rec_item()
        _check_status()
        Return item
    End Function

    ''' <summary>
    ''' Returns a list of items (list of name or pointers) of all available items in the currently open station in robodk.
    ''' Optionally, use a filter to return specific items (example: getItemListNames(filter = ITEM_CASE_ROBOT))
    ''' </summary>
    ''' <param name="filter">ITEM_TYPE</param>
    ''' <returns></returns>
    Public Function getItemListNames(Optional filter As Integer = -1) As String()
        _check_connection()
        Dim command As String
        If filter < 0 Then
            command = "G_List_Items"
            _send_line(command)
        Else
            command = "G_List_Items_Type"
            _send_line(command)
            _send_int(filter)
        End If
        Dim numitems As Integer = _rec_int()
        Dim listnames As String() = New String(numitems - 1) {}
        For i As Integer = 0 To numitems - 1
            listnames(i) = _rec_line()
        Next
        _check_status()
        Return listnames
    End Function

    ''' <summary>
    ''' Returns a list of items (list of name or pointers) of all available items in the currently open station in robodk.
    ''' Optionally, use a filter to return specific items (example: getItemListNames(filter = ITEM_CASE_ROBOT))
    ''' </summary>
    ''' <param name="filter">ITEM_TYPE</param>
    ''' <returns></returns>
    Public Function getItemList(Optional filter As Integer = -1) As Item()
        _check_connection()
        Dim command As String
        If filter < 0 Then
            command = "G_List_Items_ptr"
            _send_line(command)
        Else
            command = "G_List_Items_Type_ptr"
            _send_line(command)
            _send_int(filter)
        End If
        Dim numitems As Integer = _rec_int()
        Dim listitems As Item() = New Item(numitems - 1) {}
        For i As Integer = 0 To numitems - 1
            listitems(i) = _rec_item()
        Next
        _check_status()
        Return listitems
    End Function

    '//// add more methods

    ''' <summary>
    ''' Shows a RoboDK popup to select one object from the open station.
    ''' An item type can be specified to filter desired items. If no type is specified, all items are selectable.
    ''' </summary>
    ''' <param name="message">Message to pop up</param>
    ''' <param name="itemtype">optionally filter by RoboDK.ITEM_TYPE_*</param>
    ''' <returns></returns>
    Public Function ItemUserPick(Optional message As String = "Pick one item", Optional itemtype As Integer = -1) As Item
        _check_connection()
        Dim command As String = "PickItem"
        _send_line(command)
        _send_line(message)
        _send_int(itemtype)
        COM.ReceiveTimeout = 3600 * 1000
        Dim item As Item = _rec_item()
        COM.ReceiveTimeout = TIMEOUT
        _check_status()
        Return item
    End Function

    ''' <summary>
    ''' Shows or raises the RoboDK window
    ''' </summary>
    Public Sub ShowRoboDK()
        _check_connection()
        Dim command As String = "RAISE"
        _send_line(command)
        _check_status()
    End Sub

    ''' <summary>
    ''' Hides the RoboDK window
    ''' </summary>
    Public Sub HideRoboDK()
        _check_connection()
        Dim command As String = "HIDE"
        _send_line(command)
        _check_status()
    End Sub

    ''' <summary>
    ''' Closes RoboDK window and finishes RoboDK execution
    ''' </summary>
    Public Sub CloseRoboDK()
        _check_connection()
        Dim command As String = "QUIT"
        _send_line(command)
        _check_status()
        COM.Disconnect(False)
        PROCESS = Nothing
    End Sub



    ''' <summary>
    ''' Set the state of the RoboDK window
    ''' </summary>
    ''' <param name="windowstate"></param>
    Public Sub setWindowState(Optional windowstate As Integer = WINDOWSTATE_NORMAL)
        _check_connection()
        Dim command As String = "S_WindowState"
        _send_line(command)
        _send_int(windowstate)
        _check_status()
    End Sub

    Public Sub ShowMessage(message As String)
        _check_connection()
        Dim command As String = "ShowMessage"
        _send_line(command)
        _send_line(message)
        COM.ReceiveTimeout = 3600 * 1000
        _check_status()
        COM.ReceiveTimeout = TIMEOUT
    End Sub

    '''//////////// Add More methods
    Public Sub Copy(item As Item)
        'Makes a copy of an item (same as Ctrl+C), which can be pasted (Ctrl+V) using Paste_Item().
        'In 1 : item
        'Example:
        '        RL = Robolink()
        '            object = RL.Item('My Object');
        '            object.Copy()         #RL.Copy(object); also works
        '            newobject = RL.Paste();
        '            newobject.setName('My Object (copy 1)');
        '            newobject = RL.Paste();
        '            newobject.setName('My Object (copy 2)');"""
        _check_connection()
        Dim command As String = "Copy"
        _send_line(command)
        _send_item(item)
        _check_status()
    End Sub

    Public Function Paste(Optional toparent As Item = Nothing) As Item
        'Pastes the copied item (same as Ctrl+V). Needs to be used after Copy_Item(). See Copy_Item() for an example.
        'In 1 (optional): item -> parent to paste to"""
        _check_connection()
        Dim command As String = "Paste"
        _send_line(command)
        _send_item(toparent)
        Dim newitem As Item = _rec_item()
        _check_status()
        Return newitem
    End Function

    ''' <summary>
    ''' Loads a file and attaches it to parent. It can be any file supported by robodk.
    ''' </summary>
    ''' <param name="filename">absolute path of the file</param>
    ''' <param name="parent">parent to attach. Leave empty for new stations or to load an object at the station root</param>
    ''' <returns>Newly added object. Check with item.Valid() for a successful load</returns>
    Public Function AddFile(filename As String, Optional parent As Item = Nothing) As Item
        'Example:
        'RL = Robolink()
        'item = Add_File(r'C:\\Users\\Name\\Desktop\\object.step')
        'RL.Set_Pose(item, transl(100,50,500))"""
        _check_connection()
        Dim command As String = "Add"
        _send_line(command)
        _send_line(filename)
        _send_item(parent)
        Dim newitem As Item = _rec_item()
        _check_status()
        Return newitem
    End Function

    '''//////////// Add More methods
    ''' <summary>
    ''' Adds a shape provided triangle coordinates. Triangles must be provided as a list of vertices. A vertex normal can be provided optionally.
    ''' </summary>
    ''' <param name="triangle_points"> matrix 3xN or 6xN -> N must be multiple of 3 because vertices must be stacked by groups of 3. Each group is a triangle.</param>
    ''' <param name="add_to">If True, the curve will be added as part of the object in the RoboDK item tree (a reference object must be provided)</param>
    ''' <returns>added object/shape (0 if failed)</returns>
    Public Function AddShape(triangle_points As Mat, Optional add_to As Item = Nothing) As Item
        '    if isinstance(triangle_points,list):
        '        triangle_points = tr(Mat(triangle_points))
        '    elif not isinstance(triangle_points, Mat):
        '        raise Exception("triangle_points must be a 3xN or 6xN list or matrix")
        _check_connection()
        Dim command As String = "AddShape"
        _send_line(command)
        _send_matrix(triangle_points)
        _send_item(add_to)
        Dim newitem As Item = _rec_item()
        _check_status()
        Return newitem
    End Function

    ''' <summary>
    ''' Adds a curve provided point coordinates. The provided points must be a list of vertices. A vertex normal can be provided optionally.
    ''' </summary>
    ''' <param name="curve_points">matrix 3xN or 6xN -> N must be multiple of 3</param>
    ''' <param name="reference_object">object to add the curve and/or project the curve to the surface</param>
    ''' <param name="add_to_ref">If True, the curve will be added as part of the object in the RoboDK item tree (a reference object must be provided)</param>
    ''' <param name="projection_type">Type of projection. For example: PROJECTION_ALONG_NORMAL_RECALC will project along the point normal and recalculate the normal vector on the surface projected.</param>
    ''' <returns>added object/curve (null if failed)</returns>
    Public Function AddCurve(curve_points As Mat, Optional reference_object As Item = Nothing, Optional add_to_ref As Boolean = False, Optional projection_type As Integer = PROJECTION_ALONG_NORMAL_RECALC) As Item
        _check_connection()
        Dim command As String = "AddWire"
        _send_line(command)
        _send_matrix(curve_points)
        _send_item(reference_object)
        _send_int(If(add_to_ref, 1, 0))
        _send_int(projection_type)
        Dim newitem As Item = _rec_item()
        _check_status()
        Return newitem
    End Function

    ''' <summary>
    ''' Adds a list of points to an object. The provided points must be a list of vertices. A vertex normal can be provided optionally.
    ''' </summary>
    ''' <param name="points">matrix 3xN or 6xN -> N must be multiple of 3</param>
    ''' <param name="reference_object">object to add the curve and/or project the curve to the surface</param>
    ''' <param name="add_to_ref">If True, the points will be added as part of the object in the RoboDK item tree (a reference object must be provided)</param>
    ''' <param name="projection_type">Type of projection. For example: PROJECTION_ALONG_NORMAL_RECALC will project along the point normal and recalculate the normal vector on the surface projected.</param>
    ''' <returns>added object/curve (0 if failed)</returns>
    Public Function AddPoints(points As Mat, Optional reference_object As Item = Nothing, Optional add_to_ref As Boolean = False, Optional projection_type As Integer = PROJECTION_ALONG_NORMAL_RECALC) As Item
        '    if isinstance(points,list):
        '       points = Mat(points).tr()
        '    elif not isinstance(points, Mat):
        '        raise Exception("points must be a 3xN or 6xN list or matrix")
        _check_connection()
        Dim command As String = "AddPoints"
        _send_line(command)
        _send_matrix(points)
        _send_item(reference_object)
        If add_to_ref Then
            _send_int(1)
        Else
            _send_int(0)
        End If
        _send_int(projection_type)
        Dim newitem As Item = _rec_item()
        _check_status()
        Return newitem
    End Function

    ''' <summary>
    ''' Projects a point given its coordinates. The provided points must be a list of [XYZ] coordinates. Optionally, a vertex normal can be provided [XYZijk].
    ''' </summary>
    ''' <param name="points">matrix 3xN or 6xN -> list of points to project</param>
    ''' <param name="object_project">object to project</param>
    ''' <param name="projection_type">Type of projection. For example: PROJECTION_ALONG_NORMAL_RECALC will project along the point normal and recalculate the normal vector on the surface projected.</param>
    ''' <returns></returns>
    Public Function ProjectPoints(points As Mat, object_project As Item, Optional projection_type As Integer = PROJECTION_ALONG_NORMAL_RECALC) As Mat
        _check_connection()
        Dim command As String = "ProjectPoints"
        _send_line(command)
        _send_matrix(points)
        _send_item(object_project)
        _send_int(projection_type)
        Dim projected_points As Mat = _rec_matrix()
        _check_status()
        Return projected_points
    End Function

    ''' <summary>
    ''' Save an item to a file. If no item is provided, the open station is saved.
    ''' </summary>
    ''' <param name="filename">absolute path to save the file</param>
    ''' <param name="itemsave">object or station to save. Leave empty to automatically save the current station.</param>
    Public Sub Save(filename As String, Optional itemsave As Item = Nothing)
        _check_connection()
        Dim command As String = "Save"
        _send_line(command)
        _send_line(filename)
        _send_item(itemsave)
        _check_status()
    End Sub

    ''' <summary>
    ''' Adds a new empty station.
    ''' </summary>
    ''' <param name="name">name of the station</param>
    ''' <returns>the new station created</returns>
    Public Function AddStation(Optional name As String = "New Station") As Item
        _check_connection()
        Dim command As String = "NewStation"
        _send_line(command)
        _send_line(name)
        Dim newitem As Item = _rec_item()
        _check_status()
        Return newitem
    End Function

    ''' <summary>
    ''' Closes the current station without suggesting to save
    ''' </summary>
    Public Sub CloseStation()
        _check_connection()
        Dim command As String = "Remove"
        _send_line(command)
        _send_item(New Item(Me))
        _check_status()
    End Sub

    ''' <summary>
    ''' Adds a new target that can be reached with a robot.
    ''' </summary>
    ''' <param name="name">name of the target</param>
    ''' <param name="itemparent">parent to attach to (such as a frame)</param>
    ''' <param name="itemrobot">main robot that will be used to go to self target</param>
    ''' <returns>the new target created</returns>
    Public Function AddTarget(name As String, Optional itemparent As Item = Nothing, Optional itemrobot As Item = Nothing) As Item
        _check_connection()
        Dim command As String = "Add_TARGET"
        _send_line(command)
        _send_line(name)
        _send_item(itemparent)
        _send_item(itemrobot)
        Dim newitem As Item = _rec_item()
        _check_status()
        Return newitem
    End Function

    ''' <summary>
    ''' Adds a new Frame that can be referenced by a robot.
    ''' </summary>
    ''' <param name="name">name of the reference frame</param>
    ''' <param name="itemparent">parent to attach to (such as the robot base frame)</param>
    ''' <returns>the new reference frame created</returns>
    Public Function AddFrame(name As String, Optional itemparent As Item = Nothing) As Item
        _check_connection()
        Dim command As String = "Add_FRAME"
        _send_line(command)
        _send_line(name)
        _send_item(itemparent)
        Dim newitem As Item = _rec_item()
        _check_status()
        Return newitem
    End Function

    ''' <summary>
    ''' Adds a new Program.
    ''' </summary>
    ''' <param name="name">name of the program</param>
    ''' <param name="itemrobot">robot that will be used</param>
    ''' <returns>the new program created</returns>
    Public Function AddProgram(name As String, Optional itemrobot As Item = Nothing) As Item
        _check_connection()
        Dim command As String = "Add_PROG"
        _send_line(command)
        _send_line(name)
        _send_item(itemrobot)
        Dim newitem As Item = _rec_item()
        _check_status()
        Return newitem
    End Function

    ''' <summary>
    ''' Adds a new machining project. Machining projects can also be used for 3D printing, curve following and point following.
    ''' </summary>
    ''' <param name="name">name of the machining project</param>
    ''' <param name="itemrobot">robot that will be used</param>
    ''' <returns>the new program created</returns>
    Public Function AddMillingProject(name As String, Optional itemrobot As Item = Nothing) As Item
        _check_connection()
        Dim command As String = "Add_MACHINING"
        _send_line(command)
        _send_line(name)
        _send_item(itemrobot)
        Dim newitem As Item = _rec_item()
        _check_status()
        Return newitem
    End Function

    '%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    ''' <summary>
    ''' Adds a function call in the program output. RoboDK will handle the syntax when the code is generated for a specific robot. If the program exists it will also run the program in simulate mode.
    ''' </summary>
    ''' <param name="function_w_params">Function name with parameters (if any)</param>
    ''' <returns></returns>
    Public Function RunProgram(function_w_params As String) As Integer
        Return RunCode(function_w_params, True)
    End Function

    ''' <summary>
    ''' Adds code to run in the program output. If the program exists it will also run the program in simulate mode.
    ''' </summary>
    ''' <param name="code"></param>
    ''' <param name="code_is_fcn_call"></param>
    ''' <returns></returns>
    Public Function RunCode(code As String, Optional code_is_fcn_call As Boolean = False) As Integer
        _check_connection()
        Dim command As String = "RunCode"
        _send_line(command)
        _send_int(If(code_is_fcn_call, 1, 0))
        _send_line(code)
        Dim prog_status As Integer = _rec_int()
        _check_status()
        Return prog_status
    End Function

    ''' <summary>
    ''' Shows a message or a comment in the output robot program.
    ''' </summary>
    ''' <param name="message"></param>
    ''' <param name="message_is_comment"></param>
    Public Sub RunMessage(message As String, Optional message_is_comment As Boolean = False)
        _check_connection()
        Dim command As String = "RunMessage"
        _send_line(command)
        _send_int(If(message_is_comment, 1, 0))
        _send_line(message)
        _check_status()
    End Sub

    ''' <summary>
    ''' Renders the scene. This function turns off rendering unless always_render is set to true.
    ''' </summary>
    ''' <param name="always_render"></param>
    Public Sub Render(Optional always_render As Boolean = False)
        Dim auto_render As Boolean = Not always_render
        _check_connection()
        Dim command As String = "Render"
        _send_line(command)
        _send_int(If(auto_render, 1, 0))
        _check_status()
    End Sub

    ''' <summary>
    ''' Returns (1/True) if object_inside is inside the object_parent
    ''' </summary>
    ''' <param name="object_inside"></param>
    ''' <param name="object_parent"></param>
    ''' <returns></returns>
    Public Function IsInside(object_inside As Item, object_parent As Item) As Boolean
        _check_connection()
        Dim command As String = "IsInside"
        _send_line(command)
        _send_item(object_inside)
        _send_item(object_parent)
        Dim inside As Integer = _rec_int()
        _check_status()
        Return inside > 0
    End Function

    ''' <summary>
    ''' Set collision checking ON or OFF (COLLISION_OFF/COLLISION_OFF) according to the collision map. If collision check is activated it returns the number of pairs of objects that are currently in a collision state.
    ''' </summary>
    ''' <param name="check_state"></param>
    ''' <returns>Number of pairs of objects in a collision state</returns>
    Public Function setCollisionActive(Optional check_state As Integer = COLLISION_ON) As Integer
        _check_connection()
        _send_line("Collision_SetState")
        _send_int(check_state)
        Dim ncollisions As Integer = _rec_int()
        _check_status()
        Return ncollisions
    End Function

    ''' <summary>
    ''' Set collision checking ON or OFF (COLLISION_ON/COLLISION_OFF) for a specific pair of objects. This allows altering the collision map for Collision checking. 
    ''' Specify the link id for robots or moving mechanisms (id 0 is the base).
    ''' </summary>
    ''' <param name="check_state">Set to COLLISION_ON or COLLISION_OFF</param>
    ''' <param name="item1">Item 1</param>
    ''' <param name="item2">Item 2</param>
    ''' <param name="id1">Joint id for Item 1 (if Item 1 is a robot or a mechanism)</param>
    ''' <param name="id2">Joint id for Item 2 (if Item 2 is a robot or a mechanism)</param>
    ''' <returns>Returns true if succeeded. Returns false if setting the pair failed (wrong id was provided)</returns>
    Public Function setCollisionActivePair(check_state As Integer, item1 As Item, item2 As Item, Optional id1 As Integer = 0, Optional id2 As Integer = 0) As Boolean
        _check_connection()
        Dim command As String = "Collision_SetPair"
        _send_line(command)
        _send_item(item1)
        _send_item(item2)
        _send_int(id1)
        _send_int(id2)
        _send_int(check_state)
        Dim success As Integer = _rec_int()
        _check_status()
        Return success > 0
    End Function

    ''' <summary>
    ''' Returns the number of pairs of objects that are currently in a collision state.
    ''' </summary>
    ''' <returns></returns>
    Public Function Collisions() As Integer
        _check_connection()
        Dim command As String = "Collisions"
        _send_line(command)
        Dim ncollisions As Integer = _rec_int()
        _check_status()
        Return ncollisions
    End Function

    ''' <summary>
    ''' Returns 1 if item1 and item2 collided. Otherwise returns 0.
    ''' </summary>
    ''' <param name="item1"></param>
    ''' <param name="item2"></param>
    ''' <returns>ncollisions</returns>
    Public Function Collision(item1 As Item, item2 As Item) As Boolean
        _check_connection()
        Dim command As String = "Collided"
        _send_line(command)
        _send_item(item1)
        _send_item(item2)
        Dim ncollisions As Integer = _rec_int()
        _check_status()
        Return ncollisions > 0
    End Function

    ''' <summary>
    ''' Sets the current simulation speed. Set the speed to 1 for a real-time simulation. The slowest speed allowed is 0.001 times the real speed. Set to a high value (>100) for fast simulation results.
    ''' </summary>
    ''' <param name="speed"></param>
    Public Sub setSimulationSpeed(speed As Double)
        _check_connection()
        Dim command As String = "SimulateSpeed"
        _send_line(command)
        _send_int(CInt(speed * 1000.0))
        _check_status()
    End Sub

    ''' <summary>
    ''' Gets the current simulation speed. Set the speed to 1 for a real-time simulation.
    ''' </summary>
    ''' <returns></returns>
    Public Function SimulationSpeed() As Double
        _check_connection()
        Dim command As String = "GetSimulateSpeed"
        _send_line(command)
        Dim speed As Double = CDbl(_rec_int()) / 1000.0
        _check_status()
        Return speed
    End Function

    ''' <summary>
    ''' Sets the behavior of the RoboDK API. By default, robodk shows the path simulation for movement instructions (run_mode=1=RUNMODE_SIMULATE).
    ''' Setting the run_mode to RUNMODE_QUICKVALIDATE allows performing a quick check to see if the path is feasible.
    ''' if robot.Connect() is used, RUNMODE_RUN_FROM_PC is selected automatically.
    ''' </summary>
    ''' <param name="run_mode">int = RUNMODE
    ''' RUNMODE_SIMULATE=1        performs the simulation moving the robot (default)
    ''' RUNMODE_QUICKVALIDATE=2   performs a quick check to validate the robot movements
    ''' RUNMODE_MAKE_ROBOTPROG=3  makes the robot program
    ''' RUNMODE_RUN_REAL=4        moves the real robot is it is connected</param>
    Public Sub setRunMode(Optional run_mode As Integer = 1)
        _check_connection()
        Dim command As String = "S_RunMode"
        _send_line(command)
        _send_int(run_mode)
        _check_status()
    End Sub

    ''' <summary>
    ''' Returns the behavior of the RoboDK API. By default, robodk shows the path simulation for movement instructions (run_mode=1)
    ''' </summary>
    ''' <returns>int = RUNMODE
    ''' RUNMODE_SIMULATE=1        performs the simulation moving the robot (default)
    ''' RUNMODE_QUICKVALIDATE=2   performs a quick check to validate the robot movements
    ''' RUNMODE_MAKE_ROBOTPROG=3  makes the robot program
    ''' RUNMODE_RUN_REAL=4        moves the real robot is it is connected</returns>
    Public Function RunMode() As Integer
        _check_connection()
        Dim command As String = "G_RunMode"
        _send_line(command)
        Dim runmode__1 As Integer = _rec_int()
        _check_status()
        Return runmode__1
    End Function

    ''' <summary>
    ''' Gets all the user parameters from the open RoboDK station.
    ''' The parameters can also be modified by right clicking the station and selecting "shared parameters"
    ''' User parameters can be added or modified by the user
    ''' </summary>
    ''' <returns>list of pairs of strings as parameter-value (list of a list)</returns>
    Public Function getParams() As List(Of List(Of String))
        _check_connection()
        Dim command As String = "G_Params"
        _send_line(command)
        Dim paramlist As New List(Of List(Of String))()
        Dim nparam As Integer = _rec_int()
        For i As Integer = 0 To nparam - 1
            Dim param As String = _rec_line()
            Dim value As String = _rec_line()

            Dim param_value As New List(Of String)()
            param_value.Add(param)
            param_value.Add(value)
            paramlist.Add(param_value)
        Next
        _check_status()
        Return paramlist
    End Function

    ''' <summary>
    ''' Gets a global or a user parameter from the open RoboDK station.
    ''' The parameters can also be modified by right clicking the station and selecting "shared parameters"
    ''' Some available parameters:
    ''' PATH_OPENSTATION = folder path of the current .stn file
    ''' FILE_OPENSTATION = file path of the current .stn file
    ''' PATH_DESKTOP = folder path of the user's folder
    ''' Other parameters can be added or modified by the user
    ''' </summary>
    ''' <param name="param">RoboDK parameter</param>
    ''' <returns>value</returns>
    Public Function getParam(param As String) As String
        _check_connection()
        Dim command As String = "G_Param"
        _send_line(command)
        _send_line(param)
        Dim value As String = _rec_line()
        If value.StartsWith("UNKNOWN ") Then
            value = Nothing
        End If
        _check_status()
        Return value
    End Function

    ''' <summary>
    ''' Sets a global parameter from the RoboDK station. If the parameters exists, it will be modified. If not, it will be added to the station.
    ''' The parameters can also be modified by right clicking the station and selecting "shared parameters"
    ''' </summary>
    ''' <param name="param">RoboDK parameter</param>
    ''' <param name="value">value</param>
    Public Sub setParam(param As String, value As String)
        _check_connection()
        Dim command As String = "S_Param"
        _send_line(command)
        _send_line(param)
        _send_line(value)
        _check_status()
    End Sub

    ''' <summary>
    ''' Displays a sequence of joints
    ''' </summary>
    ''' <param name="matrix">joint sequence as a 6xN matrix or instruction sequence as a 7xN matrix</param>
    Public Sub ShowSequence(matrix As Mat)
        '    """Displays a sequence of joints
        '    In  1 : joint sequence as a 6xN matrix or instruction sequence as a 7xN matrix"""
        getItem(0).ShowSequence(matrix)
    End Sub


    'def LaserTracker_Measure(self, estimate=[0,0,0], search=False):
    '    """Takes a laser tracker measurement with respect to the reference frame. If an estimate point is provided, the laser tracker will first move to those coordinates. If search is True, the tracker will search for a target.
    '    Returns the XYZ coordinates of target if it was found. Othewise it retuns None."""
    '    self._check_connection()
    '    command = 'MeasLT'
    '    self._send_line(command)
    '    self._send_xyz(estimate)
    '    self._send_int(1 if search else 0)
    '    xyz = self._rec_xyz()
    '    self._check_status()
    '    if xyz[0]*xyz[0] + xyz[1]*xyz[1] + xyz[2]*xyz[2] < 0.0001:
    '        return None

    '    return xyz        

    'def StereoCamera_Measure(self):
    '    """Takes a measurement with the C-Track stereocamera. Returns two poses, the base reference frame and the measured object reference frame. Status is 0 if measurement succeeded."""
    '    self._check_connection()
    '    command = 'MeasPose'
    '    self._send_line(command)
    '    pose1 = self._rec_pose()
    '    pose2 = self._rec_pose()
    '    npoints1 = self._rec_int()
    '    npoints2 = self._rec_int()
    '    time = self._rec_int()
    '    status = self._rec_int()
    '    self._check_status()        
    '    return pose1, pose2, npoints1, npoints2, time, status

    'def Collision_Line(self, p1, p2, ref=eye(4)):
    '    """Checks the collision between a line and the station. The line is composed by 2 points.
    '    In  1 : p1 -> start point of the line
    '    In  2 : p2 -> end point of the line
    '    In  3 : pose (optional) -> reference of the 2 points
    '    Out 1 : collision -> True if there is a collision, False otherwise
    '    Out 2 : item -> Item collided
    '    Out 3 : point -> collision point (station reference)"""
    '    p1abs = ref*p1;
    '    p2abs = ref*p2;        
    '    self._check_connection()
    '    command = 'CollisionLine'
    '    self._send_line(command)
    '    self._send_xyz(p1abs)
    '    self._send_xyz(p2abs)
    '    itempicked = self._rec_item()
    '    xyz = self._rec_xyz()
    '    collision = itempicked.Valid()
    '    self._check_status()
    '    return collision, itempicked, xyz

    'def setPoses(self, items, poses):
    '    """Sets the relative positions (poses) of a list of items with respect to their parent. For example, the position of an object/frame/target with respect to its parent.
    '    Use this function instead of setPose() for faster rendering.
    '    In 1 : List of items
    '    In 2 : List of poses"""
    '    if len(items) != len(poses):
    '        raise Exception('The number of items must match the number of poses')

    '    if len(items) == 0:
    '        return

    '    self._check_connection()
    '    command = 'S_Hlocals'
    '    self._send_line(command)
    '    self._send_int(len(items))
    '    for i in range(len(items)):
    '        self._send_item(items[i])
    '        self._send_pose(poses[i])
    '    self._check_status()


    'def setPosesAbs(self, items, poses):
    '    """Sets the absolute positions (poses) of a list of items with respect to the station reference. For example, the position of an object/frame/target with respect to its parent.
    '    Use this function instead of setPose() for faster rendering.
    '    In 1 : List of items
    '    In 2 : List of poses"""
    '    if len(items) != len(poses):
    '        raise Exception('The number of items must match the number of poses')

    '    if len(items) == 0:
    '        return

    '    self._check_connection()
    '    command = 'S_Hlocal_AbsS'
    '    self._send_line(command)
    '    self._send_int(len(items))
    '    for i in range(len(items)):
    '        self._send_item(items[i])
    '        self._send_pose(poses[i])
    '    self._check_status()
















    ''' <summary>
    ''' Returns the current joints of a list of robots.
    ''' </summary>
    ''' <param name="robot_item_list">list of robot items</param>
    ''' <returns>list of robot joints (double x nDOF)</returns>
    Public Function Joints(robot_item_list As Item()) As Double()()
        _check_connection()
        Dim command As String = "G_ThetasList"
        _send_line(command)
        Dim nrobs As Integer = robot_item_list.Length
        _send_int(nrobs)
        Dim joints_list As Double()() = New Double(nrobs - 1)() {}
        For i As Integer = 0 To nrobs - 1
            _send_item(robot_item_list(i))
            joints_list(i) = _rec_array()
        Next
        _check_status()
        Return joints_list
    End Function

    ''' <summary>
    ''' Sets the current robot joints for a list of robot items and a list of a set of joints.
    ''' </summary>
    ''' <param name="robot_item_list">list of robot items</param>
    ''' <param name="joints_list">list of robot joints (double x nDOF)</param>
    Public Sub setJoints(robot_item_list As Item(), joints_list As Double()())
        Dim nrobs As Integer = Math.Min(robot_item_list.Length, joints_list.Length)
        _check_connection()
        Dim command As String = "S_ThetasList"
        _send_line(command)
        _send_int(nrobs)
        For i As Integer = 0 To nrobs - 1
            _send_item(robot_item_list(i))
            _send_array(joints_list(i))
        Next
        _check_status()
    End Sub

    ''' <summary>
    ''' Calibrate a tool (TCP) given a number of points or calibration joints. Important: If the robot is calibrated, provide joint values to maximize accuracy.
    ''' </summary>
    ''' <param name="poses_joints">matrix of poses in a given format or a list of joints</param>
    ''' <param name="error_stats">stats[mean, standard deviation, max] - Output error stats summary</param>
    ''' <param name="format">Euler format. Optionally, use JOINT_FORMAT and provide the robot.</param>
    ''' <param name="algorithm">type of algorithm (by point, plane, ...)</param>
    ''' <param name="robot">Robot used for calibration (if using joint values)</param>
    ''' <returns>TCP as [x, y, z] - calculated TCP</returns>
    ''' 
    Public Function CalibrateTool(poses_joints As Mat, ByRef error_stats As Double(), Optional format As Integer = EULER_RX_RY_RZ, Optional algorithm As Integer = CALIBRATE_TCP_BY_POINT, Optional robot As Item = Nothing) As Double()
        _check_connection()
        Dim command As String = "CalibTCP2"
        _send_line(command)
        _send_matrix(poses_joints)
        _send_int(format)
        _send_int(algorithm)
        _send_item(robot)
        Dim tcp As Double() = _rec_array()
        error_stats = _rec_array()
        Dim error_graph As Mat = _rec_matrix()
        _check_status()
        Return tcp
        'errors = errors[:, 1].tolist()
    End Function

    ''' <summary>
    ''' Calibrate a Reference Frame given a list of points or joint values. Important: If the robot is calibrated, provide joint values to maximize accuracy.
    ''' </summary>
    ''' <param name="joints">points as a 3xN matrix or nDOFsxN) - List of points or a list of robot joints</param>
    ''' <param name="method">type of algorithm(by point, plane, ...) CALIBRATE_FRAME_...</param>
    ''' <param name="use_joints">use points or joint values. The robot item must be provided if joint values is used.</param>
    ''' <param name="robot"></param>
    ''' <returns></returns>
    Public Function CalibrateReference(joints As Mat, Optional method As Integer = CALIBRATE_FRAME_3P_P1_ON_X, Optional use_joints As Boolean = False, Optional robot As Item = Nothing) As Mat
        _check_connection()
        Dim command As String = "CalibFrame"
        _send_line(command)
        _send_matrix(joints)
        _send_int(If(use_joints, -1, 0))
        _send_int(method)
        _send_item(robot)
        Dim reference_pose As Mat = _rec_pose()
        Dim error_stats As Double() = _rec_array()
        _check_status()
        'errors = errors[:, 1].tolist()
        Return reference_pose
    End Function

    ''' <summary>
    ''' Defines the name of the program when the program is generated. It is also possible to specify the name of the post processor as well as the folder to save the program. 
    ''' This method must be called before any program output is generated (before any robot movement or other instruction).
    ''' </summary>
    ''' <param name="progname">name of the program</param>
    ''' <param name="defaultfolder">folder to save the program, leave empty to use the default program folder</param>
    ''' <param name="postprocessor">name of the post processor (for a post processor in C:/RoboDK/Posts/Fanuc_post.py it is possible to provide "Fanuc_post.py" or simply "Fanuc_post")</param>
    ''' <param name="robot">Robot to link</param>
    ''' <returns></returns>
    Public Function ProgramStart(progname As String, Optional defaultfolder As String = "", Optional postprocessor As String = "", Optional robot As Item = Nothing) As Integer
        _check_connection()
        Dim command As String = "ProgramStart"
        _send_line(command)
        _send_line(progname)
        _send_line(defaultfolder)
        _send_line(postprocessor)
        _send_item(robot)
        Dim errors As Integer = _rec_int()
        _check_status()
        Return errors
    End Function

    ''' <summary>
    ''' Set the pose of the wold reference frame with respect to the view (camera/screen)
    ''' </summary>
    ''' <param name="pose"></param>
    Public Sub setViewPose(pose As Mat)
        _check_connection()
        Dim command As String = "S_ViewPose"
        _send_line(command)
        _send_pose(pose)
        _check_status()
    End Sub

    ''' <summary>
    ''' Get the pose of the wold reference frame with respect to the view (camera/screen)
    ''' </summary>
    Public Function ViewPose() As Mat
        _check_connection()
        Dim command As String = "G_ViewPose"
        _send_line(command)
        Dim pose As Mat = _rec_pose()
        _check_status()
        Return pose
    End Function


    '#------------------------------------------------------------------
    '#----------------------- CAMERA VIEWS ----------------------------
    'def Cam2D_Add(self, item_object, cam_params=""):
    '    """Adds a 2D camera view.
    '    In  1 : Parameters of the camera 
    '    Out 1 : camera handle pointer"""
    '    self._check_connection()
    '    command = 'Cam2D_Add'
    '    self._send_line(command)
    '    self._send_item(item_object)
    '    self._send_line(cam_params)
    '    cam_handle = self._rec_ptr()
    '    self._check_status()
    '    return cam_handle

    'def Cam2D_Snapshot(self, file_save_img, cam_handle=0):
    '    """Returns the current joints of a list of robots.
    '    In  1 : Parameters of the camera 
    '    Out 1 :  1 if success, 0 otherwise"""
    '    self._check_connection()
    '    command = 'Cam2D_Snapshot'
    '    self._send_line(command)
    '    self._send_ptr(int(cam_handle))
    '    self._send_line(file_save_img)        
    '    success = self._rec_int()
    '    self._check_status()
    '    return success

    'def Cam2D_Close(self, cam_handle=0):
    '    """Closes all camera windows or one specific camera if the camera handle is provided.
    '    In  1 : Camera handle (optional)
    '    Out 1 : 1 if success, 0 otherwise"""
    '    self._check_connection()
    '    if cam_handle == 0:
    '        command = 'Cam2D_CloseAll'
    '        self._send_line(command)
    '    else:
    '        command = 'Cam2D_Close'
    '        self._send_line(command)
    '        self._send_ptr(cam_handle)
    '    success = self._rec_int()
    '    self._check_status()
    '    return success

    'def Cam2D_SetParams(self, params, cam_handle=0):
    '    """Set the parameters of the camera.
    '    In  1 : Parameters of the camera 
    '    Out 1 :  1 if success, 0 otherwise"""
    '    self._check_connection()
    '    command = 'Cam2D_SetParams'
    '    self._send_line(command)
    '    self._send_ptr(int(cam_handle))
    '    self._send_line(params)        
    '    success = self._rec_int()
    '    self._check_status()
    '    return success

    '#------------------------------------------------------------------
    '#----------------------- SPRAY GUN SIMULATION ----------------------------
    'def Spray_Add(self, item_tool=0, item_object=0, params="", points=None, geometry=None):
    '    """Adds spray gun"""
    '    self._check_connection()
    '    command = 'Gun_Add'
    '    self._send_line(command)
    '    self._send_item(item_tool)
    '    self._send_item(item_object)        
    '    self._send_line(params)
    '    self._send_matrix(points)
    '    self._send_matrix(geometry)        
    '    id_spray = self._rec_int()
    '    self._check_status()
    '    return id_spray

    'def Spray_SetState(self, state=SPRAY_ON, id_spray=-1):
    '    """Sets the state of a spray gun"""
    '    self._check_connection()
    '    command = 'Gun_SetState'
    '    self._send_line(command)
    '    self._send_int(id_spray)
    '    self._send_int(state)        
    '    success = self._rec_int()
    '    self._check_status()
    '    return success

    'def Spray_GetStats(self, id_spray=-1):
    '    """Gets statistics about spray guns"""
    '    self._check_connection()
    '    command = 'Gun_Stats'
    '    self._send_line(command)
    '    self._send_int(id_spray)
    '    info = self._rec_line()
    '    info.replace('<br>','\t')
    '    print(info)
    '    data = self._rec_matrix()
    '    self._check_status()
    '    return info, data

    'def Spray_Clear(self, id_spray=-1):
    '    """Stops simulating a spray gun"""
    '    self._check_connection()
    '    command = 'Gun_Clear'
    '    self._send_line(command)
    '    self._send_int(id_spray)
    '    success = self._rec_int()
    '    self._check_status()
    '    return success



    ''' <summary>
    ''' The Item class represents an item in RoboDK station. An item can be a robot, a frame, a tool, an object, a target, ... any item visible in the station tree.
    ''' An item can also be seen as a node where other items can be attached to (child items).
    ''' Every item has one parent item/node and can have one or more child items/nodes
    ''' RoboLinkItem is a "friend" class of RoboLink.
    ''' </summary>
    Public Class Item
        Public ID As UInt64 = 0
        Private link As RoboDK ' pointer to the RoboLink connection
        Private _type As Integer = -1

        Public Sub New(ByRef connection_link As RoboDK, Optional item_ptr As UInt64 = 0, Optional itemtype As Integer = -1)
            ID = item_ptr
            link = connection_link
            _type = itemtype
        End Sub

        Public Function ToString2() As String
            If Valid() Then
                Return [String].Format("RoboDK item {0} of type {1}", ID, _type)
            Else
                Return "RoboDK item (INVALID)"
            End If
        End Function

        ''' <summary>
        ''' Returns an integer that represents the type of the item (robot, object, tool, frame, ...)
        ''' Compare the returned value to ITEM_CASE_* variables
        ''' </summary>
        ''' <param name="item_other"></param>
        ''' <returns></returns>
        Public Shadows Function Equals(item_other As Item) As Boolean
            Return Me.ID = item_other.ID
        End Function

        ''' <summary>
        ''' Returns the RoboDK link Robolink().
        ''' </summary>
        ''' <returns></returns>
        Public Function RDK() As RoboDK
            Return link
        End Function

        ''' <summary>
        ''' Returns the RoboDK link Robolink (old version)().
        ''' </summary>
        ''' <returns></returns>
        Public Function RL() As RoboDK
            Return link
        End Function

        '''///// GENERIC ITEM CALLS
        ''' <summary>
        ''' Returns the type of an item (robot, object, target, reference frame, ...)
        ''' </summary>
        ''' <returns></returns>
        Public Function Type() As Integer
            link._check_connection()
            Dim command As String = "G_Item_Type"
            link._send_line(command)
            link._send_item(Me)
            Dim itemtype As Integer = link._rec_int()
            link._check_status()
            Return itemtype
        End Function

        '/// add more methods

        ''' <summary>
        ''' Copy the item to the clipboard (same as Ctrl+C). Use together with Paste() to duplicate items.
        ''' </summary>
        Public Sub Copy()
            link.Copy(Me)
        End Sub

        ''' <summary>
        ''' Paste the item from the clipboard as a child of this item (same as Ctrl+V)
        ''' </summary>
        Public Function Paste() As Item
            Return link.Paste(Me)
        End Function

        ''' <summary>
        ''' Adds an object as a child of this object
        ''' </summary>
        ''' <param name="filename"></param>
        Public Function AddFile(filename As String) As Item
            Return link.AddFile(filename)
        End Function

        ''' <summary>
        ''' Save a station or object to a file
        ''' </summary>
        ''' <param name="filename"></param>
        Public Sub Save(filename As String)
            link.Save(filename, Me)
        End Sub


        ''' <summary>
        ''' Checks if this item is in a collision state with another item
        ''' </summary>
        ''' <param name="item_check"></param>
        Public Function Collision(item_check As Item) As Boolean
            Return link.Collision(Me, item_check)
        End Function

        ''' <summary>
        ''' Returns True if the object is inside the provided object
        ''' </summary>
        ''' <param name="item_check"></param>
        Public Function IsInside(item_check As Item) As Boolean
            Return link.IsInside(Me, item_check)
        End Function

        ''' <summary>
        ''' Makes a copy of the geometry fromitem adding it at a given position (pose) relative to this item.
        ''' </summary>
        Public Sub AddGeometry(fromitem As Item, pose As Mat)
            link._check_connection()
            Dim command As String = "CopyFaces"
            link._send_line(command)
            link._send_item(fromitem)
            link._send_item(Me)
            link._send_pose(pose)
            link._check_status()
        End Sub

        ''' <summary>
        ''' Deletes an item and its childs from the station.
        ''' </summary>
        Public Sub Delete()
            link._check_connection()
            Dim command As String = "Remove"
            link._send_line(command)
            link._send_item(Me)
            link._check_status()
            ID = 0
        End Sub

        ''' <summary>
        ''' Checks if the item is valid. An invalid item will be returned by an unsuccessful function call.
        ''' </summary>
        ''' <returns>true if valid, false if invalid</returns>
        Public Function Valid() As Boolean
            If ID = 0 Then
                Return False
            End If
            Return True
        End Function

        '/// add more methods

        ''' <summary>
        ''' Moves the item to another location (parent) without changing the current position in the station
        ''' </summary>
        ''' <param name="parent"> parent to attach the item</param>
        Public Sub setParentStatic(parent As Item)
            link._check_connection()
            Dim command As String = "S_Parent_Static"
            link._send_line(command)
            link._send_item(Me)
            link._send_item(parent)
            link._check_status()
        End Sub

        ''' <summary>
        ''' Attaches the closest object to the provided tool (see also: Set_Parent_Static).
        ''' </summary>
        ''' <returns> the item that was attached (item.Valid() is False if none found)</returns>
        Public Function AttachClosest() As Item
            link._check_connection()
            Dim command As String = "Attach_Closest"
            link._send_line(command)
            link._send_item(Me)
            Dim item_attached As Item = link._rec_item()
            link._check_status()
            Return item_attached
        End Function

        ''' <summary>
        ''' Detaches the closest object attached to the tool (see also: setParentStatic).
        ''' </summary>
        ''' <param name="parent"></param>
        ''' <returns> the item that was detached (item.Valid() is False if none found)</returns>
        Public Function DetachClosest(Optional parent As Item = Nothing)
            link._check_connection()
            Dim command As String = "Detach_Closest"
            link._send_line(command)
            link._send_item(Me)
            link._send_item(parent)
            Dim item_detached As Item = link._rec_item()
            link._check_status()
            Return item_detached
        End Function

        ''' <summary>
        ''' Detaches any object attached to a tool (see also: setParentStatic).
        ''' </summary>
        ''' <param name="parent"></param>
        Public Sub DetachAll(Optional parent As Item = Nothing)
            link._check_connection()
            Dim command As String = "Detach_All"
            link._send_line(command)
            link._send_item(Me)
            link._send_item(parent)
            link._check_status()
        End Sub

        ''' <summary>
        ''' Returns the parent item of the item.
        ''' </summary>
        ''' <returns>the parent item of the item.</returns>
        Public Function Parent() As Item
            link._check_connection()
            Dim command As String = "G_Parent"
            link._send_line(command)
            link._send_item(Me)
            Dim parentItem As Item = link._rec_item()
            link._check_status()
            Return parentItem
        End Function


        ''' <summary>
        ''' Returns a list of the item childs that are attached to the provided item.
        ''' </summary>
        ''' <returns>item x n -> list of child items</returns>
        Public Function Childs() As Item()
            link._check_connection()
            Dim command As String = "G_Childs"
            link._send_line(command)
            link._send_item(Me)
            Dim nitems As Integer = link._rec_int()
            Dim itemlist As Item() = New Item(nitems - 1) {}
            For i As Integer = 0 To nitems - 1
                itemlist(i) = link._rec_item()
            Next
            link._check_status()
            Return itemlist
        End Function

        ''' <summary>
        ''' Returns 1 if the item is visible, otherwise, returns 0.
        ''' </summary>
        ''' <returns>true if visible, false if not visible</returns>
        Public Function Visible() As Boolean
            link._check_connection()
            Dim command As String = "G_Visible"
            link._send_line(command)
            link._send_item(Me)
            Dim visible__1 As Integer = link._rec_int()
            link._check_status()
            Return (visible__1 <> 0)
        End Function
        ''' <summary>
        ''' Sets the item visiblity status
        ''' </summary>
        ''' <param name="visible"></param>
        ''' <param name="visible_frame">srt the visible reference frame (1) or not visible (0)</param>
        Public Sub setVisible(visible As Boolean, Optional visible_frame As Integer = -1)
            If visible_frame < 0 Then
                visible_frame = If(visible, 1, 0)
            End If
            link._check_connection()
            Dim command As String = "S_Visible"
            link._send_line(command)
            link._send_item(Me)
            link._send_int(If(visible, 1, 0))
            link._send_int(visible_frame)
            link._check_status()
        End Sub

        ''' <summary>
        ''' Returns the name of an item. The name of the item is always displayed in the RoboDK station tree
        ''' </summary>
        ''' <returns>name of the item</returns>
        Public Function Name() As String
            link._check_connection()
            Dim command As String = "G_Name"
            link._send_line(command)
            link._send_item(Me)
            Dim _name As String = link._rec_line()
            link._check_status()
            Return _name
        End Function

        ''' <summary>
        ''' Set the name of a RoboDK item.
        ''' </summary>
        ''' <param name="name"></param>
        Public Sub setName(name As String)
            link._check_connection()
            Dim command As String = "S_Name"
            link._send_line(command)
            link._send_item(Me)
            link._send_line(name)
            link._check_status()
        End Sub

        ' add more methods
        ''' <summary>
        ''' Sets a any property value to an item.
        ''' </summary>
        ''' <param name="varname">string</param>
        ''' <param name="value">matrix</param>
        Public Sub setValue(varname As String, value As Mat)
            link._check_connection()
            Dim command As String = "S_Gen_Mat"
            link._send_line(command)
            link._send_item(Me)
            link._send_line(varname)
            link._send_matrix(value)
            link._check_status()
        End Sub

        ''' <summary>
        ''' Sets a any property value to an item.
        ''' </summary>
        ''' <param name="varname">string</param>
        ''' <param name="value">string</param>
        Public Sub setValue(varname As String, value As String)
            link._check_connection()
            Dim command As String = "S_Gen_Str"
            link._send_line(command)
            link._send_item(Me)
            link._send_line(varname)
            link._send_line(value)
            link._check_status()
        End Sub

        ''' <summary>
        ''' Sets the local position (pose) of an object, target or reference frame. For example, the position of an object/frame/target with respect to its parent.
        ''' If a robot is provided, it will set the pose of the end efector.
        ''' </summary>
        ''' <param name="pose">4x4 homogeneous matrix</param>
        Public Sub setPose(pose As Mat)
            link._check_connection()
            Dim command As String = "S_Hlocal"
            link._send_line(command)
            link._send_item(Me)
            link._send_pose(pose)
            link._check_status()
        End Sub

        ''' <summary>
        ''' Returns the local position (pose) of an object, target or reference frame. For example, the position of an object/frame/target with respect to its parent.
        ''' If a robot is provided, it will get the pose of the end efector
        ''' </summary>
        ''' <returns>4x4 homogeneous matrix (pose)</returns>
        Public Function Pose() As Mat
            link._check_connection()
            Dim command As String = "G_Hlocal"
            link._send_line(command)
            link._send_item(Me)
            Dim pose__1 As Mat = link._rec_pose()
            link._check_status()
            Return pose__1
        End Function

        ''' <summary>
        ''' Sets the position (pose) the object geometry with respect to its own reference frame. This procedure works for tools and objects.
        ''' </summary>
        ''' <param name="pose">4x4 homogeneous matrix</param>
        Public Sub setGeometryPose(pose As Mat)
            link._check_connection()
            Dim command As String = "S_Hgeom"
            link._send_line(command)
            link._send_item(Me)
            link._send_pose(pose)
            link._check_status()
        End Sub

        ''' <summary>
        ''' Returns the position (pose) the object geometry with respect to its own reference frame. This procedure works for tools and objects.
        ''' </summary>
        ''' <returns>4x4 homogeneous matrix (pose)</returns>
        Public Function GeometryPose() As Mat
            link._check_connection()
            Dim command As String = "G_Hgeom"
            link._send_line(command)
            link._send_item(Me)
            Dim pose As Mat = link._rec_pose()
            link._check_status()
            Return pose
        End Function

        ''' <summary>
        ''' Sets the global position (pose) of an item. For example, the position of an object/frame/target with respect to the station origin.
        ''' </summary>
        ''' <param name="pose">4x4 homogeneous matrix (pose)</param>
        Public Sub setPoseAbs(pose As Mat)
            link._check_connection()
            Dim command As String = "S_Hlocal_Abs"
            link._send_line(command)
            link._send_item(Me)
            link._send_pose(pose)
            link._check_status()
        End Sub

        ''' <summary>
        ''' Returns the global position (pose) of an item. For example, the position of an object/frame/target with respect to the station origin.
        ''' </summary>
        ''' <returns>4x4 homogeneous matrix (pose)</returns>
        Public Function PoseAbs() As Mat
            link._check_connection()
            Dim command As String = "G_Hlocal_Abs"
            link._send_line(command)
            link._send_item(Me)
            Dim pose As Mat = link._rec_pose()
            link._check_status()
            Return pose
        End Function

        ''' <summary>
        ''' Changes the color of a robot/object/tool. A color must must in the format COLOR=[R,G,B,(A=1)] where all values range from 0 to 1.
        ''' Alpha (A) defaults to 1 (100% opaque). Set A to 0 to make an object transparent.
        ''' </summary>
        ''' <param name="tocolor">color to change to</param>
        ''' <param name="fromcolor">filter by this color</param>
        ''' <param name="tolerance">optional tolerance to use if a color filter is used (defaults to 0.1)</param>
        Public Sub Recolor(tocolor As Double(), Optional fromcolor As Double() = Nothing, Optional tolerance As Double = 0.1)
            link._check_connection()
            If fromcolor Is Nothing Then
                fromcolor = New Double() {0, 0, 0, 0}
                tolerance = 2
            End If
            link._check_color(tocolor)
            link._check_color(fromcolor)
            Dim command As String = "Recolor"
            link._send_line(command)
            link._send_item(Me)
            Dim combined As Double() = New Double(8) {}
            combined(0) = tolerance
            Array.Copy(fromcolor, 0, combined, 1, 4)
            Array.Copy(tocolor, 0, combined, 5, 4)
            link._send_array(combined)
            link._check_status()
        End Sub


        ''' <summary>
        ''' Set the color of an object, tool or robot. A color must must in the format COLOR=[R,G,B,(A=1)] where all values range from 0 to 1.
        ''' Alpha (A) defaults to 1 (100% opaque). Set A to 0 to make an object transparent.
        ''' </summary>
        ''' <param name="tocolor">color to change to</param>
        Public Sub setColor(tocolor As Double())
            link._check_connection()
            If link._check_color(tocolor) Then
                Dim command As String = "S_Color"
                link._send_line(command)
                link._send_item(Me)
                link._send_array(tocolor)
                link._check_status()
            End If
        End Sub

        ''' <summary>
        ''' Returns the color of an object, tool or robot (first color found). A color is in the format COLOR=[R,G,B,(A=1)] where all values range from 0 to 1.
        ''' </summary>
        ''' <returns>the color as a list of Double of an object, tool or robot (first color found). A color is in the format COLOR=[R,G,B,(A=1)] where all values range from 0 to 1.</returns>
        Public Function Color() As List(Of Double)
            link._check_connection()
            Dim command As String = "G_Color"
            link._send_line(command)
            link._send_item(Me)
            Dim ColorArray As Double() = link._rec_array()
            link._check_status()
            Return ColorArray.ToList()
        End Function


        ''' <summary>
        ''' Apply a scale to an object to make it bigger or smaller.
        ''' The scale can be uniform (if scale is a float value) or per axis (if scale is a vector).
        ''' </summary>
        ''' <param name="scale__1">scale to apply as [scale_x, scale_y, scale_z]</param>
        Public Sub Scale(scale__1 As Double())
            link._check_connection()
            If scale__1.Length <> 3 Then
                Throw New RDKException("scale must be a single value or a 3-vector value")
            End If
            Dim command As String = "Scale"
            link._send_line(command)
            link._send_item(Me)
            link._send_array(scale__1)
            link._check_status()
        End Sub

        '#"""Object specific calls"""

        ''' <summary>
        ''' Adds a shape to the object provided some triangle coordinates. Triangles must be provided as a list of vertices. A vertex normal can be provided optionally
        ''' </summary>
        ''' <param name="triangle_points">matrix 3xN or 6xN -> N must be multiple of 3 because vertices must be stacked by groups of 3. Each group is a triangle.</param>
        ''' <returns>returns the object where the curve was added or null if failed</returns>
        Public Function AddShape(triangle_points As Mat) As Item
            '"""Adds a shape to the object provided some triangle coordinates. Triangles must be provided as a list of vertices. A vertex normal can be provided optionally.
            'In 1  : matrix 3xN or 6xN -> N must be multiple of 3 because vertices must be stacked by groups of 3. Each group is a triangle."""
            Return link.AddShape(triangle_points, Me)
        End Function

        ''' <summary>
        ''' Adds a curve provided point coordinates. The provided points must be a list of vertices. A vertex normal can be provided optionally.
        ''' </summary>
        ''' <param name="curve_points">matrix 3xN or 6xN -> N must be multiple of 3</param>
        ''' <param name="add_to_ref">add_to_ref -> If True, the curve will be added as part of the object in the RoboDK item tree</param>
        ''' <param name="projection_type">Type of projection. For example: PROJECTION_ALONG_NORMAL_RECALC will project along the point normal and recalculate the normal vector on the surface projected.</param>
        ''' <returns>returns the object where the curve was added or null if failed</returns>
        Public Function AddCurve(curve_points As Mat, Optional add_to_ref As Boolean = False, Optional projection_type As Integer = PROJECTION_ALONG_NORMAL_RECALC) As Item
            Return link.AddCurve(curve_points, Me, add_to_ref, projection_type)
        End Function

        ''' <summary>
        ''' Adds a list of points to an object. The provided points must be a list of vertices. A vertex normal can be provided optionally.
        ''' </summary>
        ''' <param name="points">matrix 3xN or 6xN -> N must be multiple of 3</param>
        ''' <param name="add_to_ref">add_to_ref -> If True, the curve will be added as part of the object in the RoboDK item tree</param>
        ''' <param name="projection_type">Type of projection. For example: PROJECTION_ALONG_NORMAL_RECALC will project along the point normal and recalculate the normal vector on the surface projected.</param>
        ''' <returns>returns the object where the curve was added or null if failed</returns>
        Public Function AddPoints(points As Mat, Optional add_to_ref As Boolean = False, Optional projection_type As Integer = PROJECTION_ALONG_NORMAL_RECALC) As Item
            Return link.AddPoints(points, Me, add_to_ref, projection_type)
        End Function

        ''' <summary>
        ''' Projects a point to the object given its coordinates. The provided points must be a list of [XYZ] coordinates. Optionally, a vertex normal can be provided [XYZijk].
        ''' </summary>
        ''' <param name="points">matrix 3xN or 6xN -> list of points to project</param>
        ''' <param name="projection_type">projection_type -> Type of projection. For example: PROJECTION_ALONG_NORMAL_RECALC will project along the point normal and recalculate the normal vector on the surface projected.</param>
        ''' <returns>projected points (empty matrix if failed)</returns>
        Public Function ProjectPoints(points As Mat, Optional projection_type As Integer = PROJECTION_ALONG_NORMAL_RECALC) As Mat
            Return link.ProjectPoints(points, Me, projection_type)
        End Function

        ''' <summary>
        ''' Is the item selected.
        ''' </summary>
        ''' <param name="feature_type">FEATURE_CURVE if the last point selected was a wire, FEATURE_POINT if the last feature selected was a point or FEATURE_SURFACE otherwise.</param>
        ''' <param name="feature_id">index of the curve or point in the object</param>
        ''' <returns>is_selected as boolean</returns>
        Public Function SelectedFeature(ByRef feature_type As Integer, feature_id As Integer) As Boolean
            link._check_connection()
            Dim command As String = "G_ObjSelection"
            link._send_line(command)
            link._send_item(Me)
            Dim is_selected As Integer = link._rec_int()
            feature_type = link._rec_int()
            feature_id = link._rec_int()
            link._check_status()
            Return is_selected > 0
        End Function

        'def GetPoints(self, feature_type=FEATURE_SURFACE, feature_id=0):
        '    """Retrieves the point under the mouse cursor, a curve or the 3D points of an object. The points are provided in [XYZijk] format, where the XYZ is the point coordinate and ijk is the surface normal.
        '    In 1  : feature_type (int) -> set to FEATURE_SURFACE to retrieve the point under the mouse cursor, FEATURE_CURVE to retrieve the list of points for that wire, or FEATURE_POINT to retrieve the list of points.
        '    In 2  : feature_id -> used only if FEATURE_CURVE is specified, it allows retrieving the appropriate curve id of an object
        '    Out 1 : List of points"""
        '    self.link._check_connection()
        '    command = 'G_ObjPoint'
        '    self.link._send_line(command)
        '    self.link._send_item(self)
        '    self.link._send_int(feature_type)
        '    self.link._send_int(feature_id)        
        '    points = self.link._rec_matrix()
        '    feature_name = self.link._rec_line()
        '    self.link._check_status()
        '    return points.tr().rows, feature_name


        ''' <summary>
        ''' Adds a new machining project. Machining projects can also be used for 3D printing, curve following and point following.
        ''' </summary>
        ''' <param name="ncfile">name of the project</param>
        ''' <param name="part">(optional): item -> curve or point object to automatically set up a curve/point follow project</param>
        ''' <param name="params"></param>
        ''' <returns>newprog created</returns>
        Public Function setMillingParameters(ncfile As String, ByRef status As Integer, Optional part As Item = Nothing, Optional params As String = "") As Item
            link._check_connection()
            Dim command As String = "S_MachiningParams"
            link._send_line(command)
            link._send_item(Me)
            link._send_line(ncfile)
            link._send_item(part)
            link._send_line(params)
            link.COM.ReceiveTimeout = 3600 * 1000
            Dim newprog As Item = link._rec_item()
            link.COM.ReceiveTimeout = link.TIMEOUT
            status = link._rec_int() / 1000.0
            link._check_status()
            Return newprog
        End Function


        '"""Target item calls"""

        ''' <summary>
        ''' Sets a target as a cartesian target. A cartesian target moves to cartesian coordinates.
        ''' </summary>
        Public Sub setAsCartesianTarget()
            link._check_connection()
            Dim command As String = "S_Target_As_RT"
            link._send_line(command)
            link._send_item(Me)
            link._check_status()
        End Sub

        ''' <summary>
        ''' Sets a target as a joint target. A joint target moves to a joints position without regarding the cartesian coordinates.
        ''' </summary>
        Public Sub setAsJointTarget()
            link._check_connection()
            Dim command As String = "S_Target_As_JT"
            link._send_line(command)
            link._send_item(Me)
            link._check_status()
        End Sub

        '#####Robot item calls####

        ''' <summary>
        ''' Returns the current joints of a robot or the joints of a target. If the item is a cartesian target, it returns the preferred joints (configuration) to go to that cartesian position.
        ''' </summary>
        ''' <returns>double x n -> joints matrix</returns>
        Public Function Joints() As Double()
            link._check_connection()
            Dim command As String = "G_Thetas"
            link._send_line(command)
            link._send_item(Me)
            Dim joints__1 As Double() = link._rec_array()
            link._check_status()
            Return joints__1
        End Function

        ' add more methods

        '    def JointPoses(self, joints = None):
        '"""Returns the positions of the joint links for a provided robot configuration (joints). If no joints are provided it will return the poses for the current robot position.
        'Out 1 : 4x4 x n -> array of 4x4 homogeneous matrices. Index 0 is the base frame reference (it never moves when the joints move).
        '"""
        'self.link._check_connection()
        'command = 'G_LinkPoses'
        'self.link._send_line(command)
        'self.link._send_item(self)
        'if joints is None:
        '    self.link._send_array([])
        'else:
        '    self.link._send_array(joints)

        'nlinks = self.link._rec_int()
        'poses = []
        'for i in range(nlinks):
        '    poses.append(self.link._rec_pose())

        'self.link._check_status()
        'return poses


        ''' <summary>
        ''' Returns the home joints of a robot. These joints can be manually set in the robot "Parameters" menu, then select "Set home position"
        ''' </summary>
        ''' <returns>double x n -> joints array</returns>
        Public Function JointsHome() As Double()
            link._check_connection()
            Dim command As String = "G_Home"
            link._send_line(command)
            link._send_item(Me)
            Dim joints As Double() = link._rec_array()
            link._check_status()
            Return joints
        End Function

        ''' <summary>
        ''' Returns an item pointer to the link id (0 for the robot base, 1 for the first link, ...).
        ''' This is useful if we want to show/hide certain links or change their geometry.
        ''' </summary>
        ''' <returns>item object (pointer) to the robot link</returns>
        Public Function ObjectLink(Optional link_id As Integer = 0) As Item
            link._check_connection()
            Dim command As String = "G_LinkObjId"
            link._send_line(command)
            link._send_item(Me)
            link._send_int(link_id)
            Dim linkedItem = link._rec_item()
            link._check_status()
            Return linkedItem
        End Function

        ''' <summary>
        ''' Sets the current joints of a robot or the joints of a target. It the item is a cartesian target, it returns the preferred joints (configuration) to go to that cartesian position.
        ''' </summary>
        ''' <param name="joints"></param>
        Public Sub setJoints(joints As Double())
            link._check_connection()
            Dim command As String = "S_Thetas"
            link._send_line(command)
            link._send_array(joints)
            link._send_item(Me)
            link._check_status()
        End Sub

        ''' <summary>
        ''' Returns the joint limits of a robot
        ''' </summary>
        ''' <param name="lower_limits"></param>
        ''' <param name="upper_limits"></param>
        Public Sub JointLimits(lower_limits As Double(), upper_limits As Double())
            link._check_connection()
            Dim command As String = "G_RobLimits"
            link._send_line(command)
            link._send_item(Me)
            lower_limits = link._rec_array()
            upper_limits = link._rec_array()
            Dim joints_type As Double = link._rec_int() / 1000.0
            link._check_status()
        End Sub

        ''' <summary>
        ''' Set the robot joint limits
        ''' </summary>
        ''' <param name="lower_limit"></param>
        ''' <param name="upper_limit"></param>
        Public Sub setJointLimits(lower_limit As Double(), upper_limit As Double())
            link._check_connection()
            Dim command As String = "S_RobLimits"
            link._send_line(command)
            link._send_item(Me)
            link._send_array(lower_limit)
            link._send_array(upper_limit)
            link._check_status()
        End Sub

        ''' <summary>
        ''' Sets the robot of a program or a target. You must set the robot linked to a program or a target every time you copy paste these objects.
        ''' If the robot is not provided, the first available robot will be chosen automatically.
        ''' </summary>
        ''' <param name="robot">Robot item</param>
        Public Sub setRobot(Optional robot As Item = Nothing)
            link._check_connection()
            Dim command As String = "S_Robot"
            link._send_line(command)
            link._send_item(Me)
            link._send_item(robot)
            link._check_status()
        End Sub

        ''' <summary>
        ''' Obsolete: Use setPoseFrame instead.
        ''' Sets the frame of a robot (user frame). The frame can be either an item or a 4x4 Matrix.
        ''' If "frame" is an item, it links the robot to the frame item. If frame is a 4x4 Matrix, it updates the linked pose of the robot frame.
        ''' </summary>
        ''' <param name="frame">item/pose -> frame item or 4x4 Matrix (pose of the reference frame)</param>
        Public Sub setFrame(frame As Item)
            setPoseFrame(frame)
        End Sub

        ''' <summary>
        ''' Obsolete: Use setPoseFrame instead.
        ''' Sets the frame of a robot (user frame). The frame can be either an item or a 4x4 Matrix.
        ''' If "frame" is an item, it links the robot to the frame item. If frame is a 4x4 Matrix, it updates the linked pose of the robot frame.
        ''' </summary>
        ''' <param name="frame">item/pose -> frame item or 4x4 Matrix (pose of the reference frame)</param>
        Public Sub setFrame(frame As Mat)
            setPoseFrame(frame)
        End Sub

        ''' <summary>
        ''' Obsolete: Use setPoseTool instead.
        ''' Sets the tool pose of a robot. The tool pose can be either an item or a 4x4 Matrix.
        ''' If "tool" is an item, it links the robot to the tool item. If tool is a 4x4 Matrix, it updates the linked pose of the robot tool.
        ''' </summary>
        ''' <param name="tool">item/pose -> tool item or 4x4 Matrix (pose of the tool frame)</param>
        Public Sub setTool(tool As Item)
            setPoseTool(tool)
        End Sub

        ''' <summary>
        ''' Obsolete: Use setPoseTool instead.
        ''' Sets the tool pose of a robot. The tool pose can be either an item or a 4x4 Matrix.
        ''' If "tool" is an item, it links the robot to the tool item. If tool is a 4x4 Matrix, it updates the linked pose of the robot tool.
        ''' </summary>
        ''' <param name="tool">item/pose -> tool item or 4x4 Matrix (pose of the tool frame)</param>
        Public Sub setTool(tool As Mat)
            setPoseTool(tool)
        End Sub

        ''' <summary>
        ''' Sets the reference frame of a robot(user frame). The frame can be either an item or a pose.
        ''' If "frame" is an item, it links the robot to the frame item. If frame is a pose, it updates the linked pose of the robot frame (with respect to the robot reference frame).
        ''' </summary>
        ''' <param name="frame_pose">4x4 homogeneous matrix (pose)</param>
        Public Sub setPoseFrame(frame_pose As Mat)
            link._check_connection()
            Dim command As String = "S_Frame"
            link._send_line(command)
            link._send_pose(frame_pose)
            link._send_item(Me)
            link._check_status()
        End Sub

        ''' <summary>
        ''' Sets the tool of a robot or a tool object (Tool Center Point, or TCP). The tool pose can be either an item or a 4x4 Matrix.
        ''' If the item is a tool, it links the robot to the tool item.If tool is a pose, it updates the current robot TCP.
        ''' </summary>
        ''' <param name="frame_item">4x4 homogeneous matrix (pose)</param>
        Public Sub setPoseFrame(frame_item As RoboDK.Item)
            link._check_connection()
            Dim command As String = "S_Frame_ptr"
            link._send_line(command)
            link._send_item(frame_item)
            link._send_item(Me)
            link._check_status()
        End Sub


        ''' <summary>
        ''' Sets the tool of a robot or a tool object (Tool Center Point, or TCP). The tool pose can be either an item or a 4x4 Matrix.
        ''' If the item is a tool, it links the robot to the tool item.If tool is a pose, it updates the current robot TCP.
        ''' </summary>
        ''' <param name="tool_pose">4x4 homogeneous matrix (pose)</param>
        Public Sub setPoseTool(tool_pose As Mat)
            link._check_connection()
            Dim command As String = "S_Tool"
            link._send_line(command)
            link._send_pose(tool_pose)
            link._send_item(Me)
            link._check_status()
        End Sub

        ''' <summary>
        ''' Sets the tool of a robot or a tool object (Tool Center Point, or TCP). The tool pose can be either an item or a 4x4 Matrix.
        ''' If the item is a tool, it links the robot to the tool item.If tool is a pose, it updates the current robot TCP.
        ''' </summary>
        ''' <param name="tool_item">Tool item</param>
        Public Sub setPoseTool(tool_item As RoboDK.Item)
            link._check_connection()
            Dim command As String = "S_Tool_ptr"
            link._send_line(command)
            link._send_item(tool_item)
            link._send_item(Me)
            link._check_status()
        End Sub

        ''' <summary>
        ''' Returns the tool pose of an item. If a robot is provided it will get the tool pose of the active tool held by the robot.
        ''' </summary>
        ''' <returns>4x4 homogeneous matrix (pose)</returns>
        Public Function PoseTool() As Mat
            link._check_connection()
            Dim command As String = "G_Tool"
            link._send_line(command)
            link._send_item(Me)
            Dim pose As Mat = link._rec_pose()
            link._check_status()
            Return pose
        End Function

        ''' <summary>
        ''' Returns the reference frame pose of an item. If a robot is provided it will get the tool pose of the active reference frame used by the robot.
        ''' </summary>
        ''' <returns>4x4 homogeneous matrix (pose)</returns>
        Public Function PoseFrame() As Mat
            link._check_connection()
            Dim command As String = "G_Frame"
            link._send_line(command)
            link._send_item(Me)
            Dim pose As Mat = link._rec_pose()
            link._check_status()
            Return pose
        End Function


        ''' <summary>
        ''' Obsolete: Use setPoseTool(pose) instead. Sets the tool pose of a tool item. If a robot is provided it will set the tool pose of the active tool held by the robot.
        ''' </summary>
        ''' <param name="pose">4x4 homogeneous matrix (pose)</param>
        Public Sub setHtool(pose As Mat)
            link._check_connection()
            Dim command As String = "S_Htool"
            link._send_line(command)
            link._send_item(Me)
            link._send_pose(pose)
            link._check_status()
        End Sub

        ''' <summary>
        ''' Obsolete: Use PoseTool() instead. 
        ''' Returns the tool pose of an item. If a robot is provided it will get the tool pose of the active tool held by the robot.
        ''' </summary>
        ''' <returns>4x4 homogeneous matrix (pose)</returns>
        Public Function Htool() As Mat
            link._check_connection()
            Dim command As String = "G_Htool"
            link._send_line(command)
            link._send_item(Me)
            Dim pose As Mat = link._rec_pose()
            link._check_status()
            Return pose
        End Function

        ''' <summary>
        ''' Adds an empty tool to the robot provided the tool pose (4x4 Matrix) and the tool name.
        ''' </summary>
        ''' <param name="tool_pose">pose -> TCP as a 4x4 Matrix (pose of the tool frame)</param>
        ''' <param name="tool_name">New tool name</param>
        ''' <returns>new item created</returns>
        Public Function AddTool(tool_pose As Mat, Optional tool_name As String = "New TCP") As Item
            link._check_connection()
            Dim command As String = "AddToolEmpty"
            link._send_line(command)
            link._send_item(Me)
            link._send_pose(tool_pose)
            link._send_line(tool_name)
            Dim newtool As Item = link._rec_item()
            link._check_status()
            Return newtool
        End Function

        ''' <summary>
        ''' Computes the forward kinematics of the robot for the provided joints. The tool and the reference frame are not taken into account.
        ''' </summary>
        ''' <param name="joints"></param>
        ''' <returns>4x4 homogeneous matrix: pose of the robot flange with respect to the robot base</returns>
        Public Function SolveFK(joints As Double()) As Mat
            link._check_connection()
            Dim command As String = "G_FK"
            link._send_line(command)
            link._send_array(joints)
            link._send_item(Me)
            Dim pose As Mat = link._rec_pose()
            link._check_status()
            Return pose
        End Function

        ''' <summary>
        ''' Returns the robot configuration state for a set of robot joints.
        ''' </summary>
        ''' <param name="joints">array of joints</param>
        ''' <returns>3-array -> configuration status as [REAR, LOWERARM, FLIP]</returns>
        Public Function JointsConfig(joints As Double()) As Double()
            link._check_connection()
            Dim command As String = "G_Thetas_Config"
            link._send_line(command)
            link._send_array(joints)
            link._send_item(Me)
            Dim config As Double() = link._rec_array()
            link._check_status()
            Return config
        End Function

        ''' <summary>
        ''' Computes the inverse kinematics for the specified robot and pose. The joints returned are the closest to the current robot configuration (see SolveIK_All())
        ''' </summary>
        ''' <param name="pose">4x4 matrix -> pose of the robot flange with respect to the robot base frame</param>
        ''' <returns>array of joints</returns>
        Public Function SolveIK(pose As Mat) As Double()
            link._check_connection()
            Dim command As String = "G_IK"
            link._send_line(command)
            link._send_pose(pose)
            link._send_item(Me)
            Dim joints As Double() = link._rec_array()
            link._check_status()
            Return joints
        End Function

        ''' <summary>
        ''' Computes the inverse kinematics for the specified robot and pose. The function returns all available joint solutions as a 2D matrix.
        ''' </summary>
        ''' <param name="pose">4x4 matrix -> pose of the robot tool with respect to the robot frame</param>
        ''' <returns>double x n x m -> joint list (2D matrix)</returns>
        Public Function SolveIK_All(pose As Mat) As Mat
            link._check_connection()
            Dim command As String = "G_IK_cmpl"
            link._send_line(command)
            link._send_pose(pose)
            link._send_item(Me)
            Dim joints_list As Mat = link._rec_matrix()
            link._check_status()
            Return joints_list
        End Function


        'def FilterTarget(self, pose, joints_approx=None):
        '    """Filters a target to improve accuracy.
        '    In  1 : 4x4 matrix -> pose of the robot TCP with respect to the robot reference frame
        '    In  2 : double x n -> approximate joints to define preferred configuration
        '    Out 1 : double x n x m -> joint list (2D matrix)"""
        '    self.link._check_connection()
        '    command = 'FilterTarget'
        '    self.link._send_line(command)
        '    self.link._send_pose(pose)
        '    if joints_approx is None:
        '        joints_approx = [0,0,0,0,0,0]
        '    self.link._send_array(joints_approx)
        '    self.link._send_item(self)
        '    pose_filtered = self.link._rec_pose()
        '    joints_filtered = self.link._rec_array()
        '    self.link._check_status()
        '    return pose_filtered, joints_filtered


        ''' <summary>
        ''' Connect to a real robot using the robot driver.
        ''' </summary>
        ''' <param name="robot_ip">IP of the robot to connect. Leave empty to use the one defined in RoboDK</param>
        ''' <returns>status -> true if connected successfully, false if connection failed</returns>
        Public Function Connect(Optional robot_ip As String = "") As Boolean
            link._check_connection()
            Dim command As String = "Connect"
            link._send_line(command)
            link._send_item(Me)
            link._send_line(robot_ip)
            Dim status As Integer = link._rec_int()
            link._check_status()
            Return status <> 0
        End Function

        'def ConnectSafe(self, robot_ip = '', max_attempts=5, wait_connection=4):
        '    """Connect to a real robot and wait for a connection to succeed.
        '    In  1 : robot_ip (string) -> IP of the robot to connect. Leave blank to use the IP selected in the connection panel of the robot.
        '    Out 1 : status -> 1 if connection succeeded 0 if it failed"""    
        '    trycount = 0
        '    refresh_rate = 0.5
        '    self.Connect()
        '    tic()
        '    timer1 = toc()
        '    pause(refresh_rate)
        '    while True:
        '        con_status, status_msg = self.ConnectedState()
        '        print(status_msg)
        '        if con_status == ROBOTCOM_READY:
        '            print(status_msg)
        '            break
        '        elif con_status == ROBOTCOM_DISCONNECTED:
        '            print('Trying to reconnect...')
        '            self.Connect()
        '        if toc() - timer1 > wait_connection:
        '            timer1 = toc()
        '            self.Disconnect()
        '            trycount = trycount + 1
        '            if trycount >= max_attempts:
        '                print('Failed to connect: Timed out')
        '                break
        '            print('Retrying connection...')
        '        pause(refresh_rate)
        '    return con_status


        'def ConnectionParams(self):
        '    """Retrieve robot connection parameters
        '    Out 1 : string -> robot IP
        '    Out 2 : int    -> port connection
        '    Out 3 : string -> remote path
        '    Out 4 : string -> FTP user name
        '    Out 5 : string -> FTP password"""
        '    self.link._check_connection()
        '    command = 'ConnectParams'
        '    self.link._send_line(command)
        '    self.link._send_item(self)
        '    robot_ip = self.link._rec_line()
        '    port = self.link._rec_int()
        '    remote_path = self.link._rec_line()
        '    ftp_user = self.link._rec_line()
        '    ftp_pass = self.link._rec_line()
        '    self.link._check_status()
        '    return robot_ip, port, remote_path, ftp_user, ftp_pass

        'def setConnectionParams(self, robot_ip, port, remote_path, ftp_user, ftp_pass):
        '    """Retrieve robot connection parameters
        '    In 1 : string -> robot IP
        '    In 2 : int    -> port connection
        '    In 3 : string -> remote path
        '    In 4 : string -> FTP user name
        '    In 5 : string -> FTP password"""
        '    self.link._check_connection()
        '    command = 'setConnectParams'
        '    self.link._send_line(command)
        '    self.link._send_item(self)
        '    self.link._send_line(robot_ip)
        '    self.link._send_int(port)
        '    self.link._send_line(remote_path)
        '    self.link._send_line(ftp_user)
        '    self.link._send_line(ftp_pass)
        '    self.link._check_status()

        'def ConnectedState(self):
        '    """Check connection status with a real robobt
        '    Out 1 : status code -> (int) ROBOTCOM_READY if the robot is ready to move, otherwise, status message will provide more information about the issue
        '    Out 2 : status message -> Message description of the robot status"""
        '    self.link._check_connection()
        '    command = 'ConnectedState'
        '    self.link._send_line(command)
        '    self.link._send_item(self)
        '    robotcom_status = self.link._rec_int()
        '    status_msg = self.link._rec_line()        
        '    self.link._check_status()
        '    return robotcom_status, status_msg

        ''' <summary>
        ''' Disconnect from a real robot (when the robot driver is used)
        ''' </summary>
        ''' <returns>status -> true if disconnected successfully, false if it failed. It can fail if it was previously disconnected manually for example.</returns>
        Public Function Disconnect() As Boolean
            link._check_connection()
            Dim command As String = "Disconnect"
            link._send_line(command)
            link._send_item(Me)
            Dim status As Integer = link._rec_int()
            link._check_status()
            Return status <> 0
        End Function

        ''' <summary>
        ''' Moves a robot to a specific target ("Move Joint" mode). By default, this function blocks until the robot finishes its movements.
        ''' </summary>
        ''' <param name="itemtarget">target -> target to move to as a target item (RoboDK target item)</param>
        ''' <param name="blocking">blocking -> True if we want the instruction to block until the robot finished the movement (default=true)</param>
        Public Sub MoveJ(itemtarget As Item, Optional blocking As Boolean = True)
            link._moveX(itemtarget, Nothing, Nothing, Me, 1, blocking)
        End Sub

        ''' <summary>
        ''' Moves a robot to a specific target ("Move Joint" mode). By default, this function blocks until the robot finishes its movements.
        ''' </summary>
        ''' <param name="joints">joints -> joint target to move to.</param>
        ''' <param name="blocking">blocking -> True if we want the instruction to block until the robot finished the movement (default=true)</param>
        Public Sub MoveJ(joints As Double(), Optional blocking As Boolean = True)
            link._moveX(Nothing, joints, Nothing, Me, 1, blocking)
        End Sub

        ''' <summary>
        ''' Moves a robot to a specific target ("Move Joint" mode). By default, this function blocks until the robot finishes its movements.
        ''' </summary>
        ''' <param name="target">pose -> pose target to move to. It must be a 4x4 Homogeneous matrix</param>
        ''' <param name="blocking">blocking -> True if we want the instruction to block until the robot finished the movement (default=true)</param>
        Public Sub MoveJ(target As Mat, Optional blocking As Boolean = True)
            link._moveX(Nothing, Nothing, target, Me, 1, blocking)
        End Sub

        ''' <summary>
        ''' Moves a robot to a specific target ("Move Linear" mode). By default, this function blocks until the robot finishes its movements.
        ''' </summary>
        ''' <param name="itemtarget">target -> target to move to as a target item (RoboDK target item)</param>
        ''' <param name="blocking">blocking -> True if we want the instruction to block until the robot finished the movement (default=true)</param>
        Public Sub MoveL(itemtarget As Item, Optional blocking As Boolean = True)
            link._moveX(itemtarget, Nothing, Nothing, Me, 2, blocking)
        End Sub

        ''' <summary>
        ''' Moves a robot to a specific target ("Move Linear" mode). By default, this function blocks until the robot finishes its movements.
        ''' </summary>
        ''' <param name="joints">joints -> joint target to move to.</param>
        ''' <param name="blocking">blocking -> True if we want the instruction to block until the robot finished the movement (default=true)</param>
        Public Sub MoveL(joints As Double(), Optional blocking As Boolean = True)
            link._moveX(Nothing, joints, Nothing, Me, 2, blocking)
        End Sub

        ''' <summary>
        ''' Moves a robot to a specific target ("Move Linear" mode). By default, this function blocks until the robot finishes its movements.
        ''' </summary>
        ''' <param name="target">pose -> pose target to move to. It must be a 4x4 Homogeneous matrix</param>
        ''' <param name="blocking">blocking -> True if we want the instruction to block until the robot finished the movement (default=true)</param>
        Public Sub MoveL(target As Mat, Optional blocking As Boolean = True)
            link._moveX(Nothing, Nothing, target, Me, 2, blocking)
        End Sub


        'def SearchL(self, target, blocking=True):
        '    """Moves a robot to a specific target looking for a specific signal to be triggered ("Search Linear"). This function waits (blocks) until the robot finishes its movements.
        '    In  1 : joints/pose/target -> target to move to. It can be the robot joints (Nx1 or 1xN), the pose (4x4) or a target (item pointer)
        '    In  2 (optional): blocking -> True if we want the instruction to wait until the robot finished the movement (default=True)"""
        '    self.link._moveX(target, self, 5, blocking)

        ''' <summary>
        ''' Moves a robot to a specific target ("Move Circular" mode). By default, this function blocks until the robot finishes its movements.
        ''' </summary>
        ''' <param name="itemtarget1">target -> intermediate target to move to as a target item (RoboDK target item)</param>
        ''' <param name="itemtarget2">target -> final target to move to as a target item (RoboDK target item)</param>
        ''' <param name="blocking">blocking -> True if we want the instruction to block until the robot finished the movement (default=true)</param>
        Public Sub MoveC(itemtarget1 As Item, itemtarget2 As Item, Optional blocking As Boolean = True)
            link._moveC_private(itemtarget1, Nothing, Nothing, itemtarget2, Nothing, Nothing, _
             Me, blocking)
        End Sub

        ''' <summary>
        ''' Moves a robot to a specific target ("Move Circular" mode). By default, this function blocks until the robot finishes its movements.
        ''' </summary>
        ''' <param name="joints1">joints -> intermediate joint target to move to.</param>
        ''' <param name="joints2">joints -> final joint target to move to.</param>
        ''' <param name="blocking">blocking -> True if we want the instruction to block until the robot finished the movement (default=true)</param>
        Public Sub MoveC(joints1 As Double(), joints2 As Double(), Optional blocking As Boolean = True)
            link._moveC_private(Nothing, joints1, Nothing, Nothing, joints2, Nothing, _
             Me, blocking)
        End Sub

        ''' <summary>
        ''' Moves a robot to a specific target ("Move Circular" mode). By default, this function blocks until the robot finishes its movements.
        ''' </summary>
        ''' <param name="target1">pose -> intermediate pose target to move to. It must be a 4x4 Homogeneous matrix</param>
        ''' <param name="target2">pose -> final pose target to move to. It must be a 4x4 Homogeneous matrix</param>
        ''' <param name="blocking">blocking -> True if we want the instruction to block until the robot finished the movement (default=true)</param>
        Public Sub MoveC(target1 As Mat, target2 As Mat, Optional blocking As Boolean = True)
            link._moveC_private(Nothing, Nothing, target1, Nothing, Nothing, target2, _
             Me, blocking)
        End Sub

        ''' <summary>
        ''' Checks if a joint movement is free of collision.
        ''' </summary>
        ''' <param name="j1">joints -> start joints</param>
        ''' <param name="j2">joints -> destination joints</param>
        ''' <param name="minstep_deg">(optional): maximum joint step in degrees</param>
        ''' <returns>collision : returns 0 if the movement is free of collision. Otherwise it returns the number of pairs of objects that collided if there was a collision.</returns>
        Public Function MoveJ_Collision(j1 As Double(), j2 As Double(), Optional minstep_deg As Double = -1) As Integer
            link._check_connection()
            Dim command As String = "CollisionMove"
            link._send_line(command)
            link._send_item(Me)
            link._send_array(j1)
            link._send_array(j2)
            link._send_int(CInt(minstep_deg * 1000.0))
            Dim collision As Integer = link._rec_int()
            link._check_status()
            Return collision
        End Function

        ''' <summary>
        ''' Checks if a linear movement is free of collision.
        ''' </summary>
        ''' <param name="j1">joints -> start joints</param>
        ''' <param name="j2">joints -> destination joints</param>
        ''' <param name="minstep_deg">(optional): maximum joint step in degrees</param>
        ''' <returns>collision : returns 0 if the movement is free of collision. Otherwise it returns the number of pairs of objects that collided if there was a collision.</returns>
        Public Function MoveL_Collision(j1 As Double(), j2 As Double(), Optional minstep_deg As Double = -1) As Integer
            link._check_connection()
            Dim command As String = "CollisionMoveL"
            link._send_line(command)
            link._send_item(Me)
            link._send_array(j1)
            link._send_array(j2)
            link._send_int(CInt(minstep_deg * 1000.0))
            Dim collision As Integer = link._rec_int()
            link._check_status()
            Return collision
        End Function

        ' ''' <summary>
        ' ''' Sets the speed and/or the acceleration of a robot.
        ' ''' </summary>
        ' ''' <param name="speed">speed -> speed in mm/s (-1 = no change)</param>
        ' ''' <param name="accel">acceleration (optional) -> acceleration in mm/s2 (-1 = no change)</param>
        ''
        ''        public void setSpeed(double speed, double accel = -1)
        ''        {
        ''            link.check_connection();
        ''            string command = "S_Speed";
        ''            link.send_line(command);
        ''            link.send_int((int)(speed * 1000.0));
        ''            link.send_int((int)(accel * 1000.0));
        ''            link.send_item(this);
        ''            link.check_status();
        ''
        ''        }


        ''' <summary>
        ''' Sets the speed and/or the acceleration of a robot.
        ''' </summary>
        ''' <param name="speed_linear">linear speed in mm/s (-1 = no change)</param>
        ''' <param name="accel_linear">linear acceleration in mm/s2 (-1 = no change)</param>
        ''' <param name="speed_joints">joint speed in deg/s (-1 = no change)</param>
        ''' <param name="accel_joints">joint acceleration in deg/s2 (-1 = no change)</param>
        Public Sub setSpeed(speed_linear As Double, Optional accel_linear As Double = -1, Optional speed_joints As Double = -1, Optional accel_joints As Double = -1)
            link._check_connection()
            Dim command As String = "S_Speed4"
            link._send_line(command)
            link._send_item(Me)
            Dim speed_accel As Double() = New Double(3) {}
            speed_accel(0) = speed_linear
            speed_accel(1) = accel_linear
            speed_accel(2) = speed_joints
            speed_accel(3) = accel_joints
            link._send_array(speed_accel)
            link._check_status()
        End Sub

        'def setAcceleration(self, accel_linear):
        '    """Sets the linear acceleration of a robot in mm/s2
        '    In  1 : angular speed -> acceleration in mm/s2"""
        '    self.setSpeed(-1,accel_linear,-1,-1)

        'def setSpeedJoints(self, speed_joints):
        '    """Sets the joint speed of a robot in deg/s for rotary joints and mm/s for linear joints
        '    In  1 : joint speed -> speed in deg/s for rotary joints and mm/s for linear joints"""
        '    self.setSpeed(-1,-1,speed_joints,-1)

        'def setAccelerationJoints(self, accel_joints):
        '    """Sets the joint acceleration of a robot
        '    In  1 : joint acceleration -> acceleration in deg/s2 for rotary joints and mm/s2 for linear joints"""
        '    self.setSpeed(-1,-1,-1,accel_joints)   


        ''' <summary>
        ''' Sets the robot movement smoothing accuracy (also known as zone data value).
        ''' </summary>
        ''' <param name="zonedata">zonedata value (int) (robot dependent, set to -1 for fine movements)</param>
        Public Sub setZoneData(zonedata As Double)
            link._check_connection()
            Dim command As String = "S_ZoneData"
            link._send_line(command)
            link._send_int(CInt(zonedata * 1000.0))
            link._send_item(Me)
            link._check_status()
        End Sub

        ''' <summary>
        ''' Displays a sequence of joints
        ''' </summary>
        ''' <param name="sequence">joint sequence as a 6xN matrix or instruction sequence as a 7xN matrix</param>
        Public Sub ShowSequence(sequence As Mat)
            link._check_connection()
            Dim command As String = "Show_Seq"
            link._send_line(command)
            link._send_matrix(sequence)
            link._send_item(Me)
            link._check_status()
        End Sub


        ''' <summary>
        ''' Checks if a robot or program is currently running (busy or moving)
        ''' </summary>
        ''' <returns>busy status (true=moving, false=stopped)</returns>
        Public Function Busy() As Boolean
            link._check_connection()
            Dim command As String = "IsBusy"
            link._send_line(command)
            link._send_item(Me)
            Dim busy__1 As Integer = link._rec_int()
            link._check_status()
            Return (busy__1 > 0)
        End Function

        ''' <summary>
        ''' Stops a program or a robot
        ''' </summary>
        Public Sub [Stop]()
            link._check_connection()
            Dim command As String = "Stop"
            link._send_line(command)
            link._send_item(Me)
            link._check_status()
        End Sub

        ''' <summary>
        ''' Waits (blocks) until the robot finishes its movement.
        ''' </summary>
        ''' <param name="timeout_sec">timeout -> Max time to wait for robot to finish its movement (in seconds)</param>
        Public Sub WaitMove(Optional timeout_sec As Double = 300)
            link._check_connection()
            Dim command As String = "WaitMove"
            link._send_line(command)
            link._send_item(Me)
            link._check_status()
            link.COM.ReceiveTimeout = CInt(timeout_sec * 1000.0)
            link._check_status()
            'will wait here;
            link.COM.ReceiveTimeout = link.TIMEOUT
            'int isbusy = link.Busy(this);
            'while (isbusy)
            '{
            '    busy = link.Busy(item);
            '}
        End Sub

        ''' <summary>
        ''' Wait until the program finishes.
        ''' </summary>
        Public Sub WaitFinished()
            While Me.Busy()
                Threading.Thread.Sleep(0.05 * 1000)
            End While
        End Sub
        '////// ADD MORE METHODS

        ' ---- Program item calls -----

        ''' <summary>
        ''' Defines the name of the program when the program is generated. It is also possible to specify the name of the post processor as well as the folder to save the program. 
        ''' This method must be called before any program output is generated (before any robot movement or other instruction).
        ''' </summary>
        ''' <param name="programname">name of the program</param>
        ''' <param name="folder">folder to save the program, leave empty to use the default program folder</param>
        ''' <param name="postprocessor">name of the post processor (for a post processor in C:/RoboDK/Posts/Fanuc_post.py it is possible to provide "Fanuc_post.py" or simply "Fanuc_post")</param>
        Public Function ProgramStart(programname As String, Optional folder As String = "", Optional postprocessor As String = "") As Integer
            Return link.ProgramStart(programname, folder, postprocessor, Me)
        End Function

        ''' <summary>
        ''' Sets the accuracy of the robot active or inactive.
        ''' </summary>
        ''' <param name="accurate"></param>
        Public Sub setAccuracyActive(Optional accurate As Boolean = True)
            link._check_connection()
            Dim command As String = "S_AbsAccOn"
            link._send_line(command)
            link._send_item(Me)
            If accurate Then
                link._send_int(1)
            Else
                link._send_int(0)
            End If
            link._check_status()
        End Sub

        ''' <summary>
        ''' Filters a program file to improve accuracy for a specific robot. The robot must have been previously calibrated.
        ''' </summary>
        ''' <param name="filestr">File path of the program.</param>
        ''' <param name="filter_msg">Summary of the filter process..</param>
        ''' <returns>status : 0 if the filter succeeded, below 0 if there are conversion problems.</returns>
        Public Function FilterProgram(filestr As String, ByRef filter_msg As String) As Integer
            link._check_connection()
            Dim command As String = "FilterProg2"
            link._send_line(command)
            link._send_item(Me)
            link._send_line(filestr)
            Dim filter_status As Integer = link._rec_int()
            filter_msg = link._rec_line()
            link._check_status()
            Return filter_status
        End Function

        ''' <summary>
        ''' Saves a program to a file.
        ''' </summary>
        ''' <param name="folder">folder path of the program</param>
        ''' <returns>success</returns>
        Public Function MakeProgram(folder As String) As Boolean
            link._check_connection()
            Dim command As String = "MakeProg"
            link._send_line(command)
            link._send_item(Me)
            link._send_line(folder)

            link.COM.ReceiveTimeout = 3600 * 1000
            Dim success As Boolean = False
            Dim prog_status As Integer = link._rec_int()
            Dim prog_log_str As String = link._rec_line()
            success = (prog_status > 0)

            link.COM.ReceiveTimeout = link.TIMEOUT
            link._check_status()

            Return success
        End Function

        ''' <summary>
        ''' Sets if the program will be run in simulation mode or on the real robot.
        ''' Use: "PROGRAM_RUN_ON_SIMULATOR" to set the program to run on the simulator only or "PROGRAM_RUN_ON_ROBOT" to force the program to run on the robot.
        ''' </summary>
        Public Sub setRunType(program_run_type As Integer)
            link._check_connection()
            Dim command As String = "S_ProgRunType"
            link._send_line(command)
            link._send_item(Me)
            link._send_int(program_run_type)
            link._check_status()
        End Sub

        ''' <summary>
        ''' Runs a program. It returns the number of instructions that can be executed successfully (a quick program check is performed before the program starts)
        ''' This is a non-blocking call. Use IsBusy() to check if the program execution finished.
        ''' Notes:
        ''' if setRunMode(RUNMODE_SIMULATE) is used  -> the program will be simulated (default run mode)
        ''' if setRunMode(RUNMODE_RUN_ROBOT) is used -> the program will run on the robot (default when RUNMODE_RUN_ROBOT is used)
        ''' if setRunMode(RUNMODE_RUN_ROBOT) is used together with program.setRunType(PROGRAM_RUN_ON_ROBOT) -> the program will run sequentially on the robot the same way as if we right clicked the program and selected "Run on robot" in the RoboDK GUI        
        ''' </summary>
        ''' <returns>number of instructions that can be executed</returns>
        Public Function RunProgram() As Integer
            link._check_connection()
            Dim command As String = "RunProg"
            link._send_line(command)
            link._send_item(Me)
            Dim prog_status As Integer = link._rec_int()
            link._check_status()
            Return prog_status
        End Function


        ''' <summary>
        ''' Runs a program. It returns the number of instructions that can be executed successfully (a quick program check is performed before the program starts)
        ''' Program parameters can be provided for Python calls.
        ''' This is a non-blocking call.Use IsBusy() to check if the program execution finished.
        ''' Notes: if setRunMode(RUNMODE_SIMULATE) is used  -> the program will be simulated (default run mode)
        ''' if setRunMode(RUNMODE_RUN_ROBOT) is used ->the program will run on the robot(default when RUNMODE_RUN_ROBOT is used)
        ''' if setRunMode(RUNMODE_RUN_ROBOT) is used together with program.setRunType(PROGRAM_RUN_ON_ROBOT) -> the program will run sequentially on the robot the same way as if we right clicked the program and selected "Run on robot" in the RoboDK GUI
        ''' </summary>
        ''' <param name="parameters">Number of instructions that can be executed</param>
        Public Function RunCode(Optional parameters As String = Nothing) As Integer
            link._check_connection()
            If parameters Is Nothing Then
                Dim command As String = "RunProg"
                link._send_line(command)
                link._send_item(Me)
            Else
                Dim command As String = "RunProgParam"
                link._send_line(command)
                link._send_item(Me)
                link._send_line(parameters)
            End If
            Dim progstatus As Integer = link._rec_int()
            link._check_status()
            Return progstatus
        End Function

        ''' <summary>
        ''' Adds a program call, code, message or comment inside a program.
        ''' </summary>
        ''' <param name="code">string of the code or program to run</param>
        ''' <param name="run_type">INSTRUCTION_* variable to specify if the code is a progra</param>
        Public Function RunCodeCustom(code As String, Optional run_type As Integer = INSTRUCTION_CALL_PROGRAM) As Integer
            link._check_connection()
            Dim command As String = "RunCode2"
            link._send_line(command)
            link._send_item(Me)
            link._send_line(code.Replace(vbLf & vbLf, "<br>").Replace(vbLf, "<br>"))
            link._send_int(run_type)
            Dim progstatus As Integer = link._rec_int()
            link._check_status()
            Return progstatus
        End Function

        ''' <summary>
        ''' Generates a pause instruction for a robot or a program when generating code. Set it to -1 (default) if you want the robot to stop and let the user resume the program anytime.
        ''' </summary>
        ''' <param name="time_ms">Time in milliseconds</param>
        Public Sub Pause(Optional time_ms As Double = -1)
            link._check_connection()
            Dim command As String = "RunPause"
            link._send_line(command)
            link._send_item(Me)
            link._send_int(CInt(time_ms * 1000.0))
            link._check_status()
        End Sub


        ''' <summary>
        ''' Sets a variable (output) to a given value. This can also be used to set any variables to a desired value.
        ''' </summary>
        ''' <param name="io_var">io_var -> digital output (string or number)</param>
        ''' <param name="io_value">io_value -> value (string or number)</param>
        Public Sub setDO(io_var As String, io_value As String)
            link._check_connection()
            Dim command As String = "setDO"
            link._send_line(command)
            link._send_item(Me)
            link._send_line(io_var)
            link._send_line(io_value)
            link._check_status()
        End Sub

        ''' <summary>
        ''' Waits for an input io_id to attain a given value io_value. Optionally, a timeout can be provided.
        ''' </summary>
        ''' <param name="io_var">io_var -> digital output (string or number)</param>
        ''' <param name="io_value">io_value -> value (string or number)</param>
        ''' <param name="timeout_ms">int (optional) -> timeout in miliseconds</param>
        Public Sub waitDI(io_var As String, io_value As String, Optional timeout_ms As Double = -1)
            link._check_connection()
            Dim command As String = "waitDI"
            link._send_line(command)
            link._send_item(Me)
            link._send_line(io_var)
            link._send_line(io_value)
            link._send_int(CInt(timeout_ms * 1000.0))
            link._check_status()
        End Sub



        ''' <summary>
        ''' Adds a new robot move joint instruction to a program.
        ''' </summary>
        ''' <param name="itemtarget">target to move to</param>
        Public Sub addMoveJ(itemtarget As Item)
            link._check_connection()
            Dim command As String = "Add_INSMOVE"
            link._send_line(command)
            link._send_item(itemtarget)
            link._send_item(Me)
            link._send_int(1)
            link._check_status()
        End Sub

        ''' <summary>
        ''' Adds a new robot move linear instruction to a program.
        ''' </summary>
        ''' <param name="itemtarget">target to move to</param>
        Public Sub addMoveL(itemtarget As Item)
            link._check_connection()
            Dim command As String = "Add_INSMOVE"
            link._send_line(command)
            link._send_item(itemtarget)
            link._send_item(Me)
            link._send_int(2)
            link._check_status()
        End Sub

        '/////// ADD MORE METHODS

        ''' <summary>
        ''' Show instructions inside a program in RoboDK tree
        ''' </summary>
        ''' <param name="show"> optional </param>
        Public Sub ShowInstructions(Optional show As Boolean = True)
            link._check_connection()
            Dim command As String = "Prog_ShowIns"
            link._send_line(command)
            link._send_item(Me)
            If show Then
                link._send_int(1)
            Else
                link._send_int(0)
            End If
            link._check_status()
        End Sub

        ''' <summary>
        ''' Returns the number of instructions of a program.
        ''' </summary>
        ''' <returns></returns>
        Public Function InstructionCount() As Integer
            link._check_connection()
            Dim command As String = "Prog_Nins"
            link._send_line(command)
            link._send_item(Me)
            Dim nins As Integer = link._rec_int()
            link._check_status()
            Return nins
        End Function

        ''' <summary>
        ''' Returns the program instruction at position id
        ''' </summary>
        ''' <param name="ins_id"></param>
        ''' <param name="name"></param>
        ''' <param name="instype"></param>
        ''' <param name="movetype"></param>
        ''' <param name="isjointtarget"></param>
        ''' <param name="target"></param>
        ''' <param name="joints"></param>
        Public Sub Instruction(ins_id As Integer, ByRef name As String, ByRef instype As Integer, ByRef movetype As Integer, ByRef isjointtarget As Boolean, ByRef target As Mat, _
         ByRef joints As Double())
            link._check_connection()
            Dim command As String = "Prog_GIns"
            link._send_line(command)
            link._send_item(Me)
            link._send_int(ins_id)
            name = link._rec_line()
            instype = link._rec_int()
            movetype = 0
            isjointtarget = False
            target = Nothing
            joints = Nothing
            If instype = INS_TYPE_MOVE Then
                movetype = link._rec_int()
                isjointtarget = If(link._rec_int() > 0, True, False)
                target = link._rec_pose()
                joints = link._rec_array()
            End If
            link._check_status()
        End Sub

        ''' <summary>
        ''' Updates a program and returns the estimated time and the number of valid instructions.
        ''' </summary>
        ''' <param name="valid_instructions_number"> Returns the number of valid instructions</param>
        ''' <param name="program_time_seconds"> Estimated cycle time (in seconds)</param>
        ''' <param name="program_distance_mm"> Distance that the robot TCP will travel (in mm)</param>
        ''' <param name="valid_program">It is True if the program has no issues, False otherwise.</param>
        Public Sub Update(ByRef valid_instructions_number As Integer, ByRef program_time_seconds As Double, ByRef program_distance_mm As Double, ByRef valid_program As Boolean)
            '    Out 1:
            '    Out 2: 
            '    Out 3: 
            '    Out 4: """
            link._check_connection()
            Dim command As String = "Update"
            link._send_line(command)
            link._send_item(Me)
            Dim values As Double() = link._rec_array()
            link._check_status()
            valid_instructions_number = CInt(values(0))
            program_time_seconds = values(1)
            program_distance_mm = values(2)
            valid_program = values(3) > 0
        End Sub

        ''' <summary>
        ''' Sets the program instruction at position id
        ''' </summary>
        ''' <param name="ins_id"></param>
        ''' <param name="name"></param>
        ''' <param name="instype"></param>
        ''' <param name="movetype"></param>
        ''' <param name="isjointtarget"></param>
        ''' <param name="target"></param>
        ''' <param name="joints"></param>
        Public Sub setInstruction(ins_id As Integer, name As String, instype As Integer, movetype As Integer, isjointtarget As Boolean, target As Mat, _
         joints As Double())
            link._check_connection()
            Dim command As String = "Prog_SIns"
            link._send_line(command)
            link._send_item(Me)
            link._send_int(ins_id)
            link._send_line(name)
            link._send_int(instype)
            If instype = INS_TYPE_MOVE Then
                link._send_int(movetype)
                link._send_int(If(isjointtarget, 1, 0))
                link._send_pose(target)
                link._send_array(joints)
            End If
            link._check_status()
        End Sub


        ''' <summary>
        ''' Returns the list of program instructions as an MxN matrix, where N is the number of instructions and M equals to 1 plus the number of robot axes.
        ''' </summary>
        ''' <param name="instructions">the matrix of instructions</param>
        ''' <returns>Returns 0 if success</returns>
        Public Function InstructionList(ByRef instructions As Mat) As Integer
            link._check_connection()
            Dim command As String = "G_ProgInsList"
            link._send_line(command)
            link._send_item(Me)
            instructions = link._rec_matrix()
            Dim errors As Integer = link._rec_int()
            link._check_status()
            Return errors
        End Function

        ''' <summary>
        ''' Returns a list of joints an MxN matrix, where M is the number of robot axes plus 4 columns. Linear moves are rounded according to the smoothing parameter set inside the program.
        ''' </summary>
        ''' <param name="error_msg">Returns a human readable error message (if any)</param>
        ''' <param name="joint_list">Returns the list of joints as [J1, J2, ..., Jn, ERROR, MM_STEP, DEG_STEP, MOVE_ID] if a file name is not specified</param>
        ''' <param name="mm_step">Maximum step in millimeters for linear movements (millimeters)</param>
        ''' <param name="deg_step">Maximum step for joint movements (degrees)</param>
        ''' <param name="save_to_file">Provide a file name to directly save the output to a file. If the file name is not provided it will return the matrix. If step values are very small, the returned matrix can be very large.</param>
        ''' <returns>Returns 0 if success, otherwise, it will return negative values</returns>
        Public Function InstructionListJoints(ByRef error_msg As String, ByRef joint_list As Mat, Optional mm_step As Double = 10.0, Optional deg_step As Double = 5.0, Optional save_to_file As String = "") As Integer
            link._check_connection()
            Dim command As String = "G_ProgJointList"
            link._send_line(command)
            link._send_item(Me)
            Dim ste_mm_deg As Double() = {mm_step, deg_step}
            link._send_array(ste_mm_deg)
            'joint_list = save_to_file;
            If save_to_file.Length <= 0 Then
                link._send_line("")
                joint_list = link._rec_matrix()
            Else
                link._send_line(save_to_file)
                joint_list = Nothing
            End If
            Dim error_code As Integer = link._rec_int()
            error_msg = link._rec_line()
            link._check_status()
            Return error_code
        End Function

        ''' <summary>
        ''' Disconnect from the RoboDK API. This flushes any pending program generation.
        ''' </summary>
        ''' <returns></returns>
        Public Function Finish() As Boolean
            Return link.Finish()
        End Function
    End Class
End Class
