import numpy
import pandas
import chess
import io
import chess.pgn
import os
import re
import csv

from Backend.pipeline import count_users_with_most_games_from_lichess_api as count
from Backend.pipeline import create_second_dataset as second

def move_and_position_to_bitboard(move : str, position): 
    position = chess.Board(position)
    position.push_san(move)
    
    return from_chess_move_create_bitboard(position.peek())

# expecting df with columns:
# 'position','move' 

def from_df_create_move_bitboard(size, moves, positions, start, chunk_number):
    bitboard_save = []
    moves = moves.iloc[start:start + size]
    positions = positions.iloc[start:start + size]
    for i in range(size):
        bitboard_save.append(move_and_position_to_bitboard(moves[start + i],positions[start + i]))  
    
    bitboard_save = numpy.array(bitboard_save)
    numpy.save('chunk_'+ str(chunk_number) + '_y.npy',bitboard_save)                 

# done for the first 10 million GAMES (not positions)

def create_chunk(size : int, df : pandas.DataFrame, start: int, chunk_number: int):
    bitboard_save = []
    df = df.iloc[start:start + size]
    for i in df:
        bitboard_save.append(from_fen_create_bitboard(i))

    bitboard_save = numpy.array(bitboard_save)
    numpy.save('chunk_'+ str(chunk_number) + '.npy',bitboard_save)                 

def from_fen_create_bitboard(fen):
    return from_chess_board_create_bit_boards(chess.Board(fen))

def pgn_string_to_list_moves(pgn : str):
    pgn = pgn.replace('e.p.+','')
    pgn = pgn.replace('e.p.','')
    pattern = re.compile(r'\d+\.')
    cleaned_string = re.sub(pattern, '', pgn)
    cleaned_string = re.sub(r'\s+', ' ', cleaned_string).strip()
    return cleaned_string.split()

def from_pgn_fens_and_moves(pgn : str):
    boards = get_chess_boards_from_pgn(pgn)
    moves = pgn_string_to_list_moves(pgn)
    boards = [i.fen() for i in boards]
    
    # deleting first move and last position
    
    moves.pop(0)
    boards.pop(-1)

    return (boards, moves)

def append_to_file(filename,rows):
    
    with open(filename, 'a', newline='') as file:
        writer = csv.writer(file)
        for i in range(len(rows[0])):
            writer.writerow([rows[0][i], rows[1][i]])

# this functions adds to a given filename a set of moves and position fen
# it expects a pandas df with only a column containing a sting with all the moves of the game.

def from_list_of_pgns_append_to_file(filename,pgn_list : pandas.DataFrame):

    for pgn in pgn_list:    
        rows = from_pgn_fens_and_moves(pgn)
        append_to_file(filename,rows)

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

def from_chess_move_create_bitboard(move : chess.Move):
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

def from_bitboard_reshape_data(x,y):
    print('reshaping data to fit 2 models type of engine')
    x2 = second.transform_from_first_dataset_to_second(x,y)
    y,y2 = second.transform_y(y)

    return x,x2,y,y2

def from_bitboard_save_file(filepath, username, x_bitboard, x2_bitboard, y_bitboard, y2_bitboard, list_of_white):
    print('saving bitboards files')
    username = ''
    x_filename = filepath + username + r'\x.npy'
    x2_filename = filepath + username + r'\x2.npy'
    y_filename = filepath + username + r'\y.npy'
    y2_filename = filepath + username + r'\y2.npy'
    
    white_filename = filepath + username + '_white_bitboard.npy'

    numpy.save(x_filename, x_bitboard)
    numpy.save(y_filename, y_bitboard)
    numpy.save(x2_filename, x2_bitboard)
    numpy.save(y2_filename, y2_bitboard)
    numpy.save(white_filename, list_of_white)


        
    # numpy.save(white_filename, list_of_white)

    print('saving at : ', x_filename)

    return

# filename has to be defined by the user
# filename is the path to a json file where the games will be converted 

def generate_from_filename(username, first_pgn_index = 0, filename = None, number = None, saving_path = None):

    user_rating = 1700

    filepath = filename

    if saving_path:
        filepath_to_save = saving_path
    else:
        filepath_to_save = 'Backend/data/bit_boards/bit_boards_' + str(user_rating) + '/'

    print(filepath)
    assert os.path.isfile(filepath)

    json_df = pandas.read_json(filepath, lines=True)

    json_df = json_df.iloc[first_pgn_index:]

    list_of_position = from_json_dataframe_create_list_of_chess_position(json_df, username)
    x_list, y_list = from_list_of_chess_position_split_x_and_y_for_bitboards(list_of_position)

    x_bitboard, y_bitboard, list_of_white = from_list_of_x_and_y_position_create_bitboard(x_list, y_list)

    x1, x2, y1, y2 = from_bitboard_reshape_data(x_bitboard,y_bitboard)

    from_bitboard_save_file(filepath_to_save, username,  x1, x2, y1, y2, list_of_white)

    return

def generate_from_filepath_and_username(username, saving_path, filepath):
    
    print('generating for the user : ', username)
    json_df = pandas.read_json(filepath, lines=True)

    list_of_position = from_json_dataframe_create_list_of_chess_position(json_df, username)
    x_list, y_list = from_list_of_chess_position_split_x_and_y_for_bitboards(list_of_position)

    x_bitboard, y_bitboard, list_of_white = from_list_of_x_and_y_position_create_bitboard(x_list, y_list)

    x1, x2, y1, y2 = from_bitboard_reshape_data(x_bitboard,y_bitboard)

    from_bitboard_save_file(saving_path, username,  x1, x2, y1, y2, list_of_white)

    return 