import numpy as np
from keras import Model
import keras

from Backend.evaluation import legal_moves_evaluation
from Backend.evaluation import simple_positions_test
from Backend.evaluation import white_board_evaluation


# ALL TESTING DONE ONLY FOR THE FIRST HALF OF THE MODEL

# function used to evaluate a keras model on set of tests 
def evaluate_first_half_model(model_path : str, testing_dataset: np.array):

    model =  keras.models.load_model(model_path)    
    
    simple_positions_test.model1_assertion(model)
    
    print('testing color of bitboard')
    white_board_evaluation.white_evaluation(model,testing_dataset)
    
    print('testing percentage of legal moves')
    legal_moves_evaluation.legal_evaluation(model,testing_dataset)






