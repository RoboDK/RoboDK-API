// Copyright 2015-2018 - RoboDK Inc. - https://robodk.com/
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
// http://www.apache.org/licenses/LICENSE-2.0
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
//
// --------------------------------------------
// --------------- DESCRIPTION ----------------
// This file defines the following two classes:
//     Joints : for 1D arrays representing joint values
//     Mat : for pose multiplications
//     RoboDK (Robolink()) : Main interface with RoboDK
//     Item : Represents an item in the RoboDK station
// These classes are the objects used to interact with RoboDK and create macros.
// An item is an object in the RoboDK tree (it can be either a robot, an object, a tool, a frame, a program, ...).
// Items can be retrieved from the RoboDK station using the Robolink() object (such as Robolink.Item() method)
//
// In this document: pose = transformation matrix = homogeneous matrix = 4x4 matrix
//
// More information about the RoboDK API here:
//     https://robodk.com/doc/en/RoboDK-API.html
//     https://robodk.com/doc/en/PythonAPI/index.html
//
// More information about RoboDK post processors here:
//     https://robodk.com/help#PostProcessor
//
// Visit the Matrix and Quaternions FAQ for more information about pose/homogeneous transformations
//     http://www.j3d.org/matrix_faq/matrfaq_latest.html
//
//---------------------------------------------
// TIPS:
//  1- Add #define RDK_SKIP_NAMESPACE
//     to avoid using the RoboDK_API namespace
//  2- Add #define RDK_WITH_EXPORTS  (and RDK_EXPORTS)
//     to generate/import as a DLL
//---------------------------------------------


/*! \mainpage RoboDK API for C++
*
* \section LinkIntro Introduction
*
* This section of the documentation is an introduction to the RoboDK API for C++.
*
* The RoboDK API allows creating simulations for industrial robots and generate vendor-specific robot programs.
* While RoboDK's graphical user interface can be used to create programs, it is possible to extend the robot controller limitations by using a universal programming language such as C++.
* The RoboDK API is available in C++, C#, Python, Matlab and Visual Basic.
*
* \image html RoboDK-API-Cpp.png width=800
*
* With the RoboDK API it is possible to simulate and program any industrial robot using your preferred programming language.
* This avoids using vendor-specific programming languages.
*
* Note: This RoboDK API is not the Plugin Interface:
* - https://robodk.com/doc/en/PlugIns/index.html.
*
* More information here: \ref LinkPluginAPI.
*
* \section Classes
*
* The RoboDK API for C++ is implemented in 2 files (robodk_api.h and robodk_api.cpp). These files define the following classes.
*
* \subsection LinkRoboDKAPI RoboDK class
* The RoboDK class defines the interface to the RoboDK API. The original Python reference is available here: https://robodk.com/doc/en/RoboDK-API.html#RoboDKAPI.
*
* More information about the RoboDK API is available here:
* - Python Reference: https://robodk.com/doc/en/PythonAPI/robolink.html
*
* \subsection LinkItem Item class
* The Item class can be used to operate on any item available in the RoboDK tree. Use functions such as class: IRoboDK::getItem or class: IRoboDK::getItemList to retrieve items from the RoboDK station tree.
* Item is a pointer to IItem. Items should be deleted using class: IItem::Delete (not using the class destructor).
*
* More information about the RoboDK Item class (based on the Python API) is available here:
* - https://robodk.com/doc/en/PythonAPI/robolink.html#robolink-item.
*
* \image html station-tree.png width=800
*
* \subsection LinkTypes RoboDK types file
* The RoboDK API defines a set of types used by the RoboDK API. Including:
* - The Mat class for Pose manipulations.
* - The tJoints class to represent robot joint variables
* - The tMatrix2D data structure to represent a variable size 2D matrix (mostly used for internal purposes)
*
* \section LinkPluginAPI Plug-In Interface vs. RoboDK API
* The RoboDK API is a generic set of commands that allows you to interact with RoboDK and automate tasks. The RoboDK API is used by default when macros are used in RoboDK.
* The RoboDK Plug-In is a library (DLL) that can be loaded by RoboDK to extend certain features and customize the RoboDK interface. The interface includes an interface to the RoboDK API.
*
* The main advantages of using the RoboDK API through a Plug-In Inteface are the following:
* - The RoboDK API is much faster because it is loaded as a library (a RoboDK Plug-In is actually a library loaded by RoboDK).
* - You can customize the appearance of RoboDK's main window (including the menu, toolbar, and add docked windows).
*
* You should pay attention to the following when using the RoboDK API inside a Plug-In:
* - Items (Item/IItem) are pointers, not objects. You can check if an item is valid or not by checking if it is a null pointer (nullptr).
* - You must call class: IRoboDK::Render every time you want to update the screen (for example, if you change the position of a robot using class: IItem::Joints). Updading the screen is not done automatically.
* - Plug-Ins can only be deployed as C++ code using Qt libraries.
*
* \section LinkRequirements Requirements
* The RoboDK API uses Qt libraries and an example is provided created using Qt Creator.
* It is recommended to use the \ref APIExample project to get started with your new project (double click RoboDK-API-Cpp-Sample.pro to open it with Qt Creator).
*
*
* \section LinkInstall Installation Requirements
* Requirements to make RoboDK Plug-Ins work:
* - It is required to install RoboDK (v3.5.4 or later): https://robodk.com/download
* - You should install Qt libraries and Qt Creator (unless you are planning to use Qt libraries on Visual Studio).
*
* \image html qttoolkit.png width=800
*
*
*
* \section LinkExample Offline Programming Example
* The following code (C++) shows an example that uses the RoboDK API for robot simulation and offline programming::
* ```
*    // Draw a hexagon inside a circle of radius 100.0 mm
*    int n_sides = 6;
*    float size = 100.0;
*    // retrieve the reference frame and the tool frame (TCP)
*    Mat pose_frame = ROBOT->PoseFrame();
*    Mat pose_tool = ROBOT->PoseTool();
*    Mat pose_ref = ROBOT->Pose();
*
*    // Program start
*    ROBOT->MoveJ(pose_ref);
*    ROBOT->setPoseFrame(pose_frame);  // set the reference frame
*    ROBOT->setPoseTool(pose_tool);    // set the tool frame: important for Online Programming
*    ROBOT->setSpeed(100);             // Set Speed to 100 mm/s
*    ROBOT->setRounding(5);            // set the rounding instruction (C_DIS & APO_DIS / CNT / ZoneData / Blend Radius / ...)
*    ROBOT->RunInstruction("CallOnStart"); // run a program
*    for (int i = 0; i <= n_sides; i++) {
*        // calculate angle in degrees:
*        double angle = ((double) i / n_sides) * 360.0;
*
*        // create a pose relative to the pose_ref
*        Mat pose_i(pose_ref);
*        pose_i.rotate(angle,0,0,1.0);
*        pose_i.translate(size, 0, 0);
*        pose_i.rotate(-angle,0,0,1.0);
*
*        // add a comment (when generating code)
*        ROBOT->RunInstruction("Moving to point " + QString::number(i), RoboDK::INSTRUCTION_COMMENT);
*
*        // example to retrieve the pose as Euler angles (X,Y,Z,W,P,R)
*        double xyzwpr[6];
*        pose_i.ToXYZRPW(xyzwpr);
*
*        ROBOT->MoveL(pose_i);  // move the robot
*    }
*    ROBOT->RunInstruction("CallOnFinish");
*    ROBOT->MoveL(pose_ref);     // move back to the reference point
*
* ```
*
* The same script used for simulation can be used for offline programming, this means that the corresponding program can be generated for the robot controller. RoboDK supports a large number of robot controllers and it is easy to include compatibility for new robot controllers using Post Processors.
*
* For more Examples:
*  * https://robodk.com/doc/en/PythonAPI/examples.html
*
* For more information about robot post processors:
*  * [Quick introduction to RoboDK post processors](https://robodk.com/help#PostProcessor)
*  * [How to use Post Processors](https://robodk.com/doc/en/Post-Processors.html)
*  * [Technical Reference](https://robodk.com/doc/en/PythonAPI/postprocessor.html)
*
* \section LinkSupportedRobots Supported robots
*
* The following list includes the robot controllers supported by RoboDK:
*  * ABB RAPID IRC5: for ABB IRC5 robot controllers
*  * ABB RAPID S4C: for ABB S4C robot controllers
*  * Adept Vplus: for Adept V+ programming language
*  * Allen Bradley Logix5000: for Allen Bradley Logix5000 PCL
*  * CLOOS: for cloos robot controllers
*  * Comau C5G: for Comau C5G robot controllers
*  * Denso PAC: for Denso RC7 (and older) robot controllers (PAC programming language)
*  * Denso RC8: for Denso RC8 (and newer) robot controllers (PacScript programming language)
*  * Dobot: for educational Dobot robots
*  * Fanuc R30iA: for Fanuc R30iA and R30iB robot controllers
*  * Fanuc R30iA Arc: for Fanuc Arc welding
*  * Fanuc RJ3: for Fanuc RJ3 robot controllers
*  * GCode BnR: for B&R robot controllers
*  * GSK: for GSK robots
*  * HIWIN HRSS: for HIWIN robots
*  * KAIRO: for Keba Kairo robot controllers
*  * KUKA IIWA: for KUKA IIWA sunrise programming in Java
*  * KUKA KRC2: for KUKA KRC2 robot controllers
*  * KUKA KRC2 CamRob: for KUKA CamRob milling option
*  * KUKA KRC2 DAT: for KUKA KRC2 robot controllers including DAT data files
*  * KUKA KRC4: for KUKA KRC4 robot controllers
*  * KUKA KRC4 Config: for KUKA KRC4 robot controllers with configuration data in each line
*  * KUKA KRC4 DAT: for KUKA KRC4 robot controllers including DAT data files
*  * Kawasaki: for Kawasaki AS robot controllers
*  * Mecademic: for Mecademic Meca500 robot
*  * Motoman/Yaskawa: For Motoman robot controllers (JBI II and JBI III programming)
*  * Mitsubishi: for Mitsubishi robot controllers
*  * Nachi AX FD: for Nachi AX and FD robot controllers
*  * Daihen OTC: for Daihen OTC robot controllers
*  * Precise: for Precise Scara robots
*  * Siemens Sinumerik: for Siemens Sinumerik ROBX robot controller
*  * Staubli VAL3: for Staubli VAL3 robot programs (CS8 controllers and later)
*  * Staubli VAL3 InlineMove: to generate Staubli VAL3 programs with inline movement data
*  * Staubli S6: for Staubli S6 robot controllers
*  * Toshiba: for Toshiba robots
*  * Universal Robots: for UR robots, generates linear movements as pose targets
*  * Universal Robots RobotiQ: for UR robots including support for RobotiQ gripper
*  * Universal Robots joints: for UR robots, generates linear movements as joint targets
*  * Yamaha: for Yamaha robots
*
*
*
*
*
* \section LinkQt Qt Tips
* The C++ version of the RoboDK API is based on Qt. Qt is a set of useful libraries for C++ and Qt Creator is the default development environment (IDE) for Qt.
*
* This list provides some useful links and tips for programming with Qt:
* - Double click the RoboDK-API-Cpp-Sample.pro file to open the example project using Qt Creator.
* - Use Qt signal/slots mechanism for action/button callbacks (http://doc.qt.io/qt-5/signalsandslots.html). Signals and slots are thread safe.
* - Wrap your strings using tr("your string") or QObject::tr("your string") to allow translation using Qt Linguist. For more information: http://doc.qt.io/qt-5/qtlinguist-index.html.
* - If you experience strange build issues it may be useful to delete the build folder that is automatically created to force a new build.
* - If you experience strange plugin load issues in RoboDK it is recommended to delete the libraries and create the plugin library with a new build.
* - More information about Qt: https://www.qt.io/.
*
*
* \section LinkRefs Useful Links
* Useful links involving the RoboDK API:
* - Standard RoboDK API Introduction: https://robodk.com/doc/en/RoboDK-API.html#RoboDKAPI.
* - Standard RoboDK API Reference (based on Python): https://robodk.com/doc/en/PythonAPI/robolink.html.
* - Latest RoboDK API on GitHub (you'll find RoboDK C++ in a subfolder): https://github.com/RoboDK/RoboDK-API.
* - RoboDK API Introductory video: https://www.youtube.com/watch?v=3I6OK1Kd2Eo.
* - RoboDK API using the Plugin Interface: https://robodk.com/doc/en/PlugIns/index.html.
*
*/









