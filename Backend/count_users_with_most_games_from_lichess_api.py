import pandas


def get_users_with_most_games_in_dataset(df):
    df = df.drop_duplicates(subset=['game_id'])
    player_counts = pandas.concat([df['white_player'], df['black_player']]).value_counts()
    top_100_players = player_counts.head(200).index.to_numpy()

    return top_100_players


def save_players(top_100_players):
    print(top_100_players)
    with open('list_of_players.txt', 'w') as f:
        for player in top_100_players:
            f.write(str(player[1]) + ' ' + player[0])


def open_file_pandas():
    return





def search_users():
    return


def get_user_info():
    return




