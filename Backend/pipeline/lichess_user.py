
class LichessUser:
    def __init__(self, json_response=None, json_file_row=None):
        self.username = None
        if json_response:
            try:
                if json_response['disabled']:
                    self.username = json_response['username']

                    self.blitz_rating = 0
                    self.rapid_rating = 0
                    self.classical_rating = 0

                    self.blitz_amount_of_games = 0
                    self.rapid_amount_of_games = 0
                    self.classical_amount_of_games = 0

                    self.total_amount_of_games = 0
                    self.total_slow_games = 0
                    self.games_downloaded = 0
                    self.bitboard_games = 0
                    self.searched_games = 0
                    return

            except KeyError:

                self.username = json_response['username']

                self.blitz_rating = json_response['perfs']['blitz']['rating']
                self.rapid_rating = json_response['perfs']['rapid']['rating']
                self.classical_rating = json_response['perfs']['classical']['rating']

                self.blitz_amount_of_games = json_response['perfs']['blitz']['games']
                self.rapid_amount_of_games = json_response['perfs']['rapid']['games']
                self.classical_amount_of_games = json_response['perfs']['classical']['games']

                self.total_amount_of_games = self.blitz_amount_of_games + self.rapid_amount_of_games + self.classical_amount_of_games
                self.total_slow_games = self.rapid_amount_of_games + self.classical_amount_of_games

                self.games_downloaded = 0
                self.bitboard_games = 0
                self.searched_games = 0

        elif json_file_row:
            self.username = json_file_row['username']

            self.blitz_rating = json_file_row['blitz_rating']
            self.rapid_rating = json_file_row['rapid_rating']
            self.classical_rating = json_file_row['classical_rating']

            self.blitz_amount_of_games = json_file_row['blitz_amount_of_games']
            self.rapid_amount_of_games = json_file_row['rapid_amount_of_games']
            self.classical_amount_of_games = json_file_row['classical_amount_of_games']

            self.total_amount_of_games = json_file_row['total_amount_of_games']
            self.total_slow_games = json_file_row['total_slow_games']
            self.games_downloaded = json_file_row['games_downloaded']
            self.bitboard_games = json_file_row['bitboard_games']
            self.searched_games = json_file_row['searched_games']

    def get_rating_range(self):
        rating_range = self.rapid_rating % 100
        if rating_range > 50:
            rating_range = 100 - rating_range + self.rapid_rating
        else:
            rating_range = self.rapid_rating - rating_range

        return rating_range


def get_rating_range(rating):
    rating_range = rating % 100
    if rating_range > 50:
        rating_range = 100 - rating_range + rating
    else:
        rating_range = rating - rating_range

    return rating_range