from Backend import manage_files as m
import chess
import chess.engine
import chess.pgn
import numpy


def test_engine_on_dataset(engine_path, dataset_path, amount_of_testing_sets, starting_point = 0):

    x_path, y_path = dataset_path
    accuracy = 0
    engine = chess.engine.SimpleEngine.popen_uci(engine_path)
    x_dataset = numpy.load(x_path)[starting_point:]
    y_dataset = numpy.load(y_path)[starting_point:]

    for i in range(amount_of_testing_sets):
        try:
            board = m.bitboard_to_board(x_dataset[i])
            result = engine.play(board, chess.engine.Limit(time=0.01))
            y = m.bitboard_to_move(y_dataset[i])
            if i:
                print(' accuracy : ', accuracy/i, i)
            if result.move == y:
                accuracy += 1
        except Exception as e:
            print(' EROORRRRRR ', e)
            engine = chess.engine.SimpleEngine.popen_uci(engine_path)

    return accuracy


def check_validity_of_dataset(dataset_path, amount_of_testing_sets):

    x_path, y_path = dataset_path
    accuracy = 0
    x_dataset = numpy.load(x_path, mmap_mode='r')
    y_dataset = numpy.load(y_path, mmap_mode='r')

    for i in range(amount_of_testing_sets):
        board = m.bitboard_to_board(x_dataset[i])
        y = m.bitboard_to_move(y_dataset[i])
        print(i)
        board.push(y)

    return accuracy

