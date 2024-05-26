from Backend.engine__creation import engine_creation as engine

# simple ladder checkmate with 2 rooks
def ladder_checkmate( model1, model2):

    fen = 'k7/6R1/7R/8/8/8/8/K7 w - - 0 1'
    move = engine.engine(fen, model1, model2)

    print(move)

# queen is hanged 
def queen_hang(model1, model2):

    fen = 'rnb1kb1r/ppp1pppp/5n2/3q4/8/2N5/PPPP1PPP/R1BQKBNR w KQkq - 2 4'
    move = engine.engine(fen, model1, model2)
    print(move)


# queen is hanged 
def french_advanced_pawn_recapture(model1, model2):

    fen = 'r1bqkbnr/pp3ppp/2n1p3/3pP3/3p4/2P2N2/PP3PPP/RNBQKB1R w KQkq - 0 6'
    move = engine.engine(fen, model1, model2)
    print(move)


# scholars mate 
def scholars_mate(model1, model2):

    fen = 'r1bqkb1r/pppp1ppp/2n2n2/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq - 4 4'
    move = engine.engine(fen, model1, model2)
    print(move)


# queen is hanged 
def queen_hang(model1, model2):

    fen = 'rnb1kb1r/ppp1pppp/5n2/3q4/8/2N5/PPPP1PPP/R1BQKBNR w KQkq - 2 4'
    move = engine.engine(fen, model1, model2)
    print(move)