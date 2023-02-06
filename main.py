
import chess 
import pygame


def render_promotion_choice(square_to_promote, board_size, screen):

    grey = (200, 200, 200)
    x, y = get_coordinate_from_click_location(square_to_promote,board_size)
    square_side = board_size/8

    y = 7 - y
    x *= square_side
    y *= square_side
    if y == 0:  # white pieces
        pygame.draw.rect(screen, grey, (x, y, square_side, square_side * 4))
        x, y = get_coordinate_from_click_location(square_to_promote, board_size)
        square_to_promote = chess.square(x, y)

        queen = chess.Piece(5, True)
        knight = chess.Piece(2, True)
        rook = chess.Piece(4, True)
        bishop = chess.Piece(3, True)

        render_piece(square_to_promote - 8 * 0, queen, screen)
        render_piece(square_to_promote - 8 * 1, knight, screen)
        render_piece(square_to_promote - 8 * 2, rook, screen)
        render_piece(square_to_promote - 8 * 3, bishop, screen)

    else:
        pygame.draw.rect(screen, grey, (x, y - square_side * 3, square_side, square_side * 4))
        x, y = get_coordinate_from_click_location(square_to_promote, board_size)
        square_to_promote = chess.square(x, y)

        queen = chess.Piece(5, False)
        knight = chess.Piece(2, False)
        rook = chess.Piece(4, False)
        bishop = chess.Piece(3, False)

        render_piece(square_to_promote + 8 * 0, queen, screen)
        render_piece(square_to_promote + 8 * 1, knight, screen)
        render_piece(square_to_promote + 8 * 2, rook, screen)
        render_piece(square_to_promote + 8 * 3, bishop, screen)
    return


def click_promotion(position_of_click, position_of_square_to_promote, board_size):
    x, y = get_coordinate_from_click_location(position_of_click, board_size)
    choice_of_promotion = chess.square(x, y)
    x, y = get_coordinate_from_click_location(position_of_square_to_promote, board_size)
    square_to_promote = chess.square(x, y)
    choice_of_promotion = abs(choice_of_promotion - square_to_promote) / 8

    if choice_of_promotion == 0:  # queen
        choice_of_promotion = 5

    elif choice_of_promotion == 1:  # knight
        choice_of_promotion = 2

    elif choice_of_promotion == 2:  # rook
        choice_of_promotion = 4

    elif choice_of_promotion == 3:  # bishop
        choice_of_promotion = 3
    else:
        choice_of_promotion = - 1
    return choice_of_promotion


def make_promotion(first_move, second_move, board_size, choice_of_promotion, chess_board):
    x, y = get_coordinate_from_click_location(first_move, board_size)
    first_move = chess.square(x, y)
    x, y = get_coordinate_from_click_location(second_move, board_size)
    second_move = chess.square(x, y)

    move = chess.Move(first_move, second_move, choice_of_promotion)
    chess_board.push(move)
    return chess_board


def make_a_promotion(first_square, second_square, chess_board):
    move = chess.Move(first_square, second_square, 5)
    if move in chess_board.legal_moves:
        move = None
        display_promotion = True
    else:
        move = chess.Move(first_square, second_square)
        display_promotion = False
    return move, display_promotion


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

    # checks for possibility of promotion
    if chess.square_rank(first_square) == 6 and chess.square_rank(second_square) == 7:
        move, display_promotion = make_a_promotion(first_square, second_square, chess_board)
    elif chess.square_rank(first_square) == 1 and chess.square_rank(second_square) == 0:
        move, display_promotion = make_a_promotion(first_square, second_square, chess_board)
    else:
        move = chess.Move(first_square, second_square)
        display_promotion = False

    if move in chess_board.legal_moves:
        chess_board.push(move)
    print('------------')
    print(chess_board)
    print(chess.square_rank(first_square), chess.square_rank(second_square))
    return chess_board, display_promotion


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


def render_background(screen, board_size, black, white):
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


def render_board(screen, board, black=(181, 136, 99), white=(244, 220, 180)):

    result = board.piece_map()
    render_background(screen, (700, 700), black, white)
    for square, piece in result.items():
        render_piece(square, piece, screen)

    return


def main():
    square_clicked = None
    piece_clicked = None
    WIDTH = 696
    HEIGHT = 696
    board_size = 700
    framerate = 15
    running = True
    display_promotion = False
    position = 1
    board = chess.Board()

    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    
    while running:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if display_promotion:
                    choice_of_promotion = click_promotion(event.pos, position, board_size)
                    if not(choice_of_promotion == -1):
                        board = make_promotion(square_clicked, position, board_size, choice_of_promotion, board)
                    display_promotion = False

                elif piece_clicked:
                    board, display_promotion = make_a_move(piece_clicked, event.pos, board_size, board)
                    position = event.pos
                    piece_clicked = None

                else:
                    print('piece got clicked')
                    piece_clicked = click_a_piece(event.pos, board_size)
                    square_clicked = event.pos

        screen.fill((200, 200, 200))
        render_board(screen, board)
        if display_promotion:
            render_promotion_choice(position, board_size, screen)
        pygame.display.update()
        clock.tick(framerate)


main()
