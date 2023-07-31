import analysis_mode
import pygame
import helper



def assert_value(current_branch,current_depth,current_move, analysis_board):

    if current_branch != analysis_board.current_branch:
        return False

    if current_depth != analysis_board.current_depth:
        return False

    if current_move != analysis_board.current_move:
        return False

    return True


def main():
    WIDTH = 1200
    HEIGHT = 800
    board_size = 700

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    analysis_board = analysis_mode.AnalysisMode(board_size, screen)
    analysis_board.set_board_padding((20, 85))

    analysis_board.on_click((0, 0))
    analysis_board.on_click((0, 0))

    analysis_board.on_click((0, 0))
    analysis_board.on_click((0, 0))

    print(analysis_board.current_branch)
    print(analysis_board.current_depth)
    print(analysis_board.current_move)




    return

main()

