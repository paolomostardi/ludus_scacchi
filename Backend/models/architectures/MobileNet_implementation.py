
import os
import warnings
from keras.layers import ReLU
from keras import layers


def hard_sigmoid(x):
    return ReLU(6.)(x + 3.) * (1. / 6.)


def hard_swish(x):
    return layers.Multiply()([layers.Activation(hard_sigmoid)(x), x])


def _depth(v, divisor=8, min_value=None):
    if min_value is None:
        min_value = divisor
    new_v = max(min_value, int(v + divisor / 2) // divisor * divisor)
    # Make sure that round down does not go down by more than 10%.
    if new_v < 0.9 * v:
        new_v += divisor
    return new_v


def _se_block(inputs, filters, se_ratio, prefix):

    x = layers.GlobalAveragePooling2D(name=prefix + 'squeeze_excite/AvgPool')(inputs)
    x = layers.Conv2D(_depth(filters * se_ratio), kernel_size=1, padding='same', name=prefix + 'squeeze_excite/Conv')(x)
    x = layers.ReLU(name=prefix + 'squeeze_excite/Relu')(x)
    x = layers.Conv2D(filters, kernel_size=1, padding='same', name=prefix + 'squeeze_excite/Conv_1')(x)
    x = layers.Activation(hard_sigmoid)(x)
    if backend.backend() == 'theano':
        # For the Theano backend, we have to explicitly make
        # the excitation weights broadcastable.
        x = layers.Lambda(
            lambda br: backend.pattern_broadcast(br, [True, True, True, False]),
            output_shape=lambda input_shape: input_shape,
            name=prefix + 'squeeze_excite/broadcast')(x)
    x = layers.Multiply(name=prefix + 'squeeze_excite/Mul')([inputs, x])
    return x


def _inverted_res_block(x, expansion, filters, kernel_size, stride,se_ratio, activation, block_id):

    channel_axis = 1 if backend.image_data_format() == 'channels_first' else -1
    shortcut = x
    prefix = 'expanded_conv/'
    infilters = backend.int_shape(x)[channel_axis]

    if block_id:
        # Expand
        prefix = 'expanded_conv_{}/'.format(block_id)
        x = layers.Conv2D(_depth(infilters * expansion), kernel_size=1, padding='same', use_bias=False, name=prefix + 'expand')(x)
        x = layers.BatchNormalization(axis=channel_axis, epsilon=1e-3, momentum=0.999, name=prefix + 'expand/BatchNorm')(x)
        x = layers.Activation(activation)(x)

    if stride == 2:
        x = layers.ZeroPadding2D(padding=correct_pad(backend, x, kernel_size),name=prefix + 'depthwise/pad')(x)
    x = layers.DepthwiseConv2D(kernel_size,strides=stride,padding='same' if stride == 1 else 'valid',use_bias=False,name=prefix + 'depthwise')(x)
    x = layers.BatchNormalization(axis=channel_axis,epsilon=1e-3,momentum=0.999,name=prefix + 'depthwise/BatchNorm')(x)
    x = layers.Activation(activation)(x)

    if se_ratio:
        x = _se_block(x, _depth(infilters * expansion), se_ratio, prefix)

    x = layers.Conv2D(filters,kernel_size=1,padding='same',use_bias=False,name=prefix + 'project')(x)
    x = layers.BatchNormalization(axis=channel_axis,epsilon=1e-3,momentum=0.999,name=prefix + 'project/BatchNorm')(x)

    if stride == 1 and infilters == filters:
        x = layers.Add(name=prefix + 'Add')([shortcut, x])
    return x


def MobileNetV3():

    # Determine proper input shape and default size.
    # If both input_shape and input_tensor are used, they should match
       # If input_shape is None, infer shape from input_tensor

    row_axis, col_axis = (0, 1)
    row_axis, col_axis = (1, 2)
    activation = ReLU


    x = layers.ZeroPadding2D(padding=,name='Conv_pad')(img_input)
    x = layers.Conv2D(16,kernel_size=3,strides=(2, 2),paddding='valid',use_bias=False,name='Conv')(x)
    x = layers.BatchNormalization(axis=channel_axis,epsilon=1e-3,momentum=0.999,name='Conv/BatchNorm')(x)
    x = layers.Activation(activation)(x)

    x = stack_fn(x, kernel, activation, se_ratio)

    last_conv_ch = _depth(backend.int_shape(x)[channel_axis] * 6)

    x = layers.Conv2D(last_conv_ch,kernel_size=1,padding='same',use_bias=False,name='Conv_1')(x)
    x = layers.BatchNormalization(axis=channel_axis,epsilon=1e-3,momentum=0.999,name='Conv_1/BatchNorm')(x)
    x = layers.Activation(activation)(x)
    x = layers.Conv2D(last_point_ch,kernel_size=1,padding='same',name='Conv_2')(x)
    x = layers.Activation(activation)(x)
        if dropout_rate > 0:
            x = layers.Dropout(dropout_rate)(x)
        x = layers.Conv2D(classes,
                          kernel_size=1,
                          padding='same',
                          name='Logits')(x)
        x = layers.Flatten()(x)
        x = layers.Softmax(name='Predictions/Softmax')(x)
    else:
        if pooling == 'avg':
            x = layers.GlobalAveragePooling2D(name='avg_pool')(x)
        elif pooling == 'max':
            x = layers.GlobalMaxPooling2D(name='max_pool')(x)
    # Ensure that the model takes into account
    # any potential predecessors of `input_tensor`.
    if input_tensor is not None:
        inputs = keras_utils.get_source_inputs(input_tensor)
    else:
        inputs = img_input

    # Create model.
    model = models.Model(inputs, x, name='MobilenetV3' + model_type)

    return model
