import pandas

from Backend import count_users_with_most_games_from_lichess_api as count_users
from Backend import get_games_in_pgn_from_lichess_api as games_in_pgn
from Backend import from_PGN_generate_bitboards as generate_bitboard


class PipelineManager:
    def __init__(self, user_file='Backend/data/user_record.csv'):

        self.user_file = user_file
        self.user_df = pandas.read_csv(user_file)

        self.user_rating = 1700
        self.rating_range = 50
        self.current_range_df = self.get_list_of_users_by_current_rating()

        return

    # add bitboards to the current rating range folder
    def add_data(self, number_of_games=2000):
        self.current_range_df = self.get_list_of_users_by_current_rating()

        if self.bitboard_left_to_generate() >= number_of_games:
            self.generate_bitboards(number_of_games)

        elif self.bitboard_left_to_generate() + self.pgn_left_to_download() >= number_of_games:
            self.add_pgn(number_of_games - self.bitboard_left_to_generate())
            self.generate_bitboards(number_of_games)

        else:
            self.add_users(number_of_games)
            self.add_pgn(number_of_games - self.bitboard_left_to_generate())
            self.generate_bitboards(number_of_games)

        return

    def get_list_of_users_by_current_rating(self):

        lower_bound = self.user_rating - self.rating_range
        upper_bound = self.user_rating + self.rating_range
        df = self.user_df

        df = df[(df['rating'] >= lower_bound) & (df['rating'] <= upper_bound)]

        self.current_range_df = df

        return df

    def bitboard_left_to_generate(self):
        amount_of_games_downloaded = self.current_range_df['games_downloaded']
        amount_of_bitboard_games = self.current_range_df['bitboard_games']
        bitboard_left = amount_of_games_downloaded - amount_of_bitboard_games
        return bitboard_left

    def pgn_left_to_download(self):
        amount_of_games_downloaded = self.current_range_df['games_downloaded']
        total_amount_of_games = self.current_range_df['total_amount_of_games']
        pgn_left = total_amount_of_games - amount_of_games_downloaded
        return pgn_left

    def generate_bitboards(self, number_of_games):

        if self.bitboard_left_to_generate() - number_of_games <= 0:
            self.add_pgn(number_of_games)

        current_df = self.current_range_df
        users_left = (current_df['games_downloaded'] - current_df['bitboard_games'] >= 0)
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

    def save_df(self):
        self.user_df.to_csv(self.user_file)
        return

    def add_pgn(self, number_of_games):
        if self.pgn_left_to_download() < number_of_games:
            self.add_users(number_of_games)


        return

    def add_users(self, number_of_games):
        return


    def set_user_rating_and_range(self, user_rating, rating_range):
        return