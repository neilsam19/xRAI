from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.models import load_model
import numpy as np
import sys
import cv2

MODEL_PATH = "models/pneumonia_detector.h5"
model = load_model(MODEL_PATH)

def pneumonia_detector(img_path):
    image = load_img(img_path, target_size=(300, 300, 3))
    image_array = img_to_array(image)
    image_array = image_array / 255.0
    image_array = np.expand_dims(image_array, axis=0)
    pred = model.predict(image_array, verbose=0)[0][0]

    if (pred > 0.9):
        return "Pneumonia"
    return "normal"

if __name__ == '__main__':
    if len(sys.argv) > 1:
        img_path = sys.argv[1]
        print( pneumonia_detector(img_path) )