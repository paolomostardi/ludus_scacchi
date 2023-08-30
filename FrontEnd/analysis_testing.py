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

    63, 62, 61, 60, 59, 58, 57, 56,
    55, 54, 53, 52, 51, 50, 49, 48,
    47, 46, 45, 44, 43, 42, 41, 40,
    39, 38, 37, 36, 35, 34, 33, 32,
    31, 30, 29, 28, 27, 26, 25, 24,
    23, 22, 21, 20, 19, 18, 17, 16,
    15, 14, 13, 12, 11, 10,  9,  8,
     7,  6,  5,  4,  3,  2,  1,  0  
   

"""



def main():
    WIDTH = 1200
    HEIGHT = 800
    board_size = 700
    padding = (20, 85)

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    analysis_board = analysis_mode.AnalysisMode(board_size, screen)
    analysis_board.set_board_padding(padding)

    analysis_board.on_click((0, 0))
    analysis_board.on_click((0, 0))

    analysis_board.on_click((0, 0))
    analysis_board.on_click((0, 0))

    e2 = chess.E2
    click_e2 = helper.from_square_get_click_location(e2, board_size, padding)

    e4 = chess.E4
    click_e4 = helper.from_square_get_click_location(e4, board_size, padding)

    analysis_board.on_click(click_e2)
    analysis_board.on_click(click_e4)

    print(click_e2)
    print(click_e4)

    print(analysis_board.current_branch)
    print(analysis_board.current_depth)
    print(analysis_board.current_move)

    analysis_mode.main()
    return

main()

