#include "robodktypes.h"

#include <QtMath>
#include <QDebug>


//----------------------------------- tJoints class -------------------
tJoints::tJoints(int ndofs)
{
    _nDOFs = qMin(ndofs, RDK_SIZE_JOINTS_MAX);
    for (int i=0; i < _nDOFs; i++)
    {
        _Values[i] = 0.0;
    }
}

tJoints::tJoints(const tJoints &copy)
{
    SetValues(copy._Values, copy._nDOFs);
}

tJoints::tJoints(const double *joints, int ndofs)
{
    SetValues(joints, ndofs);
}

tJoints::tJoints(const float *joints, int ndofs)
{
    int ndofs_ok = qMin(ndofs, RDK_SIZE_JOINTS_MAX);
    double jnts[RDK_SIZE_JOINTS_MAX];

    for (int i=0; i < ndofs_ok; i++)
    {
        jnts[i] = joints[i];
    }
    SetValues(jnts, ndofs_ok);
}

tJoints::tJoints(const tMatrix2D *mat2d, int column, int ndofs)
{
    if (Matrix2D_Size(mat2d, 2) >= column)
    {
        _nDOFs = 0;
        qDebug() << "Warning: tMatrix2D column outside range when creating joints";
    }
    if (ndofs < 0)
    {
        ndofs = Matrix2D_Size(mat2d, 1);
    }
    _nDOFs = qMin(ndofs, RDK_SIZE_JOINTS_MAX);

    double *ptr = Matrix2D_Get_col(mat2d, column);
    SetValues(ptr, _nDOFs);
}

tJoints::tJoints(const QString &str)
{
    _nDOFs = 0;
    FromString(str);
}

const double* tJoints::ValuesD() const
{
    return _Values;
}

const float* tJoints::ValuesF() const
{
    for (int i=0; i < RDK_SIZE_JOINTS_MAX; i++)
    {
        _ValuesF[i] = _Values[i];
    }

    return _ValuesF;
}

#ifdef ROBODK_API_FLOATS
const float* tJoints::Values() const
{
    return ValuesF();
}
#else
const double* tJoints::Values() const
{
    return _Values;
}
#endif

double tJoints::Compare(const tJoints &other) const
{
    double sum_diff = 0.0;
    for (int i = 0; i <qMin(_nDOFs, other.Length()); i++)
    {
        sum_diff += qAbs(_Values[i] - other.Values()[i]);
    }
    return sum_diff;
}

double* tJoints::Data()
{
    return _Values;
}

void tJoints::SetValues(const double *values, int ndofs)
{
    if (ndofs >= 0)
    {
        _nDOFs = qMin(ndofs, RDK_SIZE_JOINTS_MAX);
    }

    for (int i=0; i<_nDOFs; i++)
    {
        _Values[i] = values[i];
    }
}

void tJoints::SetValues(const float *values, int ndofs)
{
    if (ndofs >= 0)
    {
        _nDOFs = qMin(ndofs, RDK_SIZE_JOINTS_MAX);
    }

    for (int i=0; i<_nDOFs; i++)
    {
        _Values[i] = values[i];
    }
}

int tJoints::GetValues(double *values)
{
    for (int i=0; i<_nDOFs; i++)
    {
        values[i] = _Values[i];
    }

    return _nDOFs;
}

QString tJoints::ToString(const QString &separator, int precision) const
{
    QString values;
    for (int i = 0; i < _nDOFs; i++)
    {
        if (i > 0)
        {
            values.append(separator);
        }
        values.append(QString::number(_Values[i], 'f', precision));
    }
    return values;
}

