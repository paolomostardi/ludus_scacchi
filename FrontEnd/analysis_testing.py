import analysis_mode
import pygame
import helper
import chess


def assert_value(current_branch, current_depth, current_move, analysis_board):

    if current_branch != analysis_board.current_branch:
        return False

    if current_depth != analysis_board.current_depth:
        return False

    if current_move != analysis_board.current_move:
        return False

    return True

"""

56 57 58 59 60 61 62 63
48 49 50 51 52 53 54 55
40 41 42 43 44 45 46 47
32 33 34 35 36 37 38 39
24 25 26 27 28 29 30 31
16 17 18 19 20 21 22 23
8  9  10 11 12 13 14 15 
0  1  2  3  4  5  6  7    

"""


def make_click_move(square, square2, board):
    print('NEW MOVE TO MAKE NOW ---------------------------------------------------------------------')

    board.on_click(square)
    board.on_click(square2)


def main():
    WIDTH = 1200
    HEIGHT = 800
    board_size = 700
    padding = (20, 85)

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    analysis_board = analysis_mode.AnalysisMode(board_size, screen)
    analysis_board.set_board_padding(padding)

    e2, e4 = (406, 649), (409, 475)

    e7, e5 = (405, 218), (409, 384)

    g1, f3 = (581, 723), (498, 556)

    b8, c6 = (159, 133), (235, 300)

    f1, b5 = (510, 736), (162, 396)

    a7, a6 = (62, 231), (70, 304)

    b5, c6 = (152, 406), (248, 308)

    make_click_move(e2, e4, analysis_board)

    make_click_move(e7, e5, analysis_board)

    make_click_move(g1, f3, analysis_board)

    make_click_move(b8, c6, analysis_board)  # nc6
    make_click_move(f1, b5, analysis_board)  # Bb4
    make_click_move(a7, a6, analysis_board)  # a6
    make_click_move(b5, c6, analysis_board)  # Bxc6

    return

main()

