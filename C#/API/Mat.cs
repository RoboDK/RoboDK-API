// ----------------------------------------------------------------------------------------------------------
// Copyright 2018 - RoboDK Inc. - https://robodk.com/
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
// http://www.apache.org/licenses/LICENSE-2.0
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
// ----------------------------------------------------------------------------------------------------------

// ----------------------------------------------------------------------------------------------------------
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
//     https://robodk.com/doc/en/CsAPI/index.html
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
// ----------------------------------------------------------------------------------------------------------

#region Namespaces

using System;
using RoboDk.API.Exceptions;

#endregion

namespace RoboDk.API
{
    /// <summary>
    /// Matrix class for robotics.
    /// Simple matrix class for homogeneous operations.
    /// </summary>
    public partial class Mat 
    {
        #region Fields

        private int _rows;
        private int _cols;
        private readonly double[,] _mat;

        public Mat L;
        public Mat U;

        #endregion

        #region Constructors

        /// <summary>
        ///     Matrix class constructor for any size matrix
        /// </summary>
        /// <param name="rows">dimension 1 size (rows)</param>
        /// <param name="cols">dimension 2 size (columns)</param>
        public Mat(int rows, int cols) // Matrix Class constructor
        {
            _rows = rows;
            _cols = cols;
            _mat = new double[_rows, _cols];
        }


        /// <summary>
        /// Matrix class constructor for a double array. The array will be set as a column matrix.
        /// Example:
        ///     RDK.AddCurve(new Mat(new double[6] {{0,0,0, 0,0,1}}));
        /// </summary>
        /// <param name="point">Column array</param>
        /// <param name="isPose">if isPose is True then convert vector into a 4x4 Pose Matrix.</param>
        public Mat(double[] point, bool isPose = false)
        {
            if (isPose)
            {
                _cols = 4;
                _rows = 4;
                if (point.GetLength(0) < 16)
                {
                    throw new MatException("Invalid array size to create a pose Mat"); //raise Exception('Problems running function');
                }

                // Convert a double array of arrays to a Mat object:
                _mat = new double[_rows, _cols];
                for (var r = 0; r < _rows; r++)
                {
                    for (var c = 0; r < _rows; r++)
                    {
                        _mat[r, c] = point[r + c * 4];
                    }
                }
            }
            else
            {
                _cols = 1;
                _rows = point.GetLength(0);

                // Convert a double array of arrays to a Mat object:
                _mat = new double[_rows, _cols];
                for (int r = 0; r < _rows; r++)
                {
                    _mat[r, 1] = point[r];
                }
            }

        }

        /// <summary>
        ///     Matrix class constructor for a 4x4 homogeneous matrix
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
        public Mat(double nx, double ox, double ax, double tx, double ny, double oy, double ay, double ty, double nz,
            double oz, double az, double tz) // Matrix Class constructor
        {
            _rows = 4;
            _cols = 4;
            _mat = new double[_rows, _cols];
            _mat[0, 0] = nx;
            _mat[1, 0] = ny;
            _mat[2, 0] = nz;
            _mat[0, 1] = ox;
            _mat[1, 1] = oy;
            _mat[2, 1] = oz;
            _mat[0, 2] = ax;
            _mat[1, 2] = ay;
            _mat[2, 2] = az;
            _mat[0, 3] = tx;
            _mat[1, 3] = ty;
            _mat[2, 3] = tz;
            _mat[3, 0] = 0.0;
            _mat[3, 1] = 0.0;
            _mat[3, 2] = 0.0;
            _mat[3, 3] = 1.0;
        }

        /// <summary>
        ///     Matrix class constructor for a 4x4 homogeneous matrix as a copy from another matrix
        /// </summary>
        public Mat(Mat pose)
        {
            _rows = pose._rows;
            _cols = pose._cols;
            _mat = new double[_rows, _cols];
            for (var i = 0; i < _rows; i++)
            for (var j = 0; j < _cols; j++)
                _mat[i, j] = pose[i, j];
        }

        /// <summary>
        ///     Matrix class constructor for a 4x1 vector [x,y,z,1]
        /// </summary>
        /// <param name="x">x coordinate</param>
        /// <param name="y">y coordinate</param>
        /// <param name="z">z coordinate</param>
        public Mat(double x, double y, double z)
        {
            _rows = 4;
            _cols = 1;
            _mat = new double[_rows, _cols];
            _mat[0, 0] = x;
            _mat[1, 0] = y;
            _mat[2, 0] = z;
            _mat[3, 0] = 1.0;
        }

