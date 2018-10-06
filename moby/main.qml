import QtQuick 2.7
import QtQuick.Controls 2.0
import QtQuick.Layouts 1.0

ApplicationWindow {
    id: main
    visible: true
    width: 1000
    height: 1000
    title: qsTr("MobyView")


    ViewListPane{
        anchors.fill: parent
    }
}