#ifndef ROBODK_API_H
#define ROBODK_API_H



#ifdef RDK_WITH_EXPORTS
    #ifdef RDK_EXPORTS
    #define ROBODK __declspec(dllexport)
    #else
    #define ROBODK __declspec(dllimport)
    #endif
#else
    #define ROBODK
#endif


#include <QtCore/QString>
#include <QtGui/QMatrix4x4> // this should not be part of the QtGui! it is just a matrix
#include <QDebug>


class QTcpSocket;


#ifndef RDK_SKIP_NAMESPACE

/// All RoboDK API functions are wrapped in the RoboDK_API namespace. If you prefer to forget about the RoboDK_API you can define RDK_SKIP_NAMESPACE (add the define: RDK_SKIP_NAMESPACE)
namespace RoboDK_API {
#endif


class Item;
class RoboDK;


/// maximum size of robot joints (maximum allowed degrees of freedom for a robot)
#define RDK_SIZE_JOINTS_MAX 12
// IMPORTANT!! Do not change this value

/// Constant defining the size of a robot configuration (at least 3 doubles are required)
#define RDK_SIZE_MAX_CONFIG 4
// IMPORTANT!! Do not change this value

/// Six doubles that represent robot joints (usually in degrees)
//typedef double tJoints[RDK_SIZE_JOINTS_MAX];


/// @brief tXYZWPR (mm, rad) holds the same information as a \ref tMatrix4x4 pose but represented as XYZ position (in mm) and WPR orientation (in rad) (XYZWPR = [X,Y,Z,W,P,R])
/// This type of variable is easier to read and it is what most robot controllers use to input a pose. However, for internal calculations it is better to use a 4x4 pose matrix as it is faster and more accurate.
/// To calculate a 4x4 matrix: pose4x4 = transl(X,Y,Z)*rotx(W)*roty(P)*rotz(R)
/// See \ref POSE_2_XYZWPR and \ref XYZWPR_2_POSE to exchange between \ref tMatrix4x4 and \ref tXYZWPR
typedef double tXYZWPR[6];

/// @brief tXYZ (mm) represents a position or a vector in mm
typedef double tXYZ[3];


/// @brief The robot configuration defines a specific state of the robot without crossing any singularities. Changing the configuration requires crossing a singularity.
/// There are 2x2x2=8 different configurations.
/// A robot configurations is also known by "Assembly mode"
/// The robot configuration is defined as an array of 3 doubles: [FACING REAR, LOWER ARM, WRIST FLIP].
/// FACING REAR=0 means FACING FRONT
/// LOWER ARM=0 means ELBOW UP
/// WRIST FLIP=0 means WRIST NON FLIP
/// the 4th value is reserved
typedef double tConfig[RDK_SIZE_MAX_CONFIG];


/// Calculate the dot product
#define DOT(v,q)   ((v)[0]*(q)[0] + (v)[1]*(q)[1] + (v)[2]*(q)[2])

/// Calculate the normal product
#define NORM(v)   (sqrt((v)[0]*(v)[0] + (v)[1]*(v)[1] + (v)[2]*(v)[2]))

/// Apply the cross product
#define CROSS(out,a,b) \
    (out)[0] = (a)[1]*(b)[2] - (b)[1]*(a)[2]; \
    (out)[1] = (a)[2]*(b)[0] - (b)[2]*(a)[0]; \
    (out)[2] = (a)[0]*(b)[1] - (b)[0]*(a)[1];

/// Normalize a vector (dimension 3)
#define NORMALIZE(inout){\
    double norm;\
    norm = sqrt((inout)[0]*(inout)[0] + (inout)[1]*(inout)[1] + (inout)[2]*(inout)[2]);\
    (inout)[0] = (inout)[0]/norm;\
    (inout)[1] = (inout)[1]/norm;\
    (inout)[2] = (inout)[2]/norm;}



/// The Color struct represents an RGBA color (each color component should be in the range [0-1])
struct Color{
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





//--------------------- Joints class -----------------------

/// The tJoints class represents a joint position of a robot (robot axes).
class ROBODK tJoints {

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
    bool Valid() const;

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
    QString ToString(const QString &separator=", ", int precision = 3) const;

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
    float _ValuesF[RDK_SIZE_JOINTS_MAX];
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
class ROBODK Mat : public QMatrix4x4 {

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
    /// \param xyzwpr_only if set to true (default) the pose will be represented as XYZWPR 6-dimensional array using ToXYZRPW, if set to false, it will include information about the pose
    /// \return
    QString ToString(const QString &separator=", ", int precision = 3, bool xyzwpr_only = false) const;

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
    double _ddata16[16];

};

/// <summary>
/// This class is the iterface to the RoboDK API. With the RoboDK API you can automate certain tasks and operate on items.
/// Interactions with items in the station tree are made through Items (IItem).
/// An item is an object in the RoboDK tree (it can be either a robot, an object, a tool, a frame, a program, ...).
/// </summary>
class ROBODK RoboDK {
    friend class RoboDK_API::Item;


public:
    RoboDK(const QString &robodk_ip="", int com_port=-1, const QString &args="", const QString &path="");
    ~RoboDK();

    quint64 ProcessID();
    quint64 WindowID();

    bool Connected();
    bool Connect();

    void Disconnect();
    void Finish();


    /// <summary>
    /// Returns an item by its name. If there is no exact match it will return the last closest match.
    /// </summary>
    /// <param name="name">Item name</param>
    /// <param name="itemtype">Filter by item type RoboDK.ITEM_TYPE_...</param>
    /// <returns>Item or nullptr if no item was found</returns>
    Item getItem(QString name, int itemtype = -1);

    /// <summary>
    /// Returns a list of items (list of names or Items) of all available items in the currently open station in RoboDK.
    /// Optionally, use a filter to return specific items (example: getItemListNames(filter = ITEM_TYPE_ROBOT))
    /// </summary>
    /// <param name="filter">ITEM_TYPE_...</param>
    /// <returns>List of item names</returns>
    QStringList getItemListNames(int filter = -1);

    /// <summary>
    /// Returns a list of items (list of names or pointers) of all available items in the currently open station in RoboDK.
    /// Optionally, use a filter to return specific items (example: getItemListNames(filter = ITEM_CASE_ROBOT))
    /// </summary>
    /// <param name="filter">ITEM_TYPE</param>
    /// <returns>List of items with a match</returns>
    QList<Item> getItemList(int filter = -1);

    /// <summary>
    /// Shows a RoboDK popup to select one object from the open RoboDK station.
    /// An item type can be specified to filter desired items. If no type is specified, all items are selectable.
    /// </summary>
    /// <param name="message">Message to show in the pop up</param>
    /// <param name="itemtype">optionally filter by RoboDK.ITEM_TYPE_*</param>
    /// <returns>Picked item or nullptr if the user selected Cancel</returns>
    Item ItemUserPick(const QString &message = "Pick one item", int itemtype = -1);

    /// <summary>
    /// Shows or raises the RoboDK window.
    /// </summary>
    void ShowRoboDK();

    /// <summary>
    /// Hides the RoboDK window. RoboDK will continue running in the background.
    /// </summary>
    void HideRoboDK();

    /// <summary>
    /// Closes RoboDK window and finishes RoboDK execution
    /// </summary>
    void CloseRoboDK();

    /// <summary>
    /// Return the vesion of RoboDK as a 4 digit string: Major.Minor.Revision.Build
    /// </summary>
    QString Version();

    /// <summary>
    /// Set the state of the RoboDK window
    /// </summary>
    /// <param name="windowstate"></param>
    void setWindowState(int windowstate = WINDOWSTATE_NORMAL);

    /// <summary>
    /// Update the RoboDK flags. RoboDK flags allow defining how much access the user has to certain RoboDK features. Use FLAG_ROBODK_* variables to set one or more flags.
    /// </summary>
    /// <param name="flags">state of the window(FLAG_ROBODK_*)</param>
    void setFlagsRoboDK(int flags = FLAG_ROBODK_ALL);

    /// <summary>
    /// Update item flags. Item flags allow defining how much access the user has to item-specific features. Use FLAG_ITEM_* flags to set one or more flags.
    /// </summary>
    /// <param name="item"></param>
    /// <param name="flags">New flags</param>
    void setFlagsItem(Item item, int flags = FLAG_ITEM_ALL);

    /// <summary>
    /// Retrieve current item flags. Item flags allow defining how much access the user has to item-specific features. Use FLAG_ITEM_* flags to set one or more flags.
    /// </summary>
    /// <param name="item"></param>
    /// <returns></returns>
    int getFlagsItem(Item item);

    /// <summary>
    /// Show a message in RoboDK (it can be blocking or non blocking in the status bar)
    /// </summary>
    /// <param name="message">Message to display</param>
    /// <param name="popup">Set to true to make the message blocking or set to false to make it non blocking</param>
    void ShowMessage(const QString &message, bool popup = true);

    /// <summary>
    /// Loads a file and attaches it to parent. It can be any file supported by RoboDK.
    /// </summary>
    /// <param name="filename">Absolute path of the file.</param>
    /// <param name="parent">Parent to attach. Leave empty for new stations or to load an object at the station root.</param>
    /// <returns>Newly added object. Check with item.Valid() for a successful load.</returns>
    Item AddFile(const QString &filename, const Item *parent=NULL);

    /// <summary>
    /// Save an item to a file. If no item is provided, the open station is saved.
    /// </summary>
    /// <param name="filename">Absolute path to save the file</param>
    /// <param name="itemsave">Object or station to save. Leave empty to automatically save the current station.</param>
    void Save(const QString &filename, const Item *itemsave=NULL);

    /// <summary>
    /// Adds a shape provided triangle coordinates. Triangles must be provided as a list of vertices. A vertex normal can be provided optionally.
    /// </summary>
    /// <param name="trianglePoints">List of vertices grouped by triangles (3xN or 6xN matrix, N must be multiple of 3 because vertices must be stacked by groups of 3)</param>
    /// <param name="addTo">item to attach the newly added geometry (optional). Leave empty to create a new object.</param>
    /// <param name="shapeOverride">Set to true to replace any other existing geometry</param>
    /// <param name="color">Optionally specify the color as RGBA [0-1]</param>
    /// <returns>Added or modified item</returns>
    Item AddShape(tMatrix2D *trianglePoints,Item *addTo = NULL, bool shapeOverride = false, Color *color = NULL);

