import chess
import pygame
from FrontEnd import helper
import numpy


class RenderChess:
    def __init__(self, board_size, screen):

        self.board_size = board_size
        self.chess_board = chess.Board()
        self.screen = screen

        self.black = (181, 136, 99)
        self.white = (244, 220, 180)
        self.light_grey = (200, 200, 200, 0)
        self.dark_blue = (55, 55, 70)
        self.dark_grey = (40, 40, 40)

        self.first_square = None
        self.second_square = None
        self.square_clicked_bool = None
        self.board_x_padding = None
        self.board_y_padding = None
        self.display_promotion = False
        self.choice_of_promotion = -1

    def get_choice_of_promotion_from_click(self, third_click):
        second_square = self.second_square

        board_size = self.board_size

        square_to_promote = helper.get_square_from_click_location(third_click, board_size, self.get_padding())
        square_selected = abs(second_square - square_to_promote) / 8
        choice_of_promotion = helper.get_choice_of_promotion_from_square_selected(square_selected)

        self.choice_of_promotion = choice_of_promotion

        return choice_of_promotion

    def get_first_click(self, click):
        board_size = self.board_size
        self.first_square = helper.get_square_from_click_location(click, board_size, self.get_padding())

    def get_padding(self):
        x = self.board_x_padding
        y = self.board_y_padding
        return x, y

    def is_choice_of_promotion_valid(self):
        choice_of_promotion = self.choice_of_promotion

        if choice_of_promotion == -1:
            return False
        return

    def is_current_move_a_promotion(self):
        first_square = self.first_square
        second_square = self.second_square
        chess_board = self.chess_board

        move = chess.Move(first_square, second_square, 5)
        if move in chess_board.legal_moves:
            self.display_promotion = True
            return True
        else:
            self.display_promotion = False
            return False

    def push_move_after_second_click(self, click_location):

        first_square = self.first_square
        chess_board = self.chess_board
        board_size = self.board_size

        self.second_square = helper.get_square_from_click_location(click_location, board_size, self.get_padding())
        second_square = self.second_square

        if first_square is None:
            return chess_board

        if self.display_promotion:
            self.get_choice_of_promotion_from_click(click_location)
            self.push_promotion_to_board()

        elif self.is_current_move_a_promotion():
            return chess_board

        move = chess.Move(first_square, second_square)
        if move in self.chess_board.legal_moves:
            chess_board.push(move)
            self.first_square = None
        else:
            self.first_square = None
        return chess_board

    def push_promotion_to_board(self):
        choice_of_promotion = self.choice_of_promotion
        first_square = self.first_square
        chess_board = self.chess_board
        second_square = self.second_square
        if choice_of_promotion == -1:
            self.reset_board_event_state()
            return

        move = chess.Move(first_square, second_square, choice_of_promotion)
        print(move)
        chess_board.push(move)
        self.reset_board_event_state()
        return chess_board

    def render_queen_knight_rook_bishop_for_promotion(self, color):

        second_square = self.second_square

        queen = chess.Piece(5, color)
        knight = chess.Piece(2, color)
        rook = chess.Piece(4, color)
        bishop = chess.Piece(3, color)
        multiplier = 8
        # if the color is white we need to render squares below the point
        if color:
            multiplier *= -1

        self.render_piece(second_square + multiplier * 0, queen)
        self.render_piece(second_square + multiplier * 1, knight)
        self.render_piece(second_square + multiplier * 2, rook)
        self.render_piece(second_square + multiplier * 3, bishop)

        return

    # function used to render everything that is needed for promotion

    def render_promotion_choice(self):

        light_grey = self.light_grey
        second_square = self.second_square
        board_size = self.board_size
        screen = self.screen

        white = True
        black = False

        x, y = helper.square_number_to_coordinate(second_square)
        square_side = board_size / 8
        y = 7 - y
        x *= square_side
        y *= square_side

        if y == 0:  # white pieces
            x, y = numpy.add((x, y), self.get_padding())
            pygame.draw.rect(screen, light_grey, (x, y, square_side, square_side * 4))
            self.render_queen_knight_rook_bishop_for_promotion(white)
        else:
            x, y = numpy.add((x, y), self.get_padding())
            pygame.draw.rect(screen, light_grey, (x, y - square_side * 3, square_side, square_side * 4))
            self.render_queen_knight_rook_bishop_for_promotion(black)

        return

    # render a single piece given the square to which it belongs and the piece representation in pychess

    def render_piece(self, square, piece):

        board_size = self.board_size
        screen = self.screen

        # true is white color and false is black color
        if piece.color:
            image = pygame.image.load("Frontend/pieces/white/" + piece.symbol() + ".png")
        else:
            image = pygame.image.load("Frontend/pieces/black/" + piece.symbol() + ".png")

        x, y = helper.square_to_coordinate_piece(square, board_size)
        square_size = board_size / 8
        # need to flip on the y-axis because the board counts from 63 to 0 from up to bottom
        y = board_size - square_size - y

        image = helper.resize_image(image, board_size / 8)
        x += self.board_x_padding 
        y += self.board_y_padding
        screen.blit(image, (x, y))

    # render the background colors

    def render_background(self):
        height = self.board_size
        black = self.black
        white = self.white
        screen = self.screen
        square_side = height // 8
        for i in range(64):
            x, y = helper.square_to_coordinate_board(i, height)
            x += self.board_x_padding
            y += self.board_y_padding
            color = white if (i // 8 + i) % 2 == 0 else black
            pygame.draw.rect(screen, color, (x - square_side // 2, y - square_side // 2, square_side, square_side))

    # render the background colors and the pieces

    def render_board(self):

        chess_board = self.chess_board

        self.render_background()
        result = chess_board.piece_map()

        for square, piece in result.items():
            self.render_piece(square, piece)

        if self.first_square:
            self.render_move_suggestion_from_square()

        if self.display_promotion:
            self.render_promotion_choice()

        return

    def render_dot_in_given_square(self, square_to_render):
        board_size = self.board_size
        screen = self.screen

        transparent_light_green = (144, 238, 144, 10)
        square_size = board_size // 8
        x = square_to_render % 8 * square_size + square_size // 2
        y = (7 - square_to_render // 8) * square_size + square_size // 2
        dot_size = square_size // 7
        x, y = numpy.add((x, y), self.get_padding())
        pygame.draw.circle(screen, transparent_light_green, (x, y), dot_size)

    def render_move_suggestion_from_square(self):
        first_square = self.first_square
        chess_board = self.chess_board

        legal_moves = [move for move in chess_board.legal_moves if move.from_square == first_square]
        target_squares = [move.to_square for move in legal_moves]
        for square in target_squares:
            self.render_dot_in_given_square(square)
        return

    def reset_board_event_state(self):
        self.choice_of_promotion = -1
        self.first_square = None
        self.display_promotion = False

    def set_chess_board(self, chess_board):
        self.chess_board = chess_board

    def set_board_padding(self, padding):
        self.board_x_padding = padding[0]
        self.board_y_padding = padding[1]
