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


def play(color, engine):

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

    resign_rectangle = (755,50,50,50)
    resign_button = Button(resign_rectangle,message='Resing', screen=screen)

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

def color_choice():    

    WIDTH = 1200
    HEIGHT = 800
    board_size = 700


    background_color = (33,41,46)
    button_gray = (200,200,200)
    light_blue = (106,131,146)

    border_radius = 100

    orange = (218,145,37,100)

    black_bishop_icon = pygame.image.load(r'C:\Users\paolo\OneDrive\Desktop\Final_project\Ludus_scacchi\FrontEnd\Pieces\black\b.png')
    white_bishop_icon = pygame.image.load(r'C:\Users\paolo\OneDrive\Desktop\Final_project\Ludus_scacchi\FrontEnd\Pieces\white\b.png')
    mix_king_icon = pygame.image.load(r'C:\Users\paolo\OneDrive\Desktop\Final_project\Ludus_scacchi\FrontEnd\Pieces\mix_king.png')


    white_bishop_icon = helper.resize_image(white_bishop_icon, 200, 0.85)
    black_bishop_icon = helper.resize_image(black_bishop_icon, 200, 0.85)
    mix_king_icon = helper.resize_image(mix_king_icon, 200, 0.85)

    running = True
    pygame.font.init() 
    clock = pygame.time.Clock()
    framerate = 15
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    font =  pygame.font.SysFont('Times new roman', 50)

    pygame.display.set_icon(black_bishop_icon)
    pygame.display.set_caption('Ludus Scacchi')

    # x, y, width, height

    
    white_color, black_color, random_color = False,False,False
    choosen_engine_index = None
    choosen_engine_bool = False

    black_rectangle = (- 150,60,450,260)
    black_button = Button(black_rectangle,button_gray,screen=screen,border_radius = border_radius + 50)

    white_rectangle = (840,60,500,260)
    white_button = Button(white_rectangle,button_gray,screen=screen,border_radius = border_radius + 50)

    random_rectangle = (480 ,120,240,180 )
    random_button = Button(random_rectangle,button_gray,screen=screen, border_radius = border_radius)

    container_rectangle = (-150,60,1500, 260)
    container_button = Button(container_rectangle,light_blue,screen=screen)

    start_rectangle = (800,650,300, 100)
    start_button = Button(start_rectangle,orange,screen,message='START GAME',padding=True, padding_color=button_gray, padding_size=8, font_size= 30, font_padding=(50, 30), border_radius=30)

    engine_button_list = []

    path = 'training_data\model'
    for index, engine_name in enumerate(os.listdir(path)):
        engine_rect = (50,400 + (80 * index), 400, 50) 
        engine_button_list.append( Button(engine_rect,orange,screen,message=engine_name,font_size= 40, border_radius= 20, font_padding=(20,0)) )

    while running:

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.check_click(event.pos):
                    if (white_color or black_color or random_color) and choosen_engine_bool:
                        pygame.quit()
                        return [black_color,white_color,random_color], engine_button_list[choosen_engine_index].message
                    
                elif black_button.check_click(event.pos):
                    black_color = True
                    white_color = False
                    random_color = False
                
                elif white_button.check_click(event.pos):
                    black_color = False
                    white_color = True
                    random_color = False
                
                elif random_button.check_click(event.pos):
                    black_color = False
                    white_color = False
                    random_color = True 

                for index,button in enumerate(engine_button_list):
                    if button.check_click(event.pos):
                        choosen_engine_index = index
                        choosen_engine_bool = True                         

            if event.type == pygame.QUIT:
                    running = False


        screen.fill(background_color)

        container_button.render()

        black_button.render()
        screen.blit(black_bishop_icon, (black_button.x + 200 , random_button.y - 20))


        white_button.render()
        screen.blit(white_bishop_icon, (white_button.x + 40 , random_button.y - 20))



        random_button.render()        
        screen.blit(mix_king_icon, (random_button.x + 32 , random_button.y - 10))
        

        [engine.render() for engine in engine_button_list]

        start_button.render()

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

def main():
    
    # white,black,random
    color_choosen,engine_choosen = color_choice()

    if color_choosen[0]:
        color_choosen = False
    elif color_choosen[1]:
        color_choosen = True
    else:
        color_choosen = random.choice([True,False])

    # False is black and True is white
    play(color_choosen,engine_choosen)


