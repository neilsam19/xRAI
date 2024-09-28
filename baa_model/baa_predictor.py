import sys
import pickle
import numpy as np
from tensorflow import keras
from skimage.transform import resize
from skimage.io import imread, imshow

# load svr
with open('baa_model.pkl', 'rb') as f:
    svr = pickle.load(f)

# create segmentor
MODEL_PATH = "FINAL_UNET_MODEL.h5"
inputs = keras.layers.Input( (256, 256, 1) )
s = keras.layers.Lambda(lambda x: x / 255.)(inputs)

# contracting path
c1 = keras.layers.Conv2D(64, (5,5), activation="relu", kernel_initializer="he_normal", padding="same")(s)
c1 = keras.layers.Dropout(0.2)(c1)
c1 = keras.layers.Conv2D(64, (5,5), activation="relu", kernel_initializer="he_normal", padding="same")(c1)
p1 = keras.layers.MaxPooling2D( (2,2) )(c1)

c2 = keras.layers.Conv2D(96, (3,3), activation="relu", kernel_initializer="he_normal", padding="same")(p1)
c2 = keras.layers.Dropout(0.2)(c2)
c2 = keras.layers.Conv2D(96, (3,3), activation="relu", kernel_initializer="he_normal", padding="same")(c2)
p2 = keras.layers.MaxPooling2D( (2,2) )(c2)

c3 = keras.layers.Conv2D(128, (3,3), activation="relu", kernel_initializer="he_normal", padding="same")(p2)
c3 = keras.layers.Dropout(0.2)(c3)
c3 = keras.layers.Conv2D(128, (3,3), activation="relu", kernel_initializer="he_normal", padding="same")(c3)
p3 = keras.layers.MaxPooling2D( (2,2) )(c3)

c4 = keras.layers.Conv2D(256, (3,3), activation="relu", kernel_initializer="he_normal", padding="same")(p3)
c4 = keras.layers.Dropout(0.2)(c4)
c4 = keras.layers.Conv2D(256, (3,3), activation="relu", kernel_initializer="he_normal", padding="same")(c4)
p4 = keras.layers.MaxPooling2D( (2,2) )(c4)

c5 = keras.layers.Conv2D(512, (3,3), activation="relu", kernel_initializer="he_normal", padding="same")(p4)
c5 = keras.layers.Dropout(0.2)(c5)
c5 = keras.layers.Conv2D(512, (3,3), activation="relu", kernel_initializer="he_normal", padding="same")(c5)

# expansive path
u6 = keras.layers.Conv2DTranspose(256, (2,2), strides=(2,2), padding="same")(c5)
u6 = keras.layers.concatenate([u6, c4])
c6 = keras.layers.Conv2D(256, (3,3), activation="relu", kernel_initializer="he_normal", padding="same")(u6)
c6 = keras.layers.Dropout(0.2)(c6)
c6 = keras.layers.Conv2D(256, (3,3), activation="relu", kernel_initializer="he_normal", padding="same")(c6)

u7 = keras.layers.Conv2DTranspose(128, (2,2), strides=(2,2), padding="same")(c6)
u7 = keras.layers.concatenate([u7, c3])
c7 = keras.layers.Conv2D(128, (3,3), activation="relu", kernel_initializer="he_normal", padding="same")(u7)
c7 = keras.layers.Dropout(0.2)(c7)
c7 = keras.layers.Conv2D(128, (3,3), activation="relu", kernel_initializer="he_normal", padding="same")(c7)

u8 = keras.layers.Conv2DTranspose(96, (2,2), strides=(2,2), padding="same")(c7)
u8 = keras.layers.concatenate([u8, c2])
c8 = keras.layers.Conv2D(96, (3,3), activation="relu", kernel_initializer="he_normal", padding="same")(u8)
c8 = keras.layers.Dropout(0.1)(c8)
c8 = keras.layers.Conv2D(96, (3,3), activation="relu", kernel_initializer="he_normal", padding="same")(c8)

u9 = keras.layers.Conv2DTranspose(64, (2,2), strides=(2,2), padding="same")(c8)
u9 = keras.layers.concatenate([u9, c1], axis=3)
c9 = keras.layers.Conv2D(64, (5,5), activation="relu", kernel_initializer="he_normal", padding="same")(u9)
c9 = keras.layers.Dropout(0.1)(c9)
c9 = keras.layers.Conv2D(64, (5,5), activation="relu", kernel_initializer="he_normal", padding="same")(c9)

outputs = keras.layers.Conv2D(1, (1,1), activation="sigmoid")(c9)

model = keras.Model(inputs=[inputs], outputs=[outputs])
model.compile(optimizer="adam", loss='binary_crossentropy', metrics=['accuracy'])
model.load_weights(MODEL_PATH)

def baa_predictor(img_path):
    # read in image
    image = imread(img_path)
    image = resize(image, (256, 256, 1), mode="constant", preserve_range=True)
    result = model.predict( np.expand_dims(image, 0), verbose=0 )[0]
    result = np.where(result >= np.mean(result), 1, 0)
    result = result.flatten()
    result = result.reshape(1, -1)

    preds = svr.predict(result[:])
    return f'{preds[0]:.1f}'

if __name__ == '__main__':
    if len(sys.argv) > 1:
        img_path = sys.argv[1]
        print( baa_predictor(img_path) )