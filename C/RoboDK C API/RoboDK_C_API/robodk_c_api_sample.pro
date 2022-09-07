QT -= gui

CONFIG += c++17 console
CONFIG -= app_bundle

# INCLUDEPATH += $${PWD}/include

SOURCES += \
	robodk_api_c.c \
        ConsoleApplication1.cpp

HEADERS += \
    robodk_api_c.h \
    
