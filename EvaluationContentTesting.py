import random

import content_recom
from src import userIds, load_gameIds, game_Ids
from user_vector_class import userVector
from user_vector_data_class import userVectorData


def choose_random_user(minGames=10):
    user_ids = list(userIds("steamData/game_purchase.dat"))
    randomID = int(random.choice(user_ids))
    usr = userVectorData(str(randomID), game_Ids)
    while len(usr.gamePurchasedIds) < 10:
        randomID = int(random.choice(user_ids))
        usr = userVectorData(str(randomID), game_Ids)
    removedGameID_local = choose_random_game(usr)
    return usr, removedGameID_local


def choose_random_game(usrObject):
    randomGameID = random.choice(usrObject.gamePurchasedIds)
    usrObject.gamePurchasedIds.remove(randomGameID)
    return randomGameID


def findID(searchID):
    for gameID, gameName in game_Ids.items():  # for name, age in dictionary.iteritems():  (for Python 2.x)
        if gameName == searchID:
            return gameID


def process_results(res):
    listOfGames = list()
    for item in res:
        listOfGames.append(item[1])
    return listOfGames


def content_eval():
    randomUser, removedGameID = choose_random_user()

    current_usr = userVector(randomUser.userId)
    sorted_gameplay = current_usr.playTime
    game_Ids = load_gameIds()
    for key in sorted_gameplay.keys():
        sorted_gameplay[key] = float(sorted_gameplay[key])
    sorted_gameplay = {k: v for k, v in
                       sorted(current_usr.playTime.items(), key=lambda item: item[1], reverse=True)}
    try:
        results = content_recom.show_rec(game_Ids[str(list(sorted_gameplay)[0])], 15, True)
    except (KeyError, IndexError) as er:
        print(er)
    results = process_results(results)
    for index in range(len(results)):
        results[index] = findID(results[index])
    if str(removedGameID) in results:
        print('Content Eval: game found!')
        return 1
    else:
        print('Content Eval: game not found!')
        return 0


def content_evaluation_summary(numOfTests):
    counter = 0
    for _ in range(numOfTests):
        counter += content_eval()
    print('Content eval results: {0}'.format(counter/numOfTests))
