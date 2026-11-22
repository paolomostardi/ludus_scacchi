from keras import Model, layers

from .source_resnet import source_resnet


def source_resnet_dense(conv_filters=64, residual_blocks=6, dense_units=128, *, backbone=None):
    """Add a dense correction to the source logits of a ResNet."""
    if backbone is None:
        backbone = source_resnet(conv_filters=conv_filters, residual_blocks=residual_blocks)
    logits = backbone.get_layer("policy_head").input
    features = backbone.get_layer("square_logits").input
    features = layers.Flatten(name="dense_board_features")(features)
    features = layers.Dense(dense_units, activation="relu", name="dense_policy_hidden")(features)
    correction = layers.Dense(64, kernel_initializer="zeros", bias_initializer="zeros",
                              name="dense_policy_correction")(features)
    output = layers.Softmax(name="dense_policy_head")(layers.Add()([logits, correction]))
    return Model(backbone.inputs, output, name=f"Ludus-Source-ResNet-{residual_blocks}x{conv_filters}-Dense{dense_units}")
