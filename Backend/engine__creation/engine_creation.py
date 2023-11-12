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

    from_square = square
    from_square = (from_square - (from_square % 8)) + (7 - from_square % 8)

    square = from_square

    piece = board.piece_at(square)
    if piece is None:
        return False 
    for move in board.legal_moves:
        if move.from_square == square:
            print(move)
            print(move)
            return True 

    return False 

def return_best_legal_piece(fen, model: models.Model):
    top_indices, _ = return_top_piece_to_move(fen, model)
    board = chess.Board(fen)
    for piece in top_indices:
        if has_legal_moves(board, piece):
            print(piece)
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

    print(matrix)

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


def legal_move_given_square(board : chess.Board, from_square, to_square):

    
    from_square = (from_square - (from_square % 8)) + (7 - from_square % 8)
    for move in board.legal_moves:
        
        
        if move.from_square == from_square and move.to_square == to_square:
            
            print(from_square)
            print(move)
            print(board)
            board.push(move)
            print(board)
            return True       


def find_most_likely_legal_move(board, from_square, list_squares):

    for to_square in list_squares:
        if legal_move_given_square(board, from_square, to_square):
            return to_square 


def return_square_to_move(fen : str, model: models.Model, square: chess.square):
    sorted_indices, sorted_percentages = return_top_squares_given_square_and_board(fen,model,square)
    return find_most_likely_legal_move(chess.Board(fen),square,sorted_indices)


def engine(fen: str, model1, model2):
    square = return_best_legal_piece(fen,model1)
    print('INITIAL from square is ',square)

    return return_square_to_move(fen,model2,square)

