import sys
import numpy as np
import pandas as pd
import tensorflow as tf
from keras.applications.densenet import DenseNet121
from tensorflow.keras.preprocessing.image import load_img, img_to_array

def compile_model():
    feature_extractor = DenseNet121(weights='imagenet', include_top=False, input_shape=(512, 512, 3))
    averagePool = tf.keras.layers.GlobalAveragePooling2D()(feature_extractor.output)
    output = tf.keras.layers.Dense(14, activation='sigmoid', name='classification')(averagePool)
    model = tf.keras.Model(inputs=feature_extractor.input, outputs=output)
    optimizer = tf.keras.optimizers.SGD(learning_rate=0.01, momentum=0.9, nesterov=True)
    model.compile(optimizer=optimizer, loss='binary_crossentropy')
    return model

MODEL_PATH = "models/model13-0.8617.h5"
model = compile_model()
model.load_weights(MODEL_PATH)

CLASS_NAMES = ['Atelectasis', 'Cardiomegaly', 'Effusion', 'Infiltration', 'Mass', 'Nodule', 'Pneumonia', 'Pneumothorax',
               'Consolidation', 'Edema', 'Emphysema', 'Fibrosis', 'Pleural_Thickening', 'Hernia']

def preprocess_image(img_path, target_size=(512, 512)):
    image = load_img(img_path, target_size=target_size)
    image_array = img_to_array(image)
    image_array /= 255.0
    image_array = np.expand_dims(image_array, axis=0)
    return image_array

if __name__ == '__main__':
    if len(sys.argv) > 1:
        img_path = sys.argv[1]
        preprocessed_img = preprocess_image(img_path)
        predictions = model.predict(preprocessed_img, verbose=0)[0]
        predicted_class = int( tf.argmax(predictions) )
        print(f"{CLASS_NAMES[predicted_class]} {predictions[predicted_class]*100:.1f}")