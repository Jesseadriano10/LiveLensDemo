# This Python file uses the following encoding: utf-8
import sys
from pathlib import Path

# Import the required libraries for QT and PySide6
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QObject, Slot, Signal
from typing import List, Dict
# Model imports
import os
import numpy as np
from ultralytics import YOLO
import cv2

import matplotlib.pyplot as plt
from SegmentationModel import SegmentationModel


class Backend(QObject):
    def __init__(self):
        super(Backend, self).__init__()
        self.current_step: int = 0
        self.actual_weight = ""
        self.segmented: Dict[str, str] = {}
        self.predicted_weight: int = 0
        # self.SegmentationModel = SegmentationModel("yolov8m-seg.pt")
        self.input_image = None
        self.processed_image = None # For intermediate steps
        self.imageLoaded = Signal(str) # Signal to notify the QML when the image is loaded


    @Slot(int)
    def next_step(self):
        # Manage the state and call the appropriate function
        if self.current_step == 0:
            self.load_image()
        elif self.current_step == 1:
            self.fix_distortion()
        elif self.current_step == 2:
            self.segment()
        elif self.current_step == 3:
            self.showBinaryMask()
        elif self.current_step == 4:
            self.showFiltered()
        elif self.current_step == 5:
            self.showBounding()
        elif self.current_step == 6:
            self.predict()
        elif self.current_step == 7:
            self.display_results()
        self.current_step += 1

    def load_image(self, image_path: str):
        self.image_path = image_path
        # Load the image as numpy array array
        self.input_image = cv2.imread(image_path)
        # Emit the signal to notify the QML that the image is loaded
        self.imageLoaded.emit(image_path)
        
    def fix_distortion(self):
        pass
    def segment(self):
        pass
    def showBinaryMask(self):
        pass
    def showFiltered(self):
        pass
    def showBounding(self):
        pass
    def predict(self):
        pass
    def display_results(self):
        pass
    

if __name__ == "__main__":
    app = QGuiApplication(sys.argv)

    # Create QML engine
    engine = QQmlApplicationEngine()

    # Create backend object and expose it to QML
    backend = Backend()
    engine.rootContext().setContextProperty("backend", backend)


    # Load the main QML file
    qml_file = Path(__file__).resolve().parent / "main.qml"
    engine.load(qml_file)
    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec())
