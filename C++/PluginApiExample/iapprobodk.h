/*! \mainpage RoboDK Plug-In Interface
*
* \section LinkIntro Introduction
*
* This document introduces the RoboDK Plug-in Interface. The plugin interface allows you to to develop Plug-Ins for RoboDK. RoboDK Plug-Ins allow extending RoboDK by using the RoboDK Interface and the RoboDK API.
* Contrary to the default RoboDK API (provided in Python, C#, C++, Matlab, etc), this RoboDK Plug-In interface is linked natively into the core of RoboDK.
* Therefore, when the RoboDK API is used inside the Plugin Interface (using IItem and IRoboDK) the speed is faster than using the default API \ref LinkTiming and it allows you to better filter and synchronize events using the PluginEvent callback.
* However, contrary to the standard RoboDK API, all RoboDK Plug-In applications must exist within RoboDK's environment.
*
* Some RoboDK Example plugins are available here:
* - https://github.com/RoboDK/Plug-In-Interface
*
* Each example includes the *robodk_interface* folder. This folder is required by every plug-in and defines the interface to RoboDK.
*
* These examples include a customized robot panel applying robot forward and inverse kinematics, a real-time example, a plugin simulating the gravity and an OPC-UA interface based on [Open62541](https://open62541.org/) (Server and Client examples).
*
* Double click the PluginExample.pro file to start the project with Qt.
* Make sure to follow the installation requirements section (\ref LinkInstall) to install Qt as a C++ development environment.
*
* Important: The plugin inteface can change with different major versions of RoboDK. Make sure to use the right plugin inteface header and source files for your RoboDK version.
*
*
* \section LinkPlugin RoboDK Plug-In Structure
*
* \subsection LinkPluginI Plug-In interface (IAppRoboDK)
* Each plugin must implement the IAppRoboDK class. The IAppRoboDK defines the interface to the RoboDK application.
*
* Contrary to the standard API, the Plug-In interface allows you to interact with RoboDK's main window and customize the appearance of RoboDK through the IAppRoboDK class. The toolbar, the menu bar and windows can be customized by using the IAppRoboDK class.
*
* \image html plugin-example.png
*
* You can load one of the sample plug-ins by selecting:
* - Tools - Plug-Ins
*
* \image html plugin-load.png width=600
*
* \subsection LinkPluginRoboDKAPI RoboDK API inside a Plug-In
*
* \subsubsection LinkRoboDKAPI IRoboDK (RoboDK)
* The IRoboDK class (or RoboDK) defines the interface to the RoboDK API. This RoboDK API is the same available by default (https://robodk.com/doc/en/RoboDK-API.html#RoboDKAPI). However the RoboDK API is faster when you use it inside a RoboDK Plug-In: \ref LinkTiming.
* When the plugin is loaded using class: IAppRoboDK::PluginLoad it passes a pointer to IRoboDK which is the interface to the RoboDK API.
*
* RoboDK and IRoboDK are exactly the same type of class. RoboDK is used in the default examples to make it compatible with the standard C++ RoboDK API.
*
* More information about the RoboDK API is available here:
* - IRoboDK: C++ reference for the plugin.
* - Python Reference (using standard API): https://robodk.com/doc/en/PythonAPI/robolink.html.
*
*
*
* \subsubsection LinkItem IItem (Item)
* The IItem class (or Item) can be used to operate on any item available in the RoboDK tree. Use functions such as class: IRoboDK::getItem or class: IRoboDK::getItemList to retrieve items from the RoboDK station tree.
* Item is a pointer to IItem. Items should be deleted using class: IItem::Delete (not using the class destructor).
*
* More information about the RoboDK Item class (based on the Python API) is available here:
* - https://robodk.com/doc/en/PythonAPI/robolink.html#robolink-item.
*
*
* \subsubsection LinkTypes RoboDK types file
* The \ref robodktypes.h file defines a set of types used by the RoboDK API. Including:
* - \ref Mat class for Pose manipulations.
* - \ref tJoints class to represent robot joint variables
* - \ref tMatrix2D data structure to represent a variable size 2D matrix (mostly used for internal purposes)
*
*
*
* \subsubsection LinkPluginAPI Plug-In Interface vs. RoboDK API
* The RoboDK API is a generic set of commands that allows you to interact with RoboDK and automate tasks. The RoboDK API is used by default when macros are used in RoboDK.
* The RoboDK Plug-In interface includes an interface to the RoboDK API.
*
* The main advantages of using the RoboDK API through a Plug-In Inteface are the following:
* - The RoboDK API is much faster because it is loaded as a library (a RoboDK Plug-In is actually a library loaded by RoboDK).
* - You can customize the appearance of RoboDK's main window (including the menu, toolbar, and add docked windows).
*
* You should pay attention to the following when using the RoboDK API inside a Plug-In:
* - Items (Item/IItem) are pointers, not objects. You can check if an item is valid or not by checking if it is a null pointer (nullptr). More information here: \ref ItemValid.
* - You must call class: IRoboDK::Render every time you want to update the screen (for example, if you change the position of a robot using class: IItem::Joints). Updading the screen is not done automatically.
* - Plug-Ins can only be deployed as C++ code using Qt libraries.
*
*
*
* \section LinkTiming Timing tests
* The \ref PluginExample application shows how to implement a basic plugin. Among other things it performs some timing tests to calculate the speed of RoboDK on a specific computer.
* By selecting the "Plugin Speed Information" button you'll obtain the timing statistics.
*
* \image html sampleoutput.png width=800
*
* These statistics are generated by class: PluginExample::callback_information. For example, forward and inverse kinematics are usually under 2 micro seconds and 10 micro seconds respectively (1 micro second = 1e-6 seconds).
*
*
*
* \section LinkRequirements Requirements
* Each RoboDK Plug-In must be developed using the Qt Creator and follow Qt's project guidelines.
* It is recommended to use the \ref PluginExample project to get started with your new RoboDK Plug-In (double click PluginExample.pro to open it with Qt Creator).
*
* RoboDK must be installed to develop Plug-Ins. The free version of RoboDK is enough to develop a Plug-In as a proof of concept.
*
*
* \subsection LinkInstall Installation Requirements
* Requirements to make RoboDK Plug-Ins work:
* - Install RoboDK (v3.5.4 or later): https://robodk.com/download
* - Make sure you compile your plugin using the correct version of Qt and compiler:
*   - Qt version 5.15 on Windows (MSVC2019).
*   - Qt version 5.15 on Mac (clang 64 bit).
*   - Qt version 5.12 on Linux.
* - It is possible to run in \ref LinkDebug debug mode on Windows.
*
* \image html qttoolkit.png width=800
*
* - Place your plugin files in the folder: C:/RoboDK/bin/plugins/ (DLL files). This is set by default in the PluginExample.pro file (as shown in the following image)
* - Start RoboDK (<strong>C:/RoboDK/bin/RoboDK.exe</strong>) and pass the command line argument: <strong>-PLUGINSLOAD</strong> as shown in the following image.
*   - Alternatively, you can pass the argument "-PLUGINLOAD=path-to-your-plugin.dll" if the DLL is not placed in the default path. The value can be the path to the library, the name of the file in the plugins folder or the name of the plugin (\ref PluginName).
*   - You can also start RoboDK using the BAT file: C:/RoboDK/RoboDK-Allow-Plugins.bat. The example plugins will be displayed.
*   - Select Tools-Plug-Ins for more options. Future RoboDK versions of RoboDK will load plugins located in C:/RoboDK/bin/plugins automatically
* - For development purposes, make sure to start the plugin with RoboDK and pass the -PLUGINSLOAD argument as shown in the following image.
* <br>
* You can load one of the sample plug-ins by selecting:
* - Tools - Plug-Ins
*
* The default location for RoboDK plugins is C:/RoboDK/bin/plugins
*
* \image html qtrun.png width=800
*
*
* \section LinkDebug Run in Debug mode
* Your Plug-In release and debug binaries should not be mixed with RoboDK's release and debug binaries.
* RoboDK debug binaries are not provided by default.
*
* To properly run your plugin in debug mode you should use the RoboDK debug binary files:
* - Contact us to get the debug version of RoboDK (<strong>bind</strong> folder).
* - Unzip the bind folder in <strong>C:/RoboDK/bind/</strong>.
* - Select Projects-Run-Run Settings and set Executable to <strong>C:/RoboDK/bind/RoboDK.exe</strong> (as shown in the following image, don't forget the <strong>d</strong>).
*
* Important: Mixing a debug DLL with a release DLL will not work (a message will be provided as console output). Make sure you update this setting every time you switch debug and release modes.
*
* Important: If you experience strange plugin loading issues, try to delete all plugins and build them again (all files in C:/RoboDK/bin/plugins and C:/RoboDK/bind/plugins).
*
* \image html plugin-run-debug-setting.jpg
*
* - Select the Debug build and you can start debugging as usual.
*
* \image html plugin-debug-example.jpg width=800
*
*
*
* \section LinkQt Qt Tips
* RoboDK Plug-Ins must be created using the Qt Plugin Framework. Qt is based on C++, therefore, it is required to program the RoboDK Plug-In in C++.
*
* Qt is a set of useful libraries for C++ and Qt Creator is the default development environment (IDE) for Qt. We recommneded using Qt Creator as development environment for programming a RoboDK Plug-In.
*
* This list provides some useful links and tips for programming with Qt:
* - Double click the PluginExample.pro file to open the example project using Qt Creator.
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
* - Latest RoboDK API on GitHub (you'll find RoboDK Plugins in a subfolder): https://github.com/RoboDK/RoboDK-API.
* - RoboDK API Introductory video: https://www.youtube.com/watch?v=3I6OK1Kd2Eo.
*
*/


