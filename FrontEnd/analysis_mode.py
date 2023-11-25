from FrontEnd import helper
from FrontEnd.render_chess import RenderChess
from FrontEnd.analysis_logic import AnalysisLogic
from FrontEnd.button import Button

import pygame
import chess

import chess.engine


class AnalysisMode(RenderChess):

    def __init__(self, board_size, screen, logic_board = AnalysisLogic(), list_of_moves = []):
        super().__init__(board_size, screen)
        
        move_rectangle = (800,150,350,620)
        self.move_background = Button(move_rectangle,color=(106,131,146),screen=screen, border_radius=15)

        print('hello')

        if logic_board is None:
            print('nothing here')
            self.logic_board = AnalysisLogic()
            self.list_of_moves = []

        else:
            print('here we go')
            self.logic_board = logic_board
            self.chess_board = logic_board.get_current_board()
            self.list_of_moves = []
            for move in list_of_moves:
                self.append_move_to_list_of_moves_to_render(move)
            self.chess_board = logic_board.get_current_board()   
            print('DONE YEYEYEYY')
          
    def append_move_to_list_of_moves_to_render(self, move):
        
        index = len(self.list_of_moves)
        if index % 2:
            square = (975,int(index/2) * 50 + 150, 175, 50)
        else:
            square = (800,int(index/2) * 50 + 150, 175, 50)

        self.list_of_moves.append(Button(square, (95,125,140),self.screen,message=move,font_padding=(60,0),padding=False,padding_size=2, font_size=45,padding_color=(80,100,150)))
        
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

    def key_up(self):
        self.logic_board.key_up()
        self.chess_board = self.logic_board.get_current_board()

    def key_down(self):
        self.logic_board.key_down()
        self.chess_board = self.logic_board.get_current_board()

    def render_move_list(self):
        self.move_background.render()
        for i in self.list_of_moves:
            i.render()

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

    clock = pygame.time.Clock()
    framerate = 15
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

   
    board = AnalysisMode(board_size, screen, logic_board,list_of_moves= list_of_moves)

    
    board.set_board_padding((50, 50))

    background_rectangle = (30,30,740,740)
    background_button = Button(background_rectangle,light_blue,screen)


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

        
        screen.fill(background_color)        
        background_button.render()
        board.render_board()
        board.render_move_list()

        pygame.display.update()
        clock.tick(framerate)


                
    pygame.quit() 
    return 