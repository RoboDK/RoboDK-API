#include "robodkinternalsocket.h"

#include <cstring>

#include "irobodk.h"


RoboDKInternalSocket::RoboDKInternalSocket(IRoboDK* rdk, QObject* parent)
    : QAbstractSocket(QAbstractSocket::UnknownSocketType, parent)
    , _rdk(rdk)
    , _direction(Write)
    , _readOffset(0)
    , _writeOffset(0)
{
}

RoboDKInternalSocket::~RoboDKInternalSocket()
{
}

void RoboDKInternalSocket::connectToHost(const QString& hostName, quint16 port, OpenMode mode, NetworkLayerProtocol protocol)
{
    Q_UNUSED(hostName)
    Q_UNUSED(port)
    Q_UNUSED(protocol)

    if (open(mode))
        setSocketState(QAbstractSocket::ConnectedState);
}

void RoboDKInternalSocket::connectToHost(const QHostAddress& address, quint16 port, OpenMode mode)
{
    Q_UNUSED(address)
    Q_UNUSED(port)

    if (open(mode))
        setSocketState(QAbstractSocket::ConnectedState);
}

void RoboDKInternalSocket::disconnectFromHost()
{
    close();
}

qint64 RoboDKInternalSocket::bytesAvailable() const
{
    if (!isOpen() || _direction != Read)
        return 0;

    qint64 total = static_cast<qint64>(_data.size());
    qint64 result = total - _readOffset;
    return (result > 0) ? result : 0;
}

qint64 RoboDKInternalSocket::bytesToWrite() const
{
    return (_direction == Write) ? _data.size() : 0;
}

bool RoboDKInternalSocket::canReadLine() const
{
    if (!isOpen() || _direction != Read)
        return false;

    return _data.indexOf('\n', static_cast<int>(_readOffset)) >= 0;
}

bool RoboDKInternalSocket::open(OpenMode mode)
{
    if (!_rdk)
        return false;

    return QIODevice::open(mode | QIODevice::Unbuffered);
}

void RoboDKInternalSocket::close()
{
    setSocketState(QAbstractSocket::UnconnectedState);
    QIODevice::close();
}

bool RoboDKInternalSocket::isSequential() const
{
    return true;
}

bool RoboDKInternalSocket::atEnd() const
{
    return (_direction == Read && _readOffset >= _data.size());
}

bool RoboDKInternalSocket::waitForConnected(int msecs)
{
    Q_UNUSED(msecs)
    return (_rdk != nullptr);
}

bool RoboDKInternalSocket::waitForReadyRead(int msecs)
{
    Q_UNUSED(msecs)
    if (isOpen())
    {
        changeDirection(Read);
        return true;
    }
    return false;
}

bool RoboDKInternalSocket::waitForBytesWritten(int msecs)
{
    Q_UNUSED(msecs)
    return isOpen();
}

bool RoboDKInternalSocket::waitForDisconnected(int msecs)
{
    Q_UNUSED(msecs)
    return true;
}

qint64 RoboDKInternalSocket::readData(char* data, qint64 maxlen)
{
    changeDirection(Read);
    qint64 total = static_cast<qint64>(_data.size());
    qint64 tail = total - _readOffset;
    if (tail <= 0)
        return 0;

    qint64 result = qMin(tail, maxlen);
    if (result > 0)
    {
        std::memcpy(data, &_data.data()[_readOffset], result);
        _readOffset += result;
    }

    return result;
}

qint64 RoboDKInternalSocket::readLineData(char* data, qint64 maxlen)
{
    changeDirection(Read);
    qint64 total = static_cast<qint64>(_data.size());
    qint64 tail = total - _readOffset;
    if (tail <= 0 || maxlen <= 0)
        return 0;

    for (qint64 i = 0; i < qMin(tail, maxlen); ++i)
    {
        if (_data.data()[_readOffset + i] != '\n')
            continue;

        std::memcpy(data, &_data.data()[_readOffset], i + 1);
        _readOffset += i + 1;
        return i + 1;
    }
    return 0;
}

qint64 RoboDKInternalSocket::writeData(const char* data, qint64 len)
{
    changeDirection(Write);
    if (len <= 0)
        return 0;
    _data.append(data, static_cast<int>(len));
    _writeOffset += len;
    return len;
}

void RoboDKInternalSocket::changeDirection(Direction newDirection)
{
    if (newDirection == _direction)
        return;

    _readOffset = 0;
    _writeOffset = 0;
    _direction = newDirection;
    switch (_direction)
    {
    case Read:
        if (_rdk)
        {
            const QString command(QLatin1String("RDKCOM"));
            _rdk->setData(command, _data);
            _data = _rdk->getData(command);
        }
        else
        {
            _data.clear();
        }
        break;

    case Write:
        _data.clear();
        break;
    }
}
