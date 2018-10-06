import QtQuick 2.7
import QtQuick.Controls 2.0

Page{
    id: root
    property int minId: 1
    property int maxId: 20
    property int page_size: 20
    property int totalCount: mobyGamesModel.getTotalCount()
    header:Pane{
        width: parent.width
        height: parent.height*0.1
        background:Rectangle
        {
            width: parent.width
            height: parent.height
            color: "green"
        }

        Text {
            id: pages_index_text
            font.pointSize: 20
            font.bold: true
            anchors.verticalCenter: parent.verticalCenter
            anchors.horizontalCenter: parent.horizontalCenter
            text: minId+" - "+maxId+"["+totalCount+"]"
        }
        Image{
            id: prev_button
            anchors.verticalCenter: parent.verticalCenter
            anchors.right: pages_index_text.left
            width: Math.min(parent.width,parent.height)/3
            height: Math.min(parent.width,parent.height)/3
            fillMode: Image.Stretch
            source: "qrc:/images/chevron-left.svg"

            MouseArea
            {
                anchors.fill: parent
                onClicked: {
                    console.log("prev clicked")
                    var minId_ = minId - page_size
                    var maxId_ = maxId - page_size
                    if( minId_ >= 1 ){
                        minId = minId_
                        maxId = maxId_
                        pages_index_text.text = "%1 - %2[%3]".arg(minId).arg(maxId).arg(totalCount)
                        mobyGamesModel.loadEntryes(minId,maxId)
                    }
                }
            }
        }

        Image{
            id: next_button
            anchors.verticalCenter: parent.verticalCenter
            anchors.left: pages_index_text.right
            width: Math.min(parent.width,parent.height)/3
            height: Math.min(parent.width,parent.height)/3
            fillMode: Image.Stretch
            source: "qrc:/images/chevron-right.svg"

            MouseArea
            {
                anchors.fill: parent
                onClicked: {
                    console.log("next clicked")
                    var minId_ = minId + page_size
                    var maxId_ = maxId + page_size
                    console.log(minId_,maxId_,totalCount)
                    if( maxId_ < totalCount+page_size ){
                        console.log("entered")
                        minId = minId_
                        maxId = maxId_
                        pages_index_text.text = "%1 - %2[%3]".arg(minId).arg(maxId).arg(totalCount)
                        mobyGamesModel.loadEntryes(minId,maxId)
                    }
                }
            }
        }

        Row
        {
            anchors.verticalCenter: parent.verticalCenter
            anchors.left: parent.left
            anchors.right: prev_button
            Text{
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
            if( conditionsEntryes.length > 0 ){
                conditions = conditionsEntryes.join(" AND ")
            }
            console.log(conditions)
            mobyGamesModel.setConditions(conditions)
            totalCount = mobyGamesModel.getTotalCount()
            minId = 1
            maxId = minId+page_size-1
            mobyGamesModel.loadEntryes(minId,maxId)
        }
    }

    Pane{
        anchors.fill: parent
        GridView{
            id: grid
            anchors.fill: parent
            cellWidth: parent.width*0.2
            cellHeight: parent.height*0.2
            model: mobyGamesModel
            delegate: ImagesView{
                width: grid.cellWidth
                height: grid.cellHeight
                title_string: title
                year_value: year
                genre_string: genre
                sources_string: images
            }
        }
    }



}
