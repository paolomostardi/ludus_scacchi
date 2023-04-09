import numpy
import pandas
import chess


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



