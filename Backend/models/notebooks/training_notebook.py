import numpy as np
from keras import backend as K
import gc
from keras.models import Model
from keras.layers import Conv2D, Reshape, MaxPooling2D
from keras.layers import Dense, ZeroPadding2D
from keras.layers import Flatten, Concatenate, BatchNormalization
from keras import Input
from keras.regularizers import l2
from keras.optimizers import SGD
from keras.layers import Add
from keras.layers import Activation

print('LIBRARIES LOADED')


def test_resnet():
    x1 = (1, 1)
    x3 = (3, 3)

    input_shape = (14, 8, 8)
    input_layer = Input(shape=input_shape, name='input_1')

    conv1 = Conv2D(256, kernel_size=x3, strides=(1, 1), padding='same', activation='relu')(input_layer)
    conv2 = Conv2D(256, kernel_size=x3, strides=(1, 1), padding='same', activation='relu')(conv1)
    conv3 = Conv2D(128, kernel_size=x1, strides=(1, 1), padding='same', activation='relu')(conv2)

    pool1 = MaxPooling2D(pool_size=(2, 2), strides=(2, 2), padding='same')(conv3)
    pad1 = ZeroPadding2D(padding=(1, 1))(pool1)  # Adjusted padding to ensure compatibility

    conv4 = Conv2D(128, kernel_size=x1, strides=(1, 1), padding='same', activation='relu')(pad1)
    conv5 = Conv2D(128, kernel_size=x3, strides=(1, 1), padding='same', activation='relu')(conv4)
    skip_connection = Add()([conv5, pad1])

    flatten = Flatten(name='flatten')(skip_connection)
    dense1 = Dense(64, activation='relu', name='dense')(flatten)
    dense2 = Dense(32, activation='relu', name='dense_1')(dense1)
    dense3 = Dense(64, activation='softmax', name='dense_2')(dense2)

    model = Model(inputs=[input_layer], outputs=[dense3])

    opt = SGD(learning_rate=0.01, momentum=0.9)
    model.compile(optimizer=opt, loss='categorical_crossentropy', metrics=['accuracy'])

    return model


def final_model_architecture():
    x1 = (1, 1)
    x2 = (2, 2)
    x3 = (3, 3)

    input_shape = (14, 8, 8)
    input_layer = Input(shape=input_shape, name='input_1')

    conv1 = Conv2D(256, kernel_size=x3, strides=(1, 1), padding='valid', activation='relu')(input_layer)
    conv2 = Conv2D(256, kernel_size=x3, strides=(1, 1), padding='valid', activation='relu')(conv1)
    conv3 = Conv2D(128, kernel_size=x1, strides=(1, 1), padding='valid', activation='relu')(conv2)
    pool1 = MaxPooling2D(pool_size=(2, 2), strides=(2, 2), padding='valid')(conv3)

    pad1 = ZeroPadding2D(padding=(3, 3))(pool1)
    conv4 = Conv2D(64, kernel_size=x1, strides=(1, 1), padding='valid', activation='relu')(pad1)
    conv5 = Conv2D(32, kernel_size=x1, strides=(1, 1), padding='valid', activation='relu')(conv4)
    conv6 = Conv2D(64, kernel_size=x1, strides=(1, 1), padding='valid', activation='relu')(conv5)
    conv7 = Conv2D(128, kernel_size=x3, strides=(1, 1), padding='valid', activation='relu')(conv6)
    pool2 = MaxPooling2D(pool_size=(2, 2), strides=(2, 2), padding='valid', name='max_pooling2d_1')(conv7)

    pad2 = ZeroPadding2D(padding=(3, 3))(pool2)
    conv8 = Conv2D(256, kernel_size=x1, strides=(1, 1), padding='valid', activation='relu')(pad2)
    conv9 = Conv2D(128, kernel_size=x1, strides=(1, 1), padding='valid', activation='relu')(conv8)
    conv10 = Conv2D(64, kernel_size=x1, strides=(1, 1), padding='valid', activation='relu')(conv9)
    conv11 = Conv2D(128, kernel_size=x3, strides=(1, 1), padding='valid', activation='relu')(conv10)
    pool3 = MaxPooling2D(pool_size=(2, 2), strides=(2, 2), padding='valid')(conv11)

    pad3 = ZeroPadding2D(padding=(3, 3))(pool3)
    conv8 = Conv2D(256, kernel_size=x2, strides=(1, 1), padding='valid', activation='relu')(pad3)
    conv9 = Conv2D(128, kernel_size=x2, strides=(1, 1), padding='valid', activation='relu')(conv8)
    conv10 = Conv2D(64, kernel_size=x2, strides=(1, 1), padding='valid', activation='relu')(conv9)
    conv11 = Conv2D(128, kernel_size=x2, strides=(1, 1), padding='valid', activation='relu')(conv10)
    pool3 = MaxPooling2D(pool_size=(2, 2), strides=(2, 2), padding='valid')(conv11)

    flatten = Flatten(name='flatten')(pool3)
    dense1 = Dense(64, activation='relu', name='dense')(flatten)
    dense2 = Dense(32, activation='relu', name='dense_1')(dense1)
    dense3 = Dense(64, activation='softmax', name='dense_2')(dense2)

    model = Model(inputs=[input_layer], outputs=[dense3])

    opt = SGD(learning_rate=0.01, momentum=0.9)
    model.compile(optimizer=opt, loss='categorical_crossentropy', metrics=['accuracy'])
    return model


