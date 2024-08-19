#include "pluginapiexample.h"

#include <QMenuBar>
#include <QAction>

#include "irobodk.h"
#include "robodkinternalsocket.h"
#include "robodk_api.h"


PluginApiExample::PluginApiExample(QObject* parent)
    : QObject(parent)
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

QString PluginApiExample::PluginLoad(QMainWindow* , QMenuBar* menuBar, QStatusBar* ,
                             IRoboDK* rdk, const QString& )
{
    auto socket = new RoboDKInternalSocket(rdk);
    socket->connectToHost(QString(), 0);
    _objectCleaner.add(socket);

    _api.reset(new RoboDK_API::RoboDK(socket));

    auto action = menuBar->addAction(tr("Plugin Api Example"), [&]
    {
        if (!_api)
            return;

        auto names = _api->getItemListNames();
        _api->ShowMessage(names.join(QLatin1String("<br>")));
    });

    _objectCleaner.add(action);

    return QString();
};


void PluginApiExample::PluginUnload()
{
    _api.reset();
    _objectCleaner.clear();
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
