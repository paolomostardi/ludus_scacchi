
import numpy as np
from keras import Model


"""
This file is used to evaluate whether the model changes behaviour when the color bitboard is switched.

"""


def give_max(board):
    max_switch = max(range(len(board)), key=board.__getitem__)
    return max_switch

def switch_dataset(testing_dataset):
    comparing_bitboard = []
    for bit_board in testing_dataset:

        print(bit_board[14][0][0])

        if bit_board[14][0][0]: # bitboard is
            bit_board[14] = np.uint64(0) 
        else:
            bit_board[14] = np.uint64(1)
        
        print(bit_board[14][0][0])
        print('--------------------')

        comparing_bitboard.append(bit_board)

    comparing_bitboard = np.array(comparing_bitboard)
    return comparing_bitboard

def white_evaluation(model : Model, testing_dataset : np.array):
    
    original_dataset = testing_dataset.copy()
    comparing_bitboard = []
    for bit_board in testing_dataset:
        if bit_board[14][0][0]: # bitboard is true
            bit_board[14] = np.uint64(0) 
        else:
            bit_board[14] = np.uint64(1)
        comparing_bitboard.append(bit_board)

    comparing_bitboard = np.array(comparing_bitboard)
    
    switched = model.predict(comparing_bitboard, verbose = 0)
    normal = model.predict(original_dataset, verbose = 0)

    counter = 0 
    for index, board in enumerate(switched):
        max_switch = max(range(len(board)), key=board.__getitem__)
        max_normal = max(range(len(normal[index])), key=normal[index].__getitem__)
        if max_switch == max_normal:
            counter += 1
    
    same = counter/len(normal)
    lenght = len(normal)
    print( 'total percentage of same result = ', same ,' total amount of same answer: ',counter,'out of ',lenght)
    return same
