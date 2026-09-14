package com.robodk.api;

import com.robodk.api.exception.MatException;

import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.io.UncheckedIOException;
import java.util.Locale;

/**
 * A general purpose matrix of doubles, most commonly used as a 4x4 homogeneous transformation
 * matrix (a "pose"): the position and orientation of an item, target, or tool/reference frame
 * in the RoboDK station.
 * <p>
 * This is a standalone, dependency-free port of the reference RoboDK C# {@code Mat} class: a
 * row/column indexed matrix of arbitrary size, with the pose-oriented helpers (translation and
 * rotation builders, Euler angle conversions, inversion, ...) used throughout the RoboDK API.
 * <p>
 * In RoboDK, a pose is always expressed as: {@code pose = transl(x,y,z) * rotz(w) * roty(p) * rotx(r)}.
 */
public class Mat {

    private final int rows;
    private final int cols;
    private final double[][] data;

    // ------------------------------------------------------------------------------------
    // Constructors
    // ------------------------------------------------------------------------------------

    /**
     * Creates a new identity 4x4 pose (no translation, no rotation).
     */
    public Mat() {
        this(4, 4);
        for (int i = 0; i < 4; i++) {
            data[i][i] = 1.0;
        }
    }

    /**
     * Creates a new zero-filled matrix of the given size.
     */
    public Mat(int rows, int cols) {
        this.rows = rows;
        this.cols = cols;
        this.data = new double[rows][cols];
    }

    /**
     * Creates a copy of an existing matrix.
     */
    public Mat(Mat other) {
        this(other.rows, other.cols);
        for (int i = 0; i < rows; i++) {
            System.arraycopy(other.data[i], 0, data[i], 0, cols);
        }
    }

    /**
     * Creates a 4x1 column vector {@code [x, y, z, 1]}, typically used to represent a point in
     * homogeneous coordinates.
     */
    public Mat(double x, double y, double z) {
        this(4, 1);
        data[0][0] = x;
        data[1][0] = y;
        data[2][0] = z;
        data[3][0] = 1.0;
    }

    /**
     * Creates a 4x4 pose from its 12 relevant values, provided column by column: n (X axis),
     * o (Y axis), a (Z axis) and t (translation). The last row is set to {@code [0, 0, 0, 1]}.
     */
    public Mat(double nx, double ox, double ax, double tx,
               double ny, double oy, double ay, double ty,
               double nz, double oz, double az, double tz) {
        this(4, 4);
        data[0][0] = nx;
        data[1][0] = ny;
        data[2][0] = nz;
        data[0][1] = ox;
        data[1][1] = oy;
        data[2][1] = oz;
        data[0][2] = ax;
        data[1][2] = ay;
        data[2][2] = az;
        data[0][3] = tx;
        data[1][3] = ty;
        data[2][3] = tz;
        data[3][3] = 1.0;
    }

    /**
     * Creates a 3x3 rotation matrix from its 9 values, provided column by column: n (X axis),
     * o (Y axis) and a (Z axis).
     */
    public Mat(double nx, double ox, double ax,
               double ny, double oy, double ay,
               double nz, double oz, double az) {
        this(3, 3);
        data[0][0] = nx;
        data[1][0] = ny;
        data[2][0] = nz;
        data[0][1] = ox;
        data[1][1] = oy;
        data[2][1] = oz;
        data[0][2] = ax;
        data[1][2] = ay;
        data[2][2] = az;
    }

    /**
     * Creates a matrix from a flat array of doubles.
     *
     * @param values the array of values
     * @param isPose if {@code true}, {@code values} must hold exactly 16 values in column-major
     *               order (the wire format used by the RoboDK API, {@code values[row + col * 4]})
     *               and the result is a 4x4 pose; otherwise {@code values} is turned into a
     *               single-column matrix ({@code values.length} rows, 1 column)
     * @throws MatException if {@code isPose} is {@code true} and {@code values} does not hold
     *                       exactly 16 values
     */
    public Mat(double[] values, boolean isPose) {
        if (isPose) {
            this.rows = 4;
            this.cols = 4;
            this.data = new double[4][4];
            if (values == null || values.length < 16) {
                throw new MatException("Invalid array size to create a pose Mat");
            }
            for (int r = 0; r < 4; r++) {
                for (int c = 0; c < 4; c++) {
                    data[r][c] = values[r + c * 4];
                }
            }
        } else {
            this.rows = values == null ? 0 : values.length;
            this.cols = 1;
            this.data = new double[rows][1];
            for (int r = 0; r < rows; r++) {
                data[r][0] = values[r];
            }
        }
    }

