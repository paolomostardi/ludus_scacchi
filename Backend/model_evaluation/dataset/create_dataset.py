import pandas
import os

def main():

    
    dataset_columns = [
                      '2013_01_dataset',
                      '2013_04_dataset',
                      '2014_07_dataset',
                      'Gm_dataset',
                      '1700_dataset',
                      'epochs'
                    ]
    
    evaluation_columns = [
                          col + '_accuracy' for col in dataset_columns if col != 'epochs'
                        ] + [
                          'legal_moves_accuracy',
                          'simple_moves_accuracy'
                        ]

    # Create a subfolder for the datasets
    output_folder = 'Backend/model_evaluation/dataset/separate_datasets'
    os.makedirs(output_folder, exist_ok=True)

    # Load architecture dataset
    architecture_file = os.path.join(output_folder, 'architecture_dataset.csv')
    architecture_df = pandas.read_csv(architecture_file)

    # Extract architecture columns
    architecture_columns = architecture_df.columns.tolist()

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