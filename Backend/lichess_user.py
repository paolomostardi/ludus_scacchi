

class LichessUser:
    def __init__(self, json_response):
        self.username = None
        try:
            if json_response['disabled']:
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

