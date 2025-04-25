#ifndef ROBODKTYPES_H
#define ROBODKTYPES_H


#include <QString>
#include <QtGui/QMatrix4x4>
#include <QDebug>


#ifndef M_PI
#define M_PI 3.14159265358979323846264338327950288
#endif


class IItem;
class IRoboDK;
typedef IItem* Item;
typedef IRoboDK RoboDK;




/// maximum size of robot joints (maximum allowed degrees of freedom for a robot)
#define RDK_SIZE_JOINTS_MAX 12
// IMPORTANT!! Do not change this value

/// Constant defining the size of a robot configuration (at least 3 doubles are required)
#define RDK_SIZE_MAX_CONFIG 4
// IMPORTANT!! Do not change this value


/// @brief tXYZWPR (mm, rad) holds the same information as a \ref tMatrix4x4 pose but represented as XYZ position (in mm) and WPR orientation (in rad) (XYZWPR = [X,Y,Z,W,P,R])
/// This type of variable is easier to read and it is what most robot controllers use to input a pose. However, for internal calculations it is better to use a 4x4 pose matrix as it is faster and more accurate.
/// To calculate a 4x4 matrix: pose4x4 = transl(X,Y,Z)*rotx(W)*roty(P)*rotz(R)
/// See \ref POSE_2_XYZWPR and \ref XYZWPR_2_POSE to exchange between \ref tMatrix4x4 and \ref tXYZWPR
typedef double tXYZWPR[6];

/// @brief tXYZ (mm) represents a position or a vector in mm
typedef double tXYZ[3];


/// @brief A robot configuration defines a specific state of the robot. It should be possible to accomplish a movement between two positions with the same robot configuration, without crossing any singularities.
/// Changing the robot configuration requires crossing a singularity.
/// For example, for a 6-axis robot there are 2x2x2=8 different configurations/solutions.
/// A robot configurations is also known as "Assembly mode".
/// <br>
/// The robot configuration is defined as an array of 3 doubles: [FACING REAR, LOWER ARM, WRIST FLIP].
/// <br>
/// FACING REAR=0 means FACING FRONT
/// <br>
/// LOWER ARM=0 means ELBOW UP
/// <br>
/// WRIST FLIP=0 means WRIST NON FLIP
/// <br>
/// the 4th value is reserved
typedef double tConfig[RDK_SIZE_MAX_CONFIG];



/// Calculate the dot product
#define DOT(v,q)   ((v)[0]*(q)[0] + (v)[1]*(q)[1] + (v)[2]*(q)[2])

/// Calculate the norm of a vector
#define NORM(v)   (sqrt((v)[0]*(v)[0] + (v)[1]*(v)[1] + (v)[2]*(v)[2]))

/// Normalize a vector (dimension 3)
#define NORMALIZE(inout){\
    double norm;\
    norm = sqrt((inout)[0]*(inout)[0] + (inout)[1]*(inout)[1] + (inout)[2]*(inout)[2]);\
    (inout)[0] = (inout)[0]/norm;\
    (inout)[1] = (inout)[1]/norm;\
    (inout)[2] = (inout)[2]/norm;}

/// Calculate the cross product
#define CROSS(out,a,b) \
    (out)[0] = (a)[1]*(b)[2] - (b)[1]*(a)[2]; \
    (out)[1] = (a)[2]*(b)[0] - (b)[2]*(a)[0]; \
    (out)[2] = (a)[0]*(b)[1] - (b)[0]*(a)[1];

/// Copy a 3D-array
#define COPY3(out,in)\
    (out)[0]=(in)[0];\
    (out)[1]=(in)[1];\
    (out)[2]=(in)[2];

