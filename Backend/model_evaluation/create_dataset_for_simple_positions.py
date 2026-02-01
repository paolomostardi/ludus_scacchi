import pandas as pd

def main():
    ladder_fen = 'k7/6R1/7R/8/8/8/8/K7 w - - 0 1',40
    queen_hang_fen = 'rnb1kb1r/ppp1pppp/5n2/3q4/8/2N5/PPPP1PPP/R1BQKBNR w KQkq - 2 4', 21
    french_fen = 'r1bqkbnr/pp3ppp/2n1p3/3pP3/3p4/2P2N2/PP3PPP/RNBQKB1R w KQkq - 0 6', 21
    scholars_fen = 'r1bqkb1r/pppp1ppp/2n2n2/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq - 4 4',32
    exchange_french_fen = 'rnbqkbnr/ppp2ppp/4p3/3P4/3P4/8/PPP2PPP/RNBQKBNR b KQkq - 0 3', 43
    queen_hang2_fen = 'rn1qkbnr/pp1bpppp/8/1QPp4/8/8/PPP1PPPP/RNB1KBNR b KQkq - 0 4', 52
    unsound_sacrifice = 'r1bqk1nr/pppp1Bpp/2n5/2b1p3/4P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 0 4', 59
    latvian_gambit = 'rnb1kbnr/ppp3pp/3p1q2/5p2/3PP3/5N2/PPP2PPP/RNBQKB1R b KQkq - 1 5', 34

    fen_list = [ladder_fen,queen_hang_fen,french_fen,scholars_fen,
                exchange_french_fen,queen_hang2_fen,unsound_sacrifice,
                latvian_gambit]

    
    # generate dataframe from the list, column one is the string, column 2 is the number rapresenting the appropriate square. 
    
    df = pd.DataFrame(fen_list, columns=["FEN", "TargetSquare"])
    df.to_csv("simple_positions.csv", index=False)

main()