import numpy as np
from keras import Model
import keras

from Backend.model_evaluation.pipeline import legal_moves_evaluation
from Backend.model_evaluation.pipeline import simple_positions_test
from Backend.model_evaluation.pipeline import white_board_evaluation




"""
ALL TESTING DONE ONLY FOR THE FIRST HALF OF THE MODEL

File used to evaluate a keras model on set of tests 
expects path of the model, x and y. prints the final accuracy results.

So far it tests:
- simple_positions_test -> set of obvious moives to show basic chess understanding 
- white_board_evaluation -> tests if the model changes its behavior when the color bitboard is switched
- legal_moves_evaluation -> tests the percentage of legal moves predicted by the model
- total_accuracy -> tests the final accuracy of the model on the given dataset


The kaggle implementation can be found here: 
https://www.kaggle.com/code/paolomostardi/evaluate-model

"""

def evaluate_first_half_model(model_path : str, testing_dataset: np.array, y : np.array):

    model =  keras.models.load_model(model_path)    
    simple_positions_test.model1_assertion(model)
    print('-----')
    print('testing if the move changes based on the bitboard color')
    white_board_evaluation.white_evaluation(model,testing_dataset)
    print('-----')
    print('testing percentage of legal moves')
    legal_moves_evaluation.legal_evaluation(model,testing_dataset)
    print('-----')
    print('testing total accuracy on the given dataset')
    result = total_accuracy(model_path, testing_dataset, y)

    print(result)


def total_accuracy(model_path : str, testing_dataset : np.array, y):

        model = keras.models.load_model(model_path)

        # fixing the shape if its wrong 

        if y[0].shape == (2,8,8):
            y2 = []
            for i in y:
                y2.append(i[0].flat)
            y = np.array(y2)
        
        
        _, result = model.evaluate(testing_dataset,y)


        return result

def main():
    model_path = 'Backend/data/models/13-01/lichess_13_01.keras'
    testing_dataset = np.load('/media/paolo/aa2/data/bitboards/2013_01/x/chunk_0.npy')
    y = np.load('/media/paolo/aa2/data/bitboards/2013_01/y/chunk_0_y.npy')
    evaluate_first_half_model(model_path,testing_dataset,y)