/// Multiply 2 4x4 matrices
#define MULT_MAT(out,inA,inB)\
    (out)[0] = (inA)[0]*(inB)[0] + (inA)[4]*(inB)[1] + (inA)[8]*(inB)[2];\
    (out)[1] = (inA)[1]*(inB)[0] + (inA)[5]*(inB)[1] + (inA)[9]*(inB)[2];\
    (out)[2] = (inA)[2]*(inB)[0] + (inA)[6]*(inB)[1] + (inA)[10]*(inB)[2];\
    (out)[3] = 0;\
    (out)[4] = (inA)[0]*(inB)[4] + (inA)[4]*(inB)[5] + (inA)[8]*(inB)[6];\
    (out)[5] = (inA)[1]*(inB)[4] + (inA)[5]*(inB)[5] + (inA)[9]*(inB)[6];\
    (out)[6] = (inA)[2]*(inB)[4] + (inA)[6]*(inB)[5] + (inA)[10]*(inB)[6];\
    (out)[7] = 0;\
    (out)[8] = (inA)[0]*(inB)[8] + (inA)[4]*(inB)[9] + (inA)[8]*(inB)[10];\
    (out)[9] = (inA)[1]*(inB)[8] + (inA)[5]*(inB)[9] + (inA)[9]*(inB)[10];\
    (out)[10] = (inA)[2]*(inB)[8] + (inA)[6]*(inB)[9] + (inA)[10]*(inB)[10];\
    (out)[11] = 0;\
    (out)[12] = (inA)[0]*(inB)[12] + (inA)[4]*(inB)[13] + (inA)[8]*(inB)[14] + (inA)[12];\
    (out)[13] = (inA)[1]*(inB)[12] + (inA)[5]*(inB)[13] + (inA)[9]*(inB)[14] + (inA)[13];\
    (out)[14] = (inA)[2]*(inB)[12] + (inA)[6]*(inB)[13] + (inA)[10]*(inB)[14] + (inA)[14];\
    (out)[15] = 1;

/// Rotate a 3D vector (Multiply a 4x4 pose x 3D vector)
#define MULT_MAT_VECTOR(out,H,p)\
    (out)[0] = (H)[0]*(p)[0] + (H)[4]*(p)[1] + (H)[8]*(p)[2];\
    (out)[1] = (H)[1]*(p)[0] + (H)[5]*(p)[1] + (H)[9]*(p)[2];\
    (out)[2] = (H)[2]*(p)[0] + (H)[6]*(p)[1] + (H)[10]*(p)[2];

/// Translate a 3D point (Multiply a 4x4 pose x 3D point)
#define MULT_MAT_POINT(out,H,p)\
    (out)[0] = (H)[0]*(p)[0] + (H)[4]*(p)[1] + (H)[8]*(p)[2] + (H)[12];\
    (out)[1] = (H)[1]*(p)[0] + (H)[5]*(p)[1] + (H)[9]*(p)[2] + (H)[13];\
    (out)[2] = (H)[2]*(p)[0] + (H)[6]*(p)[1] + (H)[10]*(p)[2] + (H)[14];

    

/// The Color struct represents an RGBA color (each color component should be in the range [0-1])
struct tColor{
    /// Red color
    float r;

    /// Green color
    float g;

    /// Blue color
    float b;

    /// Alpha value (0 = transparent; 1 = opaque)
    float a;
};






//------------------------------------------------------------------------------------------------------------



/// \brief The tMatrix2D struct represents a variable size 2d Matrix. Use the Matrix2D_... functions to oeprate on this variable sized matrix.
/// This type of data can be used to get/set a program as a list. This is also useful for backwards compatibility functions related to RoKiSim.
struct tMatrix2D {
    /// Pointer to the data
    double *data;

    /// Pointer to the size array.
    int *size;

    /// Allocated size.
    int allocatedSize;

    /// Number of dimensions (usually 2)
    int numDimensions;

    bool canFreeData;
};




// -------------------------------------------


/// @brief Creates a new 2D matrix \ref Matrix2D.. Use \ref Matrix2D_Delete to delete the matrix (to free the memory).
/// The Procedure \ref Debug_Matrix2D shows an example to read data from a tMatrix2D
tMatrix2D* Matrix2D_Create();

