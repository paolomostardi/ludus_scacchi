import numpy
import pandas
import chess
import io
import chess.pgn

from Backend.pipeline import count_users_with_most_games_from_lichess_api as count


def number_of_square_to_bitboard_index(square):
    x = square % 8
    y = square // 8
    return x, y


def from_chess_board_create_bit_boards(board):

    board_turn = board.turn
    bit_boards = numpy.zeros((14, 8, 8), dtype=numpy.bool_)

    for piece in chess.PIECE_TYPES:
        for square in board.pieces(piece, chess.WHITE):
            index = numpy.unravel_index(square, (8, 8))
            bit_boards[piece - 1][7 - index[0]][index[1]] = 1
        for square in board.pieces(piece, chess.BLACK):
            index = numpy.unravel_index(square, (8, 8))
            bit_boards[piece + 5][7 - index[0]][index[1]] = 1

    board.turn = chess.WHITE
    for move in board.legal_moves:
        x, y = number_of_square_to_bitboard_index(move.to_square)
        bit_boards[12][y][x] = 1

    board.turn = chess.BLACK
    for move in board.legal_moves:
        x, y = number_of_square_to_bitboard_index(move.to_square)
        bit_boards[13][y][x] = 1

    board.turn = board_turn
    return bit_boards


def from_chess_move_create_bitboard(move):
    from_square = move.from_square
    to_square = move.to_square

    from_matrix = numpy.zeros((8, 8), dtype=numpy.uint8)
    to_matrix = numpy.zeros((8, 8), dtype=numpy.uint8)

    from_matrix[from_square // 8, from_square % 8] = 1
    to_matrix[to_square // 8, to_square % 8] = 1

    return from_matrix[::-1, :], to_matrix[::-1, :]


def get_chess_boards_from_pgn(pgn_string):
    board = chess.Board()
    bitboards = []
    for move in chess.pgn.read_game(io.StringIO(pgn_string)).mainline_moves():
        board.push(move)
        bitboards.append(board.copy())

    return bitboards


def from_json_dataframe_create_list_of_chess_position(json_df, username):
    print(' creating list of chess positions ')
    print(json_df)
    list_of_position_and_is_white_player = []
    for index, game in enumerate(json_df['moves']):
        try:
            if game:
                white_player = json_df['players'][index]['white']['user']['name']
                list_of_position_and_is_white_player.append((get_chess_boards_from_pgn(game), username == white_player))
        except Exception as e:
            print('some error', e)

    return list_of_position_and_is_white_player


def from_list_of_chess_position_split_x_and_y_for_bitboards(df):
    print(' splitting x and y  ')
    list_of_x_position = []
    list_of_y_position = []
    for game_white_tuple in df:
        game = []
        y_game = []

        # the player is white
        if game_white_tuple[1]:

            board = chess.Board()
            game.append((board, True))
            for index, position in enumerate(game_white_tuple[0]):
                # when the index is odd then is black to move
                if index % 2:
                    game.append((position, True))

                else:
                    y_game.append(position)

        # the player is black
        else:
            for index, position in enumerate(game_white_tuple[0]):
                if index % 2:
                    y_game.append(position)
                else:
                    game.append((position, False))

        if len(game) > len(y_game):
            print('reducing size ----- for a for an amount of : ', str(len(game) - len(y_game)) )
            game = game[:len(y_game)]
        elif len(y_game) > len(game):
            print('reducing size ----- for Y for an amount of : ', str(len(game) - len(y_game)) )
            y_game = y_game[:len(game)]

        list_of_x_position.extend(game)
        list_of_y_position.extend(y_game)

    return list_of_x_position, list_of_y_position


def from_list_of_x_and_y_position_create_bitboard(list_of_x_position, list_of_y_position):
    print(' creating bitboards ')
    x_bitboard_list = []
    y_bitboard_list = []
    list_of_white_player = []
    for x_position in list_of_x_position:
        x = from_chess_board_create_bit_boards(x_position[0])
        list_of_white_player.append(x_position[1])
        x_bitboard_list.append(x)

    for y_position in list_of_y_position:
        y = from_chess_move_create_bitboard(y_position.peek())
        y_bitboard_list.append(y)

    print('here is the length of x',len(x_bitboard_list), len(list_of_white_player))
    return x_bitboard_list, y_bitboard_list, list_of_white_player


def from_bitboard_save_file(filepath, username, x_bitboard, y_bitboard, list_of_white):
    print(' saving bitboards files')
    x_filename = filepath + username + '_bitboard.npy'
    y_filename = filepath + username + '_Y_bitboard.npy'
    white_filename = filepath + username + '_white_bitboard.npy'

    numpy.save(x_filename, x_bitboard)
    numpy.save(y_filename, y_bitboard)
    numpy.save(white_filename, list_of_white)


    return


def generate_from_username(username, first_pgn_index):

    user_rating = 1700

    filepath = 'Backend/data/pgn_games/pgn_games_' + str(user_rating) + '/pgn_games_' + username + '.json'
    filepath_to_save = 'Backend/data/bit_boards/bit_boards_' + str(user_rating) + '/'

    json_df = pandas.read_json(filepath, lines=True)
    json_df = json_df.iloc[first_pgn_index:]

    list_of_position = from_json_dataframe_create_list_of_chess_position(json_df, username)
    x_list, y_list = from_list_of_chess_position_split_x_and_y_for_bitboards(list_of_position)

    x_bitboard, y_bitboard, list_of_white = from_list_of_x_and_y_position_create_bitboard(x_list, y_list)
    from_bitboard_save_file(filepath_to_save, username, x_bitboard, y_bitboard, list_of_white)

    return


def generate_from_filename(username, first_pgn_index = 0, filename = None, number = None):

    user_rating = 1700

    filepath = filename
    filepath_to_save = 'Backend/data/bit_boards/bit_boards_' + str(user_rating) + '/'

    json_df = pandas.read_json(filepath, lines=True)

    json_df = json_df.iloc[first_pgn_index:]

    list_of_position = from_json_dataframe_create_list_of_chess_position(json_df, username)
    x_list, y_list = from_list_of_chess_position_split_x_and_y_for_bitboards(list_of_position)

    x_bitboard, y_bitboard, list_of_white = from_list_of_x_and_y_position_create_bitboard(x_list, y_list)
    from_bitboard_save_file(filepath_to_save, username+'_'+str(number), x_bitboard, y_bitboard, list_of_white)

    return
