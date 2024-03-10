import tensorflow as tf
import cv2
import numpy as np

"""
Usage:
    weights_path = '/path/to/your/weights.03.hdf5'
    image_path = '/path/to/your/test/image.jpg'

    # Instantiate the model
    prediction_model = CowWeightPredictor(weights_path)

    # Load and preprocess the image
    img = cv2.imread(image_path)
    img = cv2.resize(img, prediction_model.image_size)

    # Make a prediction
    prediction = prediction_model.make_prediction(img)
    print(prediction)
    
"""
class CowWeightPredictor:
    def __init__(self, weights_path):
        self.image_size = (224, 224)
        self.model = self.init_model(weights_path)
    
    def init_model(self, weights_path):
        # upsample input
        inputs = tf.keras.layers.Input(shape=(self.image_size[0], self.image_size[1], 3))
        
        # feature extraction using imagenet weights
        resnet_feature_extractor = tf.keras.applications.resnet.ResNet50(
            input_shape=(self.image_size[0], self.image_size[1], 3),
            include_top=False,
            weights='imagenet')(inputs)

        # some other layers
        temp = tf.keras.layers.GlobalAveragePooling2D()(resnet_feature_extractor)
        temp = tf.keras.layers.Flatten()(temp)
        temp = tf.keras.layers.Dense(512, activation='relu')(temp)
        regression_output = tf.keras.layers.Dense(1)(temp)
        model = tf.keras.Model(inputs=inputs, outputs=regression_output)
        model.load_weights(weights_path)
        return model
    
    def make_prediction(self, image):
        image_copy = np.copy(image)
        image_copy = cv2.resize(image_copy, self.image_size)
        image_copy = np.expand_dims(image_copy, axis=0) # add batch dimension
        return self.model.predict(image_copy)
    
        
        