from FrontEnd import play_mode
from FrontEnd import training_mode
from FrontEnd import helper
from FrontEnd import analysis_mode
from FrontEnd.analysis_logic import AnalysisLogic
import chess



import pygame
from FrontEnd.button import Button
import os





def make_click_move(square, square2, board):
    print('-------------------------- MAKING MOVE ----------------------------')
    print(chess.square_name(square), chess.square_name(square2))

    move = chess.Move(square, square2)
    board.add_correct_move(move)


e2, e4 = chess.E2, chess.E4
e7, e5 = chess.E7, chess.E5
f2, f4 = chess.F2, chess.F4
e5, f4 = chess.E5, chess.F4



analysis_board = AnalysisLogic()

make_click_move(e2, e4, analysis_board)  # e4
make_click_move(e7, e5, analysis_board)  # e5
make_click_move(f2, f4, analysis_board)

analysis_mode.main(analysis_board)












