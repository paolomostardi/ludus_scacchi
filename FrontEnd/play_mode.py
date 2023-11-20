from FrontEnd import helper
from FrontEnd.render_chess import RenderChess
from FrontEnd.analysis_logic import AnalysisLogic
from FrontEnd.button import Button
from FrontEnd.analysis_mode import main as analysis_main


import pygame
import chess
from keras import models
from keras.models import load_model


import chess.engine
import random

from Backend.engine__creation import engine_creation as engine

class PlayMode(RenderChess):

    def __init__(self, board_size, screen, color = None):
        super().__init__(board_size, screen)
        self.logic_board = AnalysisLogic()
        self.resnet = load_model(r'C:\Users\paolo\OneDrive\Desktop\Final_project\Ludus_scacchi\saved_model\first_mode_engine\resnet.h5')
        self.vgg = load_model(r'C:\Users\paolo\OneDrive\Desktop\Final_project\Ludus_scacchi\saved_model\second_part_engine\VGG19_piece_Predictor.h5')

        if color is None:
            self.color = random.choice([True,False])
        else:
            self.color = color

        if not self.color:
            move = engine.engine(self.chess_board.fen(),self.resnet,self.vgg)
            self.logic_board.add_move(move)
            self.chess_board.push(move)

        

    def generate_move(self):
        try:
            move = self.chess_board.peek()
            return move
        except:
            print('ERROR')

    def on_click(self, event):
        if self.first_square is None:
            self.get_first_click(event)
            return True 
        else:
            return self.push_move_after_second_click(event)

    def push_move_after_second_click(self, click_location):
        super().push_move_after_second_click(click_location)
        move = self.generate_move()
        self.logic_board.add_move(move)
        if self.chess_board.is_game_over():
            return False
        
        if self.chess_board.turn is not self.color:
            move = engine.engine(self.chess_board.fen(),self.resnet,self.vgg)
            self.logic_board.add_move(move)
            self.chess_board.push(move)
            if self.chess_board.is_game_over():
                return False 
        return True 
    
    def key_up(self):
        self.logic_board.key_up()
        self.chess_board = self.logic_board.get_current_board()

    def key_down(self):
        self.logic_board.key_down()
        self.chess_board = self.logic_board.get_current_board()

    def render_gui(self):
        return


def main(color):

    WIDTH = 1200
    HEIGHT = 800
    board_size = 700

    running = True
    resign = False
    pygame.font.init() 

    clock = pygame.time.Clock()
    framerate = 15
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    board = PlayMode(board_size, screen, color)
    board.set_board_padding((50, 50))

    engine_path = r"C:\Users\paolo\OneDrive\Desktop\Final_project\engines\stockfish_15.1_win_x64_avx2\stockfish-windows-2022-x86-64-avx2.exe"
    engine = chess.engine.SimpleEngine.popen_uci(engine_path)

    resign_rectangle = (755,50,50,50)
    resign_button = Button(resign_rectangle,message='    Resing', screen=screen)

    while running:

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                print('CLICK EVENT COORDINATE ')
                print(event.pos)
                running = board.on_click(event.pos)
                if resign_button.check_click(event.pos):
                    running = False
                    resign = True

            if event.type == pygame.QUIT:
                    running = False

            elif event.type == pygame.KEYDOWN:
                
                if event.key == pygame.K_DOWN:
                    board.key_down()
                elif event.key == pygame.K_UP:
                    board.key_up()

        screen.fill((200, 200, 200))
        board.render_board()
        resign_button.render()

        pygame.display.update()
        clock.tick(framerate)


              
    pygame.quit() 
    return board.logic_board, resign


def model_chioce():
    
    WIDTH = 1200
    HEIGHT = 800

    running = True
    pygame.font.init() 
    clock = pygame.time.Clock()
    framerate = 15
    screen = pygame.display.set_mode((WIDTH, HEIGHT))    

    analysis_rect = (200,400,200,200)
    analysis_button = Button(analysis_rect, color= (30,123,45), message = ' Select the model you would like to play with ' , screen=screen )



    while running:

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                print('CLICK EVENT COORDINATE ')
                print(event.pos)
                if analysis_button.check_click(event.pos,[logic_board]):
                        print('hello')
                        pygame.quit()
                        analysis_main(logic_board)

            if event.type == pygame.QUIT:
                    running = False


        screen.fill((150, 150, 150))
        button.render()
        analysis_button.render()
        pygame.display.update()
        clock.tick(framerate)
 
def ending_message(logic_board : AnalysisLogic, color, resign):

    WIDTH = 1200
    HEIGHT = 800

    running = True
    pygame.font.init() 
    clock = pygame.time.Clock()
    framerate = 15
    screen = pygame.display.set_mode((WIDTH, HEIGHT))    

    board = logic_board.get_current_board()

    if board.is_checkmate() or resign:
        if board.turn == color or resign:
            msg = '    You lose'
        else:
            msg = '    You win'
    else: 
        msg = '  Draw '

    
    rect = (50,50,50,50)
    button = Button(rect, message=msg, screen=screen)

    analysis_rect = (50,150,50,50)
    analysis_button = Button(analysis_rect, color= (30,123,45), message = '    Analyse the game ? ' , screen=screen )


    while running:

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                print('CLICK EVENT COORDINATE ')
                print(event.pos)
                if analysis_button.check_click(event.pos,[logic_board]):
                        print('hello')
                        pygame.quit()
                        analysis_main(logic_board)

            if event.type == pygame.QUIT:
                    running = False


        screen.fill((150, 150, 150))
        button.render()
        analysis_button.render()
        pygame.display.update()
        clock.tick(framerate)


    return color