    /// <summary>
    /// Adds a curve provided point coordinates. The provided points must be a list of vertices. A vertex normal can be provided optionally.
    /// </summary>
    /// <param name="curve_points">matrix 3xN or 6xN -> N must be multiple of 3</param>
    /// <param name="reference_object">object to add the curve and/or project the curve to the surface</param>
    /// <param name="add_to_ref">If True, the curve will be added as part of the object in the RoboDK item tree (a reference object must be provided)</param>
    /// <param name="projection_type">Type of projection. For example: PROJECTION_ALONG_NORMAL_RECALC will project along the point normal and recalculate the normal vector on the surface projected.</param>
    /// <returns>added object/curve (null if failed)</returns>
    Item AddCurve(tMatrix2D *curvePoints,Item *referenceObject = NULL,bool addToRef = false,int ProjectionType = PROJECTION_ALONG_NORMAL_RECALC);

    /// <summary>
    /// Adds a list of points to an object. The provided points must be a list of vertices. A vertex normal can be provided optionally.
    /// </summary>
    /// <param name="points">list of points as a matrix (3xN matrix, or 6xN to provide point normals as ijk vectors)</param>
    /// <param name="reference_object">item to attach the newly added geometry (optional)</param>
    /// <param name="add_to_ref">If True, the points will be added as part of the object in the RoboDK item tree (a reference object must be provided)</param>
    /// <param name="projection_type">Type of projection.Use the PROJECTION_* flags.</param>
    /// <returns>added object/shape (0 if failed)</returns>
    Item AddPoints(tMatrix2D *points, Item *referenceObject = NULL, bool addToRef = false, int ProjectionType =  PROJECTION_ALONG_NORMAL_RECALC);

    /// <summary>
    /// Projects a point given its coordinates. The provided points must be a list of [XYZ] coordinates. Optionally, a vertex normal can be provided [XYZijk].
    /// </summary>
    /// <param name="points">Matrix 3xN or 6xN: list of points to project.</param>
    /// <param name="projected">Projected points as a null/empty matrix. A new matrix will be created</param>
    /// <param name="object_project">Object to project.</param>
    /// <param name="projection_type">Type of projection. For example: PROJECTION_ALONG_NORMAL_RECALC will project along the point normal and recalculate the normal vector on the surface projected.</param>
    void ProjectPoints(tMatrix2D *points, tMatrix2D **projected, Item objectProject, int ProjectionType = PROJECTION_ALONG_NORMAL_RECALC);

    /// <summary>
    /// Close the current station without asking to save.
    /// </summary>
    void CloseStation();

    /// <summary>
    /// Adds a new target that can be reached with a robot.
    /// </summary>
    /// <param name="name">Name of the target.</param>
    /// <param name="itemparent">Parent to attach to (such as a frame).</param>
    /// <param name="itemrobot">Main robot that will be used to go to self target.</param>
    /// <returns>the new target created</returns>
    Item AddTarget(const QString &name, Item *itemparent = NULL, Item *itemrobot = NULL);

    /// <summary>
    /// Adds a new Frame that can be referenced by a robot.
    /// </summary>
    /// <param name="name">Name of the reference frame.</param>
    /// <param name="itemparent">Parent to attach to (such as the robot base frame).</param>
    /// <returns>The new reference frame created.</returns>
    Item AddFrame(const QString &name, Item *itemparent = NULL);

    /// <summary>
    /// Adds a new Frame that can be referenced by a robot.
    /// </summary>
    /// <param name="name">Name of the program.</param>
    /// <param name="itemrobot">Robot that will be used.</param>
    /// <returns>the new program created</returns>
    Item AddProgram(const QString &name, Item *itemrobot = NULL);

    /// <summary>
    /// Add a new empty station. It returns the station item added.
    /// </summary>
    /// <param name="name">Name of the station (the title bar will be renamed to match the station name).</param>
    Item AddStation(QString name);

    /// <summary>
    /// Add a new robot machining project. Machining projects can also be used for 3D printing, following curves and following points.
    /// It returns the newly created Item containing the project settings.
    /// Tip: Use the macro /RoboDK/Library/Macros/MoveRobotThroughLine.py to see an example that creates a new "curve follow project" given a list of points to follow(Option 4).
    /// </summary>
    /// <param name="name">Name of the project settings.</param>
    /// <param name="itemrobot">Robot to use for the project settings(optional). It is not required to specify the robot if only one robot or mechanism is available in the RoboDK station.</param>
    /// <returns></returns>
    Item AddMachiningProject(QString name = "Curve follow settings",Item *itemrobot = NULL);

    /// <summary>
    /// Returns the list of open stations in RoboDK.
    /// </summary>
    /// <returns></returns>
    QList<Item> getOpenStation();

    /// <summary>
    /// Set the active station (project currently visible).
    /// </summary>
    /// <param name="station">station item, it can be previously loaded as an RDK file.</param>
    void setActiveStation(Item stn);

    /// <summary>
    /// Returns the active station item (station currently visible).
    /// </summary>
    /// <returns></returns>
    Item getActiveStation();

    /// <summary>
    /// Adds a function call in the program output. RoboDK will handle the syntax when the code is generated for a specific robot. If the program exists it will also run the program in simulate mode.
    /// </summary>
    /// <param name="function_w_params">Function name with parameters (if any).</param>
    /// <returns></returns>
    int RunProgram(const QString &function_w_params);

    /// <summary>
    /// Adds code to run in the program output. If the program exists it will also run the program in simulation mode.
    /// </summary>
    /// <param name="code"></param>
    /// <param name="code_is_fcn_call"></param>
    /// <returns></returns>
    int RunCode(const QString &code, bool code_is_fcn_call = false);

    /// <summary>
    /// Shows a message or a comment in the output robot program.
    /// </summary>
    /// <param name="message"></param>
    /// <param name="message_is_comment"></param>
    void RunMessage(const QString &message, bool message_is_comment = false);

    /// <summary>
    /// Update the scene.
    /// </summary>
    /// <param name="flags">Set to RenderComplete for a full update or RenderScreen to redraw the scene without internally updating dependencies.</param>
    void Render(bool always_render = false);

    /// <summary>
    /// Update the screen.
    /// This updates the position of all robots and internal links according to previously set values.
    /// </summary>
    void Update();

    /// <summary>
    /// Check if an object is fully inside another one.
    /// </summary>
    /// <param name="object_inside"></param>
    /// <param name="object_parent"></param>
    /// <returns>Returns true if object_inside is inside the object_parent</returns>
    bool IsInside(Item object_inside, Item object_parent);

    /// <summary>
    /// Turn collision checking ON or OFF (COLLISION_OFF/COLLISION_OFF) according to the collision map. If collision checking is activated it returns the number of pairs of objects that are currently in a collision state.
    /// </summary>
    /// <param name="check_state"></param>
    /// <returns>Number of pairs of objects in a collision state (0 if no collisions).</returns>
    int setCollisionActive(int check_state = COLLISION_ON);

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
    bool setCollisionActivePair(int check_state, Item item1, Item item2, int id1 = 0, int id2 = 0);

    /// <summary>
    /// Returns the number of pairs of objects that are currently in a collision state.
    /// </summary>
    /// <returns>0 if no collisions are found.</returns>
    int Collisions();

    /// <summary>
    /// Returns 1 if item1 and item2 collided. Otherwise returns 0.
    /// </summary>
    /// <param name="item1"></param>
    /// <param name="item2"></param>
    /// <returns>0 if no collisions are found.</returns>
    int Collision(Item item1, Item item2);

    /// <summary>
    /// Return the list of items that are in a collision state. This function can be used after calling Collisions() to retrieve the items that are in a collision state.
    /// </summary>
    /// <param name="link_id_list">List of robot link IDs that are in collision (0 for objects and tools).</param>
    /// <returns>List of items that are in a collision state.</returns>
    QList<Item> getCollisionItems(QList<int> link_id_list);

    /// <summary>
    /// Sets the current simulation speed. Set the speed to 1 for a real-time simulation. The slowest speed allowed is 0.001 times the real speed. Set to a high value (>100) for fast simulation results.
    /// </summary>
    /// <param name="speed">Simulation speed ratio (1 means real time simulation)</param>
    void setSimulationSpeed(double speed);

    /// <summary>
    /// Gets the current simulation speed. Set the speed to 1 for a real-time simulation.
    /// </summary>
    /// <returns>Simulation speed ratio (1 means real time simulation)</returns>
    double SimulationSpeed();

    /// <summary>
    /// Sets the behavior of the RoboDK API. By default, RoboDK shows the path simulation for movement instructions (run_mode=1=RUNMODE_SIMULATE).
    /// Setting the run_mode to RUNMODE_QUICKVALIDATE allows performing a quick check to see if the path is feasible.
    /// if robot.Connect() is used, RUNMODE_RUN_FROM_PC is selected automatically.
    /// </summary>
    /// <param name="run_mode">int = RUNMODE
    /// RUNMODE_SIMULATE=1        performs the simulation moving the robot (default)
    /// RUNMODE_QUICKVALIDATE=2   performs a quick check to validate the robot movements
    /// RUNMODE_MAKE_ROBOTPROG=3  makes the robot program
    /// RUNMODE_RUN_REAL=4        moves the real robot is it is connected</param>
    void setRunMode(int run_mode = 1);

    /// <summary>
    /// Returns the behavior of the RoboDK API. By default, RoboDK shows the path simulation for movement instructions (run_mode=1).
    /// </summary>
    /// <returns>int = RUNMODE
    /// RUNMODE_SIMULATE=1        performs the simulation moving the robot (default)
    /// RUNMODE_QUICKVALIDATE=2   performs a quick check to validate the robot movements
    /// RUNMODE_MAKE_ROBOTPROG=3  makes the robot program
    /// RUNMODE_RUN_REAL=4        moves the real robot is it is connected</returns>
    int RunMode();

    /// <summary>
    /// Gets all the user parameters from the open RoboDK station.
    /// The parameters can also be modified by right clicking the station and selecting "shared parameters"
    /// User parameters can be added or modified by the user
    /// </summary>
    /// <returns>List of pairs of strings as parameter-value (list of a list)</returns>
    QList<QPair<QString, QString> > getParams();

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
    /// <returns>Parameter value.</returns>
    QString getParam(const QString &param);

    /// <summary>
    /// Sets a global parameter from the RoboDK station. If the parameters exists, it will be modified. If not, it will be added to the station.
    /// The parameters can also be modified by right clicking the station and selecting "shared parameters".
    /// </summary>
    /// <param name="param">RoboDK parameter</param>
    /// <param name="value">value</param>
    /// <returns></returns>
    void setParam(const QString &param, const QString &value);

    /// <summary>
    /// Send a special command. These commands are meant to have a specific effect in RoboDK, such as changing a specific setting or provoke specific events.
    /// </summary>
    /// <param name="cmd">Command Name, such as Trace, Threads or Window.</param>
    /// <param name="value">Comand value (optional, not all commands require a value)</param>
    /// <returns>Command result.</returns>
    QString Command(const QString &cmd, const QString &value="");

