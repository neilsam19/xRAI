import tensorflow as tf
from keras.applications.densenet import DenseNet121

def compile_model():
    feature_extractor = DenseNet121(weights='imagenet', include_top=False, input_shape=(512, 512, 3))
    return

model = compile_model()