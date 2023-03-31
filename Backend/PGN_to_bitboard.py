import chess
import chess.engine
import random
import numpy
import pandas as pd

import get_data
import os

from keras import layers
from keras import models
from keras.layers import Conv2D
from keras.layers import Dense

import keras.callbacks as callbacks
import keras.optimizers as optimizers


def random_board(max_depth=100):
    board = chess.Board()
    depth = random.randrange(0, max_depth)

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
    return 8 - int(letter[1]), squares_index[letter[0]]


def split_dims(board):
    board3d = numpy.zeros((14, 8, 8), dtype= numpy.int8)

    for piece in chess.PIECE_TYPES:
        for square in board.pieces(piece, chess.WHITE):
            idx = numpy.unravel_index(square, (8, 8))
            board3d[piece - 1][7 - idx[0]][idx[1]] = 1
        for square in board.pieces(piece, chess.BLACK):
            idx = numpy.unravel_index(square, (8, 8))
            board3d[piece + 5][7 - idx[0]][idx[1]] = 1

    aux = board.turn
    board.turn = chess.WHITE
    for move in board.legal_moves:
        i, j = square_to_index(move.to_square)
        board3d[12][i][j] = 1

    board.turn = chess.BLACK
    for move in board.legal_moves:
        i, j = square_to_index(move.to_square)
        board3d[13][i][j] = 1
    board.turn = aux

    return board3d


def build_model(conv_size, conv_depth):
    board3d = layers.Input(shape=(14, 8, 8))
    x = board3d
    for _ in range(conv_depth):
        x = Conv2D(filters=conv_size, kernel_size= 3, padding= 'same', activation='relu')(x)
    x = layers.Flatten()(x)
    x = Dense(64, 'relu')(x)
    x = Dense(1, 'sigmoid')(x)

    return models.Model(inputs = board3d, outputs = x)


def get_dataset():
    container = numpy.load('dataset.npz')
    b, v = container['b'], container['v']
    v = numpy.asarray(v / abs(v).max() / 2 + 0.5, dtype=numpy.float32)
    return b, v


def test_functions():
    random_boards = random_board(max_depth = 15)
    print(random_boards)

    _3d_board = split_dims(random_boards)

    print(_3d_board)

    model = build_model(32, 4)
    model.summary()


def generate_database():
    filename = 'data/top_players.txt'
    with open(filename) as f:
        for line in f:
            get_data.get_pgn_games_from_username(line.split()[1])


def determine_user(filename):
    parts = filename.split('_')
    return parts[2].replace('.csv','')


def convert_files_to_df():
    directory = 'data/pgn_games'
    dfs = []
    users = []
    for filename in os.listdir(directory):
        print(filename)
        users.append(determine_user(filename))
        df = pd.read_json(os.path.join(directory, filename), lines=True)
        dfs.append(df)
    return dfs, users


def print_df_infos(df):
    print('size = ' + str(df.size))


# the df is structured like something
def filter_moves_by_user(dfs, user):

    return dfs


def df_to_bitboard_array(df):
    bitboard_player = []
    for move in df['moves']:
        if move:
            game = get_data.get_chess_boards_from_pgn(move)
            for position in game:
                bitboard_player.append(split_dims(position))
    return bitboard_player


def save_bitboard_player(bitboard_player, username):
    filename = 'data/bit_boards/something.npy'
    numpy.save(filename, bitboard_player)


def generate_data():
    dfs_users = convert_files_to_df()
    for df_user in dfs_users:
        df_user = filter_moves_by_user(dfs_users[0], dfs_users[1])

    for df_user in dfs_users:
        bitboard = df_to_bitboard_array(df_user[0])
        save_bitboard_player(bitboard, df_user[1])


generate_data()
