from FrontEnd import helper
from FrontEnd.render_chess import RenderChess
import pygame
import chess
import chess.engine
from FrontEnd.move_tree import MovesTree


class AnalysisMode(RenderChess):

    def __init__(self, board_size, screen):
        super().__init__(board_size, screen)
        self.current_move = 0
        self.move_tree = MovesTree('')
        self.current_branch = self.move_tree
        self.best_move = None
        engine_path = r"C:\Users\paolo\OneDrive\Desktop\Final_project\engines\leela_chess\lc0.exe"
        engine = chess.engine.SimpleEngine.popen_uci(engine_path)
        self.engine = engine

    def on_click(self, event):
        if self.first_square is None:
            self.get_first_click(event)
            print('first click')
        else:
            self.push_move_after_second_click(event)
            print('second click')

    def push_move_after_second_click(self, click_location):
        super().push_move_after_second_click(click_location)
        self.render_board()
        pygame.display.update()

        self.best_move = self.engine.play(self.chess_board, chess.engine.Limit(time=0.01))
        self.chess_board.push(self.best_move.move)
        clock = pygame.time.Clock()
        clock.tick(1)

        try:
            if self.move_tree.move == '':
                self.move_tree.move = (self.chess_board.peek())
                self.current_move += 1
            elif self.chess_board.peek() != self.move_tree.get_all_first_list_child_moves()[-1]:
                if len(self.move_tree.get_all_first_list_child_moves()):
                    print('asdasd')
                self.move_tree.push_move((self.chess_board.peek()))
                self.current_move += 1
        except IndexError:
            return
        print('tree :', self.move_tree.get_all_first_list_child_moves())

    def render_move_stack(self):
        chess_board = self.chess_board
        move_stack = chess_board.move_stack
        self.render_move_stack_background()

        counter = 0
        new_board = chess.Board()
        for move in move_stack:
            self.render_move_from_move_stack(move, counter, new_board)
            counter += 1
        return

    def render_move_stack_background(self):
        dark_blue = self.dark_blue
        screen = self.screen
        screen_width, y = screen.get_size()

        x_of_background = self.board_size + self.board_x_padding * 2
        y_of_background = self.board_y_padding
        height_of_background = self.board_size
        width_of_background = screen_width - self.board_size
        width_of_background = width_of_background // 1.2

        rectangle = (x_of_background, y_of_background, width_of_background, height_of_background)

        pygame.draw.rect(screen, dark_blue, rectangle)

    def render_move_from_move_stack(self, move, counter, new_board):

        dark_grey = self.dark_grey
        screen = self.screen
        board_size = self.board_size
        screen_width, y = screen.get_size()
        white = self.light_grey

        x_of_move = (board_size + self.board_x_padding * 2)
        y_of_move = self.board_y_padding + counter // 2 * board_size // 10
        height_of_move = board_size // 10
        width_of_move = (screen_width - self.board_size) // 2
        width_of_move = width_of_move // 1.2

        if counter % 2:
            x_of_move += width_of_move

        rectangle = (x_of_move, y_of_move, width_of_move, height_of_move)

        pygame.draw.rect(screen, dark_grey, rectangle)

        pygame.font.init()
        my_font = pygame.font.SysFont('Times new roman', 35)

        algebraic_move = helper.get_algebraic_move_from_uci(move, new_board)
        text_surface = my_font.render(str(algebraic_move), False, white)
        screen.blit(text_surface, (x_of_move, y_of_move))

    def key_down(self):
        if self.current_move > 0:
            self.current_move -= 1
            new_board = chess.Board()
            for i in range(self.current_move):
                new_board.push(self.move_tree.get_all_first_list_child_moves()[i])
            self.chess_board = new_board
        return

    def key_up(self):
        if self.current_move < len(self.move_tree.get_all_first_list_child_moves()):
            self.current_move += 1
            new_board = chess.Board()
            for i in range(self.current_move):
                new_board.push(self.move_tree.get_all_first_list_child_moves()[i])
            self.chess_board = new_board
        print(self.current_move)
        return

    def render_gui(self):
        return

    def render_board(self):
        super().render_board()
        self.render_move_stack()


def main():

    WIDTH = 1200
    HEIGHT = 800
    board_size = 700

    running = True

    clock = pygame.time.Clock()
    framerate = 15
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    board = AnalysisMode(board_size, screen)
    board.set_board_padding((20, 50))

    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                board.on_click(event.pos)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    board.key_down()
                elif event.key == pygame.K_UP:
                    board.key_up()

        screen.fill((200, 200, 200))
        board.render_board()
        pygame.display.update()
        clock.tick(framerate)