"""
architecture with:



"""


def double_input_shape_model():
    x1 = (1, 1)
    x2 = (2, 2)
    x3 = (3, 3)

    weight_decay = 0.001

    input_shape = (14, 8, 8)

    input_layer = Input(shape=input_shape, name='input_1')

    conv1 = Conv2D(256, kernel_size=x3, strides=(1, 1), padding='valid', activation='relu',
                   kernel_regularizer=l2(weight_decay))(input_layer)
    conv2 = Conv2D(256, kernel_size=x3, strides=(1, 1), padding='valid', activation='relu',
                   kernel_regularizer=l2(weight_decay))(conv1)
    conv3 = Conv2D(128, kernel_size=x1, strides=(1, 1), padding='valid', activation='relu',
                   kernel_regularizer=l2(weight_decay))(conv2)
    pool1 = MaxPooling2D(pool_size=(2, 2), strides=(2, 2), padding='valid')(conv3)

    pad1 = ZeroPadding2D(padding=(3, 3))(pool1)
    pad1 = BatchNormalization(axis=1)(pad1)
    conv4 = Conv2D(64, kernel_size=x1, strides=(1, 1), padding='valid', activation='relu',
                   kernel_regularizer=l2(weight_decay))(pad1)
    conv5 = Conv2D(32, kernel_size=x1, strides=(1, 1), padding='valid', activation='relu',
                   kernel_regularizer=l2(weight_decay))(conv4)
    conv6 = Conv2D(64, kernel_size=x1, strides=(1, 1), padding='valid', activation='relu',
                   kernel_regularizer=l2(weight_decay))(conv5)
    conv7 = Conv2D(128, kernel_size=x3, strides=(1, 1), padding='valid', activation='relu',
                   kernel_regularizer=l2(weight_decay))(conv6)
    pool2 = MaxPooling2D(pool_size=(2, 2), strides=(2, 2), padding='valid')(conv7)

    pad2 = ZeroPadding2D(padding=(3, 3))(pool2)
    pad2 = BatchNormalization(axis=1)(pad2)
    conv8 = Conv2D(256, kernel_size=x1, strides=(1, 1), padding='valid', activation='relu',
                   kernel_regularizer=l2(weight_decay))(pad2)
    conv9 = Conv2D(128, kernel_size=x1, strides=(1, 1), padding='valid', activation='relu',
                   kernel_regularizer=l2(weight_decay))(conv8)
    conv10 = Conv2D(64, kernel_size=x1, strides=(1, 1), padding='valid', activation='relu',
                    kernel_regularizer=l2(weight_decay))(conv9)
    conv11 = Conv2D(128, kernel_size=x3, strides=(1, 1), padding='valid', activation='relu',
                    kernel_regularizer=l2(weight_decay))(conv10)
    pool3 = MaxPooling2D(pool_size=(2, 2), strides=(2, 2), padding='valid')(conv11)

    pad3 = ZeroPadding2D(padding=(3, 3))(pool3)
    pad3 = BatchNormalization(axis=1)(pad3)
    conv8 = Conv2D(256, kernel_size=x2, strides=(1, 1), padding='valid', activation='relu',
                   kernel_regularizer=l2(weight_decay))(pad3)
    conv9 = Conv2D(128, kernel_size=x2, strides=(1, 1), padding='valid', activation='relu',
                   kernel_regularizer=l2(weight_decay))(conv8)
    conv10 = Conv2D(64, kernel_size=x2, strides=(1, 1), padding='valid', activation='relu',
                    kernel_regularizer=l2(weight_decay))(conv9)
    conv11 = Conv2D(128, kernel_size=x2, strides=(1, 1), padding='valid', activation='relu',
                    kernel_regularizer=l2(weight_decay))(conv10)
    pool3 = MaxPooling2D(pool_size=(2, 2), strides=(2, 2), padding='valid')(conv11)

    flatten = Flatten(name='flatten')(pool3)
    dense1 = Dense(64, activation='relu', name='dense')(flatten)
    dense2 = Dense(32, activation='relu', name='dense_1')(dense1)
    dense3 = Dense(64, activation='softmax', name='dense_2')(dense2)

    model = Model(inputs=[input_layer], outputs=[dense3])

    opt = SGD(learning_rate=0.01, momentum=0.9)
    model.compile(optimizer=opt, loss='categorical_crossentropy', metrics=['accuracy'])
    return model


