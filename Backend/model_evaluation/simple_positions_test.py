from Backend.engine__creation import engine_creation as engine
import keras
import chess
import pandas as pd


"""
63 62 61 60 59 58 57 56
55 54 53 52 51 50 49 48
47 46 45 44 43 42 41 40
39 38 37 36 35 34 33 32
31 30 29 28 27 26 25 24
23 22 21 20 19 18 17 16
15 14 13 12 11 10 9  8
7  6  5  4  3  2  1  0
"""


# file used to test the first part of the model on simple positions
# this is usefull to see if the model has a basic understunding of chess 

def model1_assertion(model1):

    ladder_fen = 'k7/6R1/7R/8/8/8/8/K7 w - - 0 1',40
    queen_hang_fen = 'rnb1kb1r/ppp1pppp/5n2/3q4/8/2N5/PPPP1PPP/R1BQKBNR w KQkq - 2 4', 21
    french_fen = 'r1bqkbnr/pp3ppp/2n1p3/3pP3/3p4/2P2N2/PP3PPP/RNBQKB1R w KQkq - 0 6', 21
    scholars_fen = 'r1bqkb1r/pppp1ppp/2n2n2/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq - 4 4',32
    exchange_french_fen = 'rnbqkbnr/ppp2ppp/4p3/3P4/3P4/8/PPP2PPP/RNBQKBNR b KQkq - 0 3', 43
    queen_hang2_fen = 'rn1qkbnr/pp1bpppp/8/1QPp4/8/8/PPP1PPPP/RNB1KBNR b KQkq - 0 4', 52
    unsound_sacrifice = 'r1bqk1nr/pppp1Bpp/2n5/2b1p3/4P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 0 4', 59
    latvian_gambit = 'rnb1kbnr/ppp3pp/3p1q2/5p2/3PP3/5N2/PPP2PPP/RNBQKB1R b KQkq - 1 5', 34


    df = pd.read_csv('Backend/evaluation/simple_positions.csv')


    fen_list = [ladder_fen,queen_hang_fen,french_fen,scholars_fen,
                exchange_french_fen,queen_hang2_fen,unsound_sacrifice,
                latvian_gambit]
    
    counter = 0
    counter2 = 0

    df = df.iterrows()

    for i in df:
        
        position,move = i[1][0],i[1][1]
        print(position,move)
        
        index = engine.return_best_legal_piece(position,model1)
        counter2 += 1
        if index == move:
            counter += 1

    print('Positions guessed correctly: ',str(counter),', out of  ', counter2)


def main():
    model = keras.models.load_model('Backend/data/models/gm_model_white_legal_moves/gm_model_chunk_9.keras')
    model1_assertion(model)

    model = keras.models.load_model('Backend/data/models/13-01/lichess_13_01.keras')
    model1_assertion(model)

    model = keras.models.load_model('Backend/data/models/14_07/gm_dataset_squeezenet.keras')
    model1_assertion(model)

    model = keras.models.load_model('Backend/data/models/gm_model_white/gm_model_chunk_9.keras')
    model1_assertion(model)

    