        /// <summary>
        /// Matrix class constructor for a double array of arrays or a single column array (list of points)
        /// Example:
        ///     RDK.AddCurve(new Mat(new double[4, 6] {{0,0,0, 0,0,1}, { 500, 0, 0, 0, 0, 1 }, { 500, 500, 0, 0, 0, 1 }, { 0, 0, 0, 0, 0, 1 } }));
        ///     RDK.AddPoints(new Mat(new double[6] {{0,0,0, 0,0,1}}));
        /// </summary>
        /// <param name="point_list">List of points (array of array of doubles)</param>
        public Mat(double[,] point_list)
        {
            if (point_list.Rank == 2)
            {
                _cols = point_list.GetLength(0);
                _rows = point_list.GetLength(1);

                // Convert a double array of arrays to a Mat object:
                _mat = new double[_rows, _cols];
                for (int c = 0; c < _cols; c++)
                {
                    for (int r = 0; r < _rows; r++)
                    {
                        _mat[r, c] = point_list[c, r];
                    }
                }
            } else if (point_list.Rank == 1)
            {
                _cols = 1;
                _rows = point_list.GetLength(0);

                // Convert a double array of arrays to a Mat object:
                _mat = new double[_rows, _cols];
                for (int r = 0; r < _rows; r++)
                {
                    _mat[r, 1] = point_list[0,r];
                }
            } else
            {
                throw new MatException("Invalid rank size. Provide a 1-dimensional or 2-dimensional double array to create a Mat.");
            }
        }

        #endregion

        #region Properties

        public int Rows => _rows;

        public int Cols => _cols;

        public double this[int iRow, int iCol] // Access this matrix as a 2D array
        {
            get { return _mat[iRow, iCol]; }
            set { _mat[iRow, iCol] = value; }
        }

        #endregion

        #region Public Methods

        //----------------------------------------------------
        //--------     Generic matrix usage    ---------------
        /// <summary>
        ///     Return a translation matrix
        ///     |  1   0   0   X |
        ///     transl(X,Y,Z) = |  0   1   0   Y |
        ///     |  0   0   1   Z |
        ///     |  0   0   0   1 |
        /// </summary>
        /// <param name="x">translation along X (mm)</param>
        /// <param name="y">translation along Y (mm)</param>
        /// <param name="z">translation along Z (mm)</param>
        /// <returns></returns>
        public static Mat transl(double x, double y, double z)
        {
            var mat = IdentityMatrix(4, 4);
            mat.setPos(x, y, z);
            return mat;
        }

        /// <summary>
        ///     Return a X-axis rotation matrix
        ///     |  1  0        0        0 |
        ///     rotx(rx) = |  0  cos(rx) -sin(rx)  0 |
        ///     |  0  sin(rx)  cos(rx)  0 |
        ///     |  0  0        0        1 |
        /// </summary>
        /// <param name="rx">rotation around X axis (in radians)</param>
        /// <returns></returns>
        public static Mat rotx(double rx)
        {
            var cx = Math.Cos(rx);
            var sx = Math.Sin(rx);
            return new Mat(1, 0, 0, 0, 0, cx, -sx, 0, 0, sx, cx, 0);
        }

        /// <summary>
        ///     Return a Y-axis rotation matrix
        ///     |  cos(ry)  0   sin(ry)  0 |
        ///     roty(ry) = |  0        1   0        0 |
        ///     | -sin(ry)  0   cos(ry)  0 |
        ///     |  0        0   0        1 |
        /// </summary>
        /// <param name="ry">rotation around Y axis (in radians)</param>
        /// <returns></returns>
        public static Mat roty(double ry)
        {
            var cy = Math.Cos(ry);
            var sy = Math.Sin(ry);
            return new Mat(cy, 0, sy, 0, 0, 1, 0, 0, -sy, 0, cy, 0);
        }

        /// <summary>
        ///     Return a Z-axis rotation matrix
        ///     |  cos(rz)  -sin(rz)   0   0 |
        ///     rotz(rx) = |  sin(rz)   cos(rz)   0   0 |
        ///     |  0         0         1   0 |
        ///     |  0         0         0   1 |
        /// </summary>
        /// <param name="rz">rotation around Z axis (in radians)</param>
        /// <returns></returns>
        public static Mat rotz(double rz)
        {
            var cz = Math.Cos(rz);
            var sz = Math.Sin(rz);
            return new Mat(cz, -sz, 0, 0, sz, cz, 0, 0, 0, 0, 1, 0);
        }

        /// <summary>
        /// Check if it is a Homogeneous Identity matrix
        /// </summary>
        /// <returns></returns>
        public bool isIdentity()
        {
            if (this.Cols != 4 || this.Rows != this.Cols)
                return false;

            for (int i = 0; i < Rows; i++)
            {
                if (_mat[i, i] != 1.0)
                    return false;

            }
            if (_mat[0, 3] != 0.0 || _mat[1, 3] != 0.0 || _mat[2, 3] != 0.0)
                return false;

            return true;
        }


