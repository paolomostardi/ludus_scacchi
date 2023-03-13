import pandas as pd
import requests


def get_users_with_most_games_in_dataset(df):
    df = df.drop_duplicates(subset=['game_id'])
    player_counts = pd.concat([df['white_player'], df['black_player']]).value_counts()
    top_100_players = player_counts.head(200).index.to_numpy()

    return top_100_players


def save_players(top_100_players):
    print(top_100_players)
    with open('top_players.txt', 'w') as f:
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
