import os
import numpy as np
from ultralytics import YOLO
import cv2

import matplotlib.pyplot as plt

class SegmentationModel:
    def __init__(self, model_path):
        self.model = YOLO(model_path)

    def preprocess_image(self, image_path):
        original_image = cv2.imread(image_path)
        converted_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)
        resized_image = cv2.resize(converted_image, dsize=(640, 480), interpolation=cv2.INTER_CUBIC)
        return resized_image

    def segment(self, image):
        return self.model.predict(source=image, conf=0.25, save=True)

    def show_binary_mask(self, results):
        return results[0].masks.data.cpu().numpy()[0]

    def show_filtered(self, image, results):
        image_copy = np.copy(image)
        return image_copy * results[0].masks.data.cpu().numpy()[0][..., np.newaxis]

    def show_bounding(self, image, results):
        image_copy = np.copy(image)
        cv2.rectangle(image_copy, (int(results[0].boxes.xyxy[0][0].item()), int(results[0].boxes.xyxy[0][1].item())), (int(results[0].boxes.xyxy[0][2].item()), int(results[0].boxes.xyxy[0][3].item())), (240,0,255), 2)
        cv2.putText(image_copy, 'cow ' + str(round(results[0].boxes.conf[0].item(), 2)), (int(results[0].boxes.xyxy[0][0].item()), int(results[0].boxes.xyxy[0][1].item()) - 7), cv2.FONT_HERSHEY_SIMPLEX, 1, (240,0,255), 2)
        return image_copy

    def display_image(self, image):
        plt.imshow(image)
        plt.axis('off')
        plt.show()
