import chess
from FrontEnd.move_tree import MovesTree


class AnalysisLogic:

    def __init__(self):
        self.current_move = [0]  # an array that keep track of all the moves.
        self.current_depth = 0  # how many subbranches the tree has to go through

        self.move_tree = MovesTree('root')  # a tree that represent all the moves played
        self.current_branch = self.move_tree  # the branch that is currently displayed

        self.last_move = None

    def get_current_move_from_tree(self):
        return self.current_branch.go_to_depth(self.current_move[self.current_depth])

    def get_current_board(self):
        current_node = self.get_current_move_from_tree()
        if current_node.move == 'root':
            return chess.Board()
        board = chess.Board(current_node.move)
        return board

    def is_this_node_a_children_of_the_current_move(self, node):

        current_tree = self.get_current_move_from_tree()
        list_of_children_of_current_move = current_tree.get_all_child_moves()

        if list_of_children_of_current_move is []:
            return False
        elif node in list_of_children_of_current_move:
            return True
        else:
            return False

    def is_this_in_the_main_line(self, node):
        current_tree = self.get_current_move_from_tree()
        list_of_children_of_current_move = current_tree.get_all_child_moves()
        if list_of_children_of_current_move is []:
            return False
        elif node == list_of_children_of_current_move[0]:
            return True
        else:
            return False

    def is_current_move_zero(self):
        if self.current_move[self.current_depth] == 0:
            return True
        return False

    def does_current_move_have_children(self):
        current_move = self.get_current_move_from_tree()
        if current_move.get_all_child_moves() == []:
            return False
        return True

    def add_child_to_current_line(self, node):
        current_move = self.get_current_move_from_tree()
        node = MovesTree(node)
        current_move.add_child(node)
        return

    def increase_current_move(self):
        self.current_move[self.current_depth] += 1

    def decrease_current_move(self):
        self.current_move[self.current_depth] -= 1

    def increase_current_move_depth(self, node):
        print('increasing depth')
        current_node = self.get_current_move_from_tree()
        self.current_depth += 1
        self.current_move.append(0)
        # find the child of the branch and make it the current branch
        current_node = current_node.find_child_given_move(node)
        print(current_node)
        if current_node:
            self.current_branch = current_node
        else:
            self.add_child_to_current_line(node)
            self.increase_current_move_depth(node)

    def decrease_current_move_depth(self):
        # todo make this
        self.current_branch =
        return

    def add_correct_move(self, move):

        current_board = self.get_current_board()
        current_board.push(move)
        current_board = current_board.fen()

        if self.is_this_node_a_children_of_the_current_move(current_board):
            if self.is_this_in_the_main_line(current_board):
                self.key_up()
            else:  # node is children but not the main line
                self.increase_current_move_depth(current_board)
        else:  # move has not been played before
            if self.does_current_move_have_children():
                self.add_child_to_current_line(current_board)
                self.increase_current_move_depth(current_board)
            else:  # move does not have any children, so we can just extend the line
                self.add_child_to_current_line(current_board)
                self.increase_current_move()
        return

    def key_up(self):
        if self.get_current_move_from_tree().has_children():
            self.increase_current_move()
        return

    def key_down(self):

        if self.get_current_move_from_tree().move != 'root':
            if self.is_current_move_zero():
                self.decrease_current_move_depth()
            else:
                self.decrease_current_move()
        return
