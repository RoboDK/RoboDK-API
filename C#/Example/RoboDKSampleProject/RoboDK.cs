// This file (RoboDK.cs) implements the RoboDK API for C#
// This file defines the following classes:
//     Mat: Matrix class, useful pose operations
//     RoboDK: API to interact with RoboDK
//     RoboDK.Item: Any item in the RoboDK station tree
//
// These classes are the objects used to interact with RoboDK and create macros.
// An item is an object in the RoboDK tree (it can be either a robot, an object, a tool, a frame, a program, ...).
// Items can be retrieved from the RoboDK station using the RoboDK() object (such as RoboDK.GetItem() method) 
//
// In this document: pose = transformation matrix = homogeneous matrix = 4x4 matrix
//
// More information about the RoboDK API for Python here:
//     https://robodk.com/doc/en/RoboDK-API.html
//     https://robodk.com/doc/en/PythonAPI/index.html
//
// More information about RoboDK post processors here:
//     https://robodk.com/help#PostProcessor
//
// Visit the Matrix and Quaternions FAQ for more information about pose/homogeneous transformations
//     http://www.j3d.org/matrix_faq/matrfaq_latest.html
//
// This library includes the mathematics to operate with homogeneous matrices for robotics.

using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Net.Sockets;       // For Socket communication
using Microsoft.Win32;          // For registry keys
using System.IO;
using System.Net;
using System.Threading;
using System.Drawing;

/// <summary>
/// Matrix class for robotics. 
/// </summary>
public class Mat // simple matrix class for homogeneous operations
{
    public int rows;
    public int cols;
    public double[,] mat;

    public Mat L;
    public Mat U;

    //  Class used for Matrix exceptions
    public class MatException : Exception
    {
        public MatException(string Message)
            : base(Message)
        { }
    }




    /// <summary>
    /// Returns the norm of a 3D vector
    /// </summary>
    /// <param name="p"></param>
    /// <returns></returns>
    static public double norm(double[] p)
    {
        return Math.Sqrt(p[0] * p[0] + p[1] * p[1] + p[2] * p[2]);
    }

    /// <summary>
    /// Returns the unitary vector
    /// </summary>
    /// <param name="p"></param>
    /// <returns></returns>
    static public double[] normalize3(double[] p)
    {
        double norminv = 1.0 / norm(p);
        return new double[] { p[0] * norminv, p[1] * norminv, p[2] * norminv };
    }

    /// <summary>
    /// Returns the cross product of two 3D vectors
    /// </summary>
    /// <param name="p"></param>
    /// <returns></returns>
    static public double[] cross(double[] a, double[] b)
    {
        return new double[] {a[1]* b[2] - a[2]* b[1],
          a[2]* b[0] - a[0]* b[2],
           a[0]* b[1] - a[1]* b[0]};
    }
    /// <summary>
    /// Returns the dot product of two 3D vectors
    /// </summary>
    /// <param name="a"></param>
    /// <param name="b"></param>
    /// <returns></returns>
    static public double dot(double[] a, double[] b)
    {
        return a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
    }

    /// <summary>
    /// Returns the angle in radians of two 3D vectors
    /// </summary>
    /// <param name="a"></param>
    /// <param name="b"></param>
    /// <returns></returns>
    static public double angle3(double[] a, double[] b)
    {
        return Math.Acos(dot(normalize3(a), normalize3(b)));
    }

    /// <summary>
    /// Convert a point XYZ and IJK vector (Z axis) to a pose given a hint for the Y axis
    /// </summary>
    /// <param name="point"></param>
    /// <param name="zaxis"></param>
    /// <param name="reference"></param>
    /// <param name="yaxis_hint"></param>
    /// <returns></returns>
    static public Mat xyzijk_2_pose(double[] point, double[] zaxis, double[] yaxis_hint = null)
    {
        Mat pose = Mat.Identity4x4();
        if (yaxis_hint == null)
        {
            yaxis_hint = new double[] { 0, 0, 1 };
        }
        pose.setPos(point);
        pose.setVZ(zaxis);
        if (Mat.angle3(zaxis, yaxis_hint) < 2 * Math.PI / 180)
        {
            yaxis_hint = new double[] { 0, 1, 1 };
        }
        double[] xaxis = Mat.normalize3(Mat.cross(yaxis_hint, zaxis));
        double[] yaxis = Mat.cross(zaxis, xaxis);
        pose.setVX(xaxis);
        pose.setVY(yaxis);
        return pose;
    }




    /// <summary>
    /// Matrix class constructor for any size matrix
    /// </summary>
    /// <param name="Rows">dimension 1 size (rows)</param>
    /// <param name="Cols">dimension 2 size (columns)</param>
    public Mat(int Rows, int Cols)         // Matrix Class constructor
    {
        rows = Rows;
        cols = Cols;
        mat = new double[rows, cols];
    }

    /// <summary>
    /// Matrix class constructor for a double array of arrays (list of points)
    /// Example:
    ///     RDK.AddCurve(new Mat(new double[4, 6] {{0,0,0, 0,0,1}, { 500, 0, 0, 0, 0, 1 }, { 500, 500, 0, 0, 0, 1 }, { 0, 0, 0, 0, 0, 1 } }));
    /// </summary>
    /// <param name="point_list">List of points (array of array of doubles)</param>
    public Mat(double[,] point_list)
    {
        cols = point_list.GetLength(0);
        rows = point_list.GetLength(1);

        // Convert a double array of arrays to a Mat object:
        mat = new double[rows, cols];
        for (int c = 0; c < cols; c++)
        {
            for (int r = 0; r < rows; r++)
            {
                mat[r, c] = point_list[c, r];
            }
        }
    }

    /// <summary>
    /// Matrix class constructor for a double array. The array will be set as a column matrix.
    /// Example:
    ///     RDK.AddCurve(new Mat(new double[6] {{0,0,0, 0,0,1}}));
    /// </summary>
    /// <param name="point">Column array</param>
    public Mat(double[] point, bool is_pose = false)
    {
        if (is_pose)
        {
            cols = 4;
            rows = 4;
            if (point.GetLength(0) < 16)
            {
                throw new MatException("Invalid array size to create a pose Mat"); //raise Exception('Problems running function');
            }

            // Convert a double array of arrays to a Mat object:
            mat = new double[rows, cols];
            for (int r = 0; r < rows; r++)
            {
                for (int c = 0; c < cols; c++)
                {
                    mat[r, c] = point[r + c * 4];
                }
            }
        }
        else
        {
            cols = 1;
            rows = point.GetLength(0);

            // Convert a double array of arrays to a Mat object:
            mat = new double[rows, cols];
            for (int r = 0; r < rows; r++)
            {
                mat[r, 0] = point[r];
            }
        }

    }

    /// <summary>
    /// Matrix class constructor for a 4x4 homogeneous matrix
    /// </summary>
    /// <param name="nx">Position [0,0]</param>
    /// <param name="ox">Position [0,1]</param>
    /// <param name="ax">Position [0,2]</param>
    /// <param name="tx">Position [0,3]</param>
    /// <param name="ny">Position [1,0]</param>
    /// <param name="oy">Position [1,1]</param>
    /// <param name="ay">Position [1,2]</param>
    /// <param name="ty">Position [1,3]</param>
    /// <param name="nz">Position [2,0]</param>
    /// <param name="oz">Position [2,1]</param>
    /// <param name="az">Position [2,2]</param>
    /// <param name="tz">Position [2,3]</param>
    public Mat(double nx, double ox, double ax, double tx, double ny, double oy, double ay, double ty, double nz, double oz, double az, double tz)         // Matrix Class constructor
    {
        rows = 4;
        cols = 4;
        mat = new double[rows, cols];
        mat[0, 0] = nx; mat[1, 0] = ny; mat[2, 0] = nz;
        mat[0, 1] = ox; mat[1, 1] = oy; mat[2, 1] = oz;
        mat[0, 2] = ax; mat[1, 2] = ay; mat[2, 2] = az;
        mat[0, 3] = tx; mat[1, 3] = ty; mat[2, 3] = tz;
        mat[3, 0] = 0.0; mat[3, 1] = 0.0; mat[3, 2] = 0.0; mat[3, 3] = 1.0;
    }

    /// <summary>
    /// Matrix class constructor for a 4x4 homogeneous matrix as a copy from another matrix
    /// </summary>
    public Mat(Mat pose)
    {
        rows = pose.rows;
        cols = pose.cols;
        mat = new double[rows, cols];
        for (int i = 0; i < rows; i++)
            for (int j = 0; j < cols; j++)
                mat[i, j] = pose[i, j];
    }

    /// <summary>
    /// Matrix class constructor for a 3x3 homogeneous matrix
    /// </summary>
    /// <param name="nx"></param>
    /// <param name="ox"></param>
    /// <param name="ax"></param>
    /// <param name="ny"></param>
    /// <param name="oy"></param>
    /// <param name="ay"></param>
    /// <param name="nz"></param>
    /// <param name="oz"></param>
    /// <param name="az"></param>
    public Mat(double nx, double ox, double ax, double ny, double oy, double ay, double nz, double oz, double az)
    {
        rows = 3;
        cols = 3;
        mat = new double[rows, cols];
        mat[0, 0] = nx; mat[1, 0] = ny; mat[2, 0] = nz;
        mat[0, 1] = ox; mat[1, 1] = oy; mat[2, 1] = oz;
        mat[0, 2] = ax; mat[1, 2] = ay; mat[2, 2] = az;
    }

    /// <summary>
    /// Returns the sub 3x3 matrix that represents the pose rotation
    /// </summary>
    /// <returns></returns>
    public Mat Rot3x3()
    {
        if (!IsHomogeneous())
        {
            throw new MatException("It is not possible to retrieve a sub 3x3 rotation mat"); //raise Exception('Problems running function');
        }
        return new Mat(mat[0, 0], mat[0, 1], mat[0, 2], mat[1, 0], mat[1, 1], mat[1, 2], mat[2, 0], mat[2, 1], mat[2, 2]);
    }


    /// <summary>
    /// Check if it is a Homogeneous Identity matrix
    /// </summary>
    /// <returns></returns>
    public bool isIdentity()
    {
        if (rows != 4 || this.rows != this.cols)
            return false;

        for (int i = 0; i < rows; i++)
        {
            if (mat[i, i] != 1.0)
                return false;

        }
        if (mat[0, 3] != 0.0 || mat[1, 3] != 0.0 || mat[2, 3] != 0.0)
            return false;

        return true;
    }

    /// <summary>
    /// Matrix class constructor for a 4x1 vector [x,y,z,1]
    /// </summary>
    /// <param name="x">x coordinate</param>
    /// <param name="y">y coordinate</param>
    /// <param name="z">z coordinate</param>
    public Mat(double x, double y, double z)
    {
        rows = 4;
        cols = 1;
        mat = new double[rows, cols];
        mat[0, 0] = x;
        mat[1, 0] = y;
        mat[2, 0] = z;
        mat[3, 0] = 1.0;
    }

    //----------------------------------------------------
    //--------     Generic matrix usage    ---------------
    /// <summary>
    /// Return a translation matrix
    ///                 |  1   0   0   X |
    /// transl(X,Y,Z) = |  0   1   0   Y |
    ///                 |  0   0   1   Z |
    ///                 |  0   0   0   1 |
    /// </summary>
    /// <param name="x">translation along X (mm)</param>
    /// <param name="y">translation along Y (mm)</param>
    /// <param name="z">translation along Z (mm)</param>
    /// <returns></returns>
    static public Mat transl(double x, double y, double z)
    {
        Mat mat = Mat.IdentityMatrix(4, 4);
        mat.setPos(x, y, z);
        return mat;
    }

    /// <summary>
    /// Return a X-axis rotation matrix
    ///            |  1  0        0        0 |
    /// rotx(rx) = |  0  cos(rx) -sin(rx)  0 |
    ///            |  0  sin(rx)  cos(rx)  0 |
    ///            |  0  0        0        1 |
    /// </summary>
    /// <param name="rx">rotation around X axis (in radians)</param>
    /// <returns></returns>
    static public Mat rotx(double rx)
    {
        double cx = Math.Cos(rx);
        double sx = Math.Sin(rx);
        return new Mat(1, 0, 0, 0, 0, cx, -sx, 0, 0, sx, cx, 0);
    }

    /// <summary>
    /// Return a Y-axis rotation matrix
    ///            |  cos(ry)  0   sin(ry)  0 |
    /// roty(ry) = |  0        1   0        0 |
    ///            | -sin(ry)  0   cos(ry)  0 |
    ///            |  0        0   0        1 |
    /// </summary>
    /// <param name="ry">rotation around Y axis (in radians)</param>
    /// <returns></returns>
    static public Mat roty(double ry)
    {
        double cy = Math.Cos(ry);
        double sy = Math.Sin(ry);
        return new Mat(cy, 0, sy, 0, 0, 1, 0, 0, -sy, 0, cy, 0);
    }

    /// <summary>
    /// Return a Z-axis rotation matrix
    ///            |  cos(rz)  -sin(rz)   0   0 |
    /// rotz(rx) = |  sin(rz)   cos(rz)   0   0 |
    ///            |  0         0         1   0 |
    ///            |  0         0         0   1 |
    /// </summary>
    /// <param name="rz">rotation around Z axis (in radians)</param>
    /// <returns></returns>
    static public Mat rotz(double rz)
    {
        double cz = Math.Cos(rz);
        double sz = Math.Sin(rz);
        return new Mat(cz, -sz, 0, 0, sz, cz, 0, 0, 0, 0, 1, 0);
    }


    //----------------------------------------------------
    //------ Pose to xyzrpw and xyzrpw to pose------------
    /// <summary>
    /// Calculates the equivalent position and euler angles ([x,y,z,r,p,w] vector) of the given pose 
    /// Note: transl(x,y,z)*rotz(w*pi/180)*roty(p*pi/180)*rotx(r*pi/180)
    /// See also: FromXYZRPW()
    /// </summary>
    /// <returns>XYZWPR translation and rotation in mm and degrees</returns>
    public double[] ToXYZRPW()
    {
        double[] xyzwpr = new double[6];
        double x = mat[0, 3];
        double y = mat[1, 3];
        double z = mat[2, 3];
        double w, p, r;
        if (mat[2, 0] > (1.0 - 1e-6))
        {
            p = -Math.PI * 0.5;
            r = 0;
            w = Math.Atan2(-mat[1, 2], mat[1, 1]);
        }
        else if (mat[2, 0] < -1.0 + 1e-6)
        {
            p = 0.5 * Math.PI;
            r = 0;
            w = Math.Atan2(mat[1, 2], mat[1, 1]);
        }
        else
        {
            p = Math.Atan2(-mat[2, 0], Math.Sqrt(mat[0, 0] * mat[0, 0] + mat[1, 0] * mat[1, 0]));
            w = Math.Atan2(mat[1, 0], mat[0, 0]);
            r = Math.Atan2(mat[2, 1], mat[2, 2]);
        }
        xyzwpr[0] = x;
        xyzwpr[1] = y;
        xyzwpr[2] = z;
        xyzwpr[3] = r * 180.0 / Math.PI;
        xyzwpr[4] = p * 180.0 / Math.PI;
        xyzwpr[5] = w * 180.0 / Math.PI;
        return xyzwpr;
    }

    /// <summary>
    /// Calculates the pose from the position and euler angles ([x,y,z,r,p,w] vector)
    /// The result is the same as calling: H = transl(x,y,z)*rotz(w*pi/180)*roty(p*pi/180)*rotx(r*pi/180)
    /// </summary>
    /// <param name="x"></param>
    /// <param name="y"></param>
    /// <param name="z"></param>
    /// <param name="w"></param>
    /// <param name="p"></param>
    /// <param name="r"></param>
    /// <returns>Homogeneous matrix (4x4)</returns>
    static public Mat FromXYZRPW(double x, double y, double z, double w, double p, double r)
    {
        double a = r * Math.PI / 180.0;
        double b = p * Math.PI / 180.0;
        double c = w * Math.PI / 180.0;
        double ca = Math.Cos(a);
        double sa = Math.Sin(a);
        double cb = Math.Cos(b);
        double sb = Math.Sin(b);
        double cc = Math.Cos(c);
        double sc = Math.Sin(c);
        return new Mat(cb * cc, cc * sa * sb - ca * sc, sa * sc + ca * cc * sb, x, cb * sc, ca * cc + sa * sb * sc, ca * sb * sc - cc * sa, y, -sb, cb * sa, ca * cb, z);
    }

    /// <summary>
    /// Calculates the pose from the position and euler angles ([x,y,z,r,p,w] vector)
    //  The result is the same as calling: H = transl(x,y,z)*rotz(w*pi/180)*roty(p*pi/180)*rotx(r*pi/180)
    /// </summary>
    /// <param name="xyzwpr"></param>
    /// <returns>Homogeneous matrix (4x4)</returns>
    static public Mat FromXYZRPW(double[] xyzwpr)
    {
        if (xyzwpr.Length < 6)
        {
            return null;
        }
        return FromXYZRPW(xyzwpr[0], xyzwpr[1], xyzwpr[2], xyzwpr[3], xyzwpr[4], xyzwpr[5]);
    }

    /// <summary>
    /// Calculates the pose from the position and euler angles ([x,y,z,rz,ry,rz] vector)
    //  The result is the same as calling: H = transl(x,y,z)*rotz(rz*pi/180)*roty(ry*pi/180)*rotz(rz2*pi/180)
    /// </summary>
    /// <param name="xyzwpr"></param>
    /// <returns>Homogeneous matrix (4x4)</returns>
    static public Mat FromComau(double[] xyzzyz)
    {
        if (xyzzyz.Length < 6)
        {
            return null;
        }
        return transl(xyzzyz[0], xyzzyz[1], xyzzyz[2]) * rotz(xyzzyz[3] * Math.PI / 180.0) * roty(xyzzyz[4] * Math.PI / 180.0) * rotz(xyzzyz[5] * Math.PI / 180.0);
    }
    /// <summary>
    /// Calculates the equivalent position and euler angles ([x,y,z,rx,ry,rz] array) of a pose 
    /// Note: Pose = transl(x,y,z)*rotx(rx*pi/180)*roty(ry*pi/180)*rotz(rz*pi/180)
    /// See also: FromTxyzRxyz()
    /// </summary>
    /// <returns>XYZWPR translation and rotation in mm and degrees</returns>
    public double[] ToComau()
    {
        double[] xyzwpr = new double[6];
        double x = mat[0, 3];
        double y = mat[1, 3];
        double z = mat[2, 3];
        double rz1 = 0;
        double ry1 = 0;
        double rzz = 0;

        if (mat[2, 2] > (1.0 - 1e-6))
        {
            rz1 = 0;
            ry1 = 0;
            rzz = Math.Atan2(mat[1, 0], mat[0, 0]);
        }
        else if (mat[2, 2] < (-1.0 + 1e-6))
        {
            rz1 = 0;
            ry1 = Math.PI / 2;
            rzz = Math.Atan2(mat[1, 0], mat[1, 1]);
        }
        else
        {
            double cb = mat[2, 2];
            double sb = +Math.Sqrt(1 - cb * cb);
            double sc = mat[2, 1] / sb;
            double cc = -mat[2, 0] / sb;
            double sa = mat[1, 2] / sb;
            double ca = mat[0, 2] / sb;
            rz1 = Math.Atan2(sa, ca);
            ry1 = Math.Atan2(sb, cb);
            rzz = Math.Atan2(sc, cc);
        }

        xyzwpr[0] = x;
        xyzwpr[1] = y;
        xyzwpr[2] = z;
        xyzwpr[3] = rz1 * 180.0 / Math.PI;
        xyzwpr[4] = ry1 * 180.0 / Math.PI;
        xyzwpr[5] = rzz * 180.0 / Math.PI;
        return xyzwpr;
    }

    /// <summary>
    /// Calculates the pose from the position and euler angles ([x,y,z,rx,ry,rz] array)
    /// The result is the same as calling: H = transl(x,y,z)*rotx(rx*pi/180)*roty(ry*pi/180)*rotz(rz*pi/180)
    /// </summary>
    /// <param name="x"></param>
    /// <param name="y"></param>
    /// <param name="z"></param>
    /// <param name="rx"></param>
    /// <param name="ry"></param>
    /// <param name="rz"></param>
    /// <returns>Homogeneous matrix (4x4)</returns>
    static public Mat FromTxyzRxyz(double x, double y, double z, double rx, double ry, double rz)
    {
        double a = rx * Math.PI / 180.0;
        double b = ry * Math.PI / 180.0;
        double c = rz * Math.PI / 180.0;
        double crx = Math.Cos(a);
        double srx = Math.Sin(a);
        double cry = Math.Cos(b);
        double sry = Math.Sin(b);
        double crz = Math.Cos(c);
        double srz = Math.Sin(c);
        return new Mat(cry * crz, -cry * srz, sry, x, crx * srz + crz * srx * sry, crx * crz - srx * sry * srz, -cry * srx, y, srx * srz - crx * crz * sry, crz * srx + crx * sry * srz, crx * cry, z);
    }

    /// <summary>
    /// Calculates the pose from the position and euler angles ([x,y,z,rx,ry,rz] array)
    /// The result is the same as calling: H = transl(x,y,z)*rotx(rx*pi/180)*roty(ry*pi/180)*rotz(rz*pi/180)
    /// </summary>
    /// <returns>Homogeneous matrix (4x4)</returns>
    static public Mat FromTxyzRxyz(double[] xyzwpr)
    {
        if (xyzwpr.Length < 6)
        {
            return null;
        }
        return FromTxyzRxyz(xyzwpr[0], xyzwpr[1], xyzwpr[2], xyzwpr[3], xyzwpr[4], xyzwpr[5]);
    }

    /// <summary>
    /// Calculates the equivalent position and euler angles ([x,y,z,rx,ry,rz] array) of a pose 
    /// Note: Pose = transl(x,y,z)*rotx(rx*pi/180)*roty(ry*pi/180)*rotz(rz*pi/180)
    /// See also: FromTxyzRxyz()
    /// </summary>
    /// <returns>XYZWPR translation and rotation in mm and degrees</returns>
    public double[] ToTxyzRxyz()
    {
        double[] xyzwpr = new double[6];
        double x = mat[0, 3];
        double y = mat[1, 3];
        double z = mat[2, 3];
        double rx1 = 0;
        double ry1 = 0;
        double rz1 = 0;


        double a = mat[0, 0];
        double b = mat[0, 1];
        double c = mat[0, 2];
        double d = mat[1, 2];
        double e = mat[2, 2];

        if (c == 1)
        {
            ry1 = 0.5 * Math.PI;
            rx1 = 0;
            rz1 = Math.Atan2(mat[1, 0], mat[1, 1]);
        }
        else if (c == -1)
        {
            ry1 = -Math.PI / 2;
            rx1 = 0;
            rz1 = Math.Atan2(mat[1, 0], mat[1, 1]);
        }
        else
        {
            double sy = c;
            double cy1 = +Math.Sqrt(1 - sy * sy);

            double sx1 = -d / cy1;
            double cx1 = e / cy1;

            double sz1 = -b / cy1;
            double cz1 = a / cy1;

            rx1 = Math.Atan2(sx1, cx1);
            ry1 = Math.Atan2(sy, cy1);
            rz1 = Math.Atan2(sz1, cz1);
        }

        xyzwpr[0] = x;
        xyzwpr[1] = y;
        xyzwpr[2] = z;
        xyzwpr[3] = rx1 * 180.0 / Math.PI;
        xyzwpr[4] = ry1 * 180.0 / Math.PI;
        xyzwpr[5] = rz1 * 180.0 / Math.PI;
        return xyzwpr;
    }

    /// <summary>
    /// Returns the quaternion of a pose (4x4 matrix)
    /// </summary>
    /// <param name="Ti"></param>
    /// <returns></returns>
    static double[] ToQuaternion(Mat Ti)
    {
        double[] q = new double[4];
        double a = (Ti[0, 0]);
        double b = (Ti[1, 1]);
        double c = (Ti[2, 2]);
        double sign2 = 1.0;
        double sign3 = 1.0;
        double sign4 = 1.0;
        if ((Ti[2, 1] - Ti[1, 2]) < 0)
        {
            sign2 = -1;
        }
        if ((Ti[0, 2] - Ti[2, 0]) < 0)
        {
            sign3 = -1;
        }
        if ((Ti[1, 0] - Ti[0, 1]) < 0)
        {
            sign4 = -1;
        }
        q[0] = 0.5 * Math.Sqrt(Math.Max(a + b + c + 1, 0));
        q[1] = 0.5 * sign2 * Math.Sqrt(Math.Max(a - b - c + 1, 0));
        q[2] = 0.5 * sign3 * Math.Sqrt(Math.Max(-a + b - c + 1, 0));
        q[3] = 0.5 * sign4 * Math.Sqrt(Math.Max(-a - b + c + 1, 0));
        return q;
    }

    /// <summary>
    /// Returns the pose (4x4 matrix) from quaternion data
    /// </summary>
    /// <param name="q"></param>
    /// <returns></returns>
    static Mat FromQuaternion(double[] qin)
    {
        double qnorm = Math.Sqrt(qin[0] * qin[0] + qin[1] * qin[1] + qin[2] * qin[2] + qin[3] * qin[3]);
        double[] q = new double[4];
        q[0] = qin[0] / qnorm;
        q[1] = qin[1] / qnorm;
        q[2] = qin[2] / qnorm;
        q[3] = qin[3] / qnorm;
        Mat pose = new Mat(1 - 2 * q[2] * q[2] - 2 * q[3] * q[3], 2 * q[1] * q[2] - 2 * q[3] * q[0], 2 * q[1] * q[3] + 2 * q[2] * q[0], 0, 2 * q[1] * q[2] + 2 * q[3] * q[0], 1 - 2 * q[1] * q[1] - 2 * q[3] * q[3], 2 * q[2] * q[3] - 2 * q[1] * q[0], 0, 2 * q[1] * q[3] - 2 * q[2] * q[0], 2 * q[2] * q[3] + 2 * q[1] * q[0], 1 - 2 * q[1] * q[1] - 2 * q[2] * q[2], 0);
        return pose;
    }

    /// <summary>
    /// Converts a pose to an ABB target
    /// </summary>
    /// <param name="H"></param>
    /// <returns></returns>
    static double[] ToABB(Mat H)
    {
        double[] q = ToQuaternion(H);
        double[] xyzq1234 = { H[0, 3], H[1, 3], H[2, 3], q[0], q[1], q[2], q[3] };
        return xyzq1234;
    }

    /// <summary>
    /// Calculates the equivalent position and euler angles ([x,y,z,r,p,w] vector) of the given pose in Universal Robots format
    /// Note: The difference between ToUR and ToXYZWPR is that the first one uses radians for the orientation and the second one uses degres
    /// Note: transl(x,y,z)*rotx(rx*pi/180)*roty(ry*pi/180)*rotz(rz*pi/180)
    /// See also: FromXYZRPW()
    /// </summary>
    /// <returns>XYZWPR translation and rotation in mm and radians</returns>
    public double[] ToUR()
    {
        double[] xyzwpr = new double[6];
        double x = mat[0, 3];
        double y = mat[1, 3];
        double z = mat[2, 3];
        double angle = Math.Acos(Math.Min(Math.Max((mat[0, 0] + mat[1, 1] + mat[2, 2] - 1) / 2, -1), 1));
        double rx = mat[2, 1] - mat[1, 2];
        double ry = mat[0, 2] - mat[2, 0];
        double rz = mat[1, 0] - mat[0, 1];
        if (angle == 0)
        {
            rx = 0;
            ry = 0;
            rz = 0;
        }
        else
        {
            rx = rx * angle / (2 * Math.Sin(angle));
            ry = ry * angle / (2 * Math.Sin(angle));
            rz = rz * angle / (2 * Math.Sin(angle));
        }
        xyzwpr[0] = x;
        xyzwpr[1] = y;
        xyzwpr[2] = z;
        xyzwpr[3] = rx;
        xyzwpr[4] = ry;
        xyzwpr[5] = rz;
        return xyzwpr;
    }