#ifndef IAPPROBODK_H
#define IAPPROBODK_H

#include <QtPlugin>
#include <QString>
#include <QList>

#include "iitem.h"

class QMainWindow;
class QMenuBar;
class QStatusBar;
class QToolBar;
class QTreeWidgetItem;
class QMenu;
class IRoboDK;


/// \brief Interface to RoboDK. Each plugin must implement this class to establish the interface to RoboDK. More information in the \ref LinkPlugin section.
/// An example PluginExample is available to show how to implement this class.
class IAppRoboDK
{
public:

    /// Types of clicks for \ref PluginItemClick function.
    enum TypeClick {

        /// No click
        ClickNone = -1,

        /// Left click
        ClickLeft = 0,

        /// Ctrl Left click
        ClickCtrlLeft = 1,

        /// Right click
        ClickRight = 2,

        /// Double click
        ClickDouble = 3
    };

    /// Event types for \ref PluginEvent function
    enum TypeEvent {

        /// Render event: The RoboDK screen is re-drawn, including the tree and the 3D environment. This function is called with the main OpenGL context active.
        /// At this moment you can call IRoboDK::DrawGeometry to customize the displayed scene
        EventRender = 1,

        /// Moved event: Something has moved, such as a robot, reference frame, object or tool. It is very likely that an EventRender will be triggered immediately after this event.
        EventMoved = 2,

