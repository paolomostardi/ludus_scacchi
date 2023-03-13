from render_chess import RenderChess
import pygame
import chess


class AnalysisMode(RenderChess):

    def on_click(self, event):
        if self.first_square is None:
            self.get_first_click(event)
            print('first click')
        else:
            self.push_move_after_second_click(event)
            print('second click')

    def render_move_stack(self):
        chess_board = self.chess_board
        move_stack = chess_board.move_stack
        self.render_move_stack_background()
        counter = 0
        for move in move_stack :
            self.render_move_from_move_stack(move, counter)
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

    def render_move_from_move_stack(self, move, counter):
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
        my_font = pygame.font.SysFont('Comic Sans MS', 30)
        text_surface = my_font.render(str(move), False, white)
        screen.blit(text_surface, (x_of_move, y_of_move))



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
        screen.fill((200, 200, 200))
        board.render_board()
        pygame.display.update()
        clock.tick(framerate)

main()
