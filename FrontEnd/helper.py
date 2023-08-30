import chess
import pygame
import numpy


def from_square_get_click_location(square, board_size, padding):

    print('square is ')
    print(square)
    x, y = square_number_to_coordinate(square)
    y = 7 - y
    square_side = board_size / 8
    x = x * square_side + padding[0]
    y = y * square_side + padding[1]
    return int(x), int(y)


def get_board_coordinate_from_click_location(click_location, board_size):
    square_size = board_size / 8
    x = int(click_location[0] / square_size)
    y = int(click_location[1] / square_size)
    y = 7 - y
    return x, y


def get_choice_of_promotion_from_square_selected(square_number):
    choice_of_promotion = square_number
    if choice_of_promotion == 0:  # queen
        choice_of_promotion = 5

    elif choice_of_promotion == 1:  # knight
        choice_of_promotion = 2

    elif choice_of_promotion == 2:  # rook
        choice_of_promotion = 4

    elif choice_of_promotion == 3:  # bishop
        choice_of_promotion = 3
    else:
        choice_of_promotion = - 1

    return choice_of_promotion


def get_square_from_click_location(click_location, board_size, padding):
    click_location = numpy.subtract(click_location, padding)
    x, y = get_board_coordinate_from_click_location(click_location, board_size)
    square = chess.square(x, y)
    return square


def get_algebraic_move_from_uci(move, new_board):
    algebraic_move = new_board.san(move)
    new_board.push(move)
    return algebraic_move


def resize_image(image, square_side, size_difference=0.98):
    square_side_smaller = int(square_side * size_difference)
    return pygame.transform.smoothscale(image, (square_side_smaller, square_side_smaller))


def square_number_to_coordinate(square_number):
    x = square_number % 8
    y = square_number // 8
    return x, y


def square_to_coordinate_board(square: int, height: int):
    square_side = height // 8
    y = (square // 8) * square_side + square_side // 2
    x = (square % 8) * square_side + square_side // 2
    return x, y


def square_to_coordinate_piece(square: int, height: int, size_difference=0.98):
    square_side = height // 8
    square_side_smaller = int(square_side * size_difference)
    y = (square // 8) * square_side + (square_side - square_side_smaller) // 2
    x = (square % 8) * square_side + (square_side - square_side_smaller) // 2
    return x, y
