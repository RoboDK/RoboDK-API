TARGET = PluginApiExample

QT += core gui widgets network

TEMPLATE = lib
CONFIG += plugin
CONFIG += c++17

CONFIG(release, debug|release) {
    message("Using release binaries.")
    message("Select Projects-Run-Executable and set to C:/RoboDK/bin/RoboDK.exe")
    win32 {
        #Default path on Windows
        DESTDIR  = C:/RoboDK/bin6/plugins
    } else {
        macx {
            # Default path on MacOS
            DESTDIR  = ~/RoboDK/RoboDK.app/Contents/MacOS/plugins
        } else {
            #Default path on Linux
            DESTDIR  = ~/RoboDK/bin/plugins
        }
    }
} else {
    message("Using debug binaries: Make sure you start the debug version of RoboDK ( C:/RoboDK/bind/ ). ")
    message("Select Projects-Run-Executable and set to C:/RoboDK/bind/RoboDK.exe ")
    message("(send us an email at info@robodk.com to obtain debug binaries that should go to the bind directory)")
    win32 {
        #Default path on Windows (debug)
        DESTDIR  = C:/RoboDK/bind/plugins
    } else {
        macx {
            # Default path on MacOS (debug)
            DESTDIR  = ~/RoboDK-Dev/Deploy/RoboDK.app/Contents/MacOS/plugins
        } else {
            #Default path on Linux (debug)
            DESTDIR  = ~/RoboDK/bind/plugins
        }
    }
}


# Main Files
HEADERS += \
    ../robodk_api.h \
    pluginapiexample.h \
    iapprobodk.h \
    iitem.h \
    irobodk.h \
    robodkinternalsocket.h \
    robodktypes.h

SOURCES += \
    ../robodk_api.cpp \
    pluginapiexample.cpp \
    robodkinternalsocket.cpp \
    robodktypes.cpp

# RoboDK API
INCLUDEPATH += $${PWD}/..
