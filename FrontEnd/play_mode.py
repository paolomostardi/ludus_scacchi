from FrontEnd import helper
from FrontEnd.render_chess import RenderChess
from FrontEnd.analysis_logic import AnalysisLogic
from FrontEnd.button import Button
from FrontEnd.analysis_mode import main as analysis_main

from FrontEnd import training_mode

import pygame
import chess
import os

from keras import models
from keras.models import load_model


import chess.engine
import random

from Backend.engine__creation import engine_creation as engine

class PlayMode(RenderChess):

    def __init__(self, board_size, screen, color = None, model_path = ''):
        super().__init__(board_size, screen)
        self.logic_board = AnalysisLogic()

        model_path = r'C:\Users\paolo\OneDrive\Desktop\Final_project\Ludus_scacchi\training_data\model\\' + model_path
        self.model1 = load_model(model_path + r'\first_part\model.h5')
        self.model2 = load_model(model_path + r'\second_part\model.h5')
        
        self.list_of_moves = []

        move_rectangle = (800,150,350,620)
        self.move_background = Button(move_rectangle,color=(106,131,146),screen=screen, border_radius=15)

        if color is None:
            self.color = random.choice([True,False])
        else:
            self.color = color

        if not self.color:
            move = engine.engine(self.chess_board.fen(),self.model1,self.model2)
            self.append_move_to_list_of_moves_to_render(self.chess_board.san(move))
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



        self.logic_board.add_move(move)



        if self.chess_board.is_game_over():
            return False
        
        if self.chess_board.turn is not self.color:
            move = engine.engine(self.chess_board.fen(),self.model1,self.model2)
            self.logic_board.add_move(move)
            self.append_move_to_list_of_moves_to_render(self.chess_board.san(move))
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

    def append_move_to_list_of_moves_to_render(self, move):
        
        index = len(self.list_of_moves)
        if index % 2:
            square = (975,int(index/2) * 50 + 150, 175, 50)
        else:
            square = (800,int(index/2) * 50 + 150, 175, 50)

        self.list_of_moves.append(Button(square, (95,125,140),self.screen,message=move,font_padding=(85,0),padding=False,padding_size=2, font_size=45,padding_color=(80,100,150)))
        
    
    def render_move_list(self):
        self.move_background.render()
        for i in self.list_of_moves:
            i.render()

        return
    
    def return_all_messages(self):
        answer = []
        for i in self.list_of_moves:
            answer.append(i.message)
        return answer