bool tJoints::FromString(const QString &str)
{
    const QLatin1Char separator(',');

    QString s = str;
    s.replace(QLatin1Char(';'), separator);
    s.replace(QLatin1Char('\t'), separator);

#if (QT_VERSION < QT_VERSION_CHECK(5, 14, 0))
    const QString::SplitBehavior behavior = QString::SkipEmptyParts;
#else
    const Qt::SplitBehavior behavior = Qt::SkipEmptyParts;
#endif

    QStringList jointList = s.split(separator, behavior);
    _nDOFs = qMin(jointList.length(), RDK_SIZE_JOINTS_MAX);
    for (int i=0; i < _nDOFs; i++)
    {
        _Values[i] = jointList[i].trimmed().toDouble();
    }
    return true;
}

int tJoints::Length() const
{
    return _nDOFs;
}

void tJoints::setLength(int new_length)
{
    if (new_length >= 0 && new_length < _nDOFs)
    {
        _nDOFs = new_length;
    }
}

bool tJoints::Valid()
{
    return _nDOFs > 0;
}
//---------------------------------------------------------------------


//----------------------------------- Mat class -----------------------
Mat transl(double x, double y, double z)
{
    return Mat::transl(x,y,z);
}

Mat rotx(double rx)
{
    return Mat::rotx(rx);
}

Mat roty(double ry)
{
    return Mat::roty(ry);
}

Mat rotz(double rz)
{
    return Mat::rotz(rz);
}

Mat::Mat()
    : QMatrix4x4()
    , _valid(true)
{
    setToIdentity();
}

Mat::Mat(bool valid)
    : QMatrix4x4()
    , _valid(valid)
{
    setToIdentity();
}

Mat::Mat(const QMatrix4x4 &matrix)
    : QMatrix4x4(matrix)
    , _valid(true)
{
}

Mat::Mat(const Mat &matrix)
    : QMatrix4x4(matrix)
    , _valid(matrix._valid)
{
}

Mat::Mat(double nx, double ox, double ax, double tx,
    double ny, double oy, double ay, double ty,
    double nz, double oz, double az, double tz)
    : QMatrix4x4(nx, ox, ax, tx, ny, oy, ay, ty, nz, oz, az, tz, 0.0, 0.0, 0.0, 1.0)
    , _valid(true)
{
}

Mat::Mat(const double v[16])
    : QMatrix4x4(v[0], v[4], v[8], v[12], v[1], v[5], v[9], v[13],
                 v[2], v[6], v[10], v[14], v[3], v[7], v[11], v[15])
    , _valid(true)
{
}

Mat::Mat(const float v[16])
    : QMatrix4x4(v[0], v[4], v[8], v[12], v[1], v[5], v[9], v[13],
                 v[2], v[6], v[10], v[14], v[3], v[7], v[11], v[15])
    , _valid(true)
{
}

Mat::Mat(double x, double y, double z)
    : QMatrix4x4(1.0, 0.0, 0.0, x, 0.0, 1.0, 0.0, y, 0.0, 0.0, 1.0, z, 0.0, 0.0, 0.0, 1.0)
    , _valid(true)
{
}

Mat::~Mat()
{
}

void Mat::VX(tXYZ xyz) const
{
    xyz[0] = Get(0, 0);
    xyz[1] = Get(1, 0);
    xyz[2] = Get(2, 0);
}

void Mat::VY(tXYZ xyz) const
{
    xyz[0] = Get(0, 1);
    xyz[1] = Get(1, 1);
    xyz[2] = Get(2, 1);
}

void Mat::VZ(tXYZ xyz) const
{
    xyz[0] = Get(0, 2);
    xyz[1] = Get(1, 2);
    xyz[2] = Get(2, 2);
}

void Mat::Pos(tXYZ xyz) const
{
    xyz[0] = Get(0, 3);
    xyz[1] = Get(1, 3);
    xyz[2] = Get(2, 3);
}

void Mat::setVX(double x, double y, double z)
{
    Set(0,0, x);
    Set(1,0, y);
    Set(2,0, z);
}

void Mat::setVY(double x, double y, double z)
{
    Set(0,1, x);
    Set(1,1, y);
    Set(2,1, z);
}

