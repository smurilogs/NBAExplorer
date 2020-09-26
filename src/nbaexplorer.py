
import pandas as pd
from filehandler import FileHandler

from abc import ABC, abstractmethod
import json
import os
import requests

class NBAExplorer():
    
    def __init__(self, seasons):
        self.seasons = seasons

    def get_odds(self):

        odds = FileHandler.load_json_file(r'../data/gameurl_odds.json')
        odds_df = pd.DataFrame.from_dict(odds)

        odds_df = odds_df.rename(columns={"hBet365": "hOdd", "vBet365": "vOdd"})
        odds_df = odds_df[['gameUrl', 'seasonPart', 'hOdd', 'vOdd']]

        return odds_df

    def get_teams_df(self):

        temp_teams = []
        for season in self.seasons:

            file = requests.get(r'http://data.nba.com/data/10s/prod/v1/' + str(season) + r'/teams.json')
            #file = FileHandler.load_json_file(r'./data/10s/prod/v1/' + str(season) + r'/teams.json')
            dic = file.json()

            for p in dic['league']['standard']:
                temp_teams.append(p)

        teams = []
        for temp_team in temp_teams:
            team = {
                "teamId": str(temp_team['teamId']),
                "team": temp_team['tricode'],
                "confName": temp_team['confName'],
                "divName": temp_team['divName']
            }
            teams.append(team)

        teams_df = pd.DataFrame.from_dict(teams)
        teams_df = teams_df.drop_duplicates(subset = ['teamId'], keep = 'first')
        return teams_df

    def get_season_games_df(self, season):

        def get_winner(aHScore, aVScore):
            if(aHScore > aVScore):
                return 'H'
            else:
                return 'V'

        file = requests.get(r'http://data.nba.com/data/10s/prod/v1/' + str(season) + r'/schedule.json')
        #file = FileHandler.load_json_file(r'./data/10s/prod/v1/' + str(season) + r'/schedule.json')
        dic = file.json()

        games = []
        auxGames = dic['league']['standard']
        for auxGame in auxGames:
            if (auxGame['hTeam']['score'] is not None and auxGame['hTeam']['score'] != '') and (auxGame['vTeam']['score'] is not None and auxGame['vTeam']['score'] != ''):
                game = {
                    "season": season,
                    "gameId": str(auxGame['gameId']),
                    "periods": auxGame['period']['current'],
                    "date": int(auxGame['gameUrlCode'][:8]),
                    "gameUrl": auxGame['gameUrlCode'],
                    "hTeamId": str(auxGame['hTeam']['teamId']),
                    "hScore": int(auxGame['hTeam']['score']),
                    "vTeamId": str(auxGame['vTeam']['teamId']),
                    "vScore": int(auxGame['vTeam']['score']),
                    "deltaScore": int(auxGame['hTeam']['score']) - int(auxGame['vTeam']['score']),
                    "winner": get_winner(int(auxGame['hTeam']['score']), int(auxGame['vTeam']['score']))
                }
                games.append(game)

        games_df = pd.DataFrame.from_dict(games)

        teams_df = self.get_teams_df()
        teams_df = teams_df[['teamId', 'team']]

        games_df = games_df.join(teams_df.set_index('teamId'), on='hTeamId')
        games_df = games_df.rename(columns={"team": "hTeam"})
        
        games_df = games_df.join(teams_df.set_index('teamId'), on='vTeamId')
        games_df = games_df.rename(columns={"team": "vTeam"})

        #odds_df = self.get_odds()
        #games_df = games_df.join(odds_df.set_index('gameUrl'), on='gameUrl')

        #games_df = games_df.drop(['hTeamId', 'vTeamId'], axis = 1)
        #games_df = games_df[['season', 'seasonPart', 'date', 'gameId', 'gameUrl', 'periods', 'hTeam', 'vTeam', 'hScore', 'vScore', 'hOdd', 'vOdd', 'winner', 'deltaScore']]
        games_df = games_df[['season', 'date', 'gameId', 'gameUrl', 'periods', 'hTeam', 'vTeam', 'hScore', 'vScore', 'winner', 'deltaScore']]        
        return games_df

    def get_games_df(self):

        df = self.get_season_games_df(2015)
        df = df.append(self.get_season_games_df(2016))
        df = df.append(self.get_season_games_df(2017))
        df = df.append(self.get_season_games_df(2018))
        df = df.append(self.get_season_games_df(2019))

        #df = df.loc[(df['seasonPart'] == 'REGULAR') | (df['seasonPart'] == 'PLAYOFFS')]
        df = df.reset_index(drop=True)
        return df

    @staticmethod
    def _get_period_second(clock):
        if(len(clock) == 5):
            sec = 720 - (60 * int(clock[:2]) + int(clock[-2:]))
            return sec
        else:
            auxClock =  clock[:5]
            sec = 720 - (60 * int(auxClock[:2]) + int(auxClock[-2:]))
            return sec

    @staticmethod
    def _get_game_second(clock, aPeriod):
        if(len(clock) == 5):
            sec = (720 - (60 * int(clock[:2]) + int(clock[-2:]))) + (720 * (aPeriod - 1))
            return sec
        else:
            auxClock =  clock[:5]
            sec = (720 - (60 * int(auxClock[:2]) + int(auxClock[-2:]))) + (720 * (aPeriod - 1))
            return sec

    @staticmethod
    def _get_delta_score(aHScore, aVScore):
        deltaScore = aHScore - aVScore
        return deltaScore

    def get_plays_df(self, game_id):

        games_df = self.get_games_df()
        game_df = games_df.loc[games_df['gameId'] == game_id]

        plays = []
        for index, row in game_df.iterrows():

            auxPlays = []
            for i in range(row['periods']):

                file = requests.get(r'http://data.nba.com/data/10s/prod/v1/' + str(row['date']) + r'/' + row['gameId'] + r'_pbp_' + str(i + 1) + r'.json')
                dic = file.json()

                for p in dic['plays']:
                    p['period'] = i + 1
                    auxPlays.append(p)

            for auxPlay in auxPlays:
                play = {
                    "gameId": row['gameId'],
                    "date": row['date'],
                    "clock": auxPlay['clock'],
                    "gameSecond": self._get_game_second(auxPlay['clock'], auxPlay['period']),
                    "periodSecond": self._get_period_second(auxPlay['clock']),
                    "period": auxPlay['period'],
                    "hScore": int(auxPlay['hTeamScore']),
                    "vScore": int(auxPlay['vTeamScore']),
                    "deltaScore": self._get_delta_score(int(auxPlay['hTeamScore']), int(auxPlay['vTeamScore'])),
                    "teamId": auxPlay['teamId'],
                    "description": auxPlay['description']
                }
                plays.append(play)

        plays_df = pd.DataFrame.from_dict(plays)

        teams_df = self.get_teams_df()
        teams_df = teams_df[['teamId', 'team']]

        plays_df = plays_df.join(teams_df.set_index('teamId'), on='teamId')
        plays_df = plays_df.drop(['teamId'], axis = 1)

        plays_df = plays_df[['date', 'gameId', 'gameSecond', 'period', 'periodSecond', 'hScore', 'vScore', 'deltaScore','team', 'description']]
        return plays_df
