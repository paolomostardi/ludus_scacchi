from Backend.engine__creation import engine_creation as engine
import keras
import chess


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

# simple ladder checkmate with 2 rooks
def model1_assertion(model1):

    ladder_fen = 'k7/6R1/7R/8/8/8/8/K7 w - - 0 1',40
    queen_hang_fen = 'rnb1kb1r/ppp1pppp/5n2/3q4/8/2N5/PPPP1PPP/R1BQKBNR w KQkq - 2 4', 21
    french_fen = 'r1bqkbnr/pp3ppp/2n1p3/3pP3/3p4/2P2N2/PP3PPP/RNBQKB1R w KQkq - 0 6', 21
    scholars_fen = 'r1bqkb1r/pppp1ppp/2n2n2/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq - 4 4',32

    fen_list = [ladder_fen,queen_hang_fen,french_fen,scholars_fen]
    print(' testing positions')
    print(fen_list)

# in this case we might want to use both ? 
    counter = 0
    for fen in fen_list:
        index = engine.return_best_legal_piece(fen[0],model1)
        if index == fen[1]:
            counter += 1
        else:
            print(fen[0], 'mistaken for this position')
    
    print('total position correct ',str(counter),'total lenght',str(len(fen_list)),'ratio: ',str(counter/len(fen_list))   )

    counter = 0
    for fen in fen_list:
        index, _ = engine.return_top_piece_to_move(fen[0],model1)
        if index[0] == fen[1]:
            counter += 1
        else:
            print(fen[0], 'mistaken for this position')
        
    print('total position correct ',str(counter),'total lenght',str(len(fen_list)),'ratio: ',str(counter/len(fen_list))   )



if __name__ == "__main__":
    model = keras.models.load_model('Backend/data/models/gm_model_white/gm_model_chunk_9.keras')
    model1_assertion(model)



