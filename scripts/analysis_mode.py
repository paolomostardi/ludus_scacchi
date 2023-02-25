from render_chess import RenderChess
import pygame
import chess


class AnalysisMode(RenderChess):

    def on_click(self, event):
        if self.first_square:
            self.push_move_after_second_click(event)
        self.get_first_click(event)



def main():
    WIDTH = 1000
    HEIGHT = 800
    board_size = 500

    running = True

    clock = pygame.time.Clock()
    framerate = 15
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    board = AnalysisMode( board_size, screen)

    while running:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                board.on_click(event.pos)
        screen.fill((200, 200, 200))
        board.render_board()
        if board.display_promotion:
            board.render_promotion_choice()

        pygame.display.update()
        clock.tick(framerate)

main()
