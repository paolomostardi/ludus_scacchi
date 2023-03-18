class MovesTree(object):

    def __init__(self, move='root', children=None):
        self.children = []
        self.move = move
        if children is not None:
            for child in children:
                self.add_child(child)

    def __repr__(self):
        return self.move

    def add_child(self, node):
        assert isinstance(node, MovesTree)
        self.children.append(node)

    def add_child_to_n(self, n, move):
        move = MovesTree(move)
        self.go_to_depth(n).add_child(move)

    def get_all_first_child_moves(self):
        if self.get_first_child():
            return self.move + ',' + self.get_first_child().get_all_first_child_moves()
        else:
            return self.move

    def get_all_first_list_child_moves(self):
        moves_list = [self.move]
        if self.get_first_child():
            moves_list.extend(self.get_first_child().get_all_first_list_child_moves())
        return moves_list

    def get_all_moves(self):
        return

    def get_first_child(self):
        if self.children:
            return self.children[0]

    def get_n_child(self, n):
        return self.children[n]

    def go_to_depth(self, depth):
        if depth == 0:
            return self
        if not self.children:
            return None
        return self.children[0].go_to_depth(depth - 1)

    def push_move(self, move):
        while self.children:
            return self.children[0].push_move(move)
        move = MovesTree(move)
        self.add_child(move)
        return

    def set_move(self, move):
        self.move = move
        return


def testing_move_tree():
    tree = MovesTree('e4')
    tree.push_move('e5')
    tree.push_move('d4')
    tree.push_move('d5')
    tree.add_child_to_n(2, 'f4')

    return tree
