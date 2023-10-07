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
        return move

    def find_child_given_move(self, move):
        list_of_child = self.get_all_child()
        for child in list_of_child:
            if move == child.move:
                return child
        return False

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

    def get_all_moves(self, parent_move=None):
        result = []
        if parent_move:
            result.append(str(parent_move) + " -> " + str(self.move))
        else:
            result.append(self.move)
        for child in self.children:
            result.extend(child.get_all_moves(self.move))
        return result

    def get_first_child(self):
        if self.children:
            return self.children[0]

    def get_n_child(self, n):
        return self.children[n]

    def get_n_parents_reverse(self, root_tree, n):
        node = self
        parents = []
        for i in range(n):
            if node is None:
                break
            node = self.find_parent(root_tree, node)
            if node is not None:
                parents.append(node)
        return parents

    def get_n_parents(self, root_tree, n):
        list_of_moves = self.get_n_parents_reverse(root_tree, n)
        list_of_moves.reverse()
        return list_of_moves

    def get_all_child(self):
        moves_list = []
        for child in self.children:
            moves_list.append(child)
        return moves_list

    def get_all_child_moves(self):
        moves_list = []
        for child in self.children:
            moves_list.append(child.move)
        return moves_list

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

    def find_parent(self, move_tree, child):
        if move_tree.children:
            for node in move_tree.children:
                if node == child:
                    return move_tree
                else:
                    parent = self.find_parent(node, child)
                    if parent:
                        return parent
        return None

    def find_last_first_child(self):
        node = self
        while node.get_first_child():
            node = node.get_first_child()
        return node

    def has_children(self):
        if self.children:
            return True
        return False

    def count_to_root(self, parent_tree):
        node = self
        count = 0
        if node is None:
            return
        while node.move != '':

            count += 1
            node = self.find_parent(parent_tree, node)

            if node is None:
                return count

        return count

    def length_to_root(self, parent_tree):
        node = self.find_last_first_child()
        return node.count_to_root(parent_tree)


def testing_move_tree():
    tree = MovesTree('e4')
    tree.push_move('e5')
    tree.push_move('nf3')
    tree.push_move('nc6')
    tree.push_move('Bb5')
    tree.push_move('a6')

    node = tree.add_child_to_n(1, 'f4')
    node.push_move('exf4')
    node.push_move('Nf3')
    node.push_move('Nf6')

    node1 = node

    node = node.add_child_to_n(1, 'd4')
    node.push_move('g5')

    return tree, node1


def test():
    tree_, node_ = testing_move_tree()
    print('Get all the moves')
    print(tree_.get_all_moves())
    print('Find parent of the node:', node_.move)
    print(tree_.find_parent(tree_, node_))

    nodes = node_.find_last_first_child()
    print('This tree: ', node_.get_all_first_list_child_moves(), 'Has as a last child :', nodes)

    print('The parent of the node ', nodes.move, ' is :')
    print(nodes.find_parent(node_, nodes))

    print('---- The count to root is : ----- ')
    print(nodes.count_to_root(tree_))

    n = 9
    print('The node is: ', nodes)
    print('Getting a list of the N parent n:', n)
    print('list : ')
    print(nodes.get_n_parents(tree_, n))
