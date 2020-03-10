from src import userIds, owned_game_list, game_Ids, create_vector_user, recommend_eval
import random
import copy
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


def run_feature_testing(numberOfTests=5):
    final_report = list()
    local_sum = 0
    for _ in range(numberOfTests):
        randomUser, removedGameID = choose_random_user()
        localUser = create_vector_user(randomUser.userId, removedGameID)
        usr = userVectorData(str(randomUser.userId), game_Ids)
        usr.usrVector = copy.deepcopy(localUser.vector)
        res = float(recommend_eval(usr, removedGameID))
        local_sum += res
        print('Test Num: {0} | Rec Score: {1}'.format(_, res))
        final_report.append((_, res))
    print('==== Final Report Feature Evaluation')
    print(final_report)
    result = local_sum / numberOfTests
    print(result)

