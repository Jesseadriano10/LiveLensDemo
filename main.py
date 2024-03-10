# This Python file uses the following encoding: utf-8
from enum import Enum, auto
import sys
from pathlib import Path

# Import the required libraries for QT and PySide6
from PySide6.QtGui import QGuiApplication, QImage, QPixmap
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QObject, Slot, Signal, Qt
from PySide6.QtQuick import QQuickImageProvider

from typing import List, Dict
# Model imports
import os
import numpy as np
from ultralytics import YOLO
import cv2 as cv



import matplotlib.pyplot as plt
from SegmentationModel import SegmentationModel
from DistortionCorrection import DistortionCorrection
from PySide6.QtCore import Qt

class State(Enum):
    INITIAL = auto()
    IMAGE_LOADED = auto()
    DISTORTION_CORRECTION_ONE = auto() # Tentatively
    DISTORTION_CORRECTION_TWO = auto()
    SEGMENTATION_PERFORMED = auto()
    BOUNDING_BOX_SHOWN = auto()
    FILTERED_IMAGE_SHOWN = auto()
    PREDICTION_MADE = auto()
    COMPARISON_DISPLAYED = auto()

class ImageProvider(QQuickImageProvider):
    def __init__(self):
       super().__init__(QQuickImageProvider.Image)
       self.myImageMap = {} # Store the images here
       
    def requestImage(self, id, size, requestedSize):
        if id in self.myImageMap:
            image = self.myImageMap[id]
            if requestedSize.isValid():
                image = image.scaled(requestedSize.width(), requestedSize.height(), Qt.KeepAspectRatio)
            size.setWidth(image.width())
            size.setHeight(image.height())
            return image
        else:
            print(f"Image with id {id} not found")
            return QImage()
        
    def addImage(self, id, image):
        # Add images to provider
        self.myImageMap[id] = image
            
                


class Backend(QObject):
    # Signal for image loaded
    imageLoaded = Signal(str)
    # Signal for image processed
    imageProcessed = Signal(QImage)
    
    def __init__(self):
        super(Backend, self).__init__()
        self.state = State.INITIAL
        self.actual_weight = ""
        self.predicted_weight: int = 0 # in kg
        self.SegmentationModel = SegmentationModel("yolov8m-seg.pt")
        self.DistortionCorrection = DistortionCorrection((9, 6), (4032, 2268))
        self.input_image = None # For the original image
        self.processed_image = None # For intermediate steps

    # This signal sends the QImages to QML
    @Slot()
    def next_step(self):
        if self.state == State.INITIAL:
            # QML logic will call load_image so we don't need to do anything here
            self.state = State.IMAGE_LOADED
        elif self.state == State.IMAGE_LOADED:
            # Apply distortion correction
            isPrepared = self.prepare_calibration()
            if isPrepared:
                self.processed_image = self.DistortionCorrection.distortion_correction(self.input_image)
                self.processed_image = cv.cvtColor(self.processed_image, cv.COLOR_BGR2RGB)
            else:
                print("Failed to prepare calibration")
            # Use QPixMap to display our numpy array
            height, width, channel = self.processed_image.shape
            bytesPerLine = 3 * width
            qImg = QImage(self.processed_image.data, width, height, bytesPerLine, QImage.Format_RGB888)
            # Emit the signal with the processed image
            self.imageProcessed.emit(qImg)
            self.state = State.DISTORTION_CORRECTION_ONE
        elif self.state == State.DISTORTION_CORRECTION_ONE:
            # Move to Distortion Correction Two
            self.state = State.DISTORTION_CORRECTION_TWO
        elif self.state == State.DISTORTION_CORRECTION_TWO:
            self.state = State.SEGMENTATION_PERFORMED
        elif self.state == State.SEGMENTATION_PERFORMED:
            self.state = State.BOUNDING_BOX_SHOWN
        elif self.state == State.BOUNDING_BOX_SHOWN:
            self.state = State.FILTERED_IMAGE_SHOWN
        elif self.state == State.FILTERED_IMAGE_SHOWN:
            self.state = State.PREDICTION_MADE
        elif self.state == State.PREDICTION_MADE:
            self.state = State.COMPARISON_DISPLAYED
        elif self.state == State.COMPARISON_DISPLAYED:
            self.state = State.INITIAL
        else:
            self.state = State.INITIAL
    
    def prepare_calibration(self) -> bool:
        try:
            # load mtx, dist from csv
            DistortionCorrection.mtx = np.loadtxt('mtx.csv', delimiter=',', dtype=np.float64)
            DistortionCorrection.dist = np.loadtxt('dist.csv', delimiter=',', dtype=np.float64)
            return True
            # Return boolean to indicate success
        except Exception as e:
            return False
            # Handle the error appropriately
        
                
        
    @Slot(str)
    def load_image(self, input_image_path: str):
        if input_image_path.startswith("file:///"):
            input_image_path = input_image_path[8:]
        self.input_image_path = Path(input_image_path)
        # Ensure path debugging
        print(f"Attempting to load image from path: {self.input_image_path}")
        try:
            self.input_image = cv.imread(str(self.input_image_path))
            if self.input_image is None:
                print(f"Failed to load image at {self.input_image_path}")
            else:
                # Emit the signal with a correct path or indication of success
                print(f"Attempting to emit signal with path: {self.input_image_path}")
                self.imageLoaded.emit(str(self.input_image_path))
                print(f"Image loaded and sent successfully from {self.input_image_path}")
        except Exception as e:
            print(f"Error loading image: {e}")
    
    def convertKgToLbs(self, weight: float) -> float:
        return weight * 2.20462
        


if __name__ == "__main__":
    app = QGuiApplication(sys.argv)

    # Create QML engine
    engine = QQmlApplicationEngine()

    # Create backend object and expose it to QML
    backend = Backend()
    engine.rootContext().setContextProperty("backend", backend)
    
    # Create an instance of the image provider
    # image_provider = ImageProvider()
    # engine.addImageProvider("image_provider", image_provider)
    
    
    # Load the main QML file
    qml_file = Path(__file__).resolve().parent / "main.qml"
    engine.load(qml_file)
    if not engine.rootObjects():
        sys.stdout.write("Failed to load QML file")
        sys.exit(-1)

    sys.exit(app.exec())