        /// An item has been added or deleted in the station or the active station has changed. This event is usually followed by a EventMoved and EventRender event.
        /// If we added a new item (for example, a reference frame) it is very likely that an EventMoved will follow with the updated position of the newly added item(s)
        EventChanged = 3,

        /// This event is triggered when we change the active station and a new station gains focus (IRoboDK::getActiveStation returns the station that was just opened). In this case we can load station-specific settings using IRoboDK::getParam or IRoboDK::getData.
        EventChangedStation = 4,

        /// The user requested to save the project and the RDK file will be saved to disk. It is recommended to save all station-specific settings at this moment.
        /// At this momment you can save station-specific parameters using \ref IRoboDK::setParam or \ref IRoboDK::setData
        EventAbout2Save = 5,

        /// The current RoboDK station is about to loose focus because the user requested to open a new station (or just changed the open station). It is recommended to save session/station-specific settings at this moment, if any.
        EventAbout2ChangeStation = 6,

        /// The current RoboDK station (RDK file) is about to be closed. Items in the tree will be deleted and become invalid pointers shortly after this event.
        /// The RDK file may be saved if the user accepted to save changes and the corresponding EventAbout2Save event will be triggered.
        EventAbout2CloseStation = 7,

        /// A new simulation move event completed for one or more robots or mechanisms. This event is usually triggered after one or more EventMoved to signal the completition of moves. This event is usually followed by a Render event after a few ms.
        /// Tip: Use the command TrajectoryTime to retrieve accurate timing according to moving objects (time_sec = RDK->Command("TrajectoryTime").toDouble())
        EventTrajectoryStep = 8,

        /// Special mask to filter for API Events (RoboDK 5.7.3 required).
        /// API Events follow a different enum called \ref IRoboDK::TypeApiEvent.
        /// Enabling command: \ref IRoboDK::Command("PluginApiEvents", "All").
        EventApiMask = 0x1000
    };

    enum TypeApiEvent {
        EVENT_SELECTIONTREE_CHANGED = 1,

        /// Obsolete after RoboDK 4.2.0. Use EVENT_ITEM_MOVED_POSE instead.
        EVENT_ITEM_MOVED = 2,

        EVENT_REFERENCE_PICKED = 3,
        EVENT_REFERENCE_RELEASED = 4,
        EVENT_TOOL_MODIFIED = 5,
        EVENT_CREATED_ISOCUBE = 6,
        EVENT_SELECTION3D_CHANGED = 7,
        EVENT_VIEWPOSE_CHANGED = 8,
        EVENT_ROBOT_MOVED = 9,
        EVENT_KEY = 10,
        EVENT_ITEM_MOVED_POSE = 11,
        EVENT_COLLISIONMAP_RESET = 12,
        EVENT_COLLISIONMAP_TOO_LARGE = 13,
        EVENT_CALIB_MEASUREMENT = 14,

        /// An object in the 3D view was clicked on (right click, left click or double click), this is not triggered when we deselect an item (use Selection3DChanged instead to have more complete information).
        EVENT_SELECTION3D_CLICK = 15,

