import numpy

from keras.optimizers import SGD
from keras import Input

from keras.models import Model

from keras.layers import Conv2D, Reshape
from keras.layers import Dense
from keras.layers import Flatten

input_shape = Input(shape=(14, 8, 8))


# comment
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




le_net = LeNet(input_shape)
le_net = compile_model(le_net)

filename_y = r'C:\Users\paolo\OneDrive\Desktop\Final_project\Ludus_scacchi\Backend\data\bit_boards\fritella_Y_bitboard.npy'
filename_x = r'C:\Users\paolo\OneDrive\Desktop\Final_project\Ludus_scacchi\Backend\data\bit_boards\fritella_bitboard.npy'

y = numpy.load(filename_y)
x = numpy.load(filename_x)

le_net.fit(x, y, epochs=100, batch_size=32)


filename_y = r'C:\Users\paolo\OneDrive\Desktop\Final_project\Ludus_scacchi\Backend\data\bit_boards\pollofritto_Y_bitboard.npy'
filename_x = r'C:\Users\paolo\OneDrive\Desktop\Final_project\Ludus_scacchi\Backend\data\bit_boards\pollofritto_bitboard.npy'

y = numpy.load(filename_y)
x = numpy.load(filename_x)

le_net.fit(x, y, epochs=100, batch_size=32)


filename_y = r'C:\Users\paolo\OneDrive\Desktop\Final_project\Ludus_scacchi\Backend\data\bit_boards\meliniak_Y_bitboard.npy'
filename_x = r'C:\Users\paolo\OneDrive\Desktop\Final_project\Ludus_scacchi\Backend\data\bit_boards\meliniak_bitboard.npy'

y = numpy.load(filename_y)
x = numpy.load(filename_x)

le_net.fit(x, y, epochs=100, batch_size=32)

