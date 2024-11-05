import numpy

from keras.optimizers import SGD
from keras import Input

from keras.models import Model

from keras.layers import Conv2D, Reshape
from keras.layers import Dense
from keras.layers import Flatten

input_shape = Input(shape=(14, 8, 8))


def compile_model(model):
    opt = SGD(lr=0.01, momentum=0.9)
    model.compile(optimizer=opt, loss='categorical_crossentropy', metrics=['accuracy'])
    return model


def LeNet(input_layer, kernel_size=(2, 2), pool_size=(2, 2), conv_size=64):

    X = Conv2D(filters=conv_size, kernel_size=kernel_size, padding='valid', activation='relu')(input_layer)
    X = Conv2D(filters=conv_size, kernel_size=kernel_size, padding='valid', activation='relu')(X)
    X = Flatten()(X)
    X = Dense(64, 'relu')(X)
    X = Dense(64, 'relu')(X)
    from_output_layer = Dense(2*8*8, activation='softmax')(X)

    from_output_layer = Reshape((2, 8, 8))(from_output_layer)

    model = Model(inputs=input_layer, outputs=[from_output_layer])

    return model

