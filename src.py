import sys
import os
import json
import requests
import csv
from datetime import datetime
import copy
import pickle

from vector_class import Vector
from user_vector_class import userVector
from user_vector_data_class import userVectorData
from new_user_vector import new_user

API_KEY = "62cf6f931b24f3128aec27128c0eff1d"


def idgb_request(api_key, endpoint, body):
    # defining the api-endpoint
    API_ENDPOINT = "https://api-v3.igdb.com/" + endpoint

    headers = {'user-key': api_key}
    # body = "fields *; search \"" + game + "\";"

    # sending post request and saving response as response object
    r = requests.post(API_ENDPOINT, data=body, headers=headers)

    return r.text


# region download data from IGDB
def download_data_idgb():
    files = os.listdir("IGDBData")
    for game in games:
        if game + ".txt" not in files:
            if sys.platform == "darwin" or sys.platform == "linux":
                DirFile = "IGDBData" + "/"
            else:
                DirFile = "IGDBData" + "\""

            # defining the api-endpoint
            API_ENDPOINT = "https://api-v3.igdb.com/games"

            headers = {'user-key': '62cf6f931b24f3128aec27128c0eff1d'}
            body = "fields *; search \"" + game + "\";"

            # sending post request and saving response as response object
            r = requests.post(API_ENDPOINT, data=body, headers=headers)

            game = game.replace("/", "")
            with open(DirFile + game + ".txt", "w") as writer:
                writer.write(r.text)
    print("Finished!")


# endregion


games = list()
games_list = list()
with open("steamData/item_info.dat") as file:
    print("Loading data from item_info.dat ...")
    for row in file:
        g = row.replace("\n", "").split("\t")
        games.append(g[1])
        games_list.append(g[0] + '=' + g[1])
games.pop(0)
games_list.pop(0)


def game_list():
    return games_list


# Checks if IGDBD data dir exists and needs to download data
if not os.path.isdir("IGDBData"):
    download_data_idgb()

# idgb_params = ['id', 'age_ratings', 'first_release_date', 'game_modes', 'genres', 'involved_companies', 'name',
#                'platforms', 'aggregated_rating']