    /**
     * Creates a single-column matrix (a column vector) from an array of doubles.
     */
    public Mat(double[] column) {
        this(column, false);
    }

    /**
     * Creates a matrix from a list of points, provided as an array of {@code [x, y, z, ...]}
     * coordinate arrays (one array per point). The resulting matrix has one column per point
     * and one row per coordinate.
     */
    public Mat(double[][] pointList) {
        this.cols = pointList.length;
        this.rows = cols == 0 ? 0 : pointList[0].length;
        this.data = new double[rows][cols];
        for (int c = 0; c < cols; c++) {
            for (int r = 0; r < rows; r++) {
                data[r][c] = pointList[c][r];
            }
        }
    }

    // ------------------------------------------------------------------------------------
    // Static factory methods
    // ------------------------------------------------------------------------------------

    /**
     * Returns a new identity matrix of the given size.
     */
    public static Mat identityMatrix(int rows, int cols) {
        Mat matrix = new Mat(rows, cols);
        int diagonal = Math.min(rows, cols);
        for (int i = 0; i < diagonal; i++) {
            matrix.data[i][i] = 1.0;
        }
        return matrix;
    }

    /**
     * Returns a new identity 4x4 pose.
     */
    public static Mat identity4x4() {
        return identityMatrix(4, 4);
    }

    /**
     * Returns a new zero-filled matrix of the given size.
     */
    public static Mat zeros(int rows, int cols) {
        return new Mat(rows, cols);
    }

    /**
     * Returns a translation pose:
     * <pre>
     * | 1 0 0 X |
     * | 0 1 0 Y |
     * | 0 0 1 Z |
     * | 0 0 0 1 |
     * </pre>
     *
     * @param x translation along X (mm)
     * @param y translation along Y (mm)
     * @param z translation along Z (mm)
     */
    public static Mat transl(double x, double y, double z) {
        Mat mat = identity4x4();
        mat.setPos(x, y, z);
        return mat;
    }

    /**
     * Returns a rotation pose around the X axis.
     *
     * @param rx rotation angle, in radians
     */
    public static Mat rotX(double rx) {
        double cx = Math.cos(rx);
        double sx = Math.sin(rx);
        return new Mat(1, 0, 0, 0, 0, cx, -sx, 0, 0, sx, cx, 0);
    }

    /**
     * Returns a rotation pose around the Y axis.
     *
     * @param ry rotation angle, in radians
     */
    public static Mat rotY(double ry) {
        double cy = Math.cos(ry);
        double sy = Math.sin(ry);
        return new Mat(cy, 0, sy, 0, 0, 1, 0, 0, -sy, 0, cy, 0);
    }

    /**
     * Returns a rotation pose around the Z axis.
     *
     * @param rz rotation angle, in radians
     */
    public static Mat rotZ(double rz) {
        double cz = Math.cos(rz);
        double sz = Math.sin(rz);
        return new Mat(cz, -sz, 0, 0, sz, cz, 0, 0, 0, 0, 1, 0);
    }

    /**
     * Builds a pose from a position and Euler angles ({@code [x, y, z, r, p, w]}), following the
     * convention {@code pose = transl(x,y,z) * rotz(w) * roty(p) * rotx(r)}.
     *
     * @param x x position (mm)
     * @param y y position (mm)
     * @param z z position (mm)
     * @param r rotation around X, applied first (deg)
     * @param p rotation around Y, applied second (deg)
     * @param w rotation around Z, applied last (deg)
     * @see #toXyzRpw()
     */
    public static Mat fromXyzRpw(double x, double y, double z, double r, double p, double w) {
        double a = Math.toRadians(r);
        double b = Math.toRadians(p);
        double c = Math.toRadians(w);
        double ca = Math.cos(a);
        double sa = Math.sin(a);
        double cb = Math.cos(b);
        double sb = Math.sin(b);
        double cc = Math.cos(c);
        double sc = Math.sin(c);
        return new Mat(
                cb * cc, cc * sa * sb - ca * sc, sa * sc + ca * cc * sb, x,
                cb * sc, ca * cc + sa * sb * sc, ca * sb * sc - cc * sa, y,
                -sb, cb * sa, ca * cb, z);
    }

    /**
     * Convenience overload of {@link #fromXyzRpw(double, double, double, double, double, double)}
     * taking a 6-element {@code [x, y, z, r, p, w]} array.
     */
    public static Mat fromXyzRpw(double[] xyzrpw) {
        if (xyzrpw == null || xyzrpw.length < 6) {
            throw new MatException("Expected a 6-element [x, y, z, r, p, w] array");
        }
        return fromXyzRpw(xyzrpw[0], xyzrpw[1], xyzrpw[2], xyzrpw[3], xyzrpw[4], xyzrpw[5]);
    }

