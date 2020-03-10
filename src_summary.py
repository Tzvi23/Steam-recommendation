import json
import requests
import os
import csv

API_KEY = "62cf6f931b24f3128aec27128c0eff1d"


def idgb_request(api_key, endpoint, body):
    # defining the api-endpoint
    API_ENDPOINT = "https://api-v3.igdb.com/" + endpoint

    headers = {'user-key': api_key}
    # body = "fields *; search \"" + game + "\";"

    # sending post request and saving response as response object
    r = requests.post(API_ENDPOINT, data=body, headers=headers)

    return r.text


if not os.path.isdir('summaryAnalyze'):
    os.mkdir('summaryAnalyze')

if not os.path.isfile('summaryAnalyze/game_summary.csv'):
    games = dict()
    with open('steamData/item_info.dat', 'r') as items:
        print('[!] Loading all the game names in file')
        data = items.readlines()
        for entry in data:
            games[entry.replace("\n", "").split("\t")[1]] = ''
        games.pop('Game Name')

    print('[!] Downloading all the summaries and storing in dict format')
    for game_name in games.keys():
        ans = idgb_request(API_KEY, 'games', 'fields *; search \"' + game_name + '\" ;')
        text = json.loads(ans)
        try:
            games[game_name] = text[0]['summary']
        except (KeyError, IndexError):
            games[game_name] = -1

    print('[!] Writing all the data in csv format file  game_summary.csv')
    with open('summaryAnalyze/game_summary.csv', mode='w') as summaryFile:
        summaryWriter = csv.writer(summaryFile, delimiter=',')
        summaryWriter.writerow(['game_name', 'summary'])  # Write header
        for game_name in games.keys():
            summaryWriter.writerow([game_name, games[game_name]])
