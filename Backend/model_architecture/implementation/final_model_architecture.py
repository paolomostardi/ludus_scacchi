from keras.models import Model

from keras.layers import Conv2D, Reshape, MaxPooling2D
from keras.layers import Dense, ZeroPadding2D
from keras.layers import Flatten, Concatenate
from keras import Input
from keras.optimizers import SGD

x1 = (1, 1)
x2 = (2, 2)
x3 = (3, 3)

# Experimental architecture 
# This code defines several convolutional neural network architectures with the following purposes:
#
# 1 - single_block_model:
#     - Takes a single input of shape (15, 8, 8)
#     - Contains one convolutional block followed by a flatten + three dense layers
#     - Outputs a reshaped tensor of shape (2, 8, 8)
#
# 2 - final_model_architecture:
#     - Takes a single input of shape (15, 8, 8)
#     - Stacks four convolutional blocks, each with Conv2D layers followed by MaxPooling
#     - Includes zero-padding between blocks to preserve spatial dimensions
#     - Ends with a flatten + three dense layers and reshapes the output to (2, 8, 8)
#
# 3 - double_input_shape_model:
#     - Takes two inputs: one of shape (15, 8, 8) and another of shape (1, 8, 8)
#     - Concatenates the inputs along the channel dimension
#     - Applies the same four-block convolutional + dense architecture as final_model_architecture
#     - Outputs a reshaped tensor of shape (2, 8, 8)
#
# Each model uses ReLU activations in the Conv2D and Dense layers, SGD optimizer with 
# momentum 0.9, and categorical crossentropy loss. The reshaping at the end allows 
# for output compatibility with a target tensor of shape (2, 8, 8).


def block_1(input_layer):

    X = Conv2D(256, kernel_size=x3, strides=(1, 1), padding='valid', activation='relu')(input_layer)
    X = Conv2D(256, kernel_size=x3, strides=(1, 1), padding='valid', activation='relu')(X)
    X = Conv2D(128, kernel_size=x1, strides=(1, 1), padding='valid', activation='relu')(X)
    X = MaxPooling2D(pool_size=(2, 2), strides=(2, 2), padding='valid', name='max_pooling2d')(X)
    
    return X

def block_2(input_layer):
    conv4 = Conv2D(64, kernel_size=x1, strides=(1, 1), padding='valid', activation='relu')(input_layer)
    conv5 = Conv2D(32, kernel_size=x1, strides=(1, 1), padding='valid', activation='relu')(conv4)
    conv6 = Conv2D(64, kernel_size=x1, strides=(1, 1), padding='valid', activation='relu')(conv5)
    conv7 = Conv2D(128, kernel_size=x3, strides=(1, 1), padding='valid', activation='relu')(conv6)
    pool2 = MaxPooling2D(pool_size=(2, 2), strides=(2, 2), padding='valid', name='max_pooling2d_1')(conv7)

    return pool2

def block_3(input_layer):
    conv4 = Conv2D(64, kernel_size=x1, strides=(1, 1), padding='valid', activation='relu')(input_layer)
    conv5 = Conv2D(32, kernel_size=x1, strides=(1, 1), padding='valid', activation='relu')(conv4)
    conv6 = Conv2D(64, kernel_size=x1, strides=(1, 1), padding='valid', activation='relu')(conv5)
    conv7 = Conv2D(128, kernel_size=x3, strides=(1, 1), padding='valid', activation='relu')(conv6)
    pool2 = MaxPooling2D(pool_size=(2, 2), strides=(2, 2), padding='valid', name='max_pooling2d_1')(conv7)  

def block_4(input_layer):
    conv8 = Conv2D(256, kernel_size=x1, strides=(1, 1), padding='valid', activation='relu')(input_layer)
    conv9 = Conv2D(128, kernel_size=x1, strides=(1, 1), padding='valid', activation='relu')(conv8)
    conv10 = Conv2D(64, kernel_size=x1, strides=(1, 1), padding='valid', activation='relu')(conv9)
    conv11 = Conv2D(128, kernel_size=x3, strides=(1, 1), padding='valid', activation='relu')(conv10)
    pool3 = MaxPooling2D(pool_size=(2, 2), strides=(2, 2), padding='valid')(conv11)

