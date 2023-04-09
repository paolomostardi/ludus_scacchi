import pandas

from Backend import count_users_with_most_games_from_lichess_api as count_users
from Backend import get_games_in_pgn_from_lichess_api as games_in_pgn
from Backend import from_PGN_generate_bitboards as generate_bitboard


class PipelineManager:
    def __init__(self, user_file='Backend/data/user_record.json'):
        self.user_file = user_file
        self.user_df = pandas.read_json(user_file)

        return

    # add data to the current rating range folder
    def add_data(self, user_rating=1700, rating_range=50, number_of_games=2000):

        users_df = self.get_list_of_users_by_rating(user_rating, rating_range)

        return

    def get_list_of_users_by_rating(self, user_rating, rating_range):
        user_df = self.user_df
        user_df =
        return user_df


