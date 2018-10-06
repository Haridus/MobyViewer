#include <QGuiApplication>
#include <QQmlApplicationEngine>
#include <QQmlContext>
#include <QSettings.h>

#include <QDebug>

#include "mobygamesitemsmodel.h"

int main(int argc, char *argv[])
{
    QCoreApplication::setAttribute(Qt::AA_EnableHighDpiScaling);
    QGuiApplication app(argc, argv);

    QSettings settings("settings.ini",QSettings::IniFormat);
    QString db = settings.value("db","./thumb_full.db").toString();
    QString outputTemplateFilePath = settings.value("output_template","").toString();
    int imageSize = settings.value("image_size",150).toInt();

    qDebug()<<settings.allKeys();

    MobyGamesItemsModel model;
    model.setSource(db);
    model.loadEntryes(1,model.getTotalCount());

    QQmlApplicationEngine engine;
    engine.load(QUrl(QLatin1String("qrc:/main.qml")));
    QQmlContext *ctxt = engine.rootContext();
    ctxt->setContextProperty("outputTemplateFilePath", outputTemplateFilePath);
    ctxt->setContextProperty("imageSize", imageSize);
    ctxt->setContextProperty("mobyGamesModel", &model);

    return app.exec();
}
