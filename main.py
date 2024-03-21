# This Python file uses the following encoding: utf-8
from enum import Enum, auto
import sys
from pathlib import Path

# Import the required libraries for QT and PySide6
from PySide6.QtGui import QGuiApplication, QImage
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QObject, Slot, Signal, Qt
from PySide6.QtQuick import QQuickImageProvider


from typing import List, Dict
# Model imports
import os
import numpy as np
from ultralytics import YOLO
import cv2 as cv
# Matplotlib for displaying images. switch to Agg backend
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt




import matplotlib.pyplot as plt
from SegmentationModel import SegmentationModel
from DistortionCorrection import DistortionCorrection
from CowWeightPredictor import CowWeightPredictor
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
    DONE = auto()

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
    # Processed image signal is ready
    imageProcessed = Signal(str)
    # Signal for weight prediction
    weightPredicted = Signal(float)
    # Signal for enum state
    stateChanged = Signal(str)
    # Signal for weight comparison
    weightComparison = Signal(float)
    

    def __init__(self):
        super(Backend, self).__init__()
        self.state = State.INITIAL
        self.SegmentationModel = SegmentationModel("yolov8m-seg.pt")
        self.DistortionCorrection = DistortionCorrection((9, 6), (4032, 2268))
        self.CowWeightPredictor = CowWeightPredictor("weights.03.hdf5")
        self.input_image = None # For the original image
        self.processed_image = None # For intermediate steps
        self.cropped_image = None # For the distortion part 2
        self.results = None # For the segmentation results
        self.weight_predicted = None # For the predicted weight, in lbs?
        self.actual_weight = None # I know the weight is in kg and in the file name
        
    


    # This signal sends the QImage ids to the QML
    @Slot()
    def next_step(self):
        if self.state == State.INITIAL:            
            self.state = State.IMAGE_LOADED
        elif self.state == State.IMAGE_LOADED:
            print('State.IMAGE_LOADED')
            # Apply distortion correction
            isPrepared = self.prepare_calibration()
            if isPrepared:
                # Apply distortion correction to the image
                self.processed_image, self.cropped_image = self.DistortionCorrection.distortion_correction(self.input_image)
                self.processed_image = cv.cvtColor(self.processed_image, cv.COLOR_BGR2RGB)
                self.cropped_image = cv.cvtColor(self.cropped_image, cv.COLOR_BGR2RGB)
                print("Distortion correction applied")
            else:
                print("Failed to prepare calibration")
            self.state = State.DISTORTION_CORRECTION_ONE
        elif self.state == State.DISTORTION_CORRECTION_ONE:
            # Make RGB
            self.processed_image = cv.cvtColor(self.processed_image, cv.COLOR_BGR2RGB)
            # Display processed image
            qImg = self.convert_npy2qimg(self.processed_image)
            # Add the image to the provider
            image_provider.addImage("corrected_img", qImg)
            # print image metadata from the map
            print(f"Image metadata: {image_provider.myImageMap['corrected_img'].size()}")
            # Emit the signal to indicate that the processed image is ready
            self.imageProcessed.emit("corrected_img")
            # Move to Distortion Correction Two
            self.state = State.DISTORTION_CORRECTION_TWO
        elif self.state == State.DISTORTION_CORRECTION_TWO:
            self.cropped_image = cv.cvtColor(self.cropped_image, cv.COLOR_BGR2RGB)
            # Same as above but show cropped image
            qImg = self.convert_npy2qimg(self.cropped_image)
            # Add the image to the provider
            image_provider.addImage("cropped_img", qImg)
            # print image metadata from the map
            print(f"Image metadata: {image_provider.myImageMap['cropped_img'].size()}")
            # Emit the signal to indicate that the processed image is ready
            self.imageProcessed.emit("cropped_img")
            self.state = State.SEGMENTATION_PERFORMED
        elif self.state == State.SEGMENTATION_PERFORMED:
            # Preprocess the image
            print("Preprocessing image...")
            self.processed_image = self.SegmentationModel.preprocess_image(self.processed_image)
            print("Preprocessing completed.")
            # Now start Segmentation segment
            print("Starting segmentation...")
            self.results = self.SegmentationModel.segment(self.processed_image)
            # Make a dir within runs/segment called binary_mask
            os.makedirs('runs/segment/binary_mask', exist_ok=True)
            # Make a dir within runs/segment called bounding_box
            os.makedirs('runs/segment/bounding_box', exist_ok=True)
            # Make a dir within runs/segment called filtered_image
            os.makedirs('runs/segment/filtered_image', exist_ok=True)
            # Display results
            print("Segmentation completed.")
            # Get the binary mask
            binary_mask = self.SegmentationModel.get_binary_mask(self.results)
            # Plot the binary mask
            plt.imshow(binary_mask)
            plt.axis('off')
            plt.savefig('runs/segment/binary_mask/binary_mask.png')
            # Save the binary mask to the image provider
            qImg = QImage('runs/segment/binary_mask/binary_mask.png')
            image_provider.addImage("binary_mask", qImg) 
            # Emit the signal to indicate that the processed image is ready
            self.imageProcessed.emit("binary_mask")
            self.state = State.BOUNDING_BOX_SHOWN
        elif self.state == State.BOUNDING_BOX_SHOWN:
            # Get the bounding box
            bounding_box_image = self.SegmentationModel.get_bounding(self.processed_image, self.results)
            # Convert color space from BGR to RGB
            bounding_box_image_rgb = cv.cvtColor(bounding_box_image, cv.COLOR_BGR2RGB)
            # Plot the bounding box
            plt.imshow(bounding_box_image_rgb.astype('uint8'))
            plt.axis('off')
            plt.savefig('runs/segment/bounding_box/bounding_box.png')
            # Save the bounding box to the image provider
            qImg = QImage('runs/segment/bounding_box/bounding_box.png')
            image_provider.addImage("bounding_box", qImg)
            # Emit the signal to indicate that the processed image is ready
            self.imageProcessed.emit("bounding_box")
            self.state = State.FILTERED_IMAGE_SHOWN
        elif self.state == State.FILTERED_IMAGE_SHOWN:
            # Get the filtered image
            filtered_image = self.SegmentationModel.get_filtered(self.processed_image, self.results)
            filtered_image_rgb = cv.cvtColor(filtered_image, cv.COLOR_BGR2RGB)
            # Plot the filtered image
            plt.imshow(filtered_image_rgb.astype('uint8'))
            plt.axis('off')
            plt.savefig('runs/segment/filtered_image/filtered_image.png')
            # Save the filtered image to the image provider
            qImg = QImage('runs/segment/filtered_image/filtered_image.png')
            image_provider.addImage("filtered_image", qImg)
            # Emit the signal to indicate that the processed image is ready
            self.imageProcessed.emit("filtered_image")
            self.state = State.PREDICTION_MADE
        elif self.state == State.PREDICTION_MADE:
            print("Making a prediction...")
            print("Actual weight: ", self.actual_weight, "kg") # This is the actual weight
            # Convert actual weight to lbs
            self.actual_weight = self.convertKgToLbs(self.actual_weight)
            print("Actual weight: ", self.actual_weight, "lbs") # This is the actual weight
            # Make a prediction
            self.weight_predicted = self.CowWeightPredictor.make_prediction(self.processed_image)
            # Convert to float instead of numpy array
            self.weight_predicted = self.weight_predicted[0][0]
            # Convert the weight to lbs
            self.weight_predicted = self.convertKgToLbs(self.weight_predicted)
            print("Predicted weight: ", self.weight_predicted, "lbs") # This is the predicted weight
            # Round to 2 decimal places
            self.weight_predicted = round(self.weight_predicted, 2)
            # Emit the signal to indicate that the processed weight is ready
            self.weightPredicted.emit(self.weight_predicted)
            self.state = State.COMPARISON_DISPLAYED
        elif self.state == State.COMPARISON_DISPLAYED:
            # Calculate the difference
            diff = abs(self.actual_weight - self.weight_predicted)
            # 2 decimal places
            diff = round(diff, 2)
            print("Difference: ", diff, "lbs") # This is the difference
            # Display the difference
            self.weightComparison.emit(diff)
            # Disable nextButton in qml
            
            # Reset the state
            self.state = State.DONE
        elif self.state == State.DONE:
            # Reset the state
            self.state = State.INITIAL
        else:
            self.state = State.INITIAL
        # Emit the signal with the new state name
        self.stateChanged.emit(self.state.name)
        
    @Slot()
    def restart_backend(self):
        self.input_image = None
        self.processed_image = None
        self.cropped_image = None
        self.results = None
        self.weight_predicted = None
        self.actual_weight = None
        self.state = State.INITIAL
        self.stateChanged.emit(self.state.name)
    
    

        

    def prepare_calibration(self) -> bool:
        try:
            # load mtx, dist from csv
            self.DistortionCorrection.mtx = np.loadtxt('mtx_05zoom', delimiter=',', dtype=np.float64)
            self.DistortionCorrection.dist = np.loadtxt('dist_05zoom', delimiter=',', dtype=np.float64)
            return True
            # Return boolean to indicate success
        except Exception as e:
            return False
            # Handle the error appropriately
            
    def convert_npy2qimg(self, npy_image: np.ndarray) -> QImage:
        height, width = npy_image.shape[:2]
        bytesPerLine = 3 * width
        qImg = QImage(npy_image.data, width, height, bytesPerLine, QImage.Format_RGB888)
        return qImg



    @Slot(str)
    def load_image(self, input_image_path: str):
        if input_image_path.startswith("file:///"):
            input_image_path = input_image_path[8:]
        self.input_image_path = Path(input_image_path)
        # Grab the last part of the path
        # Should look like 10_s_87_F.jpg
        self.truncated_path = self.input_image_path.parts[-1]
        print(f"Truncated path: {self.truncated_path}")
        # Split the string by underscore
        self.truncated_path = self.truncated_path.split('_')
        # Grab the weight part
        self.actual_weight = float(self.truncated_path[2])
        print(f"Actual weight: {self.actual_weight}")
        
        
        # Ensure path debugging
        # print(f"Attempting to load image from path: {self.input_image_path}")
        try:
            
            self.input_image = cv.imread(str(self.input_image_path))
            # Ensure image is RGB
            # If image is not 1900x1425, resize it
            if self.input_image.shape[0] != 1425 or self.input_image.shape[1] != 1900:
                self.input_image = cv.resize(self.input_image, (1900, 1425))
            self.input_image = cv.cvtColor(self.input_image, cv.COLOR_BGR2RGB)
            # Display the self.input_image metadata
            print(f"Image shape: {self.input_image.shape}")  
              
            if self.input_image is None:
                print(f"Failed to load image at {self.input_image_path}")
            else:
                # Add the image to the provider
                qImg = self.convert_npy2qimg(self.input_image)
                image_provider.addImage("input_img", qImg)
                # print image metadata from the map
                print(f"Image metadata: {image_provider.myImageMap['input_img'].size()}")
                # Emit the signal to indicate that the image is ready
                self.imageLoaded.emit("input_img")
                self.imageProcessed.emit("dummy")
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
    image_provider = ImageProvider()
    engine.addImageProvider("imageprovider", image_provider)


    # Load the main QML file
    qml_file = Path(__file__).resolve().parent / "main.qml"
    engine.load(qml_file)
    if not engine.rootObjects():
        sys.stdout.write("Failed to load QML file")
        sys.exit(-1)

    sys.exit(app.exec())