    /**
     * Builds a pose from a position and Euler angles ({@code [x, y, z, rx, ry, rz]}), following
     * the convention {@code pose = transl(x,y,z) * rotx(rx) * roty(ry) * rotz(rz)}.
     *
     * @see #toTxyzRxyz()
     */
    public static Mat fromTxyzRxyz(double x, double y, double z, double rx, double ry, double rz) {
        double a = Math.toRadians(rx);
        double b = Math.toRadians(ry);
        double c = Math.toRadians(rz);
        double crx = Math.cos(a);
        double srx = Math.sin(a);
        double cry = Math.cos(b);
        double sry = Math.sin(b);
        double crz = Math.cos(c);
        double srz = Math.sin(c);
        return new Mat(
                cry * crz, -cry * srz, sry, x,
                crx * srz + crz * srx * sry, crx * crz - srx * sry * srz, -cry * srx, y,
                srx * srz - crx * crz * sry, crz * srx + crx * sry * srz, crx * cry, z);
    }

    /**
     * Convenience overload of
     * {@link #fromTxyzRxyz(double, double, double, double, double, double)} taking a 6-element
     * {@code [x, y, z, rx, ry, rz]} array.
     */
    public static Mat fromTxyzRxyz(double[] xyzrxyz) {
        if (xyzrxyz == null || xyzrxyz.length < 6) {
            throw new MatException("Expected a 6-element [x, y, z, rx, ry, rz] array");
        }
        return fromTxyzRxyz(xyzrxyz[0], xyzrxyz[1], xyzrxyz[2], xyzrxyz[3], xyzrxyz[4], xyzrxyz[5]);
    }

    /**
     * Builds a pose from the position and rotation vector used by Universal Robots
     * ({@code [x, y, z, u, v, w]}, translation in mm and rotation vector in radians).
     *
     * @see #toUR()
     */
    public static Mat fromUR(double[] xyzuvw) {
        if (xyzuvw == null || xyzuvw.length < 6) {
            throw new MatException("Expected a 6-element [x, y, z, u, v, w] array");
        }
        double x = xyzuvw[0];
        double y = xyzuvw[1];
        double z = xyzuvw[2];
        double u = xyzuvw[3];
        double v = xyzuvw[4];
        double w = xyzuvw[5];
        double angle = Math.sqrt(u * u + v * v + w * w);
        Mat pose;
        if (angle < 1e-6) {
            pose = identity4x4();
        } else {
            double cosang = Math.cos(0.5 * angle);
            double ratio = Math.sin(0.5 * angle) / angle;
            double[] quaternion = {cosang, u * ratio, v * ratio, w * ratio};
            pose = fromQuaternion(quaternion);
        }
        pose.setPos(x, y, z);
        return pose;
    }

    /**
     * Converts a point and a Z axis direction (with an optional Y axis hint) into a pose, so
     * that the Z axis of the resulting pose points along {@code zAxis}.
     *
     * @param point      the pose position ({@code [x, y, z]})
     * @param zAxis      the desired Z axis direction (not necessarily normalized)
     * @param yAxisHint  a hint for the Y axis direction; defaults to {@code [0, 0, 1]} when
     *                   {@code null}
     */
    public static Mat fromPointNormal(double[] point, double[] zAxis, double[] yAxisHint) {
        Mat pose = identity4x4();
        double[] hint = yAxisHint == null ? new double[]{0, 0, 1} : yAxisHint;
        pose.setPos(point);
        pose.setVZ(zAxis);
        if (angle(zAxis, hint) < Math.toRadians(2)) {
            hint = new double[]{0, 1, 1};
        }
        double[] xAxis = normalize(cross(hint, zAxis));
        double[] yAxis = cross(zAxis, xAxis);
        pose.setVX(xAxis);
        pose.setVY(yAxis);
        return pose;
    }

    // ------------------------------------------------------------------------------------
    // Element access
    // ------------------------------------------------------------------------------------

    public int rows() {
        return rows;
    }

    public int cols() {
        return cols;
    }

    /** Returns the value at the given row/column. */
    public double get(int row, int col) {
        return data[row][col];
    }

    /** Sets the value at the given row/column. */
    public void set(int row, int col, double value) {
        data[row][col] = value;
    }

    public boolean isSquare() {
        return rows == cols;
    }