    /// <summary>
    /// Calculates the pose from the position and euler angles ([x,y,z,r,p,w] vector)
    /// Note: The difference between FromUR and FromXYZWPR is that the first one uses radians for the orientation and the second one uses degres
    /// The result is the same as calling: H = transl(x,y,z)*rotx(rx)*roty(ry)*rotz(rz)
    /// </summary>
    /// <param name="xyzwpr">The position and euler angles array</param>
    /// <returns>Homogeneous matrix (4x4)</returns>
    public static Mat FromUR(double[] xyzwpr)
    {
        double x = xyzwpr[0];
        double y = xyzwpr[1];
        double z = xyzwpr[2];
        double w = xyzwpr[3];
        double p = xyzwpr[4];
        double r = xyzwpr[5];
        double angle = Math.Sqrt(w * w + p * p + r * r);
        if (angle < 1e-6)
        {
            return Identity4x4();
        }
        double c = Math.Cos(angle);
        double s = Math.Sin(angle);
        double ux = w / angle;
        double uy = p / angle;
        double uz = r / angle;
        return new Mat(ux * ux + c * (1 - ux * ux), ux * uy * (1 - c) - uz * s, ux * uz * (1 - c) + uy * s, x, ux * uy * (1 - c) + uz * s, uy * uy + (1 - uy * uy) * c, uy * uz * (1 - c) - ux * s, y, ux * uz * (1 - c) - uy * s, uy * uz * (1 - c) + ux * s, uz * uz + (1 - uz * uz) * c, z);
    }

    /// <summary>
    /// Converts a matrix into a one-dimensional array of doubles
    /// </summary>
    /// <returns>one-dimensional array</returns>
    public double[] ToDoubles()
    {
        int cnt = 0;
        double[] array = new double[rows * cols];
        for (int j = 0; j < cols; j++)
        {
            for (int i = 0; i < rows; i++)
            {
                array[cnt] = mat[i, j];
                cnt = cnt + 1;
            }
        }
        return array;
    }

    /// <summary>
    /// Check if the matrix is square
    /// </summary>
    public Boolean IsSquare()
    {
        return (rows == cols);
    }

    public Boolean Is4x4()
    {
        if (cols != 4 || rows != 4)
        {
            return false;
        }
        return true;
    }

    /// <summary>
    /// Check if the matrix is homogeneous (4x4)
    /// </summary>
    public Boolean IsHomogeneous()
    {
        if (!Is4x4())
        {
            return false;
        }
        return true;
        /*
        test = self[0:3,0:3];
        test = test*test.tr()
        test[0,0] = test[0,0] - 1.0
        test[1,1] = test[1,1] - 1.0
        test[2,2] = test[2,2] - 1.0
        zero = 0.0
        for x in range(3):
            for y in range(3):
                zero = zero + abs(test[x,y])
        if zero > 1e-4:
            return False
        return True
        */
    }

    /// <summary>
    /// Returns the inverse of a homogeneous matrix (4x4 matrix)
    /// </summary>
    /// <returns>Homogeneous matrix (4x4)</returns>
    public Mat inv()
    {
        if (!IsHomogeneous())
        {
            throw new MatException("Can't invert a non-homogeneous matrix");
        }
        double[] xyz = this.Pos();
        Mat mat_xyz = new Mat(xyz[0], xyz[1], xyz[2]);
        Mat hinv = this.Duplicate();
        hinv.setPos(0, 0, 0);
        hinv = hinv.Transpose();
        Mat new_pos = rotate(hinv, mat_xyz);
        hinv[0, 3] = -new_pos[0, 0];
        hinv[1, 3] = -new_pos[1, 0];
        hinv[2, 3] = -new_pos[2, 0];
        return hinv;
    }

    /// <summary>
    /// Rotate a vector given a matrix (rotation matrix or homogeneous matrix)
    /// </summary>
    /// <param name="pose">4x4 homogeneous matrix or 3x3 rotation matrix</param>
    /// <param name="vector">4x1 or 3x1 vector</param>
    /// <returns></returns>
    static public Mat rotate(Mat pose, Mat vector)
    {
        if (pose.cols < 3 || pose.rows < 3 || vector.rows < 3)
        {
            throw new MatException("Invalid matrix size");
        }
        Mat pose3x3 = pose.Duplicate();
        Mat vector3 = vector.Duplicate();
        pose3x3.rows = 3;
        pose3x3.cols = 3;
        vector3.rows = 3;
        return pose3x3 * vector3;
    }

    /// <summary>
    /// Returns the XYZ position of the Homogeneous matrix
    /// </summary>
    /// <returns>XYZ position</returns>
    public double[] Pos()
    {
        if (!Is4x4())
        {
            return null;
        }
        double[] xyz = new double[3];
        xyz[0] = mat[0, 3]; xyz[1] = mat[1, 3]; xyz[2] = mat[2, 3];
        return xyz;
    }

    /// <summary>
    /// Sets the 4x4 position of the Homogeneous matrix
    /// </summary>
    /// <param name="xyz">XYZ position</param>
    public void setPos(double[] xyz)
    {
        if (!Is4x4() || xyz.Length < 3)
        {
            return;
        }
        mat[0, 3] = xyz[0]; mat[1, 3] = xyz[1]; mat[2, 3] = xyz[2];
    }

    /// <summary>
    /// Sets the 4x4 position of the Homogeneous matrix
    /// </summary>
    /// <param name="x">X position</param>
    /// <param name="y">Y position</param>
    /// <param name="z">Z position</param>
    public void setPos(double x, double y, double z)
    {
        if (!Is4x4())
        {
            return;
        }
        mat[0, 3] = x; mat[1, 3] = y; mat[2, 3] = z;
    }




    /// <summary>
    /// Returns the VX orientation vector of the Homogeneous matrix
    /// </summary>
    /// <returns>VX orientation vector</returns>
    public double[] VX()
    {
        if (!Is4x4())
        {
            return null;
        }
        double[] xyz = new double[3];
        xyz[0] = mat[0, 0]; xyz[1] = mat[1, 0]; xyz[2] = mat[2, 0];
        return xyz;
    }

    /// <summary>
    /// Sets the VX orientation vector of the Homogeneous matrix
    /// </summary>
    /// <param name="xyz">VX orientation vector</param>
    public void setVX(double[] xyz)
    {
        if (!Is4x4() || xyz.Length < 3)
        {
            return;
        }
        mat[0, 0] = xyz[0]; mat[1, 0] = xyz[1]; mat[2, 0] = xyz[2];
    }
    /// <summary>
    /// Returns the VY orientation vector of the Homogeneous matrix
    /// </summary>
    /// <returns>VY orientation vector</returns>
    public double[] VY()
    {
        if (!Is4x4())
        {
            return null;
        }
        double[] xyz = new double[3];
        xyz[0] = mat[0, 1]; xyz[1] = mat[1, 1]; xyz[2] = mat[2, 1];
        return xyz;
    }

    /// <summary>
    /// Sets the VY orientation vector of the Homogeneous matrix
    /// </summary>
    /// <param name="xyz">VY orientation vector</param>
    public void setVY(double[] xyz)
    {
        if (!Is4x4() || xyz.Length < 3)
        {
            return;
        }
        mat[0, 1] = xyz[0]; mat[1, 1] = xyz[1]; mat[2, 1] = xyz[2];
    }
    /// <summary>
    /// Returns the VZ orientation vector of the Homogeneous matrix
    /// </summary>
    /// <returns>VZ orientation vector</returns>
    public double[] VZ()
    {
        if (!Is4x4())
        {
            return null;
        }
        double[] xyz = new double[3];
        xyz[0] = mat[0, 2]; xyz[1] = mat[1, 2]; xyz[2] = mat[2, 2];
        return xyz;
    }

    /// <summary>
    /// Sets the VZ orientation vector of the Homogeneous matrix
    /// </summary>
    /// <param name="xyz">VZ orientation vector</param>
    public void setVZ(double[] xyz)
    {
        if (!Is4x4() || xyz.Length < 3)
        {
            return;
        }
        mat[0, 2] = xyz[0]; mat[1, 2] = xyz[1]; mat[2, 2] = xyz[2];
    }



    public double this[int iRow, int iCol]      // Access this matrix as a 2D array
    {
        get { return mat[iRow, iCol]; }
        set { mat[iRow, iCol] = value; }
    }

    public Mat GetCol(int k)
    {
        Mat m = new Mat(rows, 1);
        for (int i = 0; i < rows; i++) m[i, 0] = mat[i, k];
        return m;
    }

    public void SetCol(Mat v, int k)
    {
        for (int i = 0; i < rows; i++) mat[i, k] = v[i, 0];
    }

    public Mat Duplicate()                   // Function returns the copy of this matrix
    {
        Mat matrix = new Mat(rows, cols);
        for (int i = 0; i < rows; i++)
            for (int j = 0; j < cols; j++)
                matrix[i, j] = mat[i, j];
        return matrix;
    }

    public static Mat ZeroMatrix(int iRows, int iCols)       // Function generates the zero matrix
    {
        Mat matrix = new Mat(iRows, iCols);
        for (int i = 0; i < iRows; i++)
            for (int j = 0; j < iCols; j++)
                matrix[i, j] = 0;
        return matrix;
    }

    public static Mat IdentityMatrix(int iRows, int iCols)   // Function generates the identity matrix
    {
        Mat matrix = ZeroMatrix(iRows, iCols);
        for (int i = 0; i < Math.Min(iRows, iCols); i++)
            matrix[i, i] = 1;
        return matrix;
    }

    /// <summary>
    /// Returns an identity 4x4 matrix (homogeneous matrix)
    /// </summary>
    /// <returns></returns>
    public static Mat Identity4x4()
    {
        return Mat.IdentityMatrix(4, 4);
    }

    /*
    public static Mat Parse(string ps)                        // Function parses the matrix from string
    {
        string s = NormalizeMatrixString(ps);
        string[] rows = Regex.Split(s, "\r\n");
        string[] nums = rows[0].Split(' ');
        Mat matrix = new Mat(rows.Length, nums.Length);
        try
        {
            for (int i = 0; i < rows.Length; i++)
            {
                nums = rows[i].Split(' ');
                for (int j = 0; j < nums.Length; j++) matrix[i, j] = double.Parse(nums[j]);
            }
        }
        catch (FormatException exc) { throw new MatException("Wrong input format!"); }
        return matrix;
    }*/

    public override string ToString()                           // Function returns matrix as a string
    {
        string s = "";
        bool string_as_xyzabc = IsHomogeneous();
        if (string_as_xyzabc)
        {
            var letter = new List<string>() { "X=", "Y=", "Z=", "Rx=", "Ry=", "Rz=" };
            var units = new List<string>() { "mm", "mm", "mm", "deg", "deg", "deg" };

            var values = this.ToTxyzRxyz();
            for (int j = 0; j < 6; j++) s += letter[j] + String.Format("{0,6:0.000}", values[j]) + " " + units[j] + " , ";
            s = s.Remove(s.Length - 3);
        }
        else
        {
            for (int i = 0; i < rows; i++)
            {
                for (int j = 0; j < cols; j++) s += String.Format("{0,5:0.00}", mat[i, j]) + " ";
                s += "\r\n";
            }
        }
        return s;
    }

    /// <summary>
    /// Transpose a matrix
    /// </summary>
    /// <returns></returns>
    public Mat Transpose()
    {
        return Transpose(this);
    }
    public static Mat Transpose(Mat m)              // Matrix transpose, for any rectangular matrix
    {
        Mat t = new Mat(m.cols, m.rows);
        for (int i = 0; i < m.rows; i++)
            for (int j = 0; j < m.cols; j++)
                t[j, i] = m[i, j];
        return t;
    }

    private static void SafeAplusBintoC(Mat A, int xa, int ya, Mat B, int xb, int yb, Mat C, int size)
    {
        for (int i = 0; i < size; i++)          // rows
            for (int j = 0; j < size; j++)     // cols
            {
                C[i, j] = 0;
                if (xa + j < A.cols && ya + i < A.rows) C[i, j] += A[ya + i, xa + j];
                if (xb + j < B.cols && yb + i < B.rows) C[i, j] += B[yb + i, xb + j];
            }
    }

    private static void SafeAminusBintoC(Mat A, int xa, int ya, Mat B, int xb, int yb, Mat C, int size)
    {
        for (int i = 0; i < size; i++)          // rows
            for (int j = 0; j < size; j++)     // cols
            {
                C[i, j] = 0;
                if (xa + j < A.cols && ya + i < A.rows) C[i, j] += A[ya + i, xa + j];
                if (xb + j < B.cols && yb + i < B.rows) C[i, j] -= B[yb + i, xb + j];
            }
    }

    private static void SafeACopytoC(Mat A, int xa, int ya, Mat C, int size)
    {
        for (int i = 0; i < size; i++)          // rows
            for (int j = 0; j < size; j++)     // cols
            {
                C[i, j] = 0;
                if (xa + j < A.cols && ya + i < A.rows) C[i, j] += A[ya + i, xa + j];
            }
    }

    private static void AplusBintoC(Mat A, int xa, int ya, Mat B, int xb, int yb, Mat C, int size)
    {
        for (int i = 0; i < size; i++)          // rows
            for (int j = 0; j < size; j++) C[i, j] = A[ya + i, xa + j] + B[yb + i, xb + j];
    }

    private static void AminusBintoC(Mat A, int xa, int ya, Mat B, int xb, int yb, Mat C, int size)
    {
        for (int i = 0; i < size; i++)          // rows
            for (int j = 0; j < size; j++) C[i, j] = A[ya + i, xa + j] - B[yb + i, xb + j];
    }

    private static void ACopytoC(Mat A, int xa, int ya, Mat C, int size)
    {
        for (int i = 0; i < size; i++)          // rows
            for (int j = 0; j < size; j++) C[i, j] = A[ya + i, xa + j];
    }

    private static Mat MultiplyMat(Mat A, Mat B)                // Smart matrix multiplication
    {
        if (A.cols != B.rows) throw new MatException("Wrong dimension of matrix!");

        Mat R;

        int msize = Math.Max(Math.Max(A.rows, A.cols), Math.Max(B.rows, B.cols));

        if (msize < 32)
        {
            R = ZeroMatrix(A.rows, B.cols);
            for (int i = 0; i < R.rows; i++)
                for (int j = 0; j < R.cols; j++)
                    for (int k = 0; k < A.cols; k++)
                        R[i, j] += A[i, k] * B[k, j];
            return R;
        }

        int size = 1; int n = 0;
        while (msize > size) { size *= 2; n++; };
        int h = size / 2;


        Mat[,] mField = new Mat[n, 9];

        /*
         *  8x8, 8x8, 8x8, ...
         *  4x4, 4x4, 4x4, ...
         *  2x2, 2x2, 2x2, ...
         *  . . .
         */

        int z;
        for (int i = 0; i < n - 4; i++)          // rows
        {
            z = (int)Math.Pow(2, n - i - 1);
            for (int j = 0; j < 9; j++) mField[i, j] = new Mat(z, z);
        }

        SafeAplusBintoC(A, 0, 0, A, h, h, mField[0, 0], h);
        SafeAplusBintoC(B, 0, 0, B, h, h, mField[0, 1], h);
        MultiplyMatRun(mField[0, 0], mField[0, 1], mField[0, 1 + 1], 1, mField); // (A11 + A22) * (B11 + B22);

        SafeAplusBintoC(A, 0, h, A, h, h, mField[0, 0], h);
        SafeACopytoC(B, 0, 0, mField[0, 1], h);
        MultiplyMatRun(mField[0, 0], mField[0, 1], mField[0, 1 + 2], 1, mField); // (A21 + A22) * B11;

        SafeACopytoC(A, 0, 0, mField[0, 0], h);
        SafeAminusBintoC(B, h, 0, B, h, h, mField[0, 1], h);
        MultiplyMatRun(mField[0, 0], mField[0, 1], mField[0, 1 + 3], 1, mField); //A11 * (B12 - B22);

        SafeACopytoC(A, h, h, mField[0, 0], h);
        SafeAminusBintoC(B, 0, h, B, 0, 0, mField[0, 1], h);
        MultiplyMatRun(mField[0, 0], mField[0, 1], mField[0, 1 + 4], 1, mField); //A22 * (B21 - B11);

        SafeAplusBintoC(A, 0, 0, A, h, 0, mField[0, 0], h);
        SafeACopytoC(B, h, h, mField[0, 1], h);
        MultiplyMatRun(mField[0, 0], mField[0, 1], mField[0, 1 + 5], 1, mField); //(A11 + A12) * B22;

        SafeAminusBintoC(A, 0, h, A, 0, 0, mField[0, 0], h);
        SafeAplusBintoC(B, 0, 0, B, h, 0, mField[0, 1], h);
        MultiplyMatRun(mField[0, 0], mField[0, 1], mField[0, 1 + 6], 1, mField); //(A21 - A11) * (B11 + B12);

        SafeAminusBintoC(A, h, 0, A, h, h, mField[0, 0], h);
        SafeAplusBintoC(B, 0, h, B, h, h, mField[0, 1], h);
        MultiplyMatRun(mField[0, 0], mField[0, 1], mField[0, 1 + 7], 1, mField); // (A12 - A22) * (B21 + B22);

        R = new Mat(A.rows, B.cols);                  // result

        /// C11
        for (int i = 0; i < Math.Min(h, R.rows); i++)          // rows
            for (int j = 0; j < Math.Min(h, R.cols); j++)     // cols
                R[i, j] = mField[0, 1 + 1][i, j] + mField[0, 1 + 4][i, j] - mField[0, 1 + 5][i, j] + mField[0, 1 + 7][i, j];

        /// C12
        for (int i = 0; i < Math.Min(h, R.rows); i++)          // rows
            for (int j = h; j < Math.Min(2 * h, R.cols); j++)     // cols
                R[i, j] = mField[0, 1 + 3][i, j - h] + mField[0, 1 + 5][i, j - h];

        /// C21
        for (int i = h; i < Math.Min(2 * h, R.rows); i++)          // rows
            for (int j = 0; j < Math.Min(h, R.cols); j++)     // cols
                R[i, j] = mField[0, 1 + 2][i - h, j] + mField[0, 1 + 4][i - h, j];

        /// C22
        for (int i = h; i < Math.Min(2 * h, R.rows); i++)          // rows
            for (int j = h; j < Math.Min(2 * h, R.cols); j++)     // cols
                R[i, j] = mField[0, 1 + 1][i - h, j - h] - mField[0, 1 + 2][i - h, j - h] + mField[0, 1 + 3][i - h, j - h] + mField[0, 1 + 6][i - h, j - h];

        return R;
    }

    // function for square matrix 2^N x 2^N
    private static void MultiplyMatRun(Mat A, Mat B, Mat C, int l, Mat[,] f)    // A * B into C, level of recursion, matrix field
    {
        int size = A.rows;
        int h = size / 2;

        if (size < 32)
        {
            for (int i = 0; i < C.rows; i++)
                for (int j = 0; j < C.cols; j++)
                {
                    C[i, j] = 0;
                    for (int k = 0; k < A.cols; k++) C[i, j] += A[i, k] * B[k, j];
                }
            return;
        }

        AplusBintoC(A, 0, 0, A, h, h, f[l, 0], h);
        AplusBintoC(B, 0, 0, B, h, h, f[l, 1], h);
        MultiplyMatRun(f[l, 0], f[l, 1], f[l, 1 + 1], l + 1, f); // (A11 + A22) * (B11 + B22);

        AplusBintoC(A, 0, h, A, h, h, f[l, 0], h);
        ACopytoC(B, 0, 0, f[l, 1], h);
        MultiplyMatRun(f[l, 0], f[l, 1], f[l, 1 + 2], l + 1, f); // (A21 + A22) * B11;

        ACopytoC(A, 0, 0, f[l, 0], h);
        AminusBintoC(B, h, 0, B, h, h, f[l, 1], h);
        MultiplyMatRun(f[l, 0], f[l, 1], f[l, 1 + 3], l + 1, f); //A11 * (B12 - B22);

        ACopytoC(A, h, h, f[l, 0], h);
        AminusBintoC(B, 0, h, B, 0, 0, f[l, 1], h);
        MultiplyMatRun(f[l, 0], f[l, 1], f[l, 1 + 4], l + 1, f); //A22 * (B21 - B11);

        AplusBintoC(A, 0, 0, A, h, 0, f[l, 0], h);
        ACopytoC(B, h, h, f[l, 1], h);
        MultiplyMatRun(f[l, 0], f[l, 1], f[l, 1 + 5], l + 1, f); //(A11 + A12) * B22;

        AminusBintoC(A, 0, h, A, 0, 0, f[l, 0], h);
        AplusBintoC(B, 0, 0, B, h, 0, f[l, 1], h);
        MultiplyMatRun(f[l, 0], f[l, 1], f[l, 1 + 6], l + 1, f); //(A21 - A11) * (B11 + B12);

        AminusBintoC(A, h, 0, A, h, h, f[l, 0], h);
        AplusBintoC(B, 0, h, B, h, h, f[l, 1], h);
        MultiplyMatRun(f[l, 0], f[l, 1], f[l, 1 + 7], l + 1, f); // (A12 - A22) * (B21 + B22);

        /// C11
        for (int i = 0; i < h; i++)          // rows
            for (int j = 0; j < h; j++)     // cols
                C[i, j] = f[l, 1 + 1][i, j] + f[l, 1 + 4][i, j] - f[l, 1 + 5][i, j] + f[l, 1 + 7][i, j];

        /// C12
        for (int i = 0; i < h; i++)          // rows
            for (int j = h; j < size; j++)     // cols
                C[i, j] = f[l, 1 + 3][i, j - h] + f[l, 1 + 5][i, j - h];

        /// C21
        for (int i = h; i < size; i++)          // rows
            for (int j = 0; j < h; j++)     // cols
                C[i, j] = f[l, 1 + 2][i - h, j] + f[l, 1 + 4][i - h, j];

        /// C22
        for (int i = h; i < size; i++)          // rows
            for (int j = h; j < size; j++)     // cols
                C[i, j] = f[l, 1 + 1][i - h, j - h] - f[l, 1 + 2][i - h, j - h] + f[l, 1 + 3][i - h, j - h] + f[l, 1 + 6][i - h, j - h];
    }

    public static Mat MultiplyMatSimple(Mat m1, Mat m2)                  // Stupid matrix multiplication
    {
        if (m1.cols != m2.rows) throw new MatException("Wrong matrix dimensions to allow multiplication!");

        Mat result = ZeroMatrix(m1.rows, m2.cols);
        for (int i = 0; i < result.rows; i++)
            for (int j = 0; j < result.cols; j++)
                for (int k = 0; k < m1.cols; k++)
                    result[i, j] += m1[i, k] * m2[k, j];
        return result;
    }
    private static Mat Multiply(double n, Mat m)                          // Multiplication by constant n
    {
        Mat r = new Mat(m.rows, m.cols);
        for (int i = 0; i < m.rows; i++)
            for (int j = 0; j < m.cols; j++)
                r[i, j] = m[i, j] * n;
        return r;
    }

    private static double[] Multiply(Mat m1, double[] p1)         // Add matrix
    {
        double[] p2 = new double[p1.Length];
        if (m1.cols == 4 && m1.rows == 4 && p1.Length == 3)
        {
            // multiply a homogeneous matrix and a 3D vector
            p2[0] = m1[0, 0] * p1[0] + m1[0, 1] * p1[1] + m1[0, 2] * p1[2] + m1[0, 3];
            p2[1] = m1[1, 0] * p1[0] + m1[1, 1] * p1[1] + m1[1, 2] * p1[2] + m1[1, 3];
            p2[2] = m1[2, 0] * p1[0] + m1[2, 1] * p1[1] + m1[2, 2] * p1[2] + m1[2, 3];
            return p2;
        }
        if (m1.cols != p1.Length) throw new MatException("Matrices must have the same dimensions!");
        for (int i = 0; i < m1.rows; i++)
        {
            double vi = 0;
            for (int j = 0; j < m1.cols; j++)
            {
                vi = vi + m1[i, j] * p1[j];
            }
            p2[i] = vi;
        }
        return p2;
    }
    private static Mat Add(Mat m1, Mat m2)         // Add matrix
    {
        if (m1.rows != m2.rows || m1.cols != m2.cols) throw new MatException("Matrices must have the same dimensions!");
        Mat r = new Mat(m1.rows, m1.cols);
        for (int i = 0; i < r.rows; i++)
            for (int j = 0; j < r.cols; j++)
                r[i, j] = m1[i, j] + m2[i, j];
        return r;
    }

    public static string NormalizeMatrixString(string matStr)	// From Andy - thank you! :)
    {
        // Remove any multiple spaces
        while (matStr.IndexOf("  ") != -1)
            matStr = matStr.Replace("  ", " ");

        // Remove any spaces before or after newlines
        matStr = matStr.Replace(" \r\n", "\r\n");
        matStr = matStr.Replace("\r\n ", "\r\n");

        // If the data ends in a newline, remove the trailing newline.
        // Make it easier by first replacing \r\n’s with |’s then
        // restore the |’s with \r\n’s
        matStr = matStr.Replace("\r\n", "|");
        while (matStr.LastIndexOf("|") == (matStr.Length - 1))
            matStr = matStr.Substring(0, matStr.Length - 1);

        matStr = matStr.Replace("|", "\r\n");
        return matStr.Trim();
    }


    // Operators
    public static Mat operator -(Mat m)
    { return Mat.Multiply(-1, m); }

    public static Mat operator +(Mat m1, Mat m2)
    { return Mat.Add(m1, m2); }

    public static Mat operator -(Mat m1, Mat m2)
    { return Mat.Add(m1, -m2); }

    public static Mat operator *(Mat m1, Mat m2)
    { return Mat.MultiplyMat(m1, m2); }

    public static Mat operator *(double n, Mat m)
    { return Mat.Multiply(n, m); }

    public static double[] operator *(Mat m, double[] n)
    { return Mat.Multiply(m, n); }
}


/// <summary>
/// This class is the link to allows to create macros and automate Robodk.
/// Any interaction is made through \"items\" (Item() objects). An item is an object in the
/// robodk tree (it can be either a robot, an object, a tool, a frame, a program, ...).
/// </summary>
public class RoboDK
{
    /// <summary>
    /// Class used for RoboDK exceptions
    /// </summary>  
    public class RDKException : Exception
    {
        public RDKException(string Message)
            : base(Message)
        { }
    }

    // Tree item types
    public const int ITEM_TYPE_ANY = -1;
    public const int ITEM_TYPE_STATION = 1;
    public const int ITEM_TYPE_ROBOT = 2;
    public const int ITEM_TYPE_FRAME = 3;
    public const int ITEM_TYPE_TOOL = 4;
    public const int ITEM_TYPE_OBJECT = 5;
    public const int ITEM_TYPE_TARGET = 6;
    public const int ITEM_TYPE_PROGRAM = 8;
    public const int ITEM_TYPE_INSTRUCTION = 9;
    public const int ITEM_TYPE_PROGRAM_PYTHON = 10;
    public const int ITEM_TYPE_MACHINING = 11;
    public const int ITEM_TYPE_BALLBARVALIDATION = 12;
    public const int ITEM_TYPE_CALIBPROJECT = 13;
    public const int ITEM_TYPE_VALID_ISO9283 = 14;

