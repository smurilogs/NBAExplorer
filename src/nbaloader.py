
import requests
import time
from filehandler import FileHandler

#localPath = 
#years = ['2015', '2016', '2017', '2018']
years = ['2015']


for year in years:
    file = requests.get(r'http://data.nba.com/data/10s/prod/v1/' + year + r'/teams.json')
    dic = file.json()
    FileHandler.create_directory(r'../data/10s/prod/v1/' + year)
    FileHandler.save_json_file(dic, r'../data/10s/prod/v1/' + year + r'/teams.json')    

for year in years:
    file = requests.get(r'http://data.nba.com/data/10s/prod/v1/' + year + r'/players.json')
    dic = file.json()
    FileHandler.create_directory(r'../data/10s/prod/v1/' + year)
    FileHandler.save_json_file(dic, r'../data/10s/prod/v1/' + year + r'/players.json')

for year in years:
    file = requests.get(r'http://data.nba.com/data/10s/prod/v1/' + year + r'/coaches.json')
    dic = file.json()
    FileHandler.create_directory(r'../data/10s/prod/v1/' + year)
    FileHandler.save_json_file(dic, r'../data/10s/prod/v1/' + year + r'/coaches.json')

games = []

for year in years:
    file = requests.get(r'http://data.nba.com/data/10s/prod/v1/' + year + r'/schedule.json')
    dic = file.json()
    FileHandler.create_directory(r'../data/10s/prod/v1/' + year) 
    FileHandler.save_json_file(dic, r'../data/10s/prod/v1/' + year + r'/schedule.json')    
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