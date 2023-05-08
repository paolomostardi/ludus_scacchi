import requests
import os
import json
import pandas as pd
from Backend import from_PGN_generate_bitboards as bitboards
import numpy as np
import chess

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


def call_function_for_each_file(function, folder, usernames):
    i = 0
    for file_path in os.listdir(folder):
        dir_path, filename = os.path.split(file_path)
        username = filename.split("_")[2].split(".")[0]
        print(' LOADING THE FILE FOR ', username)
        file_path = folder + '\\' + filename
        bitboards.generate_from_filename(usernames[i], 0, file_path)
        i += 1


def call_function_for_each_element_in_list(list):

    black_list = ['Joonaf', 'CrapCrusher', 'jpk1489', 'davebb', 'CyrCo', 'AKUMARGMASTER2019', 'jelovme', 'evgen417']

    for username in list:
        if username in black_list:
            print('NOT FOR THIS ONE')
        else:
            print(' LOADING THE FILE FOR ', username)
            bitboards.generate_from_username(username, 0)


def concatenate_files(dir_path):
    X = []
    Y = []

    for file in os.listdir(dir_path):
        if file.endswith('Y_bitboard.npy'):
            print('''aaaa''')
        else:
            x_data = np.load(os.path.join(dir_path, file))
            y_file = file.split('_bitboard.npy')[0] + '_Y_bitboard.npy'
            y_data = np.load(os.path.join(dir_path, y_file))

            X.append(x_data)
            Y.append(y_data)

    return np.concatenate(X), np.concatenate(Y)


def read_json_files(folder_name):
    df = []
    filenames = []
    for filename in os.listdir(folder_name):
        if filename.endswith('.json'):
            filenames.append(filename)
            with open(os.path.join(folder_name, filename), 'r') as f:
                json_df = pd.read_json(folder_name + "\\" + filename, lines=True)
                df.append(json_df)
    return df


def from_filename_get_username(filename):
    return filename


def split_dataframes(dataframes, filenames):

    split_dataframes = []
    usernames = []
    for index, df in enumerate(dataframes):
        if len(df) > 10000:
            num_splits = len(df) // 10000 + 1
            for i in range(num_splits):
                usernames.append(from_filename_get_username(filenames[index]))

            split_dfs = [df[i*10000:(i+1)*10000] for i in range(num_splits)]
            split_dataframes += split_dfs
        else:
            usernames.append(from_filename_get_username(filenames[index]))
            split_dataframes.append(df)

    return split_dataframes, usernames


def bitboard_to_board(bitboard):
    board = chess.Board()

    for index in np.ndindex((8, 8)):
        square = chess.square(index[1], 7 - index[0])
        board.set_piece_at(square, None)

    for piece in chess.PIECE_TYPES:
        for index in np.ndindex((8, 8)):
            if bitboard[piece-1][index[0]][index[1]] == 1:
                square = chess.square(index[1], 7 - index[0])
                color = chess.WHITE
                board.set_piece_at(square, chess.Piece(piece, color))

    for piece in chess.PIECE_TYPES:
        for index in np.ndindex((8, 8)):
            if bitboard[piece+5][index[0]][index[1]] == 1:
                square = chess.square(index[1], 7 - index[0])
                color = chess.BLACK
                board.set_piece_at(square, chess.Piece(piece, color))

    return board


def bitboard_to_move(bitboard):
    bitboard1 = bitboard[0]
    bitboard2 = bitboard[1]
    for index in np.ndindex((8, 8)):
        if bitboard1[index]:
            move1 = index

    for index in np.ndindex((8, 8)):
        if bitboard2[index]:
            move2 = index


    return


def go_on():
    df = read_json_files(r'C:\Users\paolo\OneDrive\Desktop\Final_project\Ludus_scacchi\Backend\data\pgn_games\pgn_games_1700')
    usernames = ['AKUMARGMASTER2019', 'CrapCrusher', 'CyrCo', 'davebb', 'evgen417', 'jelovme', 'Joonaf', 'jpk1489', 'Kl_Men', 'l0l0l0l0l0', 'lexparker', 'MilanLukic', 'nonAs', 'ojukillo', 'Sasj1', 'shadowman54', 'Sobir_55', 'viktor_lalka', 'WaywardQueer', 'xXCroGamer91Xx', 'ZheniaFrolov']
    split_df, usernames_split = split_dataframes(df, usernames)
    for i, dff in enumerate(split_df):
        dff.to_json(r'C:\Users\paolo\OneDrive\Desktop\Final_project\Ludus_scacchi\Backend\data\pgn_games\split_pgns\\' + 'split_n_' + str(i) + '.json')
    path = r'C:\Users\paolo\OneDrive\Desktop\Final_project\Ludus_scacchi\Backend\data\pgn_games\split_pgns'
    call_function_for_each_file('', path, usernames_split)
    return usernames_split







