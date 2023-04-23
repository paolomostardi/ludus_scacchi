import requests
import os
import json
import pandas as pd


# Function to get user data from Lichess API
def get_user_data(username):
    url = f"https://lichess.org/api/user/{username}"
    response = requests.get(url)
    if response.ok:
        return response.json()
    else:
        return None


# Function to read usernames from file, get user data from API,
# and write usernames and ratings to another file
def write_user_ratings(input_file, output_file):
    with open(input_file, 'r') as f_in, open(output_file, 'w') as f_out:
        for line in f_in:
            # Read username from file
            username = line.strip().split()[1]
            # Get user data from API
            user_data = get_user_data(username)
            try:
                if user_data['perfs']['rapid']['rating']:
                    # Write user data to output file
                    rapid_rating = user_data['perfs']['rapid']['rating']
                    num_games = line.strip().split()[0]
                    f_out.write(f"{num_games} {username} {rapid_rating}\n")
                else:
                    print(f"Error retrieving data for {username}")
            except KeyError:
                print(username + 'is giving problems')


def sort_file(reading_file,writing_file):

    with open(reading_file, 'r') as f:
        lines = f.readlines()

    lines = [line.strip().split() for line in lines]
    lines = sorted(lines, key=lambda x: int(x[2]))

    with open(writing_file, 'w') as f:
        for line in lines:
            f.write(' '.join(line) + '\n')


def rename_files_to_json(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith(".csv"):
            old_filepath = os.path.join(folder_path, filename)
            new_filename = os.path.splitext(filename)[0] + ".json"
            new_filepath = os.path.join(folder_path, new_filename)
            os.rename(old_filepath, new_filepath)


def merge_csvs_and_jsons(folder_path):
    json_dfs = []
    csv_dfs = []

    for filename in os.listdir(folder_path):
        filename = folder_path + '/' + filename
        if filename.endswith(".json"):
            json_df = pd.read_json(filename, lines=True)
            json_dfs.append(json_df)
        elif filename.endswith(".csv"):
            csv_df = pd.read_csv(filename)
            csv_dfs.append(csv_df)

    merged_df = pd.concat(json_dfs + csv_dfs, axis=0, ignore_index=True)
    return merged_df