/// @brief Deletes a \ref tMatrix2D.
/// @param[in] mat: Pointer of the pointer to the matrix
void Matrix2D_Delete(tMatrix2D **mat);

/// @brief Sets the size of a \ref tMatrix2D.
/// @param[in/out] mat: Pointer to the matrix
/// @param[in] rows: The number of rows.
/// @param[in] cols: The number of columns.
void Matrix2D_Set_Size(tMatrix2D *mat, int rows, int cols);

/// @brief Sets the size of a \ref tMatrix2D.
/// @param[in/out] mat: Pointer to the matrix
/// @param[in] dim: Dimension (1 or 2)
int Matrix2D_Size(const tMatrix2D *mat, int dim);

/// @brief Returns the number of columns of a \ref tMatrix2D.
/// @param[in] mat: Pointer to the matrix
/// Returns the number of columns (Second dimension)
int Matrix2D_Get_ncols(const tMatrix2D *var);

/// @brief Returns the number of rows of a \ref tMatrix2D.
/// @param[in] mat: Pointer to the matrix
/// Returns the number of rows (First dimension)
int Matrix2D_Get_nrows(const tMatrix2D *var);

/// @brief Returns the value at location [i,j] of a \ref tMatrix2D.
/// @param[in] mat: Pointer to the matrix
/// Returns the value of the cell
double Matrix2D_Get_ij(const tMatrix2D *var, int i, int j);

/// @brief Set the value at location [i,j] of a \ref tMatrix2D.
/// @param[in] mat: Pointer to the matrix
/// @param[in] i: Row
/// @param[in] j: Column
/// @param[in] value: matrix value
void Matrix2D_Set_ij(const tMatrix2D *var, int i, int j, double value);

/// @brief Returns the pointer of a column of a \ref tMatrix2D.
/// A column has \ref Matrix2D_Get_nrows(mat) values that can be accessed/modified from the returned pointer continuously.
/// @param[in] mat: Pointer to the matrix
/// @param[in] col: Column to retreive.
/// /return double array (internal pointer) to the column
double* Matrix2D_Get_col(const tMatrix2D *var, int col);

/// @brief Copy a Matrix2D
bool Matrix2D_Copy(const tMatrix2D *in, tMatrix2D *out);

/// @brief Show an array through STDOUT
/// Given an array of doubles, it generates a string
void Debug_Array(const double *array, int arraysize);

/// @brief Display the content of a \ref tMatrix2D through STDOUT. This is only intended for debug purposes.
/// @param[in] mat: Pointer to the matrix
void Debug_Matrix2D(const tMatrix2D *mat);

/// @brief Save a matrix as binary data
void Matrix2D_Save(QDataStream *st, tMatrix2D *emx);

/// @brief Save a matrix as text
void Matrix2D_Save(QTextStream *st, tMatrix2D *emx, bool csv=false);

/// @brief Load a matrix
void Matrix2D_Load(QDataStream *st, tMatrix2D **emx);


//--------------------- Joints class -----------------------

/// The tJoints class represents a joint position of a robot (robot axes).
class tJoints {

public:
    /// \brief tJoints
    /// \param ndofs number of robot joint axes or degrees of freedom
    tJoints(int ndofs = 0);

    /// \brief Set joint values given a double array and the number of joint values
    /// \param joints Pointer to the joint values
    /// \param ndofs Number of joints
    tJoints(const double *joints, int ndofs = 0);

    /// \brief Set joint values given a float array and the number of joint values
    /// \param joints Pointer to the joint values
    /// \param ndofs Number of joints
    tJoints(const float *joints, int ndofs = 0);

    /// \brief Create a copy of an object
    /// \param jnts
    tJoints(const tJoints &jnts);