void Mat::setVZ(double x, double y, double z)
{
    Set(0,2, x);
    Set(1,2, y);
    Set(2,2, z);
}

void Mat::setPos(double x, double y, double z)
{
    Set(0,3, x);
    Set(1,3, y);
    Set(2,3, z);
}

void Mat::setVX(double xyz[3])
{
    Set(0,0, xyz[0]);
    Set(1,0, xyz[1]);
    Set(2,0, xyz[2]);
}

void Mat::setVY(double xyz[3])
{
    Set(0,1, xyz[0]);
    Set(1,1, xyz[1]);
    Set(2,1, xyz[2]);
}

void Mat::setVZ(double xyz[3])
{
    Set(0,2, xyz[0]);
    Set(1,2, xyz[1]);
    Set(2,2, xyz[2]);
}

void Mat::setPos(double xyz[3])
{
    Set(0,3, xyz[0]);
    Set(1,3, xyz[1]);
    Set(2,3, xyz[2]);
}

void Mat::setValues(double pose[16])
{
    Set(0,0, pose[0]);
    Set(1,0, pose[1]);
    Set(2,0, pose[2]);
    Set(3,0, pose[3]);

    Set(0,1, pose[4]);
    Set(1,1, pose[5]);
    Set(2,1, pose[6]);
    Set(3,1, pose[7]);

    Set(0,2, pose[8]);
    Set(1,2, pose[9]);
    Set(2,2, pose[10]);
    Set(3,2, pose[11]);

    Set(0,3, pose[12]);
    Set(1,3, pose[13]);
    Set(2,3, pose[14]);
    Set(3,3, pose[15]);
}

void Mat::Set(int i, int j, double value)
{
    QVector4D rw(this->row(i));
    rw[j] = value;
    setRow(i, rw);
}

double Mat::Get(int i, int j) const
{
    return row(i)[j];
}

Mat Mat::inv() const
{
    return this->inverted();
}

bool Mat::isHomogeneous() const
{
    const bool debug_info = false;
    tXYZ vx, vy, vz;
    const double tol = 1e-7;
    VX(vx);
    VY(vy);
    VZ(vz);

    if (fabs((double) DOT(vx,vy)) > tol)
    {
        if (debug_info)
        {
            qDebug() << "Vector X and Y are not perpendicular!";
        }
        return false;
    }
    else if (fabs((double) DOT(vx,vz)) > tol)
    {
        if (debug_info)
        {
            qDebug() << "Vector X and Z are not perpendicular!";
        }
        return false;
    }
    else if (fabs((double) DOT(vy,vz)) > tol)
    {
        if (debug_info)
        {
            qDebug() << "Vector Y and Z are not perpendicular!";
        }
        return false;
    }
    else if (fabs((double) (NORM(vx)-1.0)) > tol)
    {
        if (debug_info)
        {
            qDebug() << "Vector X is not unitary! " << NORM(vx);
        }
        return false;
    }
    else if (fabs((double) (NORM(vy)-1.0)) > tol)
    {
        if (debug_info)
        {
            qDebug() << "Vector Y is not unitary! " << NORM(vy);
        }
        return false;
    }
    else if (fabs((double) (NORM(vz)-1.0)) > tol)
    {
        if (debug_info)
        {
            qDebug() << "Vector Z is not unitary! " << NORM(vz);
        }
        return false;
    }
    return true;
}

bool Mat::MakeHomogeneous()
{
    tXYZ vx, vy, vz;
    VX(vx);
    VY(vy);
    VZ(vz);
    bool is_homogeneous = isHomogeneous();

    NORMALIZE(vx);
    CROSS(vz, vx, vy);
    NORMALIZE(vz);
    CROSS(vy, vz, vx);
    NORMALIZE(vy);
    setVX(vx);
    setVY(vy);
    setVZ(vz);
    Set(3,0, 0.0);
    Set(3,1, 0.0);
    Set(3,2, 0.0);
    Set(3,3, 1.0);
    return !is_homogeneous;
}

