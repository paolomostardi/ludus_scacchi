from Backend.pipeline import from_PGN_generate_bitboards as gen
from Backend.pipeline import gm_pipeline as pipe
import chess
import pandas
import os 

# file used to create a pandas df from pgn lichess file of the month 

# todo create df so that the columns name match the gm_pipeline code


def from_line_get_game_rating_and_time_format(game : str) -> list[str,int,int,str] :


    for line in game.split('\n'):
        if  'WhiteElo' in line:
            white_elo = line
        if  'BlackElo' in line:
            black_elo = line 
        if 'Event' in line:
            time_format = line
        if '1.' in line:
            moves = line

    white_elo = white_elo.split()[1].strip(']').strip('"').strip('?')
    black_elo = black_elo.split()[1].strip(']').strip('"').strip('?')

    if white_elo:
        white_elo = int(white_elo)
    else: 
        white_elo = 0

    if black_elo: 
        black_elo = int(black_elo)
    else: 
        black_elo = 0

    time_format = time_format.split()[2]

    try:
        moves
    except:
        print(game)
    

    return time_format, white_elo, black_elo, moves

def create_df(filename : str, saving_path = None):
    
    if saving_path is None:
        saving_path = ''
    file = open(filename)
    all_games = []
    game = ''
    for line in file:
        
        if line[0] == '[' or line[0] == '\n':
            game += line

        elif line[0] == ' ':
            game=''

        else:
            game += line
            all_games.append(from_line_get_game_rating_and_time_format(game))
            game = ''

    df = pandas.DataFrame(all_games,columns=['time_format','white_elo','black_elo','game'])
    df.to_csv(saving_path + 'games.csv')
    print(df)

def main(filename : str, saving_path = None ):
    

    if saving_path is None:
        saving_path = ''
    
    print('Creating the dataframe')

    create_df(filename, saving_path)

    df = pandas.read_csv(saving_path+'games.csv')

    df = df['game']

    print('Transforming the dataframe to only moves')
    
    for i in df:
        rows = pipe.from_pgn_fens_and_moves(i)
        pipe.append_to_file(saving_path + 'df.csv',rows)

    # todo add check with OS.path.isdir 

    del(df)

    # creates the bitboards (should take the most amount of time)

    print('genereting bitboards')

    df = pandas.read_csv(saving_path + 'df.csv')
    pipe.create_all_chunk(df,saving_path=saving_path)
    pipe.create_all_y_chunk(df,saving_path=saving_path)

