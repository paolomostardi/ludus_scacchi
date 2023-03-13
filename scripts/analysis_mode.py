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


def main():

    WIDTH = 1200
    HEIGHT = 800
    board_size = 700

    running = True

    clock = pygame.time.Clock()
    framerate = 15
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    board = AnalysisMode(board_size, screen)
    board.set_board_padding((20,20))
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