void Mat::ToXYZRPW(tXYZWPR xyzwpr) const
{
    double x = Get(0,3);
    double y = Get(1,3);
    double z = Get(2,3);
    double w, p, r;

    if (Get(2,0) > (1.0 - 1e-6))
    {
        p = -M_PI*0.5;
        r = 0;
        w = atan2(-Get(1,2), Get(1,1));
    }
    else if (Get(2,0) < -1.0 + 1e-6)
    {
        p = 0.5*M_PI;
        r = 0;
        w = atan2(Get(1,2),Get(1,1));
    }
    else
    {
        p = atan2(-Get(2, 0), sqrt(Get(0, 0) * Get(0, 0) + Get(1, 0) * Get(1, 0)));
        w = atan2(Get(1, 0), Get(0, 0));
        r = atan2(Get(2, 1), Get(2, 2));
    }

    xyzwpr[0] = x;
    xyzwpr[1] = y;
    xyzwpr[2] = z;
    xyzwpr[3] = r*180.0/M_PI;
    xyzwpr[4] = p*180.0/M_PI;
    xyzwpr[5] = w*180.0/M_PI;
}

QString Mat::ToString(const QString &separator, int precision, bool xyzwpr_only) const
{
    if (!Valid())
    {
        return "Mat(Invalid)";
    }

    QString str;
    if (!isHomogeneous())
    {
        str.append("Warning!! Pose is not homogeneous! Use Mat::MakeHomogeneous() to make this matrix homogeneous\n");
    }

    str.append("Mat(XYZRPW_2_Mat(");

    tXYZWPR xyzwpr;
    ToXYZRPW(xyzwpr);

    for (int i = 0; i < 6; i++)
    {
        if (i > 0)
        {
            str.append(separator);
        }
        str.append(QString::number(xyzwpr[i], 'f', precision));
    }
    str.append("))");

    if (xyzwpr_only)
    {
        return str;
    }

    str.append("\n");

    for (int i = 0; i < 4; i++)
    {
        str.append("[");
        for (int j = 0; j < 4; j++)
        {
            str.append(QString::number(row(i)[j], 'f', precision));
            if (j < 3) {
                str.append(separator);
            }
        }
        str.append("];\n");
    }
    return str;
}

bool Mat::FromString(const QString &pose_str)
{
    QString pose_str2 = pose_str.trimmed();

    const Qt::CaseSensitivity cs = Qt::CaseInsensitive;
    if (pose_str2.startsWith("Mat(", cs))
    {
        pose_str2.remove(0, 4);
        pose_str2 = pose_str2.trimmed();
    }

    if (pose_str2.startsWith("XYZRPW_2_Mat(", cs))
    {
        pose_str2.remove(0, 13);
        pose_str2 = pose_str2.trimmed();
    }

    while (pose_str2.endsWith(')'))
    {
        pose_str2.chop(1);
    }

    const QLatin1Char separator(',');
    pose_str2.replace(QLatin1Char(';'), separator);
    pose_str2.replace(QLatin1Char('\t'), separator);

#if (QT_VERSION < QT_VERSION_CHECK(5, 14, 0))
    const QString::SplitBehavior behavior = QString::SkipEmptyParts;
#else
    const Qt::SplitBehavior behavior = Qt::SkipEmptyParts;
#endif

    QStringList values_list = pose_str2.split(separator, behavior);
    tXYZWPR xyzwpr = {0.0, 0.0, 0.0, 0.0, 0.0, 0.0};

    if (values_list.length() < 6)
    {
        FromXYZRPW(xyzwpr);
        return false;
    }

    for (int i = 0; i < 6; i++)
    {
        xyzwpr[i] = values_list[i].trimmed().toDouble();
    }

    FromXYZRPW(xyzwpr);
    return true;
}

