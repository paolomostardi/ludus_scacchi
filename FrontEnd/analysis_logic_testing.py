import analysis_logic
import chess


def assert_value(current_branch, current_depth, current_move, analysis_board):

    if current_branch != analysis_board.current_branch:
        return False

    if current_depth != analysis_board.current_depth:
        return False

    if current_move != analysis_board.current_move:
        return False

    return True

"""

56 57 58 59 60 61 62 63
48 49 50 51 52 53 54 55
40 41 42 43 44 45 46 47
32 33 34 35 36 37 38 39
24 25 26 27 28 29 30 31
16 17 18 19 20 21 22 23
8  9  10 11 12 13 14 15 
0  1  2  3  4  5  6  7    

"""


def make_click_move(square, square2, board):
    print('-------------------------- MAKING MOVE ----------------------------')
    print(chess.square_name(square), chess.square_name(square2))

    move = chess.Move(square, square2)
    board.add_correct_move(move)


def key_down(board):
    board.key_down()


def key_up(board):
    board.key_up()


def n_key_up(board, n):
    for i in range(n):
        key_up(board)


def n_key_down(board, n):
    for i in range(n):
        key_down(board)


def play_kings_gambit(analysis_board):

    e2, e4 = chess.E2, chess.E4
    e7, e5 = chess.E7, chess.E5
    f2, f4 = chess.F2, chess.F4
    e5, f4 = chess.E5, chess.F4

    make_click_move(e2, e4, analysis_board)  # e4
    make_click_move(e7, e5, analysis_board)  # e5
    make_click_move(f2, f4, analysis_board)


def play_italian(analysis_board):

    e2, e4 = chess.E2, chess.E4
    e7, e5 = chess.E7, chess.E5
    g1, f3 = chess.G1, chess.F3
    b8, c6 = chess.B8, chess.C6
    f1, c4 = chess.F1, chess.C4

    make_click_move(e2, e4, analysis_board)  # e4
    make_click_move(e7, e5, analysis_board)  # e5
    make_click_move(g1, f3, analysis_board)  # Nf3

    assert analysis_board.current_move[0] == 3, 'not the right number'
    assert analysis_board.current_depth == 0, 'not the right depth'

    make_click_move(b8, c6, analysis_board)  # Nc6
    make_click_move(f1, c4, analysis_board)  # Bc4


def test_1_basic_ruy_lopez():

    analysis_board = analysis_logic.AnalysisLogic()

    e2, e4 = chess.E2, chess.E4
    e7, e5 = chess.E7, chess.E5
    g1, f3 = chess.G1, chess.F3
    b8, c6 = chess.B8, chess.C6
    f1, b5 = chess.F1, chess.B5
    a7, a6 = chess.A7, chess.A6

    make_click_move(e2, e4, analysis_board)  # e4
    make_click_move(e7, e5, analysis_board)  # e5
    make_click_move(g1, f3, analysis_board)  # Nf3

    assert analysis_board.current_move == [3], 'not the right number' + analysis_board.current_move
    assert analysis_board.current_depth == 0, 'not the right depth'

    make_click_move(b8, c6, analysis_board)  # Nc6
    make_click_move(f1, b5, analysis_board)  # Bb4
    make_click_move(a7, a6, analysis_board)  # a6

    assert analysis_board.current_move == [6], 'not the right number'
    assert analysis_board.current_depth == 0, 'not the right depth'

    return


def test_2_ruy_lopez_with_some_up_and_down():
    print()
    print()
    print('Executing test number 2, ruy lopez position with up and down inputs ')
    print()
    print()

    analysis_board = analysis_logic.AnalysisLogic()

    e2, e4 = chess.E2, chess.E4
    e7, e5 = chess.E7, chess.E5
    g1, f3 = chess.G1, chess.F3
    b8, c6 = chess.B8, chess.C6
    f1, b5 = chess.F1, chess.B5
    a7, a6 = chess.A7, chess.A6

    key_up(analysis_board)
    key_down(analysis_board)
    key_down(analysis_board)

    make_click_move(e2, e4, analysis_board)  # e4
    key_down(analysis_board)
    key_down(analysis_board)

    assert analysis_board.current_move == [0], 'not the right number got ' + str(analysis_board.current_move)
    assert analysis_board.current_depth == 0, 'not the right depth'

    key_up(analysis_board)

    assert analysis_board.current_move == [1], 'not the right number got ' + str(analysis_board.current_move)
    assert analysis_board.current_depth == 0, 'not the right depth'

    make_click_move(e7, e5, analysis_board)  # e5
    make_click_move(g1, f3, analysis_board)  # Nf3

    assert analysis_board.current_move == [3], 'not the right number got ' + str(analysis_board.current_move)
    assert analysis_board.current_depth == 0, 'not the right depth'

    make_click_move(b8, c6, analysis_board)  # Nc6
    make_click_move(f1, b5, analysis_board)  # Bb4
    make_click_move(a7, a6, analysis_board)  # a6

    assert analysis_board.current_move == [6], 'not the right number got ' + str(analysis_board.current_move)
    assert analysis_board.current_depth == 0, 'not the right depth'


