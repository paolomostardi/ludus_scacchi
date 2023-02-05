
import chess 
import pygame


def get_coordinate_from_click_location(coordinate, board_size):
    square_size = board_size/8
    x = int(coordinate[0]/square_size)
    y = int(coordinate[1]/square_size)
    y = 7 - y
    return x, y


def click_a_piece(coordinate, board_size):
    x, y = get_coordinate_from_click_location(coordinate, board_size)
    square = chess.square(x, y)
    return square


def make_a_move(first_square, coordinate, board_size, chess_board):
    x, y = get_coordinate_from_click_location(coordinate, board_size)
    second_square = chess.square(x, y)
    move = chess.Move(first_square, second_square)
    if move in chess_board.legal_moves:
        chess_board.push(move)
    print('------------')
    print(chess_board)
    return chess_board


def resize_image(image, square_side):
    square_side_smaller = int(square_side * 0.98)
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
    black = (181, 136, 99)
    white = (244, 220, 180)
    height, width = board_size
    square_side = height // 8
    for i in range(64):
        x, y = square_to_coordinate_board(i, height)
        color = white if (i // 8 + i) % 2 == 0 else black
        pygame.draw.rect(screen, color, (x - square_side // 2, y - square_side // 2, square_side, square_side))


def render_piece(square, piece, screen):
    # true is white color and false is black color
    if piece.color:
        image = pygame.image.load("pieces/white/" + piece.symbol() + ".png")
    else:
        image = pygame.image.load("pieces/black/" + piece.symbol() + ".png")

    x, y = square_to_coordinate_piece(square, 700)
    square_size = 700 / 8
    y = 700 - square_size - y

    image = resize_image(image, 700/8)
    screen.blit(image, (x, y))


def render_board(screen, board):

    result = board.piece_map()
    render_background(screen, (700, 700))
    for square, piece in result.items():
        render_piece(square, piece, screen)

    return


def main():
    piece_clicked = None
    WIDTH = 1000
    HEIGHT = 800
    board_size = 700
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
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if piece_clicked:
                    board = make_a_move(piece_clicked, event.pos, board_size, board)
                    piece_clicked = None
                else:
                    piece_clicked = click_a_piece(event.pos, board_size)

        screen.fill((200, 200, 200))
        render_board(screen, board)
        pygame.display.update()
        clock.tick(framerate)


main()
