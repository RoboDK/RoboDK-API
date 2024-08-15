#-------------------------------------------------
# RoboDK API sample project in C++
# This example uses Qt5 and the robodk_api.cpp file
#-------------------------------------------------

QT       += core gui
QT += network

greaterThan(QT_MAJOR_VERSION, 4): QT += widgets

TARGET = RoboDK-API-Cpp-Sample
TEMPLATE = app

# The following define makes your compiler emit warnings if you use
# any feature of Qt which has been marked as deprecated (the exact warnings
# depend on your compiler). Please consult the documentation of the
# deprecated API in order to know how to port your code away from it.
DEFINES += QT_DEPRECATED_WARNINGS

# You can also make your code fail to compile if you use deprecated APIs.
# In order to do so, uncomment the following line.
# You can also select to disable deprecated APIs only up to a certain version of Qt.
#DEFINES += QT_DISABLE_DEPRECATED_BEFORE=0x060000    # disables all the APIs deprecated before Qt 6.0.0

INCLUDEPATH += ..


SOURCES += \
    ../robodk_api.cpp \
    main.cpp \
    mainwindow.cpp \
    embedexample.cpp

HEADERS += \
    ../robodk_api.h \
    mainwindow.h \
    embedexample.h

FORMS += \
    mainwindow.ui \
    embedexample.ui
