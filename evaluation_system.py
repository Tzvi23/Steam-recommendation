import content_recom
import src
from user_similiraty import create_recommend_pairs
from user_vector_class import userVector
import re


# Feature Recommendation
def feature_recommendation(userID):
    owned_games, results = src.recommend(userID)
    print(results)


# Content Recommendation
def content_recommendation(userID):
    ownedGames = src.owned_game_list(userID)
    current_usr = userVector(str(userID))
    sorted_gameplay = current_usr.playTime
    if not sorted_gameplay:
        exit()
    game_Ids = src.load_gameIds()
    for key in sorted_gameplay.keys():
        sorted_gameplay[key] = float(sorted_gameplay[key])
    sorted_gameplay = {k: v for k, v in
                       sorted(current_usr.playTime.items(), key=lambda item: item[1], reverse=True)}
    results = content_recom.show_rec(game_Ids[str(list(sorted_gameplay)[0])])


# Similar Users Recommendation
def similar_user_recommendation(userID):
    pairs = create_recommend_pairs()
    recom = src.owned_game_list(pairs[userID])
    myGames = src.owned_game_list(userID)
    recom = check_similar_games(myGames, recom)
    print(recom)


def check_similar_games(owned, recom, noNumbers=False):
    # Remove numbers
    for _ in range(len(owned)):
        owned[_] = re.sub('^[0-9]+\s', '', owned[_])
    for _ in range(len(recom)):
        recom[_] = re.sub('^[0-9]+\s', '', recom[_])
    # Remove already owned games from the list
    same = len(list(set(recom).intersection(owned)))
    union = len(set(recom) | set(owned))
    ratio_owned = same / len(owned)
    ratio_pair = same / len(recom)
    print('Ratio - Owned: {0}'.format(ratio_owned))
    print('Ratio - pair: {0}'.format(ratio_pair))
    recom = list(set(recom) - set(owned))
    if noNumbers:
        return recom
    # Add order numbering
    for index in range(len(recom)):
        recom[index] = str(index + 1) + ' ' + recom[index]
    return recom


print('User 1')
similar_user_recommendation(1)
print('User 2')
similar_user_recommendation(2)
print('User 3')
similar_user_recommendation(3)