def create_GameInfoFile(platforms_enum, enum_Genres, enum_age_ratings, companies_enum, force_overwrite=False, readable=True, file_name='games_info.csv'):
    enum_GameModes = {1: 'single player', 2: 'multiplayer', 3: 'co-operative', 4: 'split screen', 5: 'MMO'}
    gamesInfo = dict()
    if os.path.isfile(file_name):
        if not force_overwrite:
            while True:
                ans = input("The file " + file_name + " exists. Overwrite? y/n \nAnswer: ")
                if ans == 'y' or ans == 'n':
                    break
            if ans == 'y':
                force_overwrite = True
                print("Force overwrite enabled! " + file_name + " overwritten!")
            else:
                print(file_name + " exists.")
                return
    if not os.path.isfile(file_name) or force_overwrite is True:
        with open(file_name, mode='w') as csv_file:
            fieldsNames = ['steam_id', 'idgb_id', 'game_name', 'first_release_date', 'genres', 'age_ratings',
                           'aggregated_rating', 'rating', 'platforms', 'game_modes', 'involved_companies']
            writer = csv.DictWriter(csv_file, fieldnames=fieldsNames)
            writer.writeheader()
            with open("steamData/item_info.dat") as file:
                for row in file:
                    gamesInfo.clear()  # Reset gamesInfo dict
                    infoTuple = row.replace("\n", "").split("\t")
                    if infoTuple[0] != "Game_ID" and infoTuple[1] != "Game Name":  # ignore the header of the file
                        infoTuple[1] = infoTuple[1].replace("/", "")
                        gamesInfo['steam_id'] = infoTuple[0]
                        gamesInfo['game_name'] = infoTuple[1]
                        with open("IGDBData/" + gamesInfo['game_name'] + ".txt") as jsonData:
                            data = json.load(jsonData)
                            found = False
                            for subData in data:
                                subData['name'] = subData['name'].replace(":", "")
                                if subData['name'].upper() == gamesInfo['game_name'].upper():
                                    found = True
                                    print("Correct Game Dict for {0}".format(gamesInfo['game_name']))
                                    gamesInfo['idgb_id'] = subData.get('id', -1)
                                    timeStamp = subData.get('first_release_date', -1)
                                    if readable:  # converts Unix time stamps to readable Date
                                        if timeStamp != -1:
                                            gamesInfo['first_release_date'] = datetime.fromtimestamp(timeStamp)
                                        else:
                                            gamesInfo['first_release_date'] = timeStamp
                                    else:
                                        gamesInfo['first_release_date'] = timeStamp
                                    genre = subData.get('genres', -1)
                                    if readable:
                                        if genre != -1:
                                            if isinstance(genre, int):
                                                gamesInfo['genres'] = enum_Genres[genre]
                                            else:
                                                for i in range(len(genre)):
                                                    genre[i] = enum_Genres[genre[i]]
                                                gamesInfo['genres'] = genre
                                        else:
                                            gamesInfo['genres'] = genre
                                    else:
                                        gamesInfo['genres'] = genre
                                    age = subData.get('age_ratings', -1)
                                    if readable:
                                        if age != -1:
                                            if isinstance(age, int):
                                                gamesInfo['age_ratings'] = enum_age_ratings[age]
                                            else:
                                                for i in range(len(age)):
                                                    age[i] = enum_age_ratings[age[i]]
                                                gamesInfo['age_ratings'] = age
                                        else:
                                            gamesInfo['age_ratings'] = age
                                    else:
                                        gamesInfo['age_ratings'] = age
                                    gamesInfo['rating'] = subData.get('rating', -1)
                                    gamesInfo['aggregated_rating'] = subData.get('aggregated_rating', -1)
                                    platforms = subData.get('platforms', -1)
                                    if readable:
                                        if platforms != -1:
                                            if isinstance(platforms, int):
                                                gamesInfo['platforms'] = platforms_enum[platforms]
                                            else:
                                                for i in range(len(platforms)):
                                                    platforms[i] = platforms_enum[platforms[i]]
                                                gamesInfo['platforms'] = platforms
                                        else:
                                            gamesInfo['platforms'] = platforms
                                    else:
                                        gamesInfo['platforms'] = platforms
                                    gameModes = subData.get('game_modes', -1)
                                    if readable:  # Converts Game modes
                                        if gameModes != -1:
                                            for i in range(len(gameModes)):
                                                gameModes[i] = enum_GameModes[gameModes[i]]
                                            gamesInfo['game_modes'] = gameModes
                                        else:
                                            gamesInfo['game_modes'] = gameModes
                                    else:
                                        gamesInfo['game_modes'] = gameModes
                                    companies = subData.get('involved_companies', -1)
                                    if readable:
                                        if companies != -1:
                                            if isinstance(companies, int):
                                                gamesInfo['involved_companies'] = companies_enum[companies]
                                            else:
                                                for i in range(len(companies)):
                                                    companies[i] = companies_enum[companies[i]]
                                                gamesInfo['involved_companies'] = set(companies)
                                        else:
                                            gamesInfo['involved_companies'] = companies
                                    else:
                                        gamesInfo['involved_companies'] = companies
                                    writer.writerow(gamesInfo)
                                    break
                            if not found:
                                print("[!!] No dict found for {0}".format(gamesInfo['game_name']))


