import keras
import chess
import chess.engine
import random
import numpy
from keras import Sequential
from keras import layers
from keras.layers import Conv2D
from keras.layers import Dense


def random_board(max_depth = 123 ):
    board = chess.Board()
    depth = random.randrange(0,max_depth)

    for _ in range(depth):
        all_moves = list(board.legal_moves)
        random_move = random.choice(all_moves)
        board.push(random_move)

        if board.is_game_over():
            break

    return board


def stockfish(board, depth):
    with chess.engine.SimpleEngine.popen_uci('/content/stockfish') as sf:
        result = sf.analyse(board, chess.engine.Limit(depth=depth))
        score = result['score'].white().score()
    return score


def create_basic_model():
    model = Sequential()
    model.add(Conv2D(10, (1, 1)))
    model.add(Conv2D(10, (1, 1)))
    model.add(Conv2D(10, (1, 1)))
    model.add(Dense(100, 'relu'))


squares_index = {
    'a': 0,
    'b': 1,
    'c': 2,
    'd': 3,
    'e': 4,
    'f': 5,
    'g': 6,
    'h': 7,
}


def square_to_index(square):
    letter = chess.square_name(square)
    return 8 - int(letter[1], squares_index[letter[0]])


def split_dims(board):
    board3d = numpy.zeros((14, 8, 8), dtype= numpy.int8)

    for piece in chess.PIECE_TYPES:
        for square in board.pieces(piece, chess.WHITE):
            idx = numpy.unravel_index(square, (8, 8))
            board3d[piece - 1][7 - idx[0]][idx[1]] = 1
        for square in board.pieces(piece, chess.BLACK):
            idx = numpy.unravel_index(square, (8, 8))
            board3d[piece + 5][7 - idx[0]][idx[1]] = 1




