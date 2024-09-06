import numpy as np
from keras import Model
import keras

from Backend.evaluation import legal_moves_evaluation
from Backend.evaluation import simple_positions_test
from Backend.evaluation import white_board_evaluation


# ALL TESTING DONE ONLY FOR THE FIRST HALF OF THE MODEL

# function used to evaluate a keras model on set of tests 
def evaluate_first_half_model(model_path : str, testing_dataset: np.array, y : np.array):

    model =  keras.models.load_model(model_path)    
    simple_positions_test.model1_assertion(model)
    print('testing if the move changes based on the bitboard color')
    white_board_evaluation.white_evaluation(model,testing_dataset)
    print('testing percentage of legal moves')
    legal_moves_evaluation.legal_evaluation(model,testing_dataset)
    result = total_accuracy(model_path, testing_dataset, y)
    print(result)


def total_accuracy(model_path : str, testing_dataset : np.array, y):

        model = keras.models.load_model(model_path)
        _, result = model.evaluate(testing_dataset, y)

        return result


def main():
    model_path = 'Backend/data/models/13-01/lichess_13_01.keras'
    testing_dataset = np.load('/media/paolo/aa2/data/bitboards/2013_01/x/chunk_0.npy')
    y = np.load('/media/paolo/aa2/data/bitboards/2013_01/y/chunk_0_y.npy')
    evaluate_first_half_model(model_path,testing_dataset,y)
