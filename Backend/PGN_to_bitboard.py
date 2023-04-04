from Backend import get_data
import numpy
import os
import chess
import pandas as pd
import time

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
    board3d = numpy.zeros((14, 8, 8), dtype=numpy.int8)

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


def move_to_matrix(move):
    from_square = move.from_square
    to_square = move.to_square

    from_matrix = numpy.zeros((8, 8), dtype=numpy.uint8)
    to_matrix = numpy.zeros((8, 8), dtype=numpy.uint8)

    from_matrix[from_square // 8, from_square % 8] = 1
    to_matrix[to_square // 8, to_square % 8] = 1

    return from_matrix, to_matrix


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
    dfs1 = []
    y = []
    for df in dfs:
        df1 = []
        y1 = []
        for game_white_tuple in df:
            game = []
            y_game = []
            # the player is white
            if game_white_tuple[1]:

                board = chess.Board()
                print('white player')
                game.append(board)
                for index, position in enumerate(game_white_tuple[0]):
                    # when the index is odd then is black to move
                    if index % 2:
                        game.append(position)
                    else:

                        y_game.append(position)

            # the player is black
            else:
                for index, position in enumerate(game_white_tuple[0]):
                    if index % 2:
                        y_game.append(position)
                    else:
                        game.append(position)

            df1.append(game)
            y1.append(y_game)

        dfs1.append(df1)
        y.append(y1)

    dfs_users = dfs1, users
    return dfs_users, y


def convert_df_of_moves_to_bitboard_array(dfs_users, y):
    dfs, users = dfs_users
    dfs1 = []
    ys = []
    print(' the users are ')
    print(users)
    for df, user_y in enumerate(y):
        y1 = []
        df1 = []
        for i_game, game in enumerate(user_y):
            for i_position, position in enumerate(game):
                y1.append(move_to_matrix(position.peek()))
                g = split_dims(dfs[df][i_game][i_position])
                df1.append(g)
        ys.append(y1)
        dfs1.append(df1)
    dfs_users = dfs1, users
    return dfs_users, ys


def save_bitboard_player(dfs_users, y):
    for index, value in enumerate(dfs_users[0]):
        filename = 'Backend/data/bit_boards/' + dfs_users[1][index] + '_bitboard.npy'
        numpy.save(filename, value)
        print('finished to save :')
        print(filename)
        filename = 'Backend/data/bit_boards/' + dfs_users[1][index] + '_Y_bitboard.npy'
        numpy.save(filename, y[index])


def generate_data():
    print('getting the df')
    dfs_users = convert_files_to_df()
    print('converting the games to positions')
    dfs_users = convert_game_dfs_to_position_dfs(dfs_users)
    print('converting moves to only one user moves')
    dfs_users, y = convert_to_moves_of_only_one_user(dfs_users)
    print('converting moves to bit boards')
    dfs_users = convert_df_of_moves_to_bitboard_array(dfs_users, y)
    print('saving bitboards')
    save_bitboard_player(dfs_users, y)


def test_y(x, y):
    legal = 0
    illegal = 0
    number_out = 0
    for index_game, game in enumerate(x):

        for index_position, position in enumerate(game):
            try:
                board = position.copy()
                board.push(y[index_game][index_position].peek())
                legal += 1
                print('legal --------------------------------------------------------------')

            except AssertionError:
                print('illegal move detected')
                print('move is ')
                print(y[index_game][index_position].peek())

                print('board is ')
                print(board.fen())

                print(' y board is ')
                print(y[index_game].fen())
                illegal += 1

                time.sleep(1)
                print('index is : ')
                print(index_game)

            except IndexError:
                print(' finish i guess ? ')
                number_out +=1

    print(legal)
    print(illegal)
    print(number_out)
    return legal, illegal