    /** Returns {@code true} if this matrix is 4x4. */
    public boolean is4x4() {
        return rows == 4 && cols == 4;
    }

    /**
     * Returns {@code true} if this matrix can be used as a homogeneous transform (that is, it is
     * 4x4). This mirrors the reference RoboDK API implementations, which do not otherwise
     * validate orthonormality.
     */
    public boolean isHomogeneous() {
        return is4x4();
    }

    /**
     * Returns {@code true} if this is a 4x4 homogeneous identity matrix.
     */
    public boolean isIdentity() {
        if (!is4x4()) {
            return false;
        }
        for (int i = 0; i < rows; i++) {
            if (data[i][i] != 1.0) {
                return false;
            }
        }
        return data[0][3] == 0.0 && data[1][3] == 0.0 && data[2][3] == 0.0;
    }

    // ------------------------------------------------------------------------------------
    // Position / orientation vectors (4x4 poses)
    // ------------------------------------------------------------------------------------

    /** Returns the {@code [x, y, z]} translation of this pose. */
    public double[] pos() {
        requireIs4x4();
        return new double[]{data[0][3], data[1][3], data[2][3]};
    }

    /** Sets the {@code [x, y, z]} translation of this pose. */
    public void setPos(double[] xyz) {
        requireIs4x4();
        data[0][3] = xyz[0];
        data[1][3] = xyz[1];
        data[2][3] = xyz[2];
    }

    /** Sets the {@code [x, y, z]} translation of this pose. */
    public void setPos(double x, double y, double z) {
        requireIs4x4();
        data[0][3] = x;
        data[1][3] = y;
        data[2][3] = z;
    }

    /** Returns the X axis (first column) of this pose's rotation part. */
    public double[] vx() {
        requireIs4x4();
        return new double[]{data[0][0], data[1][0], data[2][0]};
    }

    /** Sets the X axis (first column) of this pose's rotation part. */
    public void setVX(double[] xyz) {
        requireIs4x4();
        data[0][0] = xyz[0];
        data[1][0] = xyz[1];
        data[2][0] = xyz[2];
    }

    /** Returns the Y axis (second column) of this pose's rotation part. */
    public double[] vy() {
        requireIs4x4();
        return new double[]{data[0][1], data[1][1], data[2][1]};
    }

    /** Sets the Y axis (second column) of this pose's rotation part. */
    public void setVY(double[] xyz) {
        requireIs4x4();
        data[0][1] = xyz[0];
        data[1][1] = xyz[1];
        data[2][1] = xyz[2];
    }

    /** Returns the Z axis (third column) of this pose's rotation part. */
    public double[] vz() {
        requireIs4x4();
        return new double[]{data[0][2], data[1][2], data[2][2]};
    }

    /** Sets the Z axis (third column) of this pose's rotation part. */
    public void setVZ(double[] xyz) {
        requireIs4x4();
        data[0][2] = xyz[0];
        data[1][2] = xyz[1];
        data[2][2] = xyz[2];
    }

    /**
     * Returns the 3x3 rotation sub-matrix of this pose.
     *
     * @throws MatException if this matrix is not a 4x4 pose
     */
    public Mat rot3x3() {
        if (!isHomogeneous()) {
            throw new MatException("It is not possible to retrieve a 3x3 rotation matrix");
        }
        return new Mat(
                data[0][0], data[0][1], data[0][2],
                data[1][0], data[1][1], data[1][2],
                data[2][0], data[2][1], data[2][2]);
    }

    /**
     * Returns a copy of this pose with the rotation part reset to identity (translation only).
     */
    public Mat translationPose() {
        double[] p = pos();
        return transl(p[0], p[1], p[2]);
    }

    /**
     * Returns a copy of this pose with the translation part reset to zero (rotation only).
     */
    public Mat rotationPose() {
        Mat result = new Mat(this);
        result.setPos(0.0, 0.0, 0.0);
        return result;
    }

    // ------------------------------------------------------------------------------------
    // Pose <-> Euler angle conversions
    // ------------------------------------------------------------------------------------