def create_platform_enum():
    """
    Creates a csv file named enum_Platforms.csv that contains all the keys and names of platforms
    For better understanding of the data set.
    The data is gathered via post request to the IDGB site.
    :return: enum_Platforms dict
    """
    if not os.path.isfile("enum_Platforms.csv"):
        enum_Platforms = dict()
        with open("games_info.csv", mode='r') as csv_read:
            reader = csv.DictReader(csv_read)
            for line in reader:
                currentPlatforms = line['platforms']
                currentPlatformsList = json.loads(currentPlatforms)
                if isinstance(currentPlatformsList, int):
                    if enum_Platforms.get(plat) is None:  # Checks if key exists in dict
                        body = 'fields *; where id = ' + str(plat) + ';'
                        ans = idgb_request(API_KEY, 'platforms', body)
                        json_ans = json.loads(ans)
                        enum_Platforms[plat] = json_ans[0]['abbreviation']
                        print(enum_Platforms)
                else:
                    for plat in currentPlatformsList:
                        if enum_Platforms.get(plat) is None:  # Checks if key exists in dict
                            body = 'fields *; where id = ' + str(plat) + ';'
                            ans = idgb_request(API_KEY, 'platforms', body)
                            json_ans = json.loads(ans)
                            try:
                                enum_Platforms[plat] = json_ans[0]['abbreviation']
                            except KeyError:
                                enum_Platforms[plat] = json_ans[0]['name']
                            print(enum_Platforms)

        with open("enum_Platforms.csv", mode='w') as csv_write:
            enum_writer = csv.writer(csv_write, delimiter=',')

            for key in enum_Platforms.keys():
                enum_writer.writerow([key, enum_Platforms[key]])

        return enum_Platforms
    else:
        enum_Platforms = dict()
        with open("enum_Platforms.csv", mode='r') as csv_read:
            reader = csv.reader(csv_read, delimiter=',')
            for line in reader:
                enum_Platforms[int(line[0])] = line[1]
        return enum_Platforms


def create_enum(file_name, enum_name, args):
    if not os.path.isfile(file_name + ".csv"):
        enum = dict()
        with open("games_info.csv", mode='r') as csv_read:
            reader = csv.DictReader(csv_read)
            for line in reader:
                currentPlatforms = line[enum_name]
                currentPlatformsList = json.loads(currentPlatforms)
                if isinstance(currentPlatformsList, int):  # Checks if there is only one value than its int, not list of ints
                    if enum.get(plat) is None:  # Checks if key exists in dict
                        body = 'fields *; where id = ' + str(plat) + ';'
                        ans = idgb_request(API_KEY, enum_name, body)
                        json_ans = json.loads(ans)
                        enum[plat] = json_ans[0][args[0]]
                        print(enum)
                else:
                    for plat in currentPlatformsList:
                        if enum.get(plat) is None:  # Checks if key exists in dict
                            body = 'fields *; where id = ' + str(plat) + ';'
                            ans = idgb_request(API_KEY, enum_name, body)
                            json_ans = json.loads(ans)
                            try:
                                enum[plat] = json_ans[0][args[0]]
                            except KeyError:
                                enum[plat] = json_ans[0][args[1]]
                            print(enum)

        with open(file_name + ".csv", mode='w') as csv_write:
            enum_writer = csv.writer(csv_write, delimiter=',')

            for key in enum.keys():
                enum_writer.writerow([key, enum[key]])

        return enum
    else:
        enum = dict()
        with open(file_name + ".csv", mode='r') as csv_read:
            reader = csv.reader(csv_read, delimiter=',')
            for line in reader:
                enum[int(line[0])] = line[1]
        return enum


def convert_age_ratings(file_name):
    age_ratings_category = {1: 'ESRB', 2: 'PEGI'}
    age_ratings_rating = {1: '3', 2: '7', 3: '12', 4: '16', 5: '18', 6: 'RP', 7: 'EC', 8: 'E', 9: 'E10', 10: 'T',
                          11: 'M', 12: 'AO'}
    if not os.path.isfile(file_name + '.csv'):
        enum = dict()
        with open("games_info.csv", mode='r') as csv_read:
            reader = csv.DictReader(csv_read)
            for line in reader:
                current_rating = json.loads(line['age_ratings'])
                if current_rating != -1:
                    if isinstance(current_rating, int):
                        if enum.get(current_rating) is None:
                            body = 'fields *; where id = ' + str(current_rating) + ';'
                            ans = idgb_request(API_KEY, 'age_ratings', body)
                            json_ans = json.loads(ans)
                            category = age_ratings_category[json_ans['category']]
                            rating = age_ratings_rating[json_ans['rating']]
                            enum[current_rating] = category + " " + rating
                            print(enum)
                    else:
                        for rating in current_rating:
                            if enum.get(rating) is None:
                                body = 'fields *; where id = ' + str(rating) + ';'
                                ans = idgb_request(API_KEY, 'age_ratings', body)
                                json_ans = json.loads(ans)
                                category = age_ratings_category[json_ans[0]['category']]
                                rating_value = age_ratings_rating[json_ans[0]['rating']]
                                enum[rating] = category + " " + rating_value
                                print(enum)

        with open(file_name + ".csv", mode='w') as csv_write:
            enum_writer = csv.writer(csv_write, delimiter=',')

            for key in enum.keys():
                enum_writer.writerow([key, enum[key]])

        return enum
    else:
        enum = dict()
        with open(file_name + ".csv", mode='r') as csv_read:
            reader = csv.reader(csv_read, delimiter=',')
            for line in reader:
                enum[int(line[0])] = line[1]
        return enum


