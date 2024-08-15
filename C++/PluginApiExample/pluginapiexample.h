#ifndef PLUGINAPIEXAMPLE_H
#define PLUGINAPIEXAMPLE_H


#include <QScopedPointer>
#include <QObjectCleanupHandler>

#include "iapprobodk.h"
#include "robodktypes.h"


class RoboDKInternalSocket;

namespace RoboDK_API
{
class RoboDK;
}


class PluginApiExample : public QObject, public IAppRoboDK
{
    Q_OBJECT
    Q_PLUGIN_METADATA(IID "RoboDK.IAppRoboDK")
    Q_INTERFACES(IAppRoboDK)

public:
    explicit PluginApiExample(QObject* parent = nullptr);
    virtual ~PluginApiExample();

    virtual QString PluginName();
    virtual QString PluginLoad(QMainWindow* mainWindow, QMenuBar* menuBar, QStatusBar* statusBar,
                               IRoboDK* rdk, const QString& settings = "");
    virtual void PluginUnload();
    virtual void PluginLoadToolbar(QMainWindow* mainWindow, int iconSize);
    virtual bool PluginItemClick(Item item, QMenu* menu, TypeClick clickType);
    virtual QString PluginCommand(const QString& command, const QString& value);
    virtual void PluginEvent(TypeEvent eventType);
    virtual bool PluginItemClickMulti(QList<Item>& itemList, QMenu* menu, TypeClick clickType);

private:
    QScopedPointer<RoboDK_API::RoboDK> _api;
    QObjectCleanupHandler _objectCleaner;
};


#endif // PLUGINAPIEXAMPLE_H