    // --- add calibrate reference, calibrate tool, measure tracker, etc...

    /// <summary>
    /// Takes a laser tracker measurement with respect to its own reference frame. If an estimate point is provided, the laser tracker will first move to those coordinates. If search is True, the tracker will search for a target.
    /// </summary>
    /// <param name="xyz"></param>
    /// <param name="estimate"></param>
    /// <param name="search">True to search near the estimated value.</param>
    /// <returns>True if successful.</returns>
    bool LaserTrackerMeasure(tXYZ xyz, tXYZ estimate, bool search = false);

    /// <summary>
    /// Checks the collision between a line and any objects in the station. The line is composed by 2 points.
    /// Returns the collided item. Use Item.Valid() to check if there was a valid collision.
    /// </summary>
    /// <param name="p1">Start point of the line (absolute coordinates).</param>
    /// <param name="p2">End point of the line (absolute coordinates).</param>
    /// <param name="xyz_collision">Collided point.</param>
    /// <returns>True if collision found.</returns>
    bool CollisionLine(tXYZ p1, tXYZ p2);

    /// \brief Set a list of items visibile (faster than the default setVisible())
    void setVisible(QList<Item> itemList, QList<bool> visibleList, QList<int> visibleFrames);

    ///
    /// \brief Show a list of items as collided.
    void ShowAsCollided(QList<Item> itemList, QList<bool> collidedList, QList<int> *robot_link_id = NULL);

    /// <summary>
    /// Calibrate a tool (TCP) given a number of points or calibration joints. Important: If the robot is calibrated, provide joint values to maximize accuracy.
    /// </summary>
    /// <param name="poses_joints">matrix of poses in a given format or a list of joints</param>
    /// <param name="error_stats">stats[mean, standard deviation, max] - Output error stats summary.</param>
    /// <param name="format">Euler format. Optionally, use JOINT_FORMAT and provide the robot.</param>
    /// <param name="algorithm">type of algorithm (by point, plane, ...)</param>
    /// <param name="robot">Robot used for the identification (if using joint values).</param>
    /// <returns>TCP as [x, y, z] - calculated TCP</returns>
    void CalibrateTool(tMatrix2D *poses_joints, tXYZ tcp_xyz, int format=EULER_RX_RY_RZ, int algorithm=CALIBRATE_TCP_BY_POINT, Item *robot=NULL, double *error_stats=NULL);

    /// <summary>
    /// Calibrate a Reference Frame given a list of points or joint values. Important: If the robot is calibrated, provide joint values to maximize accuracy.
    /// </summary>
    /// <param name="joints">points as a 3xN matrix or nDOFsxN) - List of points or a list of robot joints.</param>
    /// <param name="method">type of algorithm(by point, plane, ...) CALIBRATE_FRAME_...</param>
    /// <param name="use_joints">use points or joint values. The robot item must be provided if joint values is used.</param>
    /// <param name="robot">Robot used for the identification (if using joint values).</param>
    /// <returns></returns>
    Mat CalibrateReference(tMatrix2D *poses_joints, int method = CALIBRATE_FRAME_3P_P1_ON_X, bool use_joints = false, Item *robot = NULL);

    /// <summary>
    /// Defines the name of the program when the program is generated. It is also possible to specify the name of the post processor as well as the folder to save the program.
    /// This method must be called before any program output is generated (before any robot movement or other instruction).
    /// </summary>
    /// <param name="progname">Name of the program.</param>
    /// <param name="defaultfolder">Folder to save the program, leave empty to use the default program folder.</param>
    /// <param name="postprocessor">Name of the post processor (for a post processor in C:/RoboDK/Posts/Fanuc_post.py it is possible to provide "Fanuc_post.py" or simply "Fanuc_post").</param>
    /// <param name="robot">Robot to link.</param>
    /// <returns></returns>
    int ProgramStart(const QString &progname, const QString &defaultfolder = "", const QString &postprocessor = "", Item *robot = NULL);

    /// <summary>
    /// Set the pose of the wold reference frame with respect to the user view (camera/screen).
    /// </summary>
    /// <param name="pose">View pose.</param>
    void setViewPose(const Mat &pose);

    /// <summary>
    /// Get the pose of the wold reference frame with respect to the user view (camera/screen).
    /// </summary>
    /// <returns>View pose.</returns>
    Mat ViewPose();

    /// <summary>
    /// Set the nominal robot parameters.
    /// </summary>
    /// <param name="robot"></param>
    /// <param name="dhm">D-H Modified table (Denavit Hartenberg Modified)</param>
    /// <param name="poseBase"></param>
    /// <param name="poseTool"></param>
    /// <returns></returns>
    bool SetRobotParams(Item *robot,tMatrix2D dhm, Mat poseBase, Mat poseTool);

    /// <summary>
    /// Returns the position of the cursor as XYZ coordinates (by default), or the 3D position of a given set of 2D coordinates of the window (x & y coordinates in pixels from the top left corner)
    /// The XYZ coordinates returned are given with respect to the RoboDK station(absolute reference).
    /// If no coordinates are provided, the current position of the cursor is retrieved.
    /// </summary>
    /// <param name="x">X coordinate in pixels</param>
    /// <param name="y">Y coordinate in pixels</param>
    /// <param name="xyzStation"></param>
    /// <returns>Item under the mouse cursor.</returns>
    Item getCursorXYZ(int x = -1, int y = -1, tXYZ xyzStation = NULL);

    /// <summary>
    /// Returns the license as a readable string (same name shown in the RoboDK's title bar, on top of the main menu).
    /// </summary>
    /// <returns></returns>
    QString License();

    /// <summary>
    /// Returns the list of items selected (it can be one or more items).
    /// </summary>
    /// <returns>List of selected items.</returns>
    QList<Item> Selection();

    /// <summary>
    /// Show the popup menu to create the ISO9283 path for position accuracy, repeatability and path accuracy performance testing.
    /// </summary>
    /// <param name="robot"></param>
    /// <param name="center">XYZ position of the center of the cube with respect to the robot base, in mm.</param>
    /// <param name="side">Cube side, in mm.</param>
    /// <returns>IS9283 Program or nullptr if the user cancelled.</returns>
    Item Popup_ISO9283_CubeProgram(Item *robot=NULL, tXYZ center=NULL, double side=-1, bool blocking=true);



public:


    /// Tree item types
    enum {
        /// Any item type.
        ITEM_TYPE_ANY = -1,

        /// Item of type station (RDK file).
        ITEM_TYPE_STATION = 1,

        /// Item of type robot (.robot file).
        ITEM_TYPE_ROBOT = 2,

        /// Item of type reference frame.
        ITEM_TYPE_FRAME = 3,

        /// Item of type tool (.tool).
        ITEM_TYPE_TOOL = 4,

        /// Item of type object (.stl, .step or .iges for example).
        ITEM_TYPE_OBJECT = 5,

        /// Target item.
        ITEM_TYPE_TARGET = 6,

        /// Program item.
        ITEM_TYPE_PROGRAM = 8,

        /// Instruction.
        ITEM_TYPE_INSTRUCTION = 9,

        /// Python macro.
        ITEM_TYPE_PROGRAM_PYTHON = 10,

        /// Robot machining project, curve follow, point follow or 3D printing project.
        ITEM_TYPE_MACHINING = 11,

        /// Ballbar validation project.
        ITEM_TYPE_BALLBARVALIDATION = 12,

        /// Robot calibration project.
        ITEM_TYPE_CALIBPROJECT = 13,

        /// Robot path accuracy validation project.
        ITEM_TYPE_VALID_ISO9283 = 14
    };

    /// Instruction types
    enum {
        /// Invalid instruction.
        INS_TYPE_INVALID = -1,

        /// Linear or joint movement instruction.
        INS_TYPE_MOVE = 0,

        /// Circular movement instruction.
        INS_TYPE_MOVEC = 1,

        /// Set speed instruction.
        INS_TYPE_CHANGESPEED = 2,

        /// Set reference frame instruction.
        INS_TYPE_CHANGEFRAME = 3,

        /// Set the tool (TCP) instruction.
        INS_TYPE_CHANGETOOL = 4,

        /// Set the robot instruction (obsolete).
        INS_TYPE_CHANGEROBOT = 5,

        /// Pause instruction.
        INS_TYPE_PAUSE = 6,

        /// Simulation event instruction.
        INS_TYPE_EVENT = 7,

        /// Program call or raw code output.
        INS_TYPE_CODE = 8,

        /// Display message on the teach pendant.
        INS_TYPE_PRINT = 9
    };

    /// Movement types
    enum {
        /// Invalid robot movement.
        MOVE_TYPE_INVALID = -1,

        /// Joint axes movement (MoveJ).
        MOVE_TYPE_JOINT = 1,

        /// Linear movement (MoveL).
        MOVE_TYPE_LINEAR = 2,

        /// Circular movement (MoveC).
        MOVE_TYPE_CIRCULAR = 3
    };

    /// Script execution types used by IRoboDK.setRunMode and IRoboDK.RunMode
    enum {
        /// Performs the simulation moving the robot (default)
        RUNMODE_SIMULATE = 1,

        /// Performs a quick check to validate the robot movements.
        RUNMODE_QUICKVALIDATE = 2,

        /// Makes the robot program.
        RUNMODE_MAKE_ROBOTPROG = 3,

        /// Makes the robot program and updates it to the robot.
        RUNMODE_MAKE_ROBOTPROG_AND_UPLOAD = 4,

        /// Makes the robot program and starts it on the robot (independently from the PC).
        RUNMODE_MAKE_ROBOTPROG_AND_START = 5,

        /// Moves the real robot from the PC (PC is the client, the robot behaves like a server).
        RUNMODE_RUN_ROBOT = 6
    };

    /// Program execution type
    enum {
        /// Set the robot program to run on the simulator.
        PROGRAM_RUN_ON_SIMULATOR = 1,

        /// Set the robot program to run on the robot.
        PROGRAM_RUN_ON_ROBOT = 2
    };

    /// TCP calibration types
    enum {

        /// Calibrate the TCP by poses touching the same point.
        CALIBRATE_TCP_BY_POINT = 0,

        /// Calibrate the TCP by poses touching the same plane.
        CALIBRATE_TCP_BY_PLANE = 1
    };

    /// Reference frame calibration types
    enum {
        ///Calibrate by 3 points: [X, X+, Y+] (p1 on X axis).
        CALIBRATE_FRAME_3P_P1_ON_X = 0,

        ///Calibrate by 3 points: [Origin, X+, XY+] (p1 is origin).
        CALIBRATE_FRAME_3P_P1_ORIGIN = 1,

        ///Calibrate by 6 points.
        CALIBRATE_FRAME_6P = 2,

        ///Calibrate turntable.
        CALIBRATE_TURNTABLE = 3
    };

    /// projection types (for AddCurve)
    enum {
        /// No curve projection
        PROJECTION_NONE                = 0,

        /// The projection will the closest point on the surface.
        PROJECTION_CLOSEST             = 1,

        /// The projection will be done along the normal.
        PROJECTION_ALONG_NORMAL        = 2,

