from keras.models import Model

from keras.layers import Conv2D, Reshape, MaxPooling2D
from keras.layers import Dense
from keras.layers import Flatten
from keras import Input

from keras.optimizers import SGD


def final_model_architecture():
    x1 = (1, 1)
    x2 = (2, 2)
    x3 = (3, 3)

    input_shape = (14, 8, 8)
    input_layer = Input(shape=input_shape, name='input_1')
    conv1 = Conv2D(256, kernel_size=x3, strides=(1, 1), padding='valid', activation='relu', name='conv2d')(input_layer)
    conv2 = Conv2D(256, kernel_size=x3, strides=(1, 1), padding='valid', activation='relu', name='conv2d_1')(conv1)
    conv3 = Conv2D(128, kernel_size=x1, strides=(1, 1), padding='valid', activation='relu', name='conv2d_2')(conv2)
    pool1 = MaxPooling2D(pool_size=(2, 2), strides=(2, 2), padding='valid', name='max_pooling2d')(conv3)

    conv4 = Conv2D(64, kernel_size=x1, strides=(1, 1), padding='valid', activation='relu', name='conv2d_3')(pool1)
    conv5 = Conv2D(32, kernel_size=x1, strides=(1, 1), padding='valid', activation='relu', name='conv2d_4')(conv4)
    conv6 = Conv2D(64, kernel_size=x1, strides=(1, 1), padding='valid', activation='relu', name='conv2d_5')(conv5)
    conv7 = Conv2D(128, kernel_size=x3, strides=(1, 1), padding='valid', activation='relu', name='conv2d_6')(conv6)
    pool2 = MaxPooling2D(pool_size=(2, 2), strides=(2, 2), padding='valid', name='max_pooling2d_1')(conv7)

    conv8 = Conv2D(256, kernel_size=x1, strides=(1, 1), padding='valid', activation='relu')(pool2)
    conv9 = Conv2D(128, kernel_size=x1, strides=(1, 1), padding='valid', activation='relu')(conv8)
    conv10 = Conv2D(64, kernel_size=x1, strides=(1, 1), padding='valid', activation='relu')(conv9)
    conv11 = Conv2D(128, kernel_size=x3, strides=(1, 1), padding='valid', activation='relu')(conv10)
    pool3 = MaxPooling2D(pool_size=(2, 2), strides=(2, 2), padding='valid')(conv11)

    conv8 = Conv2D(256, kernel_size=x2, strides=(1, 1), padding='valid', activation='relu')(pool3)
    conv9 = Conv2D(128, kernel_size=x2, strides=(1, 1), padding='valid', activation='relu')(conv8)
    conv10 = Conv2D(64, kernel_size=x2, strides=(1, 1), padding='valid', activation='relu')(conv9)
    conv11 = Conv2D(128, kernel_size=x2, strides=(1, 1), padding='valid', activation='relu')(conv10)
    pool3 = MaxPooling2D(pool_size=(2, 2), strides=(2, 2), padding='valid')(conv11)

    flatten = Flatten(name='flatten')(pool3)
    dense1 = Dense(64, activation='relu', name='dense')(flatten)
    dense2 = Dense(32, activation='relu', name='dense_1')(dense1)
    dense3 = Dense(128, activation='relu', name='dense_2')(dense2)

    reshape_layer = Reshape(target_shape=(2, 8, 8), name='reshape')(dense3)

    model = Model(inputs=input_layer, outputs=[reshape_layer])
    opt = SGD(lr=0.01, momentum=0.9)
    model.compile(optimizer=opt, loss='categorical_crossentropy', metrics=['accuracy'])
    return model






