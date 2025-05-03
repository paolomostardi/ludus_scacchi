import pandas
import requests
import json
from Backend.pipeline import lichess_user



def open_json_file_pandas(json_filename):

    return pandas.read_json(json_filename)


def search_users(dataframe, rating_desired=1700, rating_range=50, time_format='rapid'):
    lower_bound = rating_desired - rating_range
    upper_bound = rating_desired + rating_range
    list_of_players = []
    for player in dataframe['players']:
        list_of_players.append(player['white']['user']['name'])
        list_of_players.append(player['black']['user']['name'])
    list_of_players = set(list_of_players)
    filtered_list = []
    for player in list_of_players:
        player = get_user_info(player)
        print('player ', player.username)
        if player.get_rating_range() == rating_desired:
            filtered_list.append(player)
    return filtered_list


def get_user_info(username):
    url = "https://lichess.org/api/user/" + username
    response = requests.get(url)
    response = response.json()
    user = lichess_user.LichessUser(response)
    return user


def add_users_to_file(user_list, list_filename):
    with open(list_filename, 'r+') as file:
        data = file.read()
        for user in user_list:
            if user.username not in data:
                file.write(user.username + ' ')
                file.write(str(user.blitz_rating) + ' ')
                file.write(str(user.rapid_rating) + ' ')
                file.write(str(user.classical_rating) + ' ')
                file.write(str(user.blitz_amount_of_games) + ' ')
                file.write(str(user.rapid_amount_of_games) + ' ')
                file.write(str(user.classical_amount_of_games) + ' ')
                file.write(str(user.total_amount_of_games) + ' ')
                file.write(str(user.total_slow_games) + '\n')
    sort_users_by_rapid_rating(list_filename)
    return


def sort_users_by_rapid_rating(list_filename):
    with open(list_filename, 'r') as file:
        # read the lines and convert them into LichessUser objects
        lines = file.readlines()
        users = []
        for line in lines:
            user_dict = json.loads(line)
            user = lichess_user.LichessUser(user_dict)
            if user.username is not None:
                users.append(user)

        # sort the users by their rapid rating
        sorted_users = sorted(users, key=lambda user: user.rapid_rating, reverse=True)

    # rewrite the file with the sorted users
    with open(list_filename, 'w') as file:
        for user in sorted_users:
            file.write(json.dumps(vars(user)) + '\n')


def from_amount_of_games_add_user_to_file(amount_of_game, user_file, pgn_folder):

    user_dataframe = pandas.read_csv(user_file)
    search_games = (user_dataframe['games_downloaded'] - user_dataframe['searched_games'] > 0)
    games_left_to_search_dataframe = user_dataframe[search_games]

    games_added = 0
    index = 0
    while games_added < amount_of_game:
        username = games_left_to_search_dataframe.iloc[index]['username']
        rating = games_left_to_search_dataframe.iloc[index]['rapid_rating']
        rating = lichess_user.get_rating_range(rating)
        index += 1
        pgn_file = pgn_folder + 'pgn_games_' + username + '.json'
        df_to_search = pandas.read_json(pgn_file, lines=True)
        list_of_players = search_users(df_to_search, rating)
