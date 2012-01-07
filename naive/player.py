class Player:

    def __init__(self):
        self.CSLid = -1 # ID for CSL url
        self.character = '' # character.code
        self.race = -1 # race: {0: zerg, 1: protoss, 2: terran}
        self.league = '' # league: {10: gm, 11: master, 12: diamond,...}
        self.points = 0 # number of points in division on CSL profile
        self.record = {} # record[race] = (win, loss) for 1v1 games
        self.match = {} # match[id] = [opponent, map, is_win]
        self.maps = {} # maps[map] = # of plays on that map for 1v1 games
        self.wins = {} # wins[map] = # of wins on that map for 1v1 games
        self.teamgame = {} # teamgame[partner] = [games]
        self.teamgame_race = {} # teamgame[race] = number of team games played
        self.teamwins_race = {} # teamgame[race] = number of team games won
        self.ace = 0 # number of times player has played ace

    def add_id(self, CSLid):
        self.CSLid = CSLid

    def add_character(self, character):
        self.character = character
    def add_race(self, race):
        self.race = race
    def add_league(self, league):
        self.league = league

    def add_points(self, points):
        self.points = points

    # record given in CSL profile: vs P, Z, T
    def add_record(self, race, record):
        self.record[race] = record # (win, loss)

    def add_match(self, matchid, opponent, match_map, is_win):
        self.match[matchid] = [match_map, is_win]
        #self.match[matchid] = [opponent, match_map, is_win]

    def add_map(self, match_map):
        if match_map not in self.maps.keys():
            self.maps[match_map] = 1
        else:
            self.maps[match_map] += 1

    def add_win(self, match_map):
        if match_map not in self.wins.keys():
            self.wins[match_map] = 1
        else:
            self.wins[match_map] += 1
           
    def add_teamgame(self, partner, your_race, partner_race, match_map, is_win):
        game = [your_race, partner_race, match_map, is_win]
        if partner not in self.teamgame.keys():
            self.teamgame[partner] = [game] 
        else:
            self.teamgame[partner].append(game)

    def add_teammap(self, partner, match_map, teamwin):
        game = self.teamgame[partner].pop()
        new_game = [game[0], game[1], match_map, teamwin]
        self.teamgame[partner].append(new_game)

    def add_teamgame_race(self, race):
        if race not in self.teamgame_race.keys():
            self.teamgame_race[race] = 1
        else:
            self.teamgame_race[race] += 1

    def add_ace(self):
        self.ace += 1


    def print_values(self): 
        print "character: " + self.character
        print "race: " + self.race
        if 'not found' not in self.league:
            print "league: " + self.league
        if 'not found' not in self.points: 
            print "points: " + self.points
        print "record: " + str(self.record)
        if self.match:
            print "match: " + str(self.match) 
        if self.maps:
            print "maps: " + str(self.maps)
        if self.wins:
            print "wins: " + str(self.wins)
        if self.ace:    
            print "ace: " + str(self.ace)
        if self.teamgame:
            print "teamgame: " + str(self.teamgame)
        if self.teamgame_race:
            print "teamgame_race: " + str(self.teamgame_race)