        /// The projection will be done along the normal. Furthermore, the normal will be recalculated according to the surface normal.
        PROJECTION_ALONG_NORMAL_RECALC = 3,

        /// The projection will be the closest point on the surface and the normals will be recalculated.
        PROJECTION_CLOSEST_RECALC      = 4,

        /// The normals are recalculated according to the surface normal of the closest projection. The points are not changed.
        PROJECTION_RECALC              = 5
    };

    /// Euler type
    enum {

        /// joints.
        JOINT_FORMAT      = -1,

        /// Staubli, Mecademic.
        EULER_RX_RYp_RZpp = 0,

        /// ABB RobotStudio.
        EULER_RZ_RYp_RXpp = 1,

        /// Kawasaki, Adept, Staubli.
        EULER_RZ_RYp_RZpp = 2,

        /// CATIA, SolidWorks.
        EULER_RZ_RXp_RZpp = 3,

        /// Fanuc, Kuka, Motoman, Nachi.
        EULER_RX_RY_RZ    = 4,

        /// CRS.
        EULER_RZ_RY_RX    = 5,

        /// ABB Rapid.
        EULER_QUEATERNION = 6
    };

    /// State of the RoboDK window
    enum {

        /// Hide the RoboDK window. RoboDK will keep running as a process.
        WINDOWSTATE_HIDDEN = -1,

        /// Display the RoboDK window.
        WINDOWSTATE_SHOW = 0,

        /// Minimize the RoboDK window.
        WINDOWSTATE_MINIMIZED = 1,

        /// Display the RoboDK window in a normal state (not maximized)
        WINDOWSTATE_NORMAL = 2,

        /// Maximize the RoboDK Window.
        WINDOWSTATE_MAXIMIZED = 3,

        /// Make the RoboDK window fullscreen.
        WINDOWSTATE_FULLSCREEN = 4,

        /// Display RoboDK in cinema mode (hide the toolbar and the menu).
        WINDOWSTATE_CINEMA = 5,

        /// Display RoboDK in cinema mode and fullscreen.
        WINDOWSTATE_FULLSCREEN_CINEMA = 6
    };

    /// Instruction program call type:
    enum {
        /// Instruction to call a program.
        INSTRUCTION_CALL_PROGRAM = 0,

        /// Instructio to insert raw code (this will not provoke a program call).
        INSTRUCTION_INSERT_CODE = 1,

        /// Instruction to start a parallel thread. Program execution will continue and also trigger a thread.
        INSTRUCTION_START_THREAD = 2,

        /// Comment output.
        INSTRUCTION_COMMENT = 3,

        /// Instruction to pop up a message on the robot teach pendant.
        INSTRUCTION_SHOW_MESSAGE = 4
    };

    /// Object selection features:
    enum {
        /// No selection
        FEATURE_NONE = 0,

        /// Surface selection
        FEATURE_SURFACE = 1,

        /// Curve selection
        FEATURE_CURVE = 2,

        /// Point selection
        FEATURE_POINT = 3
    };

    /// Spray gun simulation:
    enum {
        /// Activate the spray simulation
        SPRAY_OFF = 0,
        SPRAY_ON = 1
    };

    /// Collision checking state
    enum {
        /// Do not use collision checking
        COLLISION_OFF = 0,

        /// Use collision checking
        COLLISION_ON = 1
    };

    /// RoboDK Window Flags
    enum {
        /// Allow using the RoboDK station tree.
        FLAG_ROBODK_TREE_ACTIVE = 1,

        /// Allow using the 3D navigation.
        FLAG_ROBODK_3DVIEW_ACTIVE = 2,

        /// Allow left clicks on the 3D navigation screen.
        FLAG_ROBODK_LEFT_CLICK = 4,

        /// Allow right clicks on the 3D navigation screen.
        FLAG_ROBODK_RIGHT_CLICK = 8,

        /// Allow double clicks on the 3D navigation screen.
        FLAG_ROBODK_DOUBLE_CLICK = 16,

        /// Enable/display the menu bar.
        FLAG_ROBODK_MENU_ACTIVE = 32,

        /// Enable the file menu (FLAG_ROBODK_MENU_ACTIVE must be allowed).
        FLAG_ROBODK_MENUFILE_ACTIVE = 64,

        /// Enable the edit menu (FLAG_ROBODK_MENU_ACTIVE must be allowed).
        FLAG_ROBODK_MENUEDIT_ACTIVE = 128,

        /// Enable the program menu (FLAG_ROBODK_MENU_ACTIVE must be allowed).
        FLAG_ROBODK_MENUPROGRAM_ACTIVE = 256,

        /// Enable the tools menu (FLAG_ROBODK_MENU_ACTIVE must be allowed).
        FLAG_ROBODK_MENUTOOLS_ACTIVE = 512,

        /// Enable the utilities menu (FLAG_ROBODK_MENU_ACTIVE must be allowed).
        FLAG_ROBODK_MENUUTILITIES_ACTIVE = 1024,

        /// Enable the connect menu (FLAG_ROBODK_MENU_ACTIVE must be allowed).
        FLAG_ROBODK_MENUCONNECT_ACTIVE = 2048,

        /// Allow using keyboard shortcuts.
        FLAG_ROBODK_WINDOWKEYS_ACTIVE = 4096,

        /// Disallow everything.
        FLAG_ROBODK_NONE = 0,

        /// Allow everything (default).
        FLAG_ROBODK_ALL = 0xFFFF,

        /// Allow using the full menu.
        FLAG_ROBODK_MENU_ACTIVE_ALL = FLAG_ROBODK_MENU_ACTIVE | FLAG_ROBODK_MENUFILE_ACTIVE | FLAG_ROBODK_MENUEDIT_ACTIVE | FLAG_ROBODK_MENUPROGRAM_ACTIVE | FLAG_ROBODK_MENUTOOLS_ACTIVE | FLAG_ROBODK_MENUUTILITIES_ACTIVE | FLAG_ROBODK_MENUCONNECT_ACTIVE
    };

    /// RoboDK Item Flags
    enum {
        /// Allow selecting RoboDK items.
        FLAG_ITEM_SELECTABLE = 1,

        /// Allow modifying RoboDK items.
        FLAG_ITEM_EDITABLE = 2,

        /// Allow draggin an item.
        FLAG_ITEM_DRAGALLOWED = 4,

        /// Allow dropping to an item.
        FLAG_ITEM_DROPALLOWED = 8,

        /// Enable the item.
        FLAG_ITEM_ENABLED = 32,

        /// Allow having nested items, expand and collapse the item.
        FLAG_ITEM_AUTOTRISTATE = 64,

        /// Do not allow adding nested items.
        FLAG_ITEM_NOCHILDREN = 128,
        FLAG_ITEM_USERTRISTATE = 256,

        /// Disallow everything.
        FLAG_ITEM_NONE = 0,

        /// Allow everything (default).
        FLAG_ITEM_ALL = 64 + 32 + 8 + 4 + 2 + 1
    };



private:
    QTcpSocket *_COM;
    QString _IP;
    int _PORT;
    int _TIMEOUT;
    qint64 _PROCESS;

    QString _ROBODK_BIN; // file path to the robodk program (executable), typically C:/RoboDK/bin/RoboDK.exe. Leave empty to use the registry key: HKEY_LOCAL_MACHINE\SOFTWARE\RoboDK
    QString _ARGUMENTS;       // arguments to provide to RoboDK on startup

    bool _connected();
    bool _connect();
    bool _connect_smart(); // will attempt to start RoboDK
    void _disconnect();

    bool _check_connection();
    bool _check_status();

    bool _waitline();
    QString _recv_Line();//QString &string);
    bool _send_Line(const QString &string);
    int _recv_Int();//qint32 &value);
    bool _send_Int(const qint32 value);
    Item _recv_Item();//Item *item);
    bool _send_Item(const Item *item);
    bool _send_Item(const Item &item);
    Mat _recv_Pose();//Mat &pose);
    bool _send_Pose(const Mat &pose);
    bool _recv_XYZ(tXYZ pos);
    bool _send_XYZ(const tXYZ pos);
    bool _recv_Array(double *values, int *psize=NULL);
    bool _send_Array(const double *values, int nvalues);
    bool _recv_Array(tJoints *jnts);
    bool _send_Array(const tJoints *jnts);
    bool _send_Array(const Mat *mat);
    bool _recv_Matrix2D(tMatrix2D **mat);
    bool _send_Matrix2D(tMatrix2D *mat);


    void _moveX(const Item *target, const tJoints *joints, const Mat *mat_target, const Item *itemrobot, int movetype, bool blocking);
    void _moveC(const Item *target1, const tJoints *joints1, const Mat *mat_target1, const Item *target2, const tJoints *joints2, const Mat *mat_target2, const Item *itemrobot, bool blocking);
};


/// \brief The Item class represents an item in RoboDK station. An item can be a robot, a frame, a tool, an object, a target, ... any item visible in the <strong>station tree</strong>.
/// An item can also be seen as a node where other items can be attached to (child items).
/// Every item has one parent item/node and can have one or more child items/nodes
///
/// \image html station-tree.png
class ROBODK Item {
    friend class RoboDK_API::RoboDK;
    
public:
    Item(RoboDK *rdk=nullptr, quint64 ptr=0, qint32 type=-1);
    Item(const Item &other);

    ~Item();

    QString ToString() const;

    RoboDK* RDK();

    void NewLink();

    /// Item type (object, robot, tool, reference, robot machining project, ...)
    int Type();

    /// <summary>
    /// Save a station, a robot, a tool or an object to a file
    /// </summary>
    /// <param name="filename">path and file name</param>
    void Save(const QString &filename);

    /// <summary>
    /// Deletes an item and its childs from the station.
    /// </summary>
    void Delete();

    /// \brief Check if an item is valid (not null and available in the open station)
    /// \param item_check Item to check
    /// \return True if the item exists, false otherwise
    bool Valid() const ;

    /// <summary>
    /// Attaches the item to a new parent while maintaining the relative position with its parent. The absolute position is changed.
    /// </summary>
    /// <param name="parent"></param>
    void setParent(Item parent);

    /// <summary>
    /// Attaches the item to another parent while maintaining the current absolute position in the station.
    /// The relationship between this item and its parent is changed to maintain the abosolute position.
    /// </summary>
    /// <param name="parent">parent item to attach this item to</param>
    void setParentStatic(Item parent);

    /// <summary>
    /// Return the parent item of this item
    /// </summary>
    /// <returns>Parent item</returns>
    Item Parent() const;

    /// <summary>
    /// Returns a list of the item childs that are attached to the provided item.
    /// </summary>
    /// <returns>item x n: list of child items</returns>
    QList<Item> Childs() const;

    /// <summary>
    /// Returns 1 if the item is visible, otherwise, returns 0.
    /// </summary>
    /// <returns>true if visible, false if not visible</returns>
    bool Visible() const;

    /// <summary>
    /// Sets the item visiblity status
    /// </summary>
    /// <param name="visible"></param>
    /// <param name="visible_reference">set the visible reference frame (1) or not visible (0)</param>
    void setVisible(bool visible, int visible_frame = -1);

    /// <summary>
    /// Returns the name of an item. The name of the item is always displayed in the RoboDK station tree
    /// </summary>
    /// <returns>name of the item</returns>
    QString Name() const;