    /**
     * Calculates the equivalent position and Euler angles ({@code [x, y, z, r, p, w]}) of this
     * pose. Note: {@code pose = transl(x,y,z) * rotz(w) * roty(p) * rotx(r)}.
     *
     * @return a 6-element array: XYZ translation in mm, RPW rotation in degrees
     * @see #fromXyzRpw(double, double, double, double, double, double)
     */
    public double[] toXyzRpw() {
        requireIs4x4();
        double x = data[0][3];
        double y = data[1][3];
        double z = data[2][3];
        double w;
        double p;
        double r;
        if (data[2][0] > 1.0 - 1e-6) {
            p = -Math.PI * 0.5;
            r = 0;
            w = Math.atan2(-data[1][2], data[1][1]);
        } else if (data[2][0] < -1.0 + 1e-6) {
            p = 0.5 * Math.PI;
            r = 0;
            w = Math.atan2(data[1][2], data[1][1]);
        } else {
            p = Math.atan2(-data[2][0], Math.sqrt(data[0][0] * data[0][0] + data[1][0] * data[1][0]));
            w = Math.atan2(data[1][0], data[0][0]);
            r = Math.atan2(data[2][1], data[2][2]);
        }
        return new double[]{x, y, z, Math.toDegrees(r), Math.toDegrees(p), Math.toDegrees(w)};
    }

    /**
     * Calculates the equivalent position and Euler angles ({@code [x, y, z, rx, ry, rz]}) of
     * this pose. Note: {@code pose = transl(x,y,z) * rotx(rx) * roty(ry) * rotz(rz)}.
     *
     * @return a 6-element array: XYZ translation in mm, RxRyRz rotation in degrees
     * @see #fromTxyzRxyz(double, double, double, double, double, double)
     */
    public double[] toTxyzRxyz() {
        requireIs4x4();
        double x = data[0][3];
        double y = data[1][3];
        double z = data[2][3];
        double rx1;
        double ry1;
        double rz1;

        double a = data[0][0];
        double b = data[0][1];
        double c = data[0][2];
        double d = data[1][2];
        double e = data[2][2];

        if (c == 1) {
            ry1 = 0.5 * Math.PI;
            rx1 = 0;
            rz1 = Math.atan2(data[1][0], data[1][1]);
        } else if (c == -1) {
            ry1 = -0.5 * Math.PI;
            rx1 = 0;
            rz1 = Math.atan2(data[1][0], data[1][1]);
        } else {
            double sy = c;
            double cy1 = Math.sqrt(1 - sy * sy);
            double sx1 = -d / cy1;
            double cx1 = e / cy1;
            double sz1 = -b / cy1;
            double cz1 = a / cy1;
            rx1 = Math.atan2(sx1, cx1);
            ry1 = Math.atan2(sy, cy1);
            rz1 = Math.atan2(sz1, cz1);
        }
        return new double[]{x, y, z, Math.toDegrees(rx1), Math.toDegrees(ry1), Math.toDegrees(rz1)};
    }

    /**
     * Calculates the equivalent position and rotation vector ({@code [x, y, z, u, v, w]}) of
     * this pose, in the format used by Universal Robots (translation in mm, rotation vector in
     * radians).
     *
     * @see #fromUR(double[])
     */
    public double[] toUR() {
        requireIs4x4();
        final double tolerance = 1e-8;
        double[] rxyz = {
                data[2][1] - data[1][2],
                data[0][2] - data[2][0],
                data[1][0] - data[0][1]
        };

        double angle = Math.acos(clamp((data[0][0] + data[1][1] + data[2][2] - 1) * 0.5, -1.0, 1.0));
        if (angle < tolerance) {
            rxyz[0] = 0.0;
            rxyz[1] = 0.0;
            rxyz[2] = 0.0;
        } else {
            double factor;
            double sinAngle = Math.sin(angle);
            if (Math.abs(sinAngle) < tolerance || norm(rxyz) < tolerance) {
                double mx;
                if (data[0][0] >= data[1][1] && data[0][0] >= data[2][2]) {
                    rxyz[0] = data[0][0] + 1.0;
                    rxyz[1] = data[1][0];
                    rxyz[2] = data[2][0];
                    mx = data[0][0];
                } else if (data[1][1] >= data[2][2]) {
                    rxyz[0] = data[0][1];
                    rxyz[1] = data[1][1] + 1.0;
                    rxyz[2] = data[2][1];
                    mx = data[1][1];
                } else {
                    rxyz[0] = data[0][2];
                    rxyz[1] = data[1][2];
                    rxyz[2] = data[2][2] + 1.0;
                    mx = data[2][2];
                }
                factor = angle / Math.sqrt(Math.max(0.0, 2.0 * (1.0 + mx)));
            } else {
                rxyz = normalize(rxyz);
                factor = angle;
            }
            rxyz[0] *= factor;
            rxyz[1] *= factor;
            rxyz[2] *= factor;
        }

        return new double[]{data[0][3], data[1][3], data[2][3], rxyz[0], rxyz[1], rxyz[2]};
    }

