import analysis_logic
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
    print('-------------------------- NEW MOVE TO MAKE NOW ----------------------------')
    move = chess.Move(square, square2)
    board.add_correct_move(move)


def press_down(board):
    board.key_down()


def press_up(board):
    board.key_up()


def test_1_basic_ruy_lopez():

    analysis_board = analysis_logic.AnalysisLogic()

    e2, e4 = chess.E2, chess.E4
    e7, e5 = chess.E7, chess.E5
    g1, f3 = chess.G1, chess.F3
    b8, c6 = chess.B8, chess.C6
    f1, b5 = chess.F1, chess.B5
    a7, a6 = chess.A7, chess.A6

    make_click_move(e2, e4, analysis_board)  # e4
    make_click_move(e7, e5, analysis_board)  # e5
    make_click_move(g1, f3, analysis_board)  # Nf3

    assert analysis_board.current_move == [3], 'not the right number'
    assert analysis_board.current_depth == 0, 'not the right depth'

    make_click_move(b8, c6, analysis_board)  # Nc6
    make_click_move(f1, b5, analysis_board)  # Bb4
    make_click_move(a7, a6, analysis_board)  # a6

    print('------------ RESULTS --------------')
    print(analysis_board.current_branch.get_all_moves())
    print(analysis_board.current_depth)
    print(analysis_board.current_move)

    assert analysis_board.current_move == [6], 'not the right number'
    assert analysis_board.current_depth == 0, 'not the right depth'

    return


def test_2_ruy_lopez_with_some_up_and_down():

    analysis_board = analysis_logic.AnalysisLogic()

    e2, e4 = chess.E2, chess.E4
    e7, e5 = chess.E7, chess.E5
    g1, f3 = chess.G1, chess.F3
    b8, c6 = chess.B8, chess.C6
    f1, b5 = chess.F1, chess.B5
    a7, a6 = chess.A7, chess.A6

    press_up(analysis_board)
    press_down(analysis_board)
    press_down(analysis_board)

    make_click_move(e2, e4, analysis_board)  # e4
    press_down(analysis_board)
    press_down(analysis_board)

    assert analysis_board.current_move == [0], 'not the right number'
    assert analysis_board.current_depth == 0, 'not the right depth'

    press_up(analysis_board)

    assert analysis_board.current_move == [1], 'not the right number'
    assert analysis_board.current_depth == 0, 'not the right depth'

    make_click_move(e7, e5, analysis_board)  # e5
    make_click_move(g1, f3, analysis_board)  # Nf3

    assert analysis_board.current_move == [3], 'not the right number'
    assert analysis_board.current_depth == 0, 'not the right depth'

    make_click_move(b8, c6, analysis_board)  # Nc6
    make_click_move(f1, b5, analysis_board)  # Bb4
    make_click_move(a7, a6, analysis_board)  # a6

    print('------------ RESULTS --------------')
    print(analysis_board.current_branch.get_all_moves())
    print(analysis_board.current_depth)
    print(analysis_board.current_move)

    assert analysis_board.current_move == [6], 'not the right number'
    assert analysis_board.current_depth == 0, 'not the right depth'


test_1_basic_ruy_lopez()

test_2_ruy_lopez_with_some_up_and_down()

