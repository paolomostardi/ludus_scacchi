from keras.models import Model

from keras.layers import Conv2D, Reshape, MaxPooling2D
from keras.layers import Dense, ZeroPadding2D
from keras.layers import Flatten, Concatenate
from keras import Input

from keras.optimizers import SGD


x1 = (1, 1)
x2 = (2, 2)
x3 = (3, 3)


def add_conv_block(X, filter = None, kernel_size = None):
    if filter is None:
        first_filter, second_filter, third_filter,fourth_filter = 256, 256, 128,128
    else:
        first_filter, second_filter, third_filter,fourth_filter = filter

    if kernel_size is None:
        first_kernel = x3
        second_kernel = x3
        third_kernel = x1
        fourth_kernel = x1

    else:
        first_kernel, second_kernel, third_kernel, fourth_kernel = filter

    X = Conv2D(first_filter, kernel_size=first_kernel, strides=(1, 1), padding='valid', activation='relu')(X)
    X = Conv2D(second_filter, kernel_size=second_kernel, strides=(1, 1), padding='valid', activation='relu')(X)
    X = Conv2D(third_filter, kernel_size=third_kernel, strides=(1, 1), padding='valid', activation='relu')(X)
    X = Conv2D(third_filter, kernel_size=third_kernel, strides=(1, 1), padding='valid', activation='relu')(X)

    X = MaxPooling2D(pool_size=(2, 2), strides=(2, 2), padding='valid')(X)

    return X


def add_dense_part(X, input_shape):
    flatten = Flatten(name='flatten')(X)
    dense1 = Dense(64, activation='relu', name='dense')(flatten)
    dense2 = Dense(32, activation='relu', name='dense_1')(dense1)
    dense3 = Dense(128, activation='relu', name='dense_2')(dense2)

    reshape_layer = Reshape(target_shape=(2, 8, 8), name='reshape')(dense3)

    model = Model(inputs=[input_shape], outputs=[reshape_layer])
    opt = SGD(learning_rate=0.01, momentum=0.9)
    model.compile(optimizer=opt, loss='categorical_crossentropy', metrics=['accuracy'])

    return model


def block_1(input_layer):

    X = Conv2D(256, kernel_size=x3, strides=(1, 1), padding='valid', activation='relu')(input_layer)
    X = Conv2D(256, kernel_size=x3, strides=(1, 1), padding='valid', activation='relu')(X)
    X = Conv2D(128, kernel_size=x1, strides=(1, 1), padding='valid', activation='relu')(X)
    X = MaxPooling2D(pool_size=(2, 2), strides=(2, 2), padding='valid', name='max_pooling2d')(X)

    return X


def final_model():
    input_shape = (14, 8, 8)
    input_layer = Input(shape=input_shape)

    X = block_1(input_layer)
    X = ZeroPadding2D(padding=(3, 3))(X)


    flatten = Flatten(name='flatten')(X)
    dense1 = Dense(64, activation='relu', name='dense')(flatten)
    dense2 = Dense(32, activation='relu', name='dense_1')(dense1)
    dense3 = Dense(128, activation='relu', name='dense_2')(dense2)

    reshape_layer = Reshape(target_shape=(2, 8, 8), name='reshape')(dense3)

    model = Model(inputs=input_layer, outputs=[reshape_layer])
    opt = SGD(learning_rate=0.01, momentum=0.9)
    model.compile(optimizer=opt, loss='categorical_crossentropy', metrics=['accuracy'])
    return model


def final_model_architecture():

    input_shape = (14, 8, 8)
    input_layer = Input(shape=input_shape, name='input_1')

    conv1 = Conv2D(256, kernel_size=x3, strides=(1, 1), padding='valid', activation='relu')(input_layer)
    conv2 = Conv2D(256, kernel_size=x3, strides=(1, 1), padding='valid', activation='relu')(conv1)
    conv3 = Conv2D(128, kernel_size=x1, strides=(1, 1), padding='valid', activation='relu')(conv2)
    pool1 = MaxPooling2D(pool_size=(2, 2), strides=(2, 2), padding='valid', name='max_pooling2d')(conv3)

    pad1 = ZeroPadding2D(padding=(3,3))(pool1)
    conv4 = Conv2D(64, kernel_size=x1, strides=(1, 1), padding='valid', activation='relu')(pad1)
    conv5 = Conv2D(32, kernel_size=x1, strides=(1, 1), padding='valid', activation='relu')(conv4)
    conv6 = Conv2D(64, kernel_size=x1, strides=(1, 1), padding='valid', activation='relu')(conv5)
    conv7 = Conv2D(128, kernel_size=x3, strides=(1, 1), padding='valid', activation='relu')(conv6)
    pool2 = MaxPooling2D(pool_size=(2, 2), strides=(2, 2), padding='valid', name='max_pooling2d_1')(conv7)

    pad2 = ZeroPadding2D(padding=(3,3))(pool2)
    conv8 = Conv2D(256, kernel_size=x1, strides=(1, 1), padding='valid', activation='relu')(pad2)
    conv9 = Conv2D(128, kernel_size=x1, strides=(1, 1), padding='valid', activation='relu')(conv8)
    conv10 = Conv2D(64, kernel_size=x1, strides=(1, 1), padding='valid', activation='relu')(conv9)
    conv11 = Conv2D(128, kernel_size=x3, strides=(1, 1), padding='valid', activation='relu')(conv10)
    pool3 = MaxPooling2D(pool_size=(2, 2), strides=(2, 2), padding='valid')(conv11)

    pad3 = ZeroPadding2D(padding=(3,3))(pool3)
    conv8 = Conv2D(256, kernel_size=x2, strides=(1, 1), padding='valid', activation='relu')(pad3)
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
    opt = SGD(learning_rate=0.01, momentum=0.9)
    model.compile(optimizer=opt, loss='categorical_crossentropy', metrics=['accuracy'])
    return model


