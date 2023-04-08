import numpy
import pandas
import chess


def square_to_index(square):
    letter = chess.square_name(square)
    return 8 - int(letter[1]), squares_index[letter[0]]


def from_chess_board_create_bit_boards(board):

    board_turn = board.turn
    bit_boards = numpy.zeros((14, 8, 8), dtype=numpy.bool)

    for piece in chess.PIECE_TYPES:
        for square in board.pieces(piece, chess.WHITE):
            index = numpy.unravel_index(square, (8, 8))
            bit_boards[piece - 1][7 - index[0]][index[1]] = 1
        for square in board.pieces(piece, chess.BLACK):
            index = numpy.unravel_index(square, (8, 8))
            bit_boards[piece + 5][7 - index[0]][index[1]] = 1

    board.turn = chess.WHITE
    for move in board.legal_moves:




