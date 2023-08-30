from FrontEnd import helper
from FrontEnd.render_chess import RenderChess
import pygame
import chess
from FrontEnd.move_tree import MovesTree
import chess.engine


class AnalysisMode(RenderChess):

    def __init__(self, board_size, screen):
        super().__init__(board_size, screen)
        self.current_move = [0]  # an array that keep track of all the moves.
        self.current_depth = 0  # how many subbranches the tree has to go through

        self.move_tree = MovesTree('root')  # a tree that represent all the moves played
        self.current_branch = self.move_tree  # the branch that is currently displayed
        self.best_move = None  # the move suggested by the engine
        self.last_move = None

    # return the length of each branch in the tree or something
    def get_total_ply_of_branch(self):
        return self.current_branch.length_to_root(self.move_tree)

    def get_current_ply(self):
        return sum(self.current_move) + self.current_depth

    def get_current_tree_move(self):
        return self.current_branch.go_to_depth(self.current_move[self.current_depth])

    def on_click(self, event):
        if self.first_square is None:
            self.get_first_click(event)
            print('first click')
        else:
            self.push_move_after_second_click(event)
            print('second click')

    def print_status(self):
        print('current set of moves', self.current_move)
        print('current branch:', self.current_branch.get_all_moves())
        print('tree :', self.move_tree.get_all_moves())

    def push_move_after_second_click(self, click_location):
        super().push_move_after_second_click(click_location)

        print('--- PUSHING THE MOVE ---')
        engine_path = r"C:\Users\paolo\OneDrive\Desktop\Final_project\engines\stockfish_15.1_win_x64_avx2\stockfish-windows-2022-x86-64-avx2.exe"
        engine = chess.engine.SimpleEngine.popen_uci(engine_path)

        self.best_move = engine.play(self.chess_board, chess.engine.Limit(time=0.01))

        try:
            if self.chess_board.peek() == self.last_move:
                print(' EMPTY MOVE NOT RECORDED')
                return

            self.last_move = self.chess_board.peek()

        except IndexError as e:
            print('empty list and stuff')

        try:
            # adding the first move
            # depth is always at least 1 unless there are no moves on the board
            # if there are no moves on the tree moves but the board has a move, a legal move has been played therefore we
            # add this move to the main line
            if not self.move_tree.children and self.chess_board.move_stack:

                self.current_branch = self.current_branch.add_child_to_n(0, self.chess_board.peek())
                self.current_depth += 1
                self.current_move.append(0)

                self.print_status()

                print('-----  Initializing the tree moves and stuff -------  ')

                return

            chess_board_peek = self.chess_board.peek()

            # If my current move is not a negative number (which should never happen)
            if self.current_move[self.current_depth] >= 0:
                current_tree_move = self.get_current_tree_move()

            # assigns local variable to the current branch
            elif self.current_depth > 0:
                print('this is it ')
                current_tree_move = self.current_branch.go_to_depth(0)
            else:
                print('something happened that was not supposed to happen')
                return
            all_child_moves = current_tree_move.get_all_child_moves()

            # check whether the move is already in the child of moves

            if chess_board_peek in all_child_moves:
                print('___ Move already stored ___ ')
                print('Old branch: ', self.current_branch)

                index = all_child_moves.index(chess_board_peek)

                # if the move is the first child than it just slides through the mainline
                if index == 0:
                    self.current_move[self.current_depth] += 1
                # otherwise it switches the current branch to the sub-branch that is stored about that move
                else:
                    self.current_branch = self.current_branch.go_to_depth(self.current_move[self.current_depth])

            elif chess_board_peek != current_tree_move:
                if current_tree_move.has_children():
                    print('___ Creating a new branch ___')
                    print(self.get_current_ply(), self.get_total_ply_of_branch())
                    print('old set of moves', self.current_move)
                    self.current_branch = self.current_branch.add_child_to_n(self.current_move[self.current_depth], self.chess_board.peek())
                    self.current_move.append(0)
                    self.current_depth += 1
                else:

                    print('___ Not creating a new branch ___')
                    self.current_branch.push_move((self.chess_board.peek()))
                    self.current_move[self.current_depth] += 1
                    print(' current ply  and total ply of branch ')
                    print(self.get_current_ply(), self.get_total_ply_of_branch())

        except IndexError as error:
            print('index ERROR', self.current_move)
            print(error)
            print(IndexError)
            return
        except AttributeError as error:
            print(' ----------- AttributeError ----------- ')
            print(error)
            print('')
            print('Current_tree_move index: ', self.current_move[self.current_depth] - 1)
            print(self.current_branch.get_all_first_list_child_moves())
            print(AttributeError)
        except TypeError as error:
            print('---- ---- TYPE ERROR  ---- ----')
            print(error)
            print(TypeError)
        self.print_status()

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
        if self.current_depth == 0:
            print('The element is root')
            return
        elif self.current_move[self.current_depth] > 0:
            print('--- Depth NOT being reduced --- ')
            self.current_move[self.current_depth] -= 1
            self.chess_board.pop()
        elif self.current_depth == 1:
            self.current_branch = self.move_tree
            self.current_depth = 0
            self.chess_board.pop()

        elif self.current_move[self.current_depth] == 0 and self.current_depth > 1:
            print('--- Depth being reduced --- ')

            self.current_depth -= 1
            n = self.current_move[self.current_depth]
            self.current_branch = self.current_branch.get_n_parents(self.move_tree, n)[0]
            self.chess_board.pop()

        self.print_status()

        engine_path = r"C:\Users\paolo\OneDrive\Desktop\Final_project\engines\stockfish_15.1_win_x64_avx2\stockfish-windows-2022-x86-64-avx2.exe"
        engine = chess.engine.SimpleEngine.popen_uci(engine_path)
        self.best_move = engine.play(self.chess_board, chess.engine.Limit(time=0.01))

        return

    def key_up(self):
        all_first_child = self.current_branch.get_all_first_list_child_moves()

        print('old depth :', self.current_depth)
        print('old move :', self.current_move)
        print('old branch :', self.current_branch.get_all_first_list_child_moves())
        if self.current_depth == 0 and all_first_child != ['root']:
            print(all_first_child)
            self.current_depth = 1
            self.current_branch = self.move_tree.children[0]

            self.chess_board.push(all_first_child[1])
            return

        elif self.current_move[self.current_depth] < len(all_first_child) - 1:
            self.current_move[self.current_depth] += 1
            n = self.current_move[self.current_depth]
            move = all_first_child[n]
            self.chess_board.push(move)

        else:
            print('not doing the up')

        self.print_status()

        engine_path = r"C:\Users\paolo\OneDrive\Desktop\Final_project\engines\stockfish_15.1_win_x64_avx2\stockfish-windows-2022-x86-64-avx2.exe"
        engine = chess.engine.SimpleEngine.popen_uci(engine_path)
        self.best_move = engine.play(self.chess_board, chess.engine.Limit(time=0.01))

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
    board.set_board_padding((20, 85))

    engine_path = r"C:\Users\paolo\OneDrive\Desktop\Final_project\engines\stockfish_15.1_win_x64_avx2\stockfish-windows-2022-x86-64-avx2.exe"

    engine = chess.engine.SimpleEngine.popen_uci(engine_path)



    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                print('CLICK EVENT COORDINATE ')
                print(event.pos)
                board.on_click(event.pos)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    board.key_down()
                elif event.key == pygame.K_UP:
                    board.key_up()

        screen.fill((200, 200, 200))
        board.render_board()
        rectangle = (20,20, 100, 50)
        pygame.draw.rect(screen, board.dark_blue, rectangle)
        if board.best_move:
            pygame.font.init()
            my_font = pygame.font.SysFont('Times new roman', 35)
            text_surface = my_font.render(str(board.best_move.move), False, board.white)
            screen.blit(text_surface, (rectangle[0], rectangle[1]))

        pygame.display.update()
        clock.tick(framerate)

