from Backend import manage_files as m
import chess
import chess.engine
import chess.pgn
import numpy


def test_engine_on_dataset(engine_path, dataset_path, amount_of_testing_sets):

    x_path, y_path = dataset_path
    accuracy = 0
    engine = chess.engine.SimpleEngine.popen_uci(engine_path)
    x_dataset = numpy.load(x_path)
    y_dataset = numpy.load(y_path)

    for i in range(amount_of_testing_sets):
        board = m.bitboard_to_board(x_dataset[i])
        result = engine.play(board, chess.engine.Limit(time=0.01))
        if result == m.bitboard_to_move(y_dataset[i]):
            accuracy += 1

    return accuracy