import chess
import numpy as np

from keras import models
from keras.models import load_model
from Backend.pipeline import from_PGN_generate_bitboards as gen 

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


def return_top_piece_to_move(fen: str, model: models.Model):
    board = chess.Board(fen)
    x = gen.from_chess_board_create_bit_boards(board)
    x = x.reshape(1, 14, 8, 8)
    prediction = model.predict(x)

    sorted_indices = np.argsort(prediction[0])[::-1]
    sorted_percentages = prediction[0][sorted_indices] * 100

    return sorted_indices, sorted_percentages

def has_legal_moves(board, square):
    piece = board.piece_at(square)
    if piece is None:
        return False 
    for move in board.legal_moves:
        if move.from_square == square:
            return True 

    return False 

def return_best_legal_piece(board: chess.Board, model: models.Model):
    top_indices, _ = return_top_piece_to_move(board.fen(), model)
    for piece in top_indices:
        if has_legal_moves(board, piece):
            return piece


# 12  has  6,4 index 
# 13 - 6,3  
# 11 - 6,5


def transorm_index_to_matrix(index: int):
    matrix = np.zeros((1,8,8))
    x = 7 - index % 8
    y = 7 - index // 8

    print(x,y)

    matrix[0][y][x] = 1

    return matrix

def return_top_squares_given_square_and_board(fen: str, model: models.Model, square: chess.square):
    board = chess.Board(fen)
    x = gen.from_chess_board_create_bit_boards(board)
   

    matrix = transorm_index_to_matrix(square)
    x = np.concatenate((x, matrix), axis=0)
    x = x.reshape(1, 15, 8, 8)
    prediction = model.predict(x)

    sorted_indices = np.argsort(prediction[0])[::-1]
    sorted_percentages = prediction[0][sorted_indices] * 100

    return sorted_indices, sorted_percentages

def return_square_to_move(fen : str, model: models.Model, square: chess.square):
    return_top_squares_given_square_and_board(fen,model,square)

