import numpy as np
from keras import Model
import keras
from Backend.data_pipeline import reverse_bitboard as r
import chess

# this file checks how many moves played by the model are legal.

def give_max(board):
    max_switch = max(range(len(board)), key=board.__getitem__)
    return max_switch

def legal_evaluation(model : Model, testing_dataset : np.array):    

    predictions = model.predict(testing_dataset)

    counter = 0

    for index, prediction in enumerate(predictions):
        board = r.from_bitboard_return_chess_board(testing_dataset[index])
        prediction = give_max(prediction)
        prediction = r.transform_index(prediction)
   
        piece_moves = [move for move in board.legal_moves if move.from_square == prediction]

        if piece_moves:
            counter += 1

    print(counter, len(predictions))
            

if __name__ == "__main__":
    model = keras.models.load_model('Backend/data/models/gm_model_white/gm_model_chunk_9.keras')
    dataset = np.load('chunk_0.npy')
    legal_evaluation(model, dataset[1:2])


def main(start, finish):
    model = keras.models.load_model('Backend/data/models/gm_model_white_legal_moves/gm_model_chunk_9.keras')
    dataset = np.load('chunk_10.npy')
    legal_evaluation(model, dataset[start:finish])


