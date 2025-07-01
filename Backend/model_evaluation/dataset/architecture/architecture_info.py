
# this class is used to store the architecture information of a model
# one of the 3 parts of the main dataset 

class architecture_info:
    def __init__(self, main_architecture, amount_of_parameters, amount_of_layers, residual_network, dropout_rate,
                 batch_normalization, activation_function, learning_rate, optimizer, loss_function, batch_size,
                 weight_initialization, input_shape, color_to_move_representation, brain_hand_both, momentum):
        self.main_architecture = main_architecture
        self.amount_of_parameters = amount_of_parameters
        self.amount_of_layers = amount_of_layers
        self.residual_network = residual_network
        self.dropout_rate = dropout_rate
        self.batch_normalization = batch_normalization
        self.activation_function = activation_function
        self.learning_rate = learning_rate
        self.optimizer = optimizer
        self.loss_function = loss_function
        self.momentum = momentum        
        self.batch_size = batch_size
        self.weight_initialization = weight_initialization
        self.input_shape = input_shape
        self.color_to_move_representation = color_to_move_representation
        self.brain_hand_both = brain_hand_both