    /// \brief Create joint values given a 2D matrix and the column selecting the desired values
    /// \param mat2d
    /// \param column
    /// \param ndofs
    tJoints(const tMatrix2D *mat2d, int column=0, int ndofs=-1);

    /// \brief Convert a string to joint values
    /// \param str Comma separated joint values (spaces or tabs are also accepted)
    tJoints(const QString &str);
    
    /// To String operator (use with qDebug() << tJoints;
    operator QString() const { return ToString(); }

    /// \brief Joint values
    /// \return Returns a pointer to the joint data array (doubles)
    const double *ValuesD() const;

    /// \brief Joint values
    /// \return Returns a pointer to the joint data array (floats)
    const float *ValuesF() const;

#ifdef ROBODK_API_FLOATS
    /// \brief Joint values
    /// \return Returns a pointer to the joint data array (doubles or floats if ROBODK_API_FLOATS is defined)
    const float *Values() const;
#else
    /// \brief Joint values
    /// \return Returns a pointer to the joint data array (doubles or floats if ROBODK_API_FLOATS is defined)
    const double *Values() const;
#endif



    double Compare(const tJoints &other) const;

    /// \brief
    /// \return Data same as Values. The only difference is that the array pointer is not const. This is provided for backwards compatibility.
    double *Data();

    /// \brief Number of joint axes of the robot (or degrees of freedom)
    /// \return
    int Length() const;
    
    /// Set the length of the array (only shrinking the array is allowed)
    void setLength(int new_length);

    /// \brief Check if the joints are valid. For example, when we request the Inverse kinematics and there is no solution the joints will not be valid.
    /// (for example, an invalid result after calling class: IItem::SolveIK returns a non valid joints)
    /// \return true if it has 1 degree of freedom or more
    bool Valid();

    /// \brief GetValues
    /// \param joints joint values in deg or mm
    /// \return returns the number of degrees of freedom
    int GetValues(double *joints);

    /// \brief Set the joint values in deg or mm. You can also important provide the number of degrees of freedom (6 for a 6 axis robot).
    /// \param joints joint values in deg or mm
    /// \param ndofs number of degrees of freedom (number of axes or joints)
    void SetValues(const double *joints, int ndofs = -1);

    /// \brief Set the joint values in deg or mm (floats). You can also important provide the number of degrees of freedom (6 for a 6 axis robot).
    /// \param joints joint values in deg or mm
    /// \param ndofs number of degrees of freedom (number of axes or joints)
    void SetValues(const float *joints, int ndofs = -1);

    /// \brief Retrieve a string representation of the joint values.
    /// \param separator String to add between consecutive joint values
    /// \param precision Number of decimals
    /// \return string as a QString
    QString ToString(const QString &separator=", ", int precision = 3) const ;

    /// \brief Set the joint values given a comma-separated string. Tabs and spaces are also allowed.
    /// \param str string. Such as "10, 20, 30, 40, 50, 60"
    /// \return false if parsing the string failed. True otherwise.
    bool FromString(const QString &str);


public:
    /// number of degrees of freedom
    int _nDOFs;

    /// joint values (doubles, used to store the joint values)
    double _Values[RDK_SIZE_JOINTS_MAX];

    /// joint values (floats, used to return a copy as a float pointer)
    mutable float _ValuesF[RDK_SIZE_JOINTS_MAX];
};




/// \brief The Mat class represents a 4x4 pose matrix. The main purpose of this object is to represent a pose in the 3D space (position and orientation).
/// In other words, a pose is a 4x4 matrix that represents the position and orientation of one reference frame with respect to another one, in the 3D space.
/// Poses are commonly used in robotics to place objects, reference frames and targets with respect to each other.
/// <br>
/// \f$ transl(x,y,z) rotx(r) roty(p) rotz(w) = \\
/// \begin{bmatrix} n_x & o_x & a_x & x \\
/// n_y & o_y & a_y & y \\
/// n_z & o_z & a_z & z \\
/// 0 & 0 & 0 & 1 \end{bmatrix} \f$
class Mat : public QMatrix4x4 {

public:

