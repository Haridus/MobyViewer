import QtQuick 2.7
import QtQuick.Controls 2.0
import QtQuick.Layouts 1.3
import QtQuick.Dialogs 1.2



Page{
    id: root
    property int totalCount: mobyGamesModel.getTotalCount()

    FileDialog {
        id: fileDialog
        title: "Please choose a file"
        folder: shortcuts.home
        nameFilters: [ "Text (*.txt)" ]
        selectExisting: false
        onAccepted: {
            var filePath = fileDialog.fileUrl
            mobyGamesModel.saveToFile(filePath,outputTemplateFilePath)
        }
        onRejected: {
            console.log("Canceled")
        }
    }

    header:Pane{
        width: parent.width
        height: parent.height*0.1
        background:Rectangle
        {
            width: parent.width
            height: parent.height
            color: "green"
        }
        Row
        {
            id: data_input_bar
            anchors.verticalCenter: parent.verticalCenter
            anchors.left: parent.left
            width: parent.width*0.8
            height: parent.height
            spacing: 5
            CheckBox{
                id: check_all
                anchors.verticalCenter: parent.verticalCenter
                text:""
            }
            Text{
                anchors.verticalCenter: parent.verticalCenter
                font.pointSize: 10
                font.bold: true
                id:title_text_label
                text: "title"
            }
            TextField
            {
                font.pointSize: 10
                anchors.verticalCenter: parent.verticalCenter
                background: Rectangle{
                    anchors.fill: parent
                    color:"white"
                }
                id: title_text
                width: title_text_label.width*2

                text:""

                onTextChanged: {
                    metadata_changed_title.restart()
                }
            }
            Text{
                anchors.verticalCenter: parent.verticalCenter
                font.pointSize: 10
                font.bold: true
                id:year_text_label
                text: "year"
            }
            TextField
            {
                font.pointSize: 10
                anchors.verticalCenter: parent.verticalCenter
                background: Rectangle{
                    anchors.fill: parent
                    color:"white"
                }
                id: year_text
                width: year_text_label.width*2

                text:""

                onTextChanged: {
                    metadata_changed_title.restart()
                }
            }
            Text{
                anchors.verticalCenter: parent.verticalCenter
                font.pointSize: 10
                font.bold: true
                id:genre_text_label
                text: "genre"
            }
            TextField
            {
                font.pointSize: 10
                anchors.verticalCenter: parent.verticalCenter
                background: Rectangle{
                    anchors.fill: parent
                    color:"white"
                }
                id: genre_text
                width: genre_text_label.width*2

                text:""

                onTextChanged: {
                    metadata_changed_title.restart()
                }
            }
            Text{
                anchors.verticalCenter: parent.verticalCenter
                font.pointSize: 10
                font.bold: true
                id: gameplay_text_label
                text: "gameplay"
            }
            TextField
            {
                font.pointSize: 10
                anchors.verticalCenter: parent.verticalCenter
                background: Rectangle{
                    anchors.fill: parent
                    color:"white"
                }
                id: gameplay_text
                width: gameplay_text_label.width*2

                text:""

                onTextChanged: {
                    metadata_changed_title.restart()
                }
            }
            Text{
                anchors.verticalCenter: parent.verticalCenter
                font.pointSize: 10
                font.bold: true
                id: narrative_text_label
                text: "narrative"
            }
            TextField
            {
                font.pointSize: 10
                anchors.verticalCenter: parent.verticalCenter
                background: Rectangle{
                    anchors.fill: parent
                    color:"white"
                }
                id: narrative_text
                width: narrative_text_label.width*2

                text:""

                onTextChanged: {
                    metadata_changed_title.restart()
                }
            }
        }
        Text{
            anchors.verticalCenter: parent.verticalCenter
            anchors.left: data_input_bar.right
            font.pointSize: 12
            font.bold: true
            id: total_count_text_label
            text: totalCount
        }
        Button{
            id:upload_to_file_button
            anchors.left: total_count_text_label.right
            anchors.right: parent.right
            anchors.verticalCenter: parent.verticalCenter
            text: "Upload to file"
            onClicked: {
                fileDialog.open()
            }
        }
    }

    Timer
    {
        id: metadata_changed_title
        interval: 500
        running: false
        onTriggered: {
            var conditionsEntryes = []
            var conditions = ""
            if(title_text.text.length > 0){
                conditionsEntryes.push( "(title LIKE '%"+title_text.text+"%')" )
            }
            if( year_text.text.length > 0 ){
                conditionsEntryes.push( " (year="+year_text.text+")" )
            }
            if( genre_text.text.length > 0 ){
                conditionsEntryes.push( conditions += "(genre LIKE '%"+genre_text.text+"%')" )
            }
            if( gameplay_text.text.length > 0 ){
                conditionsEntryes.push( conditions += "(gameplay LIKE '%"+gameplay_text.text+"%')" )
            }
            if( narrative_text.text.length > 0 ){
                conditionsEntryes.push( conditions += "(narrative LIKE '%"+narrative_text.text+"%')" )
            }
            if( conditionsEntryes.length > 0 ){
                conditions = conditionsEntryes.join(" AND ")
            }
            console.log(conditions)
            mobyGamesModel.setConditions(conditions)
            totalCount = mobyGamesModel.getTotalCount()
            mobyGamesModel.loadEntryes(1,totalCount)
            mobyGamesModel.clearcheck();
        }
    }

    Pane{
        anchors.fill: parent
        ListView{
            id: list
            anchors.fill: parent
            model: mobyGamesModel
            delegate: Item{
                width: list.width
                height: imageSize
                Pane{
                    width: parent.width
                    height: parent.height

                    background: Rectangle{
                        anchors.fill: parent
                    }

                    Pane{
                        anchors.fill: parent
                        CheckBox{
                            anchors.verticalCenter: parent.verticalCenter
                            x:0
                            width: 20
                            checked: check_all.checked
                            onCheckStateChanged: {
                                if( checked ){
                                    mobyGamesModel.check(index)
                                }
                                else{
                                    mobyGamesModel.uncheck(index)
                                }
                            }
                        }
                        Text{
                            anchors.verticalCenter: parent.verticalCenter
                            x:30
                            width: parent.width/6
                            text: title
                            wrapMode: Text.Wrap
                            font.pointSize: 12
                        }
                        Text{
                            anchors.verticalCenter: parent.verticalCenter
                            x: 30+parent.width/6
                            width: parent.width/12
                            text: year
                            wrapMode: Text.Wrap
                            font.pointSize: 12
                        }
                        Text{
                            anchors.verticalCenter: parent.verticalCenter
                            x:30+1*parent.width/6+parent.width/12
                            width: parent.width/6
                            text: genre
                            wrapMode: Text.Wrap
                            font.pointSize: 12
                        }
                        Text{
                            anchors.verticalCenter: parent.verticalCenter
                            x:30+2*parent.width/6+parent.width/12
                            width: parent.width/6
                            text: gameplay
                            wrapMode: Text.Wrap
                            font.pointSize: 12
                        }
                        Text{
                            anchors.verticalCenter: parent.verticalCenter
                            x:30+3*parent.width/6+parent.width/12
                            width: parent.width/6
                            text: narrative
                            wrapMode: Text.Wrap
                            font.pointSize: 12
                        }
                        ImagesView{
                            anchors.verticalCenter: parent.verticalCenter
                            anchors.right: parent.right
                            width: parent.height*4/3
                            height: parent.height
                            sources_string: images
                        }
                    }
                }
            }
        }
    }
}

