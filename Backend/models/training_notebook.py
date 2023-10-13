import numpy as np

from keras import backend as K
import gc


from keras.models import Model

from keras.layers import Conv2D, Reshape, MaxPooling2D
from keras.layers import Dense, ZeroPadding2D
from keras.layers import Flatten, Concatenate
from keras import Input

from keras.optimizers import SGD




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
    pool1 = MaxPooling2D(pool_size=(2, 2), strides=(2, 2), padding='valid')(conv3)

    pad1 = ZeroPadding2D(padding=(3,3))(pool1)
    conv4 = Conv2D(64, kernel_size=x1, strides=(1, 1), padding='valid', activation='relu')(pad1)
    conv5 = Conv2D(32, kernel_size=x1, strides=(1, 1), padding='valid', activation='relu')(conv4)
    conv6 = Conv2D(64, kernel_size=x1, strides=(1, 1), padding='valid', activation='relu')(conv5)
    conv7 = Conv2D(128, kernel_size=x3, strides=(1, 1), padding='valid', activation='relu')(conv6)
    pool2 = MaxPooling2D(pool_size=(2, 2), strides=(2, 2), padding='valid')(conv7)

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



f_i = 0
s_i = 1000000

t_i = s_i + 1000

def fitness(model, X, y):
    score = model.evaluate(X, y, verbose=0)
    return score[1]


def increase():
    global f_i, s_i, t_i, x_fit,y_fit,x_test,y_test,fit,test
    f_i += 1000000
    s_i += 1000000
    t_i = s_i + 1000
    x_fit = x[f_i:s_i]
    y_fit = y[f_i:s_i]
    x_test = x[s_i:t_i]
    y_test = y[s_i:t_i]
    fit = (x_fit,y_fit)
    test = (x_test,y_test)


model_to_fit = final_model_architecture()
x = np.load('/kaggle/input/1700-lichess-user-bitboards/x.npy',mmap_mode='r')
y = np.load('/kaggle/input/1700-lichess-user-bitboards/y.npy',mmap_mode='r')
white = np.load('/kaggle/input/1700-lichess-user-bitboards/white.npy',mmap_mode='r')


x_fit = [x[f_i:s_i],  white[f_i:s_i]]
y_fit = y[f_i:s_i]


x_test = [x[s_i:t_i], white[s_i:t_i]]
y_test = y[s_i:t_i]

fit = (x_fit, y_fit)
test = (x_test, y_test)

for i in range(5):
    model_to_fit.fit(fit[0][0],fit[1],batch_size=128,epochs = 3)
    fit_result = fitness(model_to_fit,test[0][0], test[1])
    print(fit_result)
    K.clear_session()
    gc.collect()
    increase()