        /// The state of one or more items changed in the tree (parent/child relationship, added/removed items or instructions, changed the active station).
        /// Use this event to know if the tree changed and had to be re-rendered.
        EVENT_CHANGED = 16,

        /// The name of an item changed (RoboDK 5.6.3 required).
        EVENT_RENAME = 17,

        /// The visibility state of an item changed (RoboDK 5.6.3 required).
        EVENT_SETVISIBLE = 18,

        /// A new robodk station was loaded (RoboDK 5.6.3 required).
        EVENT_STATIONCHANGED = 19,

        /// A program slider was opened, changed, or closed (RoboDK 5.6.4 required).
        EVENT_PROGSLIDER_CHANGED = 20,

        /// The index of a program slider changed (RoboDK 5.6.4 required).
        EVENT_PROGSLIDER_SET = 21
    };


    virtual ~IAppRoboDK() {}

    /// @brief Return the plugin name. Try to be creative and make sure the name is unique.
    virtual QString PluginName()=0;

    /// \brief Load the plugin. This function is called only once when the plugin is loaded (or RoboDK is started with the plugin).
    /// \param mw RoboDK's QMainwindow. Use this object to add menus in the main window.
    /// \param menubar Pointer to RoboDK's main menu bar
    /// \param statusbar Pointer to RoboDK's main status bar
    /// \param statusbar Pointer RoboDK's interface (implementation of the RoboDK API): \ref IRoboDK and \ref IItem
    /// \param settings Additional settings (reserved for future compatibility)
    virtual QString PluginLoad(QMainWindow *mw, QMenuBar *menubar, QStatusBar *statusbar, IRoboDK *rdk, const QString &settings="")
    {
        Q_UNUSED(mw)
        Q_UNUSED(menubar)
        Q_UNUSED(statusbar)
        Q_UNUSED(rdk)
        Q_UNUSED(settings)
        return QString();
    };

    /// \brief This function is called once only when the plugin is being unloaded.
    // It is recommended to remove the toolbar and menus that were added by the plugin. It will help during de debugging process.
    virtual void PluginUnload(){}

    ///
    /// \brief This function is called every time the toolbar is set up. This function is called at least once right after \ref PluginLoad and it can be called when the user changes the view settings (such as changing from cinema to normal mode) or changes the default toolbar layout (in Tools-Toolbar Layout)
    /// \param mw Pointer to RoboDK's main window.
    /// \param iconsize Size of the toolbar icons. The size may differ depending on the screen's DPI. It can also be set in Tools-Options-Display menu.
    virtual void PluginLoadToolbar(QMainWindow *mw, int iconsize)
    {
        Q_UNUSED(mw)
        Q_UNUSED(iconsize)
    }

    ///
    /// \brief This function is called every time a new context menu is created for an item.
    /// \param item The Item (\ref IItem) clicked
    /// \param menu Pointer to the context menu
    /// \param click_type Click type (usually left click)
    /// \return
    virtual bool PluginItemClick(Item item, QMenu *menu, TypeClick click_type)
    {
        Q_UNUSED(item)
        Q_UNUSED(menu)
        Q_UNUSED(click_type)
        return false;
    }

    ///
    /// \brief Specific commands can be passed from the RoboDK API. For example, a parent application can rely on a plugin for certain operations (for example, to create native windows within RoboDK application or take advantage of the RoboDK API speed within the plugin).
    /// Use the RoboDK API (PluginCommand(plugin_name, command, value) to send specific commands to your plugin from an external application.
    /// \param command
    /// \param value
    /// \return
    virtual QString PluginCommand(const QString &command, const QString &value)
    {
        Q_UNUSED(command)
        Q_UNUSED(value)
        return QString();
    };

    ///
    /// \brief This function is called every time there is a new RoboDK event such as rendering the screen, adding/removing items or changing the active station.
    /// If event_type is \ref EventRender you can render your own graphics here using IRoboDK::DrawGeometry.
    // Make sure to make this code as fast as possible to not provoke render lags
    /// \param event_type type of event (EventRender, EventMoved, EventChanged)
    virtual void PluginEvent(TypeEvent event_type)
    {
        Q_UNUSED(event_type)
    };

    /// \brief This function is called every time a new context menu is created for a list of items.
    /// \param item The List of Items (\ref IItem) clicked
    /// \param menu Pointer to the context menu
    /// \param click_type Click type (usually left click)
    /// \return
    virtual bool PluginItemClickMulti(QList<Item> &item_list, QMenu *menu, TypeClick click_type)
    {
        Q_UNUSED(item_list)
        Q_UNUSED(menu)
        Q_UNUSED(click_type)
        return false;
    }

};


QT_BEGIN_NAMESPACE
Q_DECLARE_INTERFACE(IAppRoboDK, "RoboDK.IAppRoboDK")
QT_END_NAMESPACE





#endif // IAPPROBODK_H
