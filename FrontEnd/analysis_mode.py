from Backend.engine__creation import engine_creation as engine
from FrontEnd import helper
from FrontEnd.render_chess import RenderChess
from FrontEnd.analysis_logic import AnalysisLogic
from FrontEnd.button import Button

import pygame
import chess
import os 

from keras.models import load_model

import chess.engine


class AnalysisMode(RenderChess):

    def __init__(self, board_size, screen, logic_board = AnalysisLogic(), list_of_moves = []):
        super().__init__(board_size, screen)
        
        move_rectangle = (800,150,350,620)
        self.move_background = Button(move_rectangle,color=(106,131,146),screen=screen, border_radius=15)

        engine_name_rectangle = (800,30,200,50)
        self.engine_name_button = Button(engine_name_rectangle,color=(77,96,107),screen=screen,padding=True,padding_size=1, font_size=40,padding_color=(50,50,50), message='Engine 1')

        change_model_rectangle = (1000,30,150,50)
        self.change_model_button = Button(change_model_rectangle,color=(106,131,146),screen=screen,padding=True,padding_size=1, font_size=20,padding_color=(50,50,50), message='Change model',font_padding=(5,10))   

        best_move_rectangle = (800,80,350,50)
        self.best_move_button = Button(best_move_rectangle,color=(106,131,146),screen=screen,padding=True,padding_size=1,padding_color=(50,50,50))       

        self.logic_board = logic_board
        self.chess_board = logic_board.get_current_board()
        self.list_of_moves = []
        for move in list_of_moves:
            self.append_move_to_list_of_moves_to_render(move)
        self.chess_board = logic_board.get_current_board()

        model_path = r'C:\Users\paolo\OneDrive\Desktop\Final_project\Ludus_scacchi\training_data\model\resnet_vgg_1700'
        self.model1 = load_model(model_path + r'\first_part\model.h5')
        self.model2 = load_model(model_path + r'\second_part\model.h5')
        self.calculate_best_move()

    def update_engine(self,model_path):
        self.model1 = load_model(model_path + r'\first_part\model.h5')
        self.model2 = load_model(model_path + r'\second_part\model.h5')
        self.calculate_best_move()

    def calculate_best_move(self):
        move = engine.engine(self.chess_board.fen(),self.model1,self.model2)
        self.best_move = move
        self.best_move_button.update_message(self.chess_board.san(move))
        print('updating the best move ', move)
        return move
      
    def append_move_to_list_of_moves_to_render(self, move):
        
        index = len(self.list_of_moves)
        if index % 2:
            square = (975,int(index/2) * 50 + 150, 175, 50)
        else:
            square = (800,int(index/2) * 50 + 150, 175, 50)

        self.list_of_moves.append(Button(square, (95,125,140),self.screen,message=move,font_padding=(60,0),padding=True,padding_size=1, font_size=45,padding_color=(50,50,50)))
        
    def generate_move(self):
        try:
            move = self.chess_board.peek()
            return move
        except:
            print('ERROR')

    def on_click(self, event):
        if self.is_click_not_in_board(event):
            return
        if self.first_square is None:
            self.get_first_click(event)
        else:
            self.push_move_after_second_click(event)
 
    def push_move_after_second_click(self, click_location):
        super().push_move_after_second_click(click_location)
        move = self.generate_move()
        self.logic_board.add_move(move)
        
        if self.list_of_moves != []:
            self.chess_board.pop()

            if self.chess_board.san(move) != self.list_of_moves[-1].message:
                print('asdasdasd')

                self.append_move_to_list_of_moves_to_render(self.chess_board.san(move))
                self.chess_board.push(move)
            else: 
                self.chess_board.push(move)
        else:
            self.chess_board.pop()

            self.append_move_to_list_of_moves_to_render(self.chess_board.san(move))
            self.chess_board.push(move)

        self.calculate_best_move()

    def key_up(self):
        self.logic_board.key_up()
        self.chess_board = self.logic_board.get_current_board()
        self.calculate_best_move()

    def key_down(self):
        self.logic_board.key_down()
        self.chess_board = self.logic_board.get_current_board()
        self.calculate_best_move()

    def render_move_list(self):
        self.move_background.render()
        for i in self.list_of_moves:
            i.render()

        return

    def render_best_move(self):

        self.engine_name_button.render()
        self.change_model_button.render()
        self.best_move_button.render()
        return

def main(logic_board: AnalysisLogic = None, list_of_moves = []):

    WIDTH = 1200
    HEIGHT = 800
    board_size = 700


    background_color = (33,41,46)
    button_gray = (200,200,200)
    light_blue = (106,131,146)
    orange = (218,145,37)

    running = True

    pygame.font.init()

    black_bishop_icon = pygame.image.load(r'C:\Users\paolo\OneDrive\Desktop\Final_project\Ludus_scacchi\FrontEnd\Pieces\black\b.png')
    pygame.display.set_icon(black_bishop_icon)
    pygame.display.set_caption('Ludus Scacchi')

    clock = pygame.time.Clock()
    framerate = 15
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

   
    board = AnalysisMode(board_size, screen, logic_board,list_of_moves= list_of_moves)

    render_choice = False
    
    board.set_board_padding((50, 50))

    background_rectangle = (30,30,740,740)
    background_button = Button(background_rectangle,light_blue,screen)

    engine_button_list = []

    path = 'training_data\model'
    for index, engine_name in enumerate(os.listdir(path)):
        engine_rect = (800,80 + (50 * index), 350, 50) 
        engine_button_list.append( Button(engine_rect,light_blue,screen,message=engine_name,font_size= 40, font_padding=(20,0),padding=True,padding_size=1,padding_color=(50,50,50) ) )


    while running:

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                print('CLICK EVENT COORDINATE ')
                print(event.pos)
                board.on_click(event.pos)
                
                if board.change_model_button.check_click(event.pos):
                    render_choice = True

                if render_choice:
                    print('checking') 
                    for engine in engine_button_list:
                        print('engine')
                        if engine.check_click(event.pos):
                            print('choosen engine')
                            board.update_engine(path+'\\'+engine.message)
                            render_choice = False

            if event.type == pygame.QUIT:
                    running = False

            elif event.type == pygame.KEYDOWN:
                
                if event.key == pygame.K_DOWN:
                    board.key_down()
                elif event.key == pygame.K_UP:
                    board.key_up()

        
        screen.fill(background_color)        
        background_button.render()
        board.render_board()
        board.render_move_list()
        board.render_best_move()

        if render_choice:
            for engine in engine_button_list:
                engine.render()

        pygame.display.update()
        clock.tick(framerate)


                
    pygame.quit() 
    return 