    /// Create the identity matrix
    Mat();

    /// Create a valid or an invalid matrix
    Mat(bool valid);

    /// Create a copy of the matrix
    Mat(const QMatrix4x4 &matrix);

    /// \brief Create a copy of the matrix
    /// \param matrix
    Mat(const Mat &matrix);

    /// <summary>
    /// Matrix class constructor for a 4x4 homogeneous matrix given N, O, A & T vectors
    /// </summary>
    /// <param name="nx">Matrix[0,0]</param>
    /// <param name="ox">Matrix[0,1]</param>
    /// <param name="ax">Matrix[0,2]</param>
    /// <param name="tx">Matrix[0,3]</param>
    /// <param name="ny">Matrix[1,0]</param>
    /// <param name="oy">Matrix[1,1]</param>
    /// <param name="ay">Matrix[1,2]</param>
    /// <param name="ty">Matrix[1,3]</param>
    /// <param name="nz">Matrix[2,0]</param>
    /// <param name="oz">Matrix[2,1]</param>
    /// <param name="az">Matrix[2,2]</param>
    /// <param name="tz">Matrix[2,3]</param>
    /// <returns> \f$ \begin{bmatrix} n_x & o_x & a_x & x \\
    /// n_y & o_y & a_y & y \\
    /// n_z & o_z & a_z & z \\
    /// 0 & 0 & 0 & 1 \end{bmatrix} \f$
    /// </returns>
    Mat(double nx, double ox, double ax, double tx, double ny, double oy, double ay, double ty, double nz, double oz, double az, double tz);

    /// \brief Create a homogeneoux matrix given a one dimensional 16-value array (doubles)
    /// \param values [nx,ny,nz,0, ox,oy,oz,0, ax,ay,az,0,  tx,ty,tz,1]
    /// <returns> \f$ \begin{bmatrix} n_x & o_x & a_x & x \\
    /// n_y & o_y & a_y & y \\
    /// n_z & o_z & a_z & z \\
    /// 0 & 0 & 0 & 1 \end{bmatrix} \f$
    /// </returns>
    Mat(const double values[16]);

    /// \brief Create a homogeneoux matrix given a one dimensional 16-value array (floats)
    /// \param values [nx,ny,nz,0, ox,oy,oz,0, ax,ay,az,0,  tx,ty,tz,1]
    /// <returns> \f$ transl(x,y,z) rotx(r) roty(p) rotz(w) = \\
    /// \begin{bmatrix} n_x & o_x & a_x & x \\
    /// n_y & o_y & a_y & y \\
    /// n_z & o_z & a_z & z \\
    /// 0 & 0 & 0 & 1 \end{bmatrix} \f$
    /// </returns>
    Mat(const float values[16]);

    /// <summary>
    /// Create a translation matrix.
    /// </summary>
    /// <param name="x">translation along X (mm)</param>
    /// <param name="y">translation along Y (mm)</param>
    /// <param name="z">translation along Z (mm)</param>
    /// <returns>
    /// \f$ rotx(\theta) = \begin{bmatrix} 1 & 0 & 0 & x \\
    /// 0 & 1 & 0 & y \\
    /// 0 & 0 & 1 & z \\
    /// 0 & 0 & 0 & 1 \\
    /// \end{bmatrix} \f$
    /// </returns>
    Mat(double x, double y, double z);

    ~Mat();
    
    /// To String operator (use with qDebug() << tJoints;
    operator QString() const { return ToString(); }

    /// Set the X vector values (N vector)
    void setVX(double x, double y, double z);

    /// Set the Y vector values (O vector)
    void setVY(double x, double y, double z);

    /// Set the Z vector values (A vector)
    void setVZ(double x, double y, double z);

    /// Set the position (T position) in mm
    void setPos(double x, double y, double z);