def play(color, engine_path):

    WIDTH = 1200
    HEIGHT = 800
    board_size = 700

    background_color = (33,41,46)
    button_gray = (200,200,200)
    light_blue = (106,131,146)
    orange = (218,145,37)

    running = True
    resign = False
    game_not_finish = True
    pygame.font.init() 

    black_bishop_icon = pygame.image.load(r'C:\Users\paolo\OneDrive\Desktop\Final_project\Ludus_scacchi\FrontEnd\Pieces\black\b.png')
    pygame.display.set_icon(black_bishop_icon)
    pygame.display.set_caption('Ludus Scacchi')

    clock = pygame.time.Clock()
    framerate = 15
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    board = PlayMode(board_size, screen, color,model_path=engine_path)
    board.set_board_padding((50, 50))

    flag_image = pygame.image.load(r'C:\Users\paolo\OneDrive\Desktop\Final_project\Ludus_scacchi\FrontEnd\Pieces\flag.png')
    
    flag_image = helper.resize_image(flag_image, 200, 0.30)

    resign_rectangle = (800,50,75,75)
    resign_button = Button(resign_rectangle, screen=screen, color=light_blue, border_radius=5)

    background_rectangle = (30,30,740,740)
    background_button = Button(background_rectangle,light_blue,screen)


    win_message_rectangle = (800,150,350,100)
    win_message_button = Button(win_message_rectangle,orange,screen,message='You win!',font_padding=(70,25))

    play_again_rectangle = (800,300,350,100)
    play_again_button =  Button(play_again_rectangle,orange,screen,message='  PLAY AGAIN', font_size=30, font_padding=(70,40))

    analyse_game_rectangle = (815,450,150,100)
    analyse_game_button = Button(analyse_game_rectangle,orange,screen,message='Analyse game',border_radius=10, font_size=20, font_padding=(22,40))

    train_new_model_rectangle = (990,450,150,100)
    train_new_model_button = Button(train_new_model_rectangle,orange,screen,message='Train model',border_radius=10, font_size=20, font_padding=(22,40)) 


    while running:

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if not resign:
                    print('CLICK EVENT COORDINATE ')
                    print(event.pos)
                    game_not_finish = board.on_click(event.pos)
                    
                    if resign_button.check_click(event.pos):
                        game_not_finish = False
                        resign = True
                        win_message_button.update_message('You lose')
                if resign or not game_not_finish:
                    if play_again_button.check_click(event.pos):
                        pygame.quit()
                        main()
                    if analyse_game_button.check_click(event.pos):
                        pygame.quit()
                        analysis_main(board.logic_board,board.return_all_messages())
                    if train_new_model_button.check_click(event.pos):
                        pygame.quit()
                        training_mode.main()
                        
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

        if game_not_finish:
            board.render_move_list()

        else: 
            board.move_background.render()
            play_again_button.render()
            win_message_button.render()
            analyse_game_button.render()
            train_new_model_button.render()
            

        resign_button.render()

        screen.blit(flag_image, (resign_button.x + 10 , resign_button.y + 10))

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

    pygame.init()  
    black_bishop_icon = pygame.image.load(r'C:\Users\paolo\OneDrive\Desktop\Final_project\Ludus_scacchi\FrontEnd\Pieces\black\b.png')
    pygame.display.set_icon(black_bishop_icon)
    pygame.display.set_caption('Ludus Scacchi')

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

    start_rectangle = (850,660,300, 100)
    start_button = Button(start_rectangle,orange,screen,message='START GAME',padding=False, padding_color=button_gray, padding_size=4, font_size= 30, font_padding=(60, 35), border_radius=30)

    analysis_rectangle = (850,540,300, 100)
    analysis_button = Button(analysis_rectangle,orange,screen,message='ANALYSE GAME',padding=False, padding_color=button_gray, padding_size=4, font_size= 30, font_padding=(50, 35), border_radius=30)

    analysis_rectangle = (850,420,300, 100)
    train_button = Button(analysis_rectangle,orange,screen,message='TRAIN MODEL',padding=False, padding_color=button_gray, padding_size=4, font_size= 30, font_padding=(60, 35), border_radius=30)


    back_junk = (0,350,1500, 1000)
    back_junk = Button(back_junk,light_blue,screen=screen)

    back_junk2 = (700,345,1500, 1000)
    back_junk2 = Button(back_junk2,light_blue,screen=screen, padding=True, padding_color=background_color)


    engine_button_list = []

    path = 'training_data\model'
    for index, engine_name in enumerate(os.listdir(path)):
        engine_rect = (50,400 + (80 * index), 400, 50) 
        engine_button_list.append( Button(engine_rect,orange,screen,message=engine_name,font_size= 40, border_radius= 20, font_padding=(20,5)) )

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

                if analysis_button.check_click(event.pos):
                        pygame.quit()
                        analysis_main()
                if train_button.check_click(event.pos):
                        pygame.quit()
                        training_mode.main()

                for index,button in enumerate(engine_button_list):
                    if button.check_click(event.pos):
                        choosen_engine_index = index
                        choosen_engine_bool = True                         

            if event.type == pygame.QUIT:
                    running = False


        screen.fill(background_color)

        container_button.render()
        back_junk.render()
        back_junk2.render()

        black_button.render()
        screen.blit(black_bishop_icon, (black_button.x + 200 , random_button.y - 20))

        white_button.render()
        screen.blit(white_bishop_icon, (white_button.x + 40 , random_button.y - 20))

        random_button.render()        
        screen.blit(mix_king_icon, (random_button.x + 32 , random_button.y - 10))
        
        analysis_button.render()
        train_button.render()

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


