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
    imageLoaded = Signal(str)
    def __init__(self):
        super(Backend, self).__init__()
        self.current_step: int = 0
        self.actual_weight = ""
        self.segmented: Dict[str, str] = {}
        self.predicted_weight: int = 0
        self.SegmentationModel = SegmentationModel("yolov8m-seg.pt")
        self.input_image = None
        self.processed_image = None # For intermediate steps

        
    @Slot(str)
    def load_image(self, input_image_path: str):
        if input_image_path.startswith("file:///"):
            input_image_path = input_image_path[8:]
        self.input_image_path = Path(input_image_path)
        # Ensure path debugging
        print(f"Attempting to load image from path: {self.input_image_path}")
        try:
            self.input_image = cv2.imread(str(self.input_image_path))
            if self.input_image is None:
                print(f"Failed to load image at {self.input_image_path}")
            else:
                # Emit the signal with a correct path or indication of success
                print(f"Attempting to emit signal with path: {self.input_image_path}")
                self.imageLoaded.emit(str(self.input_image_path))
                print(f"Image loaded and sent successfully from {self.input_image_path}")
        except Exception as e:
            print(f"Error loading image: {e}")
        


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
        sys.stdout.write("Failed to load QML file")
        sys.exit(-1)

    sys.exit(app.exec())
