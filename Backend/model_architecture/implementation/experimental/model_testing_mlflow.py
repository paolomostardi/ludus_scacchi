from keras import Input, Model
from keras import layers
from keras.optimizers import SGD


def basic_block(input_tensor, filters, stride=1, bn_axis=-1):
    """Lightweight residual block tailored for 8x8 chess bitboards."""
    x = layers.Conv2D(
        filters,
        (3, 3),
        strides=(stride, stride),
        padding="same",
        kernel_initializer="he_normal",
    )(input_tensor)
    x = layers.BatchNormalization(axis=bn_axis)(x)
    x = layers.Activation("relu")(x)

    x = layers.Conv2D(
        filters,
        (3, 3),
        strides=(1, 1),
        padding="same",
        kernel_initializer="he_normal",
    )(x)
    x = layers.BatchNormalization(axis=bn_axis)(x)

    shortcut = input_tensor
    if stride != 1 or input_tensor.shape[-1] != filters:
        shortcut = layers.Conv2D(
            filters,
            (1, 1),
            strides=(stride, stride),
            padding="same",
            kernel_initializer="he_normal",
        )(input_tensor)
        shortcut = layers.BatchNormalization(axis=bn_axis)(shortcut)

    x = layers.Add()([x, shortcut])
    x = layers.Activation("relu")(x)
    return x


def model_testing_mlflow(conv_filters=32, upsample_factor=4):
    """Compact experimental-style model for fast MLflow pipeline testing."""
    bn_axis = -1
    input_layer = Input(shape=(15,8,8), name="input_1")

    x = layers.UpSampling2D(size=(upsample_factor, upsample_factor))(input_layer)
    x = layers.Conv2D(
        conv_filters,
        (3, 3),
        padding="same",
        activation="relu",
        kernel_initializer="he_normal",
        name="conv_stem",
    )(x)
    x = layers.BatchNormalization(axis=bn_axis)(x)
    x = layers.Activation("relu")(x)

    x = basic_block(x, conv_filters * 2, stride=2, bn_axis=bn_axis)
    x = basic_block(x, conv_filters * 2, bn_axis=bn_axis)

    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dense(conv_filters * 2, activation="relu", name="dense_head")(x)
    output = layers.Dense(64, activation="softmax", name="policy_head")(x)

    model = Model(inputs=input_layer, outputs=output, name="model_testing_mlflow")

    optimizer = SGD(learning_rate=0.01, momentum=0.9)
    model.compile(optimizer=optimizer, loss="categorical_crossentropy", metrics=["accuracy"])
    return model