def test_3_ruy_lopez_and_kings_gambit():

    print()
    print()
    print('Executing test number 3, ruy lopez position with kings gambit as a sub-variation ')
    print('including some up and down key input to test the effectiveness of the sub-variation')
    print()
    print()
    analysis_board = analysis_logic.AnalysisLogic()

    kings_pawn_fen = 'rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2'
    kings_gambit_accepted_fen = 'rnbqkbnr/pppp1ppp/8/8/4Pp2/8/PPPP2PP/RNBQKBNR w KQkq - 0 3'
    ruy_lopez_fen = 'r1bqkbnr/pppp1ppp/2n5/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 3'
    begging_fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

    e2, e4 = chess.E2, chess.E4
    e7, e5 = chess.E7, chess.E5
    g1, f3 = chess.G1, chess.F3
    b8, c6 = chess.B8, chess.C6
    f1, b5 = chess.F1, chess.B5
    a7, a6 = chess.A7, chess.A6

    f2, f4 = chess.F2, chess.F4
    e5, f4 = chess.E5, chess.F4
    g1, f3 = chess.G1, chess.F3
    g7, g5 = chess.G7, chess.G5

    make_click_move(e2, e4, analysis_board)  # e4
    make_click_move(e7, e5, analysis_board)  # e5
    make_click_move(g1, f3, analysis_board)  # Nf3
    make_click_move(b8, c6, analysis_board)  # Nc6
    make_click_move(f1, b5, analysis_board)  # Bb4
    make_click_move(a7, a6, analysis_board)  # a6

    assert analysis_board.current_move == [6], 'not the right number got ' + str(analysis_board.current_move)
    assert analysis_board.current_depth == 0, 'not the right depth'

    n_key_down(analysis_board,4)

    make_click_move(f2, f4, analysis_board)
    make_click_move(e5, f4, analysis_board)
    make_click_move(g1, f3, analysis_board)
    make_click_move(g7, g5, analysis_board)

    assert analysis_board.current_move == [2, 3], 'not the right number got ' + str(analysis_board.current_move)
    assert analysis_board.current_depth == 1, 'not the right depth'

    key_down(analysis_board)
    key_down(analysis_board)

    assert analysis_board.get_current_board().fen() == kings_gambit_accepted_fen, 'not the right fen '

    key_down(analysis_board)
    key_down(analysis_board)

    assert analysis_board.current_depth == 0, 'not the right depth'
    assert analysis_board.get_current_board().fen() == kings_pawn_fen, 'not the right fen '

    n_key_up(analysis_board,3)

    assert analysis_board.current_depth == 0, 'not the right depth'
    assert analysis_board.get_current_board().fen() == ruy_lopez_fen, 'not the right fen '

    n_key_down(analysis_board, 10)

    assert analysis_board.current_depth == 0, 'not the right depth'
    assert analysis_board.get_current_board().fen() == begging_fen, 'not the right fen '

    play_kings_gambit(analysis_board)
    key_up(analysis_board)

    assert analysis_board.current_depth == 1, 'not the right depth'
    assert analysis_board.get_current_board().fen() == kings_gambit_accepted_fen, 'not the right fen ' + analysis_board.get_current_board().fen()

    n_key_down(analysis_board, 10)

    assert analysis_board.current_depth == 0, 'not the right depth'
    assert analysis_board.get_current_board().fen() == begging_fen, 'not the right fen '

    return analysis_board


def test_4_adding_italian_to_test_3(analysis_board):
    italian_fen = 'r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 3'

    n_key_down(analysis_board,10)
    play_italian(analysis_board)
    assert analysis_board.current_depth == 1, 'not the right depth'
    assert analysis_board.get_current_board().fen() == italian_fen, 'not the right fen '
    n_key_down(analysis_board,10)
    play_kings_gambit(analysis_board)
    n_key_up(analysis_board,10)
    print(analysis_board.get_current_board())


test_1_basic_ruy_lopez()
test_2_ruy_lopez_with_some_up_and_down()
analysis_board = test_3_ruy_lopez_and_kings_gambit()
test_4_adding_italian_to_test_3(analysis_board)
