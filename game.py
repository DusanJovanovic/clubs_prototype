class Game:

    def __init__(self, strng):
        game_data = strng.strip().split(',')
        self.date = game_data[0]
        self.home_team = game_data[1]
        self.home_country = game_data[2]
        self.home_result = game_data[3]
        self.away_team = game_data[4]
        self.away_country = game_data[5]
        self.away_result = game_data[6]
        self.stage = game_data[7]
        self.season = game_data[8]
    



