import random
import keras.models
from keras import Input

from keras.layers import Conv2D, MaxPooling2D, Dropout, Flatten, Dense, Add, Reshape
from keras.layers import BatchNormalization
from keras.models import Model
from keras.optimizers import SGD


def fitness(model, X, y):
    score = model.evaluate(X, y, verbose=0)
    return score[1]


def generate_random_model(input_shape):

    model_id = []
    block_id = []

    residual_network = [False]
    filter_amount = [16,32,64,128,256]
    kernel_size = [(1,1), (2,2), (3,3), (4,4)]
    dense_amount = [16,32,64]
    batch_normalization = [True,False]
    pooling_layers = [True, False]
    block_amount = [1,2,3,4]

    block_amount = random.choice(block_amount)

    block_id.append((random.choice(filter_amount),random.choice(kernel_size)))

    X = Conv2D(filters= block_id[0][0], kernel_size=block_id[0][1],activation='relu')(input_shape)

    for block in range(block_amount):

        residual_choice = random.choice(residual_network)
        block_id.append(residual_choice)
        if residual_choice:
            X_shortcut = X


        filter_choice = random.choice(filter_amount)
        kernel_choice = random.choice(kernel_size)
        block_id.append((filter_choice, kernel_choice))
        X = Conv2D(filters=filter_choice, kernel_size=kernel_choice, activation='relu',padding='same')(X)



        filter_choice = random.choice(filter_amount)
        kernel_choice = random.choice(kernel_size)
        block_id.append((filter_choice, kernel_choice))
        X = Conv2D(filters=filter_choice, kernel_size=kernel_choice, activation='relu',padding='same')(X)


        if residual_choice:
            X_shortcut = Conv2D(filters=filter_choice,kernel_size=(1,1),activation='relu',padding='same')(X_shortcut)
            X_shortcut = Conv2D(filters=filter_choice, kernel_size=(1, 1), activation='relu',padding='same')(X_shortcut)
            Add()([X,X_shortcut])

        pooling_choice = random.choice(pooling_layers)
        block_id.append(pooling_choice)

        if pooling_choice:
            X = MaxPooling2D((2, 2),padding='same')(X)

        normalization_choice = random.choice(batch_normalization)
        block_id.append(normalization_choice)

        if normalization_choice:
            X = BatchNormalization(axis=1)(X)

        model_id.append(block_id)
        block_id  = []


    X =  Flatten()(X)

    dense_choice = random.choice(dense_amount)
    model_id.append(dense_choice)
    X = Dense(dense_choice, 'relu')(X)

    dense_choice = random.choice(dense_amount)
    model_id.append(dense_choice)
    X = Dense(dense_choice, 'relu')(X)


    from_output_layer = Dense(2*8*8, activation='softmax')(X)

    from_output_layer = Reshape((2, 8, 8))(from_output_layer)

    model = Model(inputs=input_shape, outputs=[from_output_layer])

    opt = SGD(lr=0.01, momentum=0.9)
    model.compile(optimizer=opt, loss='categorical_crossentropy', metrics=['accuracy'])

    return model, model_id



def random_generation(number_of_cycles,fit,test):

    input_shape = Input(shape=(14, 8, 8))

    model_list = []


    for cycle in range(number_of_cycles):
        random_model,model_id  = generate_random_model(input_shape)
        random_model.fit(fit[0],fit[1],batch_size=64,epochs = 5)
        fit = fitness(random_model,test[0], test[1])
        model_list.append([random_model,model_id,fit])

    return model_list

# adds some extra layers
def generate_model_from_id(model_id, input_shape):
    X = Conv2D(filters=model_id[0][0][0], kernel_size=model_id[0][0][1], activation='relu')(input_shape)

    for block in model_id[1:-2]:

        residual_choice = block[0]
        if residual_choice:
            X_shortcut = X

        filter_choice, kernel_choice = block[1]
        X = Conv2D(filters=filter_choice, kernel_size=kernel_choice, activation='relu', padding='same')(X)

        filter_choice, kernel_choice = block[2]
        X = Conv2D(filters=filter_choice, kernel_size=kernel_choice, activation='relu', padding='same')(X)

        if residual_choice:
            X_shortcut = Conv2D(filters=filter_choice, kernel_size=(1, 1), activation='relu', padding='same')(
                X_shortcut)
            X_shortcut = Conv2D(filters=filter_choice, kernel_size=(1, 1), activation='relu', padding='same')(
                X_shortcut)
            X = Add()([X, X_shortcut])

        pooling_choice = block[3]

        if pooling_choice:
            X = MaxPooling2D((2, 2), padding='same')(X)

        print(block[4])

        normalization_choice = block[4]
        if normalization_choice:
            X = BatchNormalization(axis=1)(X)

    X = Conv2D(filters=128, kernel_size=(1, 1), activation='relu', padding='same')(X)
    X = Conv2D(filters=128, kernel_size=(1, 1), activation='relu', padding='same')(X)
    X = Conv2D(filters=64, kernel_size=(1, 1), activation='relu', padding='same')(X)
    X = Conv2D(filters=128, kernel_size=(3, 3), activation='relu', padding='same')(X)
    X = MaxPooling2D((2, 2), padding='same')(X)

    print('Flatten')
    X = Flatten()(X)

    dense_choice = model_id[-2]
    print(dense_choice)
    X = Dense(dense_choice, 'relu')(X)
    dense_choice = model_id[-1]
    X = Dense(dense_choice, 'relu')(X)
    from_output_layer = Dense(2 * 8 * 8, activation='softmax')(X)
    from_output_layer = Reshape((2, 8, 8))(from_output_layer)
    model = Model(inputs=input_shape, outputs=[from_output_layer])
    opt = SGD(lr=0.01, momentum=0.9)
    model.compile(optimizer=opt, loss='categorical_crossentropy', metrics=['accuracy'])
    return model