def double_input_shape_model():
    x1 = (1, 1)
    x2 = (2, 2)
    x3 = (3, 3)

    input_shape = (14, 8, 8)
    second_input_shape = (1,8,8)

    input_layer = Input(shape=input_shape, name='input_1')
    second_input_layer = Input(shape=second_input_shape, name='input_2')

    concat_input = Concatenate(1)([input_layer, second_input_layer])

    conv1 = Conv2D(256, kernel_size=x3, strides=(1, 1), padding='valid', activation='relu')(concat_input)
    conv2 = Conv2D(256, kernel_size=x3, strides=(1, 1), padding='valid', activation='relu')(conv1)
    conv3 = Conv2D(128, kernel_size=x1, strides=(1, 1), padding='valid', activation='relu')(conv2)
    pool1 = MaxPooling2D(pool_size=(2, 2), strides=(2, 2), padding='valid', name='max_pooling2d')(conv3)

    pad1 = ZeroPadding2D(padding=(3,3))(pool1)
    conv4 = Conv2D(64, kernel_size=x1, strides=(1, 1), padding='valid', activation='relu')(pad1)
    conv5 = Conv2D(32, kernel_size=x1, strides=(1, 1), padding='valid', activation='relu')(conv4)
    conv6 = Conv2D(64, kernel_size=x1, strides=(1, 1), padding='valid', activation='relu')(conv5)
    conv7 = Conv2D(128, kernel_size=x3, strides=(1, 1), padding='valid', activation='relu')(conv6)
    pool2 = MaxPooling2D(pool_size=(2, 2), strides=(2, 2), padding='valid', name='max_pooling2d_1')(conv7)

    pad2 = ZeroPadding2D(padding=(3,3))(pool2)
    conv8 = Conv2D(256, kernel_size=x1, strides=(1, 1), padding='valid', activation='relu')(pad2)
    conv9 = Conv2D(128, kernel_size=x1, strides=(1, 1), padding='valid', activation='relu')(conv8)
    conv10 = Conv2D(64, kernel_size=x1, strides=(1, 1), padding='valid', activation='relu')(conv9)
    conv11 = Conv2D(128, kernel_size=x3, strides=(1, 1), padding='valid', activation='relu')(conv10)
    pool3 = MaxPooling2D(pool_size=(2, 2), strides=(2, 2), padding='valid')(conv11)

    pad3 = ZeroPadding2D(padding=(3,3))(pool3)
    conv8 = Conv2D(256, kernel_size=x2, strides=(1, 1), padding='valid', activation='relu')(pad3)
    conv9 = Conv2D(128, kernel_size=x2, strides=(1, 1), padding='valid', activation='relu')(conv8)
    conv10 = Conv2D(64, kernel_size=x2, strides=(1, 1), padding='valid', activation='relu')(conv9)
    conv11 = Conv2D(128, kernel_size=x2, strides=(1, 1), padding='valid', activation='relu')(conv10)
    pool3 = MaxPooling2D(pool_size=(2, 2), strides=(2, 2), padding='valid')(conv11)

    flatten = Flatten(name='flatten')(pool3)
    dense1 = Dense(64, activation='relu', name='dense')(flatten)
    dense2 = Dense(32, activation='relu', name='dense_1')(dense1)
    dense3 = Dense(128, activation='relu', name='dense_2')(dense2)

    reshape_layer = Reshape(target_shape=(2, 8, 8), name='reshape')(dense3)

    model = Model(inputs=[input_layer, second_input_layer], outputs=[reshape_layer])
    opt = SGD(learning_rate=0.01, momentum=0.9)
    model.compile(optimizer=opt, loss='categorical_crossentropy', metrics=['accuracy'])
    return model


