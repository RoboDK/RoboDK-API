#ifndef ROBODKINTERNALSOCKET_H
#define ROBODKINTERNALSOCKET_H


#include <QAbstractSocket>
#include <QByteArray>


class IRoboDK;


class RoboDKInternalSocket : public QAbstractSocket
{
    Q_OBJECT

public:
    explicit RoboDKInternalSocket(IRoboDK* rdk, QObject* parent = nullptr);
    virtual ~RoboDKInternalSocket();

    void connectToHost(const QString &hostName, quint16 port, OpenMode mode = ReadWrite, NetworkLayerProtocol protocol = AnyIPProtocol) override;
    void connectToHost(const QHostAddress &address, quint16 port, OpenMode mode = ReadWrite) override;
    void disconnectFromHost() override;

    qint64 bytesAvailable() const override;
    qint64 bytesToWrite() const override;

    bool canReadLine() const override;

    bool open(OpenMode mode) override;
    void close() override;
    bool isSequential() const override;
    bool atEnd() const override;

    // for synchronous access
    bool waitForConnected(int msecs = 30000) override;
    bool waitForReadyRead(int msecs = 30000) override;
    bool waitForBytesWritten(int msecs = 30000) override;
    bool waitForDisconnected(int msecs = 30000) override;

protected:
    qint64 readData(char *data, qint64 maxlen) override;
    qint64 readLineData(char *data, qint64 maxlen) override;
    qint64 writeData(const char *data, qint64 len) override;

private:
    enum Direction
    {
        Read,
        Write
    };

private:
    void changeDirection(Direction newDirection);

private:
    Q_DISABLE_COPY(RoboDKInternalSocket)

    QByteArray _data;

    IRoboDK* _rdk;

    Direction _direction;
    qint64 _readOffset;
    qint64 _writeOffset;
};


#endif // ROBODKINTERNALSOCKET_H
