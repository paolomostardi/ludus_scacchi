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
            return False
    return True

def check_pandas_df_has_all_legal_moves(df : pd.DataFrame) -> bool:
    for i, row in df.iterrows():
        try:
            board = chess.Board(row['position'])
            board.push_san(row[' move '])
        except:
            print(row)
            print()
            print(row['position'])
            print()
            print(row[' move '])
            print()
            print(i)
            return False
        
    return True