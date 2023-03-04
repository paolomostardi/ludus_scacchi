import keras
import tensorflow
from keras.layers import Conv2D
from keras.layers import Dense

def conv2D():
    return Conv2D(10, (3, 3), activation='relu')


def dense():
    return Dense(100, 'relu')


def softmax():
    return Dense(10, 'softmax')


def create_model():
    model = keras.Sequential()
    model.add(conv2D())
    model.add(conv2D())
    model.add(dense())
    model.add(softmax())
    return model


def train_model(model_to_train):
    model_to_train.summary()
    return model_to_train


model_1 = create_model()
train_model(model_1)

