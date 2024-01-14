import pandas

from Backend.pipeline import count_users_with_most_games_from_lichess_api as count_users
from Backend.pipeline import get_games_in_pgn_from_lichess_api as games_in_pgn
from Backend.pipeline import from_PGN_generate_bitboards as generate_bitboard


class PipelineManager:
    def __init__(self, user_file='Backend/data/user_record.csv', pgn_folder_first_part='Backend/data/pgn_games'):

        self.user_file = user_file
        self.user_df = pandas.read_csv(user_file)

        self.user_rating = 1700
        self.rating_range = 50
        self.current_range_df = self.get_df_of_users_by_current_rating()
        self.pgn_folder_first_part = pgn_folder_first_part

        return

    # add bitboards to the current rating range folder
    def add_data(self, number_of_games=2000):

        print(' adding', str(number_of_games), 'games')
        self.current_range_df = self.get_df_of_users_by_current_rating()

        if self.bitboard_left_to_generate() >= number_of_games:
            print('converting to bitboards')
            self.generate_bitboards(number_of_games)

        elif self.bitboard_left_to_generate() + self.pgn_left_to_download() >= number_of_games:
            print('first downloading some games and then converting to bitboards')
            self.add_pgn(number_of_games - self.bitboard_left_to_generate())
            print('now converting to bitboards')
            self.generate_bitboards(number_of_games)

        else:
            print('first searching for more users')
            self.add_users(number_of_games)
            print('downloading some games')
            self.add_pgn(number_of_games - self.bitboard_left_to_generate())
            print('generating some bitboards')
            self.generate_bitboards(number_of_games)

        return

    def get_pgn_folder(self):
        return self.pgn_folder_first_part + str(self.user_rating) + '_pgn_games'

    def get_df_of_users_by_current_rating(self):

        lower_bound = self.user_rating - self.rating_range
        upper_bound = self.user_rating + self.rating_range
        df = self.user_df

        df = df[(df['rapid_rating'] >= lower_bound) & (df['rapid_rating'] <= upper_bound)]

        self.current_range_df = df

        return df

    def bitboard_left_to_generate(self):
        amount_of_games_downloaded = self.current_range_df['games_downloaded']
        amount_of_bitboard_games = self.current_range_df['bitboard_games']
        bitboard_left = amount_of_games_downloaded - amount_of_bitboard_games
        return bitboard_left.sum()

    def pgn_left_to_download(self):
        amount_of_games_downloaded = self.current_range_df['games_downloaded']
        total_amount_of_games = self.current_range_df['total_amount_of_games']
        pgn_left = total_amount_of_games - amount_of_games_downloaded
        return pgn_left.sum()

    def generate_bitboards(self, number_of_games):

        if self.bitboard_left_to_generate() - number_of_games <= 0:
            self.add_pgn(number_of_games)

        current_df = self.current_range_df
        users_left = (current_df['games_downloaded'] - current_df['bitboard_games'] > 0)
        users_with_bitboards_left_to_generate = current_df[users_left]

        bit_boards_generated = 0
        index = 0
        while bit_boards_generated < number_of_games:
            user = users_with_bitboards_left_to_generate.iloc[index]
            bitboards_already_generated_for_user = user['bitboard_games']
            total_pgn_available = user['games_downloaded']
            username = user['username']
            generate_bitboard.generate_from_username(username, bitboards_already_generated_for_user)
            index += 1
            bit_boards_generated += total_pgn_available - bitboards_already_generated_for_user
            self.change_user_bitboard(user, total_pgn_available)
        self.save_df()

    def change_user_bitboard(self, user, bitboard_amount):
        username = user['username']
        self.user_df.loc[self.user_df['username'] == username, 'bitboard_games'] = bitboard_amount
        return

    def change_user_pgn(self, user, pgn_amount):
        username = user['username']
        self.user_df.loc[self.user_df['username'] == username, 'games_downloaded'] = pgn_amount
        return

    def save_df(self):
        self.user_df.to_csv(self.user_file)
        print('saving at :', self.user_file)
        return

    def add_pgn(self, number_of_games):
        if self.pgn_left_to_download() < number_of_games:
            self.add_users(number_of_games)

        current_df = self.current_range_df
        users_left = (current_df['total_amount_of_games'] - current_df['games_downloaded'] > 0)
        users_with_games_left_to_download = current_df[users_left]

        games_downloaded = 0
        index = 0

        while games_downloaded < number_of_games:

            user = users_with_games_left_to_download.iloc[index]
            games_already_downloaded = user['games_downloaded']
            total_pgn_available = user['total_amount_of_games']
            username = user['username']

            games_in_pgn.get_pgn_games_from_username(username, self.get_pgn_folder())
            index += 1
            games_downloaded += total_pgn_available - games_already_downloaded
            self.change_user_pgn(user, total_pgn_available)

        self.save_df()

        return

    def add_users(self, number_of_games):

        current_df = self.current_range_df
        count_users.from_amount_of_games_add_user_to_file(number_of_games, self.user_file, self.get_pgn_folder())

        return

    def set_user_rating_and_range(self, user_rating, rating_range):
        self.user_rating = user_rating
        self.rating_range = rating_range

        return

    def add_user_from_username(self, username):
        user = count_users.get_user_info(username)
        user = vars(user)
        self.user_df = self.user_df.append(user, ignore_index=True)
        self.save_df()

    def print_report(self):

        total_slow_games = sum(self.user_df["total_slow_games"])
        total_games = sum(self.user_df["total_amount_of_games"])

        games_downloaded = sum(self.user_df["games_downloaded"])
        bitboard_games = sum(self.user_df["bitboard_games"])
        searched_games = sum(self.user_df["searched_games"])
        
        print()
        print('printing current report')
        print()

        print(self.user_df)
        print(f'there are currently {len(self.user_df)} users registered')
        print()
        
        print(f'total games available : {total_games} ({total_slow_games} slow )')
        print()

        print(f'total games downloaded : {games_downloaded} ')
        print()

        print(f'total bitboards : {bitboard_games} ')
        print()

        print(f'searched games : {searched_games} ')
        print()

pipe = PipelineManager()
pipe.print_report()