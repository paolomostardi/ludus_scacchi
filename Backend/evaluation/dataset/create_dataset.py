import pandas
import os


def main():
    architecture_columns = [ 
                'main_architecture', 
                'amount_of_parameters',
                'amount_of_layers',
                'residual_network',
                'dropout_rate',
                'batch_normalization',
                'activation_function',
                'learning_rate',
                'optimizer',
                'loss_function',
                'batch_size',
                'weight_initialization',
                'input_shape',
                'color_to_move_rapresentation',
                'brain_hand_both' # determines if the model is used to predict the piece that will move, where the piece will mmove to, or both
               ]
    
    dataset_columns = [
                      '2013_01_dataset',
                      '2013_04_dataset',
                      '2014_07_dataset',
                      'Gm_dataset',
                      '1700_dataset',
                      'epochs'
                    ]
    
    evaluation_columns = [
                          'datasetset2_accuracy',
                          'datasetset3_accuracy',
                          'datasetset4_accuracy',
                          'legal_moves_accuracy',
                          'simple_moves_accuracy'
                         ]

    # Create a subfolder for the datasets
    output_folder = 'Backend/evaluation/dataset/separate_datasets'
    os.makedirs(output_folder, exist_ok=True)

    # Create individual datasets
    architecture_df = pandas.DataFrame(columns=architecture_columns)
    architecture_df.to_csv(f'{output_folder}/architecture_dataset.csv', index=False)

    dataset_df = pandas.DataFrame(columns=dataset_columns)
    dataset_df.to_csv(f'{output_folder}/dataset_columns_dataset.csv', index=False)

    evaluation_df = pandas.DataFrame(columns=evaluation_columns)
    evaluation_df.to_csv(f'{output_folder}/evaluation_dataset.csv', index=False)

    # Create combined dataset
    combined_columns = architecture_columns + dataset_columns + evaluation_columns
    combined_df = pandas.DataFrame(columns=combined_columns)
    combined_df.to_csv(f'{output_folder}/combined_dataset.csv', index=False)


if __name__ == '__main__':
    main()