        //----------------------------------------------------
        //------ Pose to xyzrpw and xyzrpw to pose------------
        /// <summary>
        ///     Calculates the equivalent position and euler angles ([x,y,z,r,p,w] vector) of the given pose
        ///     Note: transl(x,y,z)*rotz(w*pi/180)*roty(p*pi/180)*rotx(r*pi/180)
        ///     See also: FromXYZRPW()
        /// </summary>
        /// <returns>XYZWPR translation and rotation in mm and degrees</returns>
        public double[] ToXYZRPW()
        {
            var xyzwpr = new double[6];
            var x = _mat[0, 3];
            var y = _mat[1, 3];
            var z = _mat[2, 3];
            double w, p, r;
            if (_mat[2, 0] > 1.0 - 1e-6)
            {
                p = -Math.PI * 0.5;
                r = 0;
                w = Math.Atan2(-_mat[1, 2], _mat[1, 1]);
            }
            else if (_mat[2, 0] < -1.0 + 1e-6)
            {
                p = 0.5 * Math.PI;
                r = 0;
                w = Math.Atan2(_mat[1, 2], _mat[1, 1]);
            }
            else
            {
                p = Math.Atan2(-_mat[2, 0], Math.Sqrt(_mat[0, 0] * _mat[0, 0] + _mat[1, 0] * _mat[1, 0]));
                w = Math.Atan2(_mat[1, 0], _mat[0, 0]);
                r = Math.Atan2(_mat[2, 1], _mat[2, 2]);
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
        ///     Calculates the pose from the position and euler angles ([x,y,z,r,p,w] vector)
        ///     The result is the same as calling: H = transl(x,y,z)*rotz(w*pi/180)*roty(p*pi/180)*rotx(r*pi/180)
        /// </summary>
        /// <param name="x"></param>
        /// <param name="y"></param>
        /// <param name="z"></param>
        /// <param name="w"></param>
        /// <param name="p"></param>
        /// <param name="r"></param>
        /// <returns>Homogeneous matrix (4x4)</returns>
        public static Mat FromXYZRPW(double x, double y, double z, double w, double p, double r)
        {
            var a = r * Math.PI / 180.0;
            var b = p * Math.PI / 180.0;
            var c = w * Math.PI / 180.0;
            var ca = Math.Cos(a);
            var sa = Math.Sin(a);
            var cb = Math.Cos(b);
            var sb = Math.Sin(b);
            var cc = Math.Cos(c);
            var sc = Math.Sin(c);
            return new Mat(cb * cc, cc * sa * sb - ca * sc, sa * sc + ca * cc * sb, x, cb * sc, ca * cc + sa * sb * sc,
                ca * sb * sc - cc * sa, y, -sb, cb * sa, ca * cb, z);
        }

        /// <summary>
        ///     Calculates the pose from the position and euler angles ([x,y,z,r,p,w] vector)
        /// </summary>
        /// <param name="xyzwpr"></param>
        /// <returns>Homogeneous matrix (4x4)</returns>
        public static Mat FromXYZRPW(double[] xyzwpr)
        {
            if (xyzwpr.Length < 6)
                return null;
            return FromXYZRPW(xyzwpr[0], xyzwpr[1], xyzwpr[2], xyzwpr[3], xyzwpr[4], xyzwpr[5]);
        }

        /// <summary>
        ///     Calculates the pose from the position and euler angles ([x,y,z,rx,ry,rz] array)
        ///     The result is the same as calling: H = transl(x,y,z)*rotx(rx*pi/180)*roty(ry*pi/180)*rotz(rz*pi/180)
        /// </summary>
        /// <param name="x"></param>
        /// <param name="y"></param>
        /// <param name="z"></param>
        /// <param name="rx"></param>
        /// <param name="ry"></param>
        /// <param name="rz"></param>
        /// <returns>Homogeneous matrix (4x4)</returns>
        public static Mat FromTxyzRxyz(double x, double y, double z, double rx, double ry, double rz)
        {
            var a = rx * Math.PI / 180.0;
            var b = ry * Math.PI / 180.0;
            var c = rz * Math.PI / 180.0;
            var crx = Math.Cos(a);
            var srx = Math.Sin(a);
            var cry = Math.Cos(b);
            var sry = Math.Sin(b);
            var crz = Math.Cos(c);
            var srz = Math.Sin(c);
            return new Mat(cry * crz, -cry * srz, sry, x, crx * srz + crz * srx * sry, crx * crz - srx * sry * srz,
                -cry * srx, y, srx * srz - crx * crz * sry, crz * srx + crx * sry * srz, crx * cry, z);
        }

        /// <summary>
        ///     Calculates the pose from the position and euler angles ([x,y,z,rx,ry,rz] array)
        ///     The result is the same as calling: H = transl(x,y,z)*rotx(rx*pi/180)*roty(ry*pi/180)*rotz(rz*pi/180)
        /// </summary>
        /// <returns>Homogeneous matrix (4x4)</returns>
        public static Mat FromTxyzRxyz(double[] xyzwpr)
        {
            if (xyzwpr.Length < 6)
                return null;
            return FromTxyzRxyz(xyzwpr[0], xyzwpr[1], xyzwpr[2], xyzwpr[3], xyzwpr[4], xyzwpr[5]);
        }

        /// <summary>
        ///     Calculates the equivalent position and euler angles ([x,y,z,rx,ry,rz] array) of a pose
        ///     Note: Pose = transl(x,y,z)*rotx(rx*pi/180)*roty(ry*pi/180)*rotz(rz*pi/180)
        ///     See also: FromTxyzRxyz()
        /// </summary>
        /// <returns>XYZWPR translation and rotation in mm and degrees</returns>
        public double[] ToTxyzRxyz()
        {
            var xyzwpr = new double[6];
            var x = _mat[0, 3];
            var y = _mat[1, 3];
            var z = _mat[2, 3];
            double rx1 = 0;
            double ry1 = 0;
            double rz1 = 0;


            var a = _mat[0, 0];
            var b = _mat[0, 1];
            var c = _mat[0, 2];
            var d = _mat[1, 2];
            var e = _mat[2, 2];

            if (c == 1)
            {
                ry1 = 0.5 * Math.PI;
                rx1 = 0;
                rz1 = Math.Atan2(_mat[1, 0], _mat[1, 1]);
            }
            else if (c == -1)
            {
                ry1 = -Math.PI / 2;
                rx1 = 0;
                rz1 = Math.Atan2(_mat[1, 0], _mat[1, 1]);
            }
            else
            {
                var sy = c;
                var cy1 = +Math.Sqrt(1 - sy * sy);

                var sx1 = -d / cy1;
                var cx1 = e / cy1;

                var sz1 = -b / cy1;
                var cz1 = a / cy1;

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
        ///     Calculates the equivalent position and euler angles ([x,y,z,r,p,w] vector) of the given pose in Universal Robots
        ///     format
        ///     Note: The difference between ToUR and ToXYZWPR is that the first one uses radians for the orientation and the
        ///     second one uses degres
        ///     Note: transl(x,y,z)*rotx(rx*pi/180)*roty(ry*pi/180)*rotz(rz*pi/180)
        ///     See also: FromXYZRPW()
        /// </summary>
        /// <returns>XYZWPR translation and rotation in mm and radians</returns>
        public double[] ToUR()
        {
            var xyzwpr = new double[6];
            var x = _mat[0, 3];
            var y = _mat[1, 3];
            var z = _mat[2, 3];
            var angle = Math.Acos(Math.Min(Math.Max((_mat[0, 0] + _mat[1, 1] + _mat[2, 2] - 1) / 2, -1), 1));
            var rx = _mat[2, 1] - _mat[1, 2];
            var ry = _mat[0, 2] - _mat[2, 0];
            var rz = _mat[1, 0] - _mat[0, 1];
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
        ///     Calculates the pose from the position and euler angles ([x,y,z,r,p,w] vector)
        ///     Note: The difference between FromUR and FromXYZWPR is that the first one uses radians for the orientation and the
        ///     second one uses degres
        ///     The result is the same as calling: H = transl(x,y,z)*rotx(rx)*roty(ry)*rotz(rz)
        /// </summary>
        /// <param name="xyzwpr">The position and euler angles array</param>
        /// <returns>Homogeneous matrix (4x4)</returns>
        public static Mat FromUR(double[] xyzwpr)
        {
            var x = xyzwpr[0];
            var y = xyzwpr[1];
            var z = xyzwpr[2];
            var w = xyzwpr[3];
            var p = xyzwpr[4];
            var r = xyzwpr[5];
            var angle = Math.Sqrt(w * w + p * p + r * r);
            if (angle < 1e-6)
                return Identity4x4();
            var c = Math.Cos(angle);
            var s = Math.Sin(angle);
            var ux = w / angle;
            var uy = p / angle;
            var uz = r / angle;
            return new Mat(ux * ux + c * (1 - ux * ux), ux * uy * (1 - c) - uz * s, ux * uz * (1 - c) + uy * s, x,
                ux * uy * (1 - c) + uz * s, uy * uy + (1 - uy * uy) * c, uy * uz * (1 - c) - ux * s, y,
                ux * uz * (1 - c) - uy * s, uy * uz * (1 - c) + ux * s, uz * uz + (1 - uz * uz) * c, z);
        }

        /// <summary>
        ///     Converts a matrix into a one-dimensional array of doubles
        /// </summary>
        /// <returns>one-dimensional array</returns>
        public double[] ToDoubles()
        {
            var cnt = 0;
            var array = new double[_rows * _cols];
            for (var j = 0; j < _cols; j++)
            for (var i = 0; i < _rows; i++)
            {
                array[cnt] = _mat[i, j];
                cnt = cnt + 1;
            }
            return array;
        }

        /// <summary>
        ///     Check if the matrix is square
        /// </summary>
        public bool IsSquare()
        {
            return _rows == _cols;
        }

        public bool Is4x4()
        {
            if (_cols != 4 || _rows != 4)
                return false;
            return true;
        }

        /// <summary>
        ///     Check if the matrix is homogeneous (4x4)
        /// </summary>
        public bool IsHomogeneous()
        {
            if (!Is4x4())
                return false;
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
        ///     Returns the inverse of a homogeneous matrix (4x4 matrix)
        /// </summary>
        /// <returns>Homogeneous matrix (4x4)</returns>
        public Mat inv()
        {
            if (!IsHomogeneous())
                throw new MatException("Can't invert a non-homogeneous matrix");
            var xyz = Pos();
            var mat_xyz = new Mat(xyz[0], xyz[1], xyz[2]);
            var hinv = Duplicate();
            hinv.setPos(0, 0, 0);
            hinv = hinv.Transpose();
            var new_pos = rotate(hinv, mat_xyz);
            hinv[0, 3] = -new_pos[0, 0];
            hinv[1, 3] = -new_pos[1, 0];
            hinv[2, 3] = -new_pos[2, 0];
            return hinv;
        }

        /// <summary>
        ///     Rotate a vector given a matrix (rotation matrix or homogeneous matrix)
        /// </summary>
        /// <param name="pose">4x4 homogeneous matrix or 3x3 rotation matrix</param>
        /// <param name="vector">4x1 or 3x1 vector</param>
        /// <returns></returns>
        public static Mat rotate(Mat pose, Mat vector)
        {
            if (pose._cols < 3 || pose._rows < 3 || vector._rows < 3)
                throw new MatException("Invalid matrix size");
            var pose3x3 = pose.Duplicate();
            var vector3 = vector.Duplicate();
            pose3x3._rows = 3;
            pose3x3._cols = 3;
            vector3._rows = 3;
            return pose3x3 * vector3;
        }

        /// <summary>
        ///     Returns the XYZ position of the Homogeneous matrix
        /// </summary>
        /// <returns>XYZ position</returns>
        public double[] Pos()
        {
            if (!Is4x4())
                return null;
            var xyz = new double[3];
            xyz[0] = _mat[0, 3];
            xyz[1] = _mat[1, 3];
            xyz[2] = _mat[2, 3];
            return xyz;
        }

        /// <summary>
        ///     Sets the 4x4 position of the Homogeneous matrix
        /// </summary>
        /// <param name="xyz">XYZ position</param>
        public void setPos(double[] xyz)
        {
            if (!Is4x4() || xyz.Length < 3)
                return;
            _mat[0, 3] = xyz[0];
            _mat[1, 3] = xyz[1];
            _mat[2, 3] = xyz[2];
        }

        /// <summary>
        ///     Sets the 4x4 position of the Homogeneous matrix
        /// </summary>
        /// <param name="x">X position</param>
        /// <param name="y">Y position</param>
        /// <param name="z">Z position</param>
        public void setPos(double x, double y, double z)
        {
            if (!Is4x4())
                return;
            _mat[0, 3] = x;
            _mat[1, 3] = y;
            _mat[2, 3] = z;
        }

        public Mat GetCol(int k)
        {
            var m = new Mat(_rows, 1);
            for (var i = 0; i < _rows; i++)
                m[i, 0] = _mat[i, k];
            return m;
        }

        public void SetCol(Mat v, int k)
        {
            for (var i = 0; i < _rows; i++)
                _mat[i, k] = v[i, 0];
        }

        public Mat Duplicate() // Function returns the copy of this matrix
        {
            var matrix = new Mat(_rows, _cols);
            for (var i = 0; i < _rows; i++)
            for (var j = 0; j < _cols; j++)
                matrix[i, j] = _mat[i, j];
            return matrix;
        }

        public static Mat ZeroMatrix(int iRows, int iCols) // Function generates the zero matrix
        {
            var matrix = new Mat(iRows, iCols);
            for (var i = 0; i < iRows; i++)
            for (var j = 0; j < iCols; j++)
                matrix[i, j] = 0;
            return matrix;
        }

        public static Mat IdentityMatrix(int iRows, int iCols) // Function generates the identity matrix
        {
            var matrix = ZeroMatrix(iRows, iCols);
            for (var i = 0; i < Math.Min(iRows, iCols); i++)
                matrix[i, i] = 1;
            return matrix;
        }

        /// <summary>
        ///     Returns an identity 4x4 matrix (homogeneous matrix)
        /// </summary>
        /// <returns></returns>
        public static Mat Identity4x4()
        {
            return IdentityMatrix(4, 4);
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

        public override string ToString() // Function returns matrix as a string
        {
            var s = "";
            for (var i = 0; i < _rows; i++)
            {
                for (var j = 0; j < _cols; j++)
                    s += string.Format("{0,5:0.00}", _mat[i, j]) + " ";
                s += "\r\n";
            }
            return s;
        }

        /// <summary>
        ///     Transpose a matrix
        /// </summary>
        /// <returns></returns>
        public Mat Transpose()
        {
            return Transpose(this);
        }

        public static Mat Transpose(Mat m) // Matrix transpose, for any rectangular matrix
        {
            var t = new Mat(m._cols, m._rows);
            for (var i = 0; i < m._rows; i++)
            for (var j = 0; j < m._cols; j++)
                t[j, i] = m[i, j];
            return t;
        }

        public static Mat StupidMultiply(Mat m1, Mat m2) // Stupid matrix multiplication
        {
            if (m1._cols != m2._rows)
                throw new MatException("Wrong dimensions of matrix!");

            var result = ZeroMatrix(m1._rows, m2._cols);
            for (var i = 0; i < result._rows; i++)
            for (var j = 0; j < result._cols; j++)
            for (var k = 0; k < m1._cols; k++)
                result[i, j] += m1[i, k] * m2[k, j];
            return result;
        }

        public static string NormalizeMatrixString(string matStr) // From Andy - thank you! :)
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
            while (matStr.LastIndexOf("|") == matStr.Length - 1)
                matStr = matStr.Substring(0, matStr.Length - 1);

            matStr = matStr.Replace("|", "\r\n");
            return matStr.Trim();
        }


        // Operators
        public static Mat operator -(Mat m)
        {
            return Multiply(-1, m);
        }

        public static Mat operator +(Mat m1, Mat m2)
        {
            return Add(m1, m2);
        }

        public static Mat operator -(Mat m1, Mat m2)
        {
            return Add(m1, -m2);
        }

        public static Mat operator *(Mat m1, Mat m2)
        {
            return StrassenMultiply(m1, m2);
        }

        public static Mat operator *(double n, Mat m)
        {
            return Multiply(n, m);
        }

        #endregion

        #region Private Methods

        /// <summary>
        ///     Returns the quaternion of a pose (4x4 matrix)
        /// </summary>
        /// <param name="Ti"></param>
        /// <returns></returns>
        private static double[] ToQuaternion(Mat Ti)
        {
            var q = new double[4];
            var a = Ti[0, 0];
            var b = Ti[1, 1];
            var c = Ti[2, 2];
            var sign2 = 1.0;
            var sign3 = 1.0;
            var sign4 = 1.0;
            if (Ti[2, 1] - Ti[1, 2] < 0)
                sign2 = -1;
            if (Ti[0, 2] - Ti[2, 0] < 0)
                sign3 = -1;
            if (Ti[1, 0] - Ti[0, 1] < 0)
                sign4 = -1;
            q[0] = 0.5 * Math.Sqrt(Math.Max(a + b + c + 1, 0));
            q[1] = 0.5 * sign2 * Math.Sqrt(Math.Max(a - b - c + 1, 0));
            q[2] = 0.5 * sign3 * Math.Sqrt(Math.Max(-a + b - c + 1, 0));
            q[3] = 0.5 * sign4 * Math.Sqrt(Math.Max(-a - b + c + 1, 0));
            return q;
        }

        /// <summary>
        ///     Returns the pose (4x4 matrix) from quaternion data
        /// </summary>
        /// <param name="q"></param>
        /// <returns></returns>
        private static Mat FromQuaternion(double[] qin)
        {
            var qnorm = Math.Sqrt(qin[0] * qin[0] + qin[1] * qin[1] + qin[2] * qin[2] + qin[3] * qin[3]);
            var q = new double[4];
            q[0] = qin[0] / qnorm;
            q[1] = qin[1] / qnorm;
            q[2] = qin[2] / qnorm;
            q[3] = qin[3] / qnorm;
            var pose = new Mat(1 - 2 * q[2] * q[2] - 2 * q[3] * q[3], 2 * q[1] * q[2] - 2 * q[3] * q[0],
                2 * q[1] * q[3] + 2 * q[2] * q[0], 0, 2 * q[1] * q[2] + 2 * q[3] * q[0],
                1 - 2 * q[1] * q[1] - 2 * q[3] * q[3], 2 * q[2] * q[3] - 2 * q[1] * q[0], 0,
                2 * q[1] * q[3] - 2 * q[2] * q[0], 2 * q[2] * q[3] + 2 * q[1] * q[0], 1 - 2 * q[1] * q[1] - 2 * q[2] * q[2],
                0);
            return pose;
        }

        /// <summary>
        ///     Converts a pose to an ABB target
        /// </summary>
        /// <param name="H"></param>
        /// <returns></returns>
        private static double[] ToABB(Mat H)
        {
            var q = ToQuaternion(H);
            double[] xyzq1234 = {H[0, 3], H[1, 3], H[2, 3], q[0], q[1], q[2], q[3]};
            return xyzq1234;
        }

        private static void SafeAplusBintoC(Mat A, int xa, int ya, Mat B, int xb, int yb, Mat C, int size)
        {
            for (var i = 0; i < size; i++) // rows
            for (var j = 0; j < size; j++) // cols
            {
                C[i, j] = 0;
                if (xa + j < A._cols && ya + i < A._rows)
                    C[i, j] += A[ya + i, xa + j];
                if (xb + j < B._cols && yb + i < B._rows)
                    C[i, j] += B[yb + i, xb + j];
            }
        }

        private static void SafeAminusBintoC(Mat A, int xa, int ya, Mat B, int xb, int yb, Mat C, int size)
        {
            for (var i = 0; i < size; i++) // rows
            for (var j = 0; j < size; j++) // cols
            {
                C[i, j] = 0;
                if (xa + j < A._cols && ya + i < A._rows)
                    C[i, j] += A[ya + i, xa + j];
                if (xb + j < B._cols && yb + i < B._rows)
                    C[i, j] -= B[yb + i, xb + j];
            }
        }

        private static void SafeACopytoC(Mat A, int xa, int ya, Mat C, int size)
        {
            for (var i = 0; i < size; i++) // rows
            for (var j = 0; j < size; j++) // cols
            {
                C[i, j] = 0;
                if (xa + j < A._cols && ya + i < A._rows)
                    C[i, j] += A[ya + i, xa + j];
            }
        }

        private static void AplusBintoC(Mat A, int xa, int ya, Mat B, int xb, int yb, Mat C, int size)
        {
            for (var i = 0; i < size; i++) // rows
            for (var j = 0; j < size; j++)
                C[i, j] = A[ya + i, xa + j] + B[yb + i, xb + j];
        }

        private static void AminusBintoC(Mat A, int xa, int ya, Mat B, int xb, int yb, Mat C, int size)
        {
            for (var i = 0; i < size; i++) // rows
            for (var j = 0; j < size; j++)
                C[i, j] = A[ya + i, xa + j] - B[yb + i, xb + j];
        }

        private static void ACopytoC(Mat A, int xa, int ya, Mat C, int size)
        {
            for (var i = 0; i < size; i++) // rows
            for (var j = 0; j < size; j++)
                C[i, j] = A[ya + i, xa + j];
        }

        private static Mat StrassenMultiply(Mat A, Mat B) // Smart matrix multiplication
        {
            if (A._cols != B._rows)
                throw new MatException("Wrong dimension of matrix!");

            Mat R;

            var msize = Math.Max(Math.Max(A._rows, A._cols), Math.Max(B._rows, B._cols));

            if (msize < 32)
            {
                R = ZeroMatrix(A._rows, B._cols);
                for (var i = 0; i < R._rows; i++)
                for (var j = 0; j < R._cols; j++)
                for (var k = 0; k < A._cols; k++)
                    R[i, j] += A[i, k] * B[k, j];
                return R;
            }

            var size = 1;
            var n = 0;
            while (msize > size)
            {
                size *= 2;
                n++;
            }
            ;
            var h = size / 2;


            var mField = new Mat[n, 9];

            /*
         *  8x8, 8x8, 8x8, ...
         *  4x4, 4x4, 4x4, ...
         *  2x2, 2x2, 2x2, ...
         *  . . .
         */

            int z;
            for (var i = 0; i < n - 4; i++) // rows
            {
                z = (int) Math.Pow(2, n - i - 1);
                for (var j = 0; j < 9; j++)
                    mField[i, j] = new Mat(z, z);
            }

            SafeAplusBintoC(A, 0, 0, A, h, h, mField[0, 0], h);
            SafeAplusBintoC(B, 0, 0, B, h, h, mField[0, 1], h);
            StrassenMultiplyRun(mField[0, 0], mField[0, 1], mField[0, 1 + 1], 1, mField); // (A11 + A22) * (B11 + B22);

            SafeAplusBintoC(A, 0, h, A, h, h, mField[0, 0], h);
            SafeACopytoC(B, 0, 0, mField[0, 1], h);
            StrassenMultiplyRun(mField[0, 0], mField[0, 1], mField[0, 1 + 2], 1, mField); // (A21 + A22) * B11;

            SafeACopytoC(A, 0, 0, mField[0, 0], h);
            SafeAminusBintoC(B, h, 0, B, h, h, mField[0, 1], h);
            StrassenMultiplyRun(mField[0, 0], mField[0, 1], mField[0, 1 + 3], 1, mField); //A11 * (B12 - B22);

            SafeACopytoC(A, h, h, mField[0, 0], h);
            SafeAminusBintoC(B, 0, h, B, 0, 0, mField[0, 1], h);
            StrassenMultiplyRun(mField[0, 0], mField[0, 1], mField[0, 1 + 4], 1, mField); //A22 * (B21 - B11);

            SafeAplusBintoC(A, 0, 0, A, h, 0, mField[0, 0], h);
            SafeACopytoC(B, h, h, mField[0, 1], h);
            StrassenMultiplyRun(mField[0, 0], mField[0, 1], mField[0, 1 + 5], 1, mField); //(A11 + A12) * B22;

            SafeAminusBintoC(A, 0, h, A, 0, 0, mField[0, 0], h);
            SafeAplusBintoC(B, 0, 0, B, h, 0, mField[0, 1], h);
            StrassenMultiplyRun(mField[0, 0], mField[0, 1], mField[0, 1 + 6], 1, mField); //(A21 - A11) * (B11 + B12);

            SafeAminusBintoC(A, h, 0, A, h, h, mField[0, 0], h);
            SafeAplusBintoC(B, 0, h, B, h, h, mField[0, 1], h);
            StrassenMultiplyRun(mField[0, 0], mField[0, 1], mField[0, 1 + 7], 1, mField); // (A12 - A22) * (B21 + B22);

            R = new Mat(A._rows, B._cols); // result

            /// C11
            for (var i = 0; i < Math.Min(h, R._rows); i++) // rows
            for (var j = 0; j < Math.Min(h, R._cols); j++) // cols
                R[i, j] = mField[0, 1 + 1][i, j] + mField[0, 1 + 4][i, j] - mField[0, 1 + 5][i, j] + mField[0, 1 + 7][i, j];

            /// C12
            for (var i = 0; i < Math.Min(h, R._rows); i++) // rows
            for (var j = h; j < Math.Min(2 * h, R._cols); j++) // cols
                R[i, j] = mField[0, 1 + 3][i, j - h] + mField[0, 1 + 5][i, j - h];

            /// C21
            for (var i = h; i < Math.Min(2 * h, R._rows); i++) // rows
            for (var j = 0; j < Math.Min(h, R._cols); j++) // cols
                R[i, j] = mField[0, 1 + 2][i - h, j] + mField[0, 1 + 4][i - h, j];

            /// C22
            for (var i = h; i < Math.Min(2 * h, R._rows); i++) // rows
            for (var j = h; j < Math.Min(2 * h, R._cols); j++) // cols
                R[i, j] = mField[0, 1 + 1][i - h, j - h] - mField[0, 1 + 2][i - h, j - h] + mField[0, 1 + 3][i - h, j - h] +
                          mField[0, 1 + 6][i - h, j - h];

            return R;
        }

        // function for square matrix 2^N x 2^N

        private static void
            StrassenMultiplyRun(Mat A, Mat B, Mat C, int l, Mat[,] f) // A * B into C, level of recursion, matrix field
        {
            var size = A._rows;
            var h = size / 2;

            if (size < 32)
            {
                for (var i = 0; i < C._rows; i++)
                for (var j = 0; j < C._cols; j++)
                {
                    C[i, j] = 0;
                    for (var k = 0; k < A._cols; k++)
                        C[i, j] += A[i, k] * B[k, j];
                }
                return;
            }

            AplusBintoC(A, 0, 0, A, h, h, f[l, 0], h);
            AplusBintoC(B, 0, 0, B, h, h, f[l, 1], h);
            StrassenMultiplyRun(f[l, 0], f[l, 1], f[l, 1 + 1], l + 1, f); // (A11 + A22) * (B11 + B22);

            AplusBintoC(A, 0, h, A, h, h, f[l, 0], h);
            ACopytoC(B, 0, 0, f[l, 1], h);
            StrassenMultiplyRun(f[l, 0], f[l, 1], f[l, 1 + 2], l + 1, f); // (A21 + A22) * B11;

            ACopytoC(A, 0, 0, f[l, 0], h);
            AminusBintoC(B, h, 0, B, h, h, f[l, 1], h);
            StrassenMultiplyRun(f[l, 0], f[l, 1], f[l, 1 + 3], l + 1, f); //A11 * (B12 - B22);

            ACopytoC(A, h, h, f[l, 0], h);
            AminusBintoC(B, 0, h, B, 0, 0, f[l, 1], h);
            StrassenMultiplyRun(f[l, 0], f[l, 1], f[l, 1 + 4], l + 1, f); //A22 * (B21 - B11);

            AplusBintoC(A, 0, 0, A, h, 0, f[l, 0], h);
            ACopytoC(B, h, h, f[l, 1], h);
            StrassenMultiplyRun(f[l, 0], f[l, 1], f[l, 1 + 5], l + 1, f); //(A11 + A12) * B22;

            AminusBintoC(A, 0, h, A, 0, 0, f[l, 0], h);
            AplusBintoC(B, 0, 0, B, h, 0, f[l, 1], h);
            StrassenMultiplyRun(f[l, 0], f[l, 1], f[l, 1 + 6], l + 1, f); //(A21 - A11) * (B11 + B12);

            AminusBintoC(A, h, 0, A, h, h, f[l, 0], h);
            AplusBintoC(B, 0, h, B, h, h, f[l, 1], h);
            StrassenMultiplyRun(f[l, 0], f[l, 1], f[l, 1 + 7], l + 1, f); // (A12 - A22) * (B21 + B22);

            /// C11
            for (var i = 0; i < h; i++) // rows
            for (var j = 0; j < h; j++) // cols
                C[i, j] = f[l, 1 + 1][i, j] + f[l, 1 + 4][i, j] - f[l, 1 + 5][i, j] + f[l, 1 + 7][i, j];

            /// C12
            for (var i = 0; i < h; i++) // rows
            for (var j = h; j < size; j++) // cols
                C[i, j] = f[l, 1 + 3][i, j - h] + f[l, 1 + 5][i, j - h];

            /// C21
            for (var i = h; i < size; i++) // rows
            for (var j = 0; j < h; j++) // cols
                C[i, j] = f[l, 1 + 2][i - h, j] + f[l, 1 + 4][i - h, j];

            /// C22
            for (var i = h; i < size; i++) // rows
            for (var j = h; j < size; j++) // cols
                C[i, j] = f[l, 1 + 1][i - h, j - h] - f[l, 1 + 2][i - h, j - h] + f[l, 1 + 3][i - h, j - h] +
                          f[l, 1 + 6][i - h, j - h];
        }

        private static Mat Multiply(double n, Mat m) // Multiplication by constant n
        {
            var r = new Mat(m._rows, m._cols);
            for (var i = 0; i < m._rows; i++)
            for (var j = 0; j < m._cols; j++)
                r[i, j] = m[i, j] * n;
            return r;
        }

        private static Mat Add(Mat m1, Mat m2) // Add matrix
        {
            if (m1._rows != m2._rows || m1._cols != m2._cols)
                throw new MatException("Matrices must have the same dimensions!");
            var r = new Mat(m1._rows, m1._cols);
            for (var i = 0; i < r._rows; i++)
            for (var j = 0; j < r._cols; j++)
                r[i, j] = m1[i, j] + m2[i, j];
            return r;
        }

        #endregion
    }
}