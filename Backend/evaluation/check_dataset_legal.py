import numpy as np
import chess 
from Backend.pipeline import reverse_bitboard as reverse


def check_dataset_has_all_legal_moves(x,y) -> bool:
    
    for index, position in enumerate(x):
        board = reverse.from_bitboard_return_chess_board(position)
        move = reverse.from_move_bitboard_return_bitboard(y[index])
        try :
            board.push(move) 
        except :
            return False
    return True