Mat Mat::XYZRPW_2_Mat(double x, double y, double z, double r, double p, double w)
{
    double a = r * M_PI / 180.0;
    double b = p * M_PI / 180.0;
    double c = w * M_PI / 180.0;
    double ca = cos(a);
    double sa = sin(a);
    double cb = cos(b);
    double sb = sin(b);
    double cc = cos(c);
    double sc = sin(c);
    return Mat(cb * cc, cc * sa * sb - ca * sc, sa * sc + ca * cc * sb, x,
        cb * sc, ca * cc + sa * sb * sc, ca * sb * sc - cc * sa, y,
        -sb, cb * sa, ca * cb, z);
}

Mat Mat::XYZRPW_2_Mat(tXYZWPR xyzwpr)
{
    return XYZRPW_2_Mat(xyzwpr[0], xyzwpr[1], xyzwpr[2], xyzwpr[3], xyzwpr[4], xyzwpr[5]);
}

void Mat::FromXYZRPW(tXYZWPR xyzwpr)
{
    Mat newmat = Mat::XYZRPW_2_Mat(xyzwpr[0], xyzwpr[1], xyzwpr[2],
        xyzwpr[3], xyzwpr[4], xyzwpr[5]);

    for (int i = 0; i < 4; i++)
    {
        for (int j = 0; j < 4; j++)
        {
            this->Set(i, j, newmat.Get(i, j));
        }
    }
}

const double* Mat::ValuesD() const
{
    for(int i = 0; i < 16; ++i)
    {
        _ddata16[i] = constData()[i];
    }
    return _ddata16;
}

const float* Mat::ValuesF() const
{
    return constData();
}

#ifdef ROBODK_API_FLOATS
const float* Mat::Values() const
{
    return constData();
}
#else
const double* Mat::Values() const
{
    return ValuesD();
}
#endif

void Mat::Values(double data[16]) const
{
    for(int i = 0; i < 16; ++i)
    {
        data[i] = constData()[i];
    }
}

void Mat::Values(float data[16]) const
{
    for(int i = 0; i < 16; ++i)
    {
        data[i] = constData()[i];
    }
}

bool Mat::Valid() const
{
    return _valid;
}

Mat Mat::transl(double x, double y, double z)
{
    Mat mat;
    mat.setToIdentity();
    mat.setPos(x, y, z);
    return mat;
}

Mat Mat::rotx(double rx)
{
    double cx = cos(rx);
    double sx = sin(rx);
    return Mat(1, 0, 0, 0, 0, cx, -sx, 0, 0, sx, cx, 0);
}

Mat Mat::roty(double ry)
{
    double cy = cos(ry);
    double sy = sin(ry);
    return Mat(cy, 0, sy, 0, 0, 1, 0, 0, -sy, 0, cy, 0);
}

Mat Mat::rotz(double rz)
{
    double cz = cos(rz);
    double sz = sin(rz);
    return Mat(cz, -sz, 0, 0, sz, cz, 0, 0, 0, 0, 1, 0);
}
//---------------------------------------------------------------------


//----------------------------------- 2D matrix functions -------------
void emxInit_real_T(tMatrix2D **pEmxArray, int numDimensions)
{
    tMatrix2D *emxArray;
    int i;
    *pEmxArray = (tMatrix2D *)malloc(sizeof(tMatrix2D));
    emxArray = *pEmxArray;
    emxArray->data = (double *)NULL;
    emxArray->numDimensions = numDimensions;
    emxArray->size = (int *)malloc((unsigned int)(sizeof(int) * numDimensions));
    emxArray->allocatedSize = 0;
    emxArray->canFreeData = true;
    for (i = 0; i < numDimensions; i++)
    {
        emxArray->size[i] = 0;
    }
}

tMatrix2D* Matrix2D_Create()
{
    tMatrix2D *matrix;
    emxInit_real_T((tMatrix2D**)(&matrix), 2);
    return matrix;
}