    /** Converts this matrix into a flat, column-major array of doubles. */
    public double[] toDoubles() {
        double[] array = new double[rows * cols];
        int index = 0;
        for (int c = 0; c < cols; c++) {
            for (int r = 0; r < rows; r++) {
                array[index++] = data[r][c];
            }
        }
        return array;
    }

    // ------------------------------------------------------------------------------------
    // Matrix algebra
    // ------------------------------------------------------------------------------------

    /** Returns a copy of this matrix. */
    public Mat duplicate() {
        return new Mat(this);
    }

    /** Returns the transpose of this matrix as a new matrix. */
    public Mat transpose() {
        Mat result = new Mat(cols, rows);
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                result.data[j][i] = data[i][j];
            }
        }
        return result;
    }

    /**
     * Returns the inverse of this pose, as a new matrix. For a homogeneous transform, this is
     * equivalent to (and cheaper than) a general matrix inverse.
     *
     * @throws MatException if this matrix is not a 4x4 pose
     */
    public Mat invert() {
        if (!isHomogeneous()) {
            throw new MatException("Can't invert a non-homogeneous matrix");
        }
        double[] xyz = pos();
        Mat result = duplicate();
        result.setPos(0.0, 0.0, 0.0);
        result = result.transpose();
        double[] newPos = rotate(result, xyz);
        result.data[0][3] = -newPos[0];
        result.data[1][3] = -newPos[1];
        result.data[2][3] = -newPos[2];
        return result;
    }

    /** Returns the sum of this matrix and {@code other}, as a new matrix. */
    public Mat add(Mat other) {
        requireSameSize(other);
        Mat result = new Mat(rows, cols);
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                result.data[i][j] = data[i][j] + other.data[i][j];
            }
        }
        return result;
    }

    /** Returns the difference between this matrix and {@code other}, as a new matrix. */
    public Mat subtract(Mat other) {
        requireSameSize(other);
        Mat result = new Mat(rows, cols);
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                result.data[i][j] = data[i][j] - other.data[i][j];
            }
        }
        return result;
    }

    /** Returns this matrix scaled by {@code factor}, as a new matrix. */
    public Mat multiply(double factor) {
        Mat result = new Mat(rows, cols);
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                result.data[i][j] = data[i][j] * factor;
            }
        }
        return result;
    }

    /**
     * Returns the matrix product {@code this * other}, as a new matrix.
     *
     * @throws MatException if the matrix dimensions are not compatible
     */
    public Mat multiply(Mat other) {
        if (this.cols != other.rows) {
            throw new MatException("Wrong dimensions of matrix, cannot multiply "
                    + rows + "x" + cols + " by " + other.rows + "x" + other.cols);
        }
        Mat result = new Mat(this.rows, other.cols);
        for (int i = 0; i < result.rows; i++) {
            for (int j = 0; j < result.cols; j++) {
                double sum = 0;
                for (int k = 0; k < this.cols; k++) {
                    sum += data[i][k] * other.data[k][j];
                }
                result.data[i][j] = sum;
            }
        }
        return result;
    }

    /**
     * Multiplies this matrix (typically a 4x4 pose) by a 3D point/vector and returns the
     * resulting 3D point/vector. When this matrix is a 4x4 pose, the point is treated as
     * {@code [x, y, z, 1]} (translation included); otherwise a plain matrix/vector product is
     * used.
     */
    public double[] multiply(double[] point) {
        double[] result = new double[point.length];
        if (is4x4() && point.length == 3) {
            for (int i = 0; i < 3; i++) {
                result[i] = data[i][0] * point[0] + data[i][1] * point[1] + data[i][2] * point[2] + data[i][3];
            }
            return result;
        }
        if (this.cols != point.length) {
            throw new MatException("Matrices must have compatible dimensions");
        }
        for (int i = 0; i < rows; i++) {
            double sum = 0;
            for (int j = 0; j < cols; j++) {
                sum += data[i][j] * point[j];
            }
            result[i] = sum;
        }
        return result;
    }

    /** Returns this matrix negated ({@code -this}), as a new matrix. */
    public Mat negate() {
        return multiply(-1.0);
    }

    /**
     * Rotates a 3D vector by the rotation part of a pose (or by a 3x3 rotation matrix),
     * ignoring translation.
     */
    public static double[] rotate(Mat pose, double[] vector) {
        if (pose.cols < 3 || pose.rows < 3) {
            throw new MatException("Invalid matrix size");
        }
        double[] result = new double[3];
        for (int i = 0; i < 3; i++) {
            result[i] = pose.data[i][0] * vector[0] + pose.data[i][1] * vector[1] + pose.data[i][2] * vector[2];
        }
        return result;
    }

    /**
     * Appends {@code other} to the right of this matrix (they must have the same number of
     * rows), as a new matrix.
     */
    public Mat concatenateHorizontal(Mat other) {
        if (this.rows != other.rows) {
            throw new MatException("Vertical size of matrices does not match");
        }
        Mat result = new Mat(this.rows, this.cols + other.cols);
        for (int row = 0; row < rows; row++) {
            System.arraycopy(this.data[row], 0, result.data[row], 0, this.cols);
            System.arraycopy(other.data[row], 0, result.data[row], this.cols, other.cols);
        }
        return result;
    }

    /**
     * Appends {@code other} below this matrix (they must have the same number of columns), as
     * a new matrix.
     */
    public Mat concatenateVertical(Mat other) {
        if (this.cols != other.cols) {
            throw new MatException("Horizontal size of matrices does not match");
        }
        Mat result = new Mat(this.rows + other.rows, this.cols);
        for (int row = 0; row < this.rows; row++) {
            System.arraycopy(this.data[row], 0, result.data[row], 0, this.cols);
        }
        for (int row = 0; row < other.rows; row++) {
            System.arraycopy(other.data[row], 0, result.data[this.rows + row], 0, other.cols);
        }
        return result;
    }

    // ------------------------------------------------------------------------------------
    // Tool / reference frame offsets
    // ------------------------------------------------------------------------------------

    /**
     * Calculates a relative target with respect to the tool coordinates, exactly like ABB's
     * {@code RelTool} instruction.
     *
     * @param targetPose reference pose
     * @param x          translation along the tool X axis (mm)
     * @param y          translation along the tool Y axis (mm)
     * @param z          translation along the tool Z axis (mm)
     * @param rx         rotation around the tool X axis (deg)
     * @param ry         rotation around the tool Y axis (deg)
     * @param rz         rotation around the tool Z axis (deg)
     */
    public static Mat relTool(Mat targetPose, double x, double y, double z, double rx, double ry, double rz) {
        return targetPose
                .multiply(transl(x, y, z))
                .multiply(rotX(Math.toRadians(rx)))
                .multiply(rotY(Math.toRadians(ry)))
                .multiply(rotZ(Math.toRadians(rz)));
    }

    /** Overload of {@link #relTool} with no additional rotation. */
    public static Mat relTool(Mat targetPose, double x, double y, double z) {
        return relTool(targetPose, x, y, z, 0.0, 0.0, 0.0);
    }

    /**
     * Calculates a relative target with respect to the reference frame coordinates.
     *
     * @param targetPose reference pose
     * @param x          translation along X (mm)
     * @param y          translation along Y (mm)
     * @param z          translation along Z (mm)
     * @param rx         rotation around X (deg)
     * @param ry         rotation around Y (deg)
     * @param rz         rotation around Z (deg)
     * @throws MatException if {@code targetPose} is not a 4x4 pose
     */
    public static Mat offset(Mat targetPose, double x, double y, double z, double rx, double ry, double rz) {
        if (!targetPose.isHomogeneous()) {
            throw new MatException("Pose matrix is not homogeneous");
        }
        return transl(x, y, z)
                .multiply(rotX(Math.toRadians(rx)))
                .multiply(rotY(Math.toRadians(ry)))
                .multiply(rotZ(Math.toRadians(rz)))
                .multiply(targetPose);
    }

    /** Overload of {@link #offset} with no additional rotation. */
    public static Mat offset(Mat targetPose, double x, double y, double z) {
        return offset(targetPose, x, y, z, 0.0, 0.0, 0.0);
    }

    // ------------------------------------------------------------------------------------
    // Vector helpers
    // ------------------------------------------------------------------------------------

    /** Returns the Euclidean norm of a 3D vector. */
    public static double norm(double[] p) {
        return Math.sqrt(p[0] * p[0] + p[1] * p[1] + p[2] * p[2]);
    }

    /** Returns the unit vector in the direction of {@code p}. */
    public static double[] normalize(double[] p) {
        double invNorm = 1.0 / norm(p);
        return new double[]{p[0] * invNorm, p[1] * invNorm, p[2] * invNorm};
    }

    /** Returns the cross product {@code a x b} of two 3D vectors. */
    public static double[] cross(double[] a, double[] b) {
        return new double[]{
                a[1] * b[2] - a[2] * b[1],
                a[2] * b[0] - a[0] * b[2],
                a[0] * b[1] - a[1] * b[0]
        };
    }

    /** Returns the dot product of two 3D vectors. */
    public static double dot(double[] a, double[] b) {
        return a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
    }

    /** Returns the angle, in radians, between two 3D vectors. */
    public static double angle(double[] a, double[] b) {
        return Math.acos(clamp(dot(normalize(a), normalize(b)), -1.0, 1.0));
    }

    // ------------------------------------------------------------------------------------
    // Persistence
    // ------------------------------------------------------------------------------------

    /** Saves this matrix, transposed, as a comma-separated CSV file. */
    public void saveCsv(String filename) {
        transpose().saveMat(filename, ",");
    }

    /** Saves this matrix to a text file, one row per line, values separated by {@code separator}. */
    public void saveMat(String filename, String separator) {
        try (BufferedWriter writer = new BufferedWriter(new FileWriter(filename))) {
            for (int row = 0; row < rows; row++) {
                StringBuilder line = new StringBuilder();
                for (int col = 0; col < cols; col++) {
                    line.append(String.format(Locale.ROOT, "%.6f", data[row][col])).append(separator);
                }
                writer.write(line.toString());
                writer.newLine();
            }
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
    }

    // ------------------------------------------------------------------------------------
    // Object overrides
    // ------------------------------------------------------------------------------------

    /**
     * Returns a human readable representation of this matrix: {@code X=.. Y=.. Z=.. Rx=.. Ry=..
     * Rz=..} for a 4x4 pose, or the raw matrix values otherwise.
     */
    @Override
    public String toString() {
        if (isHomogeneous()) {
            double[] values = toTxyzRxyz();
            String[] labels = {"X=", "Y=", "Z=", "Rx=", "Ry=", "Rz="};
            String[] units = {"mm", "mm", "mm", "deg", "deg", "deg"};
            StringBuilder builder = new StringBuilder();
            for (int i = 0; i < 6; i++) {
                builder.append(labels[i])
                        .append(String.format(Locale.ROOT, "%6.3f", values[i]))
                        .append(' ')
                        .append(units[i]);
                if (i < 5) {
                    builder.append(" , ");
                }
            }
            return builder.toString();
        }

        StringBuilder builder = new StringBuilder();
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                builder.append(String.format(Locale.ROOT, "%5.2f ", data[i][j]));
            }
            builder.append('\n');
        }
        return builder.toString();
    }

    @Override
    public boolean equals(Object other) {
        if (this == other) {
            return true;
        }
        if (!(other instanceof Mat)) {
            return false;
        }
        Mat that = (Mat) other;
        if (this.rows != that.rows || this.cols != that.cols) {
            return false;
        }
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                if (Double.compare(this.data[i][j], that.data[i][j]) != 0) {
                    return false;
                }
            }
        }
        return true;
    }

    @Override
    public int hashCode() {
        int result = rows * 31 + cols;
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                result = 31 * result + Double.hashCode(data[i][j]);
            }
        }
        return result;
    }

    // ------------------------------------------------------------------------------------
    // Internal helpers
    // ------------------------------------------------------------------------------------

    /**
     * Returns the 4x4 pose corresponding to a quaternion {@code [q0, q1, q2, q3]}.
     */
    private static Mat fromQuaternion(double[] qIn) {
        double qNorm = Math.sqrt(qIn[0] * qIn[0] + qIn[1] * qIn[1] + qIn[2] * qIn[2] + qIn[3] * qIn[3]);
        double q0 = qIn[0] / qNorm;
        double q1 = qIn[1] / qNorm;
        double q2 = qIn[2] / qNorm;
        double q3 = qIn[3] / qNorm;
        return new Mat(
                1 - 2 * q2 * q2 - 2 * q3 * q3, 2 * q1 * q2 - 2 * q3 * q0, 2 * q1 * q3 + 2 * q2 * q0, 0,
                2 * q1 * q2 + 2 * q3 * q0, 1 - 2 * q1 * q1 - 2 * q3 * q3, 2 * q2 * q3 - 2 * q1 * q0, 0,
                2 * q1 * q3 - 2 * q2 * q0, 2 * q2 * q3 + 2 * q1 * q0, 1 - 2 * q1 * q1 - 2 * q2 * q2, 0);
    }

    private static double clamp(double value, double min, double max) {
        return Math.min(Math.max(value, min), max);
    }

    private void requireIs4x4() {
        if (!is4x4()) {
            throw new MatException("This operation requires a 4x4 matrix, got " + rows + "x" + cols);
        }
    }

    private void requireSameSize(Mat other) {
        if (this.rows != other.rows || this.cols != other.cols) {
            throw new MatException("Matrices must have the same dimensions");
        }
    }
}
