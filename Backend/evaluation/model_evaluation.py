import numpy as np
from keras import Model
import keras

from Backend.evaluation import legal_moves_evaluation
from Backend.evaluation import simple_positions_test
from Backend.evaluation import check_dataset_legal 
from Backend.evaluation import white_board_evaluation


# ALL TESTING DONE ONLY FOR THE FIRST HALF OF THE MODEL

# function used to evaluate a keras model on set of tests 
def evaluate_first_half_model(model_path : str, testing_dataset: np.array):

    check_dataset_legal.check_dataset_has_all_legal_moves(testing_dataset)
    model =  keras.models.load_model(model_path)
    
    simple_positions_test.model1_assertion(model)
    white_board_evaluation.white_evaluation(model,testing_dataset)
    legal_moves_evaluation.legal_evaluation(model,testing_dataset)






