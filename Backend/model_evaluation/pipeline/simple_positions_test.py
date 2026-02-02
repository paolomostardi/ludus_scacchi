import keras
import chess
import pandas as pd

from Backend.model_evaluation import create_dataset_for_simple_positions as create_simple
from Backend.engine_implementation import engine_creation as engine



import os
"""
63 62 61 60 59 58 57 56
55 54 53 52 51 50 49 48
47 46 45 44 43 42 41 40
39 38 37 36 35 34 33 32
31 30 29 28 27 26 25 24
23 22 21 20 19 18 17 16
15 14 13 12 11 10 9  8
7  6  5  4  3  2  1  0
"""


# file used to test the first part of the model on simple positions
# this is useful to see if the model has a basic understunding of chess 

    
def model1_assertion(model1, df_str = ''):

    if (df_str == ''):
        if (not os.path.exists(os.getcwd() + 'Backend/model_evaluation/simple_positions.csv')):
            # creates the dataset with the positions 
            create_simple.main()
        df = pd.read_csv(os.getcwd() + '/Backend/model_evaluation/simple_positions.csv')
        
    else:
        df = pd.read_csv(df_str)


    
    counter = 0
    counter2 = 0

    df = df.iterrows()

    for i in df:
        
        position,move = i[1][0],i[1][1]
        
        index = engine.return_best_legal_piece(position,model1)
        counter2 += 1
        if index == move:
            counter += 1
        print(position,'------------ Expected move: ',move,' Acutal move: ',index)

    print('Positions guessed correctly: ',str(counter),', out of  ', counter2)


def main():
    model = keras.models.load_model('Backend/data/models/gm_model_white_legal_moves/gm_model_chunk_9.keras')
    model1_assertion(model)

    model = keras.models.load_model('Backend/data/models/13-01/lichess_13_01.keras')
    model1_assertion(model)

    model = keras.models.load_model('Backend/data/models/14_07/gm_dataset_squeezenet.keras')
    model1_assertion(model)

    model = keras.models.load_model('Backend/data/models/gm_model_white/gm_model_chunk_9.keras')
    model1_assertion(model)

    