    // Instruction types
    public const int INS_TYPE_INVALID = -1;
    public const int INS_TYPE_MOVE = 0;
    public const int INS_TYPE_MOVEC = 1;
    public const int INS_TYPE_CHANGESPEED = 2;
    public const int INS_TYPE_CHANGEFRAME = 3;
    public const int INS_TYPE_CHANGETOOL = 4;
    public const int INS_TYPE_CHANGEROBOT = 5;
    public const int INS_TYPE_PAUSE = 6;
    public const int INS_TYPE_EVENT = 7;
    public const int INS_TYPE_CODE = 8;
    public const int INS_TYPE_PRINT = 9;

    // Move types
    public const int MOVE_TYPE_INVALID = -1;
    public const int MOVE_TYPE_JOINT = 1;
    public const int MOVE_TYPE_LINEAR = 2;
    public const int MOVE_TYPE_CIRCULAR = 3;

    // Station parameters request
    public const string PATH_OPENSTATION = "PATH_OPENSTATION";
    public const string FILE_OPENSTATION = "FILE_OPENSTATION";
    public const string PATH_DESKTOP = "PATH_DESKTOP";

    // Script execution types
    public const int RUNMODE_SIMULATE = 1;                      // performs the simulation moving the robot (default)
    public const int RUNMODE_QUICKVALIDATE = 2;                 // performs a quick check to validate the robot movements
    public const int RUNMODE_MAKE_ROBOTPROG = 3;                // makes the robot program
    public const int RUNMODE_MAKE_ROBOTPROG_AND_UPLOAD = 4;     // makes the robot program and updates it to the robot
    public const int RUNMODE_MAKE_ROBOTPROG_AND_START = 5;      // makes the robot program and starts it on the robot (independently from the PC)
    public const int RUNMODE_RUN_ROBOT = 6;                     // moves the real robot from the PC (PC is the client, the robot behaves like a server)

    // Program execution type
    public const int PROGRAM_RUN_ON_SIMULATOR = 1;        // Set the program to run on the simulator
    public const int PROGRAM_RUN_ON_ROBOT = 2;            // Set the program to run on the robot

    // TCP calibration types
    public const int CALIBRATE_TCP_BY_POINT = 0;
    public const int CALIBRATE_TCP_BY_PLANE = 1;

    // Reference frame calibration types
    public const int CALIBRATE_FRAME_3P_P1_ON_X = 0;    //Calibrate by 3 points: [X, X+, Y+] (p1 on X axis)
    public const int CALIBRATE_FRAME_3P_P1_ORIGIN = 1;  //Calibrate by 3 points: [Origin, X+, XY+] (p1 is origin)
    public const int CALIBRATE_FRAME_6P = 2;            //Calibrate by 6 points
    public const int CALIBRATE_TURNTABLE = 3;           //Calibrate turntable

    // projection types (for AddCurve, AddPoints and ProjectCurve)
    public const int PROJECTION_NONE = 0; // No curve projection
    public const int PROJECTION_CLOSEST = 1; // The projection will the closest point on the surface
    public const int PROJECTION_ALONG_NORMAL = 2; // The projection will be done along the normal.
    public const int PROJECTION_ALONG_NORMAL_RECALC = 3; // The projection will be done along the normal. Furthermore, the normal will be recalculated according to the surface normal.
    public const int PROJECTION_CLOSEST_RECALC = 4; // The projection will be the closest point on the surface and the normals will be recalculated
    public const int PROJECTION_RECALC = 5; // The normals are recalculated according to the surface normal of the closest projection. The points are not changed.


    // Euler type
    public const int JOINT_FORMAT = -1; // joints
    public const int EULER_RX_RYp_RZpp = 0; // generic
    public const int EULER_RZ_RYp_RXpp = 1; // ABB RobotStudio
    public const int EULER_RZ_RYp_RZpp = 2; // Kawasaki, Adept, Staubli
    public const int EULER_RZ_RXp_RZpp = 3; // CATIA, SolidWorks
    public const int EULER_RX_RY_RZ = 4; // Fanuc, Kuka, Motoman, Nachi
    public const int EULER_RZ_RY_RX = 5; // CRS
    public const int EULER_QUEATERNION = 6; // ABB Rapid

    // State of the RoboDK window
    public const int WINDOWSTATE_HIDDEN = -1;
    public const int WINDOWSTATE_SHOW = 0;
    public const int WINDOWSTATE_MINIMIZED = 1;
    public const int WINDOWSTATE_NORMAL = 2;
    public const int WINDOWSTATE_MAXIMIZED = 3;
    public const int WINDOWSTATE_FULLSCREEN = 4;
    public const int WINDOWSTATE_CINEMA = 5;
    public const int WINDOWSTATE_FULLSCREEN_CINEMA = 6;

    // Instruction program call type:
    public const int INSTRUCTION_CALL_PROGRAM = 0;
    public const int INSTRUCTION_INSERT_CODE = 1;
    public const int INSTRUCTION_START_THREAD = 2;
    public const int INSTRUCTION_COMMENT = 3;


    // Object selection features:
    public const int FEATURE_NONE = 0;
    public const int FEATURE_SURFACE = 1;
    public const int FEATURE_CURVE = 2;
    public const int FEATURE_POINT = 3;

    // Spray gun simulation:
    public const int SPRAY_OFF = 0;
    public const int SPRAY_ON = 1;

    // Collision checking state
    public const int COLLISION_OFF = 0;
    public const int COLLISION_ON = 1;

    // RoboDK Window Flags
    public const int FLAG_ROBODK_TREE_ACTIVE = 1;
    public const int FLAG_ROBODK_3DVIEW_ACTIVE = 2;
    public const int FLAG_ROBODK_LEFT_CLICK = 4;
    public const int FLAG_ROBODK_RIGHT_CLICK = 8;
    public const int FLAG_ROBODK_DOUBLE_CLICK = 16;
    public const int FLAG_ROBODK_MENU_ACTIVE = 32;
    public const int FLAG_ROBODK_MENUFILE_ACTIVE = 64;
    public const int FLAG_ROBODK_MENUEDIT_ACTIVE = 128;
    public const int FLAG_ROBODK_MENUPROGRAM_ACTIVE = 256;
    public const int FLAG_ROBODK_MENUTOOLS_ACTIVE = 512;
    public const int FLAG_ROBODK_MENUUTILITIES_ACTIVE = 1024;
    public const int FLAG_ROBODK_MENUCONNECT_ACTIVE = 2048;
    public const int FLAG_ROBODK_WINDOWKEYS_ACTIVE = 4096;
    public const int FLAG_ROBODK_TREE_VISIBLE = 8192;
    public const int FLAG_ROBODK_REFERENCES_VISIBLE = 16384;
    public const int FLAG_ROBODK_NONE = 0;
    public const int FLAG_ROBODK_ALL = 0xFFFF;
    public const int FLAG_ROBODK_MENU_ACTIVE_ALL = FLAG_ROBODK_MENU_ACTIVE | FLAG_ROBODK_MENUFILE_ACTIVE | FLAG_ROBODK_MENUEDIT_ACTIVE | FLAG_ROBODK_MENUPROGRAM_ACTIVE | FLAG_ROBODK_MENUTOOLS_ACTIVE | FLAG_ROBODK_MENUUTILITIES_ACTIVE | FLAG_ROBODK_MENUCONNECT_ACTIVE;

    // RoboDK Item Flags
    public const int FLAG_ITEM_SELECTABLE = 1;
    public const int FLAG_ITEM_EDITABLE = 2;
    public const int FLAG_ITEM_DRAGALLOWED = 4;
    public const int FLAG_ITEM_DROPALLOWED = 8;
    public const int FLAG_ITEM_ENABLED = 32;
    public const int FLAG_ITEM_AUTOTRISTATE = 64;
    public const int FLAG_ITEM_NOCHILDREN = 128;
    public const int FLAG_ITEM_USERTRISTATE = 256;
    public const int FLAG_ITEM_NONE = 0;
    public const int FLAG_ITEM_ALL = 64 + 32 + 8 + 4 + 2 + 1;

    // Robot types
    public const int MAKE_ROBOT_1R = 1;
    public const int MAKE_ROBOT_2R = 2;
    public const int MAKE_ROBOT_3R = 3;
    public const int MAKE_ROBOT_1T = 4;
    public const int MAKE_ROBOT_2T = 5;
    public const int MAKE_ROBOT_3T = 6;
    public const int MAKE_ROBOT_6DOF = 7;
    public const int MAKE_ROBOT_7DOF = 8;
    public const int MAKE_ROBOT_SCARA = 9;
    public const int MAKE_ROBOT_GRIPPER = 10;

    // Path Error bit mask
    public const int ERROR_KINEMATIC = 1;          // One or more points is not reachable
    public const int ERROR_PATH_LIMIT = 10;         // The path reaches the limit of joint axes
    public const int ERROR_PATH_SINGULARITY = 100;   // The robot reached a singularity point
    public const int ERROR_PATH_NEARSINGULARITY = 1000;// The robot is too close to a singularity. Lower the singularity tolerance to allow the robot to continue.
    public const int ERROR_COLLISION = 100000;       // Collision detected

    // Interactive selection option (for 3D mouse behavior and setInteractiveMode)
    public const int SELECT_NONE = 0;
    public const int SELECT_RECTANGLE = 1;
    public const int SELECT_ROTATE = 2;
    public const int SELECT_ZOOM = 3;
    public const int SELECT_PAN = 4;
    public const int SELECT_MOVE = 5;
    public const int SELECT_MOVE_SHIFT = 6;
    public const int SELECT_MOVE_CLEAR = 7;

    // Bit masks to show specific reference frames and customize the display of references (for picking references with the 3D mouse and setInteractiveMode)
    public const int DISPLAY_REF_DEFAULT = -1;
    public const int DISPLAY_REF_NONE = 0;
    public const int DISPLAY_REF_TX = 1;
    public const int DISPLAY_REF_TY = 2;
    public const int DISPLAY_REF_TZ = 4;
    public const int DISPLAY_REF_RX = 8;
    public const int DISPLAY_REF_RY = 16;
    public const int DISPLAY_REF_RZ = 32;
    public const int DISPLAY_REF_PXY = 64;
    public const int DISPLAY_REF_PXZ = 128;
    public const int DISPLAY_REF_PYZ = 256;
    public const int DISPLAY_REF_ALL = 511;

    // Optional returned information from InstructionListJoints
    public const int LISTJOINTS_DEFAULT = 1; // same as 0
    public const int LISTJOINTS_SPEED = 2;
    public const int LISTJOINTS_ACCEL = 3;

    // Event types
    public const int EVENT_SELECTION_TREE_CHANGED = 1;
    public const int EVENT_ITEM_MOVED = 2;
    public const int EVENT_REFERENCE_PICKED = 3;
    public const int EVENT_REFERENCE_RELEASED = 4;
    public const int EVENT_TOOL_MODIFIED = 5;
    public const int EVENT_CREATED_ISOCUBE = 6;
    public const int EVENT_SELECTION_3D_CHANGED = 7;
    public const int EVENT_3DVIEW_MOVED = 8;

    // Robot link visibility
    public const int VISIBLE_REFERENCE_DEFAULT = -1;
    public const int VISIBLE_REFERENCE_ON = 1;
    public const int VISIBLE_REFERENCE_OFF = 0;
    public const int VISIBLE_ROBOT_NONE = 0;
    public const int VISIBLE_ROBOT_FLANGE = 0x01;
    public const int VISIBLE_ROBOT_AXIS_Base_3D = 0x01 << 1;
    public const int VISIBLE_ROBOT_AXIS_Base_REF = 0x01 << 2;
    public const int VISIBLE_ROBOT_AXIS_1_3D = 0x01 << 3;
    public const int VISIBLE_ROBOT_AXIS_1_REF = 0x01 << 4;
    public const int VISIBLE_ROBOT_AXIS_2_3D = 0x01 << 5;
    public const int VISIBLE_ROBOT_AXIS_2_REF = 0x01 << 6;
    public const int VISIBLE_ROBOT_AXIS_3_3D = 0x01 << 7;
    public const int VISIBLE_ROBOT_AXIS_3_REF = 0x01 << 8;
    public const int VISIBLE_ROBOT_AXIS_4_3D = 0x01 << 9;
    public const int VISIBLE_ROBOT_AXIS_4_REF = 0x01 << 10;
    public const int VISIBLE_ROBOT_AXIS_5_3D = 0x01 << 11;
    public const int VISIBLE_ROBOT_AXIS_5_REF = 0x01 << 12;
    public const int VISIBLE_ROBOT_AXIS_6_3D = 0x01 << 13;
    public const int VISIBLE_ROBOT_AXIS_6_REF = 0x01 << 14;
    public const int VISIBLE_ROBOT_AXIS_7_3D = 0x01 << 15;
    public const int VISIBLE_ROBOT_AXIS_7_REF = 0x02 << 16;
    public const int VISIBLE_ROBOT_DEFAULT = 0x2AAAAAAB;
    public const int VISIBLE_ROBOT_ALL = 0x7FFFFFFF;
    public const int VISIBLE_ROBOT_ALL_REFS = 0x15555555;


    public System.Diagnostics.Process PROCESS = null; // pointer to the process
    private IntPtr window_handle = IntPtr.Zero;
    public string LAST_STATUS_MESSAGE = ""; // holds any warnings for the last call


    string APPLICATION_DIR = "";            // file path to the robodk program (executable), typically C:/RoboDK/bin/RoboDK.exe. Leave empty to use the registry key: HKEY_LOCAL_MACHINE\SOFTWARE\RoboDK
    string ARGUMENTS = "";                  // arguments to provide to RoboDK on startup
    int SAFE_MODE = 1;                      // checks that provided items exist in memory
    int AUTO_UPDATE = 0;                    // if AUTO_UPDATE is zero, the scene is rendered after every function call  
    int _TIMEOUT = 10 * 1000;               // timeout for communication, in seconds
    Socket _COM = null;                     // tcpip com
    Socket _COM_EVT = null;                 // tcpip com for events (separate channel)
    string IP = "localhost";                // IP address of the simulator (localhost if it is the same computer), otherwise, use RL = Robolink('yourip') to set to a different IP
    int PORT_START = 20500;                 // port to start looking for app connection
    int PORT_END = 20500;                   // port to stop looking for app connection
    bool START_HIDDEN = false;              // forces to start hidden. ShowRoboDK must be used to show the window
    int PORT = -1;                          // port where connection succeeded
    int PORT_FORCED = -1;                   // port to force RoboDK to start listening
    int BUILD = 0;                          // This variable holds the build id and is used for version checking


    //Returns 1 if connection is valid, returns 0 if connection is invalid
    bool is_connected()
    {
        return _COM != null && _COM.Connected;
    }

    /// <summary>
    /// Checks if the object is currently linked to RoboDK
    /// </summary>
    /// <returns></returns>
    public bool Connected()
    {
        //return _COM.Connected;//does not work well
        if (_COM == null)
        {
            return false;
        }
        bool part1 = _COM.Poll(1000, SelectMode.SelectRead);
        bool part2 = _COM.Available == 0;
        if (part1 && part2)
        {
            return false;
        }
        else
        {
            return true;
        }
    }

    //If we are not connected it will attempt a connection, if it fails, it will throw an error
    void _check_connection()
    {
        if (!is_connected() && !Connect())
        {
            window_handle = IntPtr.Zero;
            throw new RDKException("Can't connect to RoboDK API");
        }
    }

    // checks the status of the connection
    int _check_status()
    {
        int status = _recv_Int();
        LAST_STATUS_MESSAGE = "";
        if (status > 0 && status < 10)
        {
            LAST_STATUS_MESSAGE = "Unknown error";
            if (status == 1)
            {
                LAST_STATUS_MESSAGE = "Invalid item provided: The item identifier provided is not valid or it does not exist.";
            }
            else if (status == 2)
            {//output warning
                LAST_STATUS_MESSAGE = _recv_Line();
                //print("WARNING: " + strproblems);
                //#warn(strproblems)# does not show where is the problem...
                return 0;
            }
            else if (status == 3)
            { // output error
                LAST_STATUS_MESSAGE = _recv_Line();
                throw new RDKException(LAST_STATUS_MESSAGE);
            }
            else if (status == 9)
            {
                LAST_STATUS_MESSAGE = "Invalid license. Contact us at: info@robodk.com";
            }
            //print(strproblems);
            throw new RDKException(LAST_STATUS_MESSAGE); //raise Exception(strproblems)
        }
        else if (status == 0)
        {
            // everything is OK
            //status = status
        }
        else
        {
            throw new RDKException("Problems running function"); //raise Exception('Problems running function');
        }
        return status;
    }

    //Formats the color in a vector of size 4x1 and ranges [0,1]
    bool check_color(double[] color)
    {
        if (color.Length < 4)
        {
            throw new RDKException("Invalid color. A color must be a 4-size double array [r,g,b,a]"); //raise Exception('Problems running function');
            //return false;
        }
        return true;
    }
    //Formats the color in a vector of size 4x1 and ranges [0,1]
    bool check_color(List<double> color)
    {
        if (color.Count < 4)
        {
            throw new RDKException("Invalid color. A color must be a 4-size double array [r,g,b,a]"); //raise Exception('Problems running function');
            //return false;
        }
        return true;
    }

    //Sends a string of characters with a \\n
    void _send_Line(string line, Socket com = null)
    {
        if (com == null)
            com = _COM;

        line.Replace('\n', ' ');// one new line at the end only!
        byte[] data = System.Text.Encoding.UTF8.GetBytes(line + "\n");
        com.Send(data);
    }

    string _recv_Line(Socket com = null)
    {
        if (com == null)
            com = _COM;

        //Receives a string. It reads until if finds LF (\\n)
        byte[] buffer = new byte[1];
        int bytesread = com.Receive(buffer, 1, SocketFlags.None);
        string line = "";
        while (bytesread > 0 && buffer[0] != '\n')
        {
            line = line + System.Text.Encoding.UTF8.GetString(buffer);
            bytesread = com.Receive(buffer, 1, SocketFlags.None);
        }
        return line;
    }

    //Sends an item pointer
    void _send_Item(Item item)
    {
        byte[] bytes;
        if (item == null)
        {
            bytes = BitConverter.GetBytes(((UInt64)0));
        }
        else
        {
            bytes = BitConverter.GetBytes((UInt64)item.get_item());
        }
        if (bytes.Length != 8)
        {
            throw new RDKException("RoboDK API error");
        }
        Array.Reverse(bytes);
        _COM.Send(bytes);
    }

    //Receives an item pointer
    Item _recv_Item(Socket com = null)
    {
        if (com == null)
            com = _COM;

        byte[] buffer1 = new byte[8];
        byte[] buffer2 = new byte[4];
        int read1 = com.Receive(buffer1, 8, SocketFlags.None);
        int read2 = com.Receive(buffer2, 4, SocketFlags.None);
        if (read1 != 8 || read2 != 4)
        {
            return null;
        }
        Array.Reverse(buffer1);
        Array.Reverse(buffer2);
        UInt64 item = BitConverter.ToUInt64(buffer1, 0);
        //Console.WriteLine("Received item: " + item.ToString());
        Int32 type = BitConverter.ToInt32(buffer2, 0);
        return new Item(this, item, type);
    }
    //Sends an item pointer
    void _send_Ptr(UInt64 ptr = 0)
    {
        byte[] bytes = BitConverter.GetBytes(ptr);
        if (bytes.Length != 8)
        {
            throw new RDKException("RoboDK API error");
        }
        Array.Reverse(bytes);
        _COM.Send(bytes);
    }

    //Receives an item pointer
    UInt64 _recv_Ptr()
    {
        byte[] bytes = new byte[8];
        int read = _COM.Receive(bytes, 8, SocketFlags.None);
        if (read != 8)
        {
            return 0;
        }
        Array.Reverse(bytes);
        UInt64 ptr = BitConverter.ToUInt64(bytes, 0);
        return ptr;
    }

    void _send_Pose(Mat pose)
    {
        if (!pose.IsHomogeneous())
        {
            // warning!!
            return;
        }
        const int nvalues = 16;
        byte[] bytesarray = new byte[8 * nvalues];
        int cnt = 0;
        for (int j = 0; j < pose.cols; j++)
        {
            for (int i = 0; i < pose.rows; i++)
            {
                byte[] onedouble = BitConverter.GetBytes((double)pose[i, j]);
                Array.Reverse(onedouble);
                Array.Copy(onedouble, 0, bytesarray, cnt * 8, 8);
                cnt = cnt + 1;
            }
        }
        _COM.Send(bytesarray, 8 * nvalues, SocketFlags.None);
    }

    Mat _recv_Pose(Socket com = null)
    {
        if (com == null)
            com = _COM;

        Mat pose = new Mat(4, 4);
        byte[] bytes = new byte[16 * 8];
        int nbytes = com.Receive(bytes, 16 * 8, SocketFlags.None);
        if (nbytes != 16 * 8)
        {
            throw new RDKException("Invalid pose sent"); //raise Exception('Problems running function');
        }
        int cnt = 0;
        for (int j = 0; j < pose.cols; j++)
        {
            for (int i = 0; i < pose.rows; i++)
            {
                byte[] onedouble = new byte[8];
                Array.Copy(bytes, cnt, onedouble, 0, 8);
                Array.Reverse(onedouble);
                pose[i, j] = BitConverter.ToDouble(onedouble, 0);
                cnt = cnt + 8;
            }
        }
        return pose;
    }

    void _send_XYZ(double[] xyzpos)
    {
        for (int i = 0; i < 3; i++)
        {
            byte[] bytes = BitConverter.GetBytes((double)xyzpos[i]);
            Array.Reverse(bytes);
            _COM.Send(bytes, 8, SocketFlags.None);
        }
    }
    void _recv_XYZ(double[] xyzpos, Socket com = null)
    {
        if (com == null)
            com = _COM;

        byte[] bytes = new byte[3 * 8];
        int nbytes = com.Receive(bytes, 3 * 8, SocketFlags.None);
        if (nbytes != 3 * 8)
        {
            throw new RDKException("Invalid pose sent"); //raise Exception('Problems running function');
        }
        for (int i = 0; i < 3; i++)
        {
            byte[] onedouble = new byte[8];
            Array.Copy(bytes, i * 8, onedouble, 0, 8);
            Array.Reverse(onedouble);
            xyzpos[i] = BitConverter.ToDouble(onedouble, 0);
        }
    }

    void _send_Int(Int32 number, Socket com = null)
    {
        if (com == null)
            com = _COM;

        byte[] bytes = BitConverter.GetBytes(number);
        Array.Reverse(bytes); // convert from big endian to little endian
        com.Send(bytes);
    }

    Int32 _recv_Int(Socket com = null)
    {
        if (com == null)
            com = _COM;

        byte[] bytes = new byte[4];
        int read = com.Receive(bytes, 4, SocketFlags.None);
        if (read < 4)
        {
            return 0;
        }
        Array.Reverse(bytes); // convert from little endian to big endian
        return BitConverter.ToInt32(bytes, 0);
    }

    // Sends an array of doubles
    void _send_ArrayList(List<double> values)
    {
        if (values == null)
        {
            _send_Int(0);
            return;
        }
        double[] values2 = new double[values.Count];
        for (int i = 0; i < values.Count; i++)
        {
            values2[i] = values[i];
        }
        _send_Array(values2);
    }


    void _send_Array(double[] values)
    {
        if (values == null)
        {
            _send_Int(0);
            return;
        }
        int nvalues = values.Length;
        _send_Int(nvalues);
        byte[] bytesarray = new byte[8 * nvalues];
        for (int i = 0; i < nvalues; i++)
        {
            byte[] onedouble = BitConverter.GetBytes(values[i]);
            Array.Reverse(onedouble);
            Array.Copy(onedouble, 0, bytesarray, i * 8, 8);
        }
        _COM.Send(bytesarray, 8 * nvalues, SocketFlags.None);
    }

    // Receives an array of doubles
    double[] _recv_Array(Socket com = null)
    {
        if (com == null)
            com = _COM;

        int nvalues = _recv_Int(com);
        if (nvalues > 0)
        {
            double[] values = new double[nvalues];
            byte[] bytes = new byte[nvalues * 8];
            int read = com.Receive(bytes, nvalues * 8, SocketFlags.None);
            for (int i = 0; i < nvalues; i++)
            {
                byte[] onedouble = new byte[8];
                Array.Copy(bytes, i * 8, onedouble, 0, 8);
                Array.Reverse(onedouble);
                values[i] = BitConverter.ToDouble(onedouble, 0);
            }
            return values;
        }
        return null;
    }
    // Receives an array of doubles
    List<double> _recv_ArrayList()
    {
        double[] arraydbl = _recv_Array();
        List<double> listdbl = new List<double>();
        foreach (double dbl in arraydbl)
        {
            listdbl.Add(dbl);
        }
        return listdbl;
    }

    // sends a 2 dimensional matrix (old version, slow)
    /*
    void _send_Matrix2D(Mat mat)
    {
        _send_Int(mat.rows);
        _send_Int(mat.cols);
        for (int j = 0; j < mat.cols; j++)
        {
            for (int i = 0; i < mat.rows; i++)
            {
                byte[] bytes = BitConverter.GetBytes((double)mat[i, j]);
                Array.Reverse(bytes);
                _COM.Send(bytes, 8, SocketFlags.None);
            }
        }

    }*/
    void _send_Matrix2D(Mat mat)
    {
        var sendBuffer = new byte[mat.cols * mat.rows * sizeof(double)];
        _send_Int(mat.rows);
        _send_Int(mat.cols);
        var index = 0;
        for (var j = 0; j < mat.cols; j++)
        {
            for (var i = 0; i < mat.rows; i++)
            {
                var bytes = BitConverter.GetBytes(mat[i, j]);
                // Convert to big Endian.
                // Factor 2 performance gain compared to Array.Reverse(onedouble);
                sendBuffer[index++] = bytes[7];
                sendBuffer[index++] = bytes[6];
                sendBuffer[index++] = bytes[5];
                sendBuffer[index++] = bytes[4];
                sendBuffer[index++] = bytes[3];
                sendBuffer[index++] = bytes[2];
                sendBuffer[index++] = bytes[1];
                sendBuffer[index++] = bytes[0];
            }
        }

        _COM.Send(sendBuffer, sendBuffer.Length, SocketFlags.None);
    }

    // receives a 2 dimensional matrix (nxm)
    Mat _recv_Matrix2D()
    {
        int size1 = _recv_Int();
        int size2 = _recv_Int();
        int recvsize = size1 * size2 * 8;
        byte[] bytes = new byte[recvsize];
        Mat mat = new Mat(size1, size2);
        int BUFFER_SIZE = 256;
        int received = 0;
        if (recvsize > 0)
        {
            int to_receive = Math.Min(recvsize, BUFFER_SIZE);
            while (to_receive > 0)
            {
                int nbytesok = _COM.Receive(bytes, received, to_receive, SocketFlags.None);
                if (nbytesok <= 0)
                {
                    throw new RDKException("Can't receive matrix properly"); //raise Exception('Problems running function');
                }
                received = received + nbytesok;
                to_receive = Math.Min(recvsize - received, BUFFER_SIZE);
            }
        }
        int cnt = 0;
        for (int j = 0; j < mat.cols; j++)
        {
            for (int i = 0; i < mat.rows; i++)
            {
                byte[] onedouble = new byte[8];
                Array.Copy(bytes, cnt, onedouble, 0, 8);
                Array.Reverse(onedouble);
                mat[i, j] = BitConverter.ToDouble(onedouble, 0);
                cnt = cnt + 8;
            }
        }
        return mat;
    }

