
import chess
from keras import Model
import numpy as np


#  currently used to check on a set of datasets, it needs a model in input and then should take dataset by itself.
#  it may find datasets in folders. 


def main(model):
    legal_dataset = ""
    simple_dataset = ""
    dataset_1700 = ""
    dataset_gm = ""
    dataset_mixed = ""

    legal_dataset = np.load(legal_dataset)
    check_legal_moves(model, legal_dataset)

    simple_dataset = np.load(simple_dataset)
    check_simple_moves(model, simple_dataset)





def give_max(board):
    max_switch = max(range(len(board)), key=board.__getitem__)
    return max_switch

def from_bitboard_return_chess_board(bitboard: np.ndarray) -> chess.Board:
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
            board.set_piece_at(transform_index(i),chess.Piece(chess.KING,chess.BLACK))

    if not bitboard[14][0][0]:
        board.turn = chess.BLACK

    return board

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

def check_legal_moves(model : Model, testing_dataset : np.array):

    predictions = model.predict(testing_dataset)

    counter = 0

    for index, prediction in enumerate(predictions):
        board = from_bitboard_return_chess_board(testing_dataset[index])
        prediction = give_max(prediction)
        prediction = transform_index(prediction)
   
        piece_moves = [move for move in board.legal_moves if move.from_square == prediction]

        if piece_moves:
            counter += 1

    print(counter, len(predictions))
    return counter, len(predictions)

def check_simple_moves(model, dataset):
    pass

def check_accuracy_on_dataset(model, dataset ):
    pass