    /// <summary>
    /// Set the name of a RoboDK item.
    /// </summary>
    /// <param name="name"></param>
    void setName(const QString &name);

    /// <summary>
    /// Sets the local position (pose) of an object, target or reference frame. For example, the position of an object/frame/target with respect to its parent.
    /// If a robot is provided, it will set the pose of the end efector.
    /// </summary>
    /// <param name="pose">4x4 homogeneous matrix</param>
    void setPose(Mat pose);

    /// <summary>
    /// Returns the local position (pose) of an object, target or reference frame. For example, the position of an object/frame/target with respect to its parent.
    /// If a robot is provided, it will get the pose of the end efector
    /// </summary>
    /// <returns>4x4 homogeneous matrix (pose)</returns>
    Mat Pose() const;

    /// <summary>
    /// Sets the position (pose) the object geometry with respect to its own reference frame. This procedure works for tools and objects.
    /// </summary>
    /// <param name="pose">4x4 homogeneous matrix</param>
    /// <param name="apply_movement">Apply the movement to the inner geometry and not as a pose shift</param>
    void setGeometryPose(Mat pose);

    /// <summary>
    /// Returns the position (pose) the object geometry with respect to its own reference frame. This procedure works for tools and objects.
    /// </summary>
    /// <returns>4x4 homogeneous matrix (pose)</returns>
    Mat GeometryPose();

    /// <summary>
    /// Obsolete: Use setPoseTool(pose) instead. Sets the tool pose of a tool item. If a robot is provided it will set the tool pose of the active tool held by the robot.
    /// </summary>
    /// <param name="pose">4x4 homogeneous matrix (pose)</param>
    void setHtool(Mat pose);

    /// <summary>
    /// Obsolete: Use PoseTool() instead.
    /// Returns the tool pose of an item. If a robot is provided it will get the tool pose of the active tool held by the robot.
    /// </summary>
    /// <returns>4x4 homogeneous matrix (pose)</returns>
    Mat Htool();

    /// <summary>
    /// Returns the tool pose of an item. If a robot is provided it will get the tool pose of the active tool held by the robot.
    /// </summary>
    /// <returns>4x4 homogeneous matrix (pose)</returns>
    Mat PoseTool();

    /// <summary>
    /// Returns the reference frame pose of an item. If a robot is provided it will get the tool pose of the active reference frame used by the robot.
    /// </summary>
    /// <returns>4x4 homogeneous matrix (pose)</returns>
    Mat PoseFrame();

    /// <summary>
    /// Sets the reference frame of a robot(user frame). The frame can be either an item or a pose.
    /// If "frame" is an item, it links the robot to the frame item. If frame is a pose, it updates the linked pose of the robot frame (with respect to the robot reference frame).
    /// </summary>
    /// <param name="frame_pose">4x4 homogeneous matrix (pose)</param>
    void setPoseFrame(Mat frame_pose);

    /// <summary>
    /// Sets the tool of a robot or a tool object (Tool Center Point, or TCP). The tool pose can be either an item or a 4x4 Matrix.
    /// If the item is a tool, it links the robot to the tool item.If tool is a pose, it updates the current robot TCP.
    /// </summary>
    /// <param name="pose">4x4 homogeneous matrix (pose)</param>
    void setPoseFrame(Item frame_item);

    /// <summary>
    /// Sets the tool of a robot or a tool object (Tool Center Point, or TCP). The tool pose can be either an item or a 4x4 Matrix.
    /// If the item is a tool, it links the robot to the tool item.If tool is a pose, it updates the current robot TCP.
    /// </summary>
    /// <param name="tool_pose">4x4 homogeneous matrix (pose)</param>
    void setPoseTool(Mat tool_pose);

    /// <summary>
    /// Sets the tool of a robot or a tool object (Tool Center Point, or TCP). The tool pose can be either an item or a 4x4 Matrix.
    /// If the item is a tool, it links the robot to the tool item.If tool is a pose, it updates the current robot TCP.
    /// </summary>
    /// <param name="tool_item">Tool item</param>
    void setPoseTool(Item tool_item);

    /// <summary>
    /// Sets the global position (pose) of an item. For example, the position of an object/frame/target with respect to the station origin.
    /// </summary>
    /// <param name="pose">4x4 homogeneous matrix (pose)</param>
    void setPoseAbs(Mat pose);

    /// <summary>
    /// Returns the global position (pose) of an item. For example, the position of an object/frame/target with respect to the station origin.
    /// </summary>
    /// <returns>4x4 homogeneous matrix (pose)</returns>
    Mat PoseAbs();

    /// <summary>
    /// Changes the color of a robot/object/tool. A color must must in the format COLOR=[R,G,B,(A=1)] where all values range from 0 to 1.
    /// Alpha (A) defaults to 1 (100% opaque). Set A to 0 to make an object transparent.
    /// </summary>
    /// <param name="tocolor">color to change to</param>
    /// <param name="fromcolor">filter by this color</param>
    /// <param name="tolerance">optional tolerance to use if a color filter is used (defaults to 0.1)</param>
    void setColor(double colorRGBA[4]);



//---------- add more

    /// <summary>
    /// Apply a scale to an object to make it bigger or smaller.
    /// The scale can be uniform (if scale is a float value) or per axis (if scale is a vector).
    /// </summary>
    void Scale(double scale);

    /// <summary>
    /// Apply a per-axis scale to an object to make it bigger or smaller.
    /// The scale can be uniform (if scale is a float value) or per axis (if scale is a vector).
    /// </summary>
    /// <param name="scale">scale to apply as [scale_x, scale_y, scale_z]</param>
    void Scale(double scale_xyz[3]);

    /// <summary>
    /// Update the robot milling path input and parameters. Parameter input can be an NC file (G-code or APT file) or an object item in RoboDK. A curve or a point follow project will be automatically set up for a robot manufacturing project.
    /// <br>Tip: Use getLink() and setLink() to get/set the robot tool, reference frame, robot and program linked to the project.
    /// <br>Tip: Use setPose() and setJoints() to update the path to tool orientation or the preferred start joints.
    /// <br>Tip: Use setPoseTool() and setPoseFrame() to link to the corresponding tool and reference frames.
    /// @code
    /// Item object_curves = RDK->ItemUserPick("Select an object with curves or points to follow", RoboDK::ITEM_TYPE_OBJECT);
    /// if (!object_curves.Valid()){
    ///     // operation cancelled
    ///     return;
    /// }
    ///
    /// // Assuming ROBOT is a robot item
    /// Item project = RDK->AddMachiningProject("Curve1 Settings", ROBOT);
    ///
    /// // set the reference link:
    /// project.setPoseFrame(ROBOT->getLink(RoboDK::ITEM_TYPE_FRAME));
    ///
    /// // set the tool link:
    /// project.setPoseTool(ROBOT->getLink(RoboDK::ITEM_TYPE_TOOL));
    ///
    /// // set preferred start joints position (value automatically set by default)
    /// project.setJoints(ROBOT->JointsHome());
    ///
    /// // link the project to the part and provide additional settings
    /// QString additional_options = "RotZ_Range=45 RotZ_Step=5 NormalApproach=50 No_Update";
    ///
    /// project.setMachiningParameters("", object_curves, additional_options);
    /// // in this example:
    /// //RotZ_Range=45 RotZ_Step=5
    /// //allow a tool z rotation of +/- 45 deg by steps of 5 deg
    ///
    /// // NormalApproach=50
    /// //Use 50 mm as normal approach by default
    ///
    /// // No_Update
    /// // Do not attempt to solve the path. It can be later updated by running project.Update()
    /// @endcode
    /// </summary>
    /// <param name="ncfile">path to the NC (G-code/APT/Point cloud) file to load (optional)</param>
    /// <param name="part_obj">object holding curves or points to automatically set up a curve/point follow project (optional)</param>
    /// <param name="options">Additional options (optional)</param>
    /// <returns>Program (can be null it has not been updated). Use Update() to retrieve the result</returns>
    Item setMachiningParameters(QString ncfile = "", Item part_obj = nullptr, QString options = "");

    /// <summary>
    /// Sets a target as a cartesian target. A cartesian target moves to cartesian coordinates.
    /// </summary>
    void setAsCartesianTarget();

    /// <summary>
    /// Sets a target as a joint target. A joint target moves to a joints position without regarding the cartesian coordinates.
    /// </summary>
    void setAsJointTarget();

    /// <summary>
    /// Returns True if a target is a joint target (green icon). Otherwise, the target is a Cartesian target (red icon).
    /// </summary>
    bool isJointTarget() const ;

    /// <summary>
    /// Returns the current joints of a robot or the joints of a target. If the item is a cartesian target, it returns the preferred joints (configuration) to go to that cartesian position.
    /// </summary>
    /// <returns>double x n: joints matrix</returns>
    tJoints Joints() const ;

    /// <summary>
    /// Returns the home joints of a robot. These joints can be manually set in the robot "Parameters" menu, then select "Set home position"
    /// </summary>
    /// <returns>joint values for the home position</returns>
    tJoints JointsHome() const;

    /// <summary>
    /// Set robot joints for the home position
    /// </summary>
    void setJointsHome(const tJoints &jnts);

    /// <summary>
    /// Returns an item pointer to the geometry of a robot link. This is useful to show/hide certain robot links or alter their geometry.
    /// </summary>
    /// <param name="link_id">link index(0 for the robot base, 1 for the first link, ...)</param>
    /// <returns>Internal geometry item</returns>
    Item ObjectLink(int link_id = 0);

    /// <summary>
    /// Returns an item linked to a robot, object, tool, program or robot machining project. This is useful to retrieve the relationship between programs, robots, tools and other specific projects.
    /// </summary>
    /// <param name="type_linked">type of linked object to retrieve</param>
    /// <returns>Linked object</returns>
    Item getLink(int type_linked = RoboDK::ITEM_TYPE_ROBOT);

    /// <summary>
    /// Set robot joints or the joints of a target
    /// </summary>
    void setJoints(const tJoints &jnts);

    /// <summary>
    /// Retrieve the joint limits of a robot
    /// </summary>
    void JointLimits(tJoints *lower_limits, tJoints *upper_limits);

    /// <summary>
    /// Sets the robot of a program or a target. You must set the robot linked to a program or a target every time you copy paste these objects.
    /// If the robot is not provided, the first available robot will be chosen automatically.
    /// </summary>
    /// <param name="robot">Robot item</param>
    void setRobot(const Item &robot);

    /// <summary>
    /// Adds an empty tool to the robot provided the tool pose (4x4 Matrix) and the tool name.
    /// </summary>
    /// <param name="tool_pose">TCP as a 4x4 Matrix (pose of the tool frame)</param>
    /// <param name="tool_name">New tool name</param>
    /// <returns>new item created</returns>
    Item AddTool(const Mat &tool_pose, const QString &tool_name = "New TCP");

    /// <summary>
    /// Computes the forward kinematics of the robot for the provided joints. The tool and the reference frame are not taken into account.
    /// </summary>
    /// <param name="joints"></param>
    /// <returns>4x4 homogeneous matrix: pose of the robot flange with respect to the robot base</returns>
    Mat SolveFK(const tJoints &joints, const Mat *tool = nullptr, const Mat *ref = nullptr);

