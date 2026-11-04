from keras import Input, Model, layers
from keras.optimizers import SGD

from .model_testing_mlflow import basic_block


def source_resnet(conv_filters=64, residual_blocks=4):
    """Predict a source square from 15 board planes."""
    board = Input(shape=(15, 8, 8), name="board")
    x = layers.Permute((2, 3, 1))(board)
    x = layers.Conv2D(conv_filters, 3, padding="same", kernel_initializer="he_normal")(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation("relu")(x)
    for _ in range(residual_blocks):
        x = basic_block(x, conv_filters)

    x = layers.Conv2D(1, 1, name="square_logits")(x)
    output = layers.Softmax(name="policy_head")(layers.Flatten()(x))
    model = Model(board, output, name=f"Ludus-Source-ResNet-{residual_blocks}x{conv_filters}")
    model.compile(
        optimizer=SGD(learning_rate=0.01, momentum=0.9),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model
