QT += qml quick network quickcontrols2 widgets gui core svg sql

CONFIG += c++11

SOURCES += main.cpp \
    mobygamesitemsmodel.cpp

RESOURCES += qml.qrc \
    images.qrc

# Additional import path used to resolve QML modules in Qt Creator's code model
QML_IMPORT_PATH =

# Default rules for deployment.
include(deployment.pri)

HEADERS += \
    mobygamesitemsmodel.h

DEPENDPATH += .

LIBS += -L"c:\\Qt\\Qt5.7.0\\Tools\\QtCreator\\bin\\" -llibeay32 -lssleay32