void emxFree_real_T(tMatrix2D **pEmxArray)
{
    if (*pEmxArray != (tMatrix2D *)NULL)
    {
        if (((*pEmxArray)->data != (double *)NULL) && (*pEmxArray)->canFreeData)
        {
            free((void *)(*pEmxArray)->data);
        }
        free((void *)(*pEmxArray)->size);
        free((void *)*pEmxArray);
        *pEmxArray = (tMatrix2D *)NULL;
    }
}

void Matrix2D_Delete(tMatrix2D **mat)
{
    emxFree_real_T((tMatrix2D**)(mat));
}

void emxEnsureCapacity(tMatrix2D *emxArray, int oldNumel, unsigned int elementSize)
{
    int newNumel;
    int i;
    double *newData;
    if (oldNumel < 0)
    {
        oldNumel = 0;
    }
    newNumel = 1;
    for (i = 0; i < emxArray->numDimensions; i++)
    {
        newNumel *= emxArray->size[i];
    }

    if (newNumel > emxArray->allocatedSize)
    {
        i = emxArray->allocatedSize;
        if (i < 16)
        {
            i = 16;
        }
        while (i < newNumel)
        {
            if (i > 1073741823)
            {
                i =(2147483647);//MAX_int32_T;
            }
            else
            {
                i <<= 1;
            }
        }

        newData = (double*) calloc((unsigned int)i, elementSize);
        if (emxArray->data != NULL)
        {
            memcpy(newData, emxArray->data, elementSize * oldNumel);
            if (emxArray->canFreeData)
            {
                free(emxArray->data);
            }
        }
        emxArray->data = newData;
        emxArray->allocatedSize = i;
        emxArray->canFreeData = true;
    }
}

void Matrix2D_Set_Size(tMatrix2D *mat, int rows, int cols)
{
    int old_numel;
    old_numel = mat->size[0] * mat->size[1];
    mat->size[0] = rows;
    mat->size[1] = cols;
    emxEnsureCapacity(mat, old_numel, sizeof(double));
}

int Matrix2D_Size(const tMatrix2D *var, int dim)
{
    // ONE BASED!!
    if (var->numDimensions >= dim)
    {
        return var->size[dim - 1];
    }
    else
    {
        return 0;
    }
}

int Matrix2D_Get_ncols(const tMatrix2D *var)
{
    return Matrix2D_Size(var, 2);
}

int Matrix2D_Get_nrows(const tMatrix2D *var)
{
    return Matrix2D_Size(var, 1);
}

double Matrix2D_Get_ij(const tMatrix2D *var, int i, int j)
{
    // ZERO BASED!!
    return var->data[var->size[0] * j + i];
}

void Matrix2D_Set_ij(const tMatrix2D *var, int i, int j, double value)
{
    // ZERO BASED!!
    var->data[var->size[0] * j + i] = value;
}

double *Matrix2D_Get_col(const tMatrix2D *var, int col)
{
    // ZERO BASED!!
    return (var->data + var->size[0] * col);
}

bool Matrix2D_Copy(const tMatrix2D *from, tMatrix2D *to)
{
    if (from->numDimensions != 2 || to->numDimensions != 2)
    {
        Matrix2D_Set_Size(to, 0,0);
        return false;
    }

    int sz1 = Matrix2D_Size(from,1);
    int sz2 = Matrix2D_Size(from,2);
    Matrix2D_Set_Size(to, sz1, sz2);
    int numel = sz1*sz2;
    for (int i = 0; i < numel; i++)
    {
        to->data[i] = from->data[i];
    }

    return true;
}


void Matrix2D_Add(tMatrix2D *var, const double *array, int numel)
{
    int oldnumel;
    int size1 = var->size[0];
    int size2 = var->size[1];
    oldnumel = size1*size2;
    var->size[1] = size2 + 1;
    emxEnsureCapacity(var, oldnumel, (int)sizeof(double));
    numel = qMin(numel, size1);
    for (int i=0; i<numel; i++){
        var->data[size1*size2 + i] = array[i];
    }
}

