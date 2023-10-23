import keras
from keras import applications
import numpy as np
from keras import backend as K
import gc
from keras.optimizers import SGD




print('LIBRARIES LOADED')

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


print('LOADING DATA')

model_to_fit = resnet50
opt = SGD(learning_rate=0.01, momentum=0.9)
model_to_fit.compile(optimizer=opt, loss='categorical_crossentropy', metrics=['accuracy'])
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