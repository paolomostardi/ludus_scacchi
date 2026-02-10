import os
import sys
import pandas as pd
import numpy as np
from keras.models import Model
from keras.layers import Dropout, BatchNormalization, Add, Activation

# Add path to model architectures
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../model_architecture/implementation')))

# Import the specific model - in a real scenario this might be dynamic or configured
try:
    from experimental_architecture1 import experimental_architecture1
except ImportError as e:
    print(f"Could not import model: {e}")
    # Fallback or exit? For the purpose of this script we expect it to exist.

def get_optimizer_details(model):
    opt = model.optimizer
    config = opt.get_config()
    
    name = opt.__class__.__name__
    lr = config.get('learning_rate', 0.01)
    if isinstance(lr, float) is False: # Handle non-float (e.g. schedules), though here it's likely float
        lr = float(lr)
        
    momentum = config.get('momentum', 0)
    
    return name, lr, momentum

def has_layer_type(model, layer_type):
    for layer in model.layers:
        if isinstance(layer, layer_type):
            return True
    return False

def get_activation(model):
    # Heuristic: find the most common activation or the one used in conv blocks
    activations = []
    for layer in model.layers:
        if hasattr(layer, 'activation'):
            # layer.activation is a function, get its name
            if hasattr(layer.activation, '__name__'):
                activations.append(layer.activation.__name__)
    
    if not activations:
        return 'unknown'
    
    # Filter out 'linear' which is default for Conv2D
    non_linear_activations = [a for a in activations if a != 'linear']
    if non_linear_activations:
        return max(set(non_linear_activations), key=non_linear_activations.count)
        
    # Return most frequent (likely relu)
    return max(set(activations), key=activations.count)

def get_weight_init(model):
    # Heuristic: check first conv/dense
    for layer in model.layers:
        if hasattr(layer, 'kernel_initializer'):
            init = layer.kernel_initializer
            if hasattr(init, 'class_name'):
                return init.class_name
            if hasattr(init, '__class__'):
                return init.__class__.__name__
    return 'unknown'

def insert_model_info(
    model_func,
    csv_path,
    name_kaggle,
    main_architecture = '',
    color_representation='full',
    brain_hand='brain',
    batch_size=64
):
    # Instantiate model to inspect it
    model = model_func()
    
    
    df = pd.read_csv(csv_path)
    
    # Calculate new ID
    if not df.empty and 'ID' in df.columns and not pd.isna(df['ID'].max()):
        new_id = int(df['ID'].max()) + 1
    else:
        new_id = 1
        
    # Extract details
    amount_of_parameters = model.count_params()
    amount_of_layers = len(model.layers)
    
    # Residual? Check for Add layers
    residual_network = has_layer_type(model, Add)
    
    dropout_rate = 0
    # Find first dropout to get rate data? Or just check existence.
    # CSV want a rate number. 
    for layer in model.layers:
        if isinstance(layer, Dropout):
            dropout_rate = layer.rate
            break # Just get first one found
            
    is_batch_norm = has_layer_type(model, BatchNormalization)
    activation_function = get_activation(model)
    
    opt_name, lr, momentum = get_optimizer_details(model)
    loss_function = model.loss
    
    weight_init = get_weight_init(model)
    
    input_shape_tuple = model.input_shape[1:] if model.input_shape[0] is None else model.input_shape

    # Format input shape as '15' or '(15, 8, 8)'. 
    # This refers to the first dimension (channels), how many features are used to rapresent the board.
    # So 12 board for piecese and then for castling legal moves enpassant and so on.
    input_shape_val = input_shape_tuple[0]
    
    new_row = {
        'ID': new_id,
        'main_architecture': main_architecture,
        'name_architecture_kaggle': name_kaggle,
        'amount_of_parameters': amount_of_parameters,
        'amount_of_layers': amount_of_layers,
        'residual_network': residual_network,
        'dropout_rate': dropout_rate,
        'batch_normalization': is_batch_norm,
        'activation_function': activation_function,
        'learning_rate': lr,
        'optimizer': opt_name,
        'loss_function': loss_function,
        'momentum': momentum,
        'batch_size': batch_size,
        'weight_initialization': weight_init,
        'input_shape': input_shape_val,
        'color_to_move_representation': color_representation,
        'brain_hand_both': brain_hand
    }
    
    print("New Row Data:")
    print(new_row)
    
    # Append to dataframe
    new_df = pd.DataFrame([new_row])
    df = pd.concat([df, new_df], ignore_index=True)
    df.to_csv(csv_path, index=False)
    print(f"Successfully added model info to {csv_path}")

if __name__ == "__main__":
    csv_file = os.path.join(os.path.dirname(__file__), 'cvs/architecture_dataset.csv')
    
    # Configuration for the new model
    # Adding experimental architecture
    # Some info added by hand 
    insert_model_info(
        model_func=experimental_architecture1,
        csv_path=csv_file,
        main_architecture='Experimental_ResNet_Custom',
        name_kaggle='Experimental_Arch1',
        color_representation='full',
        brain_hand='brain', 
        batch_size=64   
    )