    /// Set the X vector values (N vector)
    void setVX(double xyz[3]);

    /// Set the Y vector values (O vector)
    void setVY(double xyz[3]);

    /// Set the Z vector values (A vector)
    void setVZ(double xyz[3]);

    /// Set the position (T position) in mm
    void setPos(double xyz[3]);

    /// Set the pose values
    void setValues(double pose[16]);

    /// Get the X vector (N vector)
    void VX(tXYZ xyz) const;

    /// Get the Y vector (O vector)
    void VY(tXYZ xyz) const;

    /// Get the Z vector (A vector)
    void VZ(tXYZ xyz) const;

    /// Get the position (T position), in mm
    void Pos(tXYZ xyz) const;    
    
    /// \brief Set a matrix value
    /// \param r row
    /// \param c column
    /// \param value value
    void Set(int r, int c, double value);

    /// \brief Get a matrix value
    /// \param r row
    /// \param c column
    /// \return value
    double Get(int r, int c) const;

    /// Invert the pose (homogeneous matrix assumed)
    Mat inv() const;
    
    /// Returns true if the matrix is homogeneous, otherwise it returns false
    bool isHomogeneous() const;

    /// Forces 4x4 matrix to be homogeneous (vx,vy,vz must be unitary vectors and respect: vx x vy = vz). Returns True if the matrix was not homogeneous and it was be modified to make it homogeneous.
    bool MakeHomogeneous();

    //------ Pose to xyzrpw and xyzrpw to pose------------

    /// <summary>
    /// Calculates the equivalent position and euler angles ([x,y,z,r,p,w] vector) of the given pose
    /// Note: transl(x,y,z)*rotz(w*pi/180)*roty(p*pi/180)*rotx(r*pi/180)
    /// See also: FromXYZRPW()
    /// </summary>
    /// <returns>XYZWPR translation and rotation in mm and degrees</returns>
    void ToXYZRPW(tXYZWPR xyzwpr) const;

    /// \brief Retrieve a string representation of the pose
    /// \param separator String separator
    /// \param precision Number of decimals
    /// \param in_xyzwpr if set to true (default), the pose will be represented as XYZWPR 6-dimensional array using ToXYZRPW
    /// \return
    QString ToString(const QString &separator=", ", int precision = 3, bool xyzrpw_only = false) const;

    /// Set the matrix given a XYZRPW string array (6-values)
    bool FromString(const QString &str);

    /// <summary>
    /// Calculates the pose from the position and euler angles ([x,y,z,r,p,w] vector)
    /// The result is the same as:
    /// <br>
    /// H = transl(x,y,z)*rotz(w*pi/180)*roty(p*pi/180)*rotx(r*pi/180)
    /// </summary>
    /// <returns>Homogeneous matrix (4x4)</returns>
    void FromXYZRPW(tXYZWPR xyzwpr);

    /// <summary>
    /// Calculates the pose from the position and euler angles ([x,y,z,r,p,w] vector)
    /// The result is the same as:
    /// <br>
    /// H = transl(x,y,z)*rotz(w*pi/180)*roty(p*pi/180)*rotx(r*pi/180)
    /// </summary>
    /// <returns>Homogeneous matrix (4x4)</returns>
    static Mat XYZRPW_2_Mat(double x, double y, double z, double r, double p, double w);
    static Mat XYZRPW_2_Mat(tXYZWPR xyzwpr);

    /// Get a pointer to the 16-digit double array.
    const double* ValuesD() const;

    /// Get a pointer to the 16-digit array as an array of floats.
    const float* ValuesF() const;

#ifdef ROBODK_API_FLOATS
    /// Get a pointer to the 16-digit array (doubles or floats if ROBODK_API_FLOATS is defined).
    const float* Values() const;
#else
    /// Get a pointer to the 16-digit array (doubles or floats if ROBODK_API_FLOATS is defined).
    const double* Values() const;
#endif

