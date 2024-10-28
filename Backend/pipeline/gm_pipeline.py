import numpy
import pandas
import chess
import chess.pgn
import re
import csv

from Backend.pipeline import from_PGN_generate_bitboards as gen

# file used to convert the gm dataset to bitboards
# file used to train on the gm dataset https://www.kaggle.com/datasets/lazaro97/gm-chess-games

# expecting df with columns:
# 'position','move' 

# total of 10.747.142 positions 

# using generate all chunks will create a set of bitboards from a given df where each position is separeted and the moves are as well. 


def move_and_position_to_bitboard(move : str, position): 
    position = chess.Board(position)
    print(move)
    position.push_san(move)    
    return gen.from_chess_move_create_bitboard(position.peek())


def from_df_create_move_bitboard(size, df : pandas.DataFrame, start, chunk_number, saving_path = ''):
    bitboard_save = []

    df_copy = df[start:start+size]

    c = 0
    for i in df_copy.iterrows():
        c += 1
        print(c)
        bitboard_save.append(move_and_position_to_bitboard(i[1]['move'],i[1]['position']))  
    
    bitboard_save = numpy.array(bitboard_save)
    numpy.save(saving_path + 'chunk_'+ str(chunk_number) + '_y.npy',bitboard_save)  


# calling this to create the df once i have all the positions in a separete cvs file. 

def create_chunk(size : int, df : pandas.DataFrame, start: int, chunk_number: int, saving_path: str):
    bitboard_save = []
    df = df.iloc[start:start + size]
    for i in df:
        bitboard_save.append(from_fen_create_bitboard(i))

    bitboard_save = numpy.array(bitboard_save)
    numpy.save(saving_path + 'chunk_'+ str(chunk_number) + '.npy',bitboard_save)                 


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

# magic function 

def create_all_chunk( df : pandas.DataFrame, chunk_size = 1_000_000, start = 0, saving_path = ''):
    print('starting: ')
    df = df.iloc[start:]
    total_size = len(df) - start
    for i in range(int ( total_size/chunk_size)):
        create_chunk(chunk_size,df['position'],chunk_size * i, i, saving_path)
        print(i, ' AMOUNT OF CHUNK CHUNK')



def pgn_string_to_list_moves(pgn : str):
    pgn = pgn.replace('e.p.+','')
    pgn = pgn.replace('e.p.','')
    pattern = re.compile(r'\d+\.')
    cleaned_string = re.sub(pattern, '', pgn)
    cleaned_string = re.sub(r'\s+', ' ', cleaned_string).strip()
    cleaned_string = re.sub(r'{', ' ', cleaned_string).strip()
    cleaned_string = re.sub(r'}', ' ', cleaned_string).strip()
    cleaned_string = re.sub(r'\[.*?\]', ' ', cleaned_string).strip()
    cleaned_string = re.sub(r'\[%eval #-\d+\]', ' ', cleaned_string).strip()

    cleaned_string = cleaned_string.replace(r'[%eval','')
    cleaned_string = cleaned_string.replace('..','')
    cleaned_string = cleaned_string.replace('?','')
    cleaned_string = cleaned_string.replace('!','')

    return cleaned_string.split()


def append_to_file(filename,rows):
    
    with open(filename, 'a', newline='') as file:
        writer = csv.writer(file)
        for i in range(len(rows[0])):
            writer.writerow([rows[0][i], rows[1][i]])


# this functions adds to a given filename a set of moves and position fen
# it expects a pandas df with only a column containing a string with all the moves of the game.

def create_all_y_chunk(df, size = 1_000_000, saving_path = ''):

    positions = df['position']
    moves = df['move']

    total_chunks = len(df) // size

    for i in range(total_chunks):
        print('generating for chunk number ',i)
        start = i * size 
        from_df_create_move_bitboard( size,df,start=start,chunk_number=i, saving_path = saving_path )


def from_list_of_pgns_append_to_file(filename,pgn_list : pandas.DataFrame):

    for pgn in pgn_list:    
        rows = from_pgn_fens_and_moves(pgn)
        append_to_file(filename,rows)