from Backend import get_data
import numpy
import os
import chess
import pandas as pd


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


def generate_database():
    filename = 'data/top_players.txt'
    with open(filename) as f:
        for line in f:
            get_data.get_pgn_games_from_username(line.split()[1])


def determine_user(filename):
    parts = filename.split('_')
    return parts[2].replace('.csv', '')


def print_df_infos(df):
    print('size = ' + str(df.size))


#
# takes json and make it a pd df
def convert_files_to_df():
    directory = 'Backend/data/pgn_games'
    dfs = []
    users = []
    for filename in os.listdir(directory):
        print(filename)
        users.append(determine_user(filename))
        df = pd.read_json(os.path.join(directory, filename), lines=True)
        dfs.append(df)
    print(' the users are ')
    print(users)
    return dfs, users


# dfs_user is tuple of list of dataframes and users name
# this function takes the dfs and for each element of the list we change the element inside to a series of positions expressed
# in python chess

def convert_game_dfs_to_position_dfs(dfs_users):

    dfs, users = dfs_users
    dfs1 = []
    print(' the users are ')
    print(users)
    for dfs_index, df in enumerate(dfs):
        print('processing the df :')
        print(df.head(1))
        df1 = []
        for index, game in enumerate(df['moves']):
            if game:
                try:
                    white_player = df['players'][index]['white']['user']['name']
                    df1.append((get_data.get_chess_boards_from_pgn(game), users[dfs_index] == white_player))
                except KeyError:
                    print('no user likely means there is an ai so i can just skip this game')
        dfs1.append(df1)

    dfs_users = dfs1, users
    return dfs_users


def convert_to_moves_of_only_one_user(dfs_users):
    dfs, users = dfs_users
    df1 = []
    for df in dfs:



    return dfs_users


def convert_df_of_moves_to_bitboard_array(dfs_users):
    dfs, users = dfs_users
    dfs1 = []
    print(' the users are ')
    print(users)
    for df in dfs:
        print('starting a new df')
        df1 = []
        for game in df:
            for position in game:
                df1.append(split_dims(position))
        dfs1.append(df1)
    dfs_users = dfs1, users
    return dfs_users


def save_bitboard_player(dfs_users):
    for index, value in enumerate(dfs_users[0]):
        filename = 'Backend/data/bit_boards/' + dfs_users[1][index] + '_bitboard.npy'
        numpy.save(filename, value)
        print('finished to save :')
        print(filename)


def generate_data():
    print('getting the df')
    dfs_users = convert_files_to_df()
    print('converting the games to positions')
    dfs_users = convert_game_dfs_to_position_dfs(dfs_users)
    print('converting moves to only one user moves')
    dfs_users = convert_to_moves_of_only_one_user(dfs_users)
    print('converting moves to bit boards')
    dfs_users = convert_df_of_moves_to_bitboard_array(dfs_users)
    print('saving bitboards')
    save_bitboard_player(dfs_users)







