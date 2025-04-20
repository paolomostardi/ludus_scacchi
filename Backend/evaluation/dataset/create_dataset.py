# file used to create a dataset to evualuate the model
# the dataset is structured as follows:
# it is diveded into 3 sections
# 1. architecture of the model
# 2. dataset used to train the model
# 3. evaluation of the model

# the dataset is used to evaluate the model
# and determine how to improve the model


import pandas 


def main ():
    architecture_columns = [ 'main_architecture', 
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
                'brain_hand_both' # determines if the model is used to predict the piece that will move, where the piece will mmove to, or both
               ]
    
    dataset_columns = [
                      'dataset1',
                      'dataset2',
                      'dataset3',
                      'dataset4',
                      'epochs'
                       ]
    evaluation_columns = ['datasetset1_accuracy',
                          'datasetset2_accuracy',
                          'datasetset3_accuracy',
                          'datasetset4_accuracy',
                          'legal_moves_accuracy',
                          'simple_moves_accuracy'
                         ]

    columns = architecture_columns + dataset_columns + evaluation_columns

    
    df = pandas.DataFrame(columns=columns)
    print(df)



if __name__ == '__main__':

    main()








