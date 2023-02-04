
import chess 
import pygame


def resize_image(image, square_side):
    square_side_smaller = int(square_side * 0.95)
    return pygame.transform.smoothscale(image, (square_side_smaller, square_side_smaller))


def square_to_coordinate_board(square: int, height: int):
    square_side = height // 8
    y = (square // 8) * square_side + square_side // 2
    x = (square % 8) * square_side + square_side // 2
    return x, y


def square_to_coordinate_piece(square: int, height: int):
    square_side = height // 8
    square_side_smaller = int(square_side * 0.9)
    y = (square // 8) * square_side + (square_side - square_side_smaller) // 2
    x = (square % 8) * square_side + (square_side - square_side_smaller) // 2
    return x, y


def render_background(screen, board_size):
    height, width = board_size
    square_side = height // 8
    for i in range(64):
        x, y = square_to_coordinate_board(i, height)
        color = (181, 136, 99) if (i // 8 + i) % 2 == 0 else (244, 220, 180)
        pygame.draw.rect(screen, color, (x - square_side // 2, y - square_side // 2, square_side, square_side))


def render_piece(square, piece, screen):
    if piece.color:
        image = pygame.image.load("pieces/black/" + piece.symbol() + ".png")
    else:
        image = pygame.image.load("pieces/white/" + piece.symbol() + ".png")
    x, y = square_to_coordinate_piece(square, 700)
    image = resize_image(image, 700/8)
    screen.blit(image, (x, y))


def render_board(screen, board):

    result = board.piece_map()
    render_background(screen, (700, 700))
    for square, piece in result.items():
        render_piece(square, piece, screen)

    return


def main():

    WIDTH = 1000
    HEIGHT = 800
    framerate = 15
    running = True
    board = chess.Board()

    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    
    while running:
    
        for event in pygame.event.get():
        
            if event.type == pygame.QUIT:
                running = False
                
        screen.fill((200, 200, 200))
        render_board(screen, board)
        pygame.display.update()
        clock.tick(framerate)


main()
