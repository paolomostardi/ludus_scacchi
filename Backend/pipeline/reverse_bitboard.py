import numpy as np
import chess


# 0 pawn
# 1 knight 
# 2 bishop
# 3 rook
# 4 queen
# 5 king
# 6 pawn
# 7 knight 
# 8 bishop
# 9 rook 
# 10 queen
# 11 king 
# 12 legal moves white
# 13 legal moves black
# 14 whose to play  

# something about the index is coming the wrong way so i need to fix it
def transform_index(index):
    dict = {
        7: -7,
        6: -5,
        5: -3,
        4: -1,
        3: 1,
        2: 3,
        1: 5,
        0: 7
    }
    index = 63 - index
    module = index % 8
    return index + dict[module] 

def from_bitboard_return_chess_board(bitboard: np.array) -> chess.Board:
    empty_fen = '8/8/8/8/8/8/8/8 w - - 0 1'
    board = chess.Board(empty_fen)    
   
    for i,answer in enumerate(bitboard[0].flat):
        if answer:
            board.set_piece_at(transform_index(i),chess.Piece(chess.PAWN,chess.WHITE))
    for i,answer in enumerate(bitboard[1].flat):
        if answer:
            board.set_piece_at(transform_index(i),chess.Piece(chess.KNIGHT,chess.WHITE))
    for i,answer in enumerate(bitboard[2].flat):
        if answer:
            board.set_piece_at(transform_index(i),chess.Piece(chess.BISHOP,chess.WHITE))
    for i,answer in enumerate(bitboard[3].flat):
        if answer:
            board.set_piece_at(transform_index(i),chess.Piece(chess.ROOK,chess.WHITE))
    for i,answer in enumerate(bitboard[4].flat):
        if answer:
            board.set_piece_at(transform_index(i),chess.Piece(chess.QUEEN,chess.WHITE))
    for i,answer in enumerate(bitboard[5].flat):
        if answer:
            board.set_piece_at(transform_index(i),chess.Piece(chess.KING,chess.WHITE))
    
    for i,answer in enumerate(bitboard[6].flat):
        if answer:
            board.set_piece_at(transform_index(i),chess.Piece(chess.PAWN,chess.BLACK))
    for i,answer in enumerate(bitboard[7].flat):
        if answer:
            board.set_piece_at(transform_index(i),chess.Piece(chess.KNIGHT,chess.BLACK))
    for i,answer in enumerate(bitboard[8].flat):
        if answer:
            board.set_piece_at(transform_index(i),chess.Piece(chess.BISHOP,chess.BLACK))
    for i,answer in enumerate(bitboard[9].flat):
        if answer:
            board.set_piece_at(transform_index(i),chess.Piece(chess.ROOK,chess.BLACK))
    for i,answer in enumerate(bitboard[10].flat):
        if answer:
            board.set_piece_at(transform_index(i),chess.Piece(chess.QUEEN,chess.BLACK))
    for i,answer in enumerate(bitboard[11].flat):
        if answer:
            board.set_piece_at(transform_index(i),chess.Piece(chess.KING,chess.WHITE))
    

    print(board)

    return board

if __name__ == "__main__":
    x = np.load('chunk_0.npy')
    from_bitboard_return_chess_board(x[10])
