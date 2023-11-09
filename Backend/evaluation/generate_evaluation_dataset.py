import chess 
from Backend.pipeline import from_PGN_generate_bitboards as gen
from keras.models import Model
import numpy as np

def from_fen_to_answer(fen: str, model : Model):
    board = chess.Board(fen)
    x = gen.from_chess_board_create_bit_boards(board)
    x = x.reshape(1,14,8,8)
    prediction = model.predict(x)

    top3_indices = np.argsort(prediction[0])[-3:][::-1]
    top3_percentages = prediction[0][top3_indices] * 100

    return top3_indices, top3_percentages

def generate_first_dataset():
    
    return 

def make_0_63(couple):
    return couple[0] * 8 + couple[1]

def create_array(index):
    array = np.zeros(64)
    array[index] = 1
    return array



def change_y(y):

    print('CHANGING DATA ')
    
    y2 = []
    y3 = []

    for i in y:
        y2.append(make_0_63(i[0]))
    for i in y2:
        y3.append(np.array(create_array(i)))
    
    return y

