/*
This is a UI file (.ui.qml) that is intended to be edited in Qt Design Studio only.
It is supposed to be strictly declarative and only uses a subset of QML. If you edit
this file manually, you might introduce QML code that is not supported by Qt Design Studio.
Check out https://doc.qt.io/qtcreator/creator-quick-ui-forms.html for details on .ui.qml files.
*/
import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Dialogs
import QtQuick.Layouts
import Qt5Compat.GraphicalEffects

ApplicationWindow {
    visible: true
    width: 1920
    height: 1080
    Material.theme: Material.Dark
    Material.accent: Material.DeepOrange
    color: Material.backgroundColor
    title: "LiveLens Demo"

    Image {
        id: backDrop
        anchors.fill: parent
        source: "BackDrop.png"
        fillMode: Image.PreserveAspectCrop
        z: -1
    }
    Rectangle {
        id: inputImgPlaceholder
        width: parent.width * 0.3
        height: parent.height * 0.5
        x: parent.width * 0.07
        y: parent.height * 0.1
        border.color: Material.primary
        border.width: 8
        radius: 12
        color: "#292929"

        DropShadow {
            anchors.fill: inputImgPlaceholder
            source: inputImgPlaceholder
            horizontalOffset: 8
            verticalOffset: 8
            radius: 20.0
            samples: 17
            color: "#80000000"
        }

        Image {
            id: inputImg
            anchors.fill: parent
            source: "" // Source will be set dynamically when user selects an image
            fillMode: Image.PreserveAspectFit // Preserve Aspect Ratio
            visible: inputImage.source !== "" // Hide the image if no source is set
        }

        Text {
            text: qsTr("Input Image")
            textFormat: Text.MarkdownText
            font.styleName: "Regular"
            font.family: "Verdana"
            font.pointSize: 24
            anchors.centerIn: parent
            color: "white"
            visible: inputImage.source === "" // Hide the text if an image is set
        }
    }
    Button {
        id: selectImageButton
        text: "Select Image"
        anchors.right: inputImgPlaceholder.right
        anchors.top: inputImgPlaceholder.bottom
        anchors.topMargin: 20
        width: parent.width * 0.3
        height: parent.height * 0.1
        Material.background: Material.primary
        // Make text bigger
        font.pointSize: 24
        
        onClicked: {
            // inputImage.source = ""
            // inputImage.source = fileDialog.open()
        }

    }
    Rectangle {
        id: outputImgPlaceholder
        width: parent.width * 0.3
        height: parent.height * 0.5
        x: parent.width * 0.56
        y: parent.height * 0.1
        border.color: Material.primary
        border.width: 8
        radius: 12
        color: "#292929"

        DropShadow {
            anchors.fill: outputImgPlaceholder
            source: outputImgPlaceholder
            horizontalOffset: 8
            verticalOffset: 8
            radius: 20.0
            samples: 17
            color: "#80000000"
        }
        
        Image {
            id: outputImg
            anchors.fill: parent
            source: "" // Source will be set dynamically backend return
            fillMode: Image.PreserveAspectFit // Preserve Aspect Ratio
            visible: outputImage.source !== "" // Hide the image if no source is set
        }

        Text {
            font.pointSize: 24
            anchors.centerIn: parent
            color: "white"
            text: "Output Image"
            textFormat: Text.MarkdownText
            font.family: "Verdana"
        }
    }
    Button {
        id: nextButton
        text: "Next"
        anchors.right: outputImgPlaceholder.right
        anchors.top: outputImgPlaceholder.bottom
        anchors.topMargin: 20
        width: parent.width * 0.3
        height: parent.height * 0.1
        Material.background: Material.primary
        // Make text bigger
        font.pointSize: 24
        
        onClicked: {
            
        }
}

}
