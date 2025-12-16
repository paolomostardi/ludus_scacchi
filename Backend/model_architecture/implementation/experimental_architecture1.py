from keras import layers, Model
from keras import Input
from keras.optimizers import SGD

# Experimental architecture 
# This code defines an experimental convolutional neural network architecture with the following purposes:
#
# 1 - experimental_architecture1:
#     - Takes a single input of shape (15, 8, 8)
#     - Resizes the input (upsampling) to avoid aggressive padding/pooling on small dimensions
#     - Uses a ResNet-like structure with 'BasicBlock' (two 3x3 convs) instead of Bottleneck
#     - Focuses on 3x3 and 1x1 filters
#     - Uses Global Average Pooling instead of Flatten
#     - Outputs a probability distribution over 64 squares (dense softmax)
#
# Each model uses ReLU activations, SGD optimizer with momentum 0.9, 
# and categorical crossentropy loss.

def basic_block(input_tensor, filters, stride=1):
    """
    A basic residual block with two 3x3 convolutions.
    """
    bn_axis = 1  # Assuming channels_first based on (15, 8, 8) input shape usage in other files
    
    # First Conv
    x = layers.Conv2D(filters, (3, 3), strides=(stride, stride), padding='same', kernel_initializer='he_normal')(input_tensor)
    x = layers.BatchNormalization(axis=bn_axis)(x)
    x = layers.Activation('relu')(x)

    # Second Conv
    x = layers.Conv2D(filters, (3, 3), strides=(1, 1), padding='same', kernel_initializer='he_normal')(x)
    x = layers.BatchNormalization(axis=bn_axis)(x)

    # Shortcut connection
    shortcut = input_tensor
    if stride != 1 or input_tensor.shape[bn_axis] != filters:
        shortcut = layers.Conv2D(filters, (1, 1), strides=(stride, stride), kernel_initializer='he_normal')(input_tensor)
        shortcut = layers.BatchNormalization(axis=bn_axis)(shortcut)

    x = layers.add([x, shortcut])
    x = layers.Activation('relu')(x)
    return x

def experimental_architecture1():
    bn_axis = 1
    input_shape = (15, 8, 8) # Channels first suggested by usage

    input_layer = Input(shape=input_shape, name='input_1')

    # Resize/Upsample to allow for downsampling blocks
    # 8x8 -> 32x32
    x = layers.UpSampling2D(size=(4, 4))(input_layer)

    # Initial Conv
    x = layers.Conv2D(64, (3, 3), strides=(1, 1), padding='same', kernel_initializer='he_normal', name='conv1')(x)
    x = layers.BatchNormalization(axis=bn_axis, name='bn_conv1')(x)
    x = layers.Activation('relu')(x)

    # Stages (using basic blocks)
    # Block 1
    x = basic_block(x, 64)
    x = basic_block(x, 64)
    
    # Block 2 (Downsample)
    x = basic_block(x, 128, stride=2)
    x = basic_block(x, 128)

    # Block 3 (Downsample)
    x = basic_block(x, 256, stride=2)
    x = basic_block(x, 256)
    x = basic_block(x, 256)

    # Global Average Pooling
    x = layers.GlobalAveragePooling2D()(x)
    
    # Final Dense
    x = layers.Dense(64, activation='softmax', name='fc64')(x)

    model = Model(inputs=[input_layer], outputs=[x])

    opt = SGD(learning_rate=0.01, momentum=0.9)
    model.compile(optimizer=opt, loss='categorical_crossentropy', metrics=['accuracy'])

    return model