def create_company_enum(file_name):
    enum_comp_id = dict()
    enum_comp_name = dict()
    total_enum = dict()
    if not os.path.isfile(file_name + '.csv'):
        if not os.path.isfile(file_name + "_IDs.csv"):
            with open("games_info.csv", mode='r') as csv_read:
                reader = csv.DictReader(csv_read)
                for line in reader:
                    current_companies = json.loads(line['involved_companies'])
                    if current_companies != -1:
                        if isinstance(current_companies, int):
                            if enum_comp_id.get(current_companies) is None:
                                body = 'fields *; where id = ' + str(current_companies) + ';'
                                ans = idgb_request(API_KEY, 'involved_companies', body)
                                json_ans = json.loads(ans)
                                enum_comp_id[current_companies] = int(json_ans[0]['company'])
                                print(enum_comp_id)
                        else:
                            for comp in current_companies:
                                if enum_comp_id.get(comp) is None:
                                    body = 'fields *; where id = ' + str(comp) + ';'
                                    ans = idgb_request(API_KEY, 'involved_companies', body)
                                    json_ans = json.loads(ans)
                                    enum_comp_id[comp] = json_ans[0]['company']
                                    print(enum_comp_id)

            with open(file_name + "_IDs.csv", mode='w') as csv_write:
                enum_writer = csv.writer(csv_write, delimiter=',')

                for key in enum_comp_id.keys():
                    enum_writer.writerow([key, enum_comp_id[key]])

        with open(file_name + "_IDs.csv", mode='r') as csv_read:
            reader = csv.reader(csv_read, delimiter=',')
            for line in reader:
                enum_comp_id[int(line[0])] = int(line[1])

        for key in enum_comp_id.keys():
            if enum_comp_name.get(enum_comp_id[key]) is None:
                body = 'fields *; where id = ' + str(enum_comp_id[key]) + ';'
                ans = idgb_request(API_KEY, 'companies', body)
                json_ans = json.loads(ans)
                try:
                    enum_comp_name[enum_comp_id[key]] = json_ans[0]['slug']
                except KeyError:
                    enum_comp_name[enum_comp_id[key]] = json_ans[0]['name']
                print(enum_comp_name)

        with open(file_name + ".csv", mode='w') as csv_write:
            enum_writer = csv.writer(csv_write, delimiter=',')

            for key in enum_comp_name.keys():
                enum_writer.writerow([key, enum_comp_name[key]])

        for key in enum_comp_id.keys():
            total_enum[key] = enum_comp_name[enum_comp_id[key]]
    else:
        with open(file_name + "_IDs.csv", mode='r') as csv_read:
            reader = csv.reader(csv_read, delimiter=',')
            for line in reader:
                enum_comp_id[int(line[0])] = int(line[1])

        with open(file_name + ".csv", mode='r') as csv_read:
            reader = csv.reader(csv_read, delimiter=',')
            for line in reader:
                enum_comp_name[int(line[0])] = line[1]

        for key in enum_comp_id.keys():
            total_enum[key] = enum_comp_name[enum_comp_id[key]]
    return total_enum


