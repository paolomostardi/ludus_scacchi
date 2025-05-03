import pandas as pd
import os
from architecture_info import architecture_info


# this data has been inserted 3 / 05 / 2025
# it is the begging data of 3 architectures 
# the code can be found in the folder models/architectures
# resent50_implementation.py, inception_chess.py, squeeze_net.py


# Update the instantiation of architecture_info objects to match the class definition
resnet = architecture_info(
    main_architecture="ResNet",
    amount_of_parameters=47415938,
    amount_of_layers=177,
    residual_network=True,
    dropout_rate=0,
    batch_normalization=True,
    activation_function="relu",
    learning_rate=0.01,
    optimizer="SDG",
    loss_function="categorical_crossentropy",
    batch_size=64,
    weight_initialization="he_normal",
    input_shape=15,
    color_to_move_representation="full",
    brain_hand_both="brain",
    momentum=0.9
)

inception_v3 = architecture_info(
    main_architecture="Inception_v3",
    amount_of_parameters=21935360,
    amount_of_layers=338,
    residual_network=False,
    dropout_rate=0,
    batch_normalization=True,
    activation_function="relu",
    learning_rate=0.01,
    optimizer="SDG",
    loss_function="categorical_crossentropy",
    batch_size=64,
    weight_initialization="he_normal",
    input_shape=15,
    color_to_move_representation="full",
    brain_hand_both="brain",
    momentum=0.9
)

squeezenet = architecture_info(
    main_architecture="SqueezeNet",
    amount_of_parameters=1516418,
    amount_of_layers=38,
    residual_network=False,
    dropout_rate=0,
    batch_normalization=False,
    activation_function="relu",
    learning_rate=0.01,
    optimizer="SDG",
    loss_function="categorical_crossentropy",
    batch_size=64,
    weight_initialization="he_normal",
    input_shape=15,
    color_to_move_representation="full",
    brain_hand_both="brain",
    momentum=0.9
)

# Create a list of dictionaries for the DataFrame
data = [
    vars(resnet),
    vars(inception_v3),
    vars(squeezenet)
]

# Create a pandas DataFrame
df = pd.DataFrame(data)

# Define the output directory and file path
output_dir = os.path.join(os.getcwd(), "Backend/evaluation/dataset/separate_datasets")
os.makedirs(output_dir, exist_ok=True)
output_file = os.path.join(output_dir, "architecture_dataset.csv")

# Save the DataFrame to a CSV file
df.to_csv(output_file, index=False)

print(f"Dataset saved to {output_file}")
print(df.head())