    /// <summary>
    /// Returns the robot configuration state for a set of robot joints.
    /// </summary>
    /// <param name="joints">array of joints</param>
    /// <param name="config">configuration status as [REAR, LOWERARM, FLIP]</returns>
    void JointsConfig(const tJoints &joints, tConfig config);

    /// <summary>
    /// Computes the inverse kinematics for the specified robot and pose. The joints returned are the closest to the current robot configuration (see SolveIK_All())
    /// </summary>
    /// <param name="pose">4x4 matrix -> pose of the robot flange with respect to the robot base frame</param>
    /// <param name="joints_close">Aproximate joints solution to choose among the possible solutions. Leave this value empty to return the closest match to the current robot position.</param>
    /// <param name="tool_pose">Optionally provide a tool pose, otherwise, the robot flange is used. Tip: use robot.PoseTool() to retrieve the active robot tool.</param>
    /// <param name="reference_pose">Optionally provide a reference pose, otherwise, the robot base is used. Tip: use robot.PoseFrame() to retrieve the active robot reference frame.</param>
    /// <returns>array of joints</returns>
    tJoints SolveIK(const Mat &pose, const Mat *tool=nullptr, const Mat *ref=nullptr);

    /// <summary>
    /// Computes the inverse kinematics for the specified robot and pose. The joints returned are the closest to the current robot configuration (see SolveIK_All())
    /// </summary>
    /// <param name="pose">4x4 matrix -> pose of the robot flange with respect to the robot base frame</param>
    /// <param name="joints_approx">Aproximate solution. Leave empty to return the closest match to the current robot position.</param>
    /// <param name="tool">4x4 matrix -> Optionally provide a tool, otherwise, the robot flange is used. Tip: use robot.PoseTool() to retrieve the active robot tool.</param>
    /// <param name="reference">4x4 matrix -> Optionally provide a reference, otherwise, the robot base is used. Tip: use robot.PoseFrame() to retrieve the active robot reference frame.</param>
    /// <returns>array of joints</returns>
    tJoints SolveIK(const Mat pose, tJoints joints_approx, const Mat *tool = nullptr, const Mat *ref = nullptr);

    /// <summary>
    /// Computes the inverse kinematics for the specified robot and pose. The function returns all available joint solutions as a 2D matrix.
    /// </summary>
    /// <param name="pose">4x4 matrix -> pose of the robot tool with respect to the robot frame</param>
    /// <param name="tool_pose">Optionally provide a tool pose, otherwise, the robot flange is used. Tip: use robot.PoseTool() to retrieve the active robot tool.</param>
    /// <param name="reference_pose">Optionally provide a reference pose, otherwise, the robot base is used. Tip: use robot.PoseFrame() to retrieve the active robot reference frame.</param>
    /// <returns>double x n x m -> joint list (2D matrix)</returns>
    tMatrix2D *SolveIK_All_Mat2D(const Mat &pose, const Mat *tool=nullptr, const Mat *ref=nullptr);

    /// <summary>
    /// Computes the inverse kinematics for the specified robot and pose. The function returns all available joint solutions as a 2D matrix.
    /// </summary>
    /// <param name="pose">4x4 matrix -> pose of the robot tool with respect to the robot frame</param>
    /// <param name="tool_pose">Optionally provide a tool pose, otherwise, the robot flange is used. Tip: use robot.PoseTool() to retrieve the active robot tool.</param>
    /// <param name="reference_pose">Optionally provide a reference pose, otherwise, the robot base is used. Tip: use robot.PoseFrame() to retrieve the active robot reference frame.</param>
    /// <returns>double x n x m -> joint list (2D matrix)</returns>
    QList<tJoints> SolveIK_All(const Mat &pose, const Mat *tool=nullptr, const Mat *ref=nullptr);

    /// <summary>
    /// Connect to a real robot using the corresponding robot driver.
    /// </summary>
    /// <param name="robot_ip">IP of the robot to connect. Leave empty to use the one defined in RoboDK</param>
    /// <returns>true if connected successfully, false if connection failed</returns>
    bool Connect(const QString &robot_ip = "");

    /// <summary>
    /// Disconnect from a real robot (when the robot driver is used)
    /// </summary>
    /// <returns>true if disconnected successfully, false if it failed. It can fail if it was previously disconnected manually for example.</returns>
    bool Disconnect();

    /// <summary>
    /// Moves a robot to a specific target ("Move Joint" mode). By default, this function blocks until the robot finishes its movements.
    /// Given a target item, MoveJ can also be applied to programs and a new movement instruction will be added.
    /// </summary>
    /// <param name="target">Target to move to as a target item (RoboDK target item)</param>
    void MoveJ(const Item &itemtarget, bool blocking = true);

    /// <summary>
    /// Moves a robot to a specific target ("Move Joint" mode). By default, this function blocks until the robot finishes its movements.
    /// </summary>
    /// <param name="target">Robot joints to move to</param>
    void MoveJ(const tJoints &joints, bool blocking = true);

    /// <summary>
    /// Moves a robot to a specific target ("Move Joint" mode). By default, this function blocks until the robot finishes its movements.
    /// </summary>
    /// <param name="target">Pose target to move to. It must be a 4x4 Homogeneous matrix</param>
    void MoveJ(const Mat &target, bool blocking = true);

    /// <summary>
    /// Moves a robot to a specific target ("Move Linear" mode). By default, this function blocks until the robot finishes its movements.
    /// Given a target item, MoveL can also be applied to programs and a new movement instruction will be added.
    /// </summary>
    /// <param name="itemtarget">Target to move to as a target item (RoboDK target item)</param>
    void MoveL(const Item &itemtarget, bool blocking = true);

    /// <summary>
    /// Moves a robot to a specific target ("Move Linear" mode). By default, this function blocks until the robot finishes its movements.
    /// </summary>
    /// <param name="joints">Robot joints to move to</param>
    void MoveL(const tJoints &joints, bool blocking = true);

    /// <summary>
    /// Moves a robot to a specific target ("Move Linear" mode). By default, this function blocks until the robot finishes its movements.
    /// </summary>
    /// <param name="target">Pose target to move to. It must be a 4x4 Homogeneous matrix</param>
    void MoveL(const Mat &target, bool blocking = true);

    /// <summary>
    /// Moves a robot to a specific target ("Move Circular" mode). By default, this function blocks until the robot finishes its movements.
    /// </summary>
    /// <param name="itemtarget1">Intermediate target to move to as a target item (RoboDK target item)</param>
    /// <param name="itemtarget2">Final target to move to as a target item (RoboDK target item)</param>
    void MoveC(const Item &itemtarget1, const Item &itemtarget2, bool blocking = true);

    /// <summary>
    /// Moves a robot to a specific target ("Move Circular" mode). By default, this function blocks until the robot finishes its movements.
    /// </summary>
    /// <param name="joints1">Intermediate joint target to move to.</param>
    /// <param name="joints2">Final joint target to move to.</param>
    void MoveC(const tJoints &joints1, const tJoints &joints2, bool blocking = true);

    /// <summary>
    /// Moves a robot to a specific target ("Move Circular" mode). By default, this function blocks until the robot finishes its movements.
    /// </summary>
    /// <param name="target1">Intermediate pose target to move to. It must be a 4x4 Homogeneous matrix</param>
    /// <param name="target2">Final pose target to move to. It must be a 4x4 Homogeneous matrix</param>
    void MoveC(const Mat &target1, const Mat &target2, bool blocking = true);

    /// <summary>
    /// Checks if a joint movement is possible and, optionally, free of collisions.
    /// </summary>
    /// <param name="j1">Start joints</param>
    /// <param name="j2">Destination joints</param>
    /// <param name="minstep_deg">Maximum joint step in degrees. If this value is not provided it will use the path step defined in Tools-Options-Motion (degrees).</param>
    /// <returns>collision : returns 0 if the movement is free of collision. Otherwise it returns the number of pairs of objects that collided if there was a collision.</returns>
    int MoveJ_Test(const tJoints &j1, const tJoints &j2, double minstep_deg = -1);

    /// <summary>
    /// Checks if a linear movement is free of issues and, optionally, collisions.
    /// </summary>
    /// <param name="joints1">Start joints</param>
    /// <param name="pose2">Destination pose (active tool with respect to the active reference frame)</param>
    /// <param name="minstep_mm">Maximum joint step in mm. If this value is not provided it will use the path step defined in Tools-Options-Motion (mm).</param>
    /// <returns>collision : returns 0 if the movement is free of collision. Otherwise it returns the number of pairs of objects that collided if there was a collision.</returns>
    int MoveL_Test(const tJoints &joints1, const Mat &pose2, double minstep_mm = -1);

    /// <summary>
    /// Sets the speed and/or the acceleration of a robot.
    /// </summary>
    /// <param name="speed_linear">linear speed in mm/s (-1 = no change)</param>
    /// <param name="accel_linear">linear acceleration in mm/s2 (-1 = no change)</param>
    /// <param name="speed_joints">joint speed in deg/s (-1 = no change)</param>
    /// <param name="accel_joints">joint acceleration in deg/s2 (-1 = no change)</param>
    void setSpeed(double speed_linear, double accel_linear = -1, double speed_joints = -1, double accel_joints = -1);

    /// <summary>
    /// Sets the robot movement smoothing accuracy (also known as zone data value).
    /// </summary>
    /// <param name="rounding_mm">Rounding value (double) (robot dependent, set to -1 for accurate/fine movements)</param>
    void setRounding(double zonedata);

    /// <summary>
    /// Displays a sequence of joints
    /// </summary>
    /// <param name="sequence">joint sequence as a 6xN matrix or instruction sequence as a 7xN matrix</param>
    void ShowSequence(tMatrix2D *sequence);

    /// <summary>
    /// Checks if a robot or program is currently running (busy or moving)
    /// </summary>
    /// <returns>busy status (true=moving, false=stopped)</returns>
    bool Busy();

    /// <summary>
    /// Stops a program or a robot
    /// </summary>
    void Stop();

    /// <summary>
    /// Waits (blocks) until the robot finishes its movement.
    /// </summary>
    /// <param name="timeout_sec">timeout -> Max time to wait for robot to finish its movement (in seconds)</param>
    void WaitMove(double timeout_sec = 300) const;

    /// <summary>
    /// Sets the accuracy of the robot active or inactive. A robot must have been calibrated to properly use this option.
    /// </summary>
    /// <param name="accurate">set to 1 to use the accurate model or 0 to use the nominal model</param>
    void setAccuracyActive(int accurate = 1);

    /// <summary>
    /// Saves a program to a file.
    /// </summary>
    /// <param name="filename">File path of the program</param>
    /// <param name="run_mode">RUNMODE_MAKE_ROBOTPROG to generate the program file.Alternatively, Use RUNMODE_MAKE_ROBOTPROG_AND_UPLOAD or RUNMODE_MAKE_ROBOTPROG_AND_START to transfer the program through FTP and execute the program.</param>
    /// <returns>Transfer succeeded is True if there was a successful program transfer (if RUNMODE_MAKE_ROBOTPROG_AND_UPLOAD or RUNMODE_MAKE_ROBOTPROG_AND_START are used)</returns>
    bool MakeProgram(const QString &filename);