void Matrix2D_Add(tMatrix2D *var, const tMatrix2D *varadd)
{
    int oldnumel;
    int size1 = var->size[0];
    int size2 = var->size[1];
    int size1_ap = varadd->size[0];
    int size2_ap = varadd->size[1];
    int numel = size1_ap*size2_ap;
    if (size1 != size1_ap)
    {
        return;
    }
    oldnumel = size1*size2;
    var->size[1] = size2 + size2_ap;
    emxEnsureCapacity(var, oldnumel, (int)sizeof(double));
    for (int i=0; i<numel; i++)
    {
        var->data[size1*size2 + i] = varadd->data[i];
    }
}

void Debug_Array(const double *array, int arraysize)
{
    int i;
    QString strout;
    for (i = 0; i < arraysize; i++) {
        strout.append(QString::number(array[i], 'f', 3));
        if (i < arraysize - 1) {
            strout.append(" , ");
        }
    }
    qDebug().noquote() << strout;
}

void Debug_Matrix2D(const tMatrix2D *emx)
{
    int size1;
    int size2;
    int j;
    double *column;
    size1 = Matrix2D_Get_nrows(emx);
    size2 = Matrix2D_Get_ncols(emx);
    qDebug().noquote() << "Matrix size = " << size1 << " x " << size2;
    if (size1*size2 == 0)
    {
        return;
    }
    for (j = 0; j<size2; j++)
    {
        column = Matrix2D_Get_col(emx, j);
        Debug_Array(column, size1);
    }
}

void Matrix2D_Save(QDataStream *st, tMatrix2D *emx)
{
    int i;
    *st << emx->numDimensions;
    int size_values = 1;
    for (i = 0; i < emx->numDimensions; i++)
    {
        qint32 sizei = emx->size[i];
        size_values = size_values * sizei;
        *st << sizei;
    }
    for (i = 0; i < size_values; i++)
    {
        *st << emx->data[i];
    }
}

void Matrix2D_Save(QTextStream *st, tMatrix2D *emx, bool csv)
{
    int size1;
    int size2;
    int j;
    double *column;
    size1 = Matrix2D_Get_nrows(emx);
    size2 = Matrix2D_Get_ncols(emx);
    //*st << "% Matrix size = " << size1 << " x " << size2;
    if (size1 * size2 == 0)
    {
        return;
    }

    if (csv)
    {
        for (j = 0; j<size2; j++)
        {
            column = Matrix2D_Get_col(emx, j);
            for (int i = 0; i < size1; i++)
            {
                *st << QString::number(column[i], 'f', 8) << ", ";
            }
            *st << "\n";
        }
    }
    else
    {
        for (j = 0; j<size2; j++)
        {
            column = Matrix2D_Get_col(emx, j);
            *st << "[";
            for (int i = 0; i < size1; i++)
            {
                *st << QString::number(column[i], 'f', 8) << " ";
            }
            *st << "];\n";
        }
    }
}

void Matrix2D_Load(QDataStream *st, tMatrix2D **emx)
{
    if (st->atEnd())
    {
        qDebug() << "No data to read";
        return;
    }

    if (*emx != nullptr)
    {
        Matrix2D_Delete(emx);
    }

    int i;
    qint32 ndim;
    qint32 sizei;    
    *st >> ndim;
    qDebug() << "Loading matrix of dimensions: " << ndim;
    emxInit_real_T(emx, ndim);
    int size_values = 1;
    for (i = 0; i < ndim; i++)
    {
        *st >> sizei;
        size_values = size_values * sizei;
        (*emx)->size[i] = sizei;
    }
    //emxEnsureCapacity((emxArray__common *) *emx, 0, (int32_T)sizeof(real_T));
    emxEnsureCapacity(*emx, 0, sizeof(double));
    double value;
    for (i = 0; i < size_values; i++)
    {
        *st >> value;
        (*emx)->data[i] = value;
    }
}
