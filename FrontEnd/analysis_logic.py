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

    def add_correct_move(self, move):

        return

    def key_up(self):
        return

    def key_down(self):
        return
