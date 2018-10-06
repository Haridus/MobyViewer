import QtQuick 2.0
import QtQuick.Controls 2.0

Item {
    property string sources_string: ""
    property var sources: []
    property string title_string: ""
    property string year_value: ""
    property string genre_string: ""
    property int current_index: 1

    onSources_stringChanged: {
        //TODO: fill correct sources
        //sources_string = sources_string.replace("/s/","/l/")
        sources = sources_string.split(",")
      //  console.log("sources string changed")
     //   console.log(title)
      //  console.log(year)
      //  console.log(genre)
 //       console.log(sources_string)
 //       console.log(sources)

        set_source(1)
    }

    function setSources(sources_)
    {
        sources = sources_
    }

    function set_source(index)
    {
        if(index < sources.length ){
           preview.source = sources[index]
        }
    }

    function next_source()
    {
        current_index = current_index+1
        if( current_index >= sources.length ){
            current_index = 1;
        }
        set_source(current_index)
    }

    function prev_source()
    {
        current_index = current_index-1
        if( current_index < 1 ){
            current_index = sources.length-1;
        }
        set_source(current_index)
    }

    Column{
        width: parent.width
        height: parent.height

        Image {
            width: height*4/3
            height: parent.height//parent.height*0.8
            anchors.horizontalCenter: parent.horizontalCenter

            id: preview
            source: "qrc:/images/cancel.svg"

            MouseArea
            {
                anchors.fill: parent
                onClicked: {
                    console.log("image clicked")
                    //TODO on clicked() action
                }
            }

            Image{
                anchors.verticalCenter: parent.verticalCenter
                width: Math.min(parent.width,parent.height)/5
                height: Math.min(parent.width,parent.height)/5
                x: -width
                fillMode: Image.Stretch
                source: "qrc:/images/chevron-left.svg"

                MouseArea
                {
                    anchors.fill: parent
                    onClicked: {
                        console.log("prev image")
                        prev_source()
                    }
                }
            }

            Image{
                anchors.verticalCenter: parent.verticalCenter
                width: Math.min(parent.width,parent.height)/5
                height: Math.min(parent.width,parent.height)/5
                x: parent.width
                fillMode: Image.Stretch
                source: "qrc:/images/chevron-right.svg"

                MouseArea
                {
                    anchors.fill: parent
                    onClicked: {
                        console.log("next image")
                        next_source()
                    }
                }
            }
        }
//        Label
//        {
//            anchors.horizontalCenter: parent.horizontalCenter
//            text: title_text
//        }
//        Label
//        {
//            anchors.horizontalCenter: parent.horizontalCenter
//            text: year_value+" "+genre_text
//        }
    }


}
