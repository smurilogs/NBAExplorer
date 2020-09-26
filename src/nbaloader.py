
import requests
import time
from filehandler import FileHandler

def store_teams(years):
    for year in years:
        file = requests.get(r'http://data.nba.com/data/10s/prod/v1/' + str(year) + r'/teams.json')
        dic = file.json()
        FileHandler.create_directory(r'../data/10s/prod/v1/' + str(year))
        FileHandler.save_json_file(dic, r'../data/10s/prod/v1/' + str(year) + r'/teams.json')    

def store_players(years):
    for year in years:
        file = requests.get(r'http://data.nba.com/data/10s/prod/v1/' + str(year) + r'/players.json')
        dic = file.json()
        FileHandler.create_directory(r'../data/10s/prod/v1/' + str(year))
        FileHandler.save_json_file(dic, r'../data/10s/prod/v1/' + str(year) + r'/players.json')

def store_coaches(years):
    for year in years:
        file = requests.get(r'http://data.nba.com/data/10s/prod/v1/' + str(year) + r'/coaches.json')
        dic = file.json()
        FileHandler.create_directory(r'../data/10s/prod/v1/' + str(year))
        FileHandler.save_json_file(dic, r'../data/10s/prod/v1/' + str(year) + r'/coaches.json')

def store_games(years):
    games = []
    for year in years:
       
        file = requests.get(r'http://data.nba.com/data/10s/prod/v1/' + str(year) + r'/schedule.json')
        dic = file.json()
       
        FileHandler.create_directory(r'../data/10s/prod/v1/' + str(year)) 
        FileHandler.save_json_file(dic, r'../data/10s/prod/v1/' + str(year) + r'/schedule.json')    
        
        for item in dic['league']['standard']:
            game = {
                "season": int(year),
                "gameId": item['gameId'],
                "date": int(item['gameUrlCode'][:8]),
                "periods": int(item['period']['current'])
            }
            games.append(game)
        time.sleep(5)

        FileHandler.create_directory(r'../data/')
        FileHandler.save_json_file(games, r'../data/season_date_gameid.json')

if __name__ == '__main__':
    
    years = [2015, 2016, 2017, 2018, 2019, 2020]
    #years = ['2015']
    
    store_teams(years)
    store_players(years)
    store_coaches(years)
    store_games(years)

