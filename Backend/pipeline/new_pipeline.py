import numpy
import pandas
import chess
import chess.pgn
import re
import csv

from Backend.pipeline import from_PGN_generate_bitboards as gen


# file used to train on the gm dataset https://www.kaggle.com/datasets/lazaro97/gm-chess-games


# expecting df with columns:
# 'position','move' 

# total of 13.425.482 positions 


def move_and_position_to_bitboard(move : str, position): 
    position = chess.Board(position)
    position.push_san(move)    
    return gen.from_chess_move_create_bitboard(position.peek())


def from_df_create_move_bitboard(size, moves, positions, start, chunk_number):
    bitboard_save = []
    moves = moves.iloc[start:start + size]
    positions = positions.iloc[start:start + size]
    for i in range(size):
        bitboard_save.append(move_and_position_to_bitboard(moves[start + i],positions[start + i]))  
    
    bitboard_save = numpy.array(bitboard_save)
    numpy.save('chunk_'+ str(chunk_number) + '_y.npy',bitboard_save)  


# calling this to create the df once i have all the positions in a separete cvs file. 

def create_chunk(size : int, df : pandas.DataFrame, start: int, chunk_number: int):
    bitboard_save = []
    df = df.iloc[start:start + size]
    for i in df:
        bitboard_save.append(from_fen_create_bitboard(i))

    bitboard_save = numpy.array(bitboard_save)
    numpy.save('chunk_'+ str(chunk_number) + '.npy',bitboard_save)                 


def from_fen_create_bitboard(fen):
    return gen.from_chess_board_create_bit_boards(chess.Board(fen))


def from_pgn_fens_and_moves(pgn : str):
    boards = gen.get_chess_boards_from_pgn(pgn)
    moves = pgn_string_to_list_moves(pgn)
    boards = [i.fen() for i in boards]
    
    # deleting first move and last position
    
    moves.pop(0)
    boards.pop(-1)

    return (boards, moves)


def create_all_chunk( df : pandas.DataFrame, chunk_size = 1_000_000, start = 0):
    df = df.iloc[start:]
    total_size = len(df) - start
    for i in range(int ( total_size/chunk_size)):
        create_chunk(chunk_size,df['position'],chunk_size * i, i)
        print(i, ' AMOUNT OF CHUNK CHUNK')
    


def pgn_string_to_list_moves(pgn : str):
    pgn = pgn.replace('e.p.+','')
    pgn = pgn.replace('e.p.','')
    pattern = re.compile(r'\d+\.')
    cleaned_string = re.sub(pattern, '', pgn)
    cleaned_string = re.sub(r'\s+', ' ', cleaned_string).strip()
    return cleaned_string.split()


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