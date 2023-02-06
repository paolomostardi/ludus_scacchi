
import chess 
import pygame


def get_board_coordinate_from_click_location(coordinate, board_size):
    square_size = board_size/8
    x = int(coordinate[0]/square_size)
    y = int(coordinate[1]/square_size)
    y = 7 - y
    return x, y


def get_square_from_click_location(coordinate, board_size):
    x, y = get_board_coordinate_from_click_location(coordinate, board_size)
    square = chess.square(x, y)
    return square


def get_choice_of_promotion_from_square_selected(square_number):
    choice_of_promotion = square_number

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


def get_choice_of_promotion_from_click(first_click, second_click, board_size):

    square_selected = get_square_from_click_location(first_click, board_size)
    square_to_promote = get_square_from_click_location(second_click, board_size)
    square_selected = abs(square_selected - square_to_promote) / 8
    choice_of_promotion = get_choice_of_promotion_from_square_selected(square_selected)

    return choice_of_promotion


def render_queen_knight_rook_bishop_for_promotion(color, square_to_promote,board_size, screen):

    square_to_promote = get_square_from_click_location(square_to_promote, board_size)

    queen = chess.Piece(5, color)
    knight = chess.Piece(2, color)
    rook = chess.Piece(4, color)
    bishop = chess.Piece(3, color)
    multiplier = 8
    # if the color is white we need to render squares below the point
    if color:
        multiplier *= -1

    render_piece(square_to_promote + multiplier * 0, queen, screen)
    render_piece(square_to_promote + multiplier * 1, knight, screen)
    render_piece(square_to_promote + multiplier * 2, rook, screen)
    render_piece(square_to_promote + multiplier * 3, bishop, screen)

    return


def render_promotion_choice(square_to_promote, board_size, screen):

    light_grey = (200, 200, 200, 0)
    white = True
    black = False

    x, y = get_board_coordinate_from_click_location(square_to_promote, board_size)
    square_side = board_size/8

    y = 7 - y
    x *= square_side
    y *= square_side
    if y == 0:  # white pieces
        pygame.draw.rect(screen, light_grey, (x, y, square_side, square_side * 4))
        render_queen_knight_rook_bishop_for_promotion(white, square_to_promote, board_size, screen)
    else:
        pygame.draw.rect(screen, light_grey, (x, y - square_side * 3, square_side, square_side * 4))
        render_queen_knight_rook_bishop_for_promotion(black, square_to_promote, board_size, screen)

    return


def render_dot_for_move_suggestion(square, screen, board_size):
    transparent_light_green = (144, 238, 144, 10)
    square_size = board_size // 8
    x = square % 8 * square_size + square_size // 2
    y = (7 - square // 8) * square_size + square_size // 2
    dot_size = square_size // 7
    pygame.draw.circle(screen, transparent_light_green, (x, y), dot_size)


def render_move_suggestion_from_square(square_clicked, chess_board, screen, board_size):

    square_clicked = get_square_from_click_location(square_clicked,board_size)
    legal_moves = [move for move in chess_board.legal_moves if move.from_square == square_clicked]
    target_squares = [move.to_square for move in legal_moves]
    for square in target_squares:
        render_dot_for_move_suggestion(square, screen, board_size)
    return


def push_promotion_to_board(first_click, second_click, board_size, choice_of_promotion, chess_board):

    first_move = get_square_from_click_location(first_click, board_size)
    second_move = get_square_from_click_location(second_click, board_size)
    move = chess.Move(first_move, second_move, choice_of_promotion)
    chess_board.push(move)

    return chess_board


def check_is_promotion(first_square, second_square, chess_board):
    move = chess.Move(first_square, second_square, 5)
    if move in chess_board.legal_moves:
        move = None
        display_promotion = True
    else:
        move = chess.Move(first_square, second_square)
        display_promotion = False
    return move, display_promotion


def make_a_move(first_square, click_location, board_size, chess_board):

    second_square = get_square_from_click_location(click_location, board_size)

    # checks for possibility of promotion
    if chess.square_rank(first_square) == 6 and chess.square_rank(second_square) == 7:
        move, display_promotion = check_is_promotion(first_square, second_square, chess_board)
    elif chess.square_rank(first_square) == 1 and chess.square_rank(second_square) == 0:
        move, display_promotion = check_is_promotion(first_square, second_square, chess_board)
    else:
        move = chess.Move(first_square, second_square)
        display_promotion = False

    if move in chess_board.legal_moves:
        chess_board.push(move)
    print('------------')
    print(chess_board)
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


def render_piece(square, piece, screen, board_size=700):
    # true is white color and false is black color
    if piece.color:
        image = pygame.image.load("pieces/white/" + piece.symbol() + ".png")
    else:
        image = pygame.image.load("pieces/black/" + piece.symbol() + ".png")

    x, y = square_to_coordinate_piece(square, board_size)
    square_size = board_size / 8
    # need to flip on the y-axis because the board counts from 63 to 0 from up to bottom
    y = board_size - square_size - y

    image = resize_image(image, board_size/8)
    screen.blit(image, (x, y))


def render_board(screen, board, black=(181, 136, 99), white=(244, 220, 180), board_size = 700):

    result = board.piece_map()
    render_background(screen, (700, 700), black, white)
    for square, piece in result.items():
        render_piece(square, piece, screen, board_size)

    return


def main():

    square_clicked = None
    square_clicked_bool = None
    position = None

    WIDTH = 696
    HEIGHT = 696
    board_size = 700
    framerate = 15

    running = True
    display_promotion = False

    chess_board = chess.Board()
    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    
    while running:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:

                if display_promotion:
                    choice_of_promotion = get_choice_of_promotion_from_click(event.pos, position, board_size)
                    if not(choice_of_promotion == -1):
                        chess_board = push_promotion_to_board(square_clicked, position, board_size, choice_of_promotion, chess_board)
                    display_promotion = False

                elif square_clicked_bool:
                    chess_board, display_promotion = make_a_move(square_clicked_bool, event.pos, board_size, chess_board)
                    position = event.pos
                    square_clicked_bool = None

                else:
                    print('piece got clicked')
                    square_clicked_bool = get_square_from_click_location(event.pos, board_size)
                    square_clicked = event.pos

        screen.fill((200, 200, 200))
        render_board(screen, chess_board)
        if display_promotion:
            render_promotion_choice(position, board_size, screen)
        if square_clicked_bool:
            render_move_suggestion_from_square(square_clicked, chess_board, screen, board_size)
        pygame.display.update()
        clock.tick(framerate)


main()