def missing_lines_remove(file_name, max_empty_cells=8):
    if os.path.isfile(file_name):
        data_set = list()
        with open(file_name, mode='r') as csv_read:
            reader = csv.reader(csv_read)
            for line in reader:
                if line[0] == "steam_id":
                    header_enum = dict()
                    enum_header = dict()
                    for i in range(len(line)):
                        header_enum[line[i]] = i
                        enum_header[i] = line[i]
                    continue
                count = 0
                for cell in line:
                    if cell == '-1':
                        count = count + 1
                if count >= max_empty_cells:
                    continue
                else:
                    data_set.append(line)
        return data_set, header_enum, enum_header

    else:
        print("Error!! No " + file_name + " exists! Cant continue")
        exit(0)


def print_stats(data, header):
    stats = dict()
    for i in range(len(header)):
        stats[i] = 0
    total = len(data)
    for i in range(len(header)):
        for line in data:
            if line[i] == '-1':
                stats[i] += 1
    stats2 = dict()
    for key in stats.keys():
        stats2[header[key]] = stats[key]
    stats.clear()
    print("Number of missing values in current data set: ")
    for key in stats2.keys():
        print("{0} : {1}/{2} | Percentage : {3:2.2f}%".format(key, stats2[key], total, stats2[key]/total*100))


def rating_binning(value):
    val = float(value)
    if 0 <= val < 20:
        return 1
    elif 20 <= val < 40:
        return 2
    elif 40 <= val < 60:
        return 3
    elif 60 <= val < 80:
        return 4
    elif 80 <= val < 90:
        return 5
    elif 90 <= val <= 100:
        return 6
    else:
        return -1


def load_gameIds(filename="steamData/item_info.dat"):
    game_names = dict()
    with open(filename, mode='r') as data:
        firstRow = True
        for row in data:
            if firstRow:
                firstRow = False
                continue
            game_names[row.replace('\n', '').split('\t')[0]] = row.replace('\n', '').split('\t')[1]
    return game_names


game_Ids = load_gameIds()

enum_companies = create_company_enum("enum_Companies")
enum_Age_ratings = convert_age_ratings("enum_Age_Ratings")
enum_genres = create_enum("enum_Genres", "genres", ['slug', 'name'])
enum_Platforms = create_platform_enum()

# create_GameInfoFile(enum_Platforms, enum_genres, enum_Age_ratings, enum_companies)
# create_GameInfoFile(enum_Platforms, enum_genres, enum_Age_ratings, enum_companies, False, False, 'game_info_original.csv')
# TODO remove this comment section to print number of empty cells printing
# =====================================
# for i in range(1, 9):
#     print("Pre-process for {0}".format(i))
#     data_set, header_enum, enum_header = missing_lines_remove('games_info.csv', i)
#     print_stats(data_set, enum_header)
#     print("================================================")
#
# print("The chosen max empty cells is 3 as its best fit. \nAnd age_ratings & aggregated_rating is removed due to high percentage of missing data")
# =====================================
data_set, header_enum, enum_header = missing_lines_remove('games_info.csv', 3)

for line in data_set:
    line[3] = line[3][6:10]  # Convert all the dates to just Year value (strings)
    line[7] = str(rating_binning(line[7]))  # Categorize the rating value
    line.pop(5)  # Remove the age_ratings column
    line.pop(5)  # Remove the aggregated_rating column

# region Creating header list for the updated file for human review and file
header = list()
for key in header_enum:
    header.append(key)
header.pop(5)
header.pop(5)
with open("game_info_update.csv", mode='w') as update:
    updateWriter = csv.writer(update, delimiter=',', quotechar='"')
    updateWriter.writerow(header)
    for line in data_set:
        updateWriter.writerow(line)
# endregion

