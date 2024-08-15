#include "pluginapiexample.h"

#include "irobodk.h"
#include "robodkinternalsocket.h"
#include "robodk_api.h"


PluginApiExample::PluginApiExample(QObject* parent)
    : QObject(parent)
    , _socket(nullptr)
    , _api(nullptr)
{
}

PluginApiExample::~PluginApiExample()
{
    PluginUnload();
}

QString PluginApiExample::PluginName()
{
    return QLatin1String("PluginApiExample");
}

QString PluginApiExample::PluginLoad(QMainWindow* , QMenuBar* , QStatusBar* ,
                             IRoboDK* rdk, const QString& )
{
    _socket = new RoboDKInternalSocket(rdk);
    _api = new RoboDK_API::RoboDK(_socket);

    return QString();
};


void PluginApiExample::PluginUnload()
{
    if (_api)
    {
        delete _api;
        _api = nullptr;
    }

    if (_socket)
    {
        delete _socket;
        _socket = nullptr;
    }
}

void PluginApiExample::PluginLoadToolbar(QMainWindow* , int )
{
}

bool PluginApiExample::PluginItemClick(Item , QMenu* , TypeClick )
{
    return false;
}

QString PluginApiExample::PluginCommand(const QString& , const QString& )
{
    return QString();
}

void PluginApiExample::PluginEvent(TypeEvent )
{
}

bool PluginApiExample::PluginItemClickMulti(QList<Item>& , QMenu* , TypeClick )
{
    return false;
}
