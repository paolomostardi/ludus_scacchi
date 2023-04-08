import io

import pandas as pd
import requests
import os
import chess
import chess.pgn


def get_users_with_most_games_in_dataset(df):
    df = df.drop_duplicates(subset=['game_id'])
    player_counts = pd.concat([df['white_player'], df['black_player']]).value_counts()
    top_100_players = player_counts.head(200).index.to_numpy()

    return top_100_players


def save_players(top_100_players):
    print(top_100_players)
    with open('list_of_players.txt', 'w') as f:
        for player in top_100_players:
            f.write(str(player[1]) + ' ' + player[0])


def order_users_by_most_games_in_api():
    return


def get_users_with_most_games(dataset):
    df = pd.read_csv(dataset)
    list_of_users = get_users_with_most_games_in_dataset(df)
    save_players(list_of_users)


def add_chunk(skip_rows, chunk_size, rows, dataset, df):
    df2 = pd.read_csv(dataset, nrows=chunk_size, skiprows=skip_rows * chunk_size, names=rows)
    df2 = df2.drop_duplicates(subset=['game_id'])
    df2.drop(df2.loc[df2['type'] == 'Bullet'].index, inplace=True)
    df = pd.concat([df, df2])
    skip_rows += 1
    df = df.drop_duplicates(subset=['game_id'])
    return df, skip_rows


def check_user_with_api(user):
    url = "https://lichess.org/api/user/" + user
    response = requests.get(url)
    print(response.json())
    return response.json()


def get_user_amount_of_games(user, blitz = True):
    user_data = check_user_with_api(user)
    if 'perfs' not in user_data:
        return 0
    perfs = user_data['perfs']
    if blitz:
        total_amount_of_games = perfs['blitz']['games'] + perfs['rapid']['games'] + perfs['classical']['games']
    else:
        total_amount_of_games = perfs['rapid']['games'] + perfs['classical']['games']

    return total_amount_of_games


def get_all_users_in_a_file(file):
    array = []
    with open(file) as f:
        for line in f:
            user_games = get_user_amount_of_games(line.strip())
            array.append((line, user_games))
    return array


def get_only_all_username(file):
    list_of_username = []
    with open(file, 'r') as f:
        for line in f:
            parts = line.split()
            list_of_username.append(parts[1])
    return list_of_username





def get_chess_boards_from_pgn(pgn_string):
    board = chess.Board()
    bitboards = []
    for move in chess.pgn.read_game(io.StringIO(pgn_string)).mainline_moves():
        board.push(move)
        bitboards.append(board.copy())

    return bitboards


def get_games_from_all_users():

    filepath = 'Backend/data/list_of_players.txt'
    for user in get_only_all_username(filepath):
        get_pgn_games_from_username(user)


def get_1700():
    users = ['WaywardQueer', 'AKUMARGMASTER2019', 'xXCroGamer91Xx', 'Joonaf', 'CyrCo', 'ZheniaFrolov', 'jelovme',
             'nonAs', 'Sasj1', 'CrapCrusher', 'lexparker', 'jpk1489', 'davebb', 'MoRRo-13']
    for user in users:
        get_pgn_games_from_username(user)

get_1700()