    // private move type, to be used by public methods (MoveJ  and MoveL)
    void moveX(Item target, double[] joints, Mat mat_target, Item itemrobot, int movetype, bool blocking = true)
    {
        itemrobot.WaitMove();
        _send_Line("MoveX");
        _send_Int(movetype);
        if (target != null)
        {
            _send_Int(3);
            _send_Array(null);
            _send_Item(target);
        }
        else if (joints != null)
        {
            _send_Int(1);
            _send_Array(joints);
            _send_Item(null);
        }
        else if (mat_target != null && mat_target.IsHomogeneous())
        {
            _send_Int(2);
            _send_Array(mat_target.ToDoubles());
            _send_Item(null);
        }
        else
        {
            throw new RDKException("Invalid target type"); //raise Exception('Problems running function');
        }
        _send_Item(itemrobot);
        _check_status();
        if (blocking)
        {
            itemrobot.WaitMove();
        }
    }
    // private move type, to be used by public methods (MoveJ  and MoveL)
    void moveC_private(Item target1, double[] joints1, Mat mat_target1, Item target2, double[] joints2, Mat mat_target2, Item itemrobot, bool blocking = true)
    {
        itemrobot.WaitMove();
        _send_Line("MoveC");
        _send_Int(3);
        if (target1 != null)
        {
            _send_Int(3);
            _send_Array(null);
            _send_Item(target1);
        }
        else if (joints1 != null)
        {
            _send_Int(1);
            _send_Array(joints1);
            _send_Item(null);
        }
        else if (mat_target1 != null && mat_target1.IsHomogeneous())
        {
            _send_Int(2);
            _send_Array(mat_target1.ToDoubles());
            _send_Item(null);
        }
        else
        {
            throw new RDKException("Invalid type of target 1");
        }
        /////////////////////////////////////
        if (target2 != null)
        {
            _send_Int(3);
            _send_Array(null);
            _send_Item(target2);
        }
        else if (joints2 != null)
        {
            _send_Int(1);
            _send_Array(joints2);
            _send_Item(null);
        }
        else if (mat_target2 != null && mat_target2.IsHomogeneous())
        {
            _send_Int(2);
            _send_Array(mat_target2.ToDoubles());
            _send_Item(null);
        }
        else
        {
            throw new RDKException("Invalid type of target 2");
        }
        /////////////////////////////////////
        _send_Item(itemrobot);
        _check_status();
        if (blocking)
        {
            itemrobot.WaitMove();
        }
    }

    //%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%   

    /// <summary>
    /// Return the list of recently opened files
    /// </summary>
    /// <param name="extension_filter"></param>
    /// <returns></returns>
    static public List<string> RecentFiles(string extension_filter = "")
    {
        string ini_file = System.Environment.GetFolderPath(System.Environment.SpecialFolder.ApplicationData) + "\\RoboDK\\RecentFiles.ini";
        string str = "";
        if (File.Exists(ini_file))
        {
            foreach (string line in File.ReadLines(ini_file))
            {
                if (line.Contains("RecentFileList="))
                {
                    str = line.Remove(0, "RecentFileList=".Length);
                    break;
                }
            }
        }
        List<string> rdk_list = new List<string>();
        string[] read_list = str.Split(',');
        foreach (string st in read_list)
        {
            string st2 = st.Trim();
            if (st2.Length < 5) // file name should be name.abc
            {
                continue;
            }
            if (extension_filter.Length == 0 || st2.ToLower().EndsWith(extension_filter.ToLower()))
            {
                rdk_list.Add(st2);
            }

        }
        return rdk_list;
    }



    /// <summary>
    /// Creates a link with RoboDK
    /// </summary>
    /// <param name="robodk_ip"></param>
    /// <param name="start_hidden"></param>
    /// <param name="com_port"></param>
    public RoboDK(string robodk_ip = "localhost", bool start_hidden = false, int com_port = -1, string args = "", string path = "")
    {
        //A connection is attempted upon creation of the object"""
        if (robodk_ip != "")
        {
            IP = robodk_ip;
        }
        START_HIDDEN = start_hidden;
        if (com_port > 0)
        {
            PORT_FORCED = com_port;
            PORT_START = com_port;
            PORT_END = com_port;
        }
        if (path != "")
        {
            APPLICATION_DIR = path;
        }
        if (args != "")
        {
            ARGUMENTS = args;
        }
        Connect();
    }

    /// <summary>
    /// Disconnect from the RoboDK API. This flushes any pending program generation.
    /// </summary>
    /// <returns></returns>
    public bool Disconnect()
    {
        window_handle = IntPtr.Zero;
        if (_COM != null && _COM.Connected)
        {
            _COM.Disconnect(false);
            //_COM.Close(1000);
            //_COM = null;
        }
        return true;
    }

    /// <summary>
    /// Disconnect from the RoboDK API. This flushes any pending program generation.
    /// </summary>
    /// <returns></returns>
    /// 
    public bool Finish()
    {
        window_handle = IntPtr.Zero;
        return Disconnect();
    }

    /// <summary>
    /// Make sure we are connected to RoboDK
    /// </summary>
    /// <returns></returns>
    private bool verify_connection()
    {
        bool use_new_version = false;

        if (use_new_version)
        {
            _send_Line("RDK_API");
            _send_Int(0);
            string response = _recv_Line();
            int ver_api = _recv_Int();
            BUILD = _recv_Int();
            _check_status();
            return response == "RDK_API";
        }
        else
        {
            _send_Line("CMD_START");
            _send_Line(Convert.ToString(SAFE_MODE) + " " + Convert.ToString(AUTO_UPDATE));
            string response = _recv_Line();
            if (response == "READY")
            {
                return true;
            }
            return false;
        }

    }
    /// <summary>
    /// Check if the build of RoboDK is equal or greater than the build of the API call
    /// </summary>
    /// <returns></returns>
    private bool _require_build(int build_required)
    {
        if (BUILD == 0)
            return true;

        if (BUILD < build_required)
            throw new RDKException("This function is unavailable. Update RoboDK to use this function through the API");

        return true;
    }