    /// Copy the 16-values of the 4x4 matrix to a double array.
    void Values(double values[16]) const;

    /// Copy the 16-values of the 4x4 matrix to a double array.
    void Values(float values[16]) const;

    /// Check if the matrix is valid
    bool Valid() const;

    /// <summary>
    /// Return a translation matrix.
    /// </summary>
    /// <param name="x">translation along X (mm)</param>
    /// <param name="y">translation along Y (mm)</param>
    /// <param name="z">translation along Z (mm)</param>
    /// <returns>
    /// \f$ rotx(\theta) = \begin{bmatrix} 1 & 0 & 0 & x \\
    /// 0 & 1 & 0 & y \\
    /// 0 & 0 & 1 & z \\
    /// 0 & 0 & 0 & 1 \\
    /// \end{bmatrix} \f$
    /// </returns>
    static Mat transl(double x, double y, double z);

    /// <summary>
    /// Return the X-axis rotation matrix.
    /// </summary>
    /// <param name="rx">Rotation around X axis (in radians).</param>
    /// <returns>
    /// \f$ rotx(\theta) = \begin{bmatrix} 1 & 0 & 0 & 0 \\
    /// 0 & c_\theta & -s_\theta & 0 \\
    /// 0 & s_\theta & c_\theta & 0 \\
    /// 0 & 0 & 0 & 1 \\
    /// \end{bmatrix} \f$
    /// </returns>
    static Mat rotx(double rx);

    /// <summary>
    /// Return a Y-axis rotation matrix
    /// </summary>
    /// <param name="ry">Rotation around Y axis (in radians)</param>
    /// <returns>
    /// \f$ roty(\theta) = \begin{bmatrix} c_\theta & 0 & s_\theta & 0 \\
    /// 0 & 1 & 0 & 0 \\
    /// -s_\theta & 0 & c_\theta & 0 \\
    /// 0 & 0 & 0 & 1 \\
    /// \end{bmatrix} \f$
    /// </returns>
    static Mat roty(double ry);

    /// <summary>
    /// Return a Z-axis rotation matrix.
    /// </summary>
    /// <param name="rz">Rotation around Z axis (in radians)</param>
    /// <returns>
    /// \f$ rotz(\theta) = \begin{bmatrix} c_\theta & -s_\theta & 0 & 0 \\
    /// s_\theta & c_\theta & 0 & 0 \\
    /// 0 & 0 & 1 & 0 \\
    /// 0 & 0 & 0 & 1 \\
    /// \end{bmatrix} \f$
    /// </returns>
    static Mat rotz(double rz);

private:
    /// Flags if a matrix is not valid.
    double _valid;

// this is a dummy variable to easily obtain a pointer to a 16-double-array for matrix multiplications
private:
    /// Copy of the data as a double array.
    mutable double _ddata16[16];
};

/// Translation matrix class: Mat::transl.
Mat transl(double x, double y, double z);

/// Translation matrix class: Mat::rotx.
Mat rotx(double rx);

/// Translation matrix class: Mat::roty.
Mat roty(double ry);

/// Translation matrix class: Mat::rotz.
Mat rotz(double rz);

//QDataStream &operator<<(QDataStream &data, const QMatrix4x4 &);
inline QDebug operator<<(QDebug dbg, const Mat &m){ return dbg.noquote() << m.ToString(); }
inline QDebug operator<<(QDebug dbg, const tJoints &jnts){ return dbg.noquote() << jnts.ToString(); }

inline QDebug operator<<(QDebug dbg, const Mat *m){ return dbg.noquote() << (m == nullptr ? "Mat(null)" : m->ToString()); }
inline QDebug operator<<(QDebug dbg, const tJoints *jnts){ return dbg.noquote() << (jnts == nullptr ? "tJoints(null)" : jnts->ToString()); }



#endif // ROBODKTYPES_H