def dense_block(input_layer):
    dense1 = Dense(64, activation='relu', name='dense')(input_layer)
    dense2 = Dense(32, activation='relu', name='dense_1')(dense1)
    dense3 = Dense(128, activation='relu', name='dense_2')(dense2)

# a simple model 
def single_block_model(input_shape):

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


def final_model_architecture(input_shape):

    input_layer = Input(shape=input_shape, name='input_1')

    # block 1
    conv1 = Conv2D(256, kernel_size=x3, strides=(1, 1), padding='valid', activation='relu')(input_layer)
    conv2 = Conv2D(256, kernel_size=x3, strides=(1, 1), padding='valid', activation='relu')(conv1)
    conv3 = Conv2D(128, kernel_size=x1, strides=(1, 1), padding='valid', activation='relu')(conv2)
    pool1 = MaxPooling2D(pool_size=(2, 2), strides=(2, 2), padding='valid', name='max_pooling2d')(conv3)

    pad1 = ZeroPadding2D(padding=(3,3))(pool1)
    # block 2
    conv4 = Conv2D(64, kernel_size=x1, strides=(1, 1), padding='valid', activation='relu')(pad1)
    conv5 = Conv2D(32, kernel_size=x1, strides=(1, 1), padding='valid', activation='relu')(conv4)
    conv6 = Conv2D(64, kernel_size=x1, strides=(1, 1), padding='valid', activation='relu')(conv5)
    conv7 = Conv2D(128, kernel_size=x3, strides=(1, 1), padding='valid', activation='relu')(conv6)
    pool2 = MaxPooling2D(pool_size=(2, 2), strides=(2, 2), padding='valid', name='max_pooling2d_1')(conv7)
    
    pad2 = ZeroPadding2D(padding=(3,3))(pool2)
    # block 3
    conv8 = Conv2D(256, kernel_size=x1, strides=(1, 1), padding='valid', activation='relu')(pad2)
    conv9 = Conv2D(128, kernel_size=x1, strides=(1, 1), padding='valid', activation='relu')(conv8)
    conv10 = Conv2D(64, kernel_size=x1, strides=(1, 1), padding='valid', activation='relu')(conv9)
    conv11 = Conv2D(128, kernel_size=x3, strides=(1, 1), padding='valid', activation='relu')(conv10)
    pool3 = MaxPooling2D(pool_size=(2, 2), strides=(2, 2), padding='valid')(conv11)

    pad3 = ZeroPadding2D(padding=(3,3))(pool3)
    # adding kernels of size 2x2 might be questionable, but still interesting 
    # block 4    
    conv8 = Conv2D(256, kernel_size=x2, strides=(1, 1), padding='valid', activation='relu')(pad3)
    conv9 = Conv2D(128, kernel_size=x2, strides=(1, 1), padding='valid', activation='relu')(conv8)
    conv10 = Conv2D(64, kernel_size=x2, strides=(1, 1), padding='valid', activation='relu')(conv9)
    conv11 = Conv2D(128, kernel_size=x2, strides=(1, 1), padding='valid', activation='relu')(conv10)
    pool3 = MaxPooling2D(pool_size=(2, 2), strides=(2, 2), padding='valid')(conv11)

    # dense block
    flatten = Flatten(name='flatten')(pool3)
    dense1 = Dense(64, activation='relu', name='dense')(flatten)
    dense2 = Dense(32, activation='relu', name='dense_1')(dense1)
    dense3 = Dense(128, activation='relu', name='dense_2')(dense2)

    reshape_layer = Reshape(target_shape=(2, 8, 8), name='reshape')(dense3)

    model = Model(inputs=input_layer, outputs=[reshape_layer])
    opt = SGD(learning_rate=0.01, momentum=0.9)
    model.compile(optimizer=opt, loss='categorical_crossentropy', metrics=['accuracy'])
    return model


def double_input_shape_model(input_shape):
    x1 = (1, 1)
    x2 = (2, 2)
    x3 = (3, 3)

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