    /// <summary>
    /// Starts the link with RoboDK (automatic upon creation of the object)
    /// </summary>
    /// <returns></returns>
    public bool Connect()
    {
        //Establishes a connection with robodk. robodk must be running, otherwise, the variable APPLICATION_DIR must be set properly.
        bool connected = false;
        int port;
        for (int i = 0; i < 2; i++)
        {
            for (port = PORT_START; port <= PORT_END; port++)
            {
                _COM = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.IP);
                //_COM = new Socket(SocketType.Stream, ProtocolType.IPv4);
                _COM.SendTimeout = 1000;
                _COM.ReceiveTimeout = 1000;
                try
                {
                    _COM.Connect(IP, port);
                    connected = is_connected();
                    if (connected)
                    {
                        _COM.SendTimeout = _TIMEOUT;
                        _COM.ReceiveTimeout = _TIMEOUT;
                        break;
                    }
                }
                catch //Exception e)
                {
                    //connected = false;
                }
            }
            if (connected)
            {
                PORT = port;
                break;
            }
            else
            {
                if (IP != "localhost")
                {
                    break;
                }
                string arguments = "";
                if (PORT_FORCED > 0)
                {
                    PORT_START = PORT_FORCED;
                    arguments = arguments + "/PORT=" + PORT_FORCED.ToString() + " ";
                }
                if (START_HIDDEN)
                {
                    arguments = arguments + "/NOSPLASH /NOSHOW /HIDDEN ";
                }
                if (ARGUMENTS != "")
                {
                    arguments = arguments + ARGUMENTS;
                }
                if (APPLICATION_DIR == "")
                {

                    string install_path = null;

                    // retrieve install path from the registry:
                    RegistryKey localKey = RegistryKey.OpenBaseKey(Microsoft.Win32.RegistryHive.LocalMachine, RegistryView.Registry64);
                    localKey = localKey.OpenSubKey(@"SOFTWARE\RoboDK");
                    if (localKey != null)
                    {
                        install_path = localKey.GetValue("INSTDIR").ToString();
                        if (install_path != null)
                        {
                            APPLICATION_DIR = install_path + "\\bin\\RoboDK.exe";
                        }
                    }
                    /*
                    // .Net 2.0
                    RegistryKey regKey = Registry.LocalMachine.OpenSubKey(@"SOFTWARE\RoboDK", false);
                    if (regKey is RegistryKey) // check if the registry was opened
                    {
                        install_path = regKey.GetValue("INSTDIR").ToString();
                        regKey.Close();
                        if (install_path != null)
                        {
                            APPLICATION_DIR = install_path + "\\bin\\RoboDK.exe";
                        }
                    }*/
                }
                if (APPLICATION_DIR == "")
                {
                    APPLICATION_DIR = "C:/RoboDK/bin/RoboDK.exe";
                }

                //PROCESS = System.Diagnostics.Process.Start(APPLICATION_DIR, arguments);
                //connected = WaitForTcpServerPort(PORT_START, 10000);
                //PROCESS.WaitForInputIdle(); // only works if RoboDK is displayed
                //ARGUMENTS = ARGUMENTS + " -platform windows:dpiawareness=2";
                var processStartInfo = new ProcessStartInfo
                {
                    FileName = APPLICATION_DIR,
                    Arguments = arguments,
                    RedirectStandardOutput = true,
                    UseShellExecute = false
                };
                //processStartInfo.Environment["variable"] = "content";
                PROCESS = System.Diagnostics.Process.Start(processStartInfo);
                // wait for the process to get started

                // wait for RoboDK to output (stdout) RoboDK is Running. Works after v3.4.0. Warning! This poses some issues when reading STEP files. 
                // They generate a lot of STDOUT and the buffer may have to be emptied.
                string line = "";
                while (line != null && !line.Contains("RoboDK is Running"))
                {
                    line = PROCESS.StandardOutput.ReadLine();
                }
                if (line == null)
                {
                    connected = false;
                }
                PROCESS.StandardOutput.Close();
            }
        }
        if (connected && !verify_connection())
        {
            connected = false;
            PROCESS = null;
        }
        return connected;
    }

    /// <summary>
    /// Get RoboDK main window handle
    /// </summary>
    /// <returns></returns>
    public IntPtr GetWindowHandle()
    {
        if (window_handle != IntPtr.Zero)
        {
            return window_handle;
        }
        // Retrieve the wain window handle
        if (PROCESS != null)
        {
            window_handle = PROCESS.MainWindowHandle;
            return window_handle;
        }
        else
        {
            _require_build(7750);
            // RoboDK was not started from this application.
            // In that case, we can retrieve the window pointer by using a specific RoboDK command
            string str_window_id = Command("MainWindow_ID");
            window_handle = new IntPtr(Convert.ToInt32(str_window_id));
            return window_handle;
        }
    }


    /// <summary>
    /// Check if RoboDK was installed from RoboDK's official installer
    /// </summary>
    /// <returns></returns>
    public static bool RoboDKInstallFound()
    {
        return RoboDKInstallPath() != null;
    }

    /// <summary>
    /// Return the RoboDK install path according to the registry (saved by RoboDK installer)
    /// </summary>
    /// <returns></returns>
    public static string RoboDKInstallPath()
    {
        // retrieve install path from the registry:
        RegistryKey localKey = RegistryKey.OpenBaseKey(Microsoft.Win32.RegistryHive.LocalMachine, RegistryView.Registry64);
        localKey = localKey.OpenSubKey(@"SOFTWARE\RoboDK");
        if (localKey != null)
        {
            string install_path = localKey.GetValue("INSTDIR").ToString();
            if (install_path != null)
            {
                return install_path + "\\bin\\RoboDK.exe";
            }
        }
        /*
        // .Net 2.0
        RegistryKey regKey = Registry.LocalMachine.OpenSubKey(@"SOFTWARE\RoboDK", false);
        if (regKey is RegistryKey) // check if the registry was opened
        {
            install_path = regKey.GetValue("INSTDIR").ToString();
            regKey.Close();
            if (install_path != null)
            {
                return = install_path + "\\bin\\RoboDK.exe";
            }
        }*/
        return null;
    }

    private static bool WaitForTcpServerPort(int serverPort, int millisecondsTimeout)
    {
        int sleepTime = 100;
        bool serverPortIsOpen = false;
        while ((serverPortIsOpen == false) && (millisecondsTimeout > 0))
        {
            //TcpConnectionInformation[] tcpConnInfoArray = IPGlobalProperties.GetIPGlobalProperties().GetActiveTcpConnections();
            IPEndPoint[] objEndPoints = System.Net.NetworkInformation.IPGlobalProperties.GetIPGlobalProperties().GetActiveTcpListeners();
            foreach (var tcpEndPoint in objEndPoints)
            {
                if (tcpEndPoint.Port == serverPort)
                {
                    serverPortIsOpen = true;
                    break;
                }
            }
            if (serverPortIsOpen == false)
            {
                Thread.Sleep(sleepTime);
                millisecondsTimeout -= sleepTime;
            }
        }
        return serverPortIsOpen;
    }

    /// <summary>
    /// Start the event communication channel. Use WaitForEvent to wait for a new event or use EventsLoop as an example to implement an event loop.
    /// </summary>
    /// <returns></returns>
    public bool EventsListen()
    {
        _COM_EVT = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.IP);
        _COM_EVT.SendTimeout = 1000;
        _COM_EVT.ReceiveTimeout = 1000;
        try
        {
            _COM_EVT.Connect(IP, PORT);
            if (_COM_EVT.Connected)
            {
                _COM_EVT.SendTimeout = _TIMEOUT;
                _COM_EVT.ReceiveTimeout = _TIMEOUT;
            }
        }
        catch //Exception e)
        {
            return false;
        }
        _send_Line("RDK_EVT", _COM_EVT);
        _send_Int(0, _COM_EVT);
        string response = _recv_Line(_COM_EVT);
        int ver_evt = _recv_Int(_COM_EVT);
        int status = _recv_Int(_COM_EVT);
        if (response != "RDK_EVT" || status != 0)
        {
            return false;
        }
        _COM_EVT.ReceiveTimeout = 3600 * 1000;
        //return EventsLoop();
        return true;
    }

    /// <summary>
    /// Wait for a new RoboDK event. This function blocks until a new RoboDK event occurs.
    /// </summary>
    /// <param name="evt">Event ID</param>
    /// <param name="itm">Item that provoked the event (Invalid item if not applicable)</param>
    /// <returns></returns>
    public bool WaitForEvent(out int evt, out Item itm)
    {
        evt = _recv_Int(_COM_EVT);
        itm = _recv_Item(_COM_EVT);
        return true;
    }

    /// <summary>
    /// This is a sample function that is executed when a new RoboDK Event occurs.
    /// </summary>
    /// <param name="evt"></param>
    /// <param name="itm"></param>
    /// <returns></returns>
    public bool SampleRoboDkEvent(int evt, Item itm)
    {
        switch (evt)
        {
            case EVENT_SELECTION_TREE_CHANGED:
                Console.WriteLine("Event: Selection changed (the tree was selected)");
                break;
            case EVENT_SELECTION_3D_CHANGED:
                Console.WriteLine("Event: Selection changed (the 3D screen was selected)");
                break;
            case EVENT_ITEM_MOVED:
                Console.WriteLine("Event: Item Moved");
                break;
            case EVENT_REFERENCE_PICKED:
                Console.WriteLine("Event: Reference Picked");
                break;
            case EVENT_REFERENCE_RELEASED:
                Console.WriteLine("Event: Reference Released");
                break;
            case EVENT_TOOL_MODIFIED:
                Console.WriteLine("Event: Tool Modified");
                break;
            default:
                Console.WriteLine("Unknown event " + evt.ToString());
                break;
        }
        if (itm.Valid())
            Console.WriteLine("  -> " + itm.Name() + " type: " + itm.Type().ToString());
        else
            Console.WriteLine("  Unknown item");

        return true;
    }

    /// <summary>
    /// Run the RoboDK event loop. This is loop blocks until RoboDK finishes execution. Run this loop as a separate thread or create a similar loop to customize the event loop behavior.
    /// </summary>
    /// <returns></returns>
    public bool EventsLoop()
    {
        Console.WriteLine("Events loop started");
        while (_COM_EVT.Connected)
        {
            int evt;
            Item itm;
            WaitForEvent(out evt, out itm);
            if (evt == EVENT_SELECTION_3D_CHANGED)
            {
                double[] data = _recv_Array(_COM_EVT);
                Mat pose_abs = new Mat(data, true);
                double[] xyz = new double[] { data[16], data[17], data[18] };
                double[] ijk = new double[] { data[19], data[20], data[21] };
                int feature_type = Convert.ToInt32(data[22]);
                int feature_id = Convert.ToInt32(data[23]);

                Console.WriteLine("Additional event data - Absolute position (PoseAbs):");
                Console.WriteLine(pose_abs.ToString());
                Console.WriteLine("Additional event data - Point and Normal (point selected in relative coordinates)");
                Console.WriteLine(xyz[0].ToString() + "," + xyz[1].ToString() + "," + xyz[2].ToString());
                Console.WriteLine(ijk[0].ToString() + "," + ijk[1].ToString() + "," + ijk[2].ToString());
                Console.WriteLine("Feature Type and ID");
                Console.WriteLine(feature_type.ToString() + "-" + feature_id.ToString());
            }
            else
            {
                // no additional data is sent
            }
            SampleRoboDkEvent(evt, itm);
        }
        Console.WriteLine("Event loop finished");
        return true;
    }


    // %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    // public methods
    /// <summary>
    /// Returns an item by its name. If there is no exact match it will return the last closest match.
    /// </summary>
    /// <param name="name">Item name</param>
    /// <param name="type">Filter by item type RoboDK.ITEM_TYPE_...</param>
    /// <returns></returns>
    public Item getItem(string name, int itemtype = -1)
    {
        _check_connection();
        string command;
        if (itemtype < 0)
        {
            command = "G_Item";
            _send_Line(command);
            _send_Line(name);
        }
        else
        {
            command = "G_Item2";
            _send_Line(command);
            _send_Line(name);
            _send_Int(itemtype);
        }
        Item item = _recv_Item();
        _check_status();
        return item;
    }

    /// <summary>
    /// Returns a list of items (list of name or pointers) of all available items in the currently open station in robodk.
    /// Optionally, use a filter to return specific items (example: getItemListNames(filter = ITEM_CASE_ROBOT))
    /// </summary>
    /// <param name="filter">ITEM_TYPE</param>
    /// <returns></returns>
    public string[] getItemListNames(int filter = -1)
    {
        _check_connection();
        string command;
        if (filter < 0)
        {
            command = "G_List_Items";
            _send_Line(command);
        }
        else
        {
            command = "G_List_Items_Type";
            _send_Line(command);
            _send_Int(filter);
        }
        int numitems = _recv_Int();
        string[] listnames = new string[numitems];
        for (int i = 0; i < numitems; i++)
        {
            listnames[i] = _recv_Line();
        }
        _check_status();
        return listnames;
    }

    /// <summary>
    /// Returns a list of items (list of name or pointers) of all available items in the currently open station in robodk.
    /// Optionally, use a filter to return specific items (example: getItemListNames(filter = ITEM_CASE_ROBOT))
    /// </summary>
    /// <param name="filter">ITEM_TYPE</param>
    /// <returns></returns>
    public Item[] getItemList(int filter = -1)
    {
        _check_connection();
        string command;
        if (filter < 0)
        {
            command = "G_List_Items_ptr";
            _send_Line(command);
        }
        else
        {
            command = "G_List_Items_Type_ptr";
            _send_Line(command);
            _send_Int(filter);
        }
        int numitems = _recv_Int();
        Item[] listitems = new Item[numitems];
        for (int i = 0; i < numitems; i++)
        {
            listitems[i] = _recv_Item();
        }
        _check_status();
        return listitems;
    }

    /////// add more methods

    /// <summary>
    /// Shows a RoboDK popup to select one object from the open station.
    /// An item type can be specified to filter desired items. If no type is specified, all items are selectable.
    /// </summary>
    /// <param name="message">Message to pop up</param>
    /// <param name="itemtype">optionally filter by RoboDK.ITEM_TYPE_*</param>
    /// <returns></returns>
    public Item ItemUserPick(string message = "Pick one item", int itemtype = -1)
    {
        _check_connection();
        _send_Line("PickItem");
        _send_Line(message);
        _send_Int(itemtype);
        _COM.ReceiveTimeout = 3600 * 1000;
        Item item = _recv_Item();
        _COM.ReceiveTimeout = _TIMEOUT;
        _check_status();
        return item;
    }

    /// <summary>
    /// Shows or raises the RoboDK window
    /// </summary>
    public void ShowRoboDK()
    {
        _check_connection();
        _send_Line("RAISE");
        _check_status();
    }

    /// <summary>
    /// Fit all
    /// </summary>
    public void FitAll()
    {
        _check_connection();
        _send_Line("FitAll");
        _check_status();
    }

    /// <summary>
    /// Hides the RoboDK window
    /// </summary>
    public void HideRoboDK()
    {
        _check_connection();
        _send_Line("HIDE");
        _check_status();
    }

    /// <summary>
    /// Closes RoboDK window and finishes RoboDK execution
    /// </summary>
    public void CloseRoboDK()
    {
        _check_connection();
        _send_Line("QUIT");
        _check_status();
        _COM.Disconnect(false);
        PROCESS = null;
    }
    /// <summary>
    /// Return the vesion of RoboDK as a 4 digit string: Major.Minor.Revision.Build
    /// </summary>
    public string Version()
    {
        _check_connection();
        _send_Line("Version");
        string app_name = _recv_Line();
        int bit_arch = _recv_Int();
        string ver4 = _recv_Line();
        string date_build = _recv_Line();
        _check_status();
        return ver4;
    }

    /// <summary>
    /// Set the state of the RoboDK window
    /// </summary>
    /// <param name="windowstate"></param>
    public void setWindowState(int windowstate = WINDOWSTATE_NORMAL)
    {
        _check_connection();
        _send_Line("S_WindowState");
        _send_Int(windowstate);
        _check_status();
    }


    /// <summary>
    /// Update the RoboDK flags. RoboDK flags allow defining how much access the user has to RoboDK features. Use FLAG_ROBODK_* variables to set one or more flags.
    /// </summary>
    /// <param name="flags">state of the window(FLAG_ROBODK_*)</param>
    public void setFlagsRoboDK(int flags = FLAG_ROBODK_ALL)
    {
        _check_connection();
        _send_Line("S_RoboDK_Rights");
        _send_Int(flags);
        _check_status();
    }

    /// <summary>
    /// Update item flags. Item flags allow defining how much access the user has to item-specific features. Use FLAG_ITEM_* flags to set one or more flags.
    /// </summary>
    /// <param name="item"></param>
    /// <param name="flags"></param>
    public void setFlagsItem(Item item, int flags = FLAG_ITEM_ALL)
    {
        _check_connection();
        _send_Line("S_Item_Rights");
        _send_Item(item);
        _send_Int(flags);
        _check_status();
    }

    /// <summary>
    /// Retrieve current item flags. Item flags allow defining how much access the user has to item-specific features. Use FLAG_ITEM_* flags to set one or more flags.
    /// </summary>
    /// <param name="item"></param>
    /// <returns></returns>
    public int getFlagsItem(Item item)
    {
        _check_connection();
        _send_Line("S_Item_Rights");
        _send_Item(item);
        int flags = _recv_Int();
        _check_status();
        return flags;
    }

    /// <summary>
    /// Show a message in RoboDK (it can be blocking or non blocking in the status bar)
    /// </summary>
    /// <param name="message">Message to display</param>
    /// <param name="popup">Set to true to make the message blocking or set to false to make it non blocking</param>
    public void ShowMessage(string message, bool popup = true)
    {
        _check_connection();
        if (popup)
        {
            _send_Line("ShowMessage");
            _send_Line(message);
            _COM.ReceiveTimeout = 3600 * 1000;
            _check_status();
            _COM.ReceiveTimeout = _TIMEOUT;
        }
        else
        {
            _send_Line("ShowMessageStatus");
            _send_Line(message);
            _check_status();
        }

    }

    /////////////// Add More methods

    /// <summary>
    /// Loads a file and attaches it to parent. It can be any file supported by robodk.
    /// </summary>
    /// <param name="filename">absolute path of the file</param>
    /// <param name="parent">parent to attach. Leave empty for new stations or to load an object at the station root</param>
    /// <returns>Newly added object. Check with item.Valid() for a successful load</returns>
    public Item AddFile(string filename, Item parent = null)
    {
        _check_connection();
        _send_Line("Add");
        _send_Line(filename);
        _send_Item(parent);
        _COM.ReceiveTimeout = 3600 * 1000;
        Item newitem = _recv_Item();
        _COM.ReceiveTimeout = _TIMEOUT;
        _check_status();
        return newitem;
    }

    /////////////// Add More methods

    /// <summary>
    /// Save an item to a file. If no item is provided, the open station is saved.
    /// </summary>
    /// <param name="filename">absolute path to save the file</param>
    /// <param name="itemsave">object or station to save. Leave empty to automatically save the current station.</param>
    public void Save(string filename, Item itemsave = null)
    {
        _check_connection();
        _send_Line("Save");
        _send_Line(filename);
        _send_Item(itemsave);
        _check_status();
    }

    /// <summary>
    /// Add a new empty station. It returns the station created.
    /// </summary>
    /// <param name="name"></param>
    public Item AddStation(string name = "New Station")
    {
        _check_connection();
        _send_Line("NewStation");
        _send_Line(name);
        Item newitem = _recv_Item();
        _check_status();
        return newitem;
    }

    /// <summary>
    /// Adds a shape provided triangle coordinates. Triangles must be provided as a list of vertices. A vertex normal can be provided optionally.
    /// </summary>
    /// <param name="triangle_points">List of vertices grouped by triangles (3xN or 6xN matrix, N must be multiple of 3 because vertices must be stacked by groups of 3)</param>
    /// <param name="add_to">item to attach the newly added geometry (optional). Leave empty to create a new object.</param>
    /// <param name="shape_override">Set to true to replace any other existing geometry</param>
    /// <param name="color">Optionally specify the color as RGBA [0-1]</param>
    /// <returns></returns>
    public Item AddShape(Mat triangle_points, Item add_to = null, bool shape_override = false, List<double> color = null)
    {
        _require_build(5449);
        _check_connection();
        _send_Line("AddShape3");
        _send_Matrix2D(triangle_points);
        _send_Item(add_to);
        _send_Int(shape_override ? 1 : 0);
        _send_ArrayList(color);
        _COM.ReceiveTimeout = 3600 * 1000;
        Item newitem = _recv_Item();
        _COM.ReceiveTimeout = _TIMEOUT;
        _check_status();
        return newitem;
    }


    /// <summary>
    /// Adds a curve provided point coordinates. The provided points must be a list of vertices. A vertex normal can be provided optionally.
    /// </summary>
    /// <param name="curve_points">matrix 3xN or 6xN -> N must be multiple of 3</param>
    /// <param name="reference_object">object to add the curve and/or project the curve to the surface</param>
    /// <param name="add_to_ref">If True, the curve will be added as part of the object in the RoboDK item tree (a reference object must be provided)</param>
    /// <param name="projection_type">Type of projection. For example: PROJECTION_ALONG_NORMAL_RECALC will project along the point normal and recalculate the normal vector on the surface projected.</param>
    /// <returns>added object/curve (null if failed)</returns>
    public Item AddCurve(Mat curve_points, Item reference_object = null, bool add_to_ref = false, int projection_type = PROJECTION_ALONG_NORMAL_RECALC)
    {
        _check_connection();
        _send_Line("AddWire");
        _send_Matrix2D(curve_points);
        _send_Item(reference_object);
        _send_Int(add_to_ref ? 1 : 0);
        _send_Int(projection_type);
        _COM.ReceiveTimeout = 3600 * 1000;
        Item newitem = _recv_Item();
        _COM.ReceiveTimeout = _TIMEOUT;
        _check_status();
        return newitem;
    }

    /// <summary>
    /// Adds a list of points to an object. The provided points must be a list of vertices. A vertex normal can be provided optionally.
    /// </summary>
    /// <param name="points">list of points as a matrix (3xN matrix, or 6xN to provide point normals as ijk vectors)</param>
    /// <param name="reference_object">item to attach the newly added geometry (optional)</param>
    /// <param name="add_to_ref">If True, the points will be added as part of the object in the RoboDK item tree (a reference object must be provided)</param>
    /// <param name="projection_type">Type of projection.Use the PROJECTION_* flags.</param>
    /// <returns>added object/shape (0 if failed)</returns>
    public Item AddPoints(Mat points, Item reference_object = null, bool add_to_ref = false, int projection_type = PROJECTION_ALONG_NORMAL_RECALC)
    {
        _check_connection();
        _send_Line("AddPoints");
        _send_Matrix2D(points);
        _send_Item(reference_object);
        _send_Int(add_to_ref ? 1 : 0);
        _send_Int(projection_type);
        _COM.ReceiveTimeout = 3600 * 1000;
        Item newitem = _recv_Item();
        _COM.ReceiveTimeout = _TIMEOUT;
        _check_status();
        return newitem;
    }

    /// <summary>
    /// Projects a point given its coordinates. The provided points must be a list of [XYZ] coordinates. Optionally, a vertex normal can be provided [XYZijk].
    /// </summary>
    /// <param name="points">matrix 3xN or 6xN -> list of points to project</param>
    /// <param name="object_project">object to project</param>
    /// <param name="projection_type">Type of projection. For example: PROJECTION_ALONG_NORMAL_RECALC will project along the point normal and recalculate the normal vector on the surface projected.</param>
    /// <returns></returns>
    public Mat ProjectPoints(Mat points, Item object_project, int projection_type = PROJECTION_ALONG_NORMAL_RECALC)
    {
        _check_connection();
        _send_Line("ProjectPoints");
        _send_Matrix2D(points);
        _send_Item(object_project);
        _send_Int(projection_type);
        _COM.ReceiveTimeout = 3600 * 1000;
        Mat projected_points = _recv_Matrix2D();
        _COM.ReceiveTimeout = _TIMEOUT;
        _check_status();
        return projected_points;
    }

    /// <summary>
    /// Closes the current station without suggesting to save
    /// </summary>
    public void CloseStation()
    {
        _check_connection();
        _send_Line("Remove");
        _send_Item(new Item(this));
        _check_status();
    }

    /// <summary>
    /// Adds a new target that can be reached with a robot.
    /// </summary>
    /// <param name="name">name of the target</param>
    /// <param name="itemparent">parent to attach to (such as a frame)</param>
    /// <param name="itemrobot">main robot that will be used to go to self target</param>
    /// <returns>the new target created</returns>
    public Item AddTarget(string name, Item itemparent = null, Item itemrobot = null)
    {
        _check_connection();
        _send_Line("Add_TARGET");
        _send_Line(name);
        _send_Item(itemparent);
        _send_Item(itemrobot);
        Item newitem = _recv_Item();
        _check_status();
        return newitem;
    }

    /// <summary>
    /// Adds a new Frame that can be referenced by a robot.
    /// </summary>
    /// <param name="name">name of the reference frame</param>
    /// <param name="itemparent">parent to attach to (such as the robot base frame)</param>
    /// <returns>the new reference frame created</returns>
    public Item AddFrame(string name, Item itemparent = null)
    {
        _check_connection();
        _send_Line("Add_FRAME");
        _send_Line(name);
        _send_Item(itemparent);
        Item newitem = _recv_Item();
        _check_status();
        return newitem;
    }

    /// <summary>
    /// Adds a new Frame that can be referenced by a robot.
    /// </summary>
    /// <param name="name">name of the program</param>
    /// <param name="itemparent">robot that will be used</param>
    /// <returns>the new program created</returns>
    public Item AddProgram(string name, Item itemrobot = null)
    {
        _check_connection();
        _send_Line("Add_PROG");
        _send_Line(name);
        _send_Item(itemrobot);
        Item newitem = _recv_Item();
        _check_status();
        return newitem;
    }

    /// <summary>
    /// Add a new robot machining project. Machining projects can also be used for 3D printing, following curves and following points. 
    /// It returns the newly created :class:`.Item` containing the project settings.
    /// Tip: Use the macro /RoboDK/Library/Macros/MoveRobotThroughLine.py to see an example that creates a new "curve follow project" given a list of points to follow(Option 4).
    /// </summary>
    /// <param name="name">Name of the project settings</param>
    /// <param name="itemrobot">Robot to use for the project settings(optional). It is not required to specify the robot if only one robot or mechanism is available in the RoboDK station.</param>
    /// <returns></returns>
    public Item AddMachiningProject(string name = "Curve follow settings", Item itemrobot = null)
    {
        _check_connection();
        _send_Line("Add_MACHINING");
        _send_Line(name);
        _send_Item(itemrobot);
        Item newitem = _recv_Item();
        _check_status();
        return newitem;
    }


    //%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    /// <summary>
    /// Adds a function call in the program output. RoboDK will handle the syntax when the code is generated for a specific robot. If the program exists it will also run the program in simulate mode.
    /// </summary>
    /// <param name="function_w_params">Function name with parameters (if any)</param>
    /// <returns></returns>
    public int RunProgram(string function_w_params)
    {
        return RunCode(function_w_params, true);
    }

    /// <summary>
    /// Adds code to run in the program output. If the program exists it will also run the program in simulate mode.
    /// </summary>
    /// <param name="code"></param>
    /// <param name="code_is_fcn_call"></param>
    /// <returns></returns>
    public int RunCode(string code, bool code_is_fcn_call = false)
    {
        _check_connection();
        _send_Line("RunCode");
        _send_Int(code_is_fcn_call ? 1 : 0);
        _send_Line(code);
        int prog_status = _recv_Int();
        _check_status();
        return prog_status;
    }

    /// <summary>
    /// Shows a message or a comment in the output robot program.
    /// </summary>
    /// <param name="message"></param>
    /// <param name="message_is_comment"></param>
    public void RunMessage(string message, bool message_is_comment = false)
    {
        _check_connection();
        _send_Line("RunMessage");
        _send_Int(message_is_comment ? 1 : 0);
        _send_Line(message);
        _check_status();
    }

    /// <summary>
    /// Renders the scene. This function turns off rendering unless always_render is set to true.
    /// </summary>
    /// <param name="always_render"></param>
    public void Render(bool always_render = false)
    {
        bool auto_render = !always_render;
        _check_connection();
        _send_Line("Render");
        _send_Int(auto_render ? 1 : 0);
        _check_status();
    }

    /// <summary>
    /// Update the screen. 
    /// This updates the position of all robots and internal links according to previously set values.
    /// </summary>
    public void Update()
    {
        _check_connection();
        _send_Line("Refresh");
        _send_Int(0);
        _check_status();
    }

    /// <summary>
    /// Returns (1/True) if object_inside is inside the object_parent
    /// </summary>
    /// <param name="object_inside"></param>
    /// <param name="object_parent"></param>
    /// <returns></returns>
    public bool IsInside(Item object_inside, Item object_parent)
    {
        _check_connection();
        _send_Line("IsInside");
        _send_Item(object_inside);
        _send_Item(object_parent);
        int inside = _recv_Int();
        _check_status();
        return inside > 0;
    }

    /// <summary>
    /// Set collision checking ON or OFF (COLLISION_OFF/COLLISION_OFF) according to the collision map. If collision check is activated it returns the number of pairs of objects that are currently in a collision state.
    /// </summary>
    /// <param name="check_state"></param>
    /// <returns>Number of pairs of objects in a collision state</returns>
    public int setCollisionActive(int check_state = COLLISION_ON)
    {
        _check_connection();
        _send_Line("Collision_SetState");
        _send_Int(check_state);
        int ncollisions = _recv_Int();
        _check_status();
        return ncollisions;
    }

    /// <summary>
    /// Set collision checking ON or OFF (COLLISION_ON/COLLISION_OFF) for a specific pair of objects. This allows altering the collision map for Collision checking. 
    /// Specify the link id for robots or moving mechanisms (id 0 is the base).
    /// </summary>
    /// <param name="check_state">Set to COLLISION_ON or COLLISION_OFF</param>
    /// <param name="item1">Item 1</param>
    /// <param name="item2">Item 2</param>
    /// <param name="id1">Joint id for Item 1 (if Item 1 is a robot or a mechanism)</param>
    /// <param name="id2">Joint id for Item 2 (if Item 2 is a robot or a mechanism)</param>
    /// <returns>Returns true if succeeded. Returns false if setting the pair failed (wrong id was provided)</returns>
    public bool setCollisionActivePair(int check_state, Item item1, Item item2, int id1 = 0, int id2 = 0)
    {
        _check_connection();
        _send_Line("Collision_SetPair");
        _send_Item(item1);
        _send_Item(item2);
        _send_Int(id1);
        _send_Int(id2);
        _send_Int(check_state);
        int success = _recv_Int();
        _check_status();
        return success > 0;
    }

    /// <summary>
    /// Set collision checking ON or OFF (COLLISION_ON/COLLISION_OFF) for a specific list of pairs of objects. This allows altering the collision map for Collision checking. 
    /// Specify the link id for robots or moving mechanisms (id 0 is the base).
    /// </summary>
    /// <param name="check_state">Set to COLLISION_ON or COLLISION_OFF</param>
    /// <param name="item1">Item 1</param>
    /// <param name="item2">Item 2</param>
    /// <param name="id1">Joint id for Item 1 (if Item 1 is a robot or a mechanism)</param>
    /// <param name="id2">Joint id for Item 2 (if Item 2 is a robot or a mechanism)</param>
    /// <returns>Returns true if succeeded. Returns false if setting the pair failed (wrong id was provided)</returns>
    public bool setCollisionActivePair(List<int> check_state, List<Item> item1, List<Item> item2, List<int> id1 = null, List<int> id2 = null)
    {
        int npairs = Math.Min(check_state.Count, Math.Min(item1.Count, item2.Count));
        _check_connection();
        _send_Line("Collision_SetPairList");
        _send_Int(npairs);
        for (int i = 0; i < npairs; i++)
        {
            _send_Item(item1[i]);
            _send_Item(item2[i]);
            int idok1 = 0;
            int idok2 = 0;
            if (id1 != null && id1.Count > i)
            {
                idok1 = id1[i];
            }
            if (id2 != null && id2.Count > i)
            {
                idok2 = id2[i];
            }
            _send_Int(idok1);
            _send_Int(idok2);
            _send_Int(check_state[i]);
        }
        int nok = _recv_Int();
        _check_status();
        return nok == npairs;
    }

    /// <summary>
    /// Returns the number of pairs of objects that are currently in a collision state.
    /// </summary>
    /// <returns></returns>
    public int Collisions()
    {
        _check_connection();
        _send_Line("Collisions");
        int ncollisions = _recv_Int();
        _check_status();
        return ncollisions;
    }

    /// <summary>
    /// Returns 1 if item1 and item2 collided. Otherwise returns 0.
    /// </summary>
    /// <param name="item1"></param>
    /// <param name="item2"></param>
    /// <returns></returns>
    public int Collision(Item item1, Item item2, bool use_collision_map = true)
    {
        _require_build(5449);
        _check_connection();
        _send_Line("Collided3");
        _send_Item(item1);
        _send_Item(item2);
        _send_Int(use_collision_map ? 1 : 0);
        int ncollisions = _recv_Int();
        _check_status();
        return ncollisions;
    }

    /// <summary>
    /// Return the list of items that are in a collision state. This function can be used after calling Collisions() to retrieve the items that are in a collision state.
    /// </summary>
    /// <param name="link_id_list">List of robot link IDs that are in collision (0 for objects and tools)</param>
    /// <returns>List of items that are in a collision state</returns>
    public List<Item> CollisionItems(List<int> link_id_list = null)
    {
        _check_connection();
        _send_Line("Collision_Items");
        int nitems = _recv_Int();
        List<Item> item_list = new List<Item>();
        if (link_id_list != null)
        {
            link_id_list.Clear();
        }
        for (int i = 0; i < nitems; i++)
        {
            item_list.Add(_recv_Item());
            int link_id = _recv_Int();//link id for robot items (ignored)
            if (link_id_list != null)
            {
                link_id_list.Add(link_id);
            }
            int collision_times = _recv_Int();//number of objects it is in collisions with
        }
        _check_status();
        return item_list;
    }


    /// <summary>
    /// Sets the current simulation speed. Set the speed to 1 for a real-time simulation. The slowest speed allowed is 0.001 times the real speed. Set to a high value (>100) for fast simulation results.
    /// </summary>
    /// <param name="speed"></param>
    public void setSimulationSpeed(double speed)
    {
        _check_connection();
        _send_Line("SimulateSpeed");
        _send_Int((int)(speed * 1000.0));
        _check_status();
    }

    /// <summary>
    /// Gets the current simulation speed. Set the speed to 1 for a real-time simulation.
    /// </summary>
    /// <returns></returns>
    public double SimulationSpeed()
    {
        _check_connection();
        _send_Line("GetSimulateSpeed");
        double speed = ((double)_recv_Int()) / 1000.0;
        _check_status();
        return speed;
    }
    /// <summary>
    /// Sets the behavior of the RoboDK API. By default, robodk shows the path simulation for movement instructions (run_mode=1=RUNMODE_SIMULATE).
    /// Setting the run_mode to RUNMODE_QUICKVALIDATE allows performing a quick check to see if the path is feasible.
    /// if robot.Connect() is used, RUNMODE_RUN_FROM_PC is selected automatically.
    /// </summary>
    /// <param name="run_mode">int = RUNMODE
    /// RUNMODE_SIMULATE=1        performs the simulation moving the robot (default)
    /// RUNMODE_QUICKVALIDATE=2   performs a quick check to validate the robot movements
    /// RUNMODE_MAKE_ROBOTPROG=3  makes the robot program
    /// RUNMODE_RUN_REAL=4        moves the real robot is it is connected</param>
    public void setRunMode(int run_mode = 1)
    {
        _check_connection();
        _send_Line("S_RunMode");
        _send_Int(run_mode);
        _check_status();
    }

    /// <summary>
    /// Returns the behavior of the RoboDK API. By default, robodk shows the path simulation for movement instructions (run_mode=1)
    /// </summary>
    /// <returns>int = RUNMODE
    /// RUNMODE_SIMULATE=1        performs the simulation moving the robot (default)
    /// RUNMODE_QUICKVALIDATE=2   performs a quick check to validate the robot movements
    /// RUNMODE_MAKE_ROBOTPROG=3  makes the robot program
    /// RUNMODE_RUN_REAL=4        moves the real robot is it is connected</returns>
    public int RunMode()
    {
        _check_connection();
        _send_Line("G_RunMode");
        int runmode = _recv_Int();
        _check_status();
        return runmode;
    }

    /// <summary>
    /// Gets all the user parameters from the open RoboDK station.
    /// The parameters can also be modified by right clicking the station and selecting "shared parameters"
    /// User parameters can be added or modified by the user
    /// </summary>
    /// <returns>list of pairs of strings as parameter-value (list of a list)</returns>
    public List<List<string>> getParams()
    {
        _check_connection();
        _send_Line("G_Params");
        List<List<string>> paramlist = new List<List<string>>();
        int nparam = _recv_Int();
        for (int i = 0; i < nparam; i++)
        {
            string param = _recv_Line();
            string value = _recv_Line();

            List<string> param_value = new List<string>();
            param_value.Add(param);
            param_value.Add(value);
            paramlist.Add(param_value);
        }
        _check_status();
        return paramlist;
    }

    /// <summary>
    /// Gets a global or a user parameter from the open RoboDK station.
    /// The parameters can also be modified by right clicking the station and selecting "shared parameters"
    /// Some available parameters:
    /// PATH_OPENSTATION = folder path of the current .stn file
    /// FILE_OPENSTATION = file path of the current .stn file
    /// PATH_DESKTOP = folder path of the user's folder
    /// Other parameters can be added or modified by the user
    /// </summary>
    /// <param name="param">RoboDK parameter</param>
    /// <returns>value</returns>
    public string getParam(string param)
    {
        _check_connection();
        _send_Line("G_Param");
        _send_Line(param);
        string value = _recv_Line();
        if (value.StartsWith("UNKNOWN "))
        {
            value = null;
        }
        _check_status();
        return value;
    }

    /// <summary>
    /// Sets a global parameter from the RoboDK station. If the parameters exists, it will be modified. If not, it will be added to the station.
    /// The parameters can also be modified by right clicking the station and selecting "shared parameters".
    /// </summary>
    /// <param name="param">RoboDK parameter</param>
    /// <param name="value">value</param>
    /// <returns></returns>
    public void setParam(string param, string value)
    {
        _check_connection();
        _send_Line("S_Param");
        _send_Line(param);
        _send_Line(value);
        _check_status();
    }

    /// <summary>
    /// Sets a global parameter from the RoboDK station. If the parameters exists, it will be modified. If not, it will be added to the station.
    /// The parameters can also be modified by right clicking the station and selecting "shared parameters".
    /// </summary>
    /// <param name="param">RoboDK parameter</param>
    /// <param name="value">value</param>
    /// <returns></returns>
    public void setParam(string param, double value)
    {
        _check_connection();
        _send_Line("S_Param");
        _send_Line(param);
        _send_Line(value.ToString());
        _check_status();
    }

    /// <summary>
    /// Send a special command. These commands are meant to have a specific effect in RoboDK, such as changing a specific setting or provoke specific events.
    /// </summary>
    /// <param name="cmd">Command Name, such as Trace, Threads or Window.</param>
    /// <param name="value">Comand value (optional, not all commands require a value)</param>
    /// <returns></returns>
    public string Command(string cmd, string value = "")
    {
        _check_connection();
        _send_Line("SCMD");
        _send_Line(cmd);
        _send_Line(value);
        string response = _recv_Line();
        _check_status();
        return response;
    }

    /// <summary>
    /// Send a special command. These commands are meant to have a specific effect in RoboDK, such as changing a specific setting or provoke specific events.
    /// </summary>
    /// <param name="cmd">Command Name, such as Trace, Threads or Window.</param>
    /// <param name="value">Comand value (optional, not all commands require a value)</param>
    /// <returns></returns>
    public string Command(string cmd, bool value)
    {
        return Command(cmd, value ? "1" : "0");
    }

    /// <summary>
    /// Send a special command. These commands are meant to have a specific effect in RoboDK, such as changing a specific setting or provoke specific events.
    /// </summary>
    /// <param name="cmd">Command Name, such as Trace, Threads or Window.</param>
    /// <param name="value">Comand value (optional, not all commands require a value)</param>
    /// <returns></returns>
    public string Command(string cmd, int value)
    {
        return Command(cmd, value.ToString());
    }

    /// <summary>
    /// Send a special command. These commands are meant to have a specific effect in RoboDK, such as changing a specific setting or provoke specific events.
    /// </summary>
    /// <param name="cmd">Command Name, such as Trace, Threads or Window.</param>
    /// <param name="value">Comand value (optional, not all commands require a value)</param>
    /// <returns></returns>
    public string Command(string cmd, double value)
    {
        return Command(cmd, value.ToString("0.######"));
    }

    /// <summary>
    /// Returns the list of open stations in RoboDK
    /// </summary>
    /// <returns></returns>
    public List<Item> GetOpenStations()
    {
        _check_connection();
        _send_Line("G_AllStn");
        int nstn = _recv_Int();
        List<Item> list_stn = new List<Item>();
        for (int i = 0; i < nstn; i++)
        {
            Item station = _recv_Item();
            list_stn.Add(station);
        }
        _check_status();
        return list_stn;
    }

    /// <summary>
    /// Returns the active station item (station currently visible)
    /// </summary>
    /// <returns></returns>
    public Item GetActiveStation()
    {
        _check_connection();
        _send_Line("G_ActiveStn");
        Item station = _recv_Item();
        _check_status();
        return station;
    }

    /// <summary>
    /// Set the active station (project currently visible)
    /// </summary>
    /// <param name="station">station item, it can be previously loaded as an RDK file</param>
    public void SetActiveStation(Item station)
    {
        _check_connection();
        _send_Line("S_ActiveStn");
        _send_Item(station);
        _check_status();
    }


    /// <summary>
    /// Takes a laser tracker measurement with respect to its own reference frame. If an estimate point is provided, the laser tracker will first move to those coordinates. If search is True, the tracker will search for a target.
    /// </summary>
    /// <param name="estimate"></param>
    /// <param name="search">Returns the XYZ coordinates of the target (in mm). If the target was not found it retuns a null pointer.</param>
    /// <returns></returns>
    public double[] LaserTracker_Measure(double[] estimate, bool search = false)
    {
        _check_connection();
        _send_Line("MeasLT");
        _send_XYZ(estimate);
        _send_Int(search ? 1 : 0);
        double[] xyz = new double[3];
        _recv_XYZ(xyz);
        _check_status();
        if (xyz[0] * xyz[0] + xyz[1] * xyz[1] + xyz[2] * xyz[2] < 0.0001)
        {
            return null;
        }
        return xyz;
    }

    /// <summary>
    /// Takes a measurement with the C-Track stereocamera. It returns two poses, the base reference frame and the measured object reference frame.Status is 0 if measurement succeeded.
    /// </summary>
    /// <param name="pose1">Pose of the measurement reference</param>
    /// <param name="pose2">Pose of the tool measurement</param>
    /// <param name="npoints1">number of visible targets for the measurement pose</param>
    /// <param name="npoints2">number of visible targets for the tool pose</param>
    /// <param name="time">time stamp in milliseconds</param>
    /// <param name="status">Status is 0 if measurement succeeded</param>
    public void StereoCamera_Measure(out Mat pose1, out Mat pose2, out int npoints1, out int npoints2, out int time, out int status)
    {
        _check_connection();
        _send_Line("MeasPose");
        pose1 = _recv_Pose();
        pose2 = _recv_Pose();
        npoints1 = _recv_Int();
        npoints2 = _recv_Int();
        time = _recv_Int();
        status = _recv_Int();
        _check_status();
    }

    /// <summary>
    /// Checks the collision between a line and any objects in the station. The line is composed by 2 points.
    /// Returns the collided item. Use Item.Valid() to check if there was a valid collision.
    /// </summary>
    /// <param name="p1">start point of the line</param>
    /// <param name="p2">end point of the line</param>
    /// <param name="ref_abs">Reference of the two points with respect to the absolute station reference.</param>
    /// /// <param name="xyz_collision">Collided point.</param>
    public Item Collision_Line(double[] p1, double[] p2, Mat ref_abs = null, double[] xyz_collision = null)
    {
        double[] p1_abs = new double[3];
        double[] p2_abs = new double[3];

        if (ref_abs != null)
        {
            p1_abs = ref_abs * p1;
            p2_abs = ref_abs * p2;
        }
        else
        {
            p1_abs = p1;
            p2_abs = p2;
        }
        _check_connection();
        _send_Line("CollisionLine");
        _send_XYZ(p1_abs);
        _send_XYZ(p2_abs);
        Item itempicked = _recv_Item();
        if (xyz_collision != null)
        {
            _recv_XYZ(xyz_collision);
        }
        else
        {
            double[] xyz = new double[3];
            _recv_XYZ(xyz);
        }
        bool collision = itempicked.Valid();
        _check_status();
        return itempicked;
    }


    /// <summary>
    /// Calculate the forward kinematics solution for multiple robots at the same time (faster)
    /// </summary>
    /// <param name="robot_list">list of items</param>
    /// <param name="joints_list">list of joint</param>
    /// <param name="solution_ok_list">optional list of bool flags to notify about failed/invalid result</param>
    public List<Mat> SolveFK(List<Item> robot_list, List<double[]> joints_list, List<bool> solution_ok_list = null)
    {
        _require_build(6535);
        int nitm = Math.Min(robot_list.Count, joints_list.Count);
        _check_connection();
        _send_Line("G_LFK");
        _send_Int(nitm);
        List<Mat> list_poses = new List<Mat>();
        for (int i = 0; i < nitm; i++)
        {
            _send_Array(joints_list[i]);
            _send_Item(robot_list[i]);
            Mat pose = _recv_Pose();
            int status = _recv_Int();
            list_poses.Add(pose);
            if (solution_ok_list != null)
            {
                solution_ok_list.Add(status > 0);
            }
        }
        _check_status();
        return list_poses;
    }


    /// <summary>
    /// Calculate the inverse kinematics solution for multiple robots at the same time (faster)
    /// </summary>
    /// <param name="robot_list">list of items</param>
    /// <param name="pose_list">list of poses</param>
    /// <param name="solution_ok_list">optional list of bool flags to notify about failed/invalid result</param>
    public List<double[]> SolveIK(List<Item> robot_list, List<Mat> pose_list)
    {
        _require_build(6535);
        int nitm = Math.Min(robot_list.Count, pose_list.Count);
        _check_connection();
        _send_Line("G_LIK");
        _send_Int(nitm);
        List<double[]> list_joints = new List<double[]>();
        for (int i = 0; i < nitm; i++)
        {
            _send_Pose(pose_list[i]);
            _send_Item(robot_list[i]);
            double[] joints_sol = _recv_Array();
            list_joints.Add(joints_sol);
        }
        _check_status();
        return list_joints;
    }


    /// <summary>
    /// Calculate the inverse kinematics solution for multiple robots at the same time (faster)
    /// </summary>
    /// <param name="robot_list">list of items</param>
    /// <param name="pose_list">list of poses</param>
    /// <param name="solution_ok_list">optional list of bool flags to notify about failed/invalid result</param>
    public List<double[]> SolveIK(List<Item> robot_list, List<Mat> pose_list, List<double[]> japrox_list)
    {
        _require_build(7399);
        int nitm = Math.Min(Math.Min(robot_list.Count, pose_list.Count), japrox_list.Count);
        _check_connection();
        _send_Line("G_LIK_jnts");
        _send_Int(nitm);
        List<double[]> list_joints = new List<double[]>();
        for (int i = 0; i < nitm; i++)
        {
            _send_Pose(pose_list[i]);
            _send_Array(japrox_list[i]);
            _send_Item(robot_list[i]);
            double[] joints_sol = _recv_Array();
            list_joints.Add(joints_sol);
        }
        _check_status();
        return list_joints;
    }


    /// <summary>
    /// Calculate the inverse kinematics solution for multiple robots at the same time. This call allows you to have a bulk calculation for faster performance.
    /// </summary>
    /// <param name="robot_list">list of items</param>
    /// <param name="pose_list">list of poses</param>
    /// <param name="solution_ok_list">optional list of bool flags to notify about failed/invalid result</param>
    public List<Mat> SolveIK_All(List<Item> robot_list, List<Mat> pose_list)
    {
        _require_build(7399);
        int nitm = Math.Min(robot_list.Count, pose_list.Count);
        _check_connection();
        _send_Line("G_LIK_cmpl");
        _send_Int(nitm);
        List<Mat> list_joints2d = new List<Mat>();
        for (int i = 0; i < nitm; i++)
        {
            _send_Pose(pose_list[i]);
            _send_Item(robot_list[i]);
            Mat joints_sol_all = _recv_Matrix2D();
            list_joints2d.Add(joints_sol_all);
        }
        _check_status();
        return list_joints2d;
    }

    /// <summary>
    /// Returns the robot configuration state for a set of robot joints.
    /// </summary>
    /// <param name="joints">array of joints</param>
    /// <returns>3-array -> configuration status as [REAR, LOWERARM, FLIP]</returns>
    public List<double[]> JointsConfig(List<Item> robot_list, List<double[]> joints_list)
    {
        _require_build(7399);
        int nitm = Math.Min(robot_list.Count, joints_list.Count);
        _check_connection();
        _send_Line("G_LThetas_Config");
        _send_Int(nitm);
        List<double[]> list_config = new List<double[]>();
        for (int i = 0; i < nitm; i++)
        {
            _send_Array(joints_list[i]);
            _send_Item(robot_list[i]);
            double[] config = _recv_Array();
            list_config.Add(config);
        }
        _check_status();
        return list_config;
    }

    /// <summary>
    /// Sets the visibility for a list of items
    /// </summary>
    /// <param name="item_list">list of items</param>
    /// <param name="visible_list">list visible flags (bool)</param>
    /// <param name="visible_frames">list visible frames (optional, hidden by default)</param>
    public void setVisible(List<Item> item_list, List<bool> visible_list, List<int> visible_frames = null)
    {
        int nitm = Math.Min(item_list.Count, visible_list.Count);
        _check_connection();
        _send_Line("S_VisibleList");
        _send_Int(nitm);
        for (int i = 0; i < nitm; i++)
        {
            _send_Item(item_list[i]);
            _send_Int(visible_list[i] ? 1 : 0);
            int frame_vis = -1;
            if (visible_frames != null && visible_frames.Count > i)
            {
                frame_vis = visible_frames[i];
            }
            _send_Int(frame_vis);
        }
        _check_status();
    }


    static char[] hexDigits = { '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F' };
    public static string Color2Hex(Color color)
    {
        byte[] bytes = new byte[4];
        bytes[0] = color.A;
        bytes[1] = color.R;
        bytes[2] = color.G;
        bytes[3] = color.B;
        char[] chars = new char[bytes.Length * 2];
        for (int i = 0; i < bytes.Length; i++)
        {
            int b = bytes[i];
            chars[i * 2] = hexDigits[b >> 4];
            chars[i * 2 + 1] = hexDigits[b & 0xF];
        }
        return new string(chars);
    }

    /// <summary>
    /// Sets the color for a list of items
    /// </summary>
    /// <param name="item_list">list of items</param>
    /// <param name="color_list">list of colors</param>
    public void setColor(List<Item> item_list, List<Color> color_list)
    {
        int nitm = Math.Min(item_list.Count, color_list.Count);
        _check_connection();
        _send_Line("S_ColorList");
        _send_Int(nitm);
        for (int i = 0; i < nitm; i++)
        {
            _send_Item(item_list[i]);
            _send_Line("#" + Color2Hex(color_list[i]));
        }
        _check_status();
    }




    /// <summary>
    /// Show a list of objects or a robot link as collided (red) or as not collided (normal color)
    /// </summary>
    /// <param name="item_list">List of items</param>
    /// <param name="collided_list">List of collided flags (True=show as collided)</param>
    /// <param name="robot_link_id">Robot link ID, when applicable</param>
    public void ShowAsCollided(List<Item> item_list, List<bool> collided_list, List<int> robot_link_id = null)
    {
        _require_build(5794);
        _check_connection();
        int nitms = Math.Min(item_list.Count, collided_list.Count);
        if (robot_link_id != null)
        {
            nitms = Math.Min(nitms, robot_link_id.Count);
        }
        _send_Line("ShowAsCollidedList");
        _send_Int(nitms);
        for (int i = 0; i < nitms; i++)
        {
            _send_Item(item_list[i]);
            _send_Int(collided_list[i] ? 1 : 0);
            int link_id = 0;
            if (robot_link_id != null)
            {
                link_id = robot_link_id[i];
            }
            _send_Int(link_id);
        }
        _check_status();
    }

    /// <summary>
    /// Returns the current joints of a list of robots.
    /// </summary>
    /// <param name="robot_item_list">list of robot items</param>
    /// <returns>list of robot joints (double x nDOF)</returns>
    public double[][] Joints(Item[] robot_item_list)
    {
        _check_connection();
        _send_Line("G_ThetasList");
        int nrobs = robot_item_list.Length;
        _send_Int(nrobs);
        double[][] joints_list = new double[nrobs][];
        for (int i = 0; i < nrobs; i++)
        {
            _send_Item(robot_item_list[i]);
            joints_list[i] = _recv_Array();
        }
        _check_status();
        return joints_list;
    }

    /// <summary>
    /// Sets the current robot joints for a list of robot items and a list of a set of joints.
    /// </summary>
    /// <param name="robot_item_list">list of robot items</param>
    /// <param name="joints_list">list of robot joints (double x nDOF)</param>
    public void setJoints(Item[] robot_item_list, double[][] joints_list)
    {
        int nrobs = Math.Min(robot_item_list.Length, joints_list.Length);
        _check_connection();
        _send_Line("S_ThetasList");
        _send_Int(nrobs);
        for (int i = 0; i < nrobs; i++)
        {
            _send_Item(robot_item_list[i]);
            _send_Array(joints_list[i]);
        }
        _check_status();
    }

    /// <summary>
    /// Calibrate a tool (TCP) given a number of points or calibration joints. Important: If the robot is calibrated, provide joint values to maximize accuracy.
    /// </summary>
    /// <param name="poses_joints">matrix of poses in a given format or a list of joints</param>
    /// <param name="error_stats">stats[mean, standard deviation, max] - Output error stats summary</param>
    /// <param name="format">Euler format. Optionally, use JOINT_FORMAT and provide the robot.</param>
    /// <param name="algorithm">type of algorithm (by point, plane, ...)</param>
    /// <param name="robot">Robot used for calibration (if using joint values)</param>
    /// <returns>TCP as [x, y, z] - calculated TCP</returns>
    /// 
    public double[] CalibrateTool(Mat poses_joints, out double[] error_stats, int format = EULER_RX_RY_RZ, int algorithm = CALIBRATE_TCP_BY_POINT, Item robot = null)
    {
        _check_connection();
        _send_Line("CalibTCP2");
        _send_Matrix2D(poses_joints);
        _send_Int(format);
        _send_Int(algorithm);
        _send_Item(robot);
        double[] tcp = _recv_Array();
        error_stats = _recv_Array();
        Mat error_graph = _recv_Matrix2D();
        _check_status();
        return tcp;
        //errors = errors[:, 1].tolist()
    }

    /// <summary>
    /// Calibrate a Reference Frame given a list of points or joint values. Important: If the robot is calibrated, provide joint values to maximize accuracy.
    /// </summary>
    /// <param name="joints">points as a 3xN matrix or nDOFsxN) - List of points or a list of robot joints</param>
    /// <param name="method">type of algorithm(by point, plane, ...) CALIBRATE_FRAME_...</param>
    /// <param name="use_joints">use points or joint values. The robot item must be provided if joint values is used.</param>
    /// <param name="robot"></param>
    /// <returns></returns>
    public Mat CalibrateReference(Mat joints, int method = CALIBRATE_FRAME_3P_P1_ON_X, bool use_joints = false, Item robot = null)
    {
        _check_connection();
        _send_Line("CalibFrame");
        _send_Matrix2D(joints);
        _send_Int(use_joints ? -1 : 0);
        _send_Int(method);
        _send_Item(robot);
        Mat reference_pose = _recv_Pose();
        double[] error_stats = _recv_Array();
        _check_status();
        //errors = errors[:, 1].tolist()
        return reference_pose;
    }

    /// <summary>
    /// Defines the name of the program when the program is generated. It is also possible to specify the name of the post processor as well as the folder to save the program. 
    /// This method must be called before any program output is generated (before any robot movement or other instruction).
    /// </summary>
    /// <param name="progname">name of the program</param>
    /// <param name="defaultfolder">folder to save the program, leave empty to use the default program folder</param>
    /// <param name="postprocessor">name of the post processor (for a post processor in C:/RoboDK/Posts/Fanuc_post.py it is possible to provide "Fanuc_post.py" or simply "Fanuc_post")</param>
    /// <param name="robot">Robot to link</param>
    /// <returns></returns>
    public int ProgramStart(string progname, string defaultfolder = "", string postprocessor = "", Item robot = null)
    {
        _check_connection();
        _send_Line("ProgramStart");
        _send_Line(progname);
        _send_Line(defaultfolder);
        _send_Line(postprocessor);
        _send_Item(robot);
        int errors = _recv_Int();
        _check_status();
        return errors;
    }

    /// <summary>
    /// Set the pose of the wold reference frame with respect to the view (camera/screen)
    /// </summary>
    /// <param name="pose"></param>
    public void setViewPose(Mat pose)
    {
        _check_connection();
        _send_Line("S_ViewPose");
        _send_Pose(pose);
        _check_status();
    }

    /// <summary>
    /// Get the pose of the wold reference frame with respect to the view (camera/screen)
    /// </summary>
    /// <param name="pose"></param>
    public Mat ViewPose(int preset = -1)
    {
        _require_build(6700);
        _check_connection();
        _send_Line("G_ViewPose2");
        _send_Int(preset);
        Mat pose = _recv_Pose();
        _check_status();
        return pose;
    }

    /// <summary>
    /// Gets the nominal robot parameters
    /// </summary>
    /// <param name="robot"></param>
    /// <param name="dhm"></param>
    /// <param name="pose_base"></param>
    /// <param name="pose_tool"></param>
    /// <returns></returns>
    public bool setRobotParams(Item robot, double[][] dhm, Mat pose_base, Mat pose_tool)
    {
        _check_connection();
        _send_Line("S_AbsAccParam");
        _send_Item(robot);
        Mat r2b = Mat.Identity4x4();
        _send_Pose(r2b);
        _send_Pose(pose_base);
        _send_Pose(pose_tool);
        int ndofs = dhm.Length;
        _send_Int(ndofs);
        for (int i = 0; i < ndofs; i++)
        {
            _send_Array(dhm[i]);
        }

        // for internal use only
        _send_Pose(pose_base);
        _send_Pose(pose_tool);
        _send_Int(ndofs);
        for (int i = 0; i < ndofs; i++)
        {
            _send_Array(dhm[i]);
        }
        // reserved
        _send_Array(null);
        _send_Array(null);
        _check_status();
        return true;
    }

    /// <summary>
    /// Create a new robot or mechanism.
    /// </summary>
    /// <param name="type">Type of the mechanism</param>
    /// <param name="list_obj">list of object items that build the robot</param>
    /// <param name="param">robot parameters in the same order as shown in the RoboDK menu: Utilities-Build Mechanism or robot</param>
    /// <param name="joints_build">current state of the robot(joint axes) to build the robot</param>
    /// <param name="joints_home">joints for the home position(it can be changed later)</param>
    /// <param name="joints_senses"></param>
    /// <param name="joints_lim_low"></param>
    /// <param name="joints_lim_high"></param>
    /// <param name="base_frame"></param>
    /// <param name="tool"></param>
    /// <param name="name"></param>
    /// <param name="robot">existing robot in the station to replace it(optional)</param>
    /// <returns></returns>
    public Item BuildMechanism(int type, List<Item> list_obj, List<double> param, List<double> joints_build, List<double> joints_home, List<double> joints_senses, List<double> joints_lim_low, List<double> joints_lim_high, Mat base_frame = null, Mat tool = null, string name = "New robot", Item robot = null)
    {
        if (tool == null)
        {
            tool = Mat.Identity4x4();
        }
        if (base_frame == null)
        {
            base_frame = Mat.Identity4x4();
        }
        int ndofs = list_obj.Count - 1;
        _check_connection();
        _send_Line("BuildMechanism");
        _send_Item(robot);
        _send_Line(name);
        _send_Int(type);
        _send_Int(ndofs);
        for (int i = 0; i <= ndofs; i++)
        {
            _send_Item(list_obj[i]);
        }
        _send_Pose(base_frame);
        _send_Pose(tool);
        _send_ArrayList(param);
        Mat joints_data = new Mat(ndofs, 5);
        for (int i = 0; i < ndofs; i++)
        {
            joints_data[i, 0] = joints_build[i];
            joints_data[i, 1] = joints_home[i];
            joints_data[i, 2] = joints_senses[i];
            joints_data[i, 3] = joints_lim_low[i];
            joints_data[i, 4] = joints_lim_high[i];
        }
        _send_Matrix2D(joints_data);
        Item new_robot = _recv_Item();
        _check_status();
        return new_robot;
    }



    //------------------------------------------------------------------
    //----------------------- CAMERA VIEWS -----------------------------
    /// <summary>
    /// Open a simulated 2D camera view. Returns a handle pointer that can be used in case more than one simulated view is used.
    /// </summary>
    /// <param name="item">Reference frame or other object to attach the camera</param>
    /// <param name="cam_params">Camera parameters as a string. Refer to the documentation for more information.</param>
    /// <returns>Camera pointer/handle. Keep the handle if more than 1 simulated camera is used</returns>
    public UInt64 Cam2D_Add(Item item, string cam_params = "")
    {
        _check_connection();
        _send_Line("Cam2D_Add");
        _send_Item(item);
        _send_Line(cam_params);
        UInt64 ptr = _recv_Ptr();
        _check_status();
        return ptr;
    }

    /// <summary>
    /// Take a snapshot from a simulated camera view and save it to a file. Returns 1 if success, 0 otherwise.
    /// </summary>
    /// <param name="file_save_img">file path to save.Formats supported include PNG, JPEG, TIFF, ...</param>
    /// <param name="cam_handle">amera handle(pointer returned by Cam2D_Add)</param>
    /// <returns></returns>
    public bool Cam2D_Snapshot(string file_save_img, UInt64 cam_handle = 0)
    {
        _check_connection();
        _send_Line("Cam2D_Snapshot");
        _send_Ptr(cam_handle);
        _send_Line(file_save_img);
        int success = _recv_Int();
        _check_status();
        return success > 0;
    }

    /// <summary>
    /// Closes all camera windows or one specific camera if the camera handle is provided. Returns 1 if success, 0 otherwise.
    /// </summary>
    /// <param name="cam_handle">camera handle(pointer returned by Cam2D_Add). Leave to 0 to close all simulated views.</param>
    /// <returns></returns>
    public bool Cam2D_Close(UInt64 cam_handle = 0)
    {
        _check_connection();
        if (cam_handle == 0)
        {
            _send_Line("Cam2D_CloseAll");
        }
        else
        {
            _send_Line("Cam2D_Close");
            _send_Ptr(cam_handle);
        }
        int success = _recv_Int();
        _check_status();
        return success > 0;
    }

    /// <summary>
    /// Set the parameters of the simulated camera.
    /// </summary>
    /// <param name="cam_params">parameter settings according to the parameters supported by Cam2D_Add</param>
    /// <param name="cam_handle">camera handle (optional)</param>
    /// <returns></returns>
    public bool Cam2D_SetParams(string cam_params, UInt64 cam_handle = 0)
    {
        _check_connection();
        _send_Line("Cam2D_SetParams");
        _send_Ptr(cam_handle);
        _send_Line(cam_params);
        int success = _recv_Int();
        _check_status();
        return success > 0;
    }
    //-----------------------------------------------------------------------------------

    /// <summary>
    /// Returns the license string (as shown in the RoboDK main window)
    /// </summary>
    /// <returns></returns>
    public string License()
    {
        _check_connection();
        _send_Line("G_License2");
        string license = _recv_Line();
        string cid = _recv_Line();
        _check_status();
        return license;
    }

    /// <summary>
    /// Returns the list of items selected (it can be one or more items)
    /// </summary>
    /// <returns></returns>
    public List<Item> GetSelectedItems()
    {
        _check_connection();
        _send_Line("G_Selection");
        int nitems = _recv_Int();
        List<Item> list_items = new List<Item>();
        for (int i = 0; i < nitems; i++)
        {
            list_items.Add(_recv_Item());
        }
        _check_status();
        return list_items;
    }

    /// <summary>
    /// Set the selection in the tree
    /// </summary>
    /// <returns></returns>
    public void SetSelectedItems(List<Item> item_list)
    {
        _require_build(8896);
        _check_connection();
        _send_Line("S_Selection");
        _send_Int(item_list.Count);
        for (int i = 0; i < item_list.Count; i++)
        {
            _send_Item(item_list[i]);
        }
        _check_status();
    }

    /// <summary>
    /// Merge multiple object items as one. Source objects are not deleted and a new object is created.
    /// </summary>
    /// <returns>New item</returns>
    public Item MergeItems(List<Item> item_list)
    {
        _require_build(8896);
        _check_connection();
        _send_Line("MergeItems");
        _send_Int(item_list.Count);
        for (int i = 0; i < item_list.Count; i++)
        {
            _send_Item(item_list[i]);
        }
        Item newitem = _recv_Item();
        _check_status();
        return newitem;
    }

    /// <summary>
    /// Show the popup menu to create the ISO9283 path for path accuracy and performance testing
    /// </summary>
    /// <returns>IS9283 Program</returns>
    public Item Popup_ISO9283_CubeProgram(Item robot = null)
    {
        _require_build(5177);
        _check_connection();
        _send_Line("Popup_ProgISO9283");
        _send_Item(robot);
        _COM.ReceiveTimeout = 3600 * 1000;
        Item iso_program = _recv_Item();
        _COM.ReceiveTimeout = _TIMEOUT;
        _check_status();
        return iso_program;
    }


    /// <summary>
    /// Set the interactive mode to define the behavior when navigating and selecting items in RoboDK's 3D view.
    /// </summary>
    /// <param name="mode_type">The mode type defines what accion occurs when the 3D view is selected (Select object, Pan, Rotate, Zoom, Move Objects, ...)</param>
    /// <param name="default_ref_flags">When a movement is specified, we can provide what motion we allow by default with respect to the coordinate system (set apropriate flags)</param>
    /// <param name="custom_items">Provide a list of optional items to customize the move behavior for these specific items (important: the lenght of custom_ref_flags must match)</param>
    /// <param name="custom_ref_flags">Provide a matching list of flags to customize the movement behavior for specific items</param>
    public void SetInteractiveMode(int mode_type = SELECT_MOVE, int default_ref_flags = DISPLAY_REF_DEFAULT, List<Item> custom_items = null, List<int> custom_ref_flags = null)
    {
        _check_connection();
        _send_Line("S_InteractiveMode");
        _send_Int(mode_type);
        _send_Int(default_ref_flags);
        if (custom_items == null || custom_ref_flags == null)
        {
            _send_Int(-1);
        }
        else
        {
            int n_custom = Math.Min(custom_items.Count, custom_ref_flags.Count);
            _send_Int(n_custom);
            for (int i = 0; i < n_custom; i++)
            {
                _send_Item(custom_items[i]);
                _send_Int(custom_ref_flags[i]);
            }
        }
        _check_status();
    }

    /// <summary>
    /// Returns the position of the cursor as XYZ coordinates (by default), or the 3D position of a given set of 2D coordinates of the window (x & y coordinates in pixels from the top left corner)
    /// The XYZ coordinates returned are given with respect to the RoboDK station(absolute reference).
    /// If no coordinates are provided, the current position of the cursor is retrieved.
    /// </summary>
    /// <param name="x_coord">X coordinate in pixels</param>
    /// <param name="y_coord">Y coordinate in pixels</param>
    /// <param name="xyz_station"></param>
    /// <returns></returns>
    public Item GetCursorXYZ(int x_coord = -1, int y_coord = -1, List<double> xyz_station = null)
    {
        _check_connection();
        _send_Line("Proj2d3d");
        _send_Int(x_coord);
        _send_Int(y_coord);
        int selection = _recv_Int();
        double[] xyz = new double[3];
        Item selected_item = _recv_Item();
        _recv_XYZ(xyz);
        _check_status();
        if (xyz != null)
        {
            xyz_station.Add(xyz[0]); xyz_station.Add(xyz[1]); xyz_station.Add(xyz[2]);
        }
        return selected_item;
    }

    /// <summary>
    /// The Item class represents an item in RoboDK station. An item can be a robot, a frame, a tool, an object, a target, ... any item visible in the station tree.
    /// An item can also be seen as a node where other items can be attached to (child items).
    /// Every item has one parent item/node and can have one or more child items/nodes
    /// RoboLinkItem is a "friend" class of RoboLink.
    /// </summary>
    public class Item
    {
        private UInt64 item = 0;
        private RoboDK link; // pointer to the RoboLink connection
        int type = -1;
        string name;

        public Item(RoboDK connection_link, UInt64 item_ptr = 0, int itemtype = -1)
        {
            item = item_ptr;
            link = connection_link;
            type = itemtype;
        }

        public UInt64 get_item()
        {
            return item;
        }

        public string ToString2()
        {
            if (Valid())
            {
                return String.Format("RoboDK item {0} of type {1}", item, type);
            }
            else
            {
                return "RoboDK item (INVALID)";
            }
        }

        /// <summary>
        /// Returns an integer that represents the type of the item (robot, object, tool, frame, ...)
        /// Compare the returned value to ITEM_CASE_* variables
        /// </summary>
        /// <param name="item_other"></param>
        /// <returns></returns>
        public bool Equals(Item item_other)
        {
            return this.item == item_other.item;
        }

        /// <summary>
        /// Use RDK() instead. Returns the RoboDK link Robolink().
        /// </summary>
        /// <returns></returns>
        public RoboDK RL()
        {
            return link;
        }

        /// <summary>
        /// Returns the RoboDK link Robolink().
        /// </summary>
        /// <returns></returns>
        public RoboDK RDK()
        {
            return link;
        }

        /// <summary>
        /// Create a new communication link. Use this for robots if you use a multithread application running multiple robots at the same time.
        /// </summary>
        public void NewLink()
        {
            link = new RoboDK();
        }

        //////// GENERIC ITEM CALLS
        /// <summary>
        /// Returns the type of an item (robot, object, target, reference frame, ...)
        /// </summary>
        /// <returns></returns>
        public int Type()
        {
            return type;
            /*link._check_connection();
            link._send_Line("G_Item_Type");
            link._send_Item(this);
            int itemtype = link._recv_Int();
            link._check_status();
            return itemtype;*/
        }

        ////// add more methods

        /// <summary>
        /// Save a station or object to a file
        /// </summary>
        /// <param name="filename"></param>
        public void Save(string filename)
        {
            link.Save(filename, this);
        }

        /// <summary>
        /// Deletes an item and its childs from the station.
        /// </summary>
        public void Delete()
        {
            link._check_connection();
            link._send_Line("Remove");
            link._send_Item(this);
            link._check_status();
            item = 0;
        }

        /// <summary>
        /// Checks if the item is valid. An invalid item will be returned by an unsuccessful function call.
        /// </summary>
        /// <returns>true if valid, false if invalid</returns>
        public bool Valid()
        {
            if (item == 0)
            {
                return false;
            }
            return true;
        }

        /// <summary>
        /// Attaches the item to a new parent while maintaining the relative position with its parent. The absolute position is changed.
        /// </summary>
        /// <param name="parent"></param>
        public void setParent(Item parent)
        {
            link._check_connection();
            link._send_Line("S_Parent");
            link._send_Item(this);
            link._send_Item(parent);
            link._check_status();
        }

        /// <summary>
        /// Attaches the item to another parent while maintaining the current absolute position in the station.
        /// The relationship between this item and its parent is changed to maintain the abosolute position.
        /// </summary>
        /// <param name="parent">parent item to attach this item</param>
        public void setParentStatic(Item parent)
        {
            link._check_connection();
            link._send_Line("S_Parent_Static");
            link._send_Item(this);
            link._send_Item(parent);
            link._check_status();
        }


        /// <summary>
        /// Attach the closest object to the tool.
        /// Returns the item that was attached.
        /// Use item.Valid() to check if an object was attached to the tool.
        /// </summary>
        public Item AttachClosest()
        {
            link._check_connection();
            link._send_Line("Attach_Closest");
            link._send_Item(this);
            Item item_attached = link._recv_Item();
            link._check_status();
            return item_attached;
        }

        /// <summary>
        /// Detach the closest object attached to the tool (see also: setParentStatic).
        /// </summary>
        /// <param name="parent">New parent item to attach, such as a reference frame(optional). If not provided, the items held by the tool will be placed at the station root.</param>
        public Item DetachClosest(Item parent = null)
        {
            link._check_connection();
            link._send_Line("Detach_Closest");
            link._send_Item(this);
            link._send_Item(parent);
            Item item_detached = link._recv_Item();
            link._check_status();
            return item_detached;
        }

        /// <summary>
        /// Detaches any object attached to a tool.
        /// </summary>
        /// <param name="parent">New parent item to attach, such as a reference frame(optional). If not provided, the items held by the tool will be placed at the station root.</param>
        public void DetachAll(Item parent = null)
        {
            link._check_connection();
            link._send_Line("Detach_All");
            link._send_Item(this);
            link._send_Item(parent);
            link._check_status();
        }

        /// <summary>
        /// Return the parent item of this item (:class:`.Item`)
        /// </summary>
        /// <returns></returns>
        public Item Parent()
        {
            link._check_connection();
            link._send_Line("G_Parent");
            link._send_Item(this);
            Item parent = link._recv_Item();
            link._check_status();
            return parent;
        }


        /// <summary>
        /// Returns a list of the item childs that are attached to the provided item.
        /// </summary>
        /// <returns>item x n -> list of child items</returns>
        public Item[] Childs()
        {
            link._check_connection();
            link._send_Line("G_Childs");
            link._send_Item(this);
            int nitems = link._recv_Int();
            Item[] itemlist = new Item[nitems];
            for (int i = 0; i < nitems; i++)
            {
                itemlist[i] = link._recv_Item();
            }
            link._check_status();
            return itemlist;
        }

        /// <summary>
        /// Returns 1 if the item is visible, otherwise, returns 0.
        /// </summary>
        /// <returns>true if visible, false if not visible</returns>
        public bool Visible()
        {
            link._check_connection();
            link._send_Line("G_Visible");
            link._send_Item(this);
            int visible = link._recv_Int();
            link._check_status();
            return (visible != 0);
        }
        /// <summary>
        /// Sets the item visiblity status
        /// </summary>
        /// <param name="visible"></param>
        /// <param name="visible_reference">set the visible reference frame (1) or not visible (0)</param>
        public void setVisible(bool visible, int visible_reference = -1)
        {
            if (visible_reference < 0)
            {
                visible_reference = visible ? 1 : 0;
            }
            link._check_connection();
            link._send_Line("S_Visible");
            link._send_Item(this);
            link._send_Int(visible ? 1 : 0);
            link._send_Int(visible_reference);
            link._check_status();
        }

        /// <summary>
        /// Show an object or a robot link as collided (red) or as not collided (normal color)
        /// </summary>
        /// <param name="collided"></param>
        /// <param name="robot_link_id"></param>
        public void ShowAsCollided(bool collided, int robot_link_id = 0)
        {
            link._require_build(5449);
            link._check_connection();
            link._send_Line("ShowAsCollided");
            link._send_Item(this);
            link._send_Int(robot_link_id);
            link._send_Int(collided ? 1 : 0);
            link._check_status();
        }

        /// <summary>
        /// Returns the name of an item. The name of the item is always displayed in the RoboDK station tree
        /// </summary>
        /// <returns>name of the item</returns>
        public string Name()
        {
            link._check_connection();
            link._send_Line("G_Name");
            link._send_Item(this);
            name = link._recv_Line();
            link._check_status();
            return name;
        }

        /// <summary>
        /// Set the name of a RoboDK item.
        /// </summary>
        /// <param name="name"></param>
        public void setName(string name)
        {
            link._check_connection();
            link._send_Line("S_Name");
            link._send_Item(this);
            link._send_Line(name);
            link._check_status();
        }

        // add more methods

        /// <summary>
        /// Sets the local position (pose) of an object, target or reference frame. For example, the position of an object/frame/target with respect to its parent.
        /// If a robot is provided, it will set the pose of the end efector.
        /// </summary>
        /// <param name="pose">4x4 homogeneous matrix</param>
        public void setPose(Mat pose)
        {
            link._check_connection();
            link._send_Line("S_Hlocal");
            link._send_Item(this);
            link._send_Pose(pose);
            link._check_status();
        }

        /// <summary>
        /// Returns the local position (pose) of an object, target or reference frame. For example, the position of an object/frame/target with respect to its parent.
        /// If a robot is provided, it will get the pose of the end efector
        /// </summary>
        /// <returns>4x4 homogeneous matrix (pose)</returns>
        public Mat Pose()
        {
            link._check_connection();
            link._send_Line("G_Hlocal");
            link._send_Item(this);
            Mat pose = link._recv_Pose();
            link._check_status();
            return pose;
        }

        /// <summary>
        /// Sets the position (pose) the object geometry with respect to its own reference frame. This procedure works for tools and objects.
        /// </summary>
        /// <param name="pose">4x4 homogeneous matrix</param>
        /// <param name="apply_movement">Apply the movement to the inner geometry and not as a pose shift</param>
        public void setGeometryPose(Mat pose, bool apply_movement = false)
        {
            link._check_connection();
            link._send_Line("S_Hgeo2");
            link._send_Item(this);
            link._send_Pose(pose);
            link._send_Int(apply_movement ? 1 : 0);
            link._check_status();
        }

        /// <summary>
        /// Returns the position (pose) the object geometry with respect to its own reference frame. This procedure works for tools and objects.
        /// </summary>
        /// <returns>4x4 homogeneous matrix (pose)</returns>
        public Mat GeometryPose()
        {
            link._check_connection();
            link._send_Line("G_Hgeom");
            link._send_Item(this);
            Mat pose = link._recv_Pose();
            link._check_status();
            return pose;
        }

        /// <summary>
        /// Obsolete: Use setPoseTool(pose) instead. Sets the tool pose of a tool item. If a robot is provided it will set the tool pose of the active tool held by the robot.
        /// </summary>
        /// <param name="pose">4x4 homogeneous matrix (pose)</param>
        public void setHtool(Mat pose)
        {
            link._check_connection();
            link._send_Line("S_Htool");
            link._send_Item(this);
            link._send_Pose(pose);
            link._check_status();
        }

        /// <summary>
        /// Obsolete: Use PoseTool() instead. 
        /// Returns the tool pose of an item. If a robot is provided it will get the tool pose of the active tool held by the robot.
        /// </summary>
        /// <returns>4x4 homogeneous matrix (pose)</returns>
        public Mat Htool()
        {
            link._check_connection();
            link._send_Line("G_Htool");
            link._send_Item(this);
            Mat pose = link._recv_Pose();
            link._check_status();
            return pose;
        }

        /// <summary>
        /// Returns the tool pose of an item. If a robot is provided it will get the tool pose of the active tool held by the robot.
        /// </summary>
        /// <returns>4x4 homogeneous matrix (pose)</returns>
        public Mat PoseTool()
        {
            link._check_connection();
            link._send_Line("G_Tool");
            link._send_Item(this);
            Mat pose = link._recv_Pose();
            link._check_status();
            return pose;
        }

        /// <summary>
        /// Returns the reference frame pose of an item. If a robot is provided it will get the tool pose of the active reference frame used by the robot.
        /// </summary>
        /// <returns>4x4 homogeneous matrix (pose)</returns>
        public Mat PoseFrame()
        {
            link._check_connection();
            link._send_Line("G_Frame");
            link._send_Item(this);
            Mat pose = link._recv_Pose();
            link._check_status();
            return pose;
        }

        /// <summary>
        /// Sets the reference frame of a robot(user frame). The frame can be either an item or a pose.
        /// If "frame" is an item, it links the robot to the frame item. If frame is a pose, it updates the linked pose of the robot frame (with respect to the robot reference frame).
        /// </summary>
        /// <param name="frame_pose">4x4 homogeneous matrix (pose)</param>
        public void setPoseFrame(Mat frame_pose)
        {
            link._check_connection();
            link._send_Line("S_Frame");
            link._send_Pose(frame_pose);
            link._send_Item(this);
            link._check_status();
        }

        /// <summary>
        /// Sets the tool of a robot or a tool object (Tool Center Point, or TCP). The tool pose can be either an item or a 4x4 Matrix.
        /// If the item is a tool, it links the robot to the tool item.If tool is a pose, it updates the current robot TCP.
        /// </summary>
        /// <param name="pose">4x4 homogeneous matrix (pose)</param>
        public void setPoseFrame(RoboDK.Item frame_item)
        {
            link._check_connection();
            link._send_Line("S_Frame_ptr");
            link._send_Item(frame_item);
            link._send_Item(this);
            link._check_status();
        }

        /// <summary>
        /// Sets the tool of a robot or a tool object (Tool Center Point, or TCP). The tool pose can be either an item or a 4x4 Matrix.
        /// If the item is a tool, it links the robot to the tool item.If tool is a pose, it updates the current robot TCP.
        /// </summary>
        /// <param name="tool_pose">4x4 homogeneous matrix (pose)</param>
        public void setPoseTool(Mat tool_pose)
        {
            link._check_connection();
            link._send_Line("S_Tool");
            link._send_Pose(tool_pose);
            link._send_Item(this);
            link._check_status();
        }

        /// <summary>
        /// Sets the tool of a robot or a tool object (Tool Center Point, or TCP). The tool pose can be either an item or a 4x4 Matrix.
        /// If the item is a tool, it links the robot to the tool item.If tool is a pose, it updates the current robot TCP.
        /// </summary>
        /// <param name="tool_item">Tool item</param>
        public void setPoseTool(RoboDK.Item tool_item)
        {
            link._check_connection();
            link._send_Line("S_Tool_ptr");
            link._send_Item(tool_item);
            link._send_Item(this);
            link._check_status();
        }

        /// <summary>
        /// Sets the global position (pose) of an item. For example, the position of an object/frame/target with respect to the station origin.
        /// </summary>
        /// <param name="pose">4x4 homogeneous matrix (pose)</param>
        public void setPoseAbs(Mat pose)
        {
            link._check_connection();
            link._send_Line("S_Hlocal_Abs");
            link._send_Item(this);
            link._send_Pose(pose);
            link._check_status();

        }

        /// <summary>
        /// Returns the global position (pose) of an item. For example, the position of an object/frame/target with respect to the station origin.
        /// </summary>
        /// <returns>4x4 homogeneous matrix (pose)</returns>
        public Mat PoseAbs()
        {
            link._check_connection();
            link._send_Line("G_Hlocal_Abs");
            link._send_Item(this);
            Mat pose = link._recv_Pose();
            link._check_status();
            return pose;
        }

        /// <summary>
        /// Changes the color of a robot/object/tool. A color must must in the format COLOR=[R,G,B,(A=1)] where all values range from 0 to 1.
        /// Alpha (A) defaults to 1 (100% opaque). Set A to 0 to make an object transparent.
        /// </summary>
        /// <param name="tocolor">color to change to</param>
        /// <param name="fromcolor">filter by this color</param>
        /// <param name="tolerance">optional tolerance to use if a color filter is used (defaults to 0.1)</param>
        public void Recolor(double[] tocolor, double[] fromcolor = null, double tolerance = 0.1)
        {
            link._check_connection();
            if (fromcolor == null)
            {
                fromcolor = new double[] { 0, 0, 0, 0 };
                tolerance = 2;
            }
            link.check_color(tocolor);
            link.check_color(fromcolor);
            link._send_Line("Recolor");
            link._send_Item(this);
            double[] combined = new double[9];
            combined[0] = tolerance;
            Array.Copy(fromcolor, 0, combined, 1, 4);
            Array.Copy(tocolor, 0, combined, 5, 4);
            link._send_Array(combined);
            link._check_status();
        }

        /// <summary>
        /// Set the color of an object, tool or robot. A color must in the format COLOR=[R, G, B,(A = 1)] where all values range from 0 to 1.
        /// Optionally set the RBG to -1 to modify the Alpha channel (transparency)
        /// </summary>
        /// <param name="tocolor">color to set</param>
        public void SetColor(List<double> tocolor)
        {
            link._check_connection();
            link.check_color(tocolor);
            link._send_Line("S_Color");
            link._send_Item(this);
            link._send_ArrayList(tocolor);
            link._check_status();
        }

        /// <summary>
        /// Set the color of an object shape. It can also be used for tools. A color must in the format COLOR=[R, G, B,(A = 1)] where all values range from 0 to 1.
        /// </summary>
        /// <param name="shape_id">ID of the shape: the ID is the order in which the shape was added using AddShape()</param>
        /// <param name="tocolor">color to set</param>
        public void SetColor(int shape_id, List<double> tocolor)
        {
            link.check_color(tocolor);
            link._check_connection();
            link._send_Line("S_ShapeColor");
            link._send_Item(this);
            link._send_Int(shape_id);
            link._send_ArrayList(tocolor);
            link._check_status();
        }

        /// <summary>
        /// Return the color of an :class:`.Item` (object, tool or robot). If the item has multiple colors it returns the first color available). 
        /// A color is in the format COLOR=[R, G, B,(A = 1)] where all values range from 0 to 1.
        /// </summary>
        /// <returns></returns>
        public List<double> Color()
        {
            link._check_connection();
            link._send_Line("G_Color");
            link._send_Item(this);
            List<double> color = link._recv_ArrayList();
            link._check_status();
            return color;
        }

        /// <summary>
        /// Apply a scale to an object to make it bigger or smaller.
        /// The scale can be uniform (if scale is a float value) or per axis (if scale is a vector).
        /// </summary>
        /// <param name="scale">scale to apply as [scale_x, scale_y, scale_z]</param>
        public void Scale(double[] scale)
        {
            link._check_connection();
            if (scale.Length != 3)
            {
                throw new RDKException("scale must be a single value or a 3-vector value");
            }
            link._send_Line("Scale");
            link._send_Item(this);
            link._send_Array(scale);
            link._check_status();
        }

        /// <summary>
        /// Apply a scale to an object to make it bigger or smaller.
        /// The scale can be uniform (if scale is a float value) or per axis (if scale is a vector).
        /// </summary>
        /// <param name="scale">scale to apply</param>
        public void Scale(double scale)
        {
            if (scale == 1.0)
                return;

            double[] scale3 = new double[] { scale, scale, scale };
            Scale(scale3);
        }

        /// <summary>
        /// Adds a curve provided point coordinates. The provided points must be a list of vertices. A vertex normal can be provided optionally.
        /// </summary>
        /// <param name="curve_points">matrix 3xN or 6xN -> N must be multiple of 3</param>
        /// <param name="add_to_ref">add_to_ref -> If True, the curve will be added as part of the object in the RoboDK item tree</param>
        /// <param name="projection_type">Type of projection. For example: PROJECTION_ALONG_NORMAL_RECALC will project along the point normal and recalculate the normal vector on the surface projected.</param>
        /// <returns>returns the object where the curve was added or null if failed</returns>
        public Item AddCurve(Mat curve_points, bool add_to_ref = false, int projection_type = PROJECTION_ALONG_NORMAL_RECALC)
        {
            return link.AddCurve(curve_points, this, add_to_ref, projection_type);
        }

        /// <summary>
        /// Projects a point to the object given its coordinates. The provided points must be a list of [XYZ] coordinates. Optionally, a vertex normal can be provided [XYZijk].
        /// </summary>
        /// <param name="points">matrix 3xN or 6xN -> list of points to project</param>
        /// <param name="projection_type">projection_type -> Type of projection. For example: PROJECTION_ALONG_NORMAL_RECALC will project along the point normal and recalculate the normal vector on the surface projected.</param>
        /// <returns>projected points (empty matrix if failed)</returns>
        public Mat ProjectPoints(Mat points, int projection_type = PROJECTION_ALONG_NORMAL_RECALC)
        {
            return link.ProjectPoints(points, this, projection_type);
        }


        /// <summary>
        /// Retrieve the currently selected feature for this object (surface, point, line, ...)
        /// </summary>
        /// <param name="feature_type">The type of geometry, FEATURE_SURFACE, FEATURE_POINT, ... </param>
        /// <param name="feature_id">The internal ID to retrieve the raw geometry (use GetPoints)</param>
        /// <returns>True if the object is selected</returns>
        public bool SelectedFeature(out int feature_type, out int feature_id)
        {
            link._check_connection();
            link._send_Line("G_ObjSelection");
            link._send_Item(this);
            int is_selected = link._recv_Int();
            feature_type = link._recv_Int();
            feature_id = link._recv_Int();
            link._check_status();
            return is_selected > 0;
        }

        /// <summary>
        /// Retrieves the point under the mouse cursor, a curve or the 3D points of an object. The points are provided in [XYZijk] format in relative coordinates. The XYZ are the local point coordinate and ijk is the normal of the surface.
        /// </summary>
        /// <param name="feature_type">The type of geometry (FEATURE_SURFACE, FEATURE_POINT, ...). Set to FEATURE_SURFACE and if not point or curve was selected, the name of the geometry will be 'point on surface'</param>
        /// <param name="feature_id">The internal ID to retrieve the right geometry from the object (use SelectedFeature)</param>
        /// <param name="point_list">The point or a list of points as XYZijk, coordinates are relative to the object (ijk is the normal to the surface)</param>
        /// <returns>The name of the selected geometry (if applicable)</returns>
        public string GetPoints(int feature_type, int feature_id, out Mat point_list)
        {
            link._check_connection();
            link._send_Line("G_ObjPoint");
            link._send_Item(this);
            link._send_Int(feature_type);
            link._send_Int(feature_id);
            point_list = link._recv_Matrix2D();
            string name = link._recv_Line();
            link._check_status();
            return name;
        }

        /// <summary>
        /// Update the robot milling path input and parameters. Parameter input can be an NC file (G-code or APT file) or an object item in RoboDK. A curve or a point follow project will be automatically set up for a robot manufacturing project.
        /// Tip: Use getLink() and setLink() to get/set the robot tool, reference frame, robot and program linked to the project.
        /// Tip: Use setPose() and setJoints() to update the path to tool orientation or the preferred start joints.
        /// </summary>
        /// <param name="ncfile">path to the NC (G-code/APT/Point cloud) file to load (optional)</param>
        /// <param name="part_obj">object holding curves or points to automatically set up a curve/point follow project (optional)</param>
        /// <param name="options">Additional options (optional)</param>
        /// <returns>Program (null). Use Update() to retrieve the result</returns>
        public Item setMachiningParameters(string ncfile = "", Item part_obj = null, string options = "")
        {
            link._check_connection();
            link._send_Line("S_MachiningParams");
            link._send_Item(this);
            link._send_Line(ncfile);
            link._send_Item(part_obj);
            link._send_Line("NO_UPDATE " + options);
            link._COM.ReceiveTimeout = 3600 * 1000;
            Item program = link._recv_Item();
            link._COM.ReceiveTimeout = link._TIMEOUT;
            double status = link._recv_Int() / 1000.0;
            link._check_status();
            return program;
        }

        //"""Target item calls"""

        /// <summary>
        /// Sets a target as a cartesian target. A cartesian target moves to cartesian coordinates.
        /// </summary>
        public void setAsCartesianTarget()
        {
            link._check_connection();
            link._send_Line("S_Target_As_RT");
            link._send_Item(this);
            link._check_status();
        }

        /// <summary>
        /// Sets a target as a joint target. A joint target moves to a joints position without regarding the cartesian coordinates.
        /// </summary>
        public void setAsJointTarget()
        {
            link._check_connection();
            link._send_Line("S_Target_As_JT");
            link._send_Item(this);
            link._check_status();
        }

        /// <summary>
        /// Returns True if a target is a joint target (green icon). Otherwise, the target is a Cartesian target (red icon).
        /// </summary>
        public bool isJointTarget()
        {
            link._check_connection();
            link._send_Line("Target_Is_JT");
            link._send_Item(this);
            int is_jt = link._recv_Int();
            link._check_status();
            return is_jt > 0;
        }

        //#####Robot item calls####

        /// <summary>
        /// Returns the current joints of a robot or the joints of a target. If the item is a cartesian target, it returns the preferred joints (configuration) to go to that cartesian position.
        /// </summary>
        /// <returns>double x n -> joints matrix</returns>
        public double[] Joints()
        {
            link._check_connection();
            link._send_Line("G_Thetas");
            link._send_Item(this);
            double[] joints = link._recv_Array();
            link._check_status();
            return joints;
        }

        // add more methods

        /// <summary>
        /// Returns the home joints of a robot. These joints can be manually set in the robot "Parameters" menu, then select "Set home position"
        /// </summary>
        /// <returns>double x n -> joints array</returns>
        public double[] JointsHome()
        {
            link._check_connection();
            link._send_Line("G_Home");
            link._send_Item(this);
            double[] joints = link._recv_Array();
            link._check_status();
            return joints;
        }

        /// <summary>
        /// Returns an item pointer (:class:`.Item`) to a robot link. This is useful to show/hide certain robot links or alter their geometry.
        /// </summary>
        /// <param name="link_id">link index(0 for the robot base, 1 for the first link, ...)</param>
        /// <returns></returns>
        public Item ObjectLink(int link_id = 0)
        {
            link._check_connection();
            link._send_Line("G_LinkObjId");
            link._send_Item(this);
            link._send_Int(link_id);
            Item item = link._recv_Item();
            link._check_status();
            return item;
        }

        /// <summary>
        /// Returns an item pointer (Item class) to a robot, object, tool or program. This is useful to retrieve the relationship between programs, robots, tools and other specific projects.
        /// </summary>
        /// <param name="type_linked">type of linked object to retrieve</param>
        /// <returns></returns>
        public Item getLink(int type_linked = ITEM_TYPE_ROBOT)
        {
            link._check_connection();
            link._send_Line("G_LinkType");
            link._send_Item(this);
            link._send_Int(type_linked);
            Item item = link._recv_Item();
            link._check_status();
            return item;
        }

        /// <summary>
        /// Sets the current joints of a robot or the joints of a target. It the item is a cartesian target, it returns the preferred joints (configuration) to go to that cartesian position.
        /// </summary>
        /// <param name="joints"></param>
        public void setJoints(double[] joints)
        {
            link._check_connection();
            link._send_Line("S_Thetas");
            link._send_Array(joints);
            link._send_Item(this);
            link._check_status();
        }

        /// <summary>
        /// Returns the joint limits of a robot
        /// </summary>
        /// <param name="lower_limits"></param>
        /// <param name="upper_limits"></param>
        public void JointLimits(out double[] lower_limits, out double[] upper_limits)
        {
            link._check_connection();
            link._send_Line("G_RobLimits");
            link._send_Item(this);
            lower_limits = link._recv_Array();
            upper_limits = link._recv_Array();
            double joints_type = link._recv_Int() / 1000.0;
            link._check_status();
        }

        /// <summary>
        /// Sets the robot of a program or a target. You must set the robot linked to a program or a target every time you copy paste these objects.
        /// If the robot is not provided, the first available robot will be chosen automatically.
        /// </summary>
        /// <param name="robot">Robot item</param>
        public void setRobot(Item robot = null)
        {
            link._check_connection();
            link._send_Line("S_Robot");
            link._send_Item(this);
            link._send_Item(robot);
            link._check_status();
        }

        /// <summary>
        /// Obsolete: Use setPoseFrame instead.
        /// Sets the frame of a robot (user frame). The frame can be either an item or a 4x4 Matrix.
        /// If "frame" is an item, it links the robot to the frame item. If frame is a 4x4 Matrix, it updates the linked pose of the robot frame.
        /// </summary>
        /// <param name="frame">item/pose -> frame item or 4x4 Matrix (pose of the reference frame)</param>
        public void setFrame(Item frame)
        {
            setPoseFrame(frame);
        }

        /// <summary>
        /// Obsolete: Use setPoseFrame instead.
        /// Sets the frame of a robot (user frame). The frame can be either an item or a 4x4 Matrix.
        /// If "frame" is an item, it links the robot to the frame item. If frame is a 4x4 Matrix, it updates the linked pose of the robot frame.
        /// </summary>
        /// <param name="frame">item/pose -> frame item or 4x4 Matrix (pose of the reference frame)</param>
        public void setFrame(Mat frame)
        {
            setPoseFrame(frame);
        }

        /// <summary>
        /// Obsolete: Use setPoseTool instead.
        /// Sets the tool pose of a robot. The tool pose can be either an item or a 4x4 Matrix.
        /// If "tool" is an item, it links the robot to the tool item. If tool is a 4x4 Matrix, it updates the linked pose of the robot tool.
        /// </summary>
        /// <param name="tool">item/pose -> tool item or 4x4 Matrix (pose of the tool frame)</param>
        public void setTool(Item tool)
        {
            setPoseTool(tool);
        }

        /// <summary>
        /// Obsolete: Use setPoseTool instead.
        /// Sets the tool pose of a robot. The tool pose can be either an item or a 4x4 Matrix.
        /// If "tool" is an item, it links the robot to the tool item. If tool is a 4x4 Matrix, it updates the linked pose of the robot tool.
        /// </summary>
        /// <param name="tool">item/pose -> tool item or 4x4 Matrix (pose of the tool frame)</param>
        public void setTool(Mat tool)
        {
            setPoseTool(tool);
        }

        /// <summary>
        /// Adds an empty tool to the robot provided the tool pose (4x4 Matrix) and the tool name.
        /// </summary>
        /// <param name="tool_pose">pose -> TCP as a 4x4 Matrix (pose of the tool frame)</param>
        /// <param name="tool_name">New tool name</param>
        /// <returns>new item created</returns>
        public Item AddTool(Mat tool_pose, string tool_name = "New TCP")
        {
            link._check_connection();
            link._send_Line("AddToolEmpty");
            link._send_Item(this);
            link._send_Pose(tool_pose);
            link._send_Line(tool_name);
            Item newtool = link._recv_Item();
            link._check_status();
            return newtool;
        }

        /// <summary>
        /// Computes the forward kinematics of the robot for the provided joints. The tool and the reference frame are not taken into account.
        /// </summary>
        /// <param name="joints"></param>
        /// <returns>4x4 homogeneous matrix: pose of the robot flange with respect to the robot base</returns>
        public Mat SolveFK(double[] joints)
        {
            link._check_connection();
            link._send_Line("G_FK");
            link._send_Array(joints);
            link._send_Item(this);
            Mat pose = link._recv_Pose();
            link._check_status();
            return pose;
        }

        /// <summary>
        /// Returns the robot configuration state for a set of robot joints.
        /// </summary>
        /// <param name="joints">array of joints</param>
        /// <returns>3-array -> configuration status as [REAR, LOWERARM, FLIP]</returns>
        public double[] JointsConfig(double[] joints)
        {
            link._check_connection();
            link._send_Line("G_Thetas_Config");
            link._send_Array(joints);
            link._send_Item(this);
            double[] config = link._recv_Array();
            link._check_status();
            return config;
        }

        /// <summary>
        /// Computes the inverse kinematics for the specified robot and pose. The joints returned are the closest to the current robot configuration (see SolveIK_All())
        /// </summary>
        /// <param name="pose">4x4 matrix -> pose of the robot flange with respect to the robot base frame</param>
        /// <param name="joints_approx">Aproximate solution. Leave empty to return the closest match to the current robot position.</param>
        /// <param name="tool">4x4 matrix -> Optionally provide a tool, otherwise, the robot flange is used. Tip: use robot.PoseTool() to retrieve the active robot tool.</param>
        /// <param name="reference">4x4 matrix -> Optionally provide a reference, otherwise, the robot base is used. Tip: use robot.PoseFrame() to retrieve the active robot reference frame.</param>
        /// <returns>array of joints</returns>
        public double[] SolveIK(Mat pose, double[] joints_approx = null, Mat tool = null, Mat reference = null)
        {
            if (tool != null)
            {
                pose = pose * tool.inv();
            }
            if (reference != null)
            {
                pose = reference * pose;
            }
            link._check_connection();
            if (joints_approx == null)
            {
                link._send_Line("G_IK");
                link._send_Pose(pose);
            }
            else
            {
                link._send_Line("G_IK_jnts");
                link._send_Pose(pose);
                link._send_Array(joints_approx);
            }
            link._send_Item(this);
            double[] joints_sol = link._recv_Array();
            link._check_status();
            return joints_sol;
        }

        /// <summary>
        /// Computes the inverse kinematics for the specified robot and pose. The function returns all available joint solutions as a 2D matrix.
        /// </summary>
        /// <param name="pose">4x4 matrix -> pose of the robot tool with respect to the robot frame</param>
        /// <param name="tool">4x4 matrix -> Optionally provide a tool, otherwise, the robot flange is used. Tip: use robot.PoseTool() to retrieve the active robot tool.</param>
        /// <param name="reference">4x4 matrix -> Optionally provide a reference, otherwise, the robot base is used. Tip: use robot.PoseFrame() to retrieve the active robot reference frame.</param>
        /// <returns>double x n x m -> joint list (2D matrix)</returns>
        public Mat SolveIK_All(Mat pose, Mat tool = null, Mat reference = null)
        {
            if (tool != null)
            {
                pose = pose * tool.inv();
            }
            if (reference != null)
            {
                pose = reference * pose;
            }
            link._check_connection();
            link._send_Line("G_IK_cmpl");
            link._send_Pose(pose);
            link._send_Item(this);
            Mat joints_list = link._recv_Matrix2D();
            link._check_status();
            return joints_list;
        }

        /// <summary>
        /// Connect to a real robot using the robot driver.
        /// </summary>
        /// <param name="robot_ip">IP of the robot to connect. Leave empty to use the one defined in RoboDK</param>
        /// <returns>status -> true if connected successfully, false if connection failed</returns>
        public bool Connect(string robot_ip = "")
        {
            link._check_connection();
            link._send_Line("Connect");
            link._send_Item(this);
            link._send_Line(robot_ip);
            int status = link._recv_Int();
            link._check_status();
            return status != 0;
        }

        /// <summary>
        /// Disconnect from a real robot (when the robot driver is used)
        /// </summary>
        /// <returns>status -> true if disconnected successfully, false if it failed. It can fail if it was previously disconnected manually for example.</returns>
        public bool Disconnect()
        {
            link._check_connection();
            link._send_Line("Disconnect");
            link._send_Item(this);
            int status = link._recv_Int();
            link._check_status();
            return status != 0;
        }

        /// <summary>
        /// Moves a robot to a specific target ("Move Joint" mode). By default, this function blocks until the robot finishes its movements.
        /// Given a target item, MoveJ can also be applied to programs and a new movement instruction will be added.
        /// </summary>
        /// <param name="target">target -> target to move to as a target item (RoboDK target item)</param>
        /// <param name="blocking">blocking -> True if we want the instruction to block until the robot finished the movement (default=true)</param>
        public void MoveJ(Item itemtarget, bool blocking = true)
        {
            if (type == ITEM_TYPE_PROGRAM)
            {
                addMoveJ(itemtarget);
            }
            else
            {
                link.moveX(itemtarget, null, null, this, 1, blocking);
            }
        }

        /// <summary>
        /// Moves a robot to a specific target ("Move Joint" mode). By default, this function blocks until the robot finishes its movements.
        /// </summary>
        /// <param name="target">joints -> joint target to move to.</param>
        /// <param name="blocking">blocking -> True if we want the instruction to block until the robot finished the movement (default=true)</param>
        public void MoveJ(double[] joints, bool blocking = true)
        {
            link.moveX(null, joints, null, this, 1, blocking);
        }

        /// <summary>
        /// Moves a robot to a specific target ("Move Joint" mode). By default, this function blocks until the robot finishes its movements.
        /// </summary>
        /// <param name="target">pose -> pose target to move to. It must be a 4x4 Homogeneous matrix</param>
        /// <param name="blocking">blocking -> True if we want the instruction to block until the robot finished the movement (default=true)</param>
        public void MoveJ(Mat target, bool blocking = true)
        {
            link.moveX(null, null, target, this, 1, blocking);
        }

        /// <summary>
        /// Moves a robot to a specific target ("Move Linear" mode). By default, this function blocks until the robot finishes its movements.
        /// Given a target item, MoveL can also be applied to programs and a new movement instruction will be added.
        /// </summary>
        /// <param name="itemtarget">target -> target to move to as a target item (RoboDK target item)</param>
        /// <param name="blocking">blocking -> True if we want the instruction to block until the robot finished the movement (default=true)</param>
        public void MoveL(Item itemtarget, bool blocking = true)
        {
            if (type == ITEM_TYPE_PROGRAM)
            {
                addMoveL(itemtarget);
            }
            else
            {
                link.moveX(itemtarget, null, null, this, 2, blocking);
            }
        }

        /// <summary>
        /// Moves a robot to a specific target ("Move Linear" mode). By default, this function blocks until the robot finishes its movements.
        /// </summary>
        /// <param name="joints">joints -> joint target to move to.</param>
        /// <param name="blocking">blocking -> True if we want the instruction to block until the robot finished the movement (default=true)</param>
        public void MoveL(double[] joints, bool blocking = true)
        {
            link.moveX(null, joints, null, this, 2, blocking);
        }

        /// <summary>
        /// Moves a robot to a specific target ("Move Linear" mode). By default, this function blocks until the robot finishes its movements.
        /// </summary>
        /// <param name="target">pose -> pose target to move to. It must be a 4x4 Homogeneous matrix</param>
        /// <param name="blocking">blocking -> True if we want the instruction to block until the robot finished the movement (default=true)</param>
        public void MoveL(Mat target, bool blocking = true)
        {
            link.moveX(null, null, target, this, 2, blocking);
        }

        /// <summary>
        /// Moves a robot to a specific target ("Move Circular" mode). By default, this function blocks until the robot finishes its movements.
        /// </summary>
        /// <param name="itemtarget1">target -> intermediate target to move to as a target item (RoboDK target item)</param>
        /// <param name="itemtarget2">target -> final target to move to as a target item (RoboDK target item)</param>
        /// <param name="blocking">blocking -> True if we want the instruction to block until the robot finished the movement (default=true)</param>
        public void MoveC(Item itemtarget1, Item itemtarget2, bool blocking = true)
        {
            link.moveC_private(itemtarget1, null, null, itemtarget2, null, null, this, blocking);
        }

        /// <summary>
        /// Moves a robot to a specific target ("Move Circular" mode). By default, this function blocks until the robot finishes its movements.
        /// </summary>
        /// <param name="joints1">joints -> intermediate joint target to move to.</param>
        /// <param name="joints2">joints -> final joint target to move to.</param>
        /// <param name="blocking">blocking -> True if we want the instruction to block until the robot finished the movement (default=true)</param>
        public void MoveC(double[] joints1, double[] joints2, bool blocking = true)
        {
            link.moveC_private(null, joints1, null, null, joints2, null, this, blocking);
        }

        /// <summary>
        /// Moves a robot to a specific target ("Move Circular" mode). By default, this function blocks until the robot finishes its movements.
        /// </summary>
        /// <param name="target1">pose -> intermediate pose target to move to. It must be a 4x4 Homogeneous matrix</param>
        /// <param name="target2">pose -> final pose target to move to. It must be a 4x4 Homogeneous matrix</param>
        /// <param name="blocking">blocking -> True if we want the instruction to block until the robot finished the movement (default=true)</param>
        public void MoveC(Mat target1, Mat target2, bool blocking = true)
        {
            link.moveC_private(null, null, target1, null, null, target2, this, blocking);
        }

        /// <summary>
        /// Checks if a joint movement is free of collision.
        /// </summary>
        /// <param name="j1">joints -> start joints</param>
        /// <param name="j2">joints -> destination joints</param>
        /// <param name="minstep_deg">(optional): maximum joint step in degrees</param>
        /// <returns>collision : returns 0 if the movement is free of collision. Otherwise it returns the number of pairs of objects that collided if there was a collision.</returns>
        public int MoveJ_Test(double[] j1, double[] j2, double minstep_deg = -1)
        {
            link._check_connection();
            link._send_Line("CollisionMove");
            link._send_Item(this);
            link._send_Array(j1);
            link._send_Array(j2);
            link._send_Int((int)(minstep_deg * 1000.0));
            link._COM.ReceiveTimeout = 3600 * 1000;
            int collision = link._recv_Int();
            link._COM.ReceiveTimeout = link._TIMEOUT;
            link._check_status();
            return collision;
        }

        /// <summary>
        /// Checks if a joint movement is free of collision.
        /// </summary>
        /// <param name="j1">joints -> start joints</param>
        /// <param name="j2">joints -> joints via</param>
        /// <param name="j3">joints -> joints final destination</param>
        /// <param name="blend_deg">Blend in degrees</param>
        /// <param name="minstep_deg">(optional): maximum joint step in degrees</param>
        /// <returns>collision : returns false if the movement is possible and free of collision. Otherwise it returns true.</returns>
        public bool MoveJ_Test_Blend(double[] j1, double[] j2, double[] j3, double blend_deg = 5, double minstep_deg = -1)
        {
            link._require_build(7206);
            link._check_connection();
            link._send_Line("CollisionMoveBlend");
            link._send_Item(this);
            link._send_Array(j1);
            link._send_Array(j2);
            link._send_Array(j3);
            link._send_Int((int)(minstep_deg * 1000.0));
            link._send_Int((int)(blend_deg * 1000.0));
            link._COM.ReceiveTimeout = 3600 * 1000;
            int collision = link._recv_Int();
            link._COM.ReceiveTimeout = link._TIMEOUT;
            link._check_status();
            return collision != 0;
        }

        /// <summary>
        /// Checks if a linear movement is free of collision.
        /// </summary>
        /// <param name="j1">joints -> start joints</param>
        /// <param name="pose2">pose -> destination pose (active tool with respect to the active reference frame)</param>
        /// <param name="minstep_mm">(optional): maximum joint step in mm</param>
        /// <returns>collision : returns 0 if the movement is free of collision. Otherwise it returns the number of pairs of objects that collided if there was a collision.</returns>
        public int MoveL_Test(double[] j1, Mat pose2, double minstep_mm = -1)
        {
            link._check_connection();
            link._send_Line("CollisionMoveL");
            link._send_Item(this);
            link._send_Array(j1);
            link._send_Pose(pose2);
            link._send_Int((int)(minstep_mm * 1000.0));
            link._COM.ReceiveTimeout = 3600 * 1000;
            int collision = link._recv_Int();
            link._COM.ReceiveTimeout = link._TIMEOUT;
            link._check_status();
            return collision;
        }

        /// <summary>
        /// Sets the speed and/or the acceleration of a robot.
        /// </summary>
        /// <param name="speed">speed -> speed in mm/s (-1 = no change)</param>
        /// <param name="accel">acceleration (optional) -> acceleration in mm/s2 (-1 = no change)</param>
        /*
        public void setSpeed(double speed, double accel = -1)
        {
            link._check_connection();
            link._send_Line("S_Speed");
            link._send_Int((int)(speed * 1000.0));
            link._send_Int((int)(accel * 1000.0));
            link._send_Item(this);
            link._check_status();

        }*/

        /// <summary>
        /// Sets the speed and/or the acceleration of a robot.
        /// </summary>
        /// <param name="speed_linear">linear speed in mm/s (-1 = no change)</param>
        /// <param name="accel_linear">linear acceleration in mm/s2 (-1 = no change)</param>
        /// <param name="speed_joints">joint speed in deg/s (-1 = no change)</param>
        /// <param name="accel_joints">joint acceleration in deg/s2 (-1 = no change)</param>
        public void setSpeed(double speed_linear, double accel_linear = -1, double speed_joints = -1, double accel_joints = -1)
        {
            link._check_connection();
            link._send_Line("S_Speed4");
            link._send_Item(this);
            double[] speed_accel = new double[4];
            speed_accel[0] = speed_linear;
            speed_accel[1] = accel_linear;
            speed_accel[2] = speed_joints;
            speed_accel[3] = accel_joints;
            link._send_Array(speed_accel);
            link._check_status();

        }

        /// <summary>
        /// Sets the robot movement smoothing accuracy (also known as zone data value).
        /// </summary>
        /// <param name="rounding_mm">Rounding value (double) (robot dependent, set to -1 for accurate/fine movements)</param>
        public void setRounding(double rounding_mm)
        {
            link._check_connection();
            link._send_Line("S_ZoneData");
            link._send_Int((int)(rounding_mm * 1000.0));
            link._send_Item(this);
            link._check_status();
        }
        /// <summary>
        /// Obsolete, use setRounding instead
        /// </summary>
        public void setZoneData(double rounding_mm)
        {
            setRounding(rounding_mm);
        }

        /// <summary>
        /// Displays a sequence of joints
        /// </summary>
        /// <param name="sequence">joint sequence as a 6xN matrix or instruction sequence as a 7xN matrix</param>
        public void ShowSequence(Mat sequence)
        {
            link._check_connection();
            link._send_Line("Show_Seq");
            link._send_Matrix2D(sequence);
            link._send_Item(this);
            link._check_status();
        }


        /// <summary>
        /// Checks if a robot or program is currently running (busy or moving)
        /// </summary>
        /// <returns>busy status (true=moving, false=stopped)</returns>
        public bool Busy()
        {
            link._check_connection();
            link._send_Line("IsBusy");
            link._send_Item(this);
            int busy = link._recv_Int();
            link._check_status();
            return (busy > 0);
        }

        /// <summary>
        /// Stops a program or a robot
        /// </summary>
        /// <returns></returns>
        public void Stop()
        {
            link._check_connection();
            link._send_Line("Stop");
            link._send_Item(this);
            link._check_status();
        }

        /// <summary>
        /// Waits (blocks) until the robot finishes its movement.
        /// </summary>
        /// <param name="timeout_sec">timeout -> Max time to wait for robot to finish its movement (in seconds)</param>
        public void WaitMove(double timeout_sec = 300)
        {
            link._check_connection();
            link._send_Line("WaitMove");
            link._send_Item(this);
            link._check_status();
            link._COM.ReceiveTimeout = (int)(timeout_sec * 1000.0);
            link._check_status();//will wait here;
            link._COM.ReceiveTimeout = link._TIMEOUT;
            //int isbusy = link.Busy(this);
            //while (isbusy)
            //{
            //    busy = link.Busy(item);
            //}
        }

        ///////// ADD MORE METHODS


        // ---- Program item calls -----

        /// <summary>
        /// Sets the accuracy of the robot active or inactive. A robot must have been calibrated to properly use this option.
        /// </summary>
        /// <param name="accurate">set to 1 to use the accurate model or 0 to use the nominal model</param>
        public void setAccuracyActive(int accurate = 1)
        {
            link._check_connection();
            link._send_Line("S_AbsAccOn");
            link._send_Item(this);
            link._send_Int(accurate);
            link._check_status();
        }

        /// <summary>
        /// Saves a program to a file.
        /// </summary>
        /// <param name="filename">File path of the program</param>
        /// <param name="run_mode">RUNMODE_MAKE_ROBOTPROG to generate the program file.Alternatively, Use RUNMODE_MAKE_ROBOTPROG_AND_UPLOAD or RUNMODE_MAKE_ROBOTPROG_AND_START to transfer the program through FTP and execute the program.</param>
        /// <returns>Transfer succeeded is True if there was a successful program transfer (if RUNMODE_MAKE_ROBOTPROG_AND_UPLOAD or RUNMODE_MAKE_ROBOTPROG_AND_START are used)</returns>
        public bool MakeProgram(string filename = "", int run_mode = RUNMODE_MAKE_ROBOTPROG)
        {
            link._check_connection();
            link._send_Line("MakeProg2");
            link._send_Item(this);
            link._send_Line(filename);
            link._send_Int(run_mode);
            link._COM.ReceiveTimeout = 3600 * 1000;
            int prog_status = link._recv_Int();
            link._COM.ReceiveTimeout = link._TIMEOUT;
            string prog_log_str = link._recv_Line();
            int transfer_status = link._recv_Int();
            link._check_status();
            link.LAST_STATUS_MESSAGE = prog_log_str;
            bool success = prog_status > 0;
            bool transfer_ok = transfer_status > 0;
            return success && transfer_ok; // prog_log_str
            //return success, prog_log_str, transfer_ok
        }

        /// <summary>
        /// Sets if the program will be run in simulation mode or on the real robot.
        /// Use: "PROGRAM_RUN_ON_SIMULATOR" to set the program to run on the simulator only or "PROGRAM_RUN_ON_ROBOT" to force the program to run on the robot.
        /// </summary>
        /// <returns>number of instructions that can be executed</returns>
        public void setRunType(int program_run_type)
        {
            link._check_connection();
            link._send_Line("S_ProgRunType");
            link._send_Item(this);
            link._send_Int(program_run_type);
            link._check_status();
        }

        /// <summary>
        /// Runs a program. It returns the number of instructions that can be executed successfully (a quick program check is performed before the program starts)
        /// This is a non-blocking call. Use IsBusy() to check if the program execution finished.
        /// Notes:
        /// if setRunMode(RUNMODE_SIMULATE) is used  -> the program will be simulated (default run mode)
        /// if setRunMode(RUNMODE_RUN_ROBOT) is used -> the program will run on the robot (default when RUNMODE_RUN_ROBOT is used)
        /// if setRunMode(RUNMODE_RUN_ROBOT) is used together with program.setRunType(PROGRAM_RUN_ON_ROBOT) -> the program will run sequentially on the robot the same way as if we right clicked the program and selected "Run on robot" in the RoboDK GUI        
        /// </summary>
        /// <returns>number of instructions that can be executed</returns>
        public int RunProgram()
        {
            link._check_connection();
            link._send_Line("RunProg");
            link._send_Item(this);
            int prog_status = link._recv_Int();
            link._check_status();
            return prog_status;
        }


        /// <summary>
        /// Runs a program. It returns the number of instructions that can be executed successfully (a quick program check is performed before the program starts)
        /// Program parameters can be provided for Python calls.
        /// This is a non-blocking call.Use IsBusy() to check if the program execution finished.
        /// Notes: if setRunMode(RUNMODE_SIMULATE) is used  -> the program will be simulated (default run mode)
        /// if setRunMode(RUNMODE_RUN_ROBOT) is used ->the program will run on the robot(default when RUNMODE_RUN_ROBOT is used)
        /// if setRunMode(RUNMODE_RUN_ROBOT) is used together with program.setRunType(PROGRAM_RUN_ON_ROBOT) -> the program will run sequentially on the robot the same way as if we right clicked the program and selected "Run on robot" in the RoboDK GUI
        /// </summary>
        /// <param name="parameters">Number of instructions that can be executed</param>
        public int RunCode(string parameters = null)
        {
            link._check_connection();
            if (parameters == null)
            {
                link._send_Line("RunProg");
                link._send_Item(this);
            }
            else
            {
                link._send_Line("RunProgParam");
                link._send_Item(this);
                link._send_Line(parameters);
            }
            int progstatus = link._recv_Int();
            link._check_status();
            return progstatus;
        }

        /// <summary>
        /// Adds a program call, code, message or comment inside a program.
        /// </summary>
        /// <param name="code"><string of the code or program to run/param>
        /// <param name="run_type">INSTRUCTION_* variable to specify if the code is a progra</param>
        public int RunInstruction(string code, int run_type = INSTRUCTION_CALL_PROGRAM)
        {
            link._check_connection();
            link._send_Line("RunCode2");
            link._send_Item(this);
            link._send_Line(code.Replace("\n\n", "<br>").Replace("\n", "<br>"));
            link._send_Int(run_type);
            int progstatus = link._recv_Int();
            link._check_status();
            return progstatus;
        }

        /// <summary>
        /// (obsolete, use RunInstruction instead). Adds a program call, code, message or comment inside a program
        /// </summary>
        /// <param name="code"><string of the code or program to run/param>
        /// <param name="run_type">INSTRUCTION_* variable to specify if the code is a progra</param>
        public int RunCodeCustom(string code, int run_type = INSTRUCTION_CALL_PROGRAM)
        {
            return RunInstruction(code, run_type);
        }

        /// <summary>
        /// Generates a pause instruction for a robot or a program when generating code. Set it to -1 (default) if you want the robot to stop and let the user resume the program anytime.
        /// </summary>
        /// <param name="time_ms">Time in milliseconds</param>
        public void Pause(double time_ms = -1)
        {
            link._check_connection();
            link._send_Line("RunPause");
            link._send_Item(this);
            link._send_Int((int)(time_ms * 1000.0));
            link._check_status();
        }


        /// <summary>
        /// Sets a variable (output) to a given value. This can also be used to set any variables to a desired value.
        /// </summary>
        /// <param name="io_var">io_var -> digital output (string or number)</param>
        /// <param name="io_value">io_value -> value (string or number)</param>
        public void setDO(string io_var, string io_value)
        {
            link._check_connection();
            link._send_Line("setDO");
            link._send_Item(this);
            link._send_Line(io_var);
            link._send_Line(io_value);
            link._check_status();
        }

        /// <summary>
        /// Waits for an input io_id to attain a given value io_value. Optionally, a timeout can be provided.
        /// </summary>
        /// <param name="io_var">io_var -> digital output (string or number)</param>
        /// <param name="io_value">io_value -> value (string or number)</param>
        /// <param name="timeout_ms">int (optional) -> timeout in miliseconds</param>
        public void waitDI(string io_var, string io_value, double timeout_ms = -1)
        {
            link._check_connection();
            link._send_Line("waitDI");
            link._send_Item(this);
            link._send_Line(io_var);
            link._send_Line(io_value);
            link._send_Int((int)(timeout_ms * 1000.0));
            link._check_status();
        }

        /// <summary>
        /// Add a custom instruction. This instruction will execute a Python file or an executable file.
        /// </summary>
        /// <param name="name"></param>
        /// <param name="path_run">path to run(relative to RoboDK/bin folder or absolute path)</param>
        /// <param name="path_icon">icon path(relative to RoboDK/bin folder or absolute path)</param>
        /// <param name="blocking">True if blocking, 0 if it is a non blocking executable trigger</param>
        /// <param name="cmd_run_on_robot">Command to run through the driver when connected to the robot</param>
        /// :param name: digital input (string or number)
        public void customInstruction(string name, string path_run, string path_icon = "", bool blocking = true, string cmd_run_on_robot = "")
        {
            link._check_connection();
            link._send_Line("InsCustom2");
            link._send_Item(this);
            link._send_Line(name);
            link._send_Line(path_run);
            link._send_Line(path_icon);
            link._send_Line(cmd_run_on_robot);
            link._send_Int(blocking ? 1 : 0);
            link._check_status();
        }

        /// <summary>
        /// Adds a new robot move joint instruction to a program. Obsolete. Use MoveJ instead.
        /// </summary>
        /// <param name="itemtarget">target to move to</param>
        public void addMoveJ(Item itemtarget)
        {
            link._check_connection();
            link._send_Line("Add_INSMOVE");
            link._send_Item(itemtarget);
            link._send_Item(this);
            link._send_Int(1);
            link._check_status();
        }

        /// <summary>
        /// Adds a new robot move linear instruction to a program. Obsolete. Use MoveJ instead.
        /// </summary>
        /// <param name="itemtarget">target to move to</param>
        public void addMoveL(Item itemtarget)
        {
            link._check_connection();
            link._send_Line("Add_INSMOVE");
            link._send_Item(itemtarget);
            link._send_Item(this);
            link._send_Int(2);
            link._check_status();
        }

        ////////// ADD MORE METHODS

        /// <summary>
        /// Show or hide instruction items of a program in the RoboDK tree
        /// </summary>
        /// <param name="show"></param>
        public void ShowInstructions(bool show = true)
        {
            link._check_connection();
            link._send_Line("Prog_ShowIns");
            link._send_Item(this);
            link._send_Int(show ? 1 : 0);
            link._check_status();
        }

        /// <summary>
        /// Show or hide targets of a program in the RoboDK tree
        /// </summary>
        /// <param name="show"></param>
        public void ShowTargets(bool show = true)
        {
            link._check_connection();
            link._send_Line("Prog_ShowTargets");
            link._send_Item(this);
            link._send_Int(show ? 1 : 0);
            link._check_status();
        }

        /// <summary>
        /// Returns the number of instructions of a program.
        /// </summary>
        /// <returns></returns>
        public int InstructionCount()
        {
            link._check_connection();
            link._send_Line("Prog_Nins");
            link._send_Item(this);
            int nins = link._recv_Int();
            link._check_status();
            return nins;
        }

        /// <summary>
        /// Returns the program instruction at position id
        /// </summary>
        /// <param name="ins_id"></param>
        /// <param name="name"></param>
        /// <param name="instype"></param>
        /// <param name="movetype"></param>
        /// <param name="isjointtarget"></param>
        /// <param name="target"></param>
        /// <param name="joints"></param>
        public void Instruction(int ins_id, out string name, out int instype, out int movetype, out bool isjointtarget, out Mat target, out double[] joints)
        {
            link._check_connection();
            link._send_Line("Prog_GIns");
            link._send_Item(this);
            link._send_Int(ins_id);
            name = link._recv_Line();
            instype = link._recv_Int();
            movetype = 0;
            isjointtarget = false;
            target = null;
            joints = null;
            if (instype == INS_TYPE_MOVE)
            {
                movetype = link._recv_Int();
                isjointtarget = link._recv_Int() > 0 ? true : false;
                target = link._recv_Pose();
                joints = link._recv_Array();
            }
            link._check_status();
        }

        /// <summary>
        /// Sets the program instruction at position id
        /// </summary>
        /// <param name="ins_id"></param>
        /// <param name="name"></param>
        /// <param name="instype"></param>
        /// <param name="movetype"></param>
        /// <param name="isjointtarget"></param>
        /// <param name="target"></param>
        /// <param name="joints"></param>
        public void setInstruction(int ins_id, string name, int instype, int movetype, bool isjointtarget, Mat target, double[] joints)
        {
            link._check_connection();
            link._send_Line("Prog_SIns");
            link._send_Item(this);
            link._send_Int(ins_id);
            link._send_Line(name);
            link._send_Int(instype);
            if (instype == INS_TYPE_MOVE)
            {
                link._send_Int(movetype);
                link._send_Int(isjointtarget ? 1 : 0);
                link._send_Pose(target);
                link._send_Array(joints);
            }
            link._check_status();
        }


        /// <summary>
        /// Returns the list of program instructions as an MxN matrix, where N is the number of instructions and M equals to 1 plus the number of robot axes.
        /// </summary>
        /// <param name="instructions">the matrix of instructions</param>
        /// <returns>Returns 0 if success</returns>
        public int InstructionList(out Mat instructions)
        {
            link._check_connection();
            link._send_Line("G_ProgInsList");
            link._send_Item(this);
            instructions = link._recv_Matrix2D();
            int errors = link._recv_Int();
            link._check_status();
            return errors;
        }

        /// <summary>
        /// Updates a program and returns the estimated time and the number of valid instructions.
        /// An update can also be applied to a robot machining project. The update is performed on the generated program.
        /// </summary>
        /// <param name="collision_check">check_collisions: Check collisions (COLLISION_ON -yes- or COLLISION_OFF -no-)</param>
        /// <param name="timeout_sec">Maximum time to wait for the update to complete (in seconds)</param>
        /// <param name="out_nins_time_dist">optional double array [3] = [valid_instructions, program_time, program_distance]</param>
        /// <param name="mm_step">Maximum step in millimeters for linear movements (millimeters). Set to -1 to use the default, as specified in Tools-Options-Motion.</param>
        /// <param name="deg_step">Maximum step for joint movements (degrees). Set to -1 to use the default, as specified in Tools-Options-Motion.</param>
        /// <returns>1.0 if there are no problems with the path or less than 1.0 if there is a problem in the path (ratio of problem)</returns>
        public double Update(int collision_check = COLLISION_OFF, int timeout_sec = 3600, double[] out_nins_time_dist = null, double mm_step = -1, double deg_step = -1)
        {
            link._check_connection();
            link._send_Line("Update2");
            link._send_Item(this);
            double[] values = { collision_check, mm_step, deg_step };
            link._send_Array(values);
            link._COM.ReceiveTimeout = timeout_sec * 1000;
            double[] return_values = link._recv_Array();
            link._COM.ReceiveTimeout = link._TIMEOUT;
            string readable_msg = link._recv_Line();
            link._check_status();
            link.LAST_STATUS_MESSAGE = readable_msg;
            double ratio_ok = return_values[3];
            if (out_nins_time_dist != null)
            {
                out_nins_time_dist[0] = return_values[0];
                out_nins_time_dist[1] = return_values[1];
                out_nins_time_dist[2] = return_values[2];
            }
            return ratio_ok;
        }



        /// <summary>
        /// Returns a list of joints an MxN matrix, where M is the number of robot axes plus 4 columns. Linear moves are rounded according to the smoothing parameter set inside the program.
        /// </summary>
        /// <param name="error_msg">Returns a human readable error message (if any)</param>
        /// <param name="joint_list">Returns the list of joints as [J1, J2, ..., Jn, ERROR, MM_STEP, DEG_STEP, MOVE_ID] if a file name is not specified.
        /// If flags == LISTJOINTS_SPEED: [J1, J2, ..., Jn, ERROR, MM_STEP, DEG_STEP, MOVE_ID,   TIME, X_TCP, Y_TCP, Z_TCP,  Speed_J1, Speed_J2, ..., Speed_Jn] 
        /// If flags == LISTJOINTS_ACCEL: [J1, J2, ..., Jn, ERROR, MM_STEP, DEG_STEP, MOVE_ID,   TIME, X_TCP, Y_TCP, Z_TCP,  Speed_J1, Speed_J2, ..., Speed_Jn,   Accel_J1, Accel_J2, ..., Accel_Jn] </param>
        /// <param name="mm_step">Maximum step in millimeters for linear movements (millimeters)</param>
        /// <param name="deg_step">Maximum step for joint movements (degrees)</param>
        /// <param name="save_to_file">Provide a file name to directly save the output to a file. If the file name is not provided it will return the matrix. If step values are very small, the returned matrix can be very large.</param>
        /// <param name="collision_check">Check for collisions: will set to 1 or 0</param>
        /// <param name="flags">set to 1 to include the timings between movements, set to 2 to also include the joint speeds (deg/s), set to 3 to also include the accelerations, set to 4 to include all previous information and also make it time-based</param>
        /// <param name="timeout_sec">Maximum time to wait for the result (seconds)</param>
        /// <param name="time_step">Time step in seconds for time-based calculation (only used if the flag is set to 4)</param>
        /// <returns>Returns 0 if success, otherwise, it will return negative values</returns>
        public int InstructionListJoints(out string error_msg, out Mat joint_list, double mm_step = 10.0, double deg_step = 5.0, string save_to_file = "", int collision_check = COLLISION_OFF, int flags = 0, int timeout_sec = 3600, double time_step = 0.2)
        {
            link._check_connection();
            link._send_Line("G_ProgJointList");
            link._send_Item(this);
            double[] ste_mm_deg = { mm_step, deg_step, collision_check, flags, time_step };
            link._send_Array(ste_mm_deg);
            //joint_list = save_to_file;
            link._COM.ReceiveTimeout = 3600 * 1000;
            if (save_to_file.Length <= 0)
            {
                link._send_Line("");
                joint_list = link._recv_Matrix2D();
            }
            else
            {
                link._send_Line(save_to_file);
                joint_list = null;
            }

            int error_code = link._recv_Int();
            link._COM.ReceiveTimeout = link._TIMEOUT;
            error_msg = link._recv_Line();
            link._check_status();
            return error_code;
        }

        /// <summary>
        /// Disconnect from the RoboDK API. This flushes any pending program generation.
        /// </summary>
        /// <returns></returns>
        public bool Finish()
        {
            return link.Finish();
        }

        /// <summary>
        /// Send a specific parameter to RoboDK. This is reserved for internal purposes.
        /// </summary>
        /// <param name="param">Item parameter</param>
        /// <param name="value">value</param>
        /// <returns></returns>
        public string setParam(string param, string value = "")
        {
            link._require_build(7129);
            link._check_connection();
            link._send_Line("ICMD");
            link._send_Item(this);
            link._send_Line(param);
            link._send_Line(value);
            string response = link._recv_Line();
            link._check_status();
            return response;
        }
    }

}

