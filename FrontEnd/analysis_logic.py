import chess
from FrontEnd.move_tree import MovesTree


class AnalysisLogic:

    def __init__(self):
        self.current_move = [0]  # an array that keep track of all the moves.
        self.current_depth = 0  # how many subbranches the tree has to go through

        self.move_tree = MovesTree('root')  # a tree that represent all the moves played
        self.current_branch = self.move_tree  # the branch that is currently displayed
        self.current_board = chess.Board()

        self.last_move = None

    def get_current_move_from_tree(self):
        return self.current_branch.go_to_depth(self.current_move[self.current_depth])

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

    def increase_current_move_depth(self):
        self.current_depth += 1
        self.current_move.append(0)

    def add_correct_move(self, move):

        self.current_board.push(move)
        current_board = self.current_board.fen()

        if self.is_this_node_a_children_of_the_current_move(current_board):
            if self.is_this_in_the_main_line(current_board):
                self.key_up()
            else:  # node is children but not the main line
                self.increase_current_move_depth()
        else:  # move has not been played before
            if self.does_current_move_have_children():
                self.add_child_to_current_line(current_board)
                self.increase_current_move_depth()
            else:  # move does not have any children so we can just extend the line
                self.add_child_to_current_line(current_board)
                self.increase_current_move()
        return

    def key_up(self):

        return

    def key_down(self):
        return