    /// <summary>
    /// Sets if the program will be run in simulation mode or on the real robot.
    /// Use: "PROGRAM_RUN_ON_SIMULATOR" to set the program to run on the simulator only or "PROGRAM_RUN_ON_ROBOT" to force the program to run on the robot.
    /// </summary>
    /// <returns>number of instructions that can be executed</returns>
    void setRunType(int program_run_type);

    /// <summary>
    /// Runs a program. It returns the number of instructions that can be executed successfully (a quick program check is performed before the program starts)
    /// This is a non-blocking call. Use IsBusy() to check if the program execution finished.
    /// Notes:
    /// if setRunMode(RUNMODE_SIMULATE) is used  -> the program will be simulated (default run mode)
    /// if setRunMode(RUNMODE_RUN_ROBOT) is used -> the program will run on the robot (default when RUNMODE_RUN_ROBOT is used)
    /// if setRunMode(RUNMODE_RUN_ROBOT) is used together with program.setRunType(PROGRAM_RUN_ON_ROBOT) -> the program will run sequentially on the robot the same way as if we right clicked the program and selected "Run on robot" in the RoboDK GUI
    /// </summary>
    /// <returns>True if successful</returns>
    int RunProgram();

    /// <summary>
    /// Runs a program. It returns the number of instructions that can be executed successfully (a quick program check is performed before the program starts)
    /// Program parameters can be provided for Python calls.
    /// This is a non-blocking call.Use IsBusy() to check if the program execution finished.
    /// Notes: if setRunMode(RUNMODE_SIMULATE) is used  -> the program will be simulated (default run mode)
    /// if setRunMode(RUNMODE_RUN_ROBOT) is used ->the program will run on the robot(default when RUNMODE_RUN_ROBOT is used)
    /// if setRunMode(RUNMODE_RUN_ROBOT) is used together with program.setRunType(PROGRAM_RUN_ON_ROBOT) -> the program will run sequentially on the robot the same way as if we right clicked the program and selected "Run on robot" in the RoboDK GUI
    /// </summary>
    /// <param name="parameters">Number of instructions that can be executed</param>
    int RunCode(const QString &parameters);

    /// <summary>
    /// Adds a program call, code, message or comment inside a program.
    /// </summary>
    /// <param name="code"><string of the code or program to run/param>
    /// <param name="run_type">INSTRUCTION_* variable to specify if the code is a progra</param>
    int RunInstruction(const QString &code, int run_type = RoboDK::INSTRUCTION_CALL_PROGRAM);

    /// <summary>
    /// Generates a pause instruction for a robot or a program when generating code. Set it to -1 (default) if you want the robot to stop and let the user resume the program anytime.
    /// </summary>
    /// <param name="time_ms">Time in milliseconds</param>
    void Pause(double time_ms = -1);

    /// <summary>
    /// Sets a variable (output) to a given value. This can also be used to set any variables to a desired value.
    /// </summary>
    /// <param name="io_var">io_var -> digital output (string or number)</param>
    /// <param name="io_value">io_value -> value (string or number)</param>
    void setDO(const QString &io_var, const QString &io_value);

    /// <summary>
    /// Set an analog Output
    /// </summary>
    /// <param name="io_var">Analog Output</param>
    /// <param name="io_value">Value as a string</param>
    void setAO(const QString &io_var, const QString &io_value);

    /// <summary>
    /// Get a Digital Input (DI). This function is only useful when connected to a real robot using the robot driver. It returns a string related to the state of the Digital Input (1=True, 0=False). This function returns an empty string if the script is not executed on the robot.
    /// </summary>
    /// <param name="io_var">io_var -> digital input (string or number as a string)</param>
    QString Item::getDI(const QString &io_var);


    /// <summary>
    /// Get an Analog Input (AI). This function is only useful when connected to a real robot using the robot driver. It returns a string related to the state of the Digital Input (0-1 or other range depending on the robot driver). This function returns an empty string if the script is not executed on the robot.
    /// </summary>
    /// <param name="io_var">io_var -> analog input (string or number as a string)</param>
    QString Item::getAI(const QString &io_var);

    /// <summary>
    /// Waits for an input io_id to attain a given value io_value. Optionally, a timeout can be provided.
    /// </summary>
    /// <param name="io_var">io_var -> digital output (string or number)</param>
    /// <param name="io_value">io_value -> value (string or number)</param>
    /// <param name="timeout_ms">int (optional) -> timeout in miliseconds</param>
    void waitDI(const QString &io_var, const QString &io_value, double timeout_ms = -1);

    /// <summary>
    /// Add a custom instruction. This instruction will execute a Python file or an executable file.
    /// </summary>
    /// <param name="name"></param>
    /// <param name="path_run">path to run(relative to RoboDK/bin folder or absolute path)</param>
    /// <param name="path_icon">icon path(relative to RoboDK/bin folder or absolute path)</param>
    /// <param name="blocking">True if blocking, 0 if it is a non blocking executable trigger</param>
    /// <param name="cmd_run_on_robot">Command to run through the driver when connected to the robot</param>
    /// :param name: digital input (string or number)
    void customInstruction(const QString &name, const QString &path_run, const QString &path_icon = "", bool blocking = true, const QString &cmd_run_on_robot = "");


    //void addMoveJ(const Item &itemtarget);
    //void addMoveL(const Item &itemtarget);

    /// <summary>
    /// Show or hide instruction items of a program in the RoboDK tree
    /// </summary>
    /// <param name="show"></param>
    void ShowInstructions(bool visible=true);

    /// <summary>
    /// Show or hide targets of a program in the RoboDK tree
    /// </summary>
    /// <param name="show"></param>
    void ShowTargets(bool visible=true);

    /// <summary>
    /// Returns the number of instructions of a program.
    /// </summary>
    /// <returns></returns>
    int InstructionCount();

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
    void Instruction(int ins_id, QString &name, int &instype, int &movetype, bool &isjointtarget, Mat &target, tJoints &joints);

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
    void setInstruction(int ins_id, const QString &name, int instype, int movetype, bool isjointtarget, const Mat &target, const tJoints &joints);

    /// <summary>
    /// Returns the list of program instructions as an MxN matrix, where N is the number of instructions and M equals to 1 plus the number of robot axes.
    /// </summary>
    /// <param name="instructions">the matrix of instructions</param>
    /// <returns>Returns 0 if success</returns>
    int InstructionList(tMatrix2D *instructions);

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
    double Update(int collision_check = RoboDK::COLLISION_OFF, int timeout_sec = 3600, double *out_nins_time_dist = nullptr, double mm_step = -1, double deg_step = -1);

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
    int InstructionListJoints(QString &error_msg, tMatrix2D **joint_list, double mm_step = 10.0, double deg_step = 5.0, const QString &save_to_file = "");

    /// <summary>
    /// Disconnect from the RoboDK API. This flushes any pending program generation.
    /// </summary>
    /// <returns></returns>
    bool Finish();


    /// Get the item pointer
    quint64 GetID();


private:
    /// Pointer to RoboDK link object
    RoboDK *_RDK;

    /// Pointer to the item inside RoboDK
    quint64 _PTR;

    /// Item type
    qint32 _TYPE;
};



/// Translation matrix class: Mat::transl.
ROBODK Mat transl(double x, double y, double z);

/// Translation matrix class: Mat::rotx.
ROBODK Mat rotx(double rx);

/// Translation matrix class: Mat::roty.
ROBODK Mat roty(double ry);

/// Translation matrix class: Mat::rotz.
ROBODK Mat rotz(double rz);


/////////////////////////////////////////////////////////////////
/// @brief Creates a new 2D matrix \ref tMatrix2D.. Use \ref Matrix2D_Delete to delete the matrix (to free the memory).
/// The Procedure @ref Debug_Matrix2D shows an example to read data from a tMatrix2D
ROBODK tMatrix2D* Matrix2D_Create();

/// @brief Deletes a \ref tMatrix2D.
/// @param[in] mat: Pointer of the pointer to the matrix
ROBODK void Matrix2D_Delete(tMatrix2D **mat);

/// @brief Sets the size of a \ref tMatrix2D.
/// @param[in/out] mat: Pointer to the matrix
/// @param[in] rows: The number of rows.
/// @param[in] cols: The number of columns.
ROBODK void Matrix2D_Set_Size(tMatrix2D *mat, int rows, int cols);

/// @brief Sets the size of a \ref tMatrix2D.
/// @param[in/out] mat: Pointer to the matrix
/// @param[in] dim: Dimension (1 or 2)
ROBODK int Matrix2D_Size(const tMatrix2D *mat, int dim);

/// @brief Returns the number of columns of a \ref tMatrix2D.
/// @param[in] mat: Pointer to the matrix
/// Returns the number of columns (Second dimension)
ROBODK int Matrix2D_Get_ncols(const tMatrix2D *var);

/// @brief Returns the number of rows of a \ref tMatrix2D.
/// @param[in] mat: Pointer to the matrix
/// Returns the number of rows (First dimension)
ROBODK int Matrix2D_Get_nrows(const tMatrix2D *var);

/// @brief Returns the value at location [i,j] of a \ref tMatrix2D.
/// @param[in] mat: Pointer to the matrix
/// Returns the value of the cell
ROBODK double Matrix2D_Get_ij(const tMatrix2D *var, int i, int j);

/// @brief Returns the pointer of a column of a \ref tMatrix2D.
/// A column has \ref Matrix2D_Get_nrows values that can be accessed/modified from the returned pointer continuously.
/// @param[in] mat: Pointer to the matrix
/// @param[in] col: Column to retreive.
/// /return double array (internal pointer) to the column
ROBODK double* Matrix2D_Get_col(const tMatrix2D *var, int col);

/// @brief Show an array through STDOUT
/// Given an array of doubles, it generates a string
ROBODK void Debug_Array(const double *array, int arraysize);

/// @brief Display the content of a \ref tMatrix2D through STDOUT. This is only intended for debug purposes.
/// @param[in] mat: Pointer to the matrix
ROBODK void Debug_Matrix2D(const tMatrix2D *mat);


/// @brief Displays the content of a \ref Mat through STDOUT. This is only intended for debug purposes.
/// @param[in] mat: pose matrix
/// @param[in] show_full_pose: set to false to display the 6 values of the pose as XYZWPR instead of the 4x4 matrix
//ROBODK void Debug_Mat(Mat pose, char show_full_pose);




//QDataStream &operator<<(QDataStream &data, const QMatrix4x4 &);
inline QDebug operator<<(QDebug dbg, const Mat &m){ return dbg.noquote() << m.ToString(); }
inline QDebug operator<<(QDebug dbg, const tJoints &jnts){ return dbg.noquote() << jnts.ToString(); }
inline QDebug operator<<(QDebug dbg, const Item &itm){ return dbg.noquote() << itm.ToString(); }

inline QDebug operator<<(QDebug dbg, const Mat *m){ return dbg.noquote() << (m == nullptr ? "Mat(null)" : m->ToString()); }
inline QDebug operator<<(QDebug dbg, const tJoints *jnts){ return dbg.noquote() << (jnts == nullptr ? "tJoints(null)" : jnts->ToString()); }
inline QDebug operator<<(QDebug dbg, const Item *itm){ return dbg.noquote() << (itm == nullptr ? "Item(null)" : itm->ToString()); }


#ifndef RDK_SKIP_NAMESPACE
}

#endif




#endif // ROBODK_API
