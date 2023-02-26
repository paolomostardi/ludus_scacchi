import chess
import pygame


def resize_image(image, square_side):
    square_side_smaller = int(square_side * 0.98)
    return pygame.transform.smoothscale(image, (square_side_smaller, square_side_smaller))

# returns where to render a piece given a square and the size of the board in overall pixels
# gives the coordinate to render the piece in the center and not the corner,
# assumes the piece size is related to the square size


def square_to_coordinate_piece(square: int, height: int):
    square_side = height // 8
    square_side_smaller = int(square_side * 0.9)
    y = (square // 8) * square_side + (square_side - square_side_smaller) // 2
    x = (square % 8) * square_side + (square_side - square_side_smaller) // 2
    return x, y


def square_to_coordinate_board(square: int, height: int):
    square_side = height // 8
    y = (square // 8) * square_side + square_side // 2
    x = (square % 8) * square_side + square_side // 2
    return x, y


def get_board_coordinate_from_click_location(click_location, board_size):
    square_size = board_size / 8
    x = int(click_location[0] / square_size)
    y = int(click_location[1] / square_size)
    y = 7 - y
    return x, y


def get_square_from_click_location(click_location, board_size):
    x, y = get_board_coordinate_from_click_location(click_location, board_size)
    square = chess.square(x, y)
    return square


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


def square_number_to_coordinate(square_number):
    x = square_number % 8
    y = square_number // 8

    return x, y
