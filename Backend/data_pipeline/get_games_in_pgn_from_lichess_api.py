import os
import requests




def get_pgn_games_from_username(username, folder, number_of_games=2000, performance_type=None):

    if performance_type is None:
        performance_type = ['rapid', 'blitz', 'classical']
    if not os.path.exists(folder):
        os.makedirs(folder)

    filename = os.path.join(folder, f'pgn_games_{username}.csv')

    url = f"https://lichess.org/api/games/user/{username}"

    headers = {
        "Accept": "application/x-ndjson"
    }

    params = {
        "max": number_of_games,
        "perfType": performance_type,
        'clocks': True
    }

    response = requests.get(url, headers=headers, params=params, stream=True)


    with open(filename, "w") as outfile:
        for line in response.iter_lines():
            if line:
                outfile.write(line.decode('utf-8') + "\n")