f_i = 0
s_i = 1000000

t_i = s_i + 1000


def fitness(model, X, y):
    score = model.evaluate(X, y, verbose=0)
    return score[1]


def make_0_63(couple):
    return couple[0] * 8 + couple[1]


def create_array(index):
    array = np.zeros(64)
    array[index] = 1
    return array


def increase():
    global f_i, s_i, t_i, x_fit, y_fit, x_test, y_test, white
    f_i += 1000000
    s_i += 1000000
    t_i = s_i + 1000

    x_fit = [x[f_i:s_i], white[f_i:s_i]]
    y_fit = y[f_i:s_i]

    x_test = [x[s_i:t_i], white[s_i:t_i]]
    y_test = y[s_i:t_i]


def change_data():
    global f_i, s_i, t_i, x_fit, y_fit, x_test, y_test, fit, test, white

    print('CHANGING DATA ')
    y_fit2 = []
    y_test2 = []
    for j in y_fit:
        y_fit2.append(make_0_63(j[0]))

    for j in y_test:
        y_test2.append(make_0_63(j[0]))

    y_fit = []
    y_test = []

    for j in y_fit2:
        y_fit.append(np.array(create_array(j)))

    for j in y_test2:
        y_test.append(np.array(create_array(j)))

    K.clear_session()
    gc.collect()

def main():

    print('LOADING DATA')

    model_to_fit = test_resnet()
    x = np.load('/kaggle/input/1700-lichess-user-bitboards/x.npy', mmap_mode='r')
    y = np.load('/kaggle/input/1700-lichess-user-bitboards/asdad.npy', mmap_mode='r')
    white = np.load('/kaggle/input/1700-lichess-user-bitboards/white2.npy', mmap_mode='r')

    x_fit = [x[f_i:s_i], white[f_i:s_i]]
    y_fit = y[f_i:s_i]

    x_test = [x[s_i:t_i], white[s_i:t_i]]
    y_test = y[s_i:t_i]

    for i in range(6):
        change_data()
        print('CYCLE NUMBER ', i)
        model_to_fit.fit(x_fit[0], np.array(y_fit), batch_size=64, epochs=5)
        fit_result = fitness(model_to_fit, x_test[0], np.array(y_test))
        print(fit_result)
        K.clear_session()
        gc.collect()
        increase()