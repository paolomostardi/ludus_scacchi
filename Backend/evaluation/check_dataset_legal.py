import numpy as np
import chess 
from Backend.pipeline import reverse_bitboard as reverse
import pandas as pd 

# function used to check if all the bitboards have legal moves
def check_dataset_has_all_legal_moves(x,y) -> bool:
    
    for index, position in enumerate(x):
        board = reverse.from_bitboard_return_chess_board(position)
        move = reverse.from_move_bitboard_return_bitboard(y[index])
        try :
            board.push(move) 
        except :
            print(index,'\n')
            print(board)
            print(move,'\n')
            return False
    return True

def check_pandas_df_has_all_legal_moves(df : pd.DataFrame) -> bool:
    for i, row in df.iterrows():
        try:
            board = chess.Board(row['position'])
            board.push_san(row['move'])
        except:
            print(row, '\n\n')
            print(row['position'], '\n\n')
            print(row[' move '], '\n\n')
            print(i, '\n\n')
            return False
        
    return True


def check_bitboard_folder( x_path, y_path, n_chunks) -> bool:
    for i in range(n_chunks):
        x = np.load( x_path + 'chunk_' + str(i) + '.npy')
        y = np.load( y_path + 'chunk_' + str(i) + '_y.npy')
        if not check_dataset_has_all_legal_moves(x,y):
            print('something is not legal here ',i)
            return False
        
    return True