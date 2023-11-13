from FrontEnd import helper
from FrontEnd.render_chess import RenderChess
from FrontEnd.analysis_logic import AnalysisLogic
import pygame
import chess

import chess.engine


class AnalysisMode(RenderChess):

    def __init__(self, board_size, screen):
        super().__init__(board_size, screen)
        self.logic_board = AnalysisLogic()

    def generate_move(self):
        try:
            move = self.chess_board.peek()
            return move
        except:
            print('ERROR')

    def on_click(self, event):
        if self.first_square is None:
            self.get_first_click(event)
        else:
            self.push_move_after_second_click(event)

    def push_move_after_second_click(self, click_location):
        super().push_move_after_second_click(click_location)
        move = self.generate_move()
        self.logic_board.add_move(move)

    def key_up(self):
        self.logic_board.key_up()
        self.chess_board = self.logic_board.get_current_board()

    def key_down(self):
        self.logic_board.key_down()
        self.chess_board = self.logic_board.get_current_board()

    def render_gui(self):
        return


def main():

    WIDTH = 1200
    HEIGHT = 800
    board_size = 700

    running = True

    clock = pygame.time.Clock()
    framerate = 15
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    board = AnalysisMode(board_size, screen)
    board.set_board_padding((20, 85))

    engine_path = r"C:\Users\paolo\OneDrive\Desktop\Final_project\engines\stockfish_15.1_win_x64_avx2\stockfish-windows-2022-x86-64-avx2.exe"
    engine = chess.engine.SimpleEngine.popen_uci(engine_path)

    while running:

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                print('CLICK EVENT COORDINATE ')
                print(event.pos)
                board.on_click(event.pos)

            if event.type == pygame.QUIT:
                    running = False

            elif event.type == pygame.KEYDOWN:
                
                if event.key == pygame.K_DOWN:
                    board.key_down()
                elif event.key == pygame.K_UP:
                    board.key_up()



        screen.fill((200, 200, 200))
        board.render_board()
        rectangle = (20,20, 100, 50)
        pygame.draw.rect(screen, board.dark_blue, rectangle)
        pygame.display.update()
        clock.tick(framerate)


                
    pygame.quit() 
    return 