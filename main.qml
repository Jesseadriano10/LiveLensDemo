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
        width: parent.width * 0.365
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
            anchors.margins: 8

            source: "" // Source will be set dynamically when user selects an image
            fillMode: Image.PreserveAspectFit // Preserve Aspect Ratio
            visible: inputImg.source != ""

            onStatusChanged: {
                if (inputImg.status === Image.Ready) {
                    // Automatically scale placeholder to fit the image
                    var imgRatio = inputImg.width / inputImg.height;
                    var placeholderMaxWidth = inputImgPlaceholder.width;
                    var placeholderMaxHeight = inputImgPlaceholder.height;

                    // Scale the image to fit the placeholder
                    if (imgRatio > 1) {
                        inputImg.width = placeholderMaxWidth;
                        inputImg.height = placeholderMaxWidth / imgRatio;
                    } else {
                        inputImg.height = placeholderMaxHeight;
                        inputImg.width = placeholderMaxHeight * imgRatio;
                    }
                }
            }

        }

        Text {
            text: qsTr("Input Image")
            textFormat: Text.MarkdownText
            font.styleName: "Regular"
            font.family: "Verdana"
            font.pointSize: 24
            anchors.centerIn: parent
            color: "white"
            visible: inputImg.source == "" // Hide the text if an image is set
        }
    }
    Button {
        id: selectImageButton
        text: "Select Image"
        anchors.horizontalCenter: inputImgPlaceholder.horizontalCenter
        anchors.top: inputImgPlaceholder.bottom
        anchors.topMargin: 20
        width: parent.width * 0.3
        height: parent.height * 0.1
        Material.background: Material.primary
        // Make text bigger
        font.pointSize: 24

        onClicked: {
            fileDialog.open()
        }
    }
    FileDialog {
        id: fileDialog
        title: "Select an image"
        currentFolder: StandardPaths.standardLocations(StandardPaths.PicturesLocation)[0]
        nameFilters: ["Image files (*.jpg *.png)"]
        onAccepted: {
            // Call the backend to process the image
            var localPath = selectedFile.toString().replace("file:///", "")
            // Should receive a signal from the backend to update the input image
            console.log("Calling backend to process image")
            backend.load_image(localPath) // Move to next state
            backend.next_step() // move from INITIAL to IMAGE_LOADED
            // Disable the button to prevent multiple calls
            selectImageButton.enabled = false
        }
    }



    Rectangle {
        id: outputImgPlaceholder
        width: parent.width * 0.363
        height: parent.height * 0.495
        x: parent.width * 0.50
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
            // Use 'imageprovider' as source and append the imageId received
            // from the signal
            anchors.margins: 8
            fillMode: Image.PreserveAspectFit // Preserve Aspect Ratio
            visible: outputImg.source !== "" // Hide the image if no source is set
            onStatusChanged: {
                if (outputImg.status === Image.Ready) {
                    // Automatically scale placeholder to fit the image
                    var imgRatio = outputImg.width / outputImg.height;
                    var placeholderMaxWidth = outputImgPlaceholder.width;
                    var placeholderMaxHeight = outputImgPlaceholder.height;

                    // Scale the image to fit the placeholder
                    if (imgRatio > 1) {
                        outputImg.width = placeholderMaxWidth;
                        outputImg.height = placeholderMaxWidth / imgRatio;
                    } else {
                        outputImg.height = placeholderMaxHeight;
                        outputImg.width = placeholderMaxHeight * imgRatio;
                    }
                }
            }
        }

        Text {
            font.pointSize: 24
            anchors.centerIn: parent
            color: "white"
            text: "Output Image"
            textFormat: Text.MarkdownText
            font.family: "Verdana"
            font.styleName: "Regular"
            visible: outputImg.source == "" // Hide the text if an image is set
        }
    }
    
    Button {
        id: nextButton
        text: "Next"
        anchors.horizontalCenter: outputImgPlaceholder.horizontalCenter
        anchors.top: outputImgPlaceholder.bottom
        anchors.topMargin: 20
        width: parent.width * 0.3
        height: parent.height * 0.1
        Material.background: Material.primary
        // Make text bigger
        font.pointSize: 24

        onClicked: {
            // Disable the button with timer to prevent fast clicks
            nextButton.enabled = false
            buttonTimer.start()
            // Call the backend to update the state to show a
            // different part of the demo
            backend.next_step()
        }
    }
    
    // Weight prediction text to only be displayed after weight prediction
    Text {
        id: weightPrediction
        font.pointSize: 24
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: nextButton.bottom
        anchors.topMargin: 20
        color: "white"
        visible: false
        // Idle animation for text
        NumberAnimation on opacity {
            running: true
            loops: Animation.Infinite
            from: 0.0
            to: 1.0
            duration: 2000
        }
    }
    // State text to only be displayed after state change
    Text {
        id: stateText
        font.pointSize: 24
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: parent.top
        anchors.topMargin: 20
        color: "white"
        visible: false
        // Idle animation for text
        NumberAnimation on opacity {
            running: true
            loops: Animation.Infinite
            from: 0.0
            to: 1.0
            duration: 2000 // Increase the duration to make the fade slower
        }
    }

    Connections {
        target: backend
        function onImageLoaded(imagePath) {
            console.log("Image loaded from backend: " + imagePath);
            inputImg.source = imagePath.startsWith("file:///") ? imagePath : "file:///" + imagePath;
        }
        // This function is called when the backend has processed the image
        // and stored it in a map within backend
        function onImageProcessed(imageId) {
            if (imageId !== "dummy") {
                console.log("Image processed from backend: " + imageId);
                outputImg.source = "image://imageprovider/" + imageId;
            }
        }
        // Function to display text on weight prediction
        function onWeightPredicted(weight) {
            console.log("Weight predicted from backend: " + weight);
            weightPrediction.text = "Predicted Weight: " + weight + " lbs";
            weightPrediction.visible = true;
        }
        // On state change, show the current state At the top center
        // Above the rectangle
        function onStateChanged(state) {
            console.log("State changed from backend: " + state.toString());
            stateText.text = "State: " + state.toString();
            stateText.visible = true;

            if (state == "DONE") {
                buttonTimer.stop();
                nextButton.enabled = false;

            }
        }
        // Override weight prediction text with difference in weight text
        function onWeightComparison(weightDifference) {
            console.log("Weight difference from backend: " + weightDifference);
            weightPrediction.text = "Weight Difference: " + weightDifference + " lbs";
            weightPrediction.visible = true;
        }

    }
    Timer {
        id: buttonTimer
        interval: 1000
        repeat: false
        onTriggered: {
            nextButton.enabled = true
        }
    }
}