# region Create Sets for vector
with open("backupData/game_info_update.csv", mode='r') as update2:
    first_release_date = list()
    genres = list()
    platforms = list()
    game_mode = list()
    companies = list()

    updateReader = csv.DictReader(update2)
    for line in updateReader:
        first_release_date.append(line['first_release_date'])
        # Genre Column
        genre = json.loads(line['genres'].replace('\'', '"'))
        if isinstance(genre, list):
            for g in genre:
                genres.append(g)
        else:
            genres.append(genre)

        # Platforms Column
        plat = json.loads(line['platforms'].replace('\'', '"'))
        if isinstance(plat, list):
            for g in plat:
                platforms.append(g)
        else:
            platforms.append(plat)

        # Game Mode Column
        game = json.loads(line['game_modes'].replace('\'', '"'))
        if isinstance(game, list):
            for g in game:
                game_mode.append(g)
        else:
            game_mode.append(game)

        # Companies Column
        comp = json.loads(line['involved_companies'].replace('\'', '"').replace('{', '[').replace('}', ']'))
        if isinstance(comp, list):
            for g in comp:
                companies.append(g)
        else:
            companies.append(comp)

    first_release_date = set(first_release_date)
    genres = set(genres)
    platforms = set(platforms)
    game_mode = set(game_mode)
    companies = set(companies)

vector = dict()
for item in first_release_date:
    vector[item] = 0
for item in genres:
    vector[item] = 0
for i in range(1, 7):
    vector[str(i)] = 0
vector[str(9)] = 0
for item in platforms:
    vector[item] = 0
for item in game_mode:
    vector[item] = 0
for item in companies:
    vector[item] = 0
# endregion


def checkLine(line):
    for item in line:
        if line[item] == '-1' or line[item] == -1:
            return False
    return True


def clearVector(vec):
    if -1 in vec:
        vec.pop(-1)
    for ckey in vec.keys():
        vec[ckey] = 0
    return vec


# region Get all user Ids to set
def userIds(filename):
    userIds = set()
    with open(filename, mode='r') as files:
        for usrItem in files:
            usrID = usrItem.replace("\n", "").split("\t")[0]
            if usrID == 'User_ID':
                continue
            userIds.add(usrID)
    return userIds


user_ids = userIds("steamData/game_purchase.dat")
# endregion


def create_Vector_csv(cur_vector, filename, enabled=True):
    if enabled:
        curDict = dict()
        headlines = list()
        if isinstance(cur_vector, Vector):
            curDict = cur_vector.vectorDict
        elif isinstance(cur_vector, userVector):
            curDict = cur_vector.objDict
        else:
            print("ERROR while creating vector csv. Shut Down")
            exit(0)
        for vecKey in curDict.keys():
            headlines.append(vecKey)
        if not os.path.isfile("Vectors_data/" + filename + ".csv"):
            with open("Vectors_data/" + filename + ".csv", mode='w') as vectorFile:
                vectorFileWriter = csv.DictWriter(vectorFile, fieldnames=headlines)

                vectorFileWriter.writeheader()
                vectorFileWriter.writerow(curDict)
        else:
            with open("Vectors_data/" + filename + ".csv", mode='a') as vectorFile:
                vectorFileWriter = csv.DictWriter(vectorFile, fieldnames=headlines)
                vectorFileWriter.writerow(curDict)


def create_vectors():
    VectorDict = dict()  # All game vectors
    with open("backupData/game_info_update.csv", mode='r') as info:  # TODO change back to game_info_update regular, check how to config the new data
        info_reader = csv.DictReader(info)
        for line in info_reader:
            print(line)
            if not checkLine(line):
                continue
            new_vector = Vector(clearVector(vector))
            new_vector.gameSteamID = int(line['steam_id'])
            new_vector.gameName = line['game_name']
            # == Vector data ==
            # First release date
            new_vector.vectorValues[line['first_release_date']] = 1
            # Genres
            genre = json.loads(line['genres'].replace('\'', '"'))
            if isinstance(genre, list):
                for g in genre:
                    new_vector.vectorValues[g] = 1
            else:
                new_vector.vectorValues[genre] = 1
            # Rating
            new_vector.vectorValues[line['rating']] = 1
            # Platforms
            plat = json.loads(line['platforms'].replace('\'', '"'))
            if isinstance(plat, list):
                for g in plat:
                    new_vector.vectorValues[g] = 1
            else:
                new_vector.vectorValues[plat] = 1
            # Game Modes
            game = json.loads(line['game_modes'].replace('\'', '"'))
            if isinstance(game, list):
                for g in game:
                    new_vector.vectorValues[g] = 1
            else:
                new_vector.vectorValues[game] = 1
            # Companies
            comp = json.loads(line['involved_companies'].replace('\'', '"').replace('{', '[').replace('}', ']'))
            if isinstance(comp, list):
                for g in comp:
                    new_vector.vectorValues[g] = 1
            else:
                new_vector.vectorValues[comp] = 1

            new_vector.create_full_dict()
            create_Vector_csv(new_vector, "game_vector", False)
            VectorDict[new_vector.gameSteamID] = copy.deepcopy(new_vector)  # Has to be deepcopy or else the same reference changes
    return VectorDict


if not os.path.isfile('backupData/vectorData.pickle'):
    with open('backupData/vectorData.pickle', mode='wb') as p:
        print('Pickle Data does not exists, Creating Data! ..')
        VectorDict = create_vectors()
        pickle.dump(VectorDict, p)
else:
    with open('backupData/vectorData.pickle', mode='rb') as p:
        print('Pickle Data Exists. Loading !!')
        VectorDict = pickle.load(p)


# region Create user vectors and store them in file user_Vector
userVectors = dict()
if not os.path.isfile("Vectors_data/user_vector.csv") or False:
    counter, total = 0, len(user_ids)
    for id_user in user_ids:
        clearVector(vector)
        usr = userVector(id_user, vector)
        print("Calculating vector {0}".format(usr))
        usr.calculateUserVector(VectorDict)
        usr.createObjDir()
        create_Vector_csv(usr, "user_vector", False)
        userVectors[id_user] = copy.deepcopy(usr)
        print("Progress: {0}/{1}".format(counter, total))
        counter += 1


def create_vector_user(id_user_func, removedGameID):
    clearVector(vector)
    usr_local = userVector(str(id_user_func), vector, str(removedGameID))
    print("Calculating vector {0}".format(usr_local))
    usr_local.calculateUserVector(VectorDict)
    usr_local.createObjDir()
    return usr_local


# endregion
def create_new_user_vector_obj(games_chosen, new_user_id=9999, top=5):
    newUsrObj = new_user(new_user_id, games_chosen, vector)
    newUsrObj.calculateNewUserVector(VectorDict)
    results = newUsrObj.calculate(VectorDict)
    results_list = list()
    for i in range(top):
        results_list.append(str(i + 1) + ' ' + game_Ids[str(results[i][0])] + ' Score:' + str(results[i][1]))
    return games_chosen, results_list


def create_new_user_vector_obj_class(games_chosen, new_user_id=9999):
    newUsrObj = new_user(new_user_id, games_chosen, vector)
    newUsrObj.calculateNewUserVector(VectorDict)
    return newUsrObj

# create_new_user_vector_obj(['2=Fallout 4', '4=Fallout New Vegas', '6=HuniePop', '31=Fallout New Vegas Dead Money', '50=Killing Floor'])


def recommend(userId, top=5):
    usr = userVectorData(str(userId), game_Ids)
    owned_games = usr.print_Owned_games()
    usr.loadUsrVector('Vectors_data/user_vector.csv')
    results = usr.calculate(VectorDict)
    results_list = list()
    for i in range(top):
        results_list.append(str(i + 1) + ' ' + game_Ids[str(results[i][0])] + ' Score:' + str(results[i][1]))
    return owned_games, results_list


def recommend_eval(usr, gameIdRemoved, top=5):
    # usr = userVectorData(str(userId), game_Ids)
    # owned_games = usr.print_Owned_games()
    # usr.loadUsrVector('Vectors_data/user_vector.csv')
    results = usr.calculate(VectorDict)
    results_list = list()
    for x in range(len(results)):  # TODO: change the value to top or another value
        results_list.append(results[x][0])
    if gameIdRemoved in results_list:
        print('Game removed found !!!!!!!!!! \nIndex:{0}'.format(results_list.index(gameIdRemoved)))
        return 1 - (results_list.index(gameIdRemoved) / float(len(results_list)))
    else:
        print('You suck :(')
        return 0


def owned_game_list(UserID):
    usr = userVectorData(str(UserID), game_Ids)
    owned_games = usr.print_Owned_